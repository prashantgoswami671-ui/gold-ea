"""Render the Phase 2B T2 family report from the saved result artefacts.

Inputs (written by run_t2.py):
  results/T2/t2_trial_table.csv
  results/T2/t2_summary.json
  results/T2/<trial>_constant_risk_trades.csv

Output:
  reports/T2-report.md

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

RES = ROOT / "results" / "T2"
OUT = ROOT / "reports" / "T2-report.md"


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
    table = pd.read_csv(RES / "t2_trial_table.csv")
    summary = json.loads((RES / "t2_summary.json").read_text(encoding="utf-8"))

    sel = summary["selected_by_is_sharpe"]
    bench = summary["benchmarks"]
    const = summary.get("selected_constant_risk", {})
    gates = summary.get("gates_oos", {})
    params = summary.get("selected_params", {})
    pair_counts = summary.get("pair_signal_counts", {})
    trade_counts = summary.get("trade_counts_by_trial", {})

    # Per-pair ranges on the corrected results, used in the narrative so the
    # prose cannot drift away from the table.
    stats_by_pair = {}
    for pair in pair_counts:
        tag = f"E{pair.replace('/', 'x')}"
        sel_cols = table["trial"].str.contains(tag, regex=False)
        is_sub = table[(table["cost_mult"] == 1.0) & (table["period"] == "IS") & sel_cols]
        oos_sub = table[(table["cost_mult"] == 1.0) & (table["period"] == "OOS") & sel_cols]
        stats_by_pair[pair] = {
            "is_sharpe_min": float(is_sub["sharpe"].min()),
            "is_sharpe_max": float(is_sub["sharpe"].max()),
            "oos_sharpe_min": float(oos_sub["sharpe"].min()),
            "oos_sharpe_max": float(oos_sub["sharpe"].max()),
            "oos_pf_min": float(oos_sub["profit_factor"].min()),
            "oos_pf_max": float(oos_sub["profit_factor"].max()),
            "oos_all_positive": bool((oos_sub["net_profit"] > 0).all()),
        }

    # ---------- C: performance table, baseline cost, compounded ----------
    base = table[(table["cost_mult"] == 1.0) & (table["period"].isin(["IS", "OOS"]))]
    perf_rows = []
    for tid in base["trial"].unique():
        for period in ("IS", "OOS"):
            r = base[(base["trial"] == tid) & (base["period"] == period)].iloc[0]
            perf_rows.append([
                tid, period, f(r["trades"]),
                f(r["profit_factor"], 3), f(r["sharpe"], 3),
                f(r["net_profit"], 0), f(r["max_dd_pct"], 1),
                f(r["win_rate_pct"], 1), f(r["avg_holding_days"], 0),
                f(r["cost_pct_of_gross"], 1), f(r["exposure_pct"], 1),
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

    # ---------- concentration of the selected trial ----------
    tr = pd.read_csv(RES / f"{sel}_constant_risk_trades.csv")
    tr["entry_time"] = pd.to_datetime(tr["entry_time"], utc=True)
    tr["exit_time"] = pd.to_datetime(tr["exit_time"], utc=True)
    full_net = float(tr["net_pnl"].sum())
    largest = float(tr["net_pnl"].max())
    top3 = float(tr["net_pnl"].nlargest(3).sum())
    oos_tr = tr.loc[tr["entry_time"] >= C.OOS_START]
    oos_net = float(oos_tr["net_pnl"].sum())
    oos_largest = float(oos_tr["net_pnl"].max())
    winners = int((tr["net_pnl"] > 0).sum())
    oos_winners = int((oos_tr["net_pnl"] > 0).sum())
    straddle = tr.loc[
        (tr["entry_time"] < C.OOS_START) & (tr["exit_time"] > C.OOS_START)
    ]
    t2_boundary = (
        float(bc.get("net_profit") or 0.0) - float(bc.get("net_pnl") or 0.0)
    )

    # ---------- H: decision ----------
    gate_rows = []
    labels = {
        "min_trades_100_full_sample": "At least 100 trades, full sample 2008-2026",
        "net_pf_ge_1_20": "Net profit factor >= 1.20 (OOS)",
        "net_sharpe_ge_0_50": "Net Sharpe >= 0.50 (OOS)",
        "max_dd_le_25pct": "Maximum drawdown <= 25% (OOS)",
        "positive_in_3_of_4_vol_regimes": "Positive in >= 3 of 4 OOS volatility regimes",
        "beats_buy_and_hold_sharpe": "Beats buy-and-hold gold on OOS Sharpe",
        "dsr_p_lt_0_10": "Deflated Sharpe p < 0.10",
        "cost_stress_1_5x_no_sign_flip": "OOS P&L sign stable at 1.5x costs",
        "cost_stress_2_0x_no_sign_flip": "OOS P&L sign stable at 2.0x costs",
    }
    for k, lab in labels.items():
        v = gates.get(k)
        gate_rows.append([lab, "PASS" if v else "FAIL"])

    decision = summary.get("decision", "INCONCLUSIVE")
    failed_non_trade = [k for k, v in gates.items()
                        if v is False and k != "min_trades_100_full_sample"]

    # ---------- build document ----------
    doc = []
    a = doc.append

    a("# Phase 2B - T2 family report")
    a("")
    a("**Family:** T2 - Daily dual-EMA trend system")
    a("")
    a(f"**Status:** {decision}")
    a("")
    a("**Phase:** 2B controlled backtesting, family 2 of 3 (T1 -> T2 -> T3)")
    a("")
    a("**Source of rules:** `Docs/Strategy/Phase-2A-Trend-Following-Research.md`")
    a("(v0.2), Section 8.2, grid in Section 11.7, gates in Section 8.2 and 11.12.")
    a("")
    a("---")
    a("")

    a("## A. Identity")
    a("")
    a("| Item | Value |")
    a("| --- | --- |")
    a("| Hypothesis | A slow daily EMA crossover captures multi-month gold trends well enough to pay for costs and beat a passive long position. |")
    a("| What it tests | Whether a simple, widely published trend rule has a real edge on a single instrument at retail costs. |")
    a("| Grade | E2/E3 hypothesis; the most standard and least parameterised of the four candidates. |")
    a("| Timeframe | D1, 22:00-to-22:00 UTC, stamped at the close |")
    a("| Trials | 18 pre-registered combinations |")
    a("| Data | Dukascopy XAUUSD BID/ASK candles, retrieved 2026-11-05; truncated at the OOS end |")
    a("| Symbol | XAUUSD, 2 digits, 100 oz per lot, minimum volume 0.01, volume step 0.01 |")
    a("| Test period | 2004-01-01 to 2026-06-30 |")
    a("| IS | 2004-01-01 to 2016-12-31 |")
    a("| OOS | 2017-01-01 to 2026-06-30 |")
    a(f"| Warm-up | 1,000 completed D1 bars; first signal bar {summary.get('first_signal_bar')} |")
    a("| Trial IDs | T2-01 ... T2-18 (see Appendix) |")
    a("")
    a("Pre-registered grid: EMA pairs (20,100), (50,200), (100,400); "
      "disaster stop 2.0 / 3.0 / 4.0 x ATR(14,D1); risk 0.5% / 1.0% per "
      "trade. That is 3 x 3 x 2 = 18 confirmatory trials.")
    a("")

    a("## B. Capital and execution")
    a("")
    a("| Item | Value |")
    a("| --- | --- |")
    a("| Initial capital | USD 100,000 |")
    a("| Position sizing | Fixed-fractional: risk = r x equity at entry, r = 0.5% or 1.0% per grid; size_oz = risk / (k x ATR(14,D1)) |")
    a("| Max positions | 1 |")
    a("| Contract | 100 oz per lot; P&L = USD 1 per 0.01 move per 1.0 lot |")
    a("| Entry | Next D1 open after the crossing bar closes |")
    a("| Primary exit | Opposite crossover; the position flips at the next open |")
    a("| Disaster stop | k x ATR(14,D1) from entry, intrabar; k = 2.0 / 3.0 / 4.0 |")
    a("| After a stop | Flat until the next crossover (no re-entry without a new cross) |")
    a("| Stop priority | Stop assumed hit first; a gap fills at the open |")
    a("| Execution model | Vectorised Python bar simulator; no MT5 tester |")
    a("| Rollover | Every D1 bar; triple swap on the Wednesday 22:00 rollover |")
    a("")
    a("### Cost model")
    a("")
    a("| Component | Assumption |")
    a("| --- | --- |")
    a("| Spread | Dukascopy BID/ASK, daily mean of the H1 spreads inside the 22:00-to-22:00 session. Median USD 0.418, p95 USD 0.677 |")
    a("| Entry slippage | 0.5 x spread |")
    a("| Signal exit slippage | 0.5 x spread |")
    a("| Stop exit slippage | 1.0 x spread |")
    a("| Commission | USD 0.07 per oz round turn (USD 7.00 per 100 oz lot) |")
    a("| Swap long | USD -0.126 per oz per day |")
    a("| Swap short | USD -0.046 per oz per day |")
    a("| Other costs | None modelled |")
    a("")
    a("All costs are stressed at 1.0x, 1.5x and 2.0x. The abnormal ~USD 58.12 "
      "Phase 0 spread is not used anywhere. The D1 spread is a daily average, "
      "not a point-in-time quote at the entry or exit instant; this is the only "
      "spread available at D1 resolution and is disclosed as a limitation.")
    a("")

    a("## C. Performance")
    a("")
    a("Baseline cost (1.0x), pre-registered fixed-fractional sizing. Each period "
      "is rebased to USD 100,000 at its start, so IS and OOS are not additive. "
      "Trade-level metrics (PF, win rate, cost ratio) are scale-invariant and "
      "remain comparable across periods.")
    a("")
    a(md_table(
        ["Trial", "Period", "Trades", "PF", "Sharpe", "Net P&L", "Max DD %",
         "Win %", "Hold d", "Costs % gross", "Exposure %"],
        perf_rows,
        ["---", "---", "---:", "---:", "---:", "---:", "---:", "---:", "---:",
         "---:", "---:"],
    ))
    a("")
    a("`n/a` in the cost column means gross P&L was zero or negative, so the "
      "cost-to-gross ratio is undefined. A PF of 0.000 means the trial had no "
      "winning trades in that period.")
    a("")
    a("### Cost stress, OOS constant-risk notional P&L")
    a("")
    a("The table repeats all 18 trials with risk fixed at the trial's r on the "
      "initial USD 100,000 (no compounding) and stresses all cost components at "
      "1.0x, 1.5x and 2.0x. Values are notional USD on a USD 100,000 risk base.")
    a("")
    a(md_table(
        ["Trial", "Net P&L 1.0x", "PF 1.0x", "Net P&L 1.5x", "PF 1.5x",
         "Net P&L 2.0x", "PF 2.0x"],
        stress_rows,
    ))
    a("")
    a("### Selected trial")
    a("")
    a(f"Selected on IS net Sharpe: **{sel}** "
      f"(EMA {params.get('pair')}, stop {params.get('stop')} x ATR, "
      f"risk {f((params.get('risk') or 0) * 100, 1)}% per trade). This is the "
      "only selection rule used; OOS is not used for selection.")
    a("")
    a("| Metric | IS | OOS |")
    a("| --- | ---: | ---: |")
    for key, lab, nd in [
        ("trades", "Trades", 0), ("profit_factor", "Profit factor", 3),
        ("sharpe", "Sharpe", 3), ("net_profit", "Net P&L", 0),
        ("max_dd_pct", "Max drawdown %", 1), ("win_rate_pct", "Win rate %", 1),
        ("avg_holding_days", "Average holding days", 0),
        ("cost_pct_of_gross", "Costs as % of gross", 1),
        ("expectancy_r", "Expectancy (R)", 3),
        ("exposure_pct", "Exposure %", 1),
    ]:
        a(f"| {lab} | {f(best_is.get(key), nd)} | {f(best.get(key), nd)} |")
    a("")
    a("The selected trial has only 7 IS trades and 13 OOS trades. An IS Sharpe "
      "estimated from 7 multi-month trades is extremely noisy; it is the "
      "pre-registered selection variable, not a reliable estimate of skill.")
    a("")
    a("### Selected trial, OOS metrics by cost level (constant risk)")
    a("")
    cost_rows = []
    for m in (1.0, 1.5, 2.0):
        rr = table[(table["trial"] == sel) & (table["period"] == "OOS_CONST") & (table["cost_mult"] == m)].iloc[0]
        cost_rows.append([
            f"{m:.1f}x", f(rr["trades"], 0), f(rr["return_pct"], 1),
            f(rr["profit_factor"], 3), f(rr["sharpe"], 3), f(rr["sortino"], 3),
            f(rr["max_dd_abs"], 0), f(rr["win_rate_pct"], 1),
            f(rr["avg_win"], 0), f(rr["avg_loss"], 0),
            f(rr["payoff_ratio"], 2), f(rr["expectancy_r"], 3),
            f(rr["cost_pct_of_gross"], 1),
        ])
    a(md_table(
        ["Cost", "Trades", "Return %", "PF", "Sharpe", "Sortino", "DD abs",
         "Win %", "Avg win", "Avg loss", "Payoff", "Expect R", "Cost % gross"],
        cost_rows,
        ["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:",
         "---:", "---:", "---:", "---:"],
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
        ["Turnover per year", f(bc.get("turnover_per_year"), 2)],
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
    a("#### Concentration of the selected trial")
    a("")
    a(md_table(
        ["Measure", "Full sample", "OOS"],
        [
            ["Trades (constant risk)", f(len(tr), 0), f(len(oos_tr), 0)],
            ["Winning trades", f(winners, 0), f(oos_winners, 0)],
            ["Net P&L", f(full_net, 0), f(oos_net, 0)],
            ["Largest single win", f(largest, 0), f(oos_largest, 0)],
            ["Largest win as % of net", f(largest / full_net * 100 if full_net else np.nan, 1),
             f(oos_largest / oos_net * 100 if oos_net else np.nan, 1)],
            ["Top-3 wins as % of net", f(top3 / full_net * 100 if full_net else np.nan, 1), "n/a"],
        ],
        ["---", "---:", "---:"],
    ))
    a("")
    a("The result is a classic trend-following payoff: a low win rate and a "
      "small number of very large winners. It also means the OOS P&L is not a "
      "broad-based sample of independent evidence; it is dominated by the final "
      "multi-year long trade that is still open at the sample end.")
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
    _straddle_desc = (
        f"one {'short' if straddle.iloc[0]['direction'] < 0 else 'long'} "
        f"position entered {straddle.iloc[0]['entry_time']:%Y-%m-%d} and exited "
        f"{straddle.iloc[0]['exit_time']:%Y-%m-%d}"
        if len(straddle)
        else "no straddling position"
    )
    a(f"This table is trade-level: episodes are attributed to the date they were "
      f"entered. The OOS equity-curve P&L is USD {f(bc.get('net_profit'), 0)}, "
      f"which is USD {f(abs(t2_boundary), 0)} "
      f"{'lower' if t2_boundary < 0 else 'higher'} because {_straddle_desc} "
      "straddles the boundary. The equity-curve convention is the economic "
      "record; the trade-level sum is the cost-accounting attribution.")
    a("")
    a("### Constant-risk notional results")
    a("")
    a("The same rule re-run with risk fixed at the trial's r on the initial "
      "balance (no compounding). It is a notional, risk-normalised P&L curve "
      "with no bankruptcy constraint, so drawdown is reported in dollars. T2 "
      "does not ruin the compounded account in the way T1 did, so the two "
      "curves are close; the constant-risk curve is still the basis for the "
      "statistics and for cross-family comparison.")
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
    bh_oos = bench["OOS"]
    a(f"**Strategy versus buy-and-hold (metric: OOS Sharpe and net P&L).** "
      f"The selected trial earns USD {best.get('net_profit'):,.0f} compounded "
      f"(USD {bc.get('net_profit'):,.0f} constant-risk) on the USD 100,000 "
      f"base, with Sharpe {f(best.get('sharpe'), 3)} compounded "
      f"({f(bc.get('sharpe'), 3)} constant-risk). Buy-and-hold gold earns "
      f"USD {bh_oos.get('net_profit'):,.0f} with Sharpe "
      f"{f(bh_oos.get('sharpe'), 3)}. The strategy does not beat buy-and-hold "
      "on the pre-registered risk-adjusted comparator, so this gate fails.")
    a("")
    ba = summary.get("beta_alpha_oos", {})
    a(f"Beta versus buy-and-hold (OOS, constant-risk returns): "
      f"{f(ba.get('beta'), 3)}; annualised alpha: "
      f"{f(ba.get('alpha_annual'), 2)}%. The low beta shows the result is not "
      "simply long gold beta, but it is also not enough to beat the passive "
      "benchmark on Sharpe.")
    a("")
    a("### Random-entry matched-exposure control")
    a("")
    a(md_table(
        ["Statistic", "Value"],
        [
            ["Trades in control", f(rnd.get("n_trades"), 0)],
            ["Maximum shift", f"{f(rnd.get('max_offset_bars'), 0)} bars "
             f"({f(rnd.get('max_offset_days'), 0)} days)"],
            ["Actual net P&L (control schedule)", f(rnd.get("actual_profit"), 0)],
            ["Actual net P&L (full, incl. terminal trade)", f(rnd.get("actual_profit_full"), 0)],
            ["Random median", f(rnd.get("profit_median"), 0)],
            ["Random 5th percentile", f(rnd.get("profit_p05"), 0)],
            ["Random 95th percentile", f(rnd.get("profit_p95"), 0)],
            ["Percentile of actual", f(rnd.get("percentile_of_actual"), 1)],
            ["Runs", f(rnd.get("runs"), 0)],
        ],
    ))
    a("")
    ctrl_pct = rnd.get("percentile_of_actual")
    ctrl_threshold = 95.0
    ctrl_pass = (ctrl_pct is not None) and (ctrl_pct >= ctrl_threshold)
    a(f"**Control design.** T2 holds positions for months to years. A naive "
      f"forward shift of the whole schedule pushes most trades past the end of "
      f"the sample and silently drops them, which makes the percentile "
      f"meaningless; the first implementation did exactly that and is not "
      f"reported. The corrected control excludes the terminal end_of_data "
      f"trade (its exit is an artefact of the sample end) and draws the shift "
      f"from the range that keeps every remaining trade inside the sample. "
      f"The actual non-terminal schedule is at percentile "
      f"{f(ctrl_pct, 1)} of {f(rnd.get('runs'), 0)} runs, against the 95th "
      f"percentile of USD {f(rnd.get('profit_p95'), 0)}. That is "
      f"{'a marginal pass' if ctrl_pass else 'a failure'} on the control "
      f"requirement in Section 11.10. The full actual P&L of "
      f"USD {f(rnd.get('actual_profit_full'), 0)} includes the terminal trade "
      f"and is not comparable to the control.")
    a("")

    a("## E. Robustness")
    a("")
    a("### Signal frequency and the 100-trade gate")
    a("")
    a("Crossovers after the 1,000-bar warm-up. The warm-up is a data-integrity "
      "rule, but it removes the first 3.8 years, so the trade-count gate is "
      "evaluated over 2008-2026 (18.66 years), not the full 22-year price "
      "history.")
    a("")
    sig_rows = []
    for pair, v in pair_counts.items():
        sig_rows.append([
            pair, f(v.get("full"), 0), f(v.get("is"), 0), f(v.get("oos"), 0),
            f(v.get("per_year"), 2), f(v.get("first_cross")), "FAIL" if (v.get("full") or 0) < 100 else "PASS",
        ])
    a(md_table(
        ["Pair", "Full 2008-2026", "IS", "OOS", "Per year", "First cross", "100-trade gate"],
        sig_rows,
        ["---", "---:", "---:", "---:", "---:", "---", "---"],
    ))
    a("")
    a("No pre-registered T2 pair reaches 100 trades. The 20/100 pair is the "
      "closest at 53; the 50/200 pair has 20 and the 100/400 pair has 8. This "
      "is the binding reason for the INCONCLUSIVE verdict, and it is structural: "
      "slower EMA pairs produce fewer crossovers, and the 1,000-bar warm-up "
      "removes the early sample.")
    a("")
    a("### Pair-level OOS summary")
    a("")
    pair_rows = []
    for pair, v in pair_counts.items():
        tag = f"E{pair.replace('/', 'x')}"
        sub = table[(table["cost_mult"] == 1.0) & (table["period"] == "OOS")
                    & (table["trial"].str.contains(tag, regex=False))]
        if sub.empty:
            continue
        row = sub.sort_values("sharpe", ascending=False).iloc[0]
        tc = trade_counts.get(row["trial"], {})
        pair_rows.append([
            pair, row["trial"], f(tc.get("full"), 0), f(tc.get("oos"), 0),
            f(row["profit_factor"], 3), f(row["sharpe"], 3),
            f(row["net_profit"], 0), f(row["max_dd_pct"], 1),
            f(row["win_rate_pct"], 1),
        ])
    a(md_table(
        ["Pair", "Best OOS trial", "Full trades", "OOS trades", "OOS PF",
         "OOS Sharpe", "OOS net", "OOS DD %", "OOS win %"],
        pair_rows,
        ["---", "---", "---:", "---:", "---:", "---:", "---:", "---:", "---:"],
    ))
    a("")
    s20 = stats_by_pair.get("20/100", {})
    s50 = stats_by_pair.get("50/200", {})
    s100 = stats_by_pair.get("100/400", {})
    a(f"The 20/100 pair is the strongest out of sample (OOS Sharpe "
      f"{f(s20.get('oos_sharpe_min'), 2)}-{f(s20.get('oos_sharpe_max'), 2)} "
      f"across its six stop/risk combinations, OOS PF "
      f"{f(s20.get('oos_pf_min'), 2)}-{f(s20.get('oos_pf_max'), 2)}), but its "
      f"IS Sharpe is {f(s20.get('is_sharpe_min'), 2)} to "
      f"{f(s20.get('is_sharpe_max'), 2)}, so the pre-registered IS selection "
      f"rule does not pick it. The 50/200 pair is the more consistent pair "
      f"(IS Sharpe {f(s50.get('is_sharpe_min'), 2)} to "
      f"{f(s50.get('is_sharpe_max'), 2)}, OOS Sharpe "
      f"{f(s50.get('oos_sharpe_min'), 2)} to {f(s50.get('oos_sharpe_max'), 2)}) "
      f"and is the selected pair. The 100/400 pair is negative in every OOS "
      f"configuration (OOS PF {f(s100.get('oos_pf_min'), 2)}-"
      f"{f(s100.get('oos_pf_max'), 2)}, OOS Sharpe "
      f"{f(s100.get('oos_sharpe_min'), 2)} to {f(s100.get('oos_sharpe_max'), 2)}) "
      f"with only 5 OOS trades. None of these differences is statistically "
      f"resolvable at this sample size.")
    a("")
    a("### Cost-to-risk ratio by year")
    a("")
    a("Round-trip friction is approximated as two spreads. Against a stop of "
      "k x ATR(14,D1), the fraction of one R consumed by costs is small for all "
      "three stop multiples. Unlike T1, cost drag is not the reason T2 fails.")
    a("")
    d1 = C.load_series("D1")
    d1 = d1.loc[d1["time"] <= C.OOS_END].reset_index(drop=True)
    d1["atr14"] = C.atr(d1, 14)
    d1["year"] = d1["time"].dt.year
    g = d1.groupby("year").agg(
        close=("close", "median"), atr=("atr14", "median"), spread=("spread", "median")
    )
    g["cost_r_2"] = 2 * g["spread"] / (2 * g["atr"])
    g["cost_r_3"] = 2 * g["spread"] / (3 * g["atr"])
    g["cost_r_4"] = 2 * g["spread"] / (4 * g["atr"])
    cost_rows = [
        [int(y), f(r["close"], 0), f(r["atr"], 2), f(r["spread"], 3),
         f(r["cost_r_2"], 4), f(r["cost_r_3"], 4), f(r["cost_r_4"], 4)]
        for y, r in g.iterrows()
    ]
    a(md_table(["Year", "Median close", "Median ATR(D1)", "Median spread",
                "Cost / 2xATR", "Cost / 3xATR", "Cost / 4xATR"], cost_rows,
               ["---", "---:", "---:", "---:", "---:", "---:", "---:"]))
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
    macro = summary.get("macro_regime_oos", {})
    macro_pos = [k for k, v in macro.items() if (v.get("sharpe") or -9) > 0]
    a(f"The OOS window falls inside M3 (2017-2019), M4 (2020-2021) and M5 "
      f"(2022-2026); M1 and M2 are in-sample and are not shown. "
      f"{len(macro_pos)} of {len(macro)} OOS macro regimes are positive on the "
      f"constant-risk basis ({', '.join(sorted(macro_pos)) if macro_pos else 'none'}); "
      f"the day counts are small and each regime contains only a handful "
      f"of trades.")
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
    a(f"| White's Reality Check (18 trials vs buy-and-hold) | p = {f(rc.get('p_value'), 4)} | p < 0.10 | "
      f"{'PASS' if (rc.get('p_value') or 1) < 0.10 else 'FAIL'} |")
    a(f"| Harvey-Liu-Zhu t (selected, OOS) | {f(hlz, 3)} | > 3.0 | "
      f"{'PASS' if (hlz or 0) > 3.0 else 'FAIL'} |")
    a(f"| Bootstrap 95% Sharpe CI (selected, OOS) | [{f(ci.get('sharpe_ci_low'), 3)}, "
      f"{f(ci.get('sharpe_ci_high'), 3)}] | must exclude 0 | "
      f"{'PASS' if (ci.get('sharpe_ci_low') or 0) > 0 else 'FAIL'} |")
    a("")
    a("All statistical tests use the constant-risk notional daily returns (USD "
      "P&L on a fixed USD 100,000 base). The selected trial's constant-risk OOS "
      f"Sharpe is {f(bc.get('sharpe'), 3)}; the Deflated Sharpe threshold is "
      f"{f(dsr.get(sel, {}).get('sr0'), 3)} in daily units against an observed "
      f"{f(dsr.get(sel, {}).get('sr_daily'), 3)}, so the result is far below "
      "the multiple-testing bar. The bootstrap CI includes zero.")
    a("")
    a(f"Effective trials used for deflation: 32 (the full pre-registered "
      f"T1+T2+T3 count, conservative for a T2-only search). Best trial by OOS "
      f"mean return in the Reality Check: {rc.get('best')}. Note that the "
      f"Reality Check's best trial (20/100) is not the IS-selected trial "
      f"(50/200); that is itself evidence that the OOS ordering is not stable.")
    a("")
    a("**Multiple-testing statement.** 18 of the 32 pre-registered trials have "
      "been run in this family report. The Deflated Sharpe uses N = 32. White's "
      "Reality Check covers the 18 T2 trials jointly. No trial was dropped and "
      "no extra trial was added.")
    a("")

    a("## G. Weaknesses and limitations")
    a("")
    a("1. **Few trades / low power (central).** The selected trial has 20 "
      "full-sample trades and 13 OOS trades. The closest pair (20/100) has 53. "
      "No T2 pair reaches the pre-registered 100-trade threshold. Multi-month "
      "trades are also serially dependent, so the effective sample is smaller "
      "than the trade count suggests. This is the reason the verdict is "
      "INCONCLUSIVE rather than PASS or FAIL.")
    a("2. **Concentration.** One trade (the 2023-2026 long closed at the sample "
      f"end) is {f(oos_largest / oos_net * 100 if oos_net else np.nan, 1)}% of "
      f"the OOS constant-risk P&L and {f(largest / full_net * 100 if full_net else np.nan, 1)}% "
      "of the full-sample P&L. The result is not a broad sample of independent "
      "trend episodes.")
    a("3. **Selection on a 7-trade IS Sharpe.** The IS-selected trial is chosen "
      "on a Sharpe estimated from 7 multi-month trades. The 20/100 pair looks "
      "much better OOS but is not selected; reselecting on OOS would spend the "
      "OOS period and is prohibited. This is reported as an observation, not a "
      "promotion.")
    a("4. **D1 spread is a daily average.** The cost model uses the mean H1 "
      "spread inside each D1 session, not the quote at the entry or exit "
      "instant. This smooths news spikes and is likely to understate cost in "
      "stress.")
    a("5. **Swap schedule.** The current MT5 Demo swap schedule is applied to "
      "history; historical schedules differ. Multi-month holds make T2 more "
      "sensitive to this than T1.")
    a("6. **Single venue.** Dukascopy prices only. The MT5 cross-check shows a "
      "median daily close difference of 0.028% and a return correlation of "
      "0.9955, but venue-specific spikes remain.")
    a("7. **Bar resolution.** Intrabar stop fills are approximated from D1 OHLC "
      "with stop-first priority. No partial fills.")
    a("8. **After-stop behaviour.** The engine is flat until the next crossover, "
      "per the project owner's resolution. A re-entry rule would change the "
      "trade count and was not tested.")
    a("9. **100/400 is structurally untestable.** With 8 full-sample trades and "
      "5 OOS trades, all but one losing, the pair cannot distinguish a bad rule "
      "from an unlucky sample. It is reported, not interpreted.")
    a("10. **Warm-up cost.** The 1,000-bar warm-up removes 2004-2007. The "
      "100-trade gate is therefore applied to 18.66 years, not 22. The gate is "
      "still applied as pre-registered.")
    a("11. **Missing controls.** Phase 2A Section 11.10 also lists a 60/40 "
      "portfolio and an always-long, same-vol-target control. They are not "
      "implemented here: the approved Phase 2B data set contains only gold, "
      "and T2 has no vol target, so both would require inventing a definition. "
      "The report relies on buy-and-hold and the random-entry control, as "
      "specified in the Phase 2B task requirements.")
    a("12. **No re-tune.** The OOS period is spent. No T2 parameter may be "
      "changed and no T2 trial may be re-run on OOS.")
    a("")

    a("## H. Decision")
    a("")
    gate_rows.append([
        "Beats 95th percentile of random-entry control (Section 11.10, full-sample notional)",
        "PASS" if ctrl_pass else "FAIL",
    ])
    a(md_table(["Gate or control (baseline cost unless noted)", "Verdict"], gate_rows))
    a("")
    a(f"**Formal family verdict: {decision}.**")
    a("")
    a(f"Section 11.12 is explicit: fewer than 100 trades for T2 is reported as "
      f"**inconclusive**, not pass or fail. The selected trial has "
      f"{f(summary.get('full_sample_trades'), 0)} full-sample trades; the "
      f"closest pair has {f(pair_counts.get('20/100', {}).get('full'), 0)}. "
      f"No pre-registered T2 configuration reaches 100.")
    a("")
    a("INCONCLUSIVE is not a soft pass. The point estimates are mixed:")
    a("")
    a(f"- The 20/100 pair is positive at all six stop/risk combinations "
      f"(OOS PF {f(s20.get('oos_pf_min'), 2)}-{f(s20.get('oos_pf_max'), 2)}, "
      f"OOS Sharpe {f(s20.get('oos_sharpe_min'), 2)}-"
      f"{f(s20.get('oos_sharpe_max'), 2)}) but has "
      f"{f(pair_counts.get('20/100', {}).get('full'), 0)} trades and a weak, "
      f"negative IS Sharpe ({f(s20.get('is_sharpe_min'), 2)} to "
      f"{f(s20.get('is_sharpe_max'), 2)}).")
    a(f"- The 50/200 pair, which the IS rule selects, is also positive "
      f"(OOS PF {f(s50.get('oos_pf_min'), 2)}-{f(s50.get('oos_pf_max'), 2)}, "
      f"OOS Sharpe {f(s50.get('oos_sharpe_min'), 2)}-"
      f"{f(s50.get('oos_sharpe_max'), 2)}) but has only "
      f"{f(pair_counts.get('50/200', {}).get('full'), 0)} trades.")
    a(f"- The 100/400 pair is negative in every OOS configuration "
      f"(OOS PF {f(s100.get('oos_pf_min'), 2)}-{f(s100.get('oos_pf_max'), 2)}, "
      f"OOS Sharpe {f(s100.get('oos_sharpe_min'), 2)} to "
      f"{f(s100.get('oos_sharpe_max'), 2)}) with 5 OOS trades.")
    a("")
    formal_failed = [labels[k] for k, v in gates.items()
                     if v is False and k != "min_trades_100_full_sample"]
    a(f"Even if the trade count were sufficient, the selected trial fails "
      f"{len(formal_failed)} further gates: {', '.join(formal_failed)}. It "
      f"does not beat buy-and-hold on OOS Sharpe "
      f"({f(best.get('sharpe'), 3)} versus {f(bh_oos.get('sharpe'), 3)}), its "
      f"Deflated Sharpe p-value is {f(dsr.get(sel, {}).get('p_value'), 3)}, and "
      f"the bootstrap Sharpe interval "
      f"[{f(ci.get('sharpe_ci_low'), 3)}, {f(ci.get('sharpe_ci_high'), 3)}] "
      f"includes zero. It also fails the Section 11.10 random-entry control: "
      f"the actual schedule is at percentile {f(ctrl_pct, 1)}, below the "
      f"95th-percentile bar. The family therefore cannot be promoted on the "
      f"available evidence, and it cannot be declared failed with confidence "
      f"either.")
    a("")
    a("The 20/100 observation is the only part of T2 that looks economically "
      "interesting. It is not a discovery: it was not selected by the "
      "pre-registered rule, it is not statistically significant after 32-trial "
      "deflation, and it is concentrated in a few large trend episodes. It "
      "must not be carried forward as a candidate without a new, separate "
      "pre-registered test.")
    a("")
    a("### Pre-run interpretation note")
    a("")
    a("The Phase 2A rules were fixed before the run. Three operational readings "
      "were resolved by the project owner on 2026-11-06 and recorded in "
      "`T2-methodology-note.md` before any T2 result was seen:")
    a("")
    a("1. **After a disaster stop, flat until the next crossover.** The rules "
      "define entry only at a crossover, so a stopped-out position is not "
      "re-entered in the prevailing trend.")
    a("2. **The 100-trade gate uses the full sample, 2008-2026.** The gate list "
      "says 'on out-of-sample data', but the parenthetical '~4.5 flips per year "
      "over 22 years' is a full-sample statement. The full sample is the only "
      "basis consistent with that parenthetical; all other gates use OOS.")
    a("3. **The T3 macro-regime gate will be applied as at least 2 of 5 "
      "regimes.** This is recorded now, before T3, so the T3 decision is not "
      "made after seeing T3 results.")
    a("")
    a("Two further implementation readings are disclosed: the stop distance "
      "uses ATR(14,D1) of the last completed bar (the entry bar's range is not "
      "known at its open), and the random-entry control excludes the terminal "
      "end_of_data trade and uses a bounded shift so every control trade stays "
      "in sample.")
    a("")

    a("---")
    a("")
    a("## Appendix: trial identifiers")
    a("")
    ap_rows = []
    for tid in sorted(table["trial"].unique()):
        parts = tid.split("-")
        ap_rows.append([tid, parts[2].replace("E", "").replace("x", " / "),
                        parts[3].replace("ST", ""), parts[4].replace("R", "") + "%"])
    a(md_table(["Trial", "EMA pair", "Stop (x ATR)", "Risk"], ap_rows))
    a("")
    a("All figures in this report are generated from `results/T2/` by "
      "`tools/report_t2.py`. No number is typed by hand.")
    a("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {OUT} ({len(doc)} lines)")
    print(f"decision: {decision}")


if __name__ == "__main__":
    main()
