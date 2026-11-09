"""Phase 2B - T3 time-series momentum overlay: six pre-registered trials.

Rules are taken from Docs/Strategy/Phase-2A-Trend-Following-Research.md
Section 8.3 and the grid in Section 11.7.

Pre-registered grid (3 x 2 = 6):
  lookback : 6, 12, 24 months (126, 252, 504 D1 bars)
  scaling  : scaled (10% target vol, 2.0x cap), unscaled (1.0x notional)

Frozen interpretation decisions (see reports/T3-methodology-note.md):
  * Signal is the sign of trailing total return on a completed D1 bar.
  * Rebalance on the last D1 bar of the calendar month; execute at the next
    D1 open.
  * 60-day EWMA volatility, span=60, adjust=False, annualised by sqrt(252).
  * No signal until 504 completed D1 bars (the longest lookback).
  * No stop. Monthly rebalance and sign flip are the only risk controls.
  * Costs are charged on turnover, split into buy-side (1.5 x spread) and
    sell-side (0.5 x spread), with half the round-turn commission per side.
  * Swap is a positive cost, subtracted (the corrected convention).
  * A trade is one position episode, from entry to the next sign flip.
  * The selected trial is the highest IS net Sharpe at baseline cost.

The runner writes results/T3/t3_trial_table.csv, t3_summary.json and the
per-trial episode logs. report_t3.py renders the report.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

import core as C

OUT = C.ROOT / "results" / "T3"
OUT.mkdir(parents=True, exist_ok=True)

INITIAL = C.INITIAL_CAPITAL
WARMUP_BARS = 504          # longest lookback, uniform across trials
TARGET_VOL = 0.10
LEV_CAP = 2.0
EWMA_SPAN = 60
LOOKBACKS = {6: 126, 12: 252, 24: 504}


# --------------------------------------------------------------------------
# Features
# --------------------------------------------------------------------------

def prepare_features() -> pd.DataFrame:
    d1 = C.load_series("D1")
    d1 = d1.loc[d1["time"] <= C.OOS_END].reset_index(drop=True)
    d1["logret"] = np.log(d1["close"]).diff()
    d1["vol_ann"] = (
        d1["logret"].ewm(span=EWMA_SPAN, adjust=False).std() * np.sqrt(C.TRADING_DAYS)
    )
    ym = d1["time"].dt.strftime("%Y-%m")
    d1["is_month_end"] = ym.ne(ym.shift(-1))
    d1["rollover_mult"] = np.where(d1["time"].dt.day_of_week == 2, 3, 1)
    d1["signal_allowed"] = np.arange(len(d1)) >= WARMUP_BARS
    for months, days in LOOKBACKS.items():
        d1[f"ret{months}"] = d1["close"] / d1["close"].shift(days) - 1.0
        d1[f"sign{months}"] = np.sign(d1[f"ret{months}"]).fillna(0.0).astype(int)
    return d1


def rebalance_signal_indices(m: pd.DataFrame) -> np.ndarray:
    mask = (
        m["is_month_end"].to_numpy(bool)
        & m["signal_allowed"].to_numpy(bool)
    )
    idx = np.flatnonzero(mask)
    return idx[idx < len(m) - 1]


# --------------------------------------------------------------------------
# Cost helpers: turnover is split into buy-side and sell-side transactions.
# --------------------------------------------------------------------------

def trade_cost(oz: float, buy: bool, spread: float, costs: C.CostModel) -> tuple[float, float]:
    """Return (spread_slippage_cost, commission_cost) for a transaction."""
    if oz <= 0:
        return 0.0, 0.0
    s = spread * costs.multiplier
    slip = 1.5 if buy else 0.5
    spread_cost = oz * s * slip
    commission = oz * costs.commission_per_oz_round_turn * costs.multiplier * 0.5
    return spread_cost, commission


# --------------------------------------------------------------------------
# Simulation
# --------------------------------------------------------------------------

def simulate(m: pd.DataFrame, months: int, scaled: bool, costs: C.CostModel,
             compound: bool = True, initial: float = INITIAL,
             sign_override: np.ndarray | None = None) -> dict:
    n = len(m)
    time = m["time"].to_numpy()
    o = m["open"].to_numpy(float)
    cl = m["close"].to_numpy(float)
    sp = m["spread"].to_numpy(float)
    vol = m["vol_ann"].to_numpy(float)
    roll = m["rollover_mult"].to_numpy(int)
    sign = (
        sign_override.astype(int)
        if sign_override is not None
        else m[f"sign{months}"].to_numpy(int)
    )
    me = m["is_month_end"].to_numpy(bool)
    allow = m["signal_allowed"].to_numpy(bool)

    equity = np.empty(n, dtype=float)
    equity[0] = initial
    pos = 0
    size = 0.0
    trades: list[dict] = []

    # Current episode accumulator.
    ep = None

    def start_episode(i: int, direction: int, open_cost: float, open_comm: float,
                      intraday_gross: float) -> dict:
        return {
            "entry_i": i,
            "entry_time": time[i],
            "entry_raw": o[i],
            "direction": direction,
            "gross": intraday_gross,
            "spread": open_cost,
            "commission": open_comm,
            "swap": 0.0,
            "notional_sum": abs(size) * cl[i],
            "bars": 0,
        }

    def finish_episode(ep: dict, exit_i: int, exit_raw: float, reason: str) -> None:
        notional_avg = ep["notional_sum"] / max(ep["bars"] + 1, 1)
        gross = ep["gross"]
        spread = ep["spread"]
        comm = ep["commission"]
        swap = ep["swap"]
        net = gross - spread - comm - swap
        holding = (time[exit_i] - time[ep["entry_i"]]) / np.timedelta64(1, "D")
        trades.append({
            "entry_time": ep["entry_time"],
            "exit_time": time[exit_i],
            "direction": ep["direction"],
            "entry_raw": ep["entry_raw"],
            "exit_raw": exit_raw,
            "size_oz": notional_avg / exit_raw if exit_raw > 0 else np.nan,
            "stop_distance": np.nan,
            "risk_dollars": 0.10 * notional_avg,
            "gross_pnl": gross,
            "spread_slip_cost": spread,
            "commission_cost": comm,
            "swap_cost": swap,
            "total_cost": spread + comm + swap,
            "net_pnl": net,
            "holding_days": holding,
            "holding_bars": exit_i - ep["entry_i"],
            "exit_reason": reason,
        })

    for i in range(1, n):
        rebal = bool(me[i - 1] and allow[i - 1] and i - 1 < n - 1)
        old_size = size
        old_pos = pos
        day_gross = 0.0
        cost_today = 0.0
        close_spread = close_comm = 0.0
        open_spread = open_comm = 0.0
        new_pos = pos
        target = size

        if rebal:
            raw = int(sign[i - 1])
            new_pos = raw if raw != 0 else pos
            if new_pos == 0:
                target = 0.0
            else:
                v = float(vol[i - 1])
                if not np.isfinite(v) or v <= 0:
                    target = size
                    new_pos = pos
                else:
                    weight = min(TARGET_VOL / v, LEV_CAP) if scaled else 1.0
                    base = equity[i - 1] if compound else initial
                    target = new_pos * weight * base / o[i] if base > 0 else 0.0

            # Overnight gap belongs to the old position.
            old_gap = old_size * (o[i] - cl[i - 1]) if old_pos != 0 else 0.0

            flip = old_pos != 0 and new_pos != old_pos
            if flip:
                # Close the old episode at this open, then open a new one.
                close_oz = abs(old_size)
                close_spread, close_comm = trade_cost(
                    close_oz, buy=(old_pos < 0), spread=sp[i], costs=costs
                )
                open_oz = abs(target)
                open_spread, open_comm = trade_cost(
                    open_oz, buy=(new_pos > 0), spread=sp[i], costs=costs
                )
                cost_today = close_spread + close_comm + open_spread + open_comm
                if ep is not None:
                    ep["gross"] += old_gap
                    ep["spread"] += close_spread
                    ep["commission"] += close_comm
                    ep["notional_sum"] += abs(old_size) * cl[i - 1]
                    ep["bars"] += i - ep["entry_i"] - ep["bars"]
                    finish_episode(ep, i, o[i], "flip")
                ep = None
                if new_pos != 0:
                    new_intraday = target * (cl[i] - o[i])
                    # The equity update must include the overnight gap earned
                    # by the old position; the new episode only owns the
                    # intraday move from the execution open.
                    day_gross = old_gap + new_intraday
                    size = target
                    pos = new_pos
                    ep = start_episode(i, new_pos, open_spread, open_comm, new_intraday)
                else:
                    day_gross = old_gap
            elif old_pos == 0 and new_pos != 0:
                # Flat to position.
                open_oz = abs(target)
                open_spread, open_comm = trade_cost(
                    open_oz, buy=(new_pos > 0), spread=sp[i], costs=costs
                )
                cost_today = open_spread + open_comm
                day_gross = target * (cl[i] - o[i])
                size = target
                pos = new_pos
                ep = start_episode(i, new_pos, open_spread, open_comm, day_gross)
            elif old_pos != 0 and new_pos == 0:
                # Position to flat.
                close_oz = abs(old_size)
                close_spread, close_comm = trade_cost(
                    close_oz, buy=(old_pos < 0), spread=sp[i], costs=costs
                )
                cost_today = close_spread + close_comm
                if ep is not None:
                    ep["gross"] += old_gap
                    ep["spread"] += close_spread
                    ep["commission"] += close_comm
                    ep["notional_sum"] += abs(old_size) * cl[i - 1]
                    ep["bars"] += i - ep["entry_i"] - ep["bars"]
                    finish_episode(ep, i, o[i], "flip")
                ep = None
                day_gross = old_gap
                size = 0.0
                pos = 0
            elif old_pos != 0 and new_pos == old_pos:
                # Same-direction resize: one turnover transaction, same episode.
                traded = target - old_size
                buy = traded > 0
                sp_cost, cm_cost = trade_cost(abs(traded), buy=buy, spread=sp[i], costs=costs)
                cost_today = sp_cost + cm_cost
                day_gross = old_gap + target * (cl[i] - o[i])
                if ep is not None:
                    ep["gross"] += day_gross
                    ep["spread"] += sp_cost
                    ep["commission"] += cm_cost
                size = target
                pos = new_pos
            else:
                # Flat remains flat (raw sign 0 and no position).
                size = 0.0
                pos = 0
        else:
            day_gross = size * (cl[i] - cl[i - 1]) if pos != 0 else 0.0
            if ep is not None:
                ep["gross"] += day_gross

        # Swap accrual on the end-of-day position.
        swap_cost = 0.0
        if size != 0:
            rate = costs.swap_long_per_oz_day if size > 0 else costs.swap_short_per_oz_day
            swap_cost = -rate * costs.multiplier * abs(size) * roll[i]
            if ep is not None:
                ep["swap"] += swap_cost

        equity[i] = equity[i - 1] + day_gross - cost_today - swap_cost

        if ep is not None:
            ep["notional_sum"] += abs(size) * cl[i]
            ep["bars"] = i - ep["entry_i"]

    # Close the open episode at the last close.
    close_cost = 0.0
    if pos != 0 and ep is not None:
        close_oz = abs(size)
        sp_cost, cm_cost = trade_cost(
            close_oz, buy=(pos < 0), spread=sp[n - 1], costs=costs
        )
        ep["spread"] += sp_cost
        ep["commission"] += cm_cost
        ep["notional_sum"] += abs(size) * cl[n - 1]
        ep["bars"] = n - 1 - ep["entry_i"]
        finish_episode(ep, n - 1, cl[n - 1], "end_of_data")
        close_cost = sp_cost + cm_cost
        equity[n - 1] -= close_cost

    eq = pd.Series(equity, index=pd.DatetimeIndex(time), name="equity")
    tdf = pd.DataFrame(trades)
    return {
        "equity_daily": eq,
        "trades": tdf,
        "months": months,
        "scaled": scaled,
        "cost_multiplier": costs.multiplier,
    }


# --------------------------------------------------------------------------
# Period metrics (same definitions as T1/T2)
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
# OLS alpha t-statistic versus buy-and-hold
# --------------------------------------------------------------------------

def alpha_tstat(strategy: pd.Series, benchmark: pd.Series) -> dict:
    df = pd.concat([strategy.rename("s"), benchmark.rename("b")], axis=1).dropna()
    if len(df) < 30:
        return {"beta": np.nan, "alpha_annual": np.nan, "alpha_t": np.nan}
    x = df["b"].to_numpy(float)
    y = df["s"].to_numpy(float)
    xm = x - x.mean()
    beta = float(np.sum(xm * (y - y.mean())) / np.sum(xm ** 2))
    alpha_d = float(y.mean() - beta * x.mean())
    resid = y - (alpha_d + beta * x)
    sigma2 = float(np.sum(resid ** 2) / max(len(df) - 2, 1))
    se_alpha = float(np.sqrt(sigma2 * (1.0 / len(df) + x.mean() ** 2 / np.sum(xm ** 2))))
    return {
        "beta": beta,
        "alpha_annual": alpha_d * C.TRADING_DAYS * 100.0,
        "alpha_t": float(alpha_d / se_alpha) if se_alpha > 0 else np.nan,
    }


# --------------------------------------------------------------------------
# Random-entry / matched-exposure control: permute the sign of the signal on
# the actual rebalance dates, keeping the weight schedule and the long/short
# count unchanged.
# --------------------------------------------------------------------------

def random_sign_control(m: pd.DataFrame, months: int, scaled: bool,
                        costs: C.CostModel, actual_profit: float | None = None,
                        n_runs: int = 500, seed: int = 20261106) -> dict:
    """Permute the actual sign labels across rebalance dates.

    The number of long, short and zero months, the rebalance calendar and the
    volatility/weight schedule are unchanged. Only the direction assigned to
    each rebalance is randomised, so the control tests whether the momentum
    sign carries information rather than whether the exposure does.
    """
    idx = rebalance_signal_indices(m)
    base_sign = m[f"sign{months}"].to_numpy(int).copy()
    values = base_sign[idx].copy()
    rng = np.random.default_rng(seed)
    profits = np.empty(n_runs)
    for r in range(n_runs):
        perm = rng.permutation(values)
        override = base_sign.copy()
        override[idx] = perm
        res = simulate(m, months, scaled, costs, compound=False, sign_override=override)
        profits[r] = float(res["equity_daily"].iloc[-1] - INITIAL)
    out = {
        "runs": n_runs,
        "rebalance_dates": int(len(idx)),
        "long_months_actual": int((values > 0).sum()),
        "short_months_actual": int((values < 0).sum()),
        "zero_months_actual": int((values == 0).sum()),
        "profit_median": float(np.median(profits)),
        "profit_p95": float(np.percentile(profits, 95)),
        "profit_p05": float(np.percentile(profits, 5)),
    }
    if actual_profit is not None:
        out["actual_profit"] = float(actual_profit)
        out["percentile_of_actual"] = float((profits < actual_profit).mean() * 100.0)
    return out


# --------------------------------------------------------------------------
# Trial runner
# --------------------------------------------------------------------------

def main() -> None:
    print("preparing D1 features ...", flush=True)
    m = prepare_features()
    print(f"  D1 rows: {len(m)}  {m['time'].iloc[0]} .. {m['time'].iloc[-1]}", flush=True)
    first_monthend = m.loc[m["signal_allowed"] & m["is_month_end"], "time"].iloc[0]
    print(f"  first eligible month-end: {first_monthend}", flush=True)
    print(f"  rebalance dates: {len(rebalance_signal_indices(m))}", flush=True)

    grid = [
        {"months": months, "scaled": scaled}
        for months, scaled in itertools.product([6, 12, 24], [True, False])
    ]

    rows = []
    const_results = {}
    return_matrix = {}
    param_by_tid = {}
    trade_counts = {}

    for gi, params in enumerate(grid, start=1):
        tag = "SCALED" if params["scaled"] else "UNSCALED"
        tid = f"T3-{gi:02d}-LB{params['months']}-{tag}"
        param_by_tid[tid] = params
        print(f"trial {tid}", flush=True)
        for mult in (1.0, 1.5, 2.0):
            costs = C.CostModel(multiplier=mult)
            res = simulate(m, params["months"], params["scaled"], costs,
                           compound=True)
            rows.append({"trial": tid, "cost_mult": mult, "period": "FULL",
                         **period_report(res, C.IS_START, C.OOS_END)})
            rows.append({"trial": tid, "cost_mult": mult, "period": "IS",
                         **period_report(res, C.IS_START, C.IS_END)})
            rows.append({"trial": tid, "cost_mult": mult, "period": "OOS",
                         **period_report(res, C.OOS_START, C.OOS_END)})

            const_res = simulate(m, params["months"], params["scaled"], costs,
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
                    "full": int(period_report(res, C.IS_START, C.OOS_END).get("trades", 0)),
                    "is": int(period_report(res, C.IS_START, C.IS_END).get("trades", 0)),
                    "oos": int(period_report(res, C.OOS_START, C.OOS_END).get("trades", 0)),
                    "full_const": int(notional_metrics(const_res, C.IS_START, C.OOS_END).get("trades", 0)),
                    "oos_const": int(notional_metrics(const_res, C.OOS_START, C.OOS_END).get("trades", 0)),
                }
        const_results[f"{tid}-C1.0"]["trades"].to_csv(OUT / f"{tid}_trades.csv", index=False)

    table = pd.DataFrame(rows)
    table.to_csv(OUT / "t3_trial_table.csv", index=False)

    # ---- benchmarks on the same windows
    d1 = C.load_series("D1")
    d1 = d1.loc[d1["time"] <= C.OOS_END].reset_index(drop=True)
    cost0 = C.CostModel()
    bench = {
        "IS": C.buy_and_hold(C.slice_period(d1, C.IS_START, C.IS_END), cost0),
        "OOS": C.buy_and_hold(C.slice_period(d1, C.OOS_START, C.OOS_END), cost0),
        "FULL": C.buy_and_hold(d1, cost0),
    }

    # ---- selection: highest IS net Sharpe at baseline cost
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

    const_res = const_results[f"{best_tid}-C1.0"]
    const = {
        "FULL": notional_metrics(const_res, C.IS_START, C.OOS_END),
        "IS": notional_metrics(const_res, C.IS_START, C.IS_END),
        "OOS": notional_metrics(const_res, C.OOS_START, C.OOS_END),
    }
    const_res["trades"].to_csv(OUT / f"{best_tid}_constant_risk_trades.csv", index=False)

    actual_full_profit = float(const_res["equity_daily"].iloc[-1] - INITIAL)
    rnd = random_sign_control(
        m, param_by_tid[best_tid]["months"], param_by_tid[best_tid]["scaled"],
        cost0, actual_profit=actual_full_profit, n_runs=500,
    )

    # ---- robustness lenses, OOS constant-risk
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
    ba = alpha_tstat(rets_oos, bh_close_all.pct_change().reindex(rets_oos.index))

    # 2011-2015 bear-market stress (in-sample window, reported separately).
    # Evaluated on the constant-risk notional curve so it is directly comparable
    # with the OOS attribution and statistical lenses.
    BEAR_START = pd.Timestamp("2011-01-01", tz="UTC")
    BEAR_END = pd.Timestamp("2015-12-31 23:59:59", tz="UTC")
    bear = notional_metrics(const_res, BEAR_START, BEAR_END)
    bear_const_trades = const_res["trades"].loc[
        (const_res["trades"]["entry_time"] >= BEAR_START)
        & (const_res["trades"]["entry_time"] <= BEAR_END)
    ]
    bear_pnl = float(bear_const_trades["net_pnl"].sum()) if not bear_const_trades.empty else 0.0
    bear_worst = float(bear_const_trades["net_pnl"].min()) if not bear_const_trades.empty else 0.0
    bear_outlier_explains = bool(bear_pnl < 0 and (bear_pnl - bear_worst) >= 0)

    # Reconcile the equity-curve P&L of the window with the episode-entry
    # attribution. An episode that starts before the window contributes only
    # its in-window portion to the equity curve; an episode that ends after
    # the window contributes only its in-window portion but appears in full in
    # the episode sum. Segment daily P&L by the open episode to measure both.
    _eq = const_res["equity_daily"]
    _idx = _eq.index
    _ids = np.full(len(_eq), -1, dtype=int)
    for _k, _row in const_res["trades"].iterrows():
        _ids[(_idx >= _row["entry_time"]) & (_idx < _row["exit_time"])] = _k
    _seg = pd.Series(_ids, index=_idx)
    _daily = _eq.diff().fillna(0.0)
    _win = (_idx >= BEAR_START) & (_idx <= BEAR_END)
    _inside = set(bear_const_trades.index)
    _prior = set(const_res["trades"].index[
        (const_res["trades"]["entry_time"] < BEAR_START)
        & (const_res["trades"]["exit_time"] > BEAR_START)
    ])
    bear_prior_in_window = float(_daily[_win & _seg.isin(_prior)].sum())
    bear_inside_after_window = float(
        _daily[(~_win) & (_idx > BEAR_END) & _seg.isin(_inside)].sum()
    )
    bear_boundary_residual = float(
        bear.get("net_profit", 0.0) - bear_pnl + bear_inside_after_window
        - bear_prior_in_window
    )

    # ---- gate checks
    oos = best_oos.loc[1.0].to_dict()
    oos_const = table[(table["trial"] == best_tid) & (table["period"] == "OOS_CONST")
                      & (table["cost_mult"] == 1.0)].iloc[0].to_dict()
    full = table[(table["trial"] == best_tid) & (table["period"] == "FULL")
                 & (table["cost_mult"] == 1.0)].iloc[0].to_dict()
    stress15 = table[(table["trial"] == best_tid) & (table["period"] == "OOS_CONST")
                     & (table["cost_mult"] == 1.5)].iloc[0].to_dict()
    stress20 = table[(table["trial"] == best_tid) & (table["period"] == "OOS_CONST")
                     & (table["cost_mult"] == 2.0)].iloc[0].to_dict()

    full_trades = int(trade_counts[best_tid]["full"])
    bh_oos_sharpe = float(bench["OOS"].get("sharpe") or -9)
    sel_rets = oos_rets[best_tid].dropna()
    hlz_t = float(sel_rets.mean() / sel_rets.std() * np.sqrt(len(sel_rets))) if sel_rets.std() > 0 else np.nan
    boot = C.bootstrap_sharpe_ci(sel_rets, n_boot=1000)

    # Paired scaled/unscaled comparison for the selected lookback.
    pair_trials = [t for t, p in param_by_tid.items()
                   if p["months"] == param_by_tid[best_tid]["months"]]
    pair_oos = {
        t: table[(table["trial"] == t) & (table["period"] == "OOS_CONST")
                 & (table["cost_mult"] == 1.0)].iloc[0].to_dict()
        for t in pair_trials
    }
    scaled_t = [t for t in pair_trials if param_by_tid[t]["scaled"]][0]
    unscaled_t = [t for t in pair_trials if not param_by_tid[t]["scaled"]][0]
    scaled_sr = float(pair_oos[scaled_t].get("sharpe") or -9)
    unscaled_sr = float(pair_oos[unscaled_t].get("sharpe") or -9)

    macro_pos = sum(1 for v in macro_perf.values() if (v.get("sharpe") or -9) > 0)
    gates = {
        "trade_count_ge_100_full_sample": bool(full_trades >= 100),
        "net_sharpe_ge_0_40": bool((oos_const.get("sharpe") or -9) >= 0.40),
        "max_dd_le_25pct": bool((oos.get("max_dd_pct") or -999) >= -25.0),
        "macro_positive_in_2_of_3_oos": bool(macro_pos >= 2),
        "bear_2011_2015_ok": bool((bear.get("sharpe") or -9) > 0 or bear_outlier_explains),
        "not_just_buy_and_hold_beta": bool(
            (ba.get("alpha_t") or -9) > 1.96 and (ba.get("alpha_annual") or -9) > 0
        ),
        "scaling_not_the_whole_result": bool(not (scaled_sr >= 0.40 and unscaled_sr < 0.40)),
        "cost_stress_1_5x_no_sign_flip": bool(
            np.sign(stress15.get("net_profit") or 0) == np.sign(oos_const.get("net_profit") or 0)
            and (stress15.get("net_profit") or 0) != 0
        ),
        "dsr_p_lt_0_10": bool((dsr_rows.get(best_tid, {}).get("p_value") or 1) < 0.10),
    }
    # The 2.0x multiple is reported as an additional stress, not as a formal
    # gate: Section 11.12 makes only the 1.5x sign flip a kill criterion.
    cost_stress = {
        "net_1_0x": float(oos_const.get("net_profit") or 0.0),
        "net_1_5x": float(stress15.get("net_profit") or 0.0),
        "net_2_0x": float(stress20.get("net_profit") or 0.0),
        "trade_net_1_0x": float(oos_const.get("net_pnl") or 0.0),
        "trade_net_1_5x": float(stress15.get("net_pnl") or 0.0),
        "trade_net_2_0x": float(stress20.get("net_pnl") or 0.0),
        "sign_flip_1_5x": bool(
            np.sign(stress15.get("net_profit") or 0) != np.sign(oos_const.get("net_profit") or 0)
        ),
        "sign_flip_2_0x": bool(
            np.sign(stress20.get("net_profit") or 0) != np.sign(oos_const.get("net_profit") or 0)
        ),
    }
    negative_oos_subperiods = [
        k for k, v in sub_perf.items() if (v.get("total_return_pct") or 0.0) < 0
    ]

    failed = [k for k, v in gates.items() if v is False]
    if not gates["trade_count_ge_100_full_sample"]:
        decision = "INCONCLUSIVE"
    elif failed:
        decision = "FAIL"
    elif bear.get("sharpe", 1) <= 0 and bear_outlier_explains:
        decision = "CONDITIONAL"
    else:
        decision = "PASS"

    summary = {
        "family": "T3",
        "trials": 6,
        "selected_by_is_sharpe": best_tid,
        "selected_params": {
            "lookback_months": param_by_tid[best_tid]["months"],
            "scaled": param_by_tid[best_tid]["scaled"],
        },
        "warmup_bars": WARMUP_BARS,
        "first_eligible_month_end": str(first_monthend),
        "rebalance_dates": int(len(rebalance_signal_indices(m))),
        "trade_counts_by_trial": trade_counts,
        "full_sample_trades": full_trades,
        "harvey_liu_zhu_t_oos": hlz_t,
        "bootstrap_sharpe_ci_oos": boot,
        "benchmarks": bench,
        "best_oos_by_cost": best_oos.to_dict(),
        "selected_constant_risk": const,
        "selected_oos_const": oos_const,
        "vol_regime_oos": vol_perf,
        "macro_regime_oos": macro_perf,
        "subperiod_full": sub_full,
        "subperiod_oos": sub_perf,
        "beta_alpha_oos": ba,
        "bear_2011_2015": {
            "metrics": bear,
            "constant_risk_trade_pnl": bear_pnl,
            "worst_trade": bear_worst,
            "single_outlier_explains_failure": bear_outlier_explains,
            "prior_episode_in_window_pnl": bear_prior_in_window,
            "inside_episode_after_window_pnl": bear_inside_after_window,
            "boundary_residual": bear_boundary_residual,
        },
        "scaled_vs_unscaled_selected_lookback": {
            "lookback_months": param_by_tid[best_tid]["months"],
            "scaled_trial": scaled_t,
            "unscaled_trial": unscaled_t,
            "scaled_oos_sharpe": scaled_sr,
            "unscaled_oos_sharpe": unscaled_sr,
        },
        "gates_oos": gates,
        "cost_stress_oos_const": cost_stress,
        "negative_oos_subperiods": negative_oos_subperiods,
        "random_control_beats_p95": bool(
            (rnd.get("actual_profit") or 0.0) > (rnd.get("profit_p95") or 0.0)
        ),
        "decision": decision,
        "deflated_sharpe_oos": dsr_rows,
        "reality_check_oos": rc,
        "random_entry": rnd,
        "notes": [
            "A trade is one position episode between sign flips, not a monthly size adjustment.",
            "The random control permutes the actual sign labels across rebalance dates.",
            "The 2011-2015 bear window is in-sample and is reported as a stress test.",
            "Statistics use constant-risk notional daily returns.",
        ],
    }
    C.save_json(summary, OUT / "t3_summary.json")
    print(json.dumps({k: v for k, v in summary.items() if k != "deflated_sharpe_oos"},
                     indent=2, default=str))
    print("\nTrial table (baseline cost):")
    print(table[table["cost_mult"] == 1.0][
        ["trial", "period", "trades", "profit_factor", "sharpe", "max_dd_pct",
         "net_profit", "win_rate_pct", "cost_pct_of_gross"]
    ].to_string(index=False))


if __name__ == "__main__":
    main()
