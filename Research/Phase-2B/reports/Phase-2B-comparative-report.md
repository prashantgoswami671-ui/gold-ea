# Phase 2B - comparative report (T1, T2, T3)

**Status:** Phase 2B controlled backtesting complete. No family passes.
T1 is rejected; T2 and T3 are inconclusive and are not promoted.

**Scope:** 32 pre-registered trials across three families, run in the
mandatory order T1 (8) -> T2 (18) -> T3 (6). The rules, grids, split and
statistical programme are those of
`Docs/Strategy/Phase-2A-Trend-Following-Research.md` (v0.2). Family
reports are the primary evidence; this document compares them and does
not add trials, parameters or post-hoc selection.

---

## 1. Headline comparison

| Family | IS-selected trial | Full trades | IS Sharpe | OOS Sharpe | OOS PF | OOS net USD | OOS max DD % | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T1 | `T1-04-PB0.2-ST1.5-RSI1` | 6,353 | -2.534 | -1.787 | 0.734 | -206,352 | -226.6 | FAIL |
| T2 | `T2-08-E50x200-ST2.0-R1.0` | 20 | 0.274 | 0.374 | 4.436 | 40,052 | -30.2 | INCONCLUSIVE |
| T3 | `T3-01-LB6-SCALED` | 35 | 0.606 | 0.147 | 1.452 | 15,905 | -49.2 | INCONCLUSIVE |

All figures in this table are constant-risk notional results at 1.0x
costs, on a fixed USD 100,000 base, so IS and OOS are not additive and
the curves do not compound. T1's drawdown exceeds 100% of the base
because the curve is notional; the family report explains the convention.

Two different conclusions sit behind the same table. T1 traded often
enough to be judged: 6,353 trades clear the 100-trade power threshold,
and the rule loses money at every cost level, so it is **FAIL**. T2 and
T3 have 20 and 35 trades, below the pre-registered threshold, so Section
11.12 forces **INCONCLUSIVE** even though their economic gates also fail.

### Trial accounting

| Family | Pre-registered trials | Trade unit | Full-sample N | OOS N | Selected by IS net Sharpe |
| --- | ---: | --- | ---: | ---: | --- |
| T1 | 8 | completed trade | 6,353 | 2,823 | `T1-04-PB0.2-ST1.5-RSI1` |
| T2 | 18 | completed trade | 20 | 13 | `T2-08-E50x200-ST2.0-R1.0` |
| T3 | 6 | position episode | 35 | 19 | `T3-01-LB6-SCALED` |

Selection used in-sample net Sharpe only, for every family. The OOS
period was never used to choose a trial. T3 counts one position episode
per sign flip rather than each monthly rebalance, which is the
conservative reading; the alternative would clear 100 mechanically.

## 2. Data and methodology validation

All families use one price source: Dukascopy XAUUSD BID/ASK candles,
retrieved 2026-11-05, with the D1 series truncated at the OOS end. The
extracted MT5 demo D1/H4 series is an independent cross-check, not a
second backtest source. Recorded row counts are:

| Series | Rows | First bar (UTC) | Last bar (UTC) | Duplicates | Bad OHLC | Median spread |
| --- | ---: | --- | --- | ---: | ---: | ---: |
| D1 | 5,918 | 2004-01-01 22:00:00+00:00 | 2026-10-30 22:00:00+00:00 | 0 | 0 | 0.418 |
| H4 | 35,741 | 2003-12-31 22:00:00+00:00 | 2026-10-30 18:00:00+00:00 | 0 | 0 | 0.409 |
| H1 | 138,451 | 2004-01-01 00:00:00+00:00 | 2026-10-30 20:00:00+00:00 | 0 | 0 | 0.386 |
| M15 | 551,336 | 2004-01-01 00:00:00+00:00 | 2026-11-04 23:45:00+00:00 | 0 | 0 | 0.384 |

The D1 cross-check covers 5,752 common dates. The
median absolute close difference is 0.0277%, the 95th
percentile is 0.1497%, the maximum is 1.6102%,
and the daily log-return correlation is 0.99549. On
138,451 common H1 bars, resampling M15 closes reproduces
the H1 close to 0.01 on 99.555% of bars (median absolute
difference 0.00000). The data are fit for the intended
purpose; they remain a datafeed substitution, not broker execution data.

The cost model is identical across families: time-varying Dukascopy
BID/ASK spread, commission USD 0.07 per oz round turn, swap charged as a
positive cost, entry/exit slippage of half a spread, and stress multiples
of 1.0x, 1.5x and 2.0x. The abnormal ~USD 58.12 Phase 0 spread is not
used anywhere.

Three methodological corrections were made before the final numbers and
are disclosed in the family reports and notes: the sign of the swap
accrual (it was being credited rather than charged), the labelling of
macro/subperiod/beta-alpha lenses that had been computed on the full
sample but reported as OOS, and a T3 flip-day equity bug found by a
single-trial smoke test before the six-trial run. None changed a frozen
rule, parameter, split or gate.

## 3. Benchmarks and controls

Buy-and-hold gold is the same comparator for all three families: same
period, same costs, same USD 100,000 base.

| Window | Net P&L | CAGR % | Sharpe | Max DD % | Vol % |
| --- | ---: | ---: | ---: | ---: | ---: |
| OOS (2017-01-01 to 2026-06-30) | 248,260 | 13.71 | 0.889 | -26.2 | 15.8 |

| Family | OOS net USD | OOS Sharpe | B&H OOS net | B&H Sharpe | Random control actual vs p95 | Control |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| T1 | -206,352 | -1.787 | 248,260 | 0.889 | -592,074 vs -39,916 | FAIL |
| T2 | 40,052 | 0.374 | 248,260 | 0.889 | 15,061 vs 18,189 | FAIL |
| T3 | 15,905 | 0.147 | 248,260 | 0.889 | 97,311 vs 96,582 | PASS |

Buy-and-hold gold dominates every family on the pre-registered
risk-adjusted comparator. No strategy Sharpe comes close to 0.889, and
every strategy drawdown is worse than the benchmark's -26.2%. The
random controls are decisive in different ways: T1 is worse than the
median random schedule, T2 sits at its 90.7th percentile against a 95th
bar, and T3 clears its 95th percentile by a narrow margin. Only T3 passes
a control, and it does so with a positive point estimate that one
episode supplies.

The 60/40 portfolio and always-long same-vol-target controls listed in
Section 11.10 are not implemented. The approved data set contains only
gold, and T2 has no vol target, so either control would require inventing
a definition. They are disclosed as missing, not treated as passes.

## 4. Cost stress

| Family | OOS net 1.0x | OOS net 1.5x | OOS net 2.0x | PF 1.5x | PF 2.0x | Sign flip |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| T1 | -206,352 | -334,566 | -461,760 | 0.614 | 0.520 | already negative |
| T2 | 40,052 | 36,035 | 32,018 | 3.967 | 3.539 | none |
| T3 | 15,905 | 7,409 | -1,086 | 1.278 | 1.127 | at 2.0x |

Net P&L falls monotonically as costs rise in every trial of every
family, so the higher multiples never improve the result. T2 survives
both multiples. T3 stays positive at 1.5x but turns negative at 2.0x;
Section 11.12 makes only the 1.5x flip a kill criterion, so the formal
cost gate passes and the 2.0x result is reported as an additional
stress. T1 is already deeply negative at 1.0x, so no stress multiple can
rescue it.

Swap is the dominant cost in the two slower families. In T2, swap is
USD 7,746 of OOS total costs of
USD 8,072; in T3 it is
USD 15,437 of USD 16,432.
Both results are therefore partly a bet that the current MT5 swap
schedule persists over multi-month holds. T1's problem is the opposite:
turnover is so high that spread and slippage consume the gross edge many
times over.

## 5. Statistical validation

| Family | Deflated Sharpe | White's Reality Check | Harvey-Liu-Zhu t | Bootstrap 95% Sharpe CI | Tests passed |
| --- | --- | --- | ---: | --- | --- |
| T1 | p = 1.0000 | p = 1.0000 | -5.944 | [-2.486, -1.139] | 0 of 4 |
| T2 | p = 0.9670 | p = 0.9990 | 1.160 | [-0.312, 1.001] | 0 of 4 |
| T3 | p = 0.8402 | p = 0.9900 | 0.442 | [-0.602, 0.861] | 0 of 4 |

No family clears a single statistical test. Deflation uses N = 32, the
full pre-registered T1 + T2 + T3 count, which is conservative for any
one family but correct for the programme as a whole. The bootstrap
intervals all include zero. The Reality Check p-values are at or near 1,
and in T2 and T3 the Reality Check's best trial is not the IS-selected
trial, which is direct evidence that the OOS ordering is unstable.

## 6. Robustness across regimes

| Family | OOS macro regimes positive | OOS vol quartiles positive | OOS subperiods negative |
| --- | ---: | ---: | ---: |
| T1 | 0 of 3 | 0 of 4 | 4 of 4 |
| T2 | 2 of 3 | 3 of 4 | 2 of 4 |
| T3 | 1 of 3 | 3 of 4 | 2 of 4 |

T1 is negative in all three OOS macro regimes, all four volatility
quartiles and all four OOS subperiods: the failure is broad, not
localised. T2 and T3 are mixed. T2 is positive in two of three macro
regimes and three of four vol quartiles but loses in 2016-2018 and
2021-2023. T3 is positive in one of three macro regimes and three of
four vol quartiles, and its OOS point estimate depends on the 2024-2026
subperiod. The T3 report shows that removing its single largest episode
turns the OOS episode sum negative.

## 7. Cross-cutting findings

1. **Costs decide the outcome.** T1's OOS gross P&L is
USD 32,794 against costs of
USD 239,133. The rule is not merely unprofitable:
its gross edge is too small to pay for its turnover. T2 and T3 have
high profit factors but their net P&L is a small residual after swap.

2. **No result survives multiple testing.** Across 32 pre-registered
trials, the best Deflated Sharpe p-value is 0.8402 (T3), and the best
Reality Check p-value is 0.9900. A programme that runs 32 trials and
finds no p-value below 0.10 has not found a candidate.

3. **Buy-and-hold gold wins every comparator.** OOS Sharpe 0.889 and
maximum drawdown -26.2%. No family gets near either number on a
risk-adjusted basis. For a single instrument in a secular bull market,
that is the expected result and the reason the benchmark was mandatory.

4. **The random controls do not endorse any family.** T1 is worse than
random entry, T2 fails its own corrected control, and T3's pass is
marginal (actual USD 97,311 versus p95 USD 96,582, on a full-sample
constant-risk base). A marginal pass on a control is not evidence of a
durable edge.

5. **In-sample selection does not survive out of sample.** T1's
IS-selected trial is negative OOS. T2's IS-selected 50/200 pair is not
the OOS-best pair (20/100), and T3's IS-selected 6-month lookback ranks
last of six on OOS Sharpe. Selection decay is present in every family.

6. **Power is the binding constraint for T2 and T3.** T2 has 20
full-sample trades, T3 has 35 episodes. Neither can reach the
pre-registered 100-trade threshold without changing the rule or the
definition. T1 has enough trades but no edge, so more data would not
change its verdict.

7. **The OOS period is spent.** It has been used once, for all three
families. Any further test of these rules on 2017-2026 would be
in-sample. No trial was re-tuned after seeing OOS results, and no trial
was dropped.

## 8. Decision

**No family passes. No strategy from Phase 2B is promoted, and none is
added to a live or demo candidate set.**

- **T1 - FAIL.** Positive evidence of no edge after costs: 6,353 trades,
  negative at 1.0x, 1.5x and 2.0x, negative in every OOS subperiod and
  volatility quartile. Reject the family.
- **T2 - INCONCLUSIVE.** The economic result is positive but
  concentrated, statistically indistinguishable from zero, below
  buy-and-hold, and below its random-entry control. It cannot be
  promoted and it cannot be declared failed with confidence.
- **T3 - INCONCLUSIVE.** The positive point estimate is one large trend
  episode plus a marginal random-control pass, with a 2.0x cost sign
  flip and no statistical support. Same disposition as T2.

To change this conclusion a future programme would need a new
pre-registered sample or a diversified multi-asset universe, enough
independent trades to clear the 100-trade threshold, survival at 2.0x
costs and swap, and a result that beats both buy-and-hold and the random
control with a Deflated Sharpe that accounts for the full search. None of
those conditions is met here.

The USD 25 account scenario was not used as a selection constraint, and
no trial was selected on net profit alone. No MQL5 implementation, live
trading or demo trading was performed, and no EA code, roadmap entry or
Phase 1 artefact was modified.

## 9. Limitations

1. **Single instrument.** Gold only. The 60/40 and always-long
   same-vol-target controls are not implemented because they would
   require assumptions the approved data set cannot support.
2. **Data substitution.** Dukascopy is a datafeed, not Exness execution.
   The cross-check supports its use but does not make it broker data.
3. **Spread timing.** D1/H4 spread is a daily or bar average, not a
   point-in-time quote at the execution open. This affects T2 and T3
   most, where execution is at a specific open.
4. **Swap history.** The current MT5 demo swap schedule is applied to
   2004-2026. Historical swap schedules differed, and swap dominates
   T2/T3 costs.
5. **Notional curves.** Constant-risk results are non-compounding by
   design, so drawdown can exceed 100% of the base and IS/OOS are not
   additive. The compounded account is reported separately in each
   family report.
6. **Multiple testing.** Deflation uses N = 32 for every family. The
   Reality Check is per family, not across all 32 trials, so the
   programme-level false-positive rate is understated even though no
   family comes close to significance.
7. **Model risk.** Vectorised bar simulation, next-open execution,
   no intraday path or gap-through logic for stops. T1's H1 stops and
   T2's disaster stops are approximations of broker execution.

---

## Appendix - artefact map

| Artefact | Path |
| --- | --- |
| Phase 2A rules | `Docs/Strategy/Phase-2A-Trend-Following-Research.md` |
| T1 report | `Research/Phase-2B/reports/T1-report.md` |
| T2 report | `Research/Phase-2B/reports/T2-report.md` |
| T3 report | `Research/Phase-2B/reports/T3-report.md` |
| T3 operational readings | `Research/Phase-2B/reports/T3-methodology-note.md` |
| Shared core | `Research/Phase-2B/tools/core.py` |
| T1 runner / reporter | `run_t1.py` / `report_t1.py` |
| T2 runner / reporter | `run_t2.py` / `report_t2.py` |
| T3 runner / reporter | `run_t3.py` / `report_t3.py` |
| Trial tables | `Research/Phase-2B/results/T{1,2,3}/*_trial_table.csv` |
| Summary JSON | `Research/Phase-2B/results/T{1,2,3}/*_summary.json` |
| Processed series | `Research/Phase-2B/data/processed/XAUUSD_{D1,H4,H1,M15}.parquet` |

`report_comparative.py` regenerates this document from the artefacts
above. The data cross-check is recomputed from the processed series on
each run; no comparative figure is typed by hand.

