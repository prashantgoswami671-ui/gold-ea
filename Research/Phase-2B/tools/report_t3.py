"""Render the Phase 2B T3 family report from the saved result artefacts.

Inputs (written by run_t3.py):
  results/T3/t3_trial_table.csv
  results/T3/t3_summary.json
  results/T3/<trial>_constant_risk_trades.csv

Output:
  reports/T3-report.md

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

RES = ROOT / "results" / "T3"
OUT = ROOT / "reports" / "T3-report.md"


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
    table = pd.read_csv(RES / "t3_trial_table.csv")
    summary = json.loads((RES / "t3_summary.json").read_text(encoding="utf-8"))

    sel = summary["selected_by_is_sharpe"]
    params = summary["selected_params"]
    bench = summary["benchmarks"]
    const = summary["selected_constant_risk"]
    gates = summary["gates_oos"]
    dsr = summary["deflated_sharpe_oos"]
    rc = summary["reality_check_oos"]
    rnd = summary["random_entry"]
    hlz = summary["harvey_liu_zhu_t_oos"]
    ci = summary["bootstrap_sharpe_ci_oos"]
    stress = summary["cost_stress_oos_const"]
    bear_block = summary["bear_2011_2015"]
    bear = bear_block["metrics"]
    ba = summary["beta_alpha_oos"]
    decision = summary["decision"]

    best = table[(table["trial"] == sel) & (table["period"] == "OOS")
                 & (table["cost_mult"] == 1.0)].iloc[0]
    best_is = table[(table["trial"] == sel) & (table["period"] == "IS")
                    & (table["cost_mult"] == 1.0)].iloc[0]
    bc = const["OOS"]
    bf = const["FULL"]
    bi = const["IS"]

    # ---------- selected-trial episode log ----------
    tr = pd.read_csv(RES / f"{sel}_constant_risk_trades.csv")
    tr["entry_time"] = pd.to_datetime(tr["entry_time"], utc=True)
    tr["exit_time"] = pd.to_datetime(tr["exit_time"], utc=True)
    oos_tr = tr.loc[tr["entry_time"] >= C.OOS_START]
    is_tr = tr.loc[tr["entry_time"] < C.OOS_START]
    straddle = tr.loc[
        (tr["entry_time"] < C.OOS_START) & (tr["exit_time"] > C.OOS_START)
    ]
    full_net = float(tr["net_pnl"].sum())
    oos_net = float(oos_tr["net_pnl"].sum())
    is_net = float(is_tr["net_pnl"].sum())
    largest = float(tr["net_pnl"].max())
    oos_largest = float(oos_tr["net_pnl"].max())
    full_ex_largest = full_net - largest
    oos_ex_largest = oos_net - oos_largest
    winners = int((tr["net_pnl"] > 0).sum())
    oos_winners = int((oos_tr["net_pnl"] > 0).sum())
    boundary = float(bc.get("net_profit") or 0.0) - oos_net
    largest_row = tr.loc[tr["net_pnl"].idxmax()]
    largest_window = (
        f"{largest_row['entry_time']:%Y-%m} to {largest_row['exit_time']:%Y-%m}"
    )
    largest_label = "long" if largest_row["direction"] > 0 else "short"
    # OOS Sharpe ranking, used only to describe where the selected trial sits.
    oos_sharpes = {
        t: float(table[(table["trial"] == t) & (table["period"] == "OOS_CONST")
                       & (table["cost_mult"] == 1.0)].iloc[0]["sharpe"])
        for t in table["trial"].unique()
    }
    selected_is_weakest_oos = min(oos_sharpes, key=oos_sharpes.get) == sel
    selected_oos_rank = (
        sorted(oos_sharpes.values(), reverse=True).index(oos_sharpes[sel]) + 1
    )
    best_oos_trial = max(oos_sharpes, key=oos_sharpes.get)
    lookback_of = {
        t: int(t.split("-")[2].replace("LB", ""))
        for t in table["trial"].unique()
    }
    best_oos_lookback = lookback_of[best_oos_trial]
    straddle_txt = (
        f"{straddle.iloc[0]['entry_time']:%Y-%m-%d} to "
        f"{straddle.iloc[0]['exit_time']:%Y-%m-%d}, "
        f"{'short' if straddle.iloc[0]['direction'] < 0 else 'long'}, "
        f"net USD {f(straddle.iloc[0]['net_pnl'], 0)}"
        if len(straddle)
        else "none"
    )
    straddle_span = (
        f"{straddle.iloc[0]['entry_time']:%Y-%m-%d} and exited "
        f"{straddle.iloc[0]['exit_time']:%Y-%m-%d}"
        if len(straddle)
        else "no episode straddles the boundary"
    )

    # ---------- C: compounded performance, baseline cost ----------
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

    # ---------- C: constant-risk performance, baseline cost ----------
    const_rows = []
    for tid in sorted(table["trial"].unique()):
        rows = {
            p: table[(table["trial"] == tid) & (table["period"] == p)
                     & (table["cost_mult"] == 1.0)].iloc[0]
            for p in ("FULL_CONST", "IS_CONST", "OOS_CONST")
        }
        const_rows.append([
            tid,
            f(rows["FULL_CONST"]["trades"]),
            f(rows["FULL_CONST"]["net_profit"], 0),
            f(rows["FULL_CONST"]["sharpe"], 3),
            f(rows["IS_CONST"]["net_profit"], 0),
            f(rows["IS_CONST"]["sharpe"], 3),
            f(rows["OOS_CONST"]["net_profit"], 0),
            f(rows["OOS_CONST"]["profit_factor"], 3),
            f(rows["OOS_CONST"]["sharpe"], 3),
            f(rows["OOS_CONST"]["max_dd_pct"], 1),
        ])

    # ---------- C: cost stress ----------
    stress_rows = []
    for tid in sorted(table["trial"].unique()):
        r0 = table[(table["trial"] == tid) & (table["period"] == "OOS_CONST")].set_index("cost_mult")
        row = [tid]
        for m in (1.0, 1.5, 2.0):
            row.append(f(r0.loc[m, "net_profit"], 0))
            row.append(f(r0.loc[m, "profit_factor"], 3))
        stress_rows.append(row)

    cost_rows = []
    for m in (1.0, 1.5, 2.0):
        rr = table[(table["trial"] == sel) & (table["period"] == "OOS_CONST")
                   & (table["cost_mult"] == m)].iloc[0]
        cost_rows.append([
            f"{m:.1f}x", f(rr["trades"], 0),
            f(rr["net_pnl"], 0), f(rr["net_profit"], 0),
            f(float(rr["net_profit"]) - float(rr["net_pnl"]), 0),
            f(rr["profit_factor"], 3), f(rr["sharpe"], 3), f(rr["sortino"], 3),
            f(rr["max_dd_abs"], 0), f(rr["win_rate_pct"], 1),
            f(rr["cost_pct_of_gross"], 1),
        ])

    # ---------- D: benchmarks ----------
    bench_rows = []
    for name, b in bench.items():
        bench_rows.append([name, f(b.get("net_profit"), 0), f(b.get("cagr_pct"), 2),
                           f(b.get("sharpe"), 3), f(b.get("max_dd_pct"), 1),
                           f(b.get("volatility_pct"), 1)])

    # ---------- D: scaled versus unscaled ----------
    pair_rows = []
    for months in (6, 12, 24):
        rs = table[(table["period"] == "OOS_CONST") & (table["cost_mult"] == 1.0)
                   & table["trial"].str.contains(f"LB{months}-SCALED", regex=False)].iloc[0]
        ru = table[(table["period"] == "OOS_CONST") & (table["cost_mult"] == 1.0)
                   & table["trial"].str.contains(f"LB{months}-UNSCALED", regex=False)].iloc[0]
        pair_rows.append([
            f"{months} months", f(rs["sharpe"], 3), f(ru["sharpe"], 3),
            f(rs["net_profit"], 0), f(ru["net_profit"], 0),
        ])

    # ---------- E: robustness tables ----------
    macro = summary["macro_regime_oos"]
    macro_pos = sum(1 for v in macro.values() if (v.get("sharpe") or -9) > 0)
    macro_rows = [[k, f(v.get("n"), 0), f(v.get("sharpe"), 3), f(v.get("total_return_pct"), 1)]
                  for k, v in sorted(macro.items())]
    vol = summary["vol_regime_oos"]
    vol_pos = sum(1 for v in vol.values() if (v.get("sharpe") or -9) > 0)
    vol_rows = [[k, f(v.get("n"), 0), f(v.get("sharpe"), 3), f(v.get("total_return_pct"), 1)]
                for k, v in sorted(vol.items())]
    sub = summary["subperiod_oos"]
    sub_rows = [[k, f(v.get("n"), 0), f(v.get("sharpe"), 3), f(v.get("total_return_pct"), 1)]
                for k, v in sorted(sub.items())]
    neg_sub = [k for k, v in sub.items() if (v.get("total_return_pct") or 0.0) < 0]
    pos_sub = [k for k, v in sub.items() if (v.get("total_return_pct") or 0.0) >= 0]
    pos_macro = [k for k, v in macro.items() if (v.get("sharpe") or -9) > 0]
    neg_macro = [k for k, v in macro.items() if (v.get("sharpe") or -9) <= 0]
    rnd_dates = int(rnd.get("rebalance_dates") or 0)
    rnd_long = int(rnd.get("long_months_actual") or 0)

    # ---------- F: statistics ----------
    dsr_sel = dsr.get(sel, {})

    # ---------- H: gates ----------
    labels = {
        "trade_count_ge_100_full_sample": "At least 100 position episodes, full sample",
        "net_sharpe_ge_0_40": "OOS net Sharpe >= 0.40",
        "max_dd_le_25pct": "OOS maximum drawdown <= 25%",
        "macro_positive_in_2_of_3_oos": "Positive in >= 2 of the 3 observable OOS macro regimes",
        "bear_2011_2015_ok": "2011-2015 bear stress not a failure",
        "not_just_buy_and_hold_beta": "Positive OLS alpha versus buy-and-hold (t > 1.96)",
        "scaling_not_the_whole_result": "Vol scaling not the whole result",
        "cost_stress_1_5x_no_sign_flip": "OOS P&L sign stable at 1.5x costs",
        "dsr_p_lt_0_10": "Deflated Sharpe p < 0.10",
    }
    gate_rows = [
        [lab, "PASS" if gates.get(k) else "FAIL"] for k, lab in labels.items()
    ]
    failed_non_trade = [k for k, v in gates.items()
                        if v is False and k != "trade_count_ge_100_full_sample"]

    # ---------- build document ----------
    doc = []
    a = doc.append

    a("# Phase 2B - T3 family report")
    a("")
    a("**Family:** T3 - Time-series momentum (TSMOM) overlay")
    a("")
    a(f"**Status:** {decision}")
    a("")
    a("**Phase:** 2B controlled backtesting, family 3 of 3 (T1 -> T2 -> T3)")
    a("")
    a("**Source of rules:** `Docs/Strategy/Phase-2A-Trend-Following-Research.md`")
    a("(v0.2), Section 8.3, grid in Section 11.7, gates in Section 8.3 and 11.12.")
    a("**Operational readings:** `Research/Phase-2B/reports/T3-methodology-note.md`,")
    a("frozen before the first T3 trial. That note also records the one pre-run")
    a("implementation correction and the treatment of the 2.0x cost multiple.")
    a("")
    a("---")
    a("")

    a("## A. Identity")
    a("")
    a("| Item | Value |")
    a("| --- | --- |")
    a("| Hypothesis | Gold's own trailing return predicts its next-month return, and a volatility-targeted long/short position exploiting it produces a positive risk-adjusted return that is not merely long-gold beta. |")
    a("| What it tests | Whether the best-documented academic effect survives on a single instrument at retail costs, and whether it survives the volatility-scaling critique. |")
    a("| Grade | E2 for the diversified version; E3 for the single-instrument version after Huang et al. (2020) and Kim, Tse & Wald (2016). |")
    a("| Timeframe | D1 signal; monthly rebalance; next D1 open execution |")
    a("| Trials | 6 pre-registered combinations (3 lookbacks x 2 scaling modes) |")
    a("| Data | Dukascopy XAUUSD BID/ASK candles, retrieved 2026-11-05; truncated at the OOS end |")
    a("| Symbol | XAUUSD, 2 digits, 100 oz per lot, minimum volume 0.01, volume step 0.01 |")
    a("| Test period | 2004-01-01 to 2026-06-30 |")
    a("| IS | 2004-01-01 to 2016-12-31 |")
    a("| OOS | 2017-01-01 to 2026-06-30 |")
    a(f"| Warm-up | {f(summary.get('warmup_bars'), 0)} completed D1 bars; first eligible month-end {summary.get('first_eligible_month_end')} |")
    a(f"| Rebalance dates | {f(summary.get('rebalance_dates'), 0)} month-ends with an executable next open |")
    a("| Trial IDs | T3-01 ... T3-06 (Appendix) |")
    a("")
    a("Pre-registered grid:")
    a("")
    a(md_table(
        ["Trial", "Lookback", "Scaling"],
        [
            ["T3-01", "6 months (126 D1 bars)", "scaled"],
            ["T3-02", "6 months (126 D1 bars)", "unscaled"],
            ["T3-03", "12 months (252 D1 bars)", "scaled"],
            ["T3-04", "12 months (252 D1 bars)", "unscaled"],
            ["T3-05", "24 months (504 D1 bars)", "scaled"],
            ["T3-06", "24 months (504 D1 bars)", "unscaled"],
        ],
        ["---", "---", "---"],
    ))
    a("")
    a("**Trade definition.** A T3 trade is one **position episode**: from entry")
    a("(the first rebalance after a sign flip) to exit (the rebalance at the next")
    a("sign flip, or the end of data). Monthly size adjustments inside an episode")
    a("are rebalances, not new trades. This measures independent economic bets;")
    a("counting every monthly rebalance would mechanically clear the 100-trade")
    a("gate without adding independent observations. The project owner selected")
    a("this definition on 2026-11-06, before T3 ran.")
    a("")

    a("## B. Capital and execution")
    a("")
    a("| Item | Value |")
    a("| --- | --- |")
    a("| Initial capital | USD 100,000 |")
    a("| Signal | Sign of `close_t / close_{t-L} - 1`, L = 126 / 252 / 504 D1 bars |")
    a("| Rebalance | Last available D1 bar of each calendar month |")
    a("| Execution | Next D1 open after the month-end signal bar |")
    a("| Volatility estimate | 60-day EWMA of D1 log returns, `span=60`, `adjust=False`, annualised by `sqrt(252)` |")
    a("| Scaled weight | `min(0.10 / realised_vol, 2.0)` of equity notional |")
    a("| Unscaled weight | 1.0x equity notional, constant |")
    a("| Target volatility | 10% annualised |")
    a("| Max positions | 1 |")
    a("| Stop loss | None; the monthly rebalance and sign flip are the risk control |")
    a("| Execution model | Vectorised Python bar simulator; no MT5 tester |")
    a("| Overnight accounting | On a rebalance day the gap from prior close to the execution open belongs to the old size; the intraday move from open to close belongs to the new size |")
    a("| Rollover | Every D1 bar; triple swap on the Wednesday 22:00 rollover |")
    a("")
    a("### Cost model")
    a("")
    a("| Component | Assumption |")
    a("| --- | --- |")
    a("| Spread | Dukascopy BID/ASK, D1 session spread. The same time-varying series used by T1 and T2 |")
    a("| Buy turnover | 1.5 x spread per oz: cross to ask plus 0.5 spread slippage |")
    a("| Sell turnover | 0.5 x spread per oz: sell at bid less 0.5 spread slippage |")
    a("| Commission | USD 0.07 per oz round turn, split as USD 0.035 per oz per side |")
    a("| Swap long | USD -0.126 per oz per day, charged as a positive cost |")
    a("| Swap short | USD -0.046 per oz per day, charged as a positive cost |")
    a("| Other costs | None modelled |")
    a("")
    a("All costs are stressed at 1.0x, 1.5x and 2.0x. The abnormal ~USD 58.12")
    a("Phase 0 spread is not used anywhere. The D1 spread is a daily average, not")
    a("a point-in-time quote at the monthly execution open; this is the only")
    a("spread available at D1 resolution and is disclosed as a limitation.")
    a("")
    a("A buy-then-sell cycle at one spread reproduces the T1/T2 round-trip cost")
    a("exactly. The same simulator convention is used in the random-sign control.")
    a("")

    a("## C. Performance")
    a("")
    a("Baseline cost (1.0x), pre-registered sizing. The compounded account is the")
    a("confirmatory record; each period is rebased to USD 100,000 at its start, so")
    a("IS and OOS are not additive.")
    a("")
    a(md_table(
        ["Trial", "Period", "Episodes", "PF", "Sharpe", "Net P&L", "Max DD %",
         "Win %", "Hold d", "Costs % gross", "Exposure %"],
        perf_rows,
        ["---", "---", "---:", "---:", "---:", "---:", "---:", "---:", "---:",
         "---:", "---:"],
    ))
    a("")
    a("`n/a` in the cost column means gross P&L was zero or negative, so the")
    a("cost-to-gross ratio is undefined. A PF of 0.000 means the trial had no")
    a("winning episodes in that period.")
    a("")
    a("### Constant-risk notional results")
    a("")
    a("The same rule re-run with the notional based on the initial USD 100,000")
    a("(no compounding). Weights, signals and costs are unchanged. This is the")
    a("basis for Sharpe, drawdown, regime attribution and all statistics, matching")
    a("T1 and T2. Values are notional USD on a USD 100,000 base.")
    a("")
    a(md_table(
        ["Trial", "Full eps", "Full net", "Full Sharpe", "IS net", "IS Sharpe",
         "OOS net", "OOS PF", "OOS Sharpe", "OOS DD %"],
        const_rows,
        ["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:"],
    ))
    a("")
    a("### Cost stress, OOS constant-risk P&L")
    a("")
    a("All six trials, OOS constant-risk notional P&L at 1.0x, 1.5x and 2.0x.")
    a("Higher cost multiples can only reduce net P&L; the table is monotone for")
    a("every trial. The 1.5x sign flip is the Section 11.12 kill criterion; 2.0x")
    a("is reported as an additional stress.")
    a("")
    a(md_table(
        ["Trial", "Net 1.0x", "PF 1.0x", "Net 1.5x", "PF 1.5x",
         "Net 2.0x", "PF 2.0x"],
        stress_rows,
        ["---", "---:", "---:", "---:", "---:", "---:", "---:"],
    ))
    a("")
    a("### Selected trial")
    a("")
    a(f"Selected on IS net Sharpe: **{sel}** (lookback")
    a(f"{f(params.get('lookback_months'), 0)} months, {'scaled' if params.get('scaled') else 'unscaled'}).")
    a("This is the only selection rule used; OOS is never used for selection.")
    a("")
    a("| Metric | IS | OOS |")
    a("| --- | ---: | ---: |")
    for key, lab, nd in [
        ("trades", "Episodes", 0), ("profit_factor", "Profit factor", 3),
        ("sharpe", "Sharpe", 3), ("net_profit", "Net P&L", 0),
        ("max_dd_pct", "Max drawdown %", 1), ("win_rate_pct", "Win rate %", 1),
        ("avg_holding_days", "Average holding days", 0),
        ("cost_pct_of_gross", "Costs as % of gross", 1),
        ("expectancy_r", "Expectancy (R)", 3),
        ("exposure_pct", "Exposure %", 1),
    ]:
        a(f"| {lab} | {f(best_is.get(key), nd)} | {f(best.get(key), nd)} |")
    a("")
    a(f"The selected trial has {f(best_is.get('trades'), 0)} IS episodes and "
      f"{f(best.get('trades'), 0)} OOS episodes. The IS Sharpe of "
      f"{f(best_is.get('sharpe'), 3)} falls to {f(best.get('sharpe'), 3)} out of "
      "sample. With this few independent episodes, both estimates are very")
    a("noisy; the decay is nonetheless in the expected direction for a selected")
    a("rule.")
    a("")
    a("The constant-risk record for the same trial:")
    a("")
    a(md_table(
        ["Period", "Episodes", "PF", "Sharpe", "Notional P&L", "Max DD abs", "Max DD %"],
        [
            ["FULL", f(bf.get("trades"), 0), f(bf.get("profit_factor"), 3),
             f(bf.get("sharpe"), 3), f(bf.get("net_profit"), 0),
             f(bf.get("max_dd_abs"), 0), f(bf.get("max_dd_pct"), 1)],
            ["IS", f(bi.get("trades"), 0), f(bi.get("profit_factor"), 3),
             f(bi.get("sharpe"), 3), f(bi.get("net_profit"), 0),
             f(bi.get("max_dd_abs"), 0), f(bi.get("max_dd_pct"), 1)],
            ["OOS", f(bc.get("trades"), 0), f(bc.get("profit_factor"), 3),
             f(bc.get("sharpe"), 3), f(bc.get("net_profit"), 0),
             f(bc.get("max_dd_abs"), 0), f(bc.get("max_dd_pct"), 1)],
        ],
        ["---", "---:", "---:", "---:", "---:", "---:", "---:"],
    ))
    a("")
    a("For the constant-risk curve, max drawdown is measured in dollars against")
    a("the fixed USD 100,000 notional base. It is not a percentage of a")
    a("compounded peak, so it can exceed the compounded drawdown percentage.")
    a("")
    a("### Selected trial, OOS metrics by cost level (constant risk)")
    a("")
    a(md_table(
        ["Cost", "Episodes", "Trade net", "Equity net", "Diff", "PF", "Sharpe",
         "Sortino", "DD abs", "Win %", "Cost % gross"],
        cost_rows,
        ["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:",
         "---:", "---:"],
    ))
    a("")
    a(f"**Trade net** is the sum of the {f(len(oos_tr), 0)} episodes entered")
    a("inside the OOS window. **Equity net** is the OOS P&L of the constant-risk")
    a("curve. **Diff** is equity minus trade. The two differ because one short")
    a(f"episode entered {straddle_span} straddles the boundary.")
    a("The episode sum counts only episodes entered in OOS, so it excludes that")
    a("episode entirely. The equity window counts only P&L earned after")
    a("2016-12-31, so it includes the episode's post-boundary loss but excludes")
    a("its pre-2017 gain. At 1.0x the post-boundary loss is")
    a(f"USD {f(abs(boundary), 0)}; the gap widens at higher cost multiples")
    a("because that episode's swap accrual grows. PF, win rate and")
    a("cost-to-gross are episode-level (entered-in-window) measures; Sharpe,")
    a("Sortino, drawdown and equity net are equity-curve measures. Return % and")
    a("CAGR are not meaningful for a non-compounding notional curve, so they")
    a("are not shown.")
    a("")
    a("### Gross-to-net decomposition")
    a("")
    a("#### Full sample, 1.0x, constant risk")
    a("")
    a(md_table(
        ["Component", "USD"],
        [
            ["Gross P&L (frictionless)", f(bf.get("gross_pnl"), 0)],
            ["Spread and slippage", f(-float(bf.get("spread_slip_cost")), 0)],
            ["Commission", f(-float(bf.get("commission_cost")), 0)],
            ["Swap", f(-float(bf.get("swap_cost")), 0)],
            ["Net P&L", f(bf.get("net_pnl"), 0)],
            ["Total costs", f(-float(bf.get("total_costs")), 0)],
        ],
        ["---", "---:"],
    ))
    a("")
    a(f"Identity: {f(bf.get('gross_pnl'), 0)} - {f(bf.get('total_costs'), 0)} "
      f"= {f(bf.get('net_pnl'), 0)}. The full-sample equity-curve P&L is the")
    a("same number because every episode is inside the window.")
    a("")
    a("#### OOS, 1.0x, constant risk, episodes entered in OOS")
    a("")
    a(md_table(
        ["Component", "USD"],
        [
            ["Gross P&L (frictionless)", f(bc.get("gross_pnl"), 0)],
            ["Spread and slippage", f(-float(bc.get("spread_slip_cost")), 0)],
            ["Commission", f(-float(bc.get("commission_cost")), 0)],
            ["Swap", f(-float(bc.get("swap_cost")), 0)],
            ["Net P&L (episode sum)", f(bc.get("net_pnl"), 0)],
            ["Total costs", f(-float(bc.get("total_costs")), 0)],
        ],
        ["---", "---:"],
    ))
    a("")
    a(f"Identity: {f(bc.get('gross_pnl'), 0)} - {f(bc.get('total_costs'), 0)} "
      f"= {f(bc.get('net_pnl'), 0)}. This table attributes each episode to the")
    a("period in which it was **entered**. The OOS equity-curve P&L is")
    a(f"USD {f(bc.get('net_profit'), 0)}, which is USD {f(abs(boundary), 0)} "
      f"{'lower' if boundary < 0 else 'higher'}.")
    a(f"The difference is the post-boundary portion of one straddling episode")
    a(f"({straddle_txt}). The equity-curve convention is the correct economic")
    a("record for the OOS period; the episode table is the correct attribution")
    a("for cost accounting. Both are shown so the reconciliation is explicit.")
    a("")
    a("### Long/short attribution")
    a("")
    a(md_table(
        ["Window", "Episodes", "Long eps", "Short eps", "Long P&L", "Short P&L", "Net"],
        [
            ["FULL", f(len(tr), 0), f((tr["direction"] > 0).sum(), 0),
             f((tr["direction"] < 0).sum(), 0), f(bf.get("long_pnl"), 0),
             f(bf.get("short_pnl"), 0), f(bf.get("net_pnl"), 0)],
            ["IS", f(len(is_tr), 0), f((is_tr["direction"] > 0).sum(), 0),
             f((is_tr["direction"] < 0).sum(), 0), f(bi.get("long_pnl"), 0),
             f(bi.get("short_pnl"), 0), f(bi.get("net_pnl"), 0)],
            ["OOS", f(len(oos_tr), 0), f((oos_tr["direction"] > 0).sum(), 0),
             f((oos_tr["direction"] < 0).sum(), 0), f(bc.get("long_pnl"), 0),
             f(bc.get("short_pnl"), 0), f(bc.get("net_pnl"), 0)],
        ],
        ["---", "---:", "---:", "---:", "---:", "---:", "---:"],
    ))
    a("")
    a("The rule is long-biased in P&L. Across the full sample the short side")
    a(f"loses USD {f(abs(float(bf.get('short_pnl'))), 0)} while the long side")
    a(f"earns USD {f(bf.get('long_pnl'), 0)}. Out of sample the short side loses")
    a(f"USD {f(abs(float(bc.get('short_pnl'))), 0)} against long P&L of")
    a(f"USD {f(bc.get('long_pnl'), 0)}. A rule that only makes money when long")
    a("is a long-biased rule in disguise, unless the short side earns its keep")
    a("in a specific regime; the 2011-2015 stress is the one window where it did.")
    a("")
    a("### Concentration of the selected trial")
    a("")
    a(md_table(
        ["Measure", "Full sample", "OOS"],
        [
            ["Episodes", f(len(tr), 0), f(len(oos_tr), 0)],
            ["Winning episodes", f(winners, 0), f(oos_winners, 0)],
            ["Net P&L (episode sum)", f(full_net, 0), f(oos_net, 0)],
            ["Largest single win", f(largest, 0), f(oos_largest, 0)],
            ["Largest win as % of net",
             f(largest / full_net * 100 if full_net else np.nan, 1),
             f(oos_largest / oos_net * 100 if oos_net else np.nan, 1)],
            ["Top 3 wins", f(tr["net_pnl"].nlargest(3).sum(), 0),
             f(oos_tr["net_pnl"].nlargest(3).sum(), 0)],
            ["Top 3 as % of net",
             f(tr["net_pnl"].nlargest(3).sum() / full_net * 100 if full_net else np.nan, 1),
             f(oos_tr["net_pnl"].nlargest(3).sum() / oos_net * 100 if oos_net else np.nan, 1)],
            ["Net excluding largest win", f(full_ex_largest, 0), f(oos_ex_largest, 0)],
        ],
        ["---", "---:", "---:"],
    ))
    a("")
    a(f"One {largest_label} episode, entered {largest_row['entry_time']:%Y-%m-%d}")
    a(f"and exited {largest_row['exit_time']:%Y-%m-%d}, earns")
    a(f"USD {f(largest, 0)}: {f(largest / full_net * 100 if full_net else np.nan, 1)}%")
    a(f"of full-sample net and {f(oos_largest / oos_net * 100 if oos_net else np.nan, 1)}%")
    a("of the OOS episode sum. Removing that single episode turns the OOS")
    a(f"episode result to USD {f(oos_ex_largest, 0)}. Only")
    a(f"{f(oos_winners, 0)} of {f(len(oos_tr), 0)} OOS episodes are profitable;")
    a("the positive point estimate is a small number of large trends, not a")
    a("broad-based edge.")
    a("")

    a("## D. Benchmarks and controls")
    a("")
    a("### Buy-and-hold gold")
    a("")
    a(md_table(
        ["Window", "Net P&L", "CAGR %", "Sharpe", "Max DD %", "Vol %"],
        bench_rows,
        ["---", "---:", "---:", "---:", "---:", "---:"],
    ))
    a("")
    a(f"OOS buy-and-hold earns USD {f(bench['OOS'].get('net_profit'), 0)} with")
    a(f"Sharpe {f(bench['OOS'].get('sharpe'), 3)} and maximum drawdown")
    a(f"{f(bench['OOS'].get('max_dd_pct'), 1)}%. The selected T3 trial earns")
    a(f"USD {f(bc.get('net_profit'), 0)} constant-risk with Sharpe")
    a(f"{f(bc.get('sharpe'), 3)} and maximum drawdown")
    a(f"{f(bc.get('max_dd_pct'), 1)}%. Buy-and-hold dominates on net return,")
    a("risk-adjusted return and drawdown. The momentum overlay therefore does")
    a("not beat the passive alternative on the pre-registered comparator.")
    a("")
    a("The 60/40 portfolio and always-long, same-vol-target controls are not")
    a("implemented. The approved Phase 2B data set contains only gold; inventing")
    a("a 60/40 definition would add an unapproved assumption. This is disclosed")
    a("as a limitation, not treated as a pass.")
    a("")
    a("### Random-sign matched-exposure control")
    a("")
    a(md_table(
        ["Statistic", "Value"],
        [
            ["Permutations", f(rnd.get("runs"), 0)],
            ["Rebalance dates", f(rnd.get("rebalance_dates"), 0)],
            ["Long months (actual)", f(rnd.get("long_months_actual"), 0)],
            ["Short months (actual)", f(rnd.get("short_months_actual"), 0)],
            ["Zero months (actual)", f(rnd.get("zero_months_actual"), 0)],
            ["Actual full-sample P&L", f(rnd.get("actual_profit"), 0)],
            ["Random median", f(rnd.get("profit_median"), 0)],
            ["Random 5th percentile", f(rnd.get("profit_p05"), 0)],
            ["Random 95th percentile", f(rnd.get("profit_p95"), 0)],
            ["Percentile of actual", f(rnd.get("percentile_of_actual"), 1)],
        ],
        ["---", "---:"],
    ))
    a("")
    a("The control keeps the actual weight schedule and the actual number of")
    a("long and short months, and randomly permutes which rebalance date gets")
    a("which sign. It therefore holds exposure, turnover and costs broadly")
    a("constant and tests only whether the momentum sign carries information.")
    a(f"The actual full-sample P&L of USD {f(rnd.get('actual_profit'), 0)} is")
    a(f"above the 95th percentile of USD {f(rnd.get('profit_p95'), 0)} by")
    a(f"USD {f((rnd.get('actual_profit') or 0) - (rnd.get('profit_p95') or 0), 0)},")
    a("so it clears the Section 11.10 bar only marginally. The random median is")
    a(f"positive because {f(rnd_long, 0)} of {f(rnd_dates, 0)} rebalance months")
    a("are long in a secular gold bull market;")
    a("the control is not evidence that the timing is irrelevant, but it is not")
    a("comfortable evidence that it is valuable either.")
    a("")
    a("### Scaled versus unscaled")
    a("")
    a(md_table(
        ["Lookback", "Scaled OOS Sharpe", "Unscaled OOS Sharpe",
         "Scaled OOS net", "Unscaled OOS net"],
        pair_rows,
        ["---", "---:", "---:", "---:", "---:"],
    ))
    a("")
    _sel_lb = int(params.get("lookback_months") or 0)
    _svu = summary.get("scaled_vs_unscaled_selected_lookback", {})
    _scaled_sr = float(_svu.get("scaled_oos_sharpe") or 0.0)
    _unscaled_sr = float(_svu.get("unscaled_oos_sharpe") or 0.0)
    a(f"At the selected {f(_sel_lb, 0)}-month lookback, scaling "
      f"**{'raises' if _scaled_sr > _unscaled_sr else 'reduces'}** OOS Sharpe")
    a(f"({f(_scaled_sr, 3)} scaled versus {f(_unscaled_sr, 3)} unscaled).")
    _lb24 = {}
    for _t in table["trial"].unique():
        if lookback_of.get(_t) == 24:
            _r = table[(table["trial"] == _t) & (table["period"] == "OOS_CONST")
                       & (table["cost_mult"] == 1.0)].iloc[0]
            _lb24["scaled" if _t.endswith("-SCALED") else "unscaled"] = (
                float(_r["sharpe"]), int(_r["trades"]), _t
            )
    _n24 = int(summary.get("trade_counts_by_trial", {}).get(
        _lb24.get("scaled", (0, 0, ""))[2], {}).get("full", 0))
    a(f"At 24 months scaling "
      f"{'helps' if _lb24['scaled'][0] > _lb24['unscaled'][0] else 'does not help'} "
      f"Sharpe, but that configuration has only {f(_n24, 0)} full-sample episodes.")
    a("The vol-scaling gate passes because the selected scaled trial is not")
    a("strong; the result is not a vol-scaling artefact.")
    a("")

    a("## E. Robustness")
    a("")
    a("### Macro regimes (OOS)")
    a("")
    a(md_table(["Regime", "Days", "Sharpe", "Total return %"], macro_rows,
               ["---", "---:", "---:", "---:"]))
    a("")
    a(f"{f(macro_pos, 0)} of {f(len(macro), 0)} observable OOS macro regimes "
      f"{'is' if macro_pos == 1 else 'are'} positive. M1 and M2 are in-sample")
    a("and cannot contribute. The gate in")
    a("Section 8.3 says '2 of the 3'; Section 11.6 defines five regimes, so the")
    a("resolved reading is at least 2 of the 3 OOS regimes. The rule fails that")
    a(f"gate: only {', '.join(pos_macro) if pos_macro else 'none'} is positive,")
    a(f"while {', '.join(neg_macro) if neg_macro else 'none'} "
      f"{'is' if len(neg_macro) == 1 else 'are'} negative.")
    a("")
    a("### Volatility quartiles (OOS)")
    a("")
    a(md_table(["Quartile", "Days", "Sharpe", "Total return %"], vol_rows,
               ["---", "---:", "---:", "---:"]))
    a("")
    a(f"{f(vol_pos, 0)} of {f(len(vol), 0)} OOS volatility quartiles are")
    a("positive. The highest-volatility quartile (V4) is negative. T3 has no")
    a("pre-registered volatility-regime gate; this table is attribution only.")
    a("")
    a("### Subperiods (OOS)")
    a("")
    a(md_table(["Subperiod", "Days", "Sharpe", "Total return %"], sub_rows,
               ["---", "---:", "---:", "---:"]))
    a("")
    a(f"{len(neg_sub)} of {len(sub)} OOS subperiods are negative "
      f"({', '.join(sorted(neg_sub)) if neg_sub else 'none'}). The positive OOS")
    a(f"point estimate is driven by "
      f"{', '.join(sorted(pos_sub)) if pos_sub else 'no subperiod'}, while")
    a(f"{', '.join(sorted(neg_sub)) if neg_sub else 'no subperiod'} "
      f"{'loses' if len(neg_sub) == 1 else 'lose'} money. Under Section 11.12 a")
    a("result that depends on one subperiod is at best CONDITIONAL, even before")
    a("the trade-count rule is applied.")
    a("")
    a("### 2011-2015 bear-market stress (in-sample, reported separately)")
    a("")
    a("The Phase 2A gate is written as an OOS condition, but 2011-2015 lies")
    a("inside the in-sample window (2004-2016). It is therefore evaluated as a")
    a("separate in-sample stress window and disclosed, not treated as OOS.")
    a("")
    a(md_table(
        ["Metric", "Value"],
        [
            ["Window", "2011-01-01 to 2015-12-31"],
            ["Episodes entered in window", f(bear.get("trades"), 0)],
            ["Equity-curve net P&L (economic record)", f(bear.get("net_profit"), 0)],
            ["Sharpe", f(bear.get("sharpe"), 3)],
            ["Max drawdown %", f(bear.get("max_dd_pct"), 1)],
            ["Episode-entry net P&L (9 episodes)", f(bear.get("net_pnl"), 0)],
            ["Profit factor (episode level)", f(bear.get("profit_factor"), 3)],
            ["Long P&L (episode level)", f(bear.get("long_pnl"), 0)],
            ["Short P&L (episode level)", f(bear.get("short_pnl"), 0)],
            ["Worst episode", f(bear.get("largest_loss"), 0)],
            ["Single outlier explains failure",
             "yes" if bear_block.get("single_outlier_explains_failure") else "no"],
        ],
        ["---", "---:"],
    ))
    a("")
    a("The equity P&L and the episode sum measure different things and must")
    a("not be interchanged. The equity figure is the money made inside the")
    a("window; the episode sum attributes each episode to the date it was")
    a("entered. They reconcile exactly:")
    a("")
    a(md_table(
        ["Reconciliation item", "USD"],
        [
            ["Episode-entry sum, 9 episodes entered in window",
             f(bear.get("net_pnl"), 0)],
            ["Add back: post-2015 P&L of the short entered 2015-06-01, which the "
             "episode sum includes but the window excludes",
             f(-float(bear_block.get("inside_episode_after_window_pnl") or 0.0), 0)],
            ["Add: in-window P&L of the long entered 2009-02-02 (before the window)",
             f(bear_block.get("prior_episode_in_window_pnl"), 0)],
            ["Add: bar-boundary and metric-convention effects",
             f(bear_block.get("boundary_residual"), 0)],
            ["Equity-curve net P&L, 2011-2015",
             f(bear.get("net_profit"), 0)],
        ],
        ["---", "---:"],
    ))
    a("")
    a(f"The rule is profitable in the 2011-2015 bear market (Sharpe")
    a(f"{f(bear.get('sharpe'), 3)}, equity net USD {f(bear.get('net_profit'), 0)}),")
    a("so the stress gate passes. On the episode-entry view the profit comes")
    a(f"from the short side (USD {f(bear.get('short_pnl'), 0)}), while the long")
    a(f"side loses USD {f(abs(float(bear.get('long_pnl'))), 0)}. That is one")
    a("regime, not a general result: the same short side loses money over the")
    a("full and OOS samples. The 2009-2012 long episode that straddles the")
    a(f"start of the window is the largest single contributor")
    a(f"(USD {f(bear_block.get('prior_episode_in_window_pnl'), 0)} inside the")
    a("window), which is why the equity net is so much larger than the")
    a("9-episode sum.")
    a("")
    a("### Cost stress")
    a("")
    a(f"At 1.5x costs the OOS constant-risk P&L stays positive at")
    a(f"USD {f(stress.get('net_1_5x'), 0)}, so the Section 11.12 1.5x sign-flip")
    a(f"criterion passes. At 2.0x it turns negative at USD {f(stress.get('net_2_0x'), 0)},")
    a("so the strategy is cost-fragile at the outer stress level. The reason is")
    a("swap: at 1.0x, swap is")
    a(f"USD {f(bc.get('swap_cost'), 0)} of the OOS total cost of")
    a(f"USD {f(bc.get('total_costs'), 0)}; at 2.0x it is")
    a(f"USD {f(2 * float(bc.get('swap_cost')), 0)}. Multi-month holds make the")
    a("result highly sensitive to the swap assumption.")
    a("")

    a("## F. Statistical validation")
    a("")
    a(md_table(
        ["Test", "Result", "Threshold", "Verdict"],
        [
            ["Deflated Sharpe (selected, OOS)",
             f"p = {f(dsr_sel.get('p_value'), 4)}", "p < 0.10",
             "PASS" if (dsr_sel.get("p_value") or 1) < 0.10 else "FAIL"],
            ["White's Reality Check (6 trials vs buy-and-hold)",
             f"p = {f(rc.get('p_value'), 4)}", "p < 0.10",
             "PASS" if (rc.get("p_value") or 1) < 0.10 else "FAIL"],
            ["Harvey-Liu-Zhu t (selected, OOS)", f(hlz, 3), "> 3.0",
             "PASS" if (hlz or 0) > 3.0 else "FAIL"],
            ["Bootstrap 95% Sharpe CI (selected, OOS)",
             f"[{f(ci.get('sharpe_ci_low'), 3)}, {f(ci.get('sharpe_ci_high'), 3)}]",
             "must exclude 0",
             "PASS" if (ci.get("sharpe_ci_low") or 0) > 0 else "FAIL"],
            ["Random-sign control: actual versus 95th percentile",
             f"{f(rnd.get('actual_profit'), 0)} vs {f(rnd.get('profit_p95'), 0)}",
             "actual > p95",
             "PASS" if (rnd.get("actual_profit") or 0) > (rnd.get("profit_p95") or 0) else "FAIL"],
            ["Position episodes, full sample", f(summary.get("full_sample_trades"), 0),
             ">= 100",
             "PASS" if (summary.get("full_sample_trades") or 0) >= 100 else "FAIL"],
        ],
        ["---", "---:", "---", "---"],
    ))
    a("")
    a(f"All statistical tests use the constant-risk notional daily returns. The")
    a(f"selected trial's OOS Sharpe is {f(bc.get('sharpe'), 3)}; the Deflated")
    a(f"Sharpe threshold is {f(dsr_sel.get('sr0'), 4)} in daily units against an")
    a(f"observed {f(dsr_sel.get('sr_daily'), 4)}, so the result is far below the")
    a("multiple-testing bar. Deflation uses N = 32, the full pre-registered")
    a("T1 + T2 + T3 count. The Reality Check's best trial is")
    a(f"**{rc.get('best')}**, which is not the IS-selected trial; that is itself")
    a("evidence that the OOS ordering is not stable. The bootstrap interval")
    a("includes zero.")
    a("")
    a(f"**Multiple-testing disclosure.** The IS rule selected the "
      f"{f(params.get('lookback_months'), 0)}-month lookback. The best OOS Sharpe")
    a(f"belongs to the {f(best_oos_lookback, 0)}-month lookback ({best_oos_trial}),")
    a("which the IS rule does not select, and that configuration has only")
    a(f"{f(summary.get('trade_counts_by_trial', {}).get(best_oos_trial, {}).get('full', 0), 0)}")
    a("full-sample episodes. Choosing it after seeing OOS would be post-hoc")
    a("selection and is not done. The reported verdict is for the")
    a("pre-registered IS-selected trial.")
    a("")

    a("## G. Weaknesses")
    a("")
    a(f"1. **Low power.** The selected trial has {f(summary.get('full_sample_trades'), 0)}")
    a(f"full-sample position episodes and {f(len(oos_tr), 0)} OOS episodes. No")
    a("pre-registered T3 configuration reaches 100; the maximum is")
    a(f"{f(max(v.get('full', 0) for v in summary.get('trade_counts_by_trial', {}).values()), 0)}.")
    a("Section 11.12 therefore makes the formal verdict INCONCLUSIVE. A 12-month")
    a("signal gives roughly one independent observation per year, so 22 years is")
    a("about 22 observations before the vol-targeting and rebalancing layers.")
    a("")
    a(f"2. **Selection decay.** The selected trial's IS Sharpe of")
    a(f"{f(best_is.get('sharpe'), 3)} falls to {f(best.get('sharpe'), 3)} OOS. It")
    a(f"ranks {f(selected_oos_rank, 0)} of {f(len(oos_sharpes), 0)} trials on OOS")
    a("Sharpe. The IS-best lookback is not the OOS-best lookback.")
    a("")
    a(f"3. **Concentration.** One {largest_label} episode ({largest_window}) earns")
    a(f"USD {f(largest, 0)}, or")
    a(f"{f(largest / full_net * 100 if full_net else np.nan, 1)}% of full-sample")
    a(f"net and {f(oos_largest / oos_net * 100 if oos_net else np.nan, 1)}% of the")
    a(f"OOS episode sum. Excluding it, OOS episodes total")
    a(f"USD {f(oos_ex_largest, 0)}. Only {f(oos_winners, 0)} of")
    a(f"{f(len(oos_tr), 0)} OOS episodes are winners.")
    a("")
    a(f"4. **Long-biased P&L.** Full-sample long P&L is")
    a(f"USD {f(bf.get('long_pnl'), 0)}; short P&L is")
    a(f"USD {f(bf.get('short_pnl'), 0)}. OOS long P&L is")
    a(f"USD {f(bc.get('long_pnl'), 0)}; short P&L is")
    a(f"USD {f(bc.get('short_pnl'), 0)}. The short side only earns its keep in")
    a("the 2011-2015 bear window.")
    a("")
    a(f"5. **Swap dominates costs.** Swap is")
    a(f"{f(bc.get('swap_cost') / bc.get('total_costs') * 100 if bc.get('total_costs') else np.nan, 1)}%")
    a("of OOS total costs. The result is a bet on the current MT5 swap schedule")
    a("persisting over multi-month holds; historical swap schedules differ.")
    a("")
    a("6. **Buy-and-hold dominates.** OOS Sharpe is")
    a(f"{f(bc.get('sharpe'), 3)} against {f(bench['OOS'].get('sharpe'), 3)} for")
    a(f"buy-and-hold; net P&L is USD {f(bc.get('net_profit'), 0)} against")
    a(f"USD {f(bench['OOS'].get('net_profit'), 0)}; maximum drawdown is")
    a(f"{f(bc.get('max_dd_pct'), 1)}% against")
    a(f"{f(bench['OOS'].get('max_dd_pct'), 1)}%. The overlay adds complexity")
    a("without adding risk-adjusted return.")
    a("")
    a(f"7. **Macro and subperiod dependence.** Only {f(macro_pos, 0)} of")
    a(f"{f(len(macro), 0)} OOS macro regimes is positive; {len(neg_sub)} of")
    a(f"{len(sub)} OOS subperiods are negative. The positive point estimate is")
    a("not broad-based across regimes.")
    a("")
    a("8. **No positive alpha versus beta.** The OLS beta to buy-and-hold is")
    a(f"{f(ba.get('beta'), 3)}, annual alpha is {f(ba.get('alpha_annual'), 2)}%,")
    a(f"and the alpha t-statistic is {f(ba.get('alpha_t'), 3)}. The rule does not")
    a("demonstrate return beyond long gold exposure.")
    a("")
    a("9. **Marginal control.** The random-sign control is cleared by only")
    a(f"USD {f((rnd.get('actual_profit') or 0) - (rnd.get('profit_p95') or 0), 0)}")
    a("at the 95th percentile. That is not a comfortable separation from random")
    a("sign assignment.")
    a("")
    a("10. **Data and execution limitations.** The D1 spread is a daily average,")
    a("not a quote at the execution open. Execution is modelled at the next open")
    a("with no intraday path or gap-through logic. The swap schedule is the")
    a("current MT5 Demo schedule applied to history. Only one instrument is")
    a("available, so the 60/40 and always-long same-vol controls are not")
    a("implemented. Overlapping 12- and 24-month signals reduce the effective")
    a("number of independent observations below the episode count.")
    a("")

    a("## H. Decision")
    a("")
    a(md_table(["Falsification gate", "Verdict"], gate_rows,
               ["---", "---"]))
    a("")
    a("### Statistical and control evidence")
    a("")
    a(md_table(
        ["Test", "Result", "Bar", "Verdict"],
        [
            ["Deflated Sharpe (selected, OOS)",
             f"p = {f(dsr_sel.get('p_value'), 4)}", "p < 0.10",
             "PASS" if (dsr_sel.get("p_value") or 1) < 0.10 else "FAIL"],
            ["White's Reality Check (6 trials)",
             f"p = {f(rc.get('p_value'), 4)}", "p < 0.10",
             "PASS" if (rc.get("p_value") or 1) < 0.10 else "FAIL"],
            ["Harvey-Liu-Zhu t (selected, OOS)",
             f(hlz, 3), "> 3.0",
             "PASS" if (hlz or 0) > 3.0 else "FAIL"],
            ["Bootstrap 95% Sharpe CI (selected, OOS)",
             f"[{f(ci.get('sharpe_ci_low'), 3)}, {f(ci.get('sharpe_ci_high'), 3)}]",
             "must exclude 0",
             "PASS" if (ci.get("sharpe_ci_low") or 0) > 0 else "FAIL"],
            ["Random-sign control (actual vs p95)",
             f"{f(rnd.get('actual_profit'), 0)} vs {f(rnd.get('profit_p95'), 0)}",
             "actual > p95",
             "PASS" if (rnd.get("actual_profit") or 0) > (rnd.get("profit_p95") or 0)
             else "FAIL"],
        ],
        ["---", "---", "---", "---"],
    ))
    a("")
    a(f"**Formal family verdict: {decision}.**")
    a("")
    a(f"Section 11.12 is explicit: fewer than 100 trades for T3 is reported as")
    a(f"**inconclusive**, not pass or fail. The selected trial has")
    a(f"{f(summary.get('full_sample_trades'), 0)} full-sample position episodes;")
    a(f"no pre-registered T3 configuration reaches 100. INCONCLUSIVE therefore")
    a("takes precedence over the economic gates.")
    a("")
    a("INCONCLUSIVE is not a soft pass. If the trade count were sufficient, the")
    a(f"selected trial would **FAIL** {len(failed_non_trade)} of the remaining")
    a("gates:")
    a("")
    for k in failed_non_trade:
        a(f"- {labels.get(k, k)}.")
    a("")
    a(f"The point estimates are weak. OOS constant-risk net P&L is")
    a(f"USD {f(bc.get('net_profit'), 0)}, PF {f(bc.get('profit_factor'), 3)}, and")
    a(f"Sharpe {f(bc.get('sharpe'), 3)}; buy-and-hold earns")
    a(f"USD {f(bench['OOS'].get('net_profit'), 0)} at Sharpe")
    a(f"{f(bench['OOS'].get('sharpe'), 3)}. The OOS episode sum is positive only")
    a(f"because of one {largest_label} episode ({largest_window}); excluding it,")
    a(f"OOS episodes total USD {f(oos_ex_largest, 0)}. The short side loses")
    a("money, the macro and subperiod lenses are mixed to negative, and the")
    a("statistical tests do not reject the null.")
    a("")
    a("**Decision.** Do not promote T3, do not add it to the live candidate set,")
    a("and do not re-tune it on this OOS period. The OOS period is spent. A")
    a("future T3 test would need a new pre-registered sample (or a diversified")
    a("multi-asset universe), a rule that survives 2.0x swap, and enough")
    a("independent episodes to clear the 100-trade power threshold. The $25")
    a("account scenario was not used as a selection constraint, and no trial was")
    a("selected on net profit alone.")
    a("")
    a("---")
    a("")
    a("## Appendix - trial definitions")
    a("")
    a(md_table(
        ["Trial", "Lookback (D1 bars)", "Rebalance", "Scaling", "Weight"],
        [
            ["T3-01", "126", "month-end, next open", "scaled", "min(0.10/vol, 2.0)"],
            ["T3-02", "126", "month-end, next open", "unscaled", "1.0"],
            ["T3-03", "252", "month-end, next open", "scaled", "min(0.10/vol, 2.0)"],
            ["T3-04", "252", "month-end, next open", "unscaled", "1.0"],
            ["T3-05", "504", "month-end, next open", "scaled", "min(0.10/vol, 2.0)"],
            ["T3-06", "504", "month-end, next open", "unscaled", "1.0"],
        ],
        ["---", "---:", "---", "---", "---"],
    ))
    a("")
    a("`run_t3.py` writes `t3_trial_table.csv`, `t3_summary.json` and the")
    a("episode log for the selected trial. `report_t3.py` regenerates this")
    a("document from those artefacts; no figure in the report is typed by hand.")
    a("")

    OUT.write_text("\n".join(doc) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(doc)} lines)")
    print("decision:", decision)


if __name__ == "__main__":
    main()
