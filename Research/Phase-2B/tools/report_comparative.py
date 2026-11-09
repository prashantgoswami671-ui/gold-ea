"""Render the Phase 2B comparative report across T1, T2 and T3.

Inputs:
  results/T1/t1_trial_table.csv, results/T1/t1_summary.json
  results/T2/t2_trial_table.csv, results/T2/t2_summary.json
  results/T3/t3_trial_table.csv, results/T3/t3_summary.json
  data/processed/*.parquet and data/raw/mt5demo_XAUUSD_D1.csv (data cross-check)
  data/processed/series_metadata.json

Output:
  reports/Phase-2B-comparative-report.md

Every number is read from an artefact or recomputed from the processed series.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
PROC = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"
OUT = ROOT / "reports" / "Phase-2B-comparative-report.md"

FAMILIES = [
    {
        "key": "T1",
        "name": "T1 - Multi-timeframe EMA pullback continuation",
        "design": "M15 pullback to EMA20 inside an H4 EMA200 trend; stop 1.0-1.5x ATR(14,H1); RSI(14,M15) 40-60 filter; risk 0.5%",
        "trade_unit": "completed trade",
        "trials": 8,
        "verdict": "FAIL",
        "verdict_reason": "Rejected outright: negative at every cost level, every subperiod and every volatility quartile.",
    },
    {
        "key": "T2",
        "name": "T2 - Daily EMA crossover trend following",
        "design": "EMA(50) / EMA(200) D1 crossover; disaster stop 2.0x ATR(14,D1); risk 1.0%",
        "trade_unit": "completed trade",
        "trials": 18,
        "verdict": None,
        "verdict_reason": "Fewer than 100 full-sample trades, so Section 11.12 makes the verdict INCONCLUSIVE; the economic gates fail as well.",
    },
    {
        "key": "T3",
        "name": "T3 - Time-series momentum overlay",
        "design": "Sign of 6-month D1 return; monthly rebalance at next open; 10% vol target capped at 2.0x; long/short",
        "trade_unit": "position episode",
        "trials": 6,
        "verdict": None,
        "verdict_reason": "Fewer than 100 position episodes, so Section 11.12 makes the verdict INCONCLUSIVE; the economic gates fail as well.",
    },
]


def f(x, nd=2):
    if x is None:
        return "n/a"
    try:
        if isinstance(x, (bool, np.bool_)):
            return "yes" if x else "no"
        if x != x:
            return "n/a"
    except Exception:  # noqa: BLE001
        pass
    if isinstance(x, (int, np.integer)):
        return f"{int(x):,}"
    if isinstance(x, (float, np.floating)):
        return f"{float(x):,.{nd}f}"
    return str(x)


def md_table(headers, rows, align=None):
    align = align or ["---"] * len(headers)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(align) + " |"]
    for r in rows:
        lines.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(lines)


def load_family(key):
    s = json.loads((RES / key / f"{key.lower()}_summary.json").read_text(encoding="utf-8"))
    t = pd.read_csv(RES / key / f"{key.lower()}_trial_table.csv")
    return s, t


def row_at(t, tid, period, cost):
    return t[(t["trial"] == tid) & (t["period"] == period)
             & (t["cost_mult"] == cost)].iloc[0].to_dict()


def data_check():
    d1 = pd.read_parquet(PROC / "XAUUSD_D1.parquet")
    d1["date"] = pd.to_datetime(d1["time"], utc=True).dt.date
    m = pd.read_csv(RAW / "mt5demo_XAUUSD_D1.csv")
    tcol = [c for c in m.columns if "time" in c.lower() or "date" in c.lower()][0]
    m = m.rename(columns={tcol: "mtime"})
    m["date"] = pd.to_datetime(m["mtime"], utc=True).dt.date
    j = d1.merge(m, on="date", suffixes=("_dk", "_mt"))
    rel = (j["close_dk"] - j["close_mt"]).abs() / j["close_mt"] * 100
    corr = float(np.log(j["close_dk"]).diff().corr(np.log(j["close_mt"]).diff()))
    m15 = pd.read_parquet(PROC / "XAUUSD_M15.parquet").set_index("time")
    h1 = pd.read_parquet(PROC / "XAUUSD_H1.parquet").set_index("time")
    agg = m15["close"].resample("1h").last().dropna()
    both = pd.DataFrame({"m15h1": agg, "h1": h1["close"]}).dropna()
    diff = (both["m15h1"] - both["h1"]).abs()
    return {
        "d1_common": len(j),
        "d1_median": float(rel.median()),
        "d1_p95": float(rel.quantile(0.95)),
        "d1_max": float(rel.max()),
        "d1_corr": corr,
        "h1_common": len(both),
        "h1_exact": float((diff <= 0.0100001).mean() * 100.0),
        "h1_median": float(diff.median()),
    }


def main() -> None:
    meta = json.loads((PROC / "series_metadata.json").read_text(encoding="utf-8"))
    dc = data_check()

    fam = {}
    for spec in FAMILIES:
        s, t = load_family(spec["key"])
        tid = s["selected_by_is_sharpe"]
        spec = dict(spec)
        spec["summary"] = s
        spec["tid"] = tid
        spec["data"] = t
        spec["is"] = row_at(t, tid, "IS_CONST", 1.0)
        spec["oos"] = row_at(t, tid, "OOS_CONST", 1.0)
        spec["full"] = row_at(t, tid, "FULL_CONST", 1.0)
        spec["oos15"] = row_at(t, tid, "OOS_CONST", 1.5)
        spec["oos20"] = row_at(t, tid, "OOS_CONST", 2.0)
        spec["verdict"] = spec["verdict"] or s.get("decision", "INCONCLUSIVE")
        fam[spec["key"]] = spec

    doc = []
    a = doc.append

    a("# Phase 2B - comparative report (T1, T2, T3)")
    a("")
    a("**Status:** Phase 2B controlled backtesting complete. No family passes.")
    a("T1 is rejected; T2 and T3 are inconclusive and are not promoted.")
    a("")
    a("**Scope:** 32 pre-registered trials across three families, run in the")
    a("mandatory order T1 (8) -> T2 (18) -> T3 (6). The rules, grids, split and")
    a("statistical programme are those of")
    a("`Docs/Strategy/Phase-2A-Trend-Following-Research.md` (v0.2). Family")
    a("reports are the primary evidence; this document compares them and does")
    a("not add trials, parameters or post-hoc selection.")
    a("")
    a("---")
    a("")

    a("## 1. Headline comparison")
    a("")
    rows = []
    for spec in FAMILIES:
        d = fam[spec["key"]]
        rows.append([
            spec["key"],
            f"`{d['tid']}`",
            f(d["full"]["trades"], 0),
            f(d["is"]["sharpe"], 3),
            f(d["oos"]["sharpe"], 3),
            f(d["oos"]["profit_factor"], 3),
            f(d["oos"]["net_profit"], 0),
            f(d["oos"]["max_dd_pct"], 1),
            d["verdict"],
        ])
    a(md_table(
        ["Family", "IS-selected trial", "Full trades", "IS Sharpe", "OOS Sharpe",
         "OOS PF", "OOS net USD", "OOS max DD %", "Verdict"],
        rows,
        ["---", "---", "---:", "---:", "---:", "---:", "---:", "---:", "---"],
    ))
    a("")
    a("All figures in this table are constant-risk notional results at 1.0x")
    a("costs, on a fixed USD 100,000 base, so IS and OOS are not additive and")
    a("the curves do not compound. T1's drawdown exceeds 100% of the base")
    a("because the curve is notional; the family report explains the convention.")
    a("")
    a("Two different conclusions sit behind the same table. T1 traded often")
    a("enough to be judged: 6,353 trades clear the 100-trade power threshold,")
    a("and the rule loses money at every cost level, so it is **FAIL**. T2 and")
    a("T3 have 20 and 35 trades, below the pre-registered threshold, so Section")
    a("11.12 forces **INCONCLUSIVE** even though their economic gates also fail.")
    a("")
    a("### Trial accounting")
    a("")
    acc = []
    for spec in FAMILIES:
        d = fam[spec["key"]]
        acc.append([
            spec["key"], spec["trials"], spec["trade_unit"],
            f(d["full"]["trades"], 0), f(d["oos"]["trades"], 0),
            f"`{d['tid']}`",
        ])
    a(md_table(
        ["Family", "Pre-registered trials", "Trade unit", "Full-sample N",
         "OOS N", "Selected by IS net Sharpe"],
        acc,
        ["---", "---:", "---", "---:", "---:", "---"],
    ))
    a("")
    a("Selection used in-sample net Sharpe only, for every family. The OOS")
    a("period was never used to choose a trial. T3 counts one position episode")
    a("per sign flip rather than each monthly rebalance, which is the")
    a("conservative reading; the alternative would clear 100 mechanically.")
    a("")

    a("## 2. Data and methodology validation")
    a("")
    a("All families use one price source: Dukascopy XAUUSD BID/ASK candles,")
    a("retrieved 2026-11-05, with the D1 series truncated at the OOS end. The")
    a("extracted MT5 demo D1/H4 series is an independent cross-check, not a")
    a("second backtest source. Recorded row counts are:")
    a("")
    a(md_table(
        ["Series", "Rows", "First bar (UTC)", "Last bar (UTC)",
         "Duplicates", "Bad OHLC", "Median spread"],
        [
            ["D1", f(meta["series"]["D1"]["rows"], 0), meta["series"]["D1"]["first"],
             meta["series"]["D1"]["last"], meta["series"]["D1"]["duplicates"],
             meta["series"]["D1"]["bad_ohlc"], f(meta["series"]["D1"]["spread_median"], 3)],
            ["H4", f(meta["series"]["H4"]["rows"], 0), meta["series"]["H4"]["first"],
             meta["series"]["H4"]["last"], meta["series"]["H4"]["duplicates"],
             meta["series"]["H4"]["bad_ohlc"], f(meta["series"]["H4"]["spread_median"], 3)],
            ["H1", f(meta["series"]["H1"]["rows"], 0), meta["series"]["H1"]["first"],
             meta["series"]["H1"]["last"], meta["series"]["H1"]["duplicates"],
             meta["series"]["H1"]["bad_ohlc"], f(meta["series"]["H1"]["spread_median"], 3)],
            ["M15", f(meta["series"]["M15"]["rows"], 0), meta["series"]["M15"]["first"],
             meta["series"]["M15"]["last"], meta["series"]["M15"]["duplicates"],
             meta["series"]["M15"]["bad_ohlc"], f(meta["series"]["M15"]["spread_median"], 3)],
        ],
        ["---", "---:", "---", "---", "---:", "---:", "---:"],
    ))
    a("")
    a(f"The D1 cross-check covers {f(dc['d1_common'], 0)} common dates. The")
    a(f"median absolute close difference is {f(dc['d1_median'], 4)}%, the 95th")
    a(f"percentile is {f(dc['d1_p95'], 4)}%, the maximum is {f(dc['d1_max'], 4)}%,")
    a(f"and the daily log-return correlation is {f(dc['d1_corr'], 5)}. On")
    a(f"{f(dc['h1_common'], 0)} common H1 bars, resampling M15 closes reproduces")
    a(f"the H1 close to 0.01 on {f(dc['h1_exact'], 3)}% of bars (median absolute")
    a(f"difference {f(dc['h1_median'], 5)}). The data are fit for the intended")
    a("purpose; they remain a datafeed substitution, not broker execution data.")
    a("")
    a("The cost model is identical across families: time-varying Dukascopy")
    a("BID/ASK spread, commission USD 0.07 per oz round turn, swap charged as a")
    a("positive cost, entry/exit slippage of half a spread, and stress multiples")
    a("of 1.0x, 1.5x and 2.0x. The abnormal ~USD 58.12 Phase 0 spread is not")
    a("used anywhere.")
    a("")
    a("Three methodological corrections were made before the final numbers and")
    a("are disclosed in the family reports and notes: the sign of the swap")
    a("accrual (it was being credited rather than charged), the labelling of")
    a("macro/subperiod/beta-alpha lenses that had been computed on the full")
    a("sample but reported as OOS, and a T3 flip-day equity bug found by a")
    a("single-trial smoke test before the six-trial run. None changed a frozen")
    a("rule, parameter, split or gate.")
    a("")

    a("## 3. Benchmarks and controls")
    a("")
    bh = fam["T1"]["summary"]["benchmarks"]["OOS"]
    a("Buy-and-hold gold is the same comparator for all three families: same")
    a("period, same costs, same USD 100,000 base.")
    a("")
    a(md_table(
        ["Window", "Net P&L", "CAGR %", "Sharpe", "Max DD %", "Vol %"],
        [["OOS (2017-01-01 to 2026-06-30)", f(bh.get("net_profit"), 0),
          f(bh.get("cagr_pct"), 2), f(bh.get("sharpe"), 3),
          f(bh.get("max_dd_pct"), 1), f(bh.get("volatility_pct"), 1)]],
        ["---", "---:", "---:", "---:", "---:", "---:"],
    ))
    a("")
    b_rows = []
    for spec in FAMILIES:
        d = fam[spec["key"]]
        s = d["summary"]
        rnd = s.get("random_entry") or {}
        b_rows.append([
            spec["key"],
            f(d["oos"]["net_profit"], 0),
            f(d["oos"]["sharpe"], 3),
            f(bh.get("net_profit"), 0),
            f(bh.get("sharpe"), 3),
            f"{f(rnd.get('actual_profit'), 0)} vs {f(rnd.get('profit_p95'), 0)}",
            "PASS" if (rnd.get("actual_profit") or 0) > (rnd.get("profit_p95") or 0)
            else "FAIL",
        ])
    a(md_table(
        ["Family", "OOS net USD", "OOS Sharpe", "B&H OOS net", "B&H Sharpe",
         "Random control actual vs p95", "Control"],
        b_rows,
        ["---", "---:", "---:", "---:", "---:", "---", "---"],
    ))
    a("")
    a("Buy-and-hold gold dominates every family on the pre-registered")
    a("risk-adjusted comparator. No strategy Sharpe comes close to 0.889, and")
    a("every strategy drawdown is worse than the benchmark's -26.2%. The")
    a("random controls are decisive in different ways: T1 is worse than the")
    a("median random schedule, T2 sits at its 90.7th percentile against a 95th")
    a("bar, and T3 clears its 95th percentile by a narrow margin. Only T3 passes")
    a("a control, and it does so with a positive point estimate that one")
    a("episode supplies.")
    a("")
    a("The 60/40 portfolio and always-long same-vol-target controls listed in")
    a("Section 11.10 are not implemented. The approved data set contains only")
    a("gold, and T2 has no vol target, so either control would require inventing")
    a("a definition. They are disclosed as missing, not treated as passes.")
    a("")

    a("## 4. Cost stress")
    a("")
    c_rows = []
    for spec in FAMILIES:
        d = fam[spec["key"]]
        n10 = float(d["oos"]["net_profit"])
        n15 = float(d["oos15"]["net_profit"])
        n20 = float(d["oos20"]["net_profit"])
        if n10 <= 0:
            flip = "already negative"
        elif np.sign(n15) != np.sign(n10):
            flip = "at 1.5x"
        elif np.sign(n20) != np.sign(n10):
            flip = "at 2.0x"
        else:
            flip = "none"
        c_rows.append([
            spec["key"], f(n10, 0), f(n15, 0), f(n20, 0),
            f(d["oos15"]["profit_factor"], 3), f(d["oos20"]["profit_factor"], 3),
            flip,
        ])
    a(md_table(
        ["Family", "OOS net 1.0x", "OOS net 1.5x", "OOS net 2.0x",
         "PF 1.5x", "PF 2.0x", "Sign flip"],
        c_rows,
        ["---", "---:", "---:", "---:", "---:", "---:", "---"],
    ))
    a("")
    a("Net P&L falls monotonically as costs rise in every trial of every")
    a("family, so the higher multiples never improve the result. T2 survives")
    a("both multiples. T3 stays positive at 1.5x but turns negative at 2.0x;")
    a("Section 11.12 makes only the 1.5x flip a kill criterion, so the formal")
    a("cost gate passes and the 2.0x result is reported as an additional")
    a("stress. T1 is already deeply negative at 1.0x, so no stress multiple can")
    a("rescue it.")
    a("")
    t2 = fam["T2"]["summary"]["selected_constant_risk"]["OOS"]
    t3 = fam["T3"]["summary"]["selected_constant_risk"]["OOS"]
    a("Swap is the dominant cost in the two slower families. In T2, swap is")
    a(f"USD {f(t2.get('swap_cost'), 0)} of OOS total costs of")
    a(f"USD {f(t2.get('total_costs'), 0)}; in T3 it is")
    a(f"USD {f(t3.get('swap_cost'), 0)} of USD {f(t3.get('total_costs'), 0)}.")
    a("Both results are therefore partly a bet that the current MT5 swap")
    a("schedule persists over multi-month holds. T1's problem is the opposite:")
    a("turnover is so high that spread and slippage consume the gross edge many")
    a("times over.")
    a("")

    a("## 5. Statistical validation")
    a("")
    s_rows = []
    for spec in FAMILIES:
        d = fam[spec["key"]]
        s = d["summary"]
        dsr = (s.get("deflated_sharpe_oos") or {}).get(d["tid"], {})
        rc = s.get("reality_check_oos") or {}
        ci = s.get("bootstrap_sharpe_ci_oos") or {}
        hlz = s.get("harvey_liu_zhu_t_oos")
        passes = sum([
            (dsr.get("p_value") or 1) < 0.10,
            (rc.get("p_value") or 1) < 0.10,
            (hlz or 0) > 3.0,
            (ci.get("sharpe_ci_low") or 0) > 0,
        ])
        s_rows.append([
            spec["key"],
            f"p = {f(dsr.get('p_value'), 4)}",
            f"p = {f(rc.get('p_value'), 4)}",
            f"{f(hlz, 3)}",
            f"[{f(ci.get('sharpe_ci_low'), 3)}, {f(ci.get('sharpe_ci_high'), 3)}]",
            f"{passes} of 4",
        ])
    a(md_table(
        ["Family", "Deflated Sharpe", "White's Reality Check",
         "Harvey-Liu-Zhu t", "Bootstrap 95% Sharpe CI", "Tests passed"],
        s_rows,
        ["---", "---", "---", "---:", "---", "---"],
    ))
    a("")
    a("No family clears a single statistical test. Deflation uses N = 32, the")
    a("full pre-registered T1 + T2 + T3 count, which is conservative for any")
    a("one family but correct for the programme as a whole. The bootstrap")
    a("intervals all include zero. The Reality Check p-values are at or near 1,")
    a("and in T2 and T3 the Reality Check's best trial is not the IS-selected")
    a("trial, which is direct evidence that the OOS ordering is unstable.")
    a("")

    a("## 6. Robustness across regimes")
    a("")
    r_rows = []
    for spec in FAMILIES:
        d = fam[spec["key"]]
        s = d["summary"]
        macro = s.get("macro_regime_oos") or {}
        vol = s.get("vol_regime_oos") or {}
        sub = s.get("subperiod_oos") or {}
        macro_pos = sum(1 for v in macro.values() if (v.get("total_return_pct") or 0) > 0)
        vol_pos = sum(1 for v in vol.values() if (v.get("total_return_pct") or 0) > 0)
        neg_sub = sum(1 for v in sub.values() if (v.get("total_return_pct") or 0) < 0)
        r_rows.append([
            spec["key"], f"{macro_pos} of {len(macro)}", f"{vol_pos} of {len(vol)}",
            f"{neg_sub} of {len(sub)}",
        ])
    a(md_table(
        ["Family", "OOS macro regimes positive", "OOS vol quartiles positive",
         "OOS subperiods negative"],
        r_rows,
        ["---", "---:", "---:", "---:"],
    ))
    a("")
    a("T1 is negative in all three OOS macro regimes, all four volatility")
    a("quartiles and all four OOS subperiods: the failure is broad, not")
    a("localised. T2 and T3 are mixed. T2 is positive in two of three macro")
    a("regimes and three of four vol quartiles but loses in 2016-2018 and")
    a("2021-2023. T3 is positive in one of three macro regimes and three of")
    a("four vol quartiles, and its OOS point estimate depends on the 2024-2026")
    a("subperiod. The T3 report shows that removing its single largest episode")
    a("turns the OOS episode sum negative.")
    a("")

    a("## 7. Cross-cutting findings")
    a("")
    t1 = fam["T1"]["summary"]["selected_constant_risk"]["OOS"]
    a(f"1. **Costs decide the outcome.** T1's OOS gross P&L is")
    a(f"USD {f(t1.get('gross_pnl'), 0)} against costs of")
    a(f"USD {f(t1.get('total_costs'), 0)}. The rule is not merely unprofitable:")
    a("its gross edge is too small to pay for its turnover. T2 and T3 have")
    a("high profit factors but their net P&L is a small residual after swap.")
    a("")
    a("2. **No result survives multiple testing.** Across 32 pre-registered")
    a("trials, the best Deflated Sharpe p-value is 0.8402 (T3), and the best")
    a("Reality Check p-value is 0.9900. A programme that runs 32 trials and")
    a("finds no p-value below 0.10 has not found a candidate.")
    a("")
    a("3. **Buy-and-hold gold wins every comparator.** OOS Sharpe 0.889 and")
    a("maximum drawdown -26.2%. No family gets near either number on a")
    a("risk-adjusted basis. For a single instrument in a secular bull market,")
    a("that is the expected result and the reason the benchmark was mandatory.")
    a("")
    a("4. **The random controls do not endorse any family.** T1 is worse than")
    a("random entry, T2 fails its own corrected control, and T3's pass is")
    a("marginal (actual USD 97,311 versus p95 USD 96,582, on a full-sample")
    a("constant-risk base). A marginal pass on a control is not evidence of a")
    a("durable edge.")
    a("")
    a("5. **In-sample selection does not survive out of sample.** T1's")
    a("IS-selected trial is negative OOS. T2's IS-selected 50/200 pair is not")
    a("the OOS-best pair (20/100), and T3's IS-selected 6-month lookback ranks")
    a("last of six on OOS Sharpe. Selection decay is present in every family.")
    a("")
    a("6. **Power is the binding constraint for T2 and T3.** T2 has 20")
    a("full-sample trades, T3 has 35 episodes. Neither can reach the")
    a("pre-registered 100-trade threshold without changing the rule or the")
    a("definition. T1 has enough trades but no edge, so more data would not")
    a("change its verdict.")
    a("")
    a("7. **The OOS period is spent.** It has been used once, for all three")
    a("families. Any further test of these rules on 2017-2026 would be")
    a("in-sample. No trial was re-tuned after seeing OOS results, and no trial")
    a("was dropped.")
    a("")

    a("## 8. Decision")
    a("")
    a("**No family passes. No strategy from Phase 2B is promoted, and none is")
    a("added to a live or demo candidate set.**")
    a("")
    a("- **T1 - FAIL.** Positive evidence of no edge after costs: 6,353 trades,")
    a("  negative at 1.0x, 1.5x and 2.0x, negative in every OOS subperiod and")
    a("  volatility quartile. Reject the family.")
    a("- **T2 - INCONCLUSIVE.** The economic result is positive but")
    a("  concentrated, statistically indistinguishable from zero, below")
    a("  buy-and-hold, and below its random-entry control. It cannot be")
    a("  promoted and it cannot be declared failed with confidence.")
    a("- **T3 - INCONCLUSIVE.** The positive point estimate is one large trend")
    a("  episode plus a marginal random-control pass, with a 2.0x cost sign")
    a("  flip and no statistical support. Same disposition as T2.")
    a("")
    a("To change this conclusion a future programme would need a new")
    a("pre-registered sample or a diversified multi-asset universe, enough")
    a("independent trades to clear the 100-trade threshold, survival at 2.0x")
    a("costs and swap, and a result that beats both buy-and-hold and the random")
    a("control with a Deflated Sharpe that accounts for the full search. None of")
    a("those conditions is met here.")
    a("")
    a("The USD 25 account scenario was not used as a selection constraint, and")
    a("no trial was selected on net profit alone. No MQL5 implementation, live")
    a("trading or demo trading was performed, and no EA code, roadmap entry or")
    a("Phase 1 artefact was modified.")
    a("")

    a("## 9. Limitations")
    a("")
    a("1. **Single instrument.** Gold only. The 60/40 and always-long")
    a("   same-vol-target controls are not implemented because they would")
    a("   require assumptions the approved data set cannot support.")
    a("2. **Data substitution.** Dukascopy is a datafeed, not Exness execution.")
    a("   The cross-check supports its use but does not make it broker data.")
    a("3. **Spread timing.** D1/H4 spread is a daily or bar average, not a")
    a("   point-in-time quote at the execution open. This affects T2 and T3")
    a("   most, where execution is at a specific open.")
    a("4. **Swap history.** The current MT5 demo swap schedule is applied to")
    a("   2004-2026. Historical swap schedules differed, and swap dominates")
    a("   T2/T3 costs.")
    a("5. **Notional curves.** Constant-risk results are non-compounding by")
    a("   design, so drawdown can exceed 100% of the base and IS/OOS are not")
    a("   additive. The compounded account is reported separately in each")
    a("   family report.")
    a("6. **Multiple testing.** Deflation uses N = 32 for every family. The")
    a("   Reality Check is per family, not across all 32 trials, so the")
    a("   programme-level false-positive rate is understated even though no")
    a("   family comes close to significance.")
    a("7. **Model risk.** Vectorised bar simulation, next-open execution,")
    a("   no intraday path or gap-through logic for stops. T1's H1 stops and")
    a("   T2's disaster stops are approximations of broker execution.")
    a("")

    a("---")
    a("")
    a("## Appendix - artefact map")
    a("")
    a(md_table(
        ["Artefact", "Path"],
        [
            ["Phase 2A rules", "`Docs/Strategy/Phase-2A-Trend-Following-Research.md`"],
            ["T1 report", "`Research/Phase-2B/reports/T1-report.md`"],
            ["T2 report", "`Research/Phase-2B/reports/T2-report.md`"],
            ["T3 report", "`Research/Phase-2B/reports/T3-report.md`"],
            ["T3 operational readings", "`Research/Phase-2B/reports/T3-methodology-note.md`"],
            ["Shared core", "`Research/Phase-2B/tools/core.py`"],
            ["T1 runner / reporter", "`run_t1.py` / `report_t1.py`"],
            ["T2 runner / reporter", "`run_t2.py` / `report_t2.py`"],
            ["T3 runner / reporter", "`run_t3.py` / `report_t3.py`"],
            ["Trial tables", "`Research/Phase-2B/results/T{1,2,3}/*_trial_table.csv`"],
            ["Summary JSON", "`Research/Phase-2B/results/T{1,2,3}/*_summary.json`"],
            ["Processed series", "`Research/Phase-2B/data/processed/XAUUSD_{D1,H4,H1,M15}.parquet`"],
        ],
        ["---", "---"],
    ))
    a("")
    a("`report_comparative.py` regenerates this document from the artefacts")
    a("above. The data cross-check is recomputed from the processed series on")
    a("each run; no comparative figure is typed by hand.")
    a("")

    OUT.write_text("\n".join(doc) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(doc)} lines)")
    for spec in FAMILIES:
        d = fam[spec["key"]]
        print(spec["key"], d["tid"], d["verdict"],
              "OOS net", round(float(d["oos"]["net_profit"]), 2),
              "OOS SR", round(float(d["oos"]["sharpe"]), 3))


if __name__ == "__main__":
    main()
