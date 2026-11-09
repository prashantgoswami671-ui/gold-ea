# Phase 2B - T2 methodology note (pre-run)

**Family:** T2 - Daily dual-EMA trend system

**Status of this note:** written and frozen **before** the first T2 trial is
run. It records the operational readings that the Phase 2A document leaves
implicit, and the three ambiguities resolved by the project owner on
2026-11-06. No T2 result had been seen when these decisions were taken.

**Source of rules:** `Docs/Strategy/Phase-2A-Trend-Following-Research.md`
(v0.2), Section 8.2, grid in Section 11.7, kill criteria in Section 11.12.

---

## 1. Pre-registered rules and grid

| Component | Specification |
| --- | --- |
| Timeframe | D1, 22:00-to-22:00 UTC, stamped at the close |
| Fast average | EMA(fast, D1) |
| Slow average | EMA(slow, D1) |
| Long signal | EMA(fast) crosses above EMA(slow) on a completed D1 bar |
| Short signal | EMA(fast) crosses below EMA(slow) on a completed D1 bar |
| Entry | Next D1 open after the crossing bar closes |
| Primary exit | Opposite crossover; the position flips at the next open |
| Disaster stop | k x ATR(14, D1) from entry, intrabar |
| Take profit | None |
| Max positions | 1 |
| Risk per trade | r of equity at the disaster stop |

Pre-registered grid (3 x 3 x 2 = 18 confirmatory trials):

| Parameter | Values |
| --- | --- |
| EMA pair (fast, slow) | (20, 100), (50, 200), (100, 400) |
| Disaster stop k | 2.0, 3.0, 4.0 x ATR(14, D1) |
| Risk fraction r | 0.5%, 1.0% |

Trial IDs are `T2-nn-E{fast}x{slow}-ST{k}-R{r}`, with `nn` running 01-18 in
the order produced by the grid. Every combination is run and reported. No
trial is dropped.

---

## 2. Data and warm-up

- Price source: Dukascopy XAUUSD BID/ASK candles, 2004-01-01 to the OOS end.
  The same processed D1 series used by T1 (`XAUUSD_D1.parquet`) is the single
  price source. No separate data feed is used for T2.
- D1 bars are stamped at the 22:00 UTC close. The engine executes a signal at
  the *next row's open*, which is the first tradeable price after the signal
  bar closed.
- **Warm-up:** no signal is allowed until 1,000 completed D1 bars exist. This
  is the same data-integrity rule applied to T1's EMA(200, H4) and is applied
  to the EMA(fast)/EMA(slow) pair as well. The first signal bar is therefore
  2007-11-01 (bar index 1,000, zero-based). The first possible entry is
  2007-11-02. This rule is conservative for the 20/100 pair (which would be
  mature much earlier) and is applied uniformly so the three pairs share the
  same start date.
- The sample is truncated at the OOS end (2026-06-30). Data after that date is
  not used in any T2 result.
- The D1 spread is the mean H1 spread inside the 22:00-to-22:00 session. It is
  a daily average, not a point-in-time quote at the entry or exit instant.
  This is the only spread available at D1 resolution and is documented as a
  limitation.

---

## 3. Execution semantics (frozen readings)

1. **Crossover definition.** Let `state = sign(EMA_fast - EMA_slow)`. A long
   signal is `state[i] > 0` and `state[i-1] <= 0`; a short signal is
   `state[i] < 0` and `state[i-1] >= 0`. Equality is treated as no trend. A
   signal is evaluated only on a completed bar and only at bar index >= 1,000.

2. **Entry.** The pending direction from a signal on bar `i` is executed at the
   open of bar `i+1`. If a position is already open and the new signal is the
   opposite direction, the engine closes the old position and opens the new
   one at the same open (a flip). The old position is charged an exit fill and
   the new position an entry fill.

3. **Disaster stop.** The stop is `entry_fill - direction * k * ATR(14,D1)`,
   floored at `2 x spread`. It is checked intrabar on every bar after entry.
   If the bar's low (long) or high (short) reaches the stop, the stop is
   assumed to have been hit first, even if the bar later closes through the
   stop in the other direction. A gap through the stop fills at the open, not
   at the stop price.

4. **After a disaster stop: flat until the next crossover.** This is the
   project owner's resolution of the main ambiguity. The Phase 2A rules define
   entry only at a crossover, so a stopped-out position is not re-entered in
   the prevailing trend. The engine is flat until a new crossover (in either
   direction) occurs. Consequence: the disaster stop can reduce the number of
   trades relative to a pure flip system, because a stopped-out trend with no
   further crossover produces no replacement trade.

5. **Primary exit / flip.** An opposite crossover always flips the position at
   the next open. There is no "exit to flat" state other than after a stop or
   at the end of the data.

6. **End of data.** Any open position is closed at the last D1 close, with a
   signal-exit fill.

7. **Sizing.** `risk_dollars = r * equity_at_entry` for the pre-registered
   compounded run, and `risk_dollars = r * 100,000` for the constant-risk
   sensitivity run. `size_oz = risk_dollars / stop_distance`. There is no
   leverage cap in the pre-registered rules; the implied notional is reported
   for context. Position size is not rounded to 0.01 lots in the simulator;
   the lot step is a broker constraint that would bind only at very small
   accounts.

8. **Swap.** The current MT5 Demo schedule is applied per D1 bar held:
   USD -0.126 per oz per day for longs, USD -0.046 for shorts, with a triple
   charge on the Wednesday 22:00 rollover. This is a documented testing
   assumption; historical swap schedules differ.

9. **Costs.** Dukascopy spread with 0.5 x spread entry slippage, 0.5 x spread
   signal-exit slippage, 1.0 x spread stop-exit slippage, USD 0.07 per oz
   round-turn commission, and the swap above. All components are stressed at
   1.0x, 1.5x and 2.0x. The abnormal ~USD 58.12 Phase 0 spread is not used.

---

## 4. Selection and reporting basis

- **Selection.** The selected T2 trial is the one with the highest **IS net
  Sharpe** at baseline cost (1.0x). OOS is never used for selection. This is
  the same rule used for T1.
- **Confirmatory sizing.** The pre-registered fixed-fractional account
  (risk = r x current equity) is the confirmatory record. Because a trend
  system holds for months and compounds, its IS and OOS periods are rebased to
  USD 100,000 at the start of each period and are **not additive**.
- **Constant-risk notional curve.** Every trial is also run with risk fixed at
  `r x 100,000` (no compounding). This keeps the rule, signals, stops and
  costs identical but removes the size-collapse problem that dominated the T1
  statistics. If the compounded T2 account is not ruined this curve will be
  close to the compounded one; it is still reported so T2 and T3 use the same
  statistical basis. It is a sensitivity analysis, not a second strategy.
- **Statistics.** Deflated Sharpe, White's Reality Check, the Harvey-Liu-Zhu
  t-statistic and the stationary bootstrap use the **constant-risk daily
  notional returns** (USD P&L on a fixed USD 100,000 base). The number of
  trials used for deflation is 32, the full pre-registered T1+T2+T3 count, so
  the correction is conservative for a T2-only search.
- **Trade-level metrics** (PF, win rate, expectancy, costs) are computed from
  the constant-risk run for like-for-like comparison across trials. The
  compounded and constant-risk trade sets are identical unless the compounded
  account is ruined.

---

## 5. Gate definitions and resolved ambiguities

T2 is rejected if any of the following holds on out-of-sample data:

| Gate | Definition used here |
| --- | --- |
| Net profit factor | OOS net PF < 1.20 at baseline cost |
| Net Sharpe | OOS net Sharpe < 0.50 |
| Maximum drawdown | OOS compounded max drawdown > 25% of the rebased period-start equity |
| Trade count | Fewer than 100 trades in the **full sample**, 2008-2026, at baseline cost |
| Volatility regimes | Not positive in at least 3 of the 4 OOS volatility quartiles |
| Buy-and-hold | Does not beat buy-and-hold gold on OOS Sharpe |
| Deflated Sharpe | OOS DSR p >= 0.10, deflated with N = 32 |
| Cost stress | The sign of the OOS constant-risk P&L flips at 1.5x costs (kill criterion, Section 11.12) |

Three ambiguities were resolved by the project owner before the run:

1. **After a disaster stop.** Flat until the next crossover (Section 3.4).
   The alternative, re-entering the prevailing trend at the next open, was
   rejected because the Phase 2A rules define entry only at a crossover.
2. **100-trade gate basis.** **Full sample, 2008-2026**, at baseline cost.
   The Phase 2A gate list says "on out-of-sample data", but the parenthetical
   says "~4.5 flips per year over 22 years", which is a full-sample statement.
   The full-sample basis is the only one consistent with that parenthetical.
   All other performance gates still use OOS data. With the 1,000-bar warm-up
   the full-sample flip counts are approximately 74 (20/100), 23 (50/200) and
   8 (100/400) before any stop-outs, so the gate is expected to bind for every
   pair.
3. **T3 macro-regime gate (recorded here for later).** The Phase 2A text says
   "2 of the 3" but Section 11.6 defines five macro regimes (M1-M5). The gate
   will be applied as **at least 2 of the 5** regimes. This is recorded now so
   the T3 decision is not made after seeing T3 results.

**Verdict precedence.** Section 11.12 is explicit: "Fewer than 100 trades for
T2/T3 | Report as **inconclusive**, not pass or fail". Therefore, if the
full-sample trade count is below 100, the formal verdict is **INCONCLUSIVE**
even if the point estimates also fail the economic gates. The report will still
show every gate outcome and will state plainly whether the observed point
estimates are positive or negative, so an inconclusive label cannot be mistaken
for a soft pass. If the trade count is at least 100, the usual precedence
applies: any failed gate gives FAIL, a qualification (for example dependence
on one subperiod) gives CONDITIONAL, and all gates passing gives PASS.

---

## 6. What will not be done

- No EMA pair, stop multiple or risk fraction outside the Section 11.7 grid.
- No filter, no take-profit, no trailing stop, no discretionary override.
- No re-entry after a stop without a new crossover.
- No change to the 1,000-bar warm-up or the 2008 start.
- No trial dropped, no trial added, no post-hoc parameter change.
- No selection on net profit, and the USD 25 scenario is not used as a
  constraint.
- The OOS period is examined once. It is not re-used to tune T2.

---

## 7. Trial identifiers

| Trial | EMA pair | Stop | Risk |
| --- | --- | --- | --- |
| T2-01 | 20/100 | 2.0 x ATR | 0.5% |
| T2-02 | 20/100 | 2.0 x ATR | 1.0% |
| T2-03 | 20/100 | 3.0 x ATR | 0.5% |
| T2-04 | 20/100 | 3.0 x ATR | 1.0% |
| T2-05 | 20/100 | 4.0 x ATR | 0.5% |
| T2-06 | 20/100 | 4.0 x ATR | 1.0% |
| T2-07 | 50/200 | 2.0 x ATR | 0.5% |
| T2-08 | 50/200 | 2.0 x ATR | 1.0% |
| T2-09 | 50/200 | 3.0 x ATR | 0.5% |
| T2-10 | 50/200 | 3.0 x ATR | 1.0% |
| T2-11 | 50/200 | 4.0 x ATR | 0.5% |
| T2-12 | 50/200 | 4.0 x ATR | 1.0% |
| T2-13 | 100/400 | 2.0 x ATR | 0.5% |
| T2-14 | 100/400 | 2.0 x ATR | 1.0% |
| T2-15 | 100/400 | 3.0 x ATR | 0.5% |
| T2-16 | 100/400 | 3.0 x ATR | 1.0% |
| T2-17 | 100/400 | 4.0 x ATR | 0.5% |
| T2-18 | 100/400 | 4.0 x ATR | 1.0% |

The executable grid is `itertools.product(pairs, stops, risks)` in that order,
so the IDs above match the runner's enumeration.

---

## 8. Post-run correction: swap sign bug (2026-11-06)

**This is a bug correction, not a parameter change.** No rule, grid point,
gate, split or trade selection was altered.

The first T2 run accrued swap as `swap_accrued += rate * ...` with a negative
`rate`, then computed `net = frictionless - ... - swap_accrued`, which added
the absolute swap instead of subtracting it. The equity mark-to-market line
and the random-entry control had the same sign error. The report showed the
symptom directly: OOS gross 49,798, spread -302, commission -24, swap -7,746,
yet net 57,218, and net P&L rose when costs were stressed to 1.5x and 2.0x.

**Correction.** The accrual is now stored as a positive cost
(`swap_accrued -= rate * ...`, with `rate < 0`), and every downstream use
continues to subtract it. The random-entry control computes
`swap_cost = -rate * ...` and subtracts that. `CostModel.swap()` also returns
a positive cost. As a result `net = gross - spread_slip - commission -
swap_cost` holds exactly and escalating cost multiples can only reduce net
P&L.

All 18 trials, the statistics, the random-entry control and the T2 report were
regenerated after the fix. The formal verdict logic is unchanged, but every
number in the corrected report differs from the pre-fix draft, which is now
superseded.

**Second correction (reporting only, same date).** The robustness lenses
labelled "OOS" for macro regimes, subperiods and beta/alpha were computed on
the full-sample return series and then labelled OOS. They are now restricted
to 2017-01-01 through 2026-06-30. The volatility-regime lens was already
effectively OOS because its regime series was reindexed to OOS dates.
Selection, gates and P&L are unaffected; only the attribution tables change.
