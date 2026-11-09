"""Phase 2B - T2 daily dual-EMA trend system: eighteen pre-registered trials.

Rules are taken from Docs/Strategy/Phase-2A-Trend-Following-Research.md
Section 8.2 and the grid in Section 11.7.

Pre-registered grid (3 x 3 x 2 = 18):
  EMA pair          : (20, 100), (50, 200), (100, 400)
  disaster stop     : 2.0, 3.0, 4.0 x ATR(14, D1)
  risk fraction     : 0.5%, 1.0%

Frozen interpretation decisions (see reports/T2-methodology-note.md):
  * Signal on a completed D1 close; entry at the next D1 open.
  * Opposite crossover flips the position at the next open.
  * Disaster stop checked intrabar; stop assumed hit first.
  * After a stop-out the engine is flat until the next crossover. It does not
    re-enter the prevailing trend without a new crossover.
  * No signal until 1,000 completed D1 bars (first signal bar 2007-11-01).
  * The stop distance uses ATR(14, D1) of the *last completed* bar, i.e. the
    bar before the entry bar, because the entry bar's range is not known at its
    open.
  * The selected trial is the highest IS net Sharpe at baseline cost.
  * The 100-trade gate uses the full sample (2008-2026), per the project
    owner's resolution of the Phase 2A wording.

The runner writes results/T2/t2_trial_table.csv, t2_summary.json and the
per-trial trade logs. It does not write the report; report_t2.py does that.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

import core as C

OUT = C.ROOT / "results" / "T2"
OUT.mkdir(parents=True, exist_ok=True)

INITIAL = C.INITIAL_CAPITAL
WARMUP_BARS = 1000  # completed D1 bars before the first signal


# --------------------------------------------------------------------------
# Feature preparation
# --------------------------------------------------------------------------

def prepare_features() -> pd.DataFrame:
    d1 = C.load_series("D1")
    d1 = d1.loc[d1["time"] <= C.OOS_END].reset_index(drop=True)
    d1["atr14"] = C.atr(d1, 14)
    d1["ema20"] = C.ema(d1["close"], 20)
    d1["ema100"] = C.ema(d1["close"], 100)
    d1["ema50"] = C.ema(d1["close"], 50)
    d1["ema200"] = C.ema(d1["close"], 200)
    d1["ema400"] = C.ema(d1["close"], 400)
    # Every D1 bar ends at a 22:00 rollover; Wednesday carries the triple swap.
    d1["rollover_mult"] = np.where(d1["time"].dt.day_of_week == 2, 3, 1)
    d1["signal_allowed"] = np.arange(len(d1)) >= WARMUP_BARS
    return d1


# --------------------------------------------------------------------------
# Simulation
# --------------------------------------------------------------------------

def simulate(m: pd.DataFrame, params: dict, costs: C.CostModel,
             risk_frac: float, initial: float = INITIAL,
             compound: bool = True) -> dict:
    n = len(m)
    time = m["time"].to_numpy()
    o = m["open"].to_numpy(float)
    hi = m["high"].to_numpy(float)
    lo = m["low"].to_numpy(float)
    cl = m["close"].to_numpy(float)
    sp = m["spread"].to_numpy(float)
    atr1 = m["atr14"].to_numpy(float)
    fast = m[params["fast"]].to_numpy(float)
    slow = m[params["slow"]].to_numpy(float)
    sig_ok = m["signal_allowed"].to_numpy(bool)
    roll = m["rollover_mult"].to_numpy(int)

    stop_mult = params["stop"]

    pos = 0
    pending = 0
    size = 0.0
    entry_raw = entry_fill = 0.0
    stop = 0.0
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
        # 1. Execute the pending signal at this bar's open. A pending opposite
        # signal flips an open position: close the old one and open the new
        # one at the same open.
        if pending != 0:
            direction = pending
            pending = 0
            if pos != 0:
                exit_raw = o[i]
                exit_fill, _ = costs.exit_fill(exit_raw, sp[i], pos, is_stop=False)
                trades.append(_close_trade(
                    time, entry_time, entry_raw, entry_fill, entry_spread,
                    exit_raw, exit_fill, sp[i], pos, size, stop_distance,
                    risk_dollars, swap_accrued, entry_i, i, "flip", costs,
                ))
                realized += trades[-1]["net_pnl"]
                pos = 0
                swap_accrued = 0.0
            entry_raw = o[i]
            entry_fill, _ = costs.entry_fill(entry_raw, sp[i], direction)
            entry_spread = sp[i]
            # ATR of the last completed bar is known at this open; the entry
            # bar's own range is not.
            stop_distance = max(stop_mult * atr1[i - 1], 2.0 * sp[i])
            base_equity = last_equity if compound else initial
            risk_dollars = risk_frac * max(base_equity, 0.0)
            size = risk_dollars / stop_distance if stop_distance > 0 else 0.0
            if size > 0:
                pos = direction
                stop = entry_fill - direction * stop_distance
                entry_i = i
                entry_time = time[i]
                swap_accrued = 0.0

        # 2. Intrabar disaster stop. Stop is assumed to be hit first.
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

        # 3. Swap accrual at the daily rollover.
        if pos != 0:
            rate = costs.swap_long_per_oz_day if pos > 0 else costs.swap_short_per_oz_day
            # Swap rates are negative when they are a cost to the trader.
            # Store the accrual as a positive cost so every downstream use
            # subtracts it; adding a negative rate would be a subsidy.
            swap_accrued -= rate * costs.multiplier * size * roll[i]

        # 4. Mark to market at the close.
        if pos != 0:
            unreal = pos * size * (cl[i] - entry_fill)
            equity[i] = initial + realized + unreal - 0.035 * size - swap_accrued
        else:
            equity[i] = initial + realized
        last_equity = equity[i]

        # 5. Signal on the closed bar. The pending order is executed at the
        # next bar's open.
        if i < n - 1 and sig_ok[i]:
            state = 1 if fast[i] > slow[i] else (-1 if fast[i] < slow[i] else 0)
            prev = 1 if fast[i - 1] > slow[i - 1] else (-1 if fast[i - 1] < slow[i - 1] else 0)
            if state > 0 and prev <= 0:
                pending = 1
            elif state < 0 and prev >= 0:
                pending = -1

    # Close any open position at the last bar's close.
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
    tdf = pd.DataFrame(trades)
    return {
        "equity_daily": eq,
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
# Period metrics (mirrors run_t1.py so T1 and T2 are directly comparable)
# --------------------------------------------------------------------------

def period_report(result: dict, start, end, initial: float = INITIAL) -> dict:
    eq = result["equity_daily"]
    eq = eq.loc[(eq.index >= start) & (eq.index <= end)]
    if len(eq) < 2:
        return {}
    base = eq.iloc[0]
    rebased = initial * eq / base if base != 0 else eq
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
    """Metrics for the constant-risk (non-compounding) run.

    Returns are computed against the fixed initial capital, so the series can
    cross zero without invalidating the Sharpe or drawdown arithmetic.
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
# Random-entry control: same directions, holding periods and stops, entries
# shifted to a random point in the sample.
# --------------------------------------------------------------------------

def random_entry_control(m: pd.DataFrame, result: dict, costs: C.CostModel,
                         n_runs: int = 500, seed: int = 20261105,
                         actual_profit: float | None = None) -> dict:
    """Matched-exposure control with a single random shift of the schedule.

    T2 holds positions for months to years, so a naive forward shift can push
    most trades past the end of the sample and silently drop them; that turns
    the control into a test of "how many trades fit", not of entry timing.
    The control therefore (a) excludes the terminal end_of_data trade, whose
    exit is an artefact of the sample end, and (b) draws the shift from the
    range that keeps every remaining trade fully inside the sample. Direction,
    holding period, stop distance, sizing and costs are unchanged.
    """
    trades = result["trades"]
    if trades.empty:
        return {"runs": 0}
    if "exit_reason" in trades.columns:
        ctrl = trades.loc[trades["exit_reason"] != "end_of_data"].reset_index(drop=True)
    else:
        ctrl = trades.reset_index(drop=True)
    if ctrl.empty:
        return {"runs": 0}

    rng = np.random.default_rng(seed)
    n = len(m)
    o = m["open"].to_numpy(float)
    hi = m["high"].to_numpy(float)
    lo = m["low"].to_numpy(float)
    cl = m["close"].to_numpy(float)
    sp = m["spread"].to_numpy(float)
    roll = m["rollover_mult"].to_numpy(int)

    entry_idx = pd.DatetimeIndex(m["time"]).get_indexer(pd.DatetimeIndex(ctrl["entry_time"]))
    if (entry_idx < 0).any():
        return {"runs": 0}
    entry_idx = entry_idx.astype(int)
    holding = ctrl["holding_bars"].to_numpy(int)
    direction = ctrl["direction"].to_numpy(int)
    stop_dist = ctrl["stop_distance"].to_numpy(float)
    risk = ctrl["risk_dollars"].to_numpy(float)

    max_end = int((entry_idx + holding).max())
    max_offset = n - 1 - max_end
    if max_offset < 1:
        return {"runs": 0, "n_trades": int(len(ctrl)), "max_offset_bars": int(max_offset)}

    profits = np.empty(n_runs)
    for r in range(n_runs):
        offset = int(rng.integers(0, max_offset + 1))
        pnl = 0.0
        for j in range(len(entry_idx)):
            ei = entry_idx[j] + offset
            xi = ei + holding[j]
            d = direction[j]
            entry_raw = o[ei]
            entry_fill, _ = costs.entry_fill(entry_raw, sp[ei], d)
            sd = max(stop_dist[j], 2.0 * sp[ei])
            size = max(risk[j], 0.0) / sd if sd > 0 else 0.0
            if size <= 0:
                continue
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
            swap_cost = -rate * costs.multiplier * size * float(roll[ei + 1: xi + 1].sum())
            gross = d * size * (exit_raw - entry_raw)
            commission = costs.commission_per_oz_round_turn * size * costs.multiplier
            net = gross - (gross - d * size * (exit_fill - entry_fill)) - commission - swap_cost
            pnl += net
        profits[r] = pnl
    actual = float(ctrl["net_pnl"].sum()) if actual_profit is None else float(actual_profit)
    return {
        "runs": n_runs,
        "n_trades": int(len(ctrl)),
        "max_offset_bars": int(max_offset),
        "max_offset_days": int((m["time"].iloc[n - 1] - m["time"].iloc[max_end]).days),
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
    print("preparing D1 features ...", flush=True)
    m = prepare_features()
    print(f"  D1 rows: {len(m)}  {m['time'].iloc[0]} .. {m['time'].iloc[-1]}", flush=True)
    print(f"  first signal bar: {m.loc[m['signal_allowed'], 'time'].iloc[0]}", flush=True)

    pairs = [(20, 100), (50, 200), (100, 400)]
    # Signal-frequency record for the report: crossovers after the 1,000-bar
    # warm-up, before any stop-out can reduce the trade count.
    pair_signal_counts = {}
    ok = m["signal_allowed"].to_numpy(bool)
    times_s = m["time"]
    years_after_warmup = (m["time"].iloc[-1] - m.loc[ok, "time"].iloc[0]).days / 365.25
    for fa, sl in pairs:
        fast = m[f"ema{fa}"].to_numpy(float)
        slow = m[f"ema{sl}"].to_numpy(float)
        state = np.where(fast > slow, 1, np.where(fast < slow, -1, 0))
        prev = np.roll(state, 1)
        prev[0] = 0
        cross = pd.Series(
            ok & (((state > 0) & (prev <= 0)) | ((state < 0) & (prev >= 0))),
            index=m.index,
        )
        pair_signal_counts[f"{fa}/{sl}"] = {
            "full": int(cross.sum()),
            "is": int((cross & (times_s <= C.IS_END)).sum()),
            "oos": int((cross & (times_s >= C.OOS_START)).sum()),
            "first_cross": str(times_s[cross].iloc[0]) if cross.any() else None,
            "years": round(float(years_after_warmup), 2),
            "per_year": round(float(cross.sum() / years_after_warmup), 2),
        }

    # Explicit 18-item grid: pair, stop, risk in that order.
    grid = []
    for (fa, sl), st, r in itertools.product(pairs, [2.0, 3.0, 4.0], [0.005, 0.01]):
        grid.append({
            "fast": f"ema{fa}", "slow": f"ema{sl}",
            "pair": (fa, sl), "stop": st, "risk": r,
        })

    rows = []
    const_results = {}
    return_matrix = {}
    param_by_tid = {}
    trade_counts = {}

    for gi, params in enumerate(grid, start=1):
        fa, sl = params["pair"]
        tid = f"T2-{gi:02d}-E{fa}x{sl}-ST{params['stop']:.1f}-R{params['risk'] * 100:.1f}"
        param_by_tid[tid] = params
        print(f"trial {tid}", flush=True)
        for mult in (1.0, 1.5, 2.0):
            costs = C.CostModel(multiplier=mult)
            res = simulate(m, params, costs, risk_frac=params["risk"])
            full = period_report(res, C.IS_START, C.OOS_END)
            is_r = period_report(res, C.IS_START, C.IS_END)
            oos_r = period_report(res, C.OOS_START, C.OOS_END)
            rows.append({"trial": tid, "cost_mult": mult, "period": "FULL", **full})
            rows.append({"trial": tid, "cost_mult": mult, "period": "IS", **is_r})
            rows.append({"trial": tid, "cost_mult": mult, "period": "OOS", **oos_r})

            const_res = simulate(m, params, costs, risk_frac=params["risk"],
                                 compound=False)
            const_results[f"{tid}-C{mult:.1f}"] = const_res
            rows.append({"trial": tid, "cost_mult": mult, "period": "FULL_CONST",
                         **notional_metrics(const_res, C.IS_START, C.OOS_END)})
            rows.append({"trial": tid, "cost_mult": mult, "period": "IS_CONST",
                         **notional_metrics(const_res, C.IS_START, C.IS_END)})
            rows.append({"trial": tid, "cost_mult": mult, "period": "OOS_CONST",
                         **notional_metrics(const_res, C.OOS_START, C.OOS_END)})
            if mult == 1.0:
                return_matrix[tid] = const_res["equity_daily"].diff() / INITIAL
                trade_counts[tid] = {
                    "full": int(full.get("trades", 0)),
                    "is": int(is_r.get("trades", 0)),
                    "oos": int(oos_r.get("trades", 0)),
                    "full_const": int(notional_metrics(const_res, C.IS_START, C.OOS_END).get("trades", 0)),
                    "oos_const": int(notional_metrics(const_res, C.OOS_START, C.OOS_END).get("trades", 0)),
                }

        const_results[f"{tid}-C1.0"]["trades"].to_csv(OUT / f"{tid}_trades.csv", index=False)

    table = pd.DataFrame(rows)
    table.to_csv(OUT / "t2_trial_table.csv", index=False)

    # ---- benchmarks on the same windows
    d1 = C.load_series("D1")
    d1 = d1.loc[d1["time"] <= C.OOS_END].reset_index(drop=True)
    cost0 = C.CostModel()
    bench = {
        "IS": C.buy_and_hold(C.slice_period(d1, C.IS_START, C.IS_END), cost0),
        "OOS": C.buy_and_hold(C.slice_period(d1, C.OOS_START, C.OOS_END), cost0),
        "FULL": C.buy_and_hold(d1, cost0),
    }

    # ---- selection: best IS net Sharpe at baseline cost
    base = table[(table["period"] == "IS") & (table["cost_mult"] == 1.0)].copy()
    base = base.sort_values(["sharpe", "profit_factor"], ascending=False)
    best_tid = base.iloc[0]["trial"]
    best_oos = table[(table["trial"] == best_tid) & (table["period"] == "OOS")].set_index("cost_mult")

    # ---- statistics on baseline cost, OOS, constant-risk returns
    oos_rets = pd.DataFrame({
        tid: series.loc[(series.index >= C.OOS_START) & (series.index <= C.OOS_END)]
        for tid, series in return_matrix.items()
    })
    sr_by_trial = oos_rets.apply(
        lambda s: s.mean() / s.std() * np.sqrt(252) if s.std() > 0 else np.nan
    )
    sr_var = float(sr_by_trial.var() / 252.0)
    dsr_rows = {
        tid: C.deflated_sharpe(oos_rets[tid].dropna(), n_trials=32, sr_variance=sr_var)
        for tid in oos_rets.columns
    }
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

    rnd = random_entry_control(
        m, const_res, cost0, n_runs=300, actual_profit=None,
    )
    rnd["actual_profit_full"] = float(const_res["trades"]["net_pnl"].sum())
    rnd["excluded_terminal_trade"] = bool(
        (const_res["trades"]["exit_reason"] == "end_of_data").any()
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

    # ---- gate checks
    oos = best_oos.loc[1.0].to_dict()
    oos_const = table[(table["trial"] == best_tid) & (table["period"] == "OOS_CONST")
                      & (table["cost_mult"] == 1.0)].iloc[0].to_dict()
    full = table[(table["trial"] == best_tid) & (table["period"] == "FULL")
                 & (table["cost_mult"] == 1.0)].iloc[0].to_dict()
    full_const = table[(table["trial"] == best_tid) & (table["period"] == "FULL_CONST")
                       & (table["cost_mult"] == 1.0)].iloc[0].to_dict()
    stress15 = table[(table["trial"] == best_tid) & (table["period"] == "OOS_CONST")
                     & (table["cost_mult"] == 1.5)].iloc[0].to_dict()
    stress20 = table[(table["trial"] == best_tid) & (table["period"] == "OOS_CONST")
                     & (table["cost_mult"] == 2.0)].iloc[0].to_dict()

    full_trades = int(full.get("trades", 0))
    bh_oos_sharpe = float(bench["OOS"].get("sharpe") or -9)
    sel_rets = oos_rets[best_tid].dropna()
    hlz_t = float(sel_rets.mean() / sel_rets.std() * np.sqrt(len(sel_rets))) if sel_rets.std() > 0 else np.nan
    boot = C.bootstrap_sharpe_ci(sel_rets, n_boot=1000)

    gates = {
        "min_trades_100_full_sample": bool(full_trades >= 100),
        "net_pf_ge_1_20": bool((oos.get("profit_factor") or 0) >= 1.20),
        "net_sharpe_ge_0_50": bool((oos.get("sharpe") or -9) >= 0.50),
        "max_dd_le_25pct": bool((oos.get("max_dd_pct") or -999) >= -25.0),
        "positive_in_3_of_4_vol_regimes": bool(
            sum(1 for v in vol_perf.values() if (v.get("sharpe") or -9) > 0) >= 3
        ),
        "beats_buy_and_hold_sharpe": bool((oos.get("sharpe") or -9) > bh_oos_sharpe),
        "dsr_p_lt_0_10": bool((dsr_rows.get(best_tid, {}).get("p_value") or 1) < 0.10),
        "cost_stress_1_5x_no_sign_flip": bool(
            np.sign(stress15.get("net_profit") or 0) == np.sign(oos_const.get("net_profit") or 0)
            and (stress15.get("net_profit") or 0) != 0
        ),
    }
    gates["cost_stress_2_0x_no_sign_flip"] = bool(
        np.sign(stress20.get("net_profit") or 0) == np.sign(oos_const.get("net_profit") or 0)
        and (stress20.get("net_profit") or 0) != 0
    )

    # Verdict precedence: Section 11.12 makes a sub-100 trade count
    # INCONCLUSIVE, not pass or fail.
    failed = [k for k, v in gates.items() if v is False]
    if not gates["min_trades_100_full_sample"]:
        decision = "INCONCLUSIVE"
    elif failed:
        decision = "FAIL"
    else:
        decision = "PASS"

    summary = {
        "family": "T2",
        "trials": 18,
        "selected_by_is_sharpe": best_tid,
        "selected_params": {
            "pair": list(param_by_tid[best_tid]["pair"]),
            "stop": param_by_tid[best_tid]["stop"],
            "risk": param_by_tid[best_tid]["risk"],
        },
        "warmup_bars": WARMUP_BARS,
        "first_signal_bar": str(m.loc[m["signal_allowed"], "time"].iloc[0]),
        "pair_signal_counts": pair_signal_counts,
        "trade_counts_by_trial": trade_counts,
        "full_sample_trades": full_trades,
        "harvey_liu_zhu_t_oos": hlz_t,
        "bootstrap_sharpe_ci_oos": boot,
        "benchmarks": bench,
        "best_oos_by_cost": best_oos.to_dict(),
        "selected_constant_risk": const,
        "selected_full_const": full_const,
        "selected_oos_const": oos_const,
        "vol_regime_oos": vol_perf,
        "macro_regime_oos": macro_perf,
        "subperiod_oos": sub_perf,
        "subperiod_full": sub_full,
        "beta_alpha_oos": ba,
        "gates_oos": gates,
        "decision": decision,
        "deflated_sharpe_oos": dsr_rows,
        "reality_check_oos": rc,
        "random_entry": rnd,
        "notes": [
            "After a disaster stop the engine is flat until the next crossover.",
            "The 100-trade gate uses the full sample, 2008-2026.",
            "The stop distance uses the last completed D1 bar's ATR.",
            "Statistics use constant-risk notional daily returns.",
        ],
    }
    C.save_json(summary, OUT / "t2_summary.json")
    print(json.dumps({k: v for k, v in summary.items() if k != "deflated_sharpe_oos"},
                     indent=2, default=str))
    print("\nTrial table (baseline cost):")
    print(table[table["cost_mult"] == 1.0][
        ["trial", "period", "trades", "profit_factor", "sharpe", "max_dd_pct",
         "net_profit", "win_rate_pct", "cost_pct_of_gross"]
    ].to_string(index=False))


if __name__ == "__main__":
    main()
