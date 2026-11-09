# Phase 2B - Final Review and Closure

Project: Gold EA  
Document type: Phase closure and decision record  
Status: **CLOSED - Phase 2B frozen**  
Date: 2026-11-09  
Authority: Project owner review of the T1, T2 and T3 family reports  
Scope: Controlled trend-following backtesting on XAUUSD  
Code changes: None  
Strategy promoted: **None**

---

## 1. Phase 2B objectives and methodology

### 1.1 Objectives

Phase 2B had one purpose: convert the trend-following candidates selected in
Phase 2A into falsifiable, pre-registered backtests, and decide on the evidence
whether any candidate should be promoted to implementation.

The phase was not an optimisation exercise. It was a controlled attempt to
disprove three hypotheses at retail costs, under a fixed protocol, with the
out-of-sample period used once and never re-tuned.

| Family | Hypothesis tested | Timeframes |
| --- | --- | --- |
| **T1** | Within an established H4 trend, M15 pullbacks to EMA20 resolve in the trend direction often enough to pay for costs. | H4 regime, M15 entry, H1 ATR |
| **T2** | A slow daily EMA crossover captures multi-month gold trends well enough to pay for costs and beat a passive long position. | D1 |
| **T3** | Gold's own trailing return predicts its next-month return, and a volatility-targeted long/short position exploiting it produces a positive risk-adjusted return that is not merely long-gold beta. | D1 signal, monthly rebalance |

The mandate was not to find a profitable configuration. It was to determine,
without changing the rules after seeing results, whether any of the three
families earned the right to proceed.

### 1.2 Fixed protocol

The rules, grids, split, costs and gates are those of
`Docs/Strategy/Phase-2A-Trend-Following-Research.md` (v0.2). Phase 2B did not
change them.

| Item | Value |
| --- | --- |
| Instrument | XAUUSD, 2 digits, 100 oz per lot, minimum volume 0.01, volume step 0.01 |
| Price source | Dukascopy XAUUSD BID/ASK candles, retrieved 2026-11-05 |
| In-sample (IS) | 2004-01-01 to 2016-12-31 |
| Out-of-sample (OOS) | 2017-01-01 to 2026-06-30 |
| Test period | 2004-01-01 to 2026-06-30, truncated at the OOS end |
| Base capital | USD 100,000 |
| Confirmatory trials | 32: T1 = 8, T2 = 18, T3 = 6 |
| Mandatory order | T1 -> T2 -> T3 |
| Selection rule | In-sample net Sharpe only, within each family |
| OOS usage | One confirmatory look; no re-tuning, no re-selection |
| Cost levels | 1.0x, 1.5x, 2.0x |
| Position limit | One position at a time in every family |
| Execution | Signals on closed bars; next-bar open; stop-first priority; gap fills at the open |

The cost model was identical across families:

- Time-varying Dukascopy BID/ASK spread.
- Commission USD 0.07 per oz round turn.
- Swap charged as a positive cost: USD -0.126/oz/day long and USD -0.046/oz/day short, triple swap on Wednesday.
- Entry and signal-exit slippage of 0.5 x spread; stop-exit slippage of 1.0 x spread.
- Stress multiples of 1.0x, 1.5x and 2.0x on all cost components.

The abnormal Phase 0 spread reading of approximately USD 58.12 was not used
anywhere. All results are reported on both the compounded pre-registered sizing
and the constant-risk notional basis; the constant-risk notional basis is the
like-for-like economic record and the basis for all statistics.

### 1.3 Verdict rules

Exactly one verdict was recorded per family: PASS, CONDITIONAL, FAIL or
INCONCLUSIVE. The binding rules were:

- Any failed non-deferred OOS gate means **FAIL**.
- Fewer than 100 trades for T2 or T3 means **INCONCLUSIVE**, not PASS or FAIL.
- A result that depends on one subperiod is at best **CONDITIONAL**.
- A cost stress at 1.5x that flips the sign means cost-fragile and reject.
- Once the OOS period has been examined it is spent.

### 1.4 Integrity and disclosed corrections

Three methodological corrections were made and disclosed before the final
numbers were fixed:

1. The sign of the swap accrual was corrected: swap had been credited rather
   than charged.
2. Macro, subperiod and beta/alpha lenses that had been computed on the full
   sample were relabelled so they are not presented as OOS.
3. A T3 flip-day equity bug was found by a single-trial smoke test and corrected
   before the six-trial run.

None of these changed a frozen rule, parameter, split or gate. No trial was
dropped, no trial was added, and no trial was re-run after the OOS results were
seen.

---

## 2. All 32 pre-registered trials and their allocation

### 2.1 Allocation and accounting

| Family | Pre-registered trials | Trade unit | Full-sample N | OOS N | IS-selected trial |
| --- | ---: | --- | ---: | ---: | --- |
| T1 | 8 | Completed trade | 6,353 | 2,823 | `T1-04-PB0.2-ST1.5-RSI1` |
| T2 | 18 | Completed trade | 20 | 13 | `T2-08-E50x200-ST2.0-R1.0` |
| T3 | 6 | Position episode | 35 | 19 | `T3-01-LB6-SCALED` |
| **Total** | **32** | | | | |

Every pre-registered combination was run and reported. No combination was
discarded on the basis of its result.

T4, the filter ablation described in Phase 2A Section 8.4, is not part of the
32 confirmatory trials. Its 14 ablation tests were not run in Phase 2B, because
T4 is explicitly not a standalone candidate and the ablation would only have
meaning after a T1 or T2 candidate had passed. No T4 result exists or is implied
by this document.

### 2.2 T1 allocation - 8 trials

Pre-registered grid: pullback 0.2 / 0.5 x ATR(14,H1); initial stop 1.0 / 1.5 x
ATR(14,H1), floored at 2 x spread; trailing stop 2.0 x ATR(14,H1); RSI(14,M15)
40-60 filter off / on; risk 0.5% per trade. H4 EMA pair fixed at (50, 200).

| Trial | Pullback | Stop | RSI filter | Selected |
| --- | --- | --- | --- | --- |
| `T1-01-PB0.2-ST1.0-RSI0` | 0.2 | 1.0 | Off | |
| `T1-02-PB0.2-ST1.0-RSI1` | 0.2 | 1.0 | On | |
| `T1-03-PB0.2-ST1.5-RSI0` | 0.2 | 1.5 | Off | |
| `T1-04-PB0.2-ST1.5-RSI1` | 0.2 | 1.5 | On | **Yes** |
| `T1-05-PB0.5-ST1.0-RSI0` | 0.5 | 1.0 | Off | |
| `T1-06-PB0.5-ST1.0-RSI1` | 0.5 | 1.0 | On | |
| `T1-07-PB0.5-ST1.5-RSI0` | 0.5 | 1.5 | Off | |
| `T1-08-PB0.5-ST1.5-RSI1` | 0.5 | 1.5 | On | |

Allocation: 2 pullback distances x 2 stop multiples x 2 RSI states = 8.

### 2.3 T2 allocation - 18 trials

Pre-registered grid: EMA pairs (20,100), (50,200), (100,400); disaster stop
2.0 / 3.0 / 4.0 x ATR(14,D1); risk 0.5% / 1.0% per trade.

| Trial | EMA pair | Stop | Risk | Selected |
| --- | --- | --- | --- | --- |
| `T2-01-E20x100-ST2.0-R0.5` | 20 / 100 | 2.0 | 0.5% | |
| `T2-02-E20x100-ST2.0-R1.0` | 20 / 100 | 2.0 | 1.0% | |
| `T2-03-E20x100-ST3.0-R0.5` | 20 / 100 | 3.0 | 0.5% | |
| `T2-04-E20x100-ST3.0-R1.0` | 20 / 100 | 3.0 | 1.0% | |
| `T2-05-E20x100-ST4.0-R0.5` | 20 / 100 | 4.0 | 0.5% | |
| `T2-06-E20x100-ST4.0-R1.0` | 20 / 100 | 4.0 | 1.0% | |
| `T2-07-E50x200-ST2.0-R0.5` | 50 / 200 | 2.0 | 0.5% | |
| `T2-08-E50x200-ST2.0-R1.0` | 50 / 200 | 2.0 | 1.0% | **Yes** |
| `T2-09-E50x200-ST3.0-R0.5` | 50 / 200 | 3.0 | 0.5% | |
| `T2-10-E50x200-ST3.0-R1.0` | 50 / 200 | 3.0 | 1.0% | |
| `T2-11-E50x200-ST4.0-R0.5` | 50 / 200 | 4.0 | 0.5% | |
| `T2-12-E50x200-ST4.0-R1.0` | 50 / 200 | 4.0 | 1.0% | |
| `T2-13-E100x400-ST2.0-R0.5` | 100 / 400 | 2.0 | 0.5% | |
| `T2-14-E100x400-ST2.0-R1.0` | 100 / 400 | 2.0 | 1.0% | |
| `T2-15-E100x400-ST3.0-R0.5` | 100 / 400 | 3.0 | 0.5% | |
| `T2-16-E100x400-ST3.0-R1.0` | 100 / 400 | 3.0 | 1.0% | |
| `T2-17-E100x400-ST4.0-R0.5` | 100 / 400 | 4.0 | 0.5% | |
| `T2-18-E100x400-ST4.0-R1.0` | 100 / 400 | 4.0 | 1.0% | |

Allocation: 3 EMA pairs x 3 stop multiples x 2 risk fractions = 18.

### 2.4 T3 allocation - 6 trials

Pre-registered grid: lookback 6 / 12 / 24 months (126 / 252 / 504 D1 bars);
volatility estimate 60-day EWMA; target vol 10%; leverage cap 2.0x; scaling
scaled / unscaled.

| Trial | Lookback | Scaling | Selected |
| --- | --- | --- | --- |
| `T3-01-LB6-SCALED` | 6 months (126 bars) | Scaled | **Yes** |
| `T3-02-LB6-UNSCALED` | 6 months (126 bars) | Unscaled | |
| `T3-03-LB12-SCALED` | 12 months (252 bars) | Scaled | |
| `T3-04-LB12-UNSCALED` | 12 months (252 bars) | Unscaled | |
| `T3-05-LB24-SCALED` | 24 months (504 bars) | Scaled | |
| `T3-06-LB24-UNSCALED` | 24 months (504 bars) | Unscaled | |

Allocation: 3 lookbacks x 2 scaling modes = 6.

A T3 trade is one position episode, from entry after a sign flip to exit at the
next sign flip or the end of data. Monthly size adjustments inside an episode
are rebalances, not new trades. This definition was fixed before T3 ran; it is
the conservative count and avoids mechanically clearing the 100-trade threshold
with overlapping monthly rebalances.

---

## 3. T1, T2 and T3 final verdicts

### 3.1 Verdict summary

| Family | IS-selected trial | OOS Sharpe | OOS PF | OOS net USD | OOS max DD % | Final verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| T1 | `T1-04-PB0.2-ST1.5-RSI1` | -1.787 | 0.734 | -206,352 | -226.6 | **FAIL** |
| T2 | `T2-08-E50x200-ST2.0-R1.0` | 0.374 | 4.436 | 40,052 | -30.2 | **INCONCLUSIVE** |
| T3 | `T3-01-LB6-SCALED` | 0.147 | 1.452 | 15,905 | -49.2 | **INCONCLUSIVE** |

Figures are constant-risk notional results at 1.0x costs on a fixed USD 100,000
base. The curves do not compound, so T1's drawdown can exceed 100% of the base
and IS and OOS are not additive.

### 3.2 T1 - FAIL

**Verdict: FAIL.** The evidence is positive evidence of no edge after costs.

| Gate (OOS, baseline cost) | Result | Verdict |
| --- | --- | --- |
| At least 300 OOS trades | 2,823 | PASS |
| Net profit factor >= 1.20 | 0.734 | FAIL |
| Costs <= 25% of gross profit | 729.2% | FAIL |
| Positive in >= 3 of 4 volatility regimes | 0 of 4 | FAIL |
| Sharpe >= T2 Sharpe + 0.10 | Deferred; cannot change the verdict | DEFERRED |

Supporting evidence:

- 6,353 full-sample trades and 2,823 OOS trades: the sample is large enough to judge the rule.
- OOS gross P&L was USD 32,794 against total costs of USD 239,133. The gross edge was USD 11.62 per trade before friction; costs were USD 84.71 per trade.
- Every one of the eight pre-registered trials was negative at 1.0x, 1.5x and 2.0x costs.
- The selected trial was negative at every cost level, in every OOS volatility quartile, and in all seven full-sample subperiods.
- Entry timing was worse than random: full-sample notional P&L of USD -592,074 versus a random median of USD -322,061 and an 11.3rd percentile rank.

T1 is rejected as a family. No T1 parameter set may be carried forward as a
candidate.

### 3.3 T2 - INCONCLUSIVE

**Verdict: INCONCLUSIVE.** The point estimate is positive but the sample is too
small to separate an edge from noise, and the economic gates fail.

| Gate or control (baseline cost unless noted) | Result | Verdict |
| --- | --- | --- |
| At least 100 trades, full sample 2008-2026 | 20 selected; 53 maximum | FAIL |
| Net profit factor >= 1.20 (OOS) | 4.436 | PASS |
| Net Sharpe >= 0.50 (OOS) | 0.374 | FAIL |
| Maximum drawdown <= 25% (OOS) | -21.4% compounded; -30.2% constant risk | PASS on the compounded gate |
| Positive in >= 3 of 4 OOS volatility regimes | 3 of 4 | PASS |
| Beats buy-and-hold gold on OOS Sharpe | 0.374 vs 0.889 | FAIL |
| Deflated Sharpe p < 0.10 | 0.9670 | FAIL |
| OOS P&L sign stable at 1.5x costs | Positive | PASS |
| OOS P&L sign stable at 2.0x costs | Positive | PASS |
| Beats 95th percentile of random-entry control | 90.7th percentile | FAIL |

The binding constraint is power. The selected 50/200 trial has 20 full-sample
trades and 13 OOS trades; the closest pair (20/100) has 53. No pre-registered T2
configuration reaches 100. Section 11.12 therefore requires INCONCLUSIVE.

The positive result is also concentrated: the largest single trade is 96.8% of
the OOS constant-risk P&L and 72.8% of the full-sample P&L. The 20/100 pair looks
stronger out of sample but was not selected by the pre-registered IS rule, so it
cannot be promoted after the fact.

### 3.4 T3 - INCONCLUSIVE

**Verdict: INCONCLUSIVE.** The positive point estimate rests on one large trend
episode and a marginal random-control pass, with no statistical support.

| Falsification gate | Result | Verdict |
| --- | --- | --- |
| At least 100 position episodes, full sample | 35 selected; 41 maximum | FAIL |
| OOS net Sharpe >= 0.40 | 0.147 | FAIL |
| OOS maximum drawdown <= 25% | -49.2% | FAIL |
| Positive in >= 2 of the 3 observable OOS macro regimes | 1 of 3 | FAIL |
| 2011-2015 bear stress not a failure | Positive, Sharpe 0.566 | PASS |
| Positive OLS alpha versus buy-and-hold (t > 1.96) | Alpha -4.14%, t = -1.411 | FAIL |
| Vol scaling not the whole result | Scaling reduced OOS Sharpe at 6 months | PASS |
| OOS P&L sign stable at 1.5x costs | Positive | PASS |
| Deflated Sharpe p < 0.10 | 0.8402 | FAIL |

The binding constraint is again power: 35 full-sample episodes and 19 OOS
episodes, with no configuration above 41. INCONCLUSIVE takes precedence over the
economic gates.

The point estimate is not broad-based. One long episode from 2023-12 to
2026-06 earns USD 51,221, which is 210.7% of the OOS episode sum; removing it
turns the OOS episode result to USD -26,916. Only 3 of 19 OOS episodes are
profitable, and the short side loses money over both the full and OOS samples.

### 3.5 What the verdicts mean

- **FAIL is a rejection.** T1 may not be re-tuned on this OOS period and may not be carried forward.
- **INCONCLUSIVE is not a soft pass.** T2 and T3 cannot be promoted, cannot be added to a live or demo candidate set, and cannot be declared failed with confidence. They are closed without promotion.
- No family is CONDITIONAL, because none met the gates subject to a stated qualification.
- No family is PASS.

---

## 4. Buy-and-hold and random-entry comparisons

### 4.1 Buy-and-hold gold

Buy-and-hold gold is the same comparator for all three families: same period,
same costs, same USD 100,000 base.

| Window | Net P&L | CAGR % | Sharpe | Max DD % | Vol % |
| --- | ---: | ---: | ---: | ---: | ---: |
| IS (2004-2016) | 176,683 | 7.88 | 0.499 | -44.7 | 18.8 |
| OOS (2017-2026) | 248,260 | 13.71 | 0.889 | -26.2 | 15.8 |
| FULL (2004-2026) | 863,985 | 10.29 | 0.646 | -44.7 | 17.6 |

### 4.2 Strategy versus buy-and-hold

| Family | OOS net USD | OOS Sharpe | B&H OOS net | B&H OOS Sharpe | B&H OOS max DD | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| T1 | -206,352 | -1.787 | 248,260 | 0.889 | -26.2% | Loses on every measure |
| T2 | 40,052 | 0.374 | 248,260 | 0.889 | -26.2% | Lower return and Sharpe; drawdown gate passes on the compounded basis |
| T3 | 15,905 | 0.147 | 248,260 | 0.889 | -26.2% | Lower return and Sharpe, deeper DD |

Buy-and-hold gold dominates every family on the pre-registered risk-adjusted
comparator. No strategy Sharpe approaches 0.889. T1 and T3 also draw down more
than the benchmark's -26.2%; T2's compounded drawdown is shallower (-21.4%), but
its return and Sharpe are far lower.

Beta and alpha versus buy-and-hold confirm the same conclusion:

| Family | OOS beta | OOS annualised alpha |
| --- | ---: | ---: |
| T1 | 0.130 | -21.72% |
| T2 | 0.535 | -3.44% |
| T3 | 0.405 | -4.14% |

None of the families demonstrates return beyond long gold exposure.

### 4.3 Random-entry and random-sign controls

| Family | Control design | Actual | Random median | Random p95 | Percentile | Control verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| T1 | Matched exposure, 300 runs, full-sample constant risk | -592,074 | -322,061 | -39,916 | 11.3 | FAIL |
| T2 | Matched exposure, 300 runs, non-terminal schedule | 15,061 | -3,802 | 18,189 | 90.7 | FAIL |
| T3 | Random sign, 500 permutations, full sample | 97,311 | 20,941 | 96,582 | 95.0 | PASS (marginal) |

- **T1 is worse than random entry.** The pullback filter did not add information; it selected slightly adverse entry points.
- **T2 fails its corrected control.** The actual non-terminal schedule sits at the 90.7th percentile, below the 95th-percentile bar. The naive first implementation silently dropped trades pushed past the sample end and is not reported.
- **T3 passes by USD 729.** The actual full-sample P&L of USD 97,311 is above the 95th percentile of USD 96,582, but only marginally. A marginal control pass on one large episode is not evidence of a durable edge.

### 4.4 Missing controls

Phase 2A Section 11.10 also lists a 60/40 portfolio and an always-long,
same-vol-target control. These are not implemented. The approved Phase 2B data
set contains only gold, and T2 has no volatility target, so either control would
require inventing a definition. They are disclosed as missing, not treated as
passes.

---

## 5. Cost-stress results

### 5.1 OOS constant-risk results by cost level

| Family | Net 1.0x | PF 1.0x | Net 1.5x | PF 1.5x | Net 2.0x | PF 2.0x | Sign flip |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T1 | -206,352 | 0.734 | -334,566 | 0.614 | -461,760 | 0.520 | Already negative |
| T2 | 40,052 | 4.436 | 36,035 | 3.967 | 32,018 | 3.539 | None |
| T3 | 15,905 | 1.452 | 7,409 | 1.278 | -1,086 | 1.127 | At 2.0x |

Every trial in every family is monotone in costs: net P&L falls as the cost
multiple rises. No higher cost multiple improved any result.

### 5.2 Interpretation

- **T1** is already deeply negative at 1.0x, so no stress multiple can rescue it. Its costs are dominated by spread and slippage: OOS spread and slippage USD 215,215, commission USD 17,113 and swap USD 6,805 against gross P&L of USD 32,794.
- **T2** survives 1.0x, 1.5x and 2.0x. Its OOS profit factor remains above 3.5 at 2.0x. The formal cost gate passes, but swap dominates the cost base: USD 7,746 of USD 8,072 total OOS costs.
- **T3** stays positive at 1.5x (USD 7,409) but turns negative at 2.0x (USD -1,086). Section 11.12 makes only the 1.5x flip a kill criterion, so the formal gate passes; the 2.0x result is reported as an additional stress. Swap is USD 15,437 of USD 16,432 total OOS costs, and rises to USD 30,873 at 2.0x.

The cost results are therefore a central finding, not a secondary check: the
slower families are profitable only as a small residual after swap, and the
faster family cannot pay for its own turnover.

---

## 6. Statistical test findings

| Family | Deflated Sharpe | White's Reality Check | Harvey-Liu-Zhu t | Bootstrap 95% Sharpe CI | Tests passed |
| --- | --- | --- | ---: | --- | --- |
| T1 | p = 1.0000 | p = 1.0000 | -5.944 | [-2.486, -1.139] | 0 of 4 |
| T2 | p = 0.9670 | p = 0.9990 | 1.160 | [-0.312, 1.001] | 0 of 4 |
| T3 | p = 0.8402 | p = 0.9900 | 0.442 | [-0.602, 0.861] | 0 of 4 |

- **No family clears a single statistical test.** The best Deflated Sharpe p-value is 0.8402 (T3), the best Reality Check p-value is 0.9900 (T3), and every bootstrap interval includes zero.
- **Deflation uses N = 32**, the full pre-registered T1 + T2 + T3 count. This is conservative for any one family but correct for the programme as a whole.
- **The Reality Check's best trial is not the IS-selected trial** in T2 or T3. In T2 the best OOS trial is the 20/100 pair, not the selected 50/200 pair; in T3 it is `T3-06-LB24-UNSCALED`, not the selected 6-month trial. The OOS ordering is unstable.
- **Selection decay is present in every family.** T1's IS-selected trial is negative OOS. T2's selected 50/200 pair is not the OOS-best pair. T3's selected 6-month lookback ranks last of six on OOS Sharpe.
- **A programme that runs 32 trials and finds no p-value below 0.10 has not found a candidate.**

---

## 7. Historical swap and spread limitations

### 7.1 Swap

The swap model applies the current MT5 demo schedule to the entire 2004-2026
history:

| Component | Assumption |
| --- | --- |
| Swap long | USD -0.126 per oz per day |
| Swap short | USD -0.046 per oz per day |
| Triple swap | Wednesday |
| Treatment | Charged as a positive cost |

This is a testing assumption, not historical broker data. Historical swap
schedules differed, and no historical swap series is available from the feed.

The limitation is material for T2 and T3 because their holding periods are
months to years:

- **T2:** swap is USD 7,746 of USD 8,072 total OOS costs.
- **T3:** swap is USD 15,437 of USD 16,432 total OOS costs, or 93.9%. At 2.0x it becomes USD 30,873 and turns the OOS result negative.

The T2 and T3 point estimates are therefore partly a bet that the current swap
schedule persists over multi-month holds. A different historical schedule would
change the net result, though it would not repair the failed statistical tests,
the low trade counts or the buy-and-hold shortfall.

### 7.2 Spread

| Series | Spread source | Median | p95 |
| --- | --- | ---: | ---: |
| D1 | Daily mean of the H1 spreads inside the 22:00-to-22:00 session | 0.418 | 0.677 |
| H4 | Bar-level BID/ASK | 0.409 | - |
| H1 | Completed H1 bar BID/ASK | 0.386 | 0.712 |
| M15 | Spread of the last completed H1 bar, applied at the M15 open | 0.384 | - |

Limitations:

- The D1/H4 spread is a daily or bar average, not a point-in-time quote at the execution open. This affects T2 and T3 most, because execution is at a specific open.
- The M15 spread is taken from the completed H1 bar, not from tick data. Intra-hour spread spikes, including news spikes, are smoothed and costs are likely understated in stress.
- Slippage is a fixed fraction of spread (0.5x entries and signal exits, 1.0x stop exits). Real slippage is state-dependent and worse in fast markets.
- The abnormal Phase 0 spread of approximately USD 58.12 was excluded entirely and was not used as a baseline, stress level or filter.

Commission is USD 0.07 per oz round turn (USD 7.00 per 100 oz lot). No other
transaction costs are modelled.

### 7.3 What cannot be fixed retrospectively

No historical broker spread, commission or swap data exists for 2004-2026 on
the connected feed. The cost model is an explicit, reproducible testing
assumption, not a reconstruction of Exness execution. It was stressed at 1.0x,
1.5x and 2.0x precisely because the baseline cannot be measured from the broker.

---

## 8. Data-source and candle-boundary limitations

### 8.1 Data source

All three families use one price source: Dukascopy XAUUSD BID/ASK candles,
retrieved 2026-11-05. The extracted MT5 demo D1/H4 series is an independent
cross-check, not a second backtest source.

| Series | Rows | First bar (UTC) | Last bar (UTC) | Duplicates | Bad OHLC |
| --- | ---: | --- | --- | ---: | ---: |
| D1 | 5,918 | 2004-01-01 22:00 | 2026-10-30 22:00 | 0 | 0 |
| H4 | 35,741 | 2003-12-31 22:00 | 2026-10-30 18:00 | 0 | 0 |
| H1 | 138,451 | 2004-01-01 00:00 | 2026-10-30 20:00 | 0 | 0 |
| M15 | 551,336 | 2004-01-01 00:00 | 2026-11-04 23:45 | 0 | 0 |

Dukascopy is a datafeed, not Exness execution. The cross-check supports its use
but does not make it broker data:

- 5,752 common D1 dates: median absolute close difference 0.0277%, 95th percentile 0.1497%, maximum 1.6102%, daily log-return correlation 0.99549.
- 138,451 common H1 bars: resampling M15 closes reproduces the H1 close to 0.01 on 99.555% of bars (median absolute difference 0.00000).

The data are fit for the intended purpose. They remain a datafeed substitution.

### 8.2 Candle-boundary convention

| Series | Convention |
| --- | --- |
| D1 | 22:00-to-22:00 UTC trading day, labelled at the 22:00 close |
| H4 | 22:00-aligned UTC (22/02/06/10/14/18), stamped at the open |
| H1 | UTC hour, stamped at the open |
| M15 | UTC quarter hour, stamped at the open |

The MT5 server runs on UTC+2, and its H4 bars close at 22/02/06/10/14/18 UTC
rather than at 00/04/08/12/16/20 UTC. The Dukascopy series was therefore built
on UTC boundaries; the MT5 series uses different boundaries and is used only as
a cross-check. The convention was fixed in writing before signal generation and
applied identically to IS and OOS.

Boundary consequences:

- The D1 bar labelled at the 22:00 close includes the rollover and is not a midnight-to-midnight calendar day.
- H4 regime signals and M15 entries in T1 are evaluated on different bar grids; the mismatch is part of the strategy design but is a source of execution approximation.
- A position entered before a period boundary and exited inside it is attributed to the entry date in trade-level tables and to the exit window in equity-curve tables. The two conventions are reconciled explicitly in each family report, and the equity-curve convention is the economic record.

### 8.3 Warm-up and truncation

- **T1:** 1,000 completed H4 bars before the first signal (about 166 trading days); first permissible signal 2004-08-17.
- **T2:** 1,000 completed D1 bars; first signal bar 2007-11-01, first possible entry 2007-11-02. The warm-up removes 2004-2007, so the trade-count gate is evaluated over 2008-2026 (18.66 years).
- **T3:** 504 completed D1 bars, the longest lookback in the grid; first eligible month-end 2005-12-30.

The sample is truncated at the OOS end, 2026-06-30. Data after that date exists
in the processed series but was not used for any result. The warm-ups are
data-integrity rules, not strategy parameters, and apply equally to all trials
in a family.

### 8.4 Execution model

All results come from a vectorised Python bar simulator, not the MT5 tester:

- Signals are computed on closed bars only, with next-open execution.
- Intrabar stops and trails are approximated from bar OHLC.
- Stop-first priority is assumed when a bar contains both stop and target.
- Gaps fill at the open, not at the stop price.
- There are no partial fills and no intraday path.
- T1's H1 stops and T2's disaster stops are approximations of broker execution.
- No new entries occur within the rollover window.

These are model risks. They are most relevant to T1, whose high trade count and
tight stops magnify bar-resolution error, and least relevant to T3, whose
monthly rebalance has no stop.

### 8.5 Single instrument

The universe is gold only. This is the main reason the 60/40 and always-long
same-vol-target controls are not implemented, and it is a structural limit on
what Phase 2B can conclude. A single instrument in a secular bull market gives
buy-and-hold a strong prior advantage; that is precisely why the benchmark was
mandatory.

---

## 9. Lessons learned

1. **Costs decide the outcome.** T1's gross edge was too small to pay for its turnover: USD 32,794 gross against USD 239,133 of costs. Faster trend rules on gold at retail costs need a much larger gross edge than the data supplies.

2. **Slow rules are structurally underpowered on one instrument.** T2's selected trial has 20 trades; T3's has 35 episodes. Neither can reach 100 without changing the rule or the trade definition. More history would not solve this: the constraint is the signal frequency, not the sample length.

3. **In-sample selection does not survive out of sample.** Every family shows selection decay. T1's IS-selected trial loses OOS; T2's OOS-best pair is not the IS-selected pair; T3's IS-selected lookback ranks last of six on OOS Sharpe. Selecting on a 7-trade IS Sharpe (T2) is especially fragile.

4. **Multiple-testing correction is not a formality.** With 32 trials, the best Deflated Sharpe p-value is 0.8402 and the best Reality Check p-value is 0.9900. The programme did not find a candidate, and no amount of post-hoc relabelling changes that.

5. **Buy-and-hold is a hard benchmark in a secular bull market.** Gold's OOS Sharpe of 0.889 and maximum drawdown of -26.2% beat all three families. Any future candidate must beat it on a risk-adjusted basis, not merely produce a positive return.

6. **Random controls separate signal from exposure.** T1 is worse than random entry, T2 fails its corrected control, and T3 passes by USD 729. The controls revealed that much of the apparent performance is long exposure, not timing skill.

7. **Concentration is not robustness.** T2's largest trade is 96.8% of OOS P&L; T3's largest episode is 210.7% of the OOS episode sum. A positive point estimate driven by one trade is not a broad-based edge.

8. **The swap assumption carries the slow strategies.** Swap is 96.0% of T2's OOS costs and 93.9% of T3's. Applying a current demo schedule to 2004-2026 is a material assumption, and T3 already turns negative at 2.0x costs.

9. **Data provenance and bar boundaries must be fixed in writing before signals are generated.** The Dukascopy substitution, the UTC boundaries, the MT5 UTC+2 mismatch and the warm-up rules all had to be resolved before the first trial, and all are disclosed.

10. **Pre-registration and disclosure preserved the integrity of a negative result.** Three corrections were made and disclosed before the final numbers; no rule, parameter, split or gate changed; no trial was dropped or re-run. A clean FAIL and two clean INCONCLUSIVEs are more useful than an unpublishable near-miss.

11. **Do not add filters to rescue a failed rule.** The T4 ablation was not run, and no post-hoc filter, parameter or subperiod selection was used to improve any verdict. A candidate that only passes after adding a filter must be rejected, not promoted.

12. **The OOS period is spent.** It has been used once, for all three families. Any further test of these rules on 2017-2026 would be in-sample. A future programme needs a new pre-registered sample, or a diversified multi-asset universe, before these hypotheses can be tested again.

---

## 10. Approval status

**No trend-following strategy from Phase 2B is approved for implementation.**

- T1 is **FAIL** and is rejected as a family.
- T2 is **INCONCLUSIVE** and is not promoted.
- T3 is **INCONCLUSIVE** and is not promoted.
- No strategy is added to a live or demo candidate set.
- No parameter set is carried forward as a candidate.
- No MQL5 implementation, live trading or demo trading was performed.
- No EA code, Phase 1 artefact, roadmap entry or historical result was modified.

Phase 2B is closed and frozen. Any future work on these hypotheses must begin
with a new pre-registered protocol. It would need, at minimum:

1. A new sample or a diversified multi-asset universe, so the OOS period is not reused.
2. Enough independent trades or episodes to clear the 100-observation power threshold.
3. Survival at 2.0x costs and under a defensible historical swap assumption.
4. A result that beats both buy-and-hold and the random control.
5. A Deflated Sharpe that accounts for the full search, with p < 0.10.

None of those conditions is met in Phase 2B. Phase 3 is not started by this
document.

---

## Appendix A - Artefact map

| Artefact | Path |
| --- | --- |
| Phase 2A rules and protocol | `Docs/Strategy/Phase-2A-Trend-Following-Research.md` |
| Phase 2B closure (this document) | `Docs/Strategy/Phase-2B-Final-Review.md` |
| Comparative report | `Research/Phase-2B/reports/Phase-2B-comparative-report.md` |
| T1 family report | `Research/Phase-2B/reports/T1-report.md` |
| T2 family report | `Research/Phase-2B/reports/T2-report.md` |
| T3 family report | `Research/Phase-2B/reports/T3-report.md` |
| T1 methodology note | `Research/Phase-2B/reports/T1-methodology-note.md` |
| T2 methodology note | `Research/Phase-2B/reports/T2-methodology-note.md` |
| T3 methodology note | `Research/Phase-2B/reports/T3-methodology-note.md` |
| Data readiness report | `Research/Phase-2B/reports/data-readiness.md` |
| Data QA report | `Research/Phase-2B/reports/data-qa-mt5demo.md` |
| Shared engine | `Research/Phase-2B/tools/core.py` |
| Family runners | `Research/Phase-2B/tools/run_t1.py`, `run_t2.py`, `run_t3.py` |
| Family reporters | `Research/Phase-2B/tools/report_t1.py`, `report_t2.py`, `report_t3.py` |
| Comparative reporter | `Research/Phase-2B/tools/report_comparative.py` |
| Trial tables | `Research/Phase-2B/results/T{1,2,3}/t*_trial_table.csv` |
| Summary JSON | `Research/Phase-2B/results/T{1,2,3}/t*_summary.json` |
| Processed series | `Research/Phase-2B/data/processed/XAUUSD_{D1,H4,H1,M15}.parquet` |

## Appendix B - Preservation and change control

- All original family reports, methodology notes, trial tables, summary JSON, equity curves and trade logs are preserved in place.
- No historical result was recomputed, overwritten or optimised for this closure.
- No trial was rerun, no parameter was changed and no alternative specification was tested.
- `EA/`, `Config/`, `Tests/Phase-1/`, `Docs/Phase-1-Execution-Engine.md`, `CHANGELOG.md` and `ROADMAP.md` are outside this phase and untouched.
- This document is a decision record. It does not alter the Phase 2A protocol or the Phase 2B reports.

---

**Closure decision:** PHASE 2B FROZEN. No strategy promoted. No implementation approved.
