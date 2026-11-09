# Phase 2B - T3 methodology note (pre-run)

**Family:** T3 - Time-series momentum (TSMOM) overlay

**Status of this note:** written and frozen **before** the first T3 trial is
run. It records the operational readings that the Phase 2A document leaves
implicit, and the decisions taken by the project owner on 2026-11-06. No T3
result had been seen when these decisions were taken.

**Source of rules:** `Docs/Strategy/Phase-2A-Trend-Following-Research.md`
(v0.2), Section 8.3, grid in Section 11.7, kill criteria in Section 11.12.

---

## 1. Pre-registered rules and grid

| Component | Specification |
| --- | --- |
| Signal | Sign of trailing total return over the lookback window |
| Rebalance | Monthly, on the last D1 bar of the calendar month |
| Execution | Next D1 open after the month-end signal bar |
| Position | Long if signal > 0, short if signal < 0 |
| Volatility estimate | 60-day exponentially weighted realised volatility, annualised |
| Target volatility | 10% annualised |
| Scaled weight | `min(0.10 / realised_vol, 2.0)` of equity notional |
| Unscaled weight | 1.0x equity notional, constant |
| Stop loss | None |
| Max positions | 1 |

Pre-registered grid (3 x 2 = 6 confirmatory trials):

| Parameter | Values |
| --- | --- |
| Lookback | 6, 12, 24 months |
| Scaling | scaled, unscaled |

Trial IDs are `T3-nn-LB{months}-{SCALED|UNSCALED}`, with `nn` running 01-06 in
the order produced by the grid. Every combination is run and reported. No
trial is dropped.

---

## 2. Data, warm-up and signal construction

- Price source: the same processed Dukascopy **D1** series used by T2
  (`XAUUSD_D1.parquet`), 2004-01-01 to the OOS end (2026-06-30). No separate
  feed.
- **Lookback conversion.** The 12-month baseline is defined in Section 8.3 as
  252 trading days. The 6- and 24-month grid points are converted with the same
  convention: **21 trading days per month**, i.e. 126, 252 and 504 D1 bars.
- **Signal.** `r_t = close_t / close_{t-L} - 1`, where `L` is the lookback in
  D1 bars. The sign is `+1` if `r_t > 0`, `-1` if `r_t < 0`, and `0` if exactly
  zero. A zero signal holds the previous direction rather than forcing a flip.
- **Uniform warm-up.** No signal is allowed until 504 completed D1 bars exist,
  the longest lookback in the grid. This makes the three lookbacks share the
  same first signal date and avoids giving the 6-month trial extra history.
  With data starting 2004-01-01, the first eligible month-end is expected in
  early 2006; the exact date is reported from the run.
- The sample is truncated at the OOS end. Data after 2026-06-30 is not used.
- **Month-end detection.** The last available D1 bar with a given calendar
  year-month is the signal bar. If the exchange calendar omits the literal last
  day, the last available bar is used. There is exactly one rebalance signal
  per calendar month.

---

## 3. Execution and accounting (frozen readings)

1. **Volatility.** `ewm(span=60, adjust=False).std()` on D1 log returns,
   annualised by `sqrt(252)`. The estimate used at a month-end signal is the
   value on that completed bar; it is not recomputed at the next open. This is
   a documented reading of "60-day EWMA"; the alternative RiskMetrics
   `lambda = 0.94` is not used.
2. **Target size.** `weight = min(0.10 / vol_ann, 2.0)` for scaled, `1.0` for
   unscaled. `size_oz = weight * base_equity / open_{t+1}`. For the compounded
   run `base_equity` is equity at the prior close; for the constant-risk run it
   is the initial USD 100,000. Sizing uses the execution open, so the target
   notional is fixed at the moment of the trade.
3. **Rebalance, not flip-only.** Every month-end produces a target size. If the
   sign is unchanged, the position is resized to the new target; if the sign
   flips, the old position is closed and the new one opened. This is the
   Section 8.3 rule ("rebalance frequency: monthly").
4. **No stop.** The monthly rebalance and sign flip are the only risk controls.
5. **Daily P&L.** On a rebalance day the overnight gap belongs to the old size
   and the intraday move to the new size:
   `pnl_t = size_old * (open_t - close_{t-1}) + size_new * (close_t - open_t)`.
   On other days `pnl_t = size_t * (close_t - close_{t-1})`.
6. **Turnover costs.** `traded_oz = |size_new - size_old|`. A buy pays
   `1.5 x spread` per oz (half-spread plus 0.5 spread slippage) and a sell pays
   `0.5 x spread` per oz, matching the fill convention used by T1 and T2. The
   round-turn commission of USD 0.07 per oz is split into USD 0.035 per oz per
   side. Over a full buy-then-sell cycle this reproduces the T1/T2 round-trip
   cost exactly.
7. **Swap.** Charged daily on the closing size: USD 0.126 per oz per day for
   longs and USD 0.046 for shorts, with a triple charge on the Wednesday 22:00
   rollover. The stored value is a **positive cost** and is subtracted. This is
   the corrected convention used by T1 and T2 after the swap sign fix.
8. **End of data.** The open position is marked and closed at the last D1
   close, with a sell/buy cost of `0.5 x spread` per oz plus the closing
   commission. No stop or gap fill is possible beyond the last bar.
9. **Cost stress.** Spread, slippage, commission and swap are all multiplied by
   1.0x, 1.5x and 2.0x. The abnormal ~USD 58.12 Phase 0 spread is not used.

---

## 4. Selection and reporting basis

- **Selection.** The selected T3 trial is the one with the highest **IS net
  Sharpe** at baseline cost (1.0x), using the compounded run. OOS is never used
  for selection. This is the same rule used for T1 and T2.
- **Compounded record.** The pre-registered fixed-fractional / vol-targeted
  account is the confirmatory record. IS and OOS are rebased to USD 100,000 at
  the start of each period and are **not additive**.
- **Constant-risk record.** Every trial is also run with the notional based on
  the initial USD 100,000 (no compounding). The rule, signals, weights and
  costs are unchanged. Sharpe, drawdown, regime attribution and all statistics
  use the constant-risk daily returns, matching T1 and T2.
- **Trade definition.** A T3 **trade is one position episode**: from entry (the
  first rebalance after a sign flip) to exit (the rebalance at the next sign
  flip, or end of data). Monthly size adjustments inside an episode are
  rebalances, not new trades. This matches T2's flip counting and measures
  independent economic bets. The alternative, counting every monthly
  rebalance, would mechanically clear the 100-trade gate without adding
  independent information; it is rejected. The project owner selected the
  episode definition on 2026-11-06.
- **Statistics.** Deflated Sharpe, White's Reality Check, the Harvey-Liu-Zhu
  t-statistic and the stationary bootstrap use constant-risk daily returns.
  Deflation uses N = 32, the full pre-registered T1+T2+T3 count.

---

## 5. Gate definitions and resolved ambiguities

T3 is rejected if any of the following holds on out-of-sample data:

| Gate | Definition used here |
| --- | --- |
| Net Sharpe | OOS constant-risk net Sharpe < 0.40 |
| Maximum drawdown | OOS compounded max drawdown > 25% of the rebased period-start equity |
| Macro regimes | Not positive in **at least 2 of the 5** regimes in Section 11.6 |
| Bear-market stress | Fails specifically in 2011-2015 **and** the failure is not explained by a single outlier period |
| Buy-and-hold beta | Returns are statistically indistinguishable from buy-and-hold gold beta |
| Scaled versus unscaled | Scaled is strong but unscaled is not, **and** no coherent reason exists for treating vol scaling as part of the strategy |
| Trade count | Fewer than 100 trades (position episodes) in the full sample |
| Cost stress | The sign of the OOS constant-risk P&L flips at 1.5x costs |
| Deflated Sharpe | OOS DSR p >= 0.10, deflated with N = 32 |

Resolved readings:

1. **Macro gate.** Section 8.3 says "2 of the 3" but Section 11.6 defines five
   regimes (M1-M5). The gate is applied as **at least 2 of the 5**. Because the
   OOS window (2017-2026) only overlaps M3, M4 and M5, M1 and M2 are in-sample
   and cannot contribute. The gate therefore requires at least 2 of the 3
   observable OOS regimes to be positive. This was resolved by the project
   owner on 2026-11-06, before T3 ran.
2. **2011-2015 bear-market gate.** The gate text says "on out-of-sample data"
   but 2011-2015 falls inside the in-sample window (2004-2016). It is therefore
   evaluated as a **separate in-sample stress window**, not as an OOS gate, and
   is reported explicitly. A failure there contributes to CONDITIONAL/FAIL
   only if it is not explained by a single outlier episode. This does not
   affect trial execution, selection or the OOS performance gates.
3. **Trade count.** Position episodes, full sample, as defined in Section 4.
   Section 11.12 says fewer than 100 trades for T3 is reported as
   **INCONCLUSIVE**, not pass or fail.
4. **Scaled versus unscaled.** The gate is evaluable by direct comparison: if
   the scaled trial is materially stronger than the unscaled trial of the same
   lookback, the result is attributed to vol scaling and the report says so.
5. **Buy-and-hold beta.** Evaluated with the OOS beta and alpha versus
   buy-and-hold, plus the Sharpe comparator. A beta near 1 with no positive
   alpha indicates long exposure rather than momentum.

**Verdict precedence.** Section 11.12 makes a sub-100 trade count
**INCONCLUSIVE** even if point estimates also fail economic gates. The report
will show every gate outcome and will state plainly whether the observed point
estimates are positive or negative, so INCONCLUSIVE cannot be mistaken for a
soft pass. If the trade count is at least 100, any failed gate gives FAIL, a
qualification gives CONDITIONAL, and all gates passing gives PASS.

---

## 6. Benchmarks and controls

- **Buy-and-hold gold.** Same window, same costs, one round trip.
- **Random-entry matched-exposure control.** T3's exposure is monthly and
  vol-targeted. The control keeps the actual weight schedule and the actual
  number of long and short months, but randomly permutes which month gets which
  sign. This matches gross exposure, turnover, holding period and costs, and
  tests only whether the momentum sign carries information. 500 permutations,
  fixed seed. This is a direction-randomisation control, not a time-shift,
  because shifting a 12-month overlapping signal by a few months changes almost
  nothing.
- **Long/short attribution.** P&L, costs and swap are split by position
  direction. A rule that only earns when long is reported as long-biased.
- **Unscaled comparison.** Required by Section 8.3 and part of the grid.

The 60/40 portfolio and always-long, same-vol-target controls are not
implemented: the approved Phase 2B data set contains only gold, and inventing a
60/40 definition would add an unapproved assumption. This is disclosed in the
report.

---

## 7. What will not be done

- No lookback outside 6/12/24 months, no vol estimator other than 60-day EWMA,
  no target vol other than 10%, no leverage cap other than 2.0x.
- No stop loss, no discretionary override, no extra filter.
- No change to the 504-bar warm-up or the month-end rule.
- No trial dropped, no trial added, no post-hoc parameter change.
- No selection on net profit, and the USD 25 scenario is not used as a
  constraint.
- The OOS period is examined once. It is not re-used to tune T3.

---

## 8. Trial identifiers

| Trial | Lookback | Scaling |
| --- | --- | --- |
| T3-01 | 6 months (126 D1) | scaled |
| T3-02 | 6 months (126 D1) | unscaled |
| T3-03 | 12 months (252 D1) | scaled |
| T3-04 | 12 months (252 D1) | unscaled |
| T3-05 | 24 months (504 D1) | scaled |
| T3-06 | 24 months (504 D1) | unscaled |

The executable grid is `itertools.product(lookbacks, [scaled, unscaled])` in
that order, so the IDs above match the runner's enumeration.

---

## 9. Pre-run implementation correction (2026-11-06)

This changes no frozen rule, parameter, split, gate or trial. It was found by a
single-trial smoke test **before** the full six-trial run.

The first version of `run_t3.py` updated equity on a sign-flip day with only
the new position's intraday P&L. The overnight gap earned by the old position
was added to the closing episode's gross but was omitted from the equity path,
so the sum of episode P&L and the equity curve differed (USD 225 on the 12-month
scaled trial). The fix adds the old position's overnight gap to the day's
equity P&L while still assigning only the intraday move to the new episode.
After the fix, on the 12-month scaled trial at 1.0x, 1.5x and 2.0x costs:

- `sum(episode net) == final equity - initial` exactly;
- `gross - spread_slip - commission - swap == net` exactly at episode level;
- swap is a strictly positive cost in every episode;
- net P&L falls monotonically as costs rise.

The frozen rules, trial grid, selection rule and gates are unchanged.

## 10. Reporting clarification on the 2.0x cost multiple

Section 11.12 of the Phase 2A document makes a sign flip at **1.5x** costs the
kill criterion. The 2.0x multiple is still computed, reported and stressed in
the T3 report, but it is treated as an additional stress observation rather
than a formal falsification gate. This avoids silently adding a stricter gate
after the run.
