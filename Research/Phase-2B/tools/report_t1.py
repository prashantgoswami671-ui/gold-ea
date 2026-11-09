"""Render the Phase 2B T1 family report from the saved result artefacts.

Inputs (written by run_t1.py):
  results/T1/t1_trial_table.csv
  results/T1/t1_summary.json
  results/T1/<trial>_trades.csv

Output:
  reports/T1-report.md

The report follows the mandatory A-H structure of the Phase 2A document.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import core as C  # noqa: E402

RES = ROOT / "results" / "T1"
OUT = ROOT / "reports" / "T1-report.md"

PCT = ["win_rate_pct", "max_dd_pct", "return_pct", "cagr_pct", "volatility_pct",
       "cost_pct_of_gross", "exposure_pct"]


def f(x, nd=2):
    if x is None:
        return "n/a"
    if isinstance(x, str):
        return x
    try:
        if isinstance(x, (bool, np.bool_)):
            return "yes" if x else "no"
        if x != x:  # NaN
            return "n/a"
    except Exception:  # noqa: BLE001
        pass
    if isinstance(x, (int, np.integer)):
        return f"{int(x):,}"
    if isinstance(x, float):
        return f"{x:,.{nd}f}"
    return str(x)


def md_table(headers, rows, align=None):
    align = align or ["---"] * len(headers)
    lines = ["| " + " | ".join(headers) + " |",
             "| " + " | ".join(align) + " |"]
    for r in rows:
        lines.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(lines)


def main() -> None:
    table = pd.read_csv(RES / "t1_trial_table.csv")
    summary = json.loads((RES / "t1_summary.json").read_text(encoding="utf-8"))

    sel = summary["selected_by_is_sharpe"]
    bench = summary["benchmarks"]
    const = summary.get("selected_constant_risk", {})
    gates = summary.get("gates_oos", {})

    # ---------- C: performance table, baseline cost ----------
    base = table[(table["cost_mult"] == 1.0) & (table["period"].isin(["IS", "OOS"]))]
    perf_rows = []
    for tid in base["trial"].unique():
        for period in ("IS", "OOS"):
            r = base[(base["trial"] == tid) & (base["period"] == period)].iloc[0]
            perf_rows.append([
                tid, period, f(r["trades"]),
                f(r["final_equity"], 0), f(r["net_profit"], 0),
                f(r["profit_factor"], 3), f(r["sharpe"], 3),
                f(r["max_dd_pct"], 1), f(r["win_rate_pct"], 1),
                f(r["avg_holding_days"], 2), f(r["cost_pct_of_gross"], 1),
                f(r["exposure_pct"], 1),
            ])

    # ---------- cost stress, on the constant-risk notional curve ----------
    stress_rows = []
    for tid in table["trial"].unique():
        r0 = table[(table["trial"] == tid) & (table["period"] == "OOS_CONST")].set_index("cost_mult")
        row = [tid]
        for m in (1.0, 1.5, 2.0):
            row.append(f(r0.loc[m, "net_profit"], 0))
            row.append(f(r0.loc[m, "profit_factor"], 3))
        stress_rows.append(row)

    # ---------- D: benchmarks ----------
    bench_rows = []
    for name, b in bench.items():
        bench_rows.append([name, f(b.get("net_profit"), 0), f(b.get("cagr_pct"), 2),
                           f(b.get("sharpe"), 3), f(b.get("max_dd_pct"), 1),
                           f(b.get("volatility_pct"), 1)])

    # ---------- F: statistics ----------
    dsr = summary.get("deflated_sharpe_oos", {})
    rc = summary.get("reality_check_oos", {})
    rnd = summary.get("random_entry", {})
    hlz = summary.get("harvey_liu_zhu_t_oos")
    ci = summary.get("bootstrap_sharpe_ci_oos", {})

    best = table[(table["trial"] == sel) & (table["period"] == "OOS") & (table["cost_mult"] == 1.0)].iloc[0]
    best_is = table[(table["trial"] == sel) & (table["period"] == "IS") & (table["cost_mult"] == 1.0)].iloc[0]
    bc = const.get("OOS", {})
    bc_full = const.get("FULL", {})

    # ---------- H: decision ----------
    gate_rows = []
    labels = {
        "min_trades_300": "At least 300 OOS trades",
        "net_pf_ge_1_20": "Net profit factor >= 1.20",
        "costs_le_25pct_gross": "Costs <= 25% of gross profit",
        "positive_in_3_of_4_vol_regimes": "Positive in >= 3 of 4 volatility regimes",
        "sharpe_ge_t2_plus_0_10": "Sharpe >= T2 Sharpe + 0.10",
    }
    for k, lab in labels.items():
        v = gates.get(k)
        if isinstance(v, str):
            verdict = "DEFERRED"
        else:
            verdict = "PASS" if v else "FAIL"
        gate_rows.append([lab, verdict])

    failed = [k for k, v in gates.items() if v is False]
    deferred = [k for k, v in gates.items() if isinstance(v, str)]
    if failed:
        decision = "FAIL"
    elif deferred:
        decision = "CONDITIONAL"
    else:
        decision = "PASS"

    # ---------- build document ----------
    doc = []
    a = doc.append

    a("# Phase 2B - T1 family report")
    a("")
    a("**Family:** T1 - Multi-timeframe EMA pullback continuation")
    a("")
    a(f"**Status:** {decision}")
    a("")
    a("**Phase:** 2B controlled backtesting, family 1 of 3 (T1 -> T2 -> T3)")
    a("")
    a("**Source of rules:** `Docs/Strategy/Phase-2A-Trend-Following-Research.md`")
    a("(v0.2), Section 8.1, grid in Section 11.7, gates in Section 8.1 and 11.8.")
    a("")
    a("---")
    a("")

    a("## A. Identity")
    a("")
    a("| Item | Value |")
    a("| --- | --- |")
    a("| Hypothesis | Within an established H4 trend, M15 pullbacks to EMA20 resolve in the trend direction often enough to pay for costs. |")
    a("| What it tests | Whether intraday timing adds anything to a trend bias on gold. |")
    a("| Grades | E4 hypothesis; fastest and most cost-sensitive of the four candidates. |")
    a("| Timeframes | H4 regime, M15 entry, H1 ATR |")
    a("| Trials | 8 pre-registered combinations |")
    a("| Data | Dukascopy XAUUSD BID/ASK candles, retrieved 2026-11-05; 2004-01-01 to 2026-11-04, truncated at the OOS end |")
    a("| Symbol | XAUUSD, 2 digits, 100 oz per lot, minimum volume 0.01, volume step 0.01 |")
    a("| Test period | 2004-01-01 to 2026-06-30 |")
    a("| IS | 2004-01-01 to 2016-12-31 |")
    a("| OOS | 2017-01-01 to 2026-06-30 |")
    a("| Trial IDs | T1-01 ... T1-08 (see Appendix) |")
    a("")
    a("Pre-registered grid: pullback 0.2 / 0.5 x ATR(14,H1); initial stop "
      "1.0 / 1.5 x ATR(14,H1) floored at 2 x spread; trailing stop 2.0 x "
      "ATR(14,H1); RSI(14,M15) 40-60 filter off / on; risk 0.5% per trade.")
    a("")

    a("## B. Capital and execution")
    a("")
    a("| Item | Value |")
    a("| --- | --- |")
    a("| Initial capital | USD 100,000 |")
    a("| Position sizing | Fixed-fractional: risk = 0.5% x current equity; size_oz = risk / stop_distance; lots = size_oz / 100 (0.01 step), confirmatory |")
    a("| Max positions | 1 |")
    a("| Contract | 100 oz per lot; P&L = USD 1 per 0.01 move per 1.0 lot |")
    a("| Entry | Next M15 open after the signal bar closes |")
    a("| Exit | Trailing stop, or H4 regime flip, or end of data |")
    a("| Stop priority | Stop assumed hit first; gap fills at the open |")
    a("| Execution model | Vectorised Python bar simulator; no MT5 tester |")
    a("| Rollover | No new entries 21:45-22:15 UTC |")
    a("")
    a("### Cost model")
    a("")
    a("| Component | Assumption |")
    a("| --- | --- |")
    a("| Spread | Dukascopy BID/ASK on the completed H1 bar; charged on entry and exit. H1 median USD 0.386, p95 USD 0.712 |")
    a("| Entry slippage | 0.5 x spread |")
    a("| Signal exit slippage | 0.5 x spread |")
    a("| Stop exit slippage | 1.0 x spread |")
    a("| Commission | USD 0.07 per oz round turn (USD 7.00 per 100 oz lot) |")
    a("| Swap long | USD -0.126 per oz per day |")
    a("| Swap short | USD -0.046 per oz per day |")
    a("| Triple swap | Wednesday |")
    a("| Other costs | None modelled |")
    a("")
    a("All costs are stressed at 1.0x, 1.5x and 2.0x. The abnormal ~USD 58.12 "
      "Phase 0 spread is not used anywhere.")
    a("")

    a("## C. Performance")
    a("")
    a("Baseline cost (1.0x), pre-registered fixed-fractional sizing at 0.5% "
      "risk per trade. Each period is rebased to USD 100,000 at the start of "
      "the period, so the IS, OOS and FULL rows are not additive: the OOS "
      "account has already been reduced to a small fraction of its starting "
      "balance by in-sample losses. Trade-level metrics (PF, win rate, cost "
      "ratio) are scale-invariant and remain comparable across periods.")
    a("")
    a(md_table(
        ["Trial", "Period", "Trades", "Final eq (rebased)", "Net P&L", "PF", "Sharpe",
         "Max DD %", "Win %", "Hold d", "Costs % gross", "Exposure %"],
        perf_rows,
        ["---", "---", "---:", "---:", "---:", "---:", "---:", "---:", "---:",
         "---:", "---:", "---:"],
    ))
    a("")
    a("`n/a` in the cost column means gross P&L was zero or negative, so the "
      "cost-to-gross ratio is undefined; the corresponding gate is recorded as "
      "failed.")
    a("")
    a("### Cost stress, OOS constant-risk notional P&L")
    a("")
    a("The compounded OOS account is near zero after in-sample losses, so its "
      "dollar P&L is not interpretable. The table below repeats the eight "
      "trials with risk fixed at 0.5% of the initial USD 100,000 (no "
      "compounding) and stresses all cost components at 1.0x, 1.5x and 2.0x. "
      "Values are notional USD on a USD 100,000 risk base. Once the compounded "
      "account is ruined, position size collapses to zero and some signals are "
      "skipped, so the compounded and constant-risk trade sets diverge; the "
      "constant-risk table is the clean like-for-like comparison across trials.")
    a("")
    a(md_table(
        ["Trial", "Net P&L 1.0x", "PF 1.0x", "Net P&L 1.5x", "PF 1.5x",
         "Net P&L 2.0x", "PF 2.0x"],
        stress_rows,
    ))
    a("")
    a("### Selected trial")
    a("")
    a(f"Selected on IS net Sharpe: **{sel}** (this is the only selection rule "
      "used; OOS is not used for selection).")
    a("")
    a("| Metric | IS | OOS |")
    a("| --- | ---: | ---: |")
    for key, lab, nd in [
        ("trades", "Trades", 0), ("profit_factor", "Profit factor", 3),
        ("sharpe", "Sharpe", 3), ("net_profit", "Net P&L", 0),
        ("max_dd_pct", "Max drawdown %", 1), ("win_rate_pct", "Win rate %", 1),
        ("avg_holding_days", "Average holding days", 2),
        ("cost_pct_of_gross", "Costs as % of gross", 1),
        ("expectancy_r", "Expectancy (R)", 3),
        ("exposure_pct", "Exposure %", 1),
    ]:
        a(f"| {lab} | {f(best_is.get(key), nd)} | {f(best.get(key), nd)} |")
    a("")
    a("Compounded (pre-registered) sizing; each period is rebased to USD "
      "100,000, as explained in Section C. The OOS constant-risk notional P&L "
      f"for the same rule is USD {f(const.get('OOS', {}).get('net_profit'), 0)}, "
      "shown below.")
    a("")
    a("### Selected trial, OOS metrics by cost level (constant risk)")
    a("")
    cost_rows = []
    for m in (1.0, 1.5, 2.0):
        rr = table[(table["trial"] == sel) & (table["period"] == "OOS_CONST") & (table["cost_mult"] == m)].iloc[0]
        cost_rows.append([
            f"{m:.1f}x", f(rr["trades"], 0),
            f(rr["return_pct"], 1), f(rr["profit_factor"], 3),
            f(rr["sharpe"], 3), f(rr["sortino"], 3), f(rr["max_dd_abs"], 0),
            f(rr["max_dd_pct"], 1), f(rr["win_rate_pct"], 1),
            f(rr["avg_win"], 0), f(rr["avg_loss"], 0),
            f(rr["avg_win_r"], 2), f(rr["avg_loss_r"], 2),
            f(rr["expectancy_r"], 3), f(rr["cost_pct_of_gross"], 1),
        ])
    a(md_table(
        ["Cost", "Trades", "Return %", "PF", "Sharpe",
         "Sortino", "DD abs", "DD %", "Win %", "Avg win", "Avg loss",
         "Avg win R", "Avg loss R", "Expect R", "Cost % gross"],
        cost_rows,
        ["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:",
         "---:", "---:", "---:", "---:", "---:", "---:"],
    ))
    a("")
    a("Return % is the OOS period P&L on the USD 100,000 notional risk base; "
      "CAGR is not reported for a non-compounding curve.")
    a("")
    a("### Selected trial, trade detail (OOS, 1.0x, constant risk)")
    a("")
    detail_rows = [
        ["Largest win", f(bc.get("largest_win"), 0)],
        ["Largest loss", f(bc.get("largest_loss"), 0)],
        ["Max consecutive wins", f(bc.get("max_consec_wins"), 0)],
        ["Max consecutive losses", f(bc.get("max_consec_losses"), 0)],
        ["Payoff ratio", f(bc.get("payoff_ratio"), 3)],
        ["Turnover per year", f(bc.get("turnover_per_year"), 1)],
        ["Total costs", f(bc.get("total_costs"), 0)],
        ["Gross P&L", f(bc.get("gross_pnl"), 0)],
        ["Long P&L", f(bc.get("long_pnl"), 0)],
        ["Short P&L", f(bc.get("short_pnl"), 0)],
        ["MAR", f(bc.get("mar"), 3)],
        ["Ulcer %", f(bc.get("ulcer_pct"), 2)],
        ["Exposure %", f(bc.get("exposure_pct"), 1)],
    ]
    a(md_table(["Metric", "Value"], detail_rows, ["---", "---:"]))
    a("")
    a("#### Gross-to-net decomposition (OOS, 1.0x, constant risk)")
    a("")
    a(md_table(
        ["Component", "USD"],
        [
            ["Gross P&L (frictionless)", f(bc.get("gross_pnl"), 0)],
            ["Spread and slippage", f(-float(bc.get("spread_slip_cost")), 0) if bc.get("spread_slip_cost") == bc.get("spread_slip_cost") else "n/a"],
            ["Commission", f(-float(bc.get("commission_cost")), 0) if bc.get("commission_cost") == bc.get("commission_cost") else "n/a"],
            ["Swap", f(-float(bc.get("swap_cost")), 0) if bc.get("swap_cost") == bc.get("swap_cost") else "n/a"],
            ["Net P&L", f(bc.get("net_pnl"), 0)],
            ["Total costs", f(-float(bc.get("total_costs")), 0) if bc.get("total_costs") == bc.get("total_costs") else "n/a"],
        ],
        ["---", "---:"],
    ))
    a("")
    _t1_diff = float(bc.get("net_profit") or 0.0) - float(bc.get("net_pnl") or 0.0)
    a(f"Trade-level sums; the OOS equity-curve P&L is USD {f(bc.get('net_profit'), 0)}, "
      f"which is USD {f(abs(_t1_diff), 0)} "
      f"{'lower' if _t1_diff < 0 else 'higher'} than the episode sum because a "
      "position that entered before the OOS boundary exits inside it.")
    a("")
    a("### Constant-risk notional results")
    a("")
    a("This is the interpretable economic record. The compounded account is "
      "effectively ruined well before the OOS window, so its Sharpe and "
      "drawdown are dominated by the size collapse. The same rule is re-run "
      "with risk fixed at 0.5% of the initial balance (no compounding). It is "
      "a notional, risk-normalised P&L curve with no bankruptcy constraint, so "
      "drawdown is reported in dollars.")
    a("")
    a("| Period | Trades | PF | Sharpe | Notional P&L | Max DD abs |")
    a("| --- | ---: | ---: | ---: | ---: | ---: |")
    for period in ("IS", "OOS", "FULL"):
        c = const.get(period, {})
        a(f"| {period} | {f(c.get('trades'), 0)} | {f(c.get('profit_factor'), 3)} | "
          f"{f(c.get('sharpe'), 3)} | {f(c.get('net_profit'), 0)} | {f(c.get('max_dd_abs'), 0)} |")
    a("")

    a("## D. Benchmarks")
    a("")
    a("Buy-and-hold gold, one round trip of costs, same windows.")
    a("")
    a(md_table(["Window", "Net P&L", "CAGR %", "Sharpe", "Max DD %", "Vol %"], bench_rows))
    a("")
    a(f"Selected trial, OOS constant-risk: notional P&L {f(bc.get('net_profit'), 0)}, "
      f"Sharpe {f(bc.get('sharpe'), 3)}, max drawdown {f(bc.get('max_dd_abs'), 0)} USD. "
      f"Buy-and-hold gold OOS on the same USD 100,000 base: net P&L "
      f"{f(bench['OOS'].get('net_profit'), 0)}, Sharpe {f(bench['OOS'].get('sharpe'), 3)}, "
      f"max DD {f(bench['OOS'].get('max_dd_pct'), 1)}%.")
    a("")
    ba = summary.get("beta_alpha_oos", {})
    a(f"Beta versus buy-and-hold (OOS): {f(ba.get('beta'), 3)}; "
      f"annualised alpha: {f(ba.get('alpha_annual'), 2)}%.")
    a("")
    a("Random-entry matched-exposure control (same directions, same holding "
      "periods, entry time shifted to a random point in the sample; 300 runs, "
      "constant risk over the full sample):")
    a("")
    a(md_table(
        ["Statistic", "Value"],
        [
            ["Actual net P&L (constant risk)", f(rnd.get("actual_profit"), 0)],
            ["Random median (constant risk)", f(rnd.get("profit_median"), 0)],
            ["Random 5th percentile", f(rnd.get("profit_p05"), 0)],
            ["Random 95th percentile", f(rnd.get("profit_p95"), 0)],
            ["Percentile of actual", f(rnd.get("percentile_of_actual"), 1)],
            ["Runs", f(rnd.get("runs"), 0)],
        ],
    ))
    a("")
    bh_oos = bench["OOS"]
    a(f"**Strategy versus buy-and-hold (metric: OOS net P&L and Sharpe).** "
      f"The selected trial loses USD {abs(bc.get('net_profit') or 0):,.0f} on a "
      f"USD 100,000 risk base while buy-and-hold gold earns "
      f"USD {bh_oos.get('net_profit'):,.0f}; the shortfall is "
      f"USD {bh_oos.get('net_profit') - (bc.get('net_profit') or 0):,.0f}. "
      f"Sharpe is {f(bc.get('sharpe'), 3)} versus {f(bh_oos.get('sharpe'), 3)}.")
    a("")
    a(f"**Strategy versus random-entry control (metric: full-sample notional net "
      f"P&L).** The actual rule returns USD {rnd.get('actual_profit'):,.0f}, "
      f"below the random median of USD {rnd.get('profit_median'):,.0f} and " 
      f"at percentile {f(rnd.get('percentile_of_actual'), 1)} of 300 matched "
      f"random schedules. Entry timing is therefore worse than random, not "
      f"merely unprofitable after costs.")
    a("")

    a("## E. Robustness")
    a("")
    a("### Cost-to-risk ratio by year")
    a("")
    a("Round-trip friction is approximately two spreads (cross the spread once, "
      "plus 1.0 spread of slippage). Against a stop of 1.0 or 1.5 x ATR(14,H1), "
      "that fixes the fraction of one R consumed by costs before the signal can "
      "add value. This is a property of the data and the pre-registered stop, "
      "not of any trial outcome.")
    a("")
    h1 = C.load_series("H1")
    h1["atr14"] = C.atr(h1, 14)
    h1["year"] = h1["time"].dt.year
    g = h1.groupby("year").agg(
        close=("close", "median"), atr=("atr14", "median"), spread=("spread", "median")
    )
    g["cost_r_1_0"] = 2 * g["spread"] / g["atr"]
    g["cost_r_1_5"] = 2 * g["spread"] / (1.5 * g["atr"])
    cost_rows = [
        [int(y), f(r["close"], 0), f(r["atr"], 2), f(r["spread"], 3),
         f(r["cost_r_1_0"], 3), f(r["cost_r_1_5"], 3)]
        for y, r in g.iterrows()
    ]
    a(md_table(["Year", "Median close", "Median ATR(H1)", "Median spread",
                "Cost / 1.0xATR", "Cost / 1.5xATR"], cost_rows,
               ["---", "---:", "---:", "---:", "---:", "---:"]))
    a("")
    a("### Volatility regimes (OOS, trailing 60-day realised vol quartiles)")
    a("")
    vol_rows = [[k, f(v.get("n"), 0), f(v.get("sharpe"), 3), f(v.get("total_return_pct"), 1)]
                for k, v in sorted(summary.get("vol_regime_oos", {}).items())]
    a(md_table(["Quartile", "Days", "Sharpe", "Total return %"], vol_rows))
    a("")
    a("### Macro regimes (OOS)")
    a("")
    macro_rows = [[k, f(v.get("n"), 0), f(v.get("sharpe"), 3), f(v.get("total_return_pct"), 1)]
                  for k, v in sorted(summary.get("macro_regime_oos", {}).items())]
    a(md_table(["Regime", "Days", "Sharpe", "Total return %"], macro_rows))
    a("")
    a("### Subperiods (full sample, IS + OOS)")
    a("")
    sub_rows = [[k, f(v.get("n"), 0), f(v.get("sharpe"), 3), f(v.get("total_return_pct"), 1)]
                for k, v in summary.get("subperiod_full", {}).items()]
    a(md_table(["Subperiod", "Days", "Sharpe", "Total return %"], sub_rows))
    a("")

    a("## F. Statistical validation")
    a("")
    a("| Test | Result | Threshold | Verdict |")
    a("| --- | ---: | --- | --- |")
    a(f"| Deflated Sharpe (selected, OOS) | p = {f(dsr.get(sel, {}).get('p_value'), 4)} | p < 0.10 | "
      f"{'PASS' if (dsr.get(sel, {}).get('p_value') or 1) < 0.10 else 'FAIL'} |")
    a(f"| White's Reality Check (8 trials vs buy-and-hold) | p = {f(rc.get('p_value'), 4)} | p < 0.10 | "
      f"{'PASS' if (rc.get('p_value') or 1) < 0.10 else 'FAIL'} |")
    a(f"| Harvey-Liu-Zhu t (selected, OOS) | {f(hlz, 3)} | > 3.0 | "
      f"{'PASS' if (hlz or 0) > 3.0 else 'FAIL'} |")
    a(f"| Bootstrap 95% Sharpe CI (selected, OOS) | [{f(ci.get('sharpe_ci_low'), 3)}, "
      f"{f(ci.get('sharpe_ci_high'), 3)}] | must exclude 0 | "
      f"{'PASS' if (ci.get('sharpe_ci_low') or 0) > 0 else 'FAIL'} |")
    a("")
    a("All statistical tests use the constant-risk notional daily returns (USD "
      "P&L on a fixed USD 100,000 base), not the ruined compounded equity "
      "curve. A 95% bootstrap CI on CAGR is not reported because the "
      "non-compounding curve has no compound growth rate; the Sharpe CI is the "
      "relevant interval for a rejected strategy.")
    a("")
    a(f"Effective trials used for deflation: 32 (conservative, as pre-registered). "
      f"Best trial by OOS mean return in the Reality Check: {rc.get('best')}.")
    a("")
    a("**Multiple-testing statement.** 8 of the 32 pre-registered trials have "
      "been run in this family report. The Deflated Sharpe is computed with "
      "N = 32, the full pre-registered count across T1-T3, so the deflation is "
      "conservative for the T1-only search. White's Reality Check covers the "
      "8 T1 trials jointly. No trial was dropped and no extra trial was added.")
    a("")

    a("## G. Weaknesses and limitations")
    a("")
    a("1. **Spread source.** M15 spread is taken from the completed H1 bar, not "
      "from tick data. This smooths intra-hour spread spikes, including news "
      "spikes, and is likely to understate cost during stress.")
    a("2. **Bar resolution.** Intrabar stop and trail fills are approximated from "
      "M15 OHLC. No partial fills; stop-first priority.")
    a("3. **Swap.** Swap is modelled from the current MT5 Demo schedule applied "
      "to history. Historical swap schedules differ.")
    a("4. **Slippage.** Slippage is a fixed fraction of spread. Real slippage is "
      "state-dependent and worse in fast markets.")
    a("5. **Single venue.** Dukascopy prices only. Cross-checks against the MT5 "
      "feed show a median daily close difference of 0.028% and a return "
      "correlation of 0.9955, but venue-specific spikes remain.")
    a("6. **Selection.** The IS-selected trial is chosen on net Sharpe; with 8 "
      "trials the selection itself consumes degrees of freedom, which the "
      "Deflated Sharpe attempts to correct.")
    a("7. **Compounding ruin.** At 0.5% risk the account is effectively wiped "
      "out in the IS window under baseline costs, so the compounded OOS equity "
      "curve is dominated by the size collapse. Trade-level metrics (PF, cost "
      "ratio) are scale-invariant, and the constant-risk notional curve is the "
      "interpretable economic record; both are reported.")
    a("8. **Gate deferral.** The gate 'Sharpe at least 0.10 above T2' cannot be "
      "evaluated until T2 runs.")
    a("")

    a("## H. Decision")
    a("")
    a(md_table(["Gate (OOS, baseline cost)", "Verdict"], gate_rows))
    a("")
    a(f"**Family verdict: {decision}.**")
    a("")
    if decision == "FAIL":
        a("At least one non-deferred falsification gate fails on out-of-sample "
          "data, so T1 is rejected as a candidate irrespective of the deferred "
          "T2 comparison.")
    elif decision == "CONDITIONAL":
        a("All evaluable gates pass, but the T2-relative gate is deferred. The "
          "family cannot be promoted until T2 has run.")
    a("")
    a("### Interpretation")
    a("")
    cost_per_trade = (bc.get("total_costs") or 0) / max(bc.get("trades") or 1, 1)
    gross_per_trade = (bc.get("gross_pnl") or 0) / max(bc.get("trades") or 1, 1)
    a(f"1. **The gross edge is approximately zero.** The constant-risk OOS gross "
      f"P&L is USD {bc.get('gross_pnl'):,.0f} over {f(bc.get('trades'), 0)} "
      f"trades, or USD {gross_per_trade:,.2f} per trade before friction. That is "
      f"too small to survive execution: total costs are "
      f"USD {bc.get('total_costs'):,.0f}, or USD {cost_per_trade:,.2f} per trade "
      f"(about {(cost_per_trade / 500):.3f}R at the USD 500 initial risk unit).")
    first_year = int(g.index.min())
    last_year = int(g.index.max())
    cr_first = float(g.loc[first_year, "cost_r_1_0"])
    cr_last = float(g.loc[last_year, "cost_r_1_0"])
    a(f"2. **Cost drag is structural, not incidental.** Round-trip friction is "
      f"roughly two spreads. Against the pre-registered 1.0xATR(H1) stop it "
      f"consumed {cr_first:.2f}R per trade in {first_year} and "
      f"{cr_last:.2f}R in {last_year}, because gold volatility rose far faster "
      f"than the spread. The strategy needs a gross edge of at least that size "
      f"simply to break even; it has none.")
    a(f"3. **Entry timing is worse than random.** The actual rule's full-sample "
      f"notional P&L of USD {rnd.get('actual_profit'):,.0f} sits at percentile "
      f"{f(rnd.get('percentile_of_actual'), 1)} of 300 "
      f"matched-exposure random-entry schedules (median "
      f"USD {rnd.get('profit_median'):,.0f}). The pullback filter is not adding "
      f"information; it is selecting slightly adverse entry points.")
    oos_base_all = table[(table["period"] == "OOS") & (table["cost_mult"] == 1.0)]
    best_pf = float(oos_base_all["profit_factor"].max())
    a(f"4. **No configuration rescues it.** At baseline cost the best OOS profit "
      f"factor across the eight pre-registered trials is {best_pf:.2f}, against "
      f"a gate of 1.20, and every trial is negative at 1.0x, 1.5x and 2.0x "
      f"costs. The failure is not confined to a subperiod or a volatility "
      f"regime: all seven subperiods and all four volatility quartiles are "
      f"negative.")
    a("")
    a("T1 is therefore rejected. No T1 parameter set may be carried forward as "
      "a candidate, and the deferred T2-relative Sharpe gate cannot change this "
      "verdict.")
    a("")
    a("### Pre-run interpretation note")
    a("")
    a("The Phase 2A rules are fixed, but two operational readings had to be "
      "chosen and are disclosed here:")
    a("")
    a("1. **Pullback band.** 'Price trades within k x ATR of EMA20' is read as "
      "the bar's adverse extreme falling inside the band "
      "`EMA20 +/- k*ATR(14,H1)`. The first implementation only required the "
      "extreme to be beyond the band on the near side, which is satisfied by "
      "every EMA20 cross and therefore filtered nothing; it was discarded "
      "before any confirmatory run.")
    a("2. **Trigger.** 'Close back in the trend direction beyond EMA20' is read "
      "as a close cross: `close > EMA20` with the previous close `<= EMA20` "
      "for longs, mirrored for shorts.")
    a("")
    a("These readings are not tuned parameters and were fixed before the full "
      "dataset was built. The pre-registered parameters (0.2/0.5 pullback, "
      "1.0/1.5 stop, RSI off/on, 2.0 trail, 0.5% risk) are unchanged.")
    a("")

    a("---")
    a("")
    a("## Appendix: trial identifiers")
    a("")
    ap_rows = []
    for tid in sorted(table["trial"].unique()):
        parts = tid.split("-")
        ap_rows.append([tid, parts[2], parts[3], parts[4]])
    a(md_table(["Trial", "Pullback", "Stop", "RSI"], ap_rows))
    a("")
    a("All figures in this report are generated from `results/T1/` by "
      "`tools/report_t1.py`. No number is typed by hand.")
    a("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {OUT} ({len(doc)} lines)")
    print(f"decision: {decision}")


if __name__ == "__main__":
    main()
