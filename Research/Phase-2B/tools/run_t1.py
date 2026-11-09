"""Phase 2B - T1 multi-timeframe EMA pullback: eight pre-registered trials.

Rules are taken from Docs/Strategy/Phase-2A-Trend-Following-Research.md
Section 8.1 and the grid in Section 11.7.

Pre-registered grid (2 x 2 x 2 = 8):
  pullback distance : 0.2, 0.5 x ATR(14,H1)
  stop multiple     : 1.0, 1.5 x ATR(14,H1)
  RSI filter        : off, on

Risk per trade is fixed at 0.5% for the confirmatory trials; 0.25% and 1.0%
are reported separately as sensitivity analyses.

Interpretation decisions (documented, not tuned):
  * "Price trades within k x ATR of EMA20" is read as the bar's adverse
    extreme falling *inside* the band EMA20 +/- k*ATR: for longs
    EMA20 - k*ATR <= low <= EMA20 + k*ATR; for shorts the mirror on high.
    Requiring the extreme to be inside the band (rather than merely beyond
    it) is what turns the condition into a filter. The first implementation
    only required low <= EMA20 + k*ATR, which is satisfied by every EMA20
    cross and therefore filtered nothing; it was discarded before any
    confirmatory run.
  * "Close back in the trend direction beyond EMA20" is read as a cross:
    close > EMA20 with the previous close <= EMA20 (and the mirror for shorts).
  * RSI band 40-60 is applied to both directions, as the rule states
    "40 and 60 for longs, 60 and 40 for shorts".
  * The trailing stop is the tighter of the initial stop and
    best-price +/- 2.0 x ATR(14,H1), and never loosens.
  * The T1 gate "Sharpe at least 0.10 above T2" cannot be evaluated until T2
    runs. It is reported as DEFERRED and caps the T1 verdict at CONDITIONAL.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

import core as C

OUT = C.ROOT / "results" / "T1"
OUT.mkdir(parents=True, exist_ok=True)

TRAIL_MULT = 2.0
RISK_FRAC = 0.005
INITIAL = C.INITIAL_CAPITAL


# --------------------------------------------------------------------------
# Feature preparation
# --------------------------------------------------------------------------

def prepare_features() -> pd.DataFrame:
    m15 = C.load_series("M15")
    h1 = C.load_series("H1")
    h4 = C.load_series("H4")

    h1["atr14"] = C.atr(h1, 14)
    h1_close = h1[["time", "atr14"]].copy()
    h1_close["time"] = h1_close["time"] + pd.Timedelta(hours=1)

    h4["ema50"] = C.ema(h4["close"], 50)
    h4["ema200"] = C.ema(h4["close"], 200)
    h4["regime"] = np.where(
        h4["ema50"] > h4["ema200"], 1, np.where(h4["ema50"] < h4["ema200"], -1, 0)
    )
    h4_close = h4[["time", "regime"]].copy()
    h4_close["time"] = h4_close["time"] + pd.Timedelta(hours=4)

    m15["ema20"] = C.ema(m15["close"], 20)
    m15["rsi14"] = C.rsi(m15["close"], 14)

    m = pd.merge_asof(m15, h1_close, on="time", direction="backward")
    m = pd.merge_asof(m, h4_close, on="time", direction="backward")
    m = m.dropna(subset=["atr14", "regime", "ema20", "rsi14"]).reset_index(drop=True)
    # EMA(200, H4) needs a long warm-up. Trading on an immature regime filter
    # would be a data artefact, not a strategy result. Require 1,000 completed
    # H4 bars (about 166 trading days) before the first signal.
    warmup_bars = min(len(h4) - 1, 1000 - 1)
    warmup_end = h4["time"].iloc[warmup_bars] + pd.Timedelta(hours=4)
    m = m.loc[m["time"] >= warmup_end].reset_index(drop=True)
    m = m.loc[m["time"] <= C.OOS_END].reset_index(drop=True)
    if m.empty or m["time"].iloc[-1] < C.OOS_END - pd.Timedelta(days=7):
        raise SystemExit(
            f"M15 data ends at {m['time'].iloc[-1] if not m.empty else 'n/a'}, "
            f"before OOS end {C.OOS_END}; rebuild the series before running."
        )

    # Rollover multiplier for swap: 22:00 UTC, triple on Wednesday.
    is_2200 = (m["time"].dt.hour == 22) & (m["time"].dt.minute == 0)
    is_wed = m["time"].dt.day_of_week == 2
    m["rollover_mult"] = np.where(is_2200, np.where(is_wed, 3, 1), 0)
    # Section 11.5: no new entries within 15 minutes of the daily rollover.
    minutes = m["time"].dt.hour * 60 + m["time"].dt.minute
    m["no_entry"] = (minutes >= 21 * 60 + 45) & (minutes < 22 * 60 + 15)
    return m


# --------------------------------------------------------------------------
# Simulation
# --------------------------------------------------------------------------

def simulate(m: pd.DataFrame, params: dict, costs: C.CostModel,
             risk_frac: float = RISK_FRAC, initial: float = INITIAL,
             compound: bool = True) -> dict:
    n = len(m)
    time = m["time"].to_numpy()
    o = m["open"].to_numpy(float)
    hi = m["high"].to_numpy(float)
    lo = m["low"].to_numpy(float)
    cl = m["close"].to_numpy(float)
    sp = m["spread"].to_numpy(float)
    ema20 = m["ema20"].to_numpy(float)
    rsi14 = m["rsi14"].to_numpy(float)
    atr1 = m["atr14"].to_numpy(float)
    regime = m["regime"].to_numpy(int)
    roll = m["rollover_mult"].to_numpy(int)
    no_entry = m["no_entry"].to_numpy(bool)

    k = params["pullback"]
    stop_mult = params["stop"]
    use_rsi = params["rsi"]

    pos = 0
    pending = 0
    size = 0.0
    entry_raw = entry_fill = 0.0
    stop = best = 0.0
    entry_i = -1
    entry_time = None
    risk_dollars = 0.0
    stop_distance = 0.0
    swap_accrued = 0.0
    entry_spread = 0.0

    realized = 0.0
    equity = np.empty(n, dtype=float)
    equity[0] = initial
    trades: list[dict] = []
    last_equity = initial

    for i in range(1, n):
        # 1. Regime flip exit at the open.
        if pos != 0 and ((pos > 0 and regime[i] < 0) or (pos < 0 and regime[i] > 0)):
            exit_raw = o[i]
            exit_fill, _ = costs.exit_fill(exit_raw, sp[i], pos, is_stop=False)
            trades.append(_close_trade(
                time, entry_time, entry_raw, entry_fill, entry_spread,
                exit_raw, exit_fill, sp[i], pos, size, stop_distance,
                risk_dollars, swap_accrued, entry_i, i, "regime_flip", costs,
            ))
            realized += trades[-1]["net_pnl"]
            pos = 0
            swap_accrued = 0.0

        # 2. Execute a pending entry at this bar's open.
        if pending != 0 and pos == 0:
            direction = pending
            pending = 0
            if no_entry[i]:
                direction = 0
            if direction != 0:
                entry_raw = o[i]
                entry_fill, _ = costs.entry_fill(entry_raw, sp[i], direction)
                entry_spread = sp[i]
                stop_distance = max(stop_mult * atr1[i], 2.0 * sp[i])
                if stop_distance > 0:
                    base_equity = last_equity if compound else initial
                    risk_dollars = risk_frac * max(base_equity, 0.0)
                    size = risk_dollars / stop_distance
                    if size > 0:
                        pos = direction
                        stop = entry_fill - direction * stop_distance
                        best = entry_fill
                        entry_i = i
                        entry_time = time[i]
                        swap_accrued = 0.0

        # 3. Intrabar stop.
        if pos != 0:
            if pos > 0 and lo[i] <= stop:
                exit_raw = min(o[i], stop)
                exit_fill, _ = costs.exit_fill(exit_raw, sp[i], pos, is_stop=True)
                trades.append(_close_trade(
                    time, entry_time, entry_raw, entry_fill, entry_spread,
                    exit_raw, exit_fill, sp[i], pos, size, stop_distance,
                    risk_dollars, swap_accrued, entry_i, i, "stop", costs,
                ))
                realized += trades[-1]["net_pnl"]
                pos = 0
                swap_accrued = 0.0
            elif pos < 0 and hi[i] >= stop:
                exit_raw = max(o[i], stop)
                exit_fill, _ = costs.exit_fill(exit_raw, sp[i], pos, is_stop=True)
                trades.append(_close_trade(
                    time, entry_time, entry_raw, entry_fill, entry_spread,
                    exit_raw, exit_fill, sp[i], pos, size, stop_distance,
                    risk_dollars, swap_accrued, entry_i, i, "stop", costs,
                ))
                realized += trades[-1]["net_pnl"]
                pos = 0
                swap_accrued = 0.0

        # 4. Swap accrual and trailing stop.
        if pos != 0:
            if roll[i]:
                rate = costs.swap_long_per_oz_day if pos > 0 else costs.swap_short_per_oz_day
                # Swap rates are negative when they are a cost to the trader.
                # Store the accrual as a positive cost so every downstream use
                # subtracts it; adding a negative rate would be a subsidy.
                swap_accrued -= rate * costs.multiplier * size * roll[i]
            if pos > 0:
                if hi[i] > best:
                    best = hi[i]
                new_stop = best - TRAIL_MULT * atr1[i]
                if new_stop > stop:
                    stop = new_stop
            else:
                if lo[i] < best:
                    best = lo[i]
                new_stop = best + TRAIL_MULT * atr1[i]
                if new_stop < stop:
                    stop = new_stop

        # 5. Mark to market.
        if pos != 0:
            unreal = pos * size * (cl[i] - entry_fill)
            equity[i] = initial + realized + unreal - 0.035 * size - swap_accrued
        else:
            equity[i] = initial + realized
        last_equity = equity[i]

        # 6. Signal on the closed bar.
        if pos == 0 and pending == 0 and i < n - 1:
            prev_c = cl[i - 1]
            prev_e = ema20[i - 1]
            # Pullback: the bar's adverse extreme trades inside the band
            # EMA20 +/- k*ATR(14,H1). Requiring the extreme to be *inside* the
            # band (not merely beyond it) is what makes the condition a filter
            # rather than a tautology on every EMA20 cross.
            long_ok = (
                regime[i] > 0
                and lo[i] >= ema20[i] - k * atr1[i]
                and lo[i] <= ema20[i] + k * atr1[i]
                and cl[i] > ema20[i]
                and prev_c <= prev_e
            )
            short_ok = (
                regime[i] < 0
                and hi[i] >= ema20[i] - k * atr1[i]
                and hi[i] <= ema20[i] + k * atr1[i]
                and cl[i] < ema20[i]
                and prev_c >= prev_e
            )
            if use_rsi:
                rsi_ok = 40.0 <= rsi14[i] <= 60.0
                long_ok = long_ok and rsi_ok
                short_ok = short_ok and rsi_ok
            if long_ok:
                pending = 1
            elif short_ok:
                pending = -1

    # Close any open position at the last bar.
    if pos != 0:
        exit_raw = cl[n - 1]
        exit_fill, _ = costs.exit_fill(exit_raw, sp[n - 1], pos, is_stop=False)
        trades.append(_close_trade(
            time, entry_time, entry_raw, entry_fill, entry_spread,
            exit_raw, exit_fill, sp[n - 1], pos, size, stop_distance,
            risk_dollars, swap_accrued, entry_i, n - 1, "end_of_data", costs,
        ))
        realized += trades[-1]["net_pnl"]
        equity[n - 1] = initial + realized

    eq = pd.Series(equity, index=pd.DatetimeIndex(time), name="equity")
    # Trading-day buckets ending at 22:00 UTC, so the daily curve is aligned
    # with the D1 series (which is stamped at its 22:00 close). pandas only
    # honours `offset` on a tz-naive index, so drop and restore UTC.
    eq_naive = eq.copy()
    eq_naive.index = eq_naive.index.tz_localize(None)
    daily = (
        eq_naive.resample("1D", offset="22h", label="right", closed="right")
        .last()
        .dropna()
    )
    daily.index = daily.index.tz_localize("UTC")
    tdf = pd.DataFrame(trades)
    return {
        "equity_bar": eq,
        "equity_daily": daily,
        "trades": tdf,
        "params": params,
        "risk_frac": risk_frac,
        "cost_multiplier": costs.multiplier,
    }


def _close_trade(time, entry_time, entry_raw, entry_fill, entry_spread,
                 exit_raw, exit_fill, exit_spread, direction, size,
                 stop_distance, risk_dollars, swap_accrued, entry_i, exit_i,
                 reason, costs) -> dict:
    frictionless = direction * size * (exit_raw - entry_raw)
    realized_gross = direction * size * (exit_fill - entry_fill)
    spread_slip = frictionless - realized_gross
    commission = costs.commission_per_oz_round_turn * size * costs.multiplier
    net = frictionless - spread_slip - commission - swap_accrued
    holding = (time[exit_i] - time[entry_i]) / np.timedelta64(1, "D")
    return {
        "entry_time": time[entry_i],
        "exit_time": time[exit_i],
        "direction": direction,
        "entry_raw": entry_raw,
        "entry_fill": entry_fill,
        "exit_raw": exit_raw,
        "exit_fill": exit_fill,
        "size_oz": size,
        "stop_distance": stop_distance,
        "risk_dollars": risk_dollars,
        "gross_pnl": frictionless,
        "spread_slip_cost": spread_slip,
        "commission_cost": commission,
        "swap_cost": swap_accrued,
        "total_cost": spread_slip + commission + swap_accrued,
        "net_pnl": net,
        "holding_days": holding,
        "holding_bars": exit_i - entry_i,
        "exit_reason": reason,
    }


# --------------------------------------------------------------------------
# Period metrics
# --------------------------------------------------------------------------

def period_report(result: dict, start, end, initial: float = INITIAL) -> dict:
    eq = result["equity_daily"]
    eq = eq.loc[(eq.index >= start) & (eq.index <= end)]
    if len(eq) < 2:
        return {}
    base = eq.iloc[0]
    rebased = initial * eq / base
    m = C.equity_metrics(rebased, initial)
    trades = result["trades"]
    if not trades.empty:
        t = trades.loc[
            (trades["entry_time"] >= start) & (trades["entry_time"] <= end)
        ]
    else:
        t = trades
    m.update(C.trade_metrics(t))
    m["exposure_pct"] = _exposure(trades, start, end)
    return m


def _exposure(trades: pd.DataFrame, start, end) -> float:
    if trades is None or trades.empty:
        return 0.0
    t = trades.loc[(trades["entry_time"] <= end) & (trades["exit_time"] >= start)]
    if t.empty:
        return 0.0
    secs = (
        (t["exit_time"].clip(upper=end) - t["entry_time"].clip(lower=start))
        .dt.total_seconds()
        .sum()
    )
    total = (pd.Timestamp(end) - pd.Timestamp(start)).total_seconds()
    return float(secs / total * 100.0) if total > 0 else 0.0


def notional_metrics(result: dict, start, end, initial: float = INITIAL) -> dict:
    """Metrics for a constant-risk (non-compounding) run.

    The equity series stays at `initial` plus cumulative P&L, so it can cross
    zero. Percent changes are therefore undefined; returns are computed against
    the fixed initial capital instead, and drawdown is measured in dollars.
    """
    eq = result["equity_daily"]
    eq = eq.loc[(eq.index >= start) & (eq.index <= end)]
    if len(eq) < 2:
        return {}
    pnl_series = eq.diff()
    pnl_series.iloc[0] = 0.0
    ret = pnl_series / initial
    std = float(ret.std())
    sharpe = float(ret.mean() / std * np.sqrt(252)) if std > 0 else np.nan
    downside = ret[ret < 0]
    dstd = float(downside.std())
    sortino = float(ret.mean() / dstd * np.sqrt(252)) if dstd > 0 else np.nan
    cummax = eq.cummax()
    dd = eq - cummax
    max_dd_abs = float(dd.min())
    period_pnl = float(eq.iloc[-1] - eq.iloc[0])
    years = max(len(eq) / 252.0, 1e-9)
    dd_pct = dd / initial
    ulcer = float(np.sqrt((dd_pct ** 2).mean()) * 100.0)
    mar = float((period_pnl / years) / abs(max_dd_abs)) if max_dd_abs < 0 else np.nan
    trades = result["trades"]
    if trades is None or trades.empty:
        t = trades
    else:
        t = trades.loc[(trades["entry_time"] >= start) & (trades["entry_time"] <= end)]
    out = C.trade_metrics(t)
    out.update({
        "final_equity": float(eq.iloc[-1]),
        "net_profit": period_pnl,
        "return_pct": period_pnl / initial * 100.0,
        "cagr_pct": np.nan,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_dd_abs": max_dd_abs,
        "max_dd_pct": max_dd_abs / initial * 100.0,
        "ulcer_pct": ulcer,
        "mar": mar,
        "volatility_pct": std * np.sqrt(252) * 100.0,
        "n_days": int(len(eq)),
        "exposure_pct": _exposure(trades, start, end),
    })
    return out


# --------------------------------------------------------------------------
# Random-entry control: circular shift of the entry schedule
# --------------------------------------------------------------------------

def random_entry_control(m: pd.DataFrame, result: dict, costs: C.CostModel,
                         n_runs: int = 500, seed: int = 20261105,
                         actual_profit: float | None = None) -> dict:
    trades = result["trades"]
    if trades.empty:
        return {"runs": 0}
    rng = np.random.default_rng(seed)
    n = len(m)
    o = m["open"].to_numpy(float)
    hi = m["high"].to_numpy(float)
    lo = m["low"].to_numpy(float)
    cl = m["close"].to_numpy(float)
    sp = m["spread"].to_numpy(float)
    atr1 = m["atr14"].to_numpy(float)
    roll = m["rollover_mult"].to_numpy(int)

    entry_idx = pd.DatetimeIndex(m["time"]).get_indexer(pd.DatetimeIndex(trades["entry_time"]))
    if (entry_idx < 0).any():
        return {"runs": 0}
    entry_idx = entry_idx.astype(int)
    holding = trades["holding_bars"].to_numpy(int)
    direction = trades["direction"].to_numpy(int)
    stop_dist = trades["stop_distance"].to_numpy(float)

    max_hold = int(holding.max())
    if max_hold >= n - 1:
        return {"runs": 0}

    profits = np.empty(n_runs)
    for r in range(n_runs):
        offset = int(rng.integers(0, n - max_hold - 1))
        pnl = 0.0
        for j in range(len(entry_idx)):
            ei = entry_idx[j] + offset
            if ei >= n - 1:
                continue
            xi = min(ei + holding[j], n - 1)
            d = direction[j]
            entry_raw = o[ei]
            entry_fill, _ = costs.entry_fill(entry_raw, sp[ei], d)
            sd = max(stop_dist[j], 2.0 * sp[ei])
            # Constant risk, so the control is not distorted by the actual
            # trial's equity collapse.
            risk = RISK_FRAC * INITIAL
            size = risk / sd if sd > 0 else 0.0
            if size <= 0:
                continue
            # stop within the holding window
            stop = entry_fill - d * sd
            exit_raw = cl[xi]
            exit_is_stop = False
            for k2 in range(ei + 1, xi + 1):
                if d > 0 and lo[k2] <= stop:
                    exit_raw = min(o[k2], stop)
                    xi = k2
                    exit_is_stop = True
                    break
                if d < 0 and hi[k2] >= stop:
                    exit_raw = max(o[k2], stop)
                    xi = k2
                    exit_is_stop = True
                    break
            exit_fill, _ = costs.exit_fill(exit_raw, sp[xi], d, is_stop=exit_is_stop)
            rate = costs.swap_long_per_oz_day if d > 0 else costs.swap_short_per_oz_day
            # Positive cost, mirroring the simulation's accrual convention.
            swap_cost = -rate * costs.multiplier * size * float(roll[ei + 1 : xi + 1].sum())
            gross = d * size * (exit_raw - entry_raw)
            commission = costs.commission_per_oz_round_turn * size * costs.multiplier
            net = gross - (gross - d * size * (exit_fill - entry_fill)) - commission - swap_cost
            pnl += net
        profits[r] = pnl
    actual = float(actual_profit) if actual_profit is not None else float(trades["net_pnl"].sum())
    return {
        "runs": n_runs,
        "profit_median": float(np.median(profits)),
        "profit_p95": float(np.percentile(profits, 95)),
        "profit_p05": float(np.percentile(profits, 5)),
        "actual_profit": actual,
        "percentile_of_actual": float((profits < actual).mean() * 100.0),
    }


# --------------------------------------------------------------------------
# Trial runner
# --------------------------------------------------------------------------

def main() -> None:
    print("preparing features ...", flush=True)
    m = prepare_features()
    print(f"  M15 rows: {len(m)}  {m['time'].iloc[0]} .. {m['time'].iloc[-1]}", flush=True)

    grid = [
        {"pullback": pb, "stop": st, "rsi": rsi_on}
        for pb, st, rsi_on in itertools.product([0.2, 0.5], [1.0, 1.5], [False, True])
    ]

    rows = []
    all_results = {}
    const_results = {}
    return_matrix = {}
    param_by_tid = {}

    for gi, params in enumerate(grid, start=1):
        tid = f"T1-{gi:02d}-PB{params['pullback']}-ST{params['stop']}-RSI{int(params['rsi'])}"
        param_by_tid[tid] = params
        print(f"trial {tid}", flush=True)
        for mult in (1.0, 1.5, 2.0):
            costs = C.CostModel(multiplier=mult)
            res = simulate(m, params, costs)
            tag = f"{tid}-C{mult:.1f}"
            all_results[tag] = res
            full = period_report(res, C.IS_START, C.OOS_END)
            is_r = period_report(res, C.IS_START, C.IS_END)
            oos_r = period_report(res, C.OOS_START, C.OOS_END)
            rows.append({
                "trial": tid, "cost_mult": mult, "period": "FULL",
                **{k: v for k, v in full.items()},
            })
            rows.append({"trial": tid, "cost_mult": mult, "period": "IS", **is_r})
            rows.append({"trial": tid, "cost_mult": mult, "period": "OOS", **oos_r})
            # Constant-risk (non-compounding) run: the pre-registered
            # fixed-fractional account is ruined in-sample, after which the
            # compounded curve is dominated by the size collapse. The
            # constant-risk curve keeps the same rule and the same 0.5%
            # initial risk but no compounding, so its returns are the
            # interpretable basis for statistics and regime analysis.
            const_res = simulate(m, params, costs, compound=False)
            const_results[tag] = const_res
            rows.append({"trial": tid, "cost_mult": mult, "period": "FULL_CONST",
                         **notional_metrics(const_res, C.IS_START, C.OOS_END)})
            rows.append({"trial": tid, "cost_mult": mult, "period": "IS_CONST",
                         **notional_metrics(const_res, C.IS_START, C.IS_END)})
            rows.append({"trial": tid, "cost_mult": mult, "period": "OOS_CONST",
                         **notional_metrics(const_res, C.OOS_START, C.OOS_END)})
            if mult == 1.0:
                return_matrix[tid] = (
                    const_res["equity_daily"].diff() / INITIAL
                )

        # save the baseline cost trade log
        all_results[f"{tid}-C1.0"]["trades"].to_csv(OUT / f"{tid}_trades.csv", index=False)

    table = pd.DataFrame(rows)
    table.to_csv(OUT / "t1_trial_table.csv", index=False)

    # ---- benchmarks on the same windows
    d1 = C.load_series("D1")
    d1 = d1.loc[d1["time"] <= C.OOS_END].reset_index(drop=True)
    cost0 = C.CostModel()
    bench = {
        "IS": C.buy_and_hold(C.slice_period(d1, C.IS_START, C.IS_END), cost0),
        "OOS": C.buy_and_hold(C.slice_period(d1, C.OOS_START, C.OOS_END), cost0),
        "FULL": C.buy_and_hold(d1, cost0),
    }

    # ---- selection: best IS net Sharpe among baseline-cost trials
    base = table[(table["period"] == "IS") & (table["cost_mult"] == 1.0)].copy()
    base = base.sort_values(["sharpe", "profit_factor"], ascending=False)
    best_tid = base.iloc[0]["trial"]
    best_oos = table[(table["trial"] == best_tid) & (table["period"] == "OOS")].set_index("cost_mult")

    # ---- statistics on baseline cost, OOS
    oos_rets = pd.DataFrame({
        tid: series.loc[(series.index >= C.OOS_START) & (series.index <= C.OOS_END)]
        for tid, series in return_matrix.items()
    })
    sr_by_trial = oos_rets.apply(lambda s: s.mean() / s.std() * np.sqrt(252) if s.std() > 0 else np.nan)
    sr_var = float(sr_by_trial.var() / 252.0)  # variance of daily SR
    dsr_rows = {}
    for tid in oos_rets.columns:
        dsr_rows[tid] = C.deflated_sharpe(oos_rets[tid].dropna(), n_trials=32, sr_variance=sr_var)
    # buy-and-hold daily returns for RC, aligned to the same 22:00 trading-day
    # stamps as the strategy curve.
    bh_eq = d1.set_index("time")["close"].loc[C.OOS_START:C.OOS_END]
    bh_ret = bh_eq.pct_change().dropna()
    rc = C.whites_reality_check(oos_rets, benchmark=bh_ret, n_boot=1000)

    # ---- constant-risk results for the selected trial
    const_res = const_results[f"{best_tid}-C1.0"]
    const = {
        "FULL": notional_metrics(const_res, C.IS_START, C.OOS_END),
        "IS": notional_metrics(const_res, C.IS_START, C.IS_END),
        "OOS": notional_metrics(const_res, C.OOS_START, C.OOS_END),
    }
    const_res["trades"].to_csv(OUT / f"{best_tid}_constant_risk_trades.csv", index=False)

    # ---- random-entry control for the selected trial (constant risk, matched
    # to the constant-risk notional total)
    rnd = random_entry_control(
        m, const_res, cost0, n_runs=300,
        actual_profit=float(const_res["trades"]["net_pnl"].sum()),
    )

    # ---- robustness lenses for the selected trial, on constant-risk returns
    d1_oos = C.slice_period(d1, C.OOS_START, C.OOS_END).set_index("time")["close"]
    vol_reg = C.regime_series(d1_oos)["regime"]
    rets = return_matrix[best_tid]
    rets_oos = rets.loc[(rets.index >= C.OOS_START) & (rets.index <= C.OOS_END)]
    vol_perf = C.perf_by_group(rets_oos, vol_reg.reindex(rets_oos.index))
    macro_perf = C.perf_by_group(rets_oos, C.macro_regime(rets_oos.index))
    sub_perf = C.perf_by_group(rets_oos, C.subperiod(rets_oos.index))
    rets_full = (const_res["equity_daily"].diff() / INITIAL).loc[C.IS_START:C.OOS_END]
    sub_full = C.perf_by_group(rets_full.dropna(), C.subperiod(rets_full.dropna().index))
    bh_close_all = d1.set_index("time")["close"]
    ba = C.beta_alpha(rets_oos, bh_close_all.pct_change().reindex(rets_oos.index))

    # ---- gate checks on OOS, baseline cost
    oos = best_oos.loc[1.0].to_dict()
    gross = oos.get("gross_pnl")
    costs = oos.get("total_costs")
    gates = {
        "min_trades_300": bool(oos.get("trades", 0) >= 300),
        "net_pf_ge_1_20": bool(oos.get("profit_factor", 0) >= 1.20),
        "costs_le_25pct_gross": bool(
            gross is not None and costs is not None and gross > 0 and costs / gross <= 0.25
        ),
        "positive_in_3_of_4_vol_regimes": bool(
            sum(1 for v in vol_perf.values() if (v.get("sharpe") or -9) > 0) >= 3
        ),
        "sharpe_ge_t2_plus_0_10": "DEFERRED (T2 not yet run)",
    }

    # ---- Harvey-Liu-Zhu t-statistic and bootstrap CI on OOS returns
    sel_rets = oos_rets[best_tid].dropna()
    hlz_t = float(sel_rets.mean() / sel_rets.std() * np.sqrt(len(sel_rets))) if sel_rets.std() > 0 else np.nan
    boot = C.bootstrap_sharpe_ci(sel_rets, n_boot=1000)
    for tag, res in all_results.items():
        if tag.endswith("C1.0"):
            res["equity_daily"].rename("equity").to_csv(OUT / f"{tag}_equity.csv")

    summary = {
        "family": "T1",
        "trials": 8,
        "selected_by_is_sharpe": best_tid,
        "harvey_liu_zhu_t_oos": hlz_t,
        "bootstrap_sharpe_ci_oos": boot,
        "benchmarks": bench,
        "best_oos_by_cost": best_oos.to_dict(),
        "selected_constant_risk": const,
        "vol_regime_oos": vol_perf,
        "macro_regime_oos": macro_perf,
        "subperiod_oos": sub_perf,
        "subperiod_full": sub_full,
        "beta_alpha_oos": ba,
        "gates_oos": gates,
        "deflated_sharpe_oos": dsr_rows,
        "reality_check_oos": rc,
        "random_entry": rnd,
        "notes": [
            "Risk fixed at 0.5% for the eight confirmatory trials.",
            "T1 gate 'Sharpe >= T2 Sharpe + 0.10' is DEFERRED until T2 runs.",
        ],
    }
    C.save_json(summary, OUT / "t1_summary.json")
    print(json.dumps({k: v for k, v in summary.items() if k != "deflated_sharpe_oos"}, indent=2, default=str))
    print("\nTrial table (baseline cost):")
    print(table[table["cost_mult"] == 1.0][
        ["trial", "period", "trades", "profit_factor", "sharpe", "max_dd_pct",
         "net_profit", "win_rate_pct", "cost_pct_of_gross"]
    ].to_string(index=False))


if __name__ == "__main__":
    main()
