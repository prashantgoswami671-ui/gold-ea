# Phase 2B - T3 family report

**Family:** T3 - Time-series momentum (TSMOM) overlay

**Status:** INCONCLUSIVE

**Phase:** 2B controlled backtesting, family 3 of 3 (T1 -> T2 -> T3)

**Source of rules:** `Docs/Strategy/Phase-2A-Trend-Following-Research.md`
(v0.2), Section 8.3, grid in Section 11.7, gates in Section 8.3 and 11.12.
**Operational readings:** `Research/Phase-2B/reports/T3-methodology-note.md`,
frozen before the first T3 trial. That note also records the one pre-run
implementation correction and the treatment of the 2.0x cost multiple.

---

## A. Identity

| Item | Value |
| --- | --- |
| Hypothesis | Gold's own trailing return predicts its next-month return, and a volatility-targeted long/short position exploiting it produces a positive risk-adjusted return that is not merely long-gold beta. |
| What it tests | Whether the best-documented academic effect survives on a single instrument at retail costs, and whether it survives the volatility-scaling critique. |
| Grade | E2 for the diversified version; E3 for the single-instrument version after Huang et al. (2020) and Kim, Tse & Wald (2016). |
| Timeframe | D1 signal; monthly rebalance; next D1 open execution |
| Trials | 6 pre-registered combinations (3 lookbacks x 2 scaling modes) |
| Data | Dukascopy XAUUSD BID/ASK candles, retrieved 2026-11-05; truncated at the OOS end |
| Symbol | XAUUSD, 2 digits, 100 oz per lot, minimum volume 0.01, volume step 0.01 |
| Test period | 2004-01-01 to 2026-06-30 |
| IS | 2004-01-01 to 2016-12-31 |
| OOS | 2017-01-01 to 2026-06-30 |
| Warm-up | 504 completed D1 bars; first eligible month-end 2005-12-30 22:00:00+00:00 |
| Rebalance dates | 246 month-ends with an executable next open |
| Trial IDs | T3-01 ... T3-06 (Appendix) |

Pre-registered grid:

| Trial | Lookback | Scaling |
| --- | --- | --- |
| T3-01 | 6 months (126 D1 bars) | scaled |
| T3-02 | 6 months (126 D1 bars) | unscaled |
| T3-03 | 12 months (252 D1 bars) | scaled |
| T3-04 | 12 months (252 D1 bars) | unscaled |
| T3-05 | 24 months (504 D1 bars) | scaled |
| T3-06 | 24 months (504 D1 bars) | unscaled |

**Trade definition.** A T3 trade is one **position episode**: from entry
(the first rebalance after a sign flip) to exit (the rebalance at the next
sign flip, or the end of data). Monthly size adjustments inside an episode
are rebalances, not new trades. This measures independent economic bets;
counting every monthly rebalance would mechanically clear the 100-trade
gate without adding independent observations. The project owner selected
this definition on 2026-11-06, before T3 ran.

## B. Capital and execution

| Item | Value |
| --- | --- |
| Initial capital | USD 100,000 |
| Signal | Sign of `close_t / close_{t-L} - 1`, L = 126 / 252 / 504 D1 bars |
| Rebalance | Last available D1 bar of each calendar month |
| Execution | Next D1 open after the month-end signal bar |
| Volatility estimate | 60-day EWMA of D1 log returns, `span=60`, `adjust=False`, annualised by `sqrt(252)` |
| Scaled weight | `min(0.10 / realised_vol, 2.0)` of equity notional |
| Unscaled weight | 1.0x equity notional, constant |
| Target volatility | 10% annualised |
| Max positions | 1 |
| Stop loss | None; the monthly rebalance and sign flip are the risk control |
| Execution model | Vectorised Python bar simulator; no MT5 tester |
| Overnight accounting | On a rebalance day the gap from prior close to the execution open belongs to the old size; the intraday move from open to close belongs to the new size |
| Rollover | Every D1 bar; triple swap on the Wednesday 22:00 rollover |

### Cost model

| Component | Assumption |
| --- | --- |
| Spread | Dukascopy BID/ASK, D1 session spread. The same time-varying series used by T1 and T2 |
| Buy turnover | 1.5 x spread per oz: cross to ask plus 0.5 spread slippage |
| Sell turnover | 0.5 x spread per oz: sell at bid less 0.5 spread slippage |
| Commission | USD 0.07 per oz round turn, split as USD 0.035 per oz per side |
| Swap long | USD -0.126 per oz per day, charged as a positive cost |
| Swap short | USD -0.046 per oz per day, charged as a positive cost |
| Other costs | None modelled |

All costs are stressed at 1.0x, 1.5x and 2.0x. The abnormal ~USD 58.12
Phase 0 spread is not used anywhere. The D1 spread is a daily average, not
a point-in-time quote at the monthly execution open; this is the only
spread available at D1 resolution and is disclosed as a limitation.

A buy-then-sell cycle at one spread reproduces the T1/T2 round-trip cost
exactly. The same simulator convention is used in the random-sign control.

## C. Performance

Baseline cost (1.0x), pre-registered sizing. The compounded account is the
confirmatory record; each period is rebased to USD 100,000 at its start, so
IS and OOS are not additive.

| Trial | Period | Episodes | PF | Sharpe | Net P&L | Max DD % | Win % | Hold d | Costs % gross | Exposure % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T3-01-LB6-SCALED | IS | 16 | 3.564 | 0.613 | 112,272 | -21.6 | 62.5 | 260 | 26.1 | 84.6 |
| T3-01-LB6-SCALED | OOS | 19 | 1.396 | 0.150 | 10,626 | -40.2 | 15.8 | 175 | 43.2 | 100.0 |
| T3-02-LB6-UNSCALED | IS | 16 | 2.565 | 0.413 | 116,740 | -37.4 | 62.5 | 260 | 36.5 | 84.6 |
| T3-02-LB6-UNSCALED | OOS | 19 | 1.658 | 0.228 | 25,656 | -46.5 | 15.8 | 175 | 33.5 | 100.0 |
| T3-03-LB12-SCALED | IS | 23 | 2.055 | 0.328 | 45,258 | -24.2 | 47.8 | 177 | 37.8 | 84.6 |
| T3-03-LB12-SCALED | OOS | 18 | 1.597 | 0.325 | 33,553 | -34.0 | 16.7 | 189 | 35.0 | 100.0 |
| T3-04-LB12-UNSCALED | IS | 23 | 1.409 | 0.186 | 26,192 | -43.3 | 43.5 | 177 | 61.2 | 84.6 |
| T3-04-LB12-UNSCALED | OOS | 18 | 1.802 | 0.349 | 51,417 | -43.3 | 22.2 | 189 | 30.5 | 100.0 |
| T3-05-LB24-SCALED | IS | 4 | 2.900 | 0.342 | 48,305 | -28.6 | 50.0 | 1,012 | 44.7 | 84.6 |
| T3-05-LB24-SCALED | OOS | 5 | 15.164 | 0.721 | 103,672 | -20.3 | 60.0 | 687 | 16.9 | 100.0 |
| T3-06-LB24-UNSCALED | IS | 4 | 2.705 | 0.319 | 73,773 | -37.6 | 25.0 | 1,012 | 51.1 | 84.6 |
| T3-06-LB24-UNSCALED | OOS | 5 | 12.272 | 0.623 | 130,249 | -28.7 | 60.0 | 687 | 17.1 | 100.0 |

`n/a` in the cost column means gross P&L was zero or negative, so the
cost-to-gross ratio is undefined. A PF of 0.000 means the trial had no
winning episodes in that period.

### Constant-risk notional results

The same rule re-run with the notional based on the initial USD 100,000
(no compounding). Weights, signals and costs are unchanged. This is the
basis for Sharpe, drawdown, regime attribution and all statistics, matching
T1 and T2. Values are notional USD on a USD 100,000 base.

| Trial | Full eps | Full net | Full Sharpe | IS net | IS Sharpe | OOS net | OOS PF | OOS Sharpe | OOS DD % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T3-01-LB6-SCALED | 35 | 97,311 | 0.399 | 81,966 | 0.606 | 15,905 | 1.452 | 0.147 | -49.2 |
| T3-02-LB6-UNSCALED | 35 | 130,386 | 0.328 | 96,939 | 0.403 | 34,128 | 1.740 | 0.218 | -58.9 |
| T3-03-LB12-SCALED | 41 | 79,320 | 0.325 | 44,168 | 0.326 | 34,610 | 1.584 | 0.320 | -39.8 |
| T3-04-LB12-UNSCALED | 41 | 96,657 | 0.243 | 43,411 | 0.181 | 52,580 | 1.796 | 0.336 | -53.6 |
| T3-05-LB24-SCALED | 9 | 122,435 | 0.502 | 46,291 | 0.342 | 76,704 | 14.705 | 0.709 | -21.7 |
| T3-06-LB24-UNSCALED | 9 | 168,811 | 0.425 | 75,120 | 0.312 | 94,373 | 11.945 | 0.604 | -30.8 |

### Cost stress, OOS constant-risk P&L

All six trials, OOS constant-risk notional P&L at 1.0x, 1.5x and 2.0x.
Higher cost multiples can only reduce net P&L; the table is monotone for
every trial. The 1.5x sign flip is the Section 11.12 kill criterion; 2.0x
is reported as an additional stress.

| Trial | Net 1.0x | PF 1.0x | Net 1.5x | PF 1.5x | Net 2.0x | PF 2.0x |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| T3-01-LB6-SCALED | 15,905 | 1.452 | 7,409 | 1.278 | -1,086 | 1.127 |
| T3-02-LB6-UNSCALED | 34,128 | 1.740 | 23,849 | 1.532 | 13,570 | 1.351 |
| T3-03-LB12-SCALED | 34,610 | 1.584 | 26,413 | 1.394 | 18,216 | 1.228 |
| T3-04-LB12-UNSCALED | 52,580 | 1.796 | 42,484 | 1.586 | 32,388 | 1.400 |
| T3-05-LB24-SCALED | 76,704 | 14.705 | 67,289 | 9.235 | 57,875 | 6.418 |
| T3-06-LB24-UNSCALED | 94,373 | 11.945 | 83,045 | 8.368 | 71,716 | 6.179 |

### Selected trial

Selected on IS net Sharpe: **T3-01-LB6-SCALED** (lookback
6 months, scaled).
This is the only selection rule used; OOS is never used for selection.

| Metric | IS | OOS |
| --- | ---: | ---: |
| Episodes | 16 | 19 |
| Profit factor | 3.564 | 1.396 |
| Sharpe | 0.613 | 0.150 |
| Net P&L | 112,272 | 10,626 |
| Max drawdown % | -21.6 | -40.2 |
| Win rate % | 62.5 | 15.8 |
| Average holding days | 260 | 175 |
| Costs as % of gross | 26.1 | 43.2 |
| Expectancy (R) | 0.689 | 0.268 |
| Exposure % | 84.6 | 100.0 |

The selected trial has 16 IS episodes and 19 OOS episodes. The IS Sharpe of 0.613 falls to 0.150 out of sample. With this few independent episodes, both estimates are very
noisy; the decay is nonetheless in the expected direction for a selected
rule.

The constant-risk record for the same trial:

| Period | Episodes | PF | Sharpe | Notional P&L | Max DD abs | Max DD % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FULL | 35 | 2.240 | 0.399 | 97,311 | -49,197 | -49.2 |
| IS | 16 | 3.958 | 0.606 | 81,966 | -24,030 | -24.0 |
| OOS | 19 | 1.452 | 0.147 | 15,905 | -49,197 | -49.2 |

For the constant-risk curve, max drawdown is measured in dollars against
the fixed USD 100,000 notional base. It is not a percentage of a
compounded peak, so it can exceed the compounded drawdown percentage.

### Selected trial, OOS metrics by cost level (constant risk)

| Cost | Episodes | Trade net | Equity net | Diff | PF | Sharpe | Sortino | DD abs | Win % | Cost % gross |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1.0x | 19 | 24,304 | 15,905 | -8,399 | 1.452 | 0.147 | 0.196 | -49,197 | 15.8 | 40.3 |
| 1.5x | 19 | 16,088 | 7,409 | -8,679 | 1.278 | 0.068 | 0.091 | -51,616 | 15.8 | 60.5 |
| 2.0x | 19 | 7,872 | -1,086 | -8,958 | 1.127 | -0.010 | -0.013 | -54,035 | 15.8 | 80.7 |

**Trade net** is the sum of the 19 episodes entered
inside the OOS window. **Equity net** is the OOS P&L of the constant-risk
curve. **Diff** is equity minus trade. The two differ because one short
episode entered 2016-11-01 and exited 2017-06-01 straddles the boundary.
The episode sum counts only episodes entered in OOS, so it excludes that
episode entirely. The equity window counts only P&L earned after
2016-12-31, so it includes the episode's post-boundary loss but excludes
its pre-2017 gain. At 1.0x the post-boundary loss is
USD 8,399; the gap widens at higher cost multiples
because that episode's swap accrual grows. PF, win rate and
cost-to-gross are episode-level (entered-in-window) measures; Sharpe,
Sortino, drawdown and equity net are equity-curve measures. Return % and
CAGR are not meaningful for a non-compounding notional curve, so they
are not shown.

### Gross-to-net decomposition

#### Full sample, 1.0x, constant risk

| Component | USD |
| --- | ---: |
| Gross P&L (frictionless) | 138,032 |
| Spread and slippage | -1,970 |
| Commission | -185 |
| Swap | -38,566 |
| Net P&L | 97,311 |
| Total costs | -40,721 |

Identity: 138,032 - 40,721 = 97,311. The full-sample equity-curve P&L is the
same number because every episode is inside the window.

#### OOS, 1.0x, constant risk, episodes entered in OOS

| Component | USD |
| --- | ---: |
| Gross P&L (frictionless) | 40,737 |
| Spread and slippage | -904 |
| Commission | -92 |
| Swap | -15,437 |
| Net P&L (episode sum) | 24,304 |
| Total costs | -16,432 |

Identity: 40,737 - 16,432 = 24,304. This table attributes each episode to the
period in which it was **entered**. The OOS equity-curve P&L is
USD 15,905, which is USD 8,399 lower.
The difference is the post-boundary portion of one straddling episode
(2016-11-01 to 2017-06-01, short, net USD -869). The equity-curve convention is the correct economic
record for the OOS period; the episode table is the correct attribution
for cost accounting. Both are shown so the reconciliation is explicit.

### Long/short attribution

| Window | Episodes | Long eps | Short eps | Long P&L | Short P&L | Net |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FULL | 35 | 18 | 17 | 115,382 | -18,071 | 97,311 |
| IS | 16 | 8 | 8 | 60,731 | 12,276 | 73,007 |
| OOS | 19 | 10 | 9 | 54,650 | -30,346 | 24,304 |

The rule is long-biased in P&L. Across the full sample the short side
loses USD 18,071 while the long side
earns USD 115,382. Out of sample the short side loses
USD 30,346 against long P&L of
USD 54,650. A rule that only makes money when long
is a long-biased rule in disguise, unless the short side earns its keep
in a specific regime; the 2011-2015 stress is the one window where it did.

### Concentration of the selected trial

| Measure | Full sample | OOS |
| --- | ---: | ---: |
| Episodes | 35 | 19 |
| Winning episodes | 13 | 3 |
| Net P&L (episode sum) | 97,311 | 24,304 |
| Largest single win | 51,221 | 51,221 |
| Largest win as % of net | 52.6 | 210.7 |
| Top 3 wins | 120,576 | 78,127 |
| Top 3 as % of net | 123.9 | 321.5 |
| Net excluding largest win | 46,091 | -26,916 |

One long episode, entered 2023-12-01
and exited 2026-06-30, earns
USD 51,221: 52.6%
of full-sample net and 210.7%
of the OOS episode sum. Removing that single episode turns the OOS
episode result to USD -26,916. Only
3 of 19 OOS episodes are profitable;
the positive point estimate is a small number of large trends, not a
broad-based edge.

## D. Benchmarks and controls

### Buy-and-hold gold

| Window | Net P&L | CAGR % | Sharpe | Max DD % | Vol % |
| --- | ---: | ---: | ---: | ---: | ---: |
| IS | 176,683 | 7.88 | 0.499 | -44.7 | 18.8 |
| OOS | 248,260 | 13.71 | 0.889 | -26.2 | 15.8 |
| FULL | 863,985 | 10.29 | 0.646 | -44.7 | 17.6 |

OOS buy-and-hold earns USD 248,260 with
Sharpe 0.889 and maximum drawdown
-26.2%. The selected T3 trial earns
USD 15,905 constant-risk with Sharpe
0.147 and maximum drawdown
-49.2%. Buy-and-hold dominates on net return,
risk-adjusted return and drawdown. The momentum overlay therefore does
not beat the passive alternative on the pre-registered comparator.

The 60/40 portfolio and always-long, same-vol-target controls are not
implemented. The approved Phase 2B data set contains only gold; inventing
a 60/40 definition would add an unapproved assumption. This is disclosed
as a limitation, not treated as a pass.

### Random-sign matched-exposure control

| Statistic | Value |
| --- | ---: |
| Permutations | 500 |
| Rebalance dates | 246 |
| Long months (actual) | 171 |
| Short months (actual) | 75 |
| Zero months (actual) | 0 |
| Actual full-sample P&L | 97,311 |
| Random median | 20,941 |
| Random 5th percentile | -52,396 |
| Random 95th percentile | 96,582 |
| Percentile of actual | 95.0 |

The control keeps the actual weight schedule and the actual number of
long and short months, and randomly permutes which rebalance date gets
which sign. It therefore holds exposure, turnover and costs broadly
constant and tests only whether the momentum sign carries information.
The actual full-sample P&L of USD 97,311 is
above the 95th percentile of USD 96,582 by
USD 729,
so it clears the Section 11.10 bar only marginally. The random median is
positive because 171 of 246 rebalance months
are long in a secular gold bull market;
the control is not evidence that the timing is irrelevant, but it is not
comfortable evidence that it is valuable either.

### Scaled versus unscaled

| Lookback | Scaled OOS Sharpe | Unscaled OOS Sharpe | Scaled OOS net | Unscaled OOS net |
| --- | ---: | ---: | ---: | ---: |
| 6 months | 0.147 | 0.218 | 15,905 | 34,128 |
| 12 months | 0.320 | 0.336 | 34,610 | 52,580 |
| 24 months | 0.709 | 0.604 | 76,704 | 94,373 |

At the selected 6-month lookback, scaling **reduces** OOS Sharpe
(0.147 scaled versus 0.218 unscaled).
At 24 months scaling helps Sharpe, but that configuration has only 9 full-sample episodes.
The vol-scaling gate passes because the selected scaled trial is not
strong; the result is not a vol-scaling artefact.

## E. Robustness

### Macro regimes (OOS)

| Regime | Days | Sharpe | Total return % |
| --- | ---: | ---: | ---: |
| M3 reflation/range | 773 | -0.259 | -9.3 |
| M4 shock/stimulus | 517 | -0.148 | -4.6 |
| M5 regime break | 1,159 | 0.503 | 26.9 |

1 of 3 observable OOS macro regimes is positive. M1 and M2 are in-sample
and cannot contribute. The gate in
Section 8.3 says '2 of the 3'; Section 11.6 defines five regimes, so the
resolved reading is at least 2 of the 3 OOS regimes. The rule fails that
gate: only M5 regime break is positive,
while M3 reflation/range, M4 shock/stimulus are negative.

### Volatility quartiles (OOS)

| Quartile | Days | Sharpe | Total return % |
| --- | ---: | ---: | ---: |
| V1 | 302 | 2.136 | 28.5 |
| V2 | 327 | 0.217 | 2.4 |
| V3 | 533 | 0.397 | 8.4 |
| V4 | 976 | -0.254 | -13.2 |

3 of 4 OOS volatility quartiles are
positive. The highest-volatility quartile (V4) is negative. T3 has no
pre-registered volatility-regime gate; this table is attribution only.

### Subperiods (OOS)

| Subperiod | Days | Sharpe | Total return % |
| --- | ---: | ---: | ---: |
| 2016-2018 | 515 | -1.090 | -20.7 |
| 2019-2020 | 517 | 1.137 | 29.7 |
| 2021-2023 | 773 | -1.230 | -34.2 |
| 2024-2026 | 644 | 1.644 | 62.3 |

2 of 4 OOS subperiods are negative (2016-2018, 2021-2023). The positive OOS
point estimate is driven by 2019-2020, 2024-2026, while
2016-2018, 2021-2023 lose money. Under Section 11.12 a
result that depends on one subperiod is at best CONDITIONAL, even before
the trade-count rule is applied.

### 2011-2015 bear-market stress (in-sample, reported separately)

The Phase 2A gate is written as an OOS condition, but 2011-2015 lies
inside the in-sample window (2004-2016). It is therefore evaluated as a
separate in-sample stress window and disclosed, not treated as OOS.

| Metric | Value |
| --- | ---: |
| Window | 2011-01-01 to 2015-12-31 |
| Episodes entered in window | 9 |
| Equity-curve net P&L (economic record) | 33,026 |
| Sharpe | 0.566 |
| Max drawdown % | -24.0 |
| Episode-entry net P&L (9 episodes) | 11,590 |
| Profit factor (episode level) | 1.721 |
| Long P&L (episode level) | -9,283 |
| Short P&L (episode level) | 20,873 |
| Worst episode | -10,987 |
| Single outlier explains failure | no |

The equity P&L and the episode sum measure different things and must
not be interchanged. The equity figure is the money made inside the
window; the episode sum attributes each episode to the date it was
entered. They reconcile exactly:

| Reconciliation item | USD |
| --- | ---: |
| Episode-entry sum, 9 episodes entered in window | 11,590 |
| Add back: post-2015 P&L of the short entered 2015-06-01, which the episode sum includes but the window excludes | 3,978 |
| Add: in-window P&L of the long entered 2009-02-02 (before the window) | 17,212 |
| Add: bar-boundary and metric-convention effects | 246 |
| Equity-curve net P&L, 2011-2015 | 33,026 |

The rule is profitable in the 2011-2015 bear market (Sharpe
0.566, equity net USD 33,026),
so the stress gate passes. On the episode-entry view the profit comes
from the short side (USD 20,873), while the long
side loses USD 9,283. That is one
regime, not a general result: the same short side loses money over the
full and OOS samples. The 2009-2012 long episode that straddles the
start of the window is the largest single contributor
(USD 17,212 inside the
window), which is why the equity net is so much larger than the
9-episode sum.

### Cost stress

At 1.5x costs the OOS constant-risk P&L stays positive at
USD 7,409, so the Section 11.12 1.5x sign-flip
criterion passes. At 2.0x it turns negative at USD -1,086,
so the strategy is cost-fragile at the outer stress level. The reason is
swap: at 1.0x, swap is
USD 15,437 of the OOS total cost of
USD 16,432; at 2.0x it is
USD 30,873. Multi-month holds make the
result highly sensitive to the swap assumption.

## F. Statistical validation

| Test | Result | Threshold | Verdict |
| --- | ---: | --- | --- |
| Deflated Sharpe (selected, OOS) | p = 0.8402 | p < 0.10 | FAIL |
| White's Reality Check (6 trials vs buy-and-hold) | p = 0.9900 | p < 0.10 | FAIL |
| Harvey-Liu-Zhu t (selected, OOS) | 0.442 | > 3.0 | FAIL |
| Bootstrap 95% Sharpe CI (selected, OOS) | [-0.602, 0.861] | must exclude 0 | FAIL |
| Random-sign control: actual versus 95th percentile | 97,311 vs 96,582 | actual > p95 | PASS |
| Position episodes, full sample | 35 | >= 100 | FAIL |

All statistical tests use the constant-risk notional daily returns. The
selected trial's OOS Sharpe is 0.147; the Deflated
Sharpe threshold is 0.0291 in daily units against an
observed 0.0089, so the result is far below the
multiple-testing bar. Deflation uses N = 32, the full pre-registered
T1 + T2 + T3 count. The Reality Check's best trial is
**T3-06-LB24-UNSCALED**, which is not the IS-selected trial; that is itself
evidence that the OOS ordering is not stable. The bootstrap interval
includes zero.

**Multiple-testing disclosure.** The IS rule selected the 6-month lookback. The best OOS Sharpe
belongs to the 24-month lookback (T3-05-LB24-SCALED),
which the IS rule does not select, and that configuration has only
9
full-sample episodes. Choosing it after seeing OOS would be post-hoc
selection and is not done. The reported verdict is for the
pre-registered IS-selected trial.

## G. Weaknesses

1. **Low power.** The selected trial has 35
full-sample position episodes and 19 OOS episodes. No
pre-registered T3 configuration reaches 100; the maximum is
41.
Section 11.12 therefore makes the formal verdict INCONCLUSIVE. A 12-month
signal gives roughly one independent observation per year, so 22 years is
about 22 observations before the vol-targeting and rebalancing layers.

2. **Selection decay.** The selected trial's IS Sharpe of
0.613 falls to 0.150 OOS. It
ranks 6 of 6 trials on OOS
Sharpe. The IS-best lookback is not the OOS-best lookback.

3. **Concentration.** One long episode (2023-12 to 2026-06) earns
USD 51,221, or
52.6% of full-sample
net and 210.7% of the
OOS episode sum. Excluding it, OOS episodes total
USD -26,916. Only 3 of
19 OOS episodes are winners.

4. **Long-biased P&L.** Full-sample long P&L is
USD 115,382; short P&L is
USD -18,071. OOS long P&L is
USD 54,650; short P&L is
USD -30,346. The short side only earns its keep in
the 2011-2015 bear window.

5. **Swap dominates costs.** Swap is
93.9%
of OOS total costs. The result is a bet on the current MT5 swap schedule
persisting over multi-month holds; historical swap schedules differ.

6. **Buy-and-hold dominates.** OOS Sharpe is
0.147 against 0.889 for
buy-and-hold; net P&L is USD 15,905 against
USD 248,260; maximum drawdown is
-49.2% against
-26.2%. The overlay adds complexity
without adding risk-adjusted return.

7. **Macro and subperiod dependence.** Only 1 of
3 OOS macro regimes is positive; 2 of
4 OOS subperiods are negative. The positive point estimate is
not broad-based across regimes.

8. **No positive alpha versus beta.** The OLS beta to buy-and-hold is
0.405, annual alpha is -4.14%,
and the alpha t-statistic is -1.411. The rule does not
demonstrate return beyond long gold exposure.

9. **Marginal control.** The random-sign control is cleared by only
USD 729
at the 95th percentile. That is not a comfortable separation from random
sign assignment.

10. **Data and execution limitations.** The D1 spread is a daily average,
not a quote at the execution open. Execution is modelled at the next open
with no intraday path or gap-through logic. The swap schedule is the
current MT5 Demo schedule applied to history. Only one instrument is
available, so the 60/40 and always-long same-vol controls are not
implemented. Overlapping 12- and 24-month signals reduce the effective
number of independent observations below the episode count.

## H. Decision

| Falsification gate | Verdict |
| --- | --- |
| At least 100 position episodes, full sample | FAIL |
| OOS net Sharpe >= 0.40 | FAIL |
| OOS maximum drawdown <= 25% | FAIL |
| Positive in >= 2 of the 3 observable OOS macro regimes | FAIL |
| 2011-2015 bear stress not a failure | PASS |
| Positive OLS alpha versus buy-and-hold (t > 1.96) | FAIL |
| Vol scaling not the whole result | PASS |
| OOS P&L sign stable at 1.5x costs | PASS |
| Deflated Sharpe p < 0.10 | FAIL |

### Statistical and control evidence

| Test | Result | Bar | Verdict |
| --- | --- | --- | --- |
| Deflated Sharpe (selected, OOS) | p = 0.8402 | p < 0.10 | FAIL |
| White's Reality Check (6 trials) | p = 0.9900 | p < 0.10 | FAIL |
| Harvey-Liu-Zhu t (selected, OOS) | 0.442 | > 3.0 | FAIL |
| Bootstrap 95% Sharpe CI (selected, OOS) | [-0.602, 0.861] | must exclude 0 | FAIL |
| Random-sign control (actual vs p95) | 97,311 vs 96,582 | actual > p95 | PASS |

**Formal family verdict: INCONCLUSIVE.**

Section 11.12 is explicit: fewer than 100 trades for T3 is reported as
**inconclusive**, not pass or fail. The selected trial has
35 full-sample position episodes;
no pre-registered T3 configuration reaches 100. INCONCLUSIVE therefore
takes precedence over the economic gates.

INCONCLUSIVE is not a soft pass. If the trade count were sufficient, the
selected trial would **FAIL** 5 of the remaining
gates:

- OOS net Sharpe >= 0.40.
- OOS maximum drawdown <= 25%.
- Positive in >= 2 of the 3 observable OOS macro regimes.
- Positive OLS alpha versus buy-and-hold (t > 1.96).
- Deflated Sharpe p < 0.10.

The point estimates are weak. OOS constant-risk net P&L is
USD 15,905, PF 1.452, and
Sharpe 0.147; buy-and-hold earns
USD 248,260 at Sharpe
0.889. The OOS episode sum is positive only
because of one long episode (2023-12 to 2026-06); excluding it,
OOS episodes total USD -26,916. The short side loses
money, the macro and subperiod lenses are mixed to negative, and the
statistical tests do not reject the null.

**Decision.** Do not promote T3, do not add it to the live candidate set,
and do not re-tune it on this OOS period. The OOS period is spent. A
future T3 test would need a new pre-registered sample (or a diversified
multi-asset universe), a rule that survives 2.0x swap, and enough
independent episodes to clear the 100-trade power threshold. The $25
account scenario was not used as a selection constraint, and no trial was
selected on net profit alone.

---

## Appendix - trial definitions

| Trial | Lookback (D1 bars) | Rebalance | Scaling | Weight |
| --- | ---: | --- | --- | --- |
| T3-01 | 126 | month-end, next open | scaled | min(0.10/vol, 2.0) |
| T3-02 | 126 | month-end, next open | unscaled | 1.0 |
| T3-03 | 252 | month-end, next open | scaled | min(0.10/vol, 2.0) |
| T3-04 | 252 | month-end, next open | unscaled | 1.0 |
| T3-05 | 504 | month-end, next open | scaled | min(0.10/vol, 2.0) |
| T3-06 | 504 | month-end, next open | unscaled | 1.0 |

`run_t3.py` writes `t3_trial_table.csv`, `t3_summary.json` and the
episode log for the selected trial. `report_t3.py` regenerates this
document from those artefacts; no figure in the report is typed by hand.

