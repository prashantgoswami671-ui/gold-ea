# T1 pre-run methodology note

**Status:** written before the confirmatory T1 run.
**Purpose:** disclose every operational decision that the Phase 2A rules do not
fully determine, so the trial results can be read without unstated assumptions.
**Authority:** `Docs/Strategy/Phase-2A-Trend-Following-Research.md` v0.2 remains
authoritative for hypotheses, parameters, split, gates and statistics. This note
does not change any pre-registered parameter or gate.

---

## 1. Data

| Item | Decision |
| --- | --- |
| Price source | Dukascopy XAUUSD BID/ASK candles |
| Range | 2004-01-01 to 2026-11-04 (results truncated at the 2026-06-30 OOS end) |
| D1 | 22:00-to-22:00 UTC trading day, labelled at the 22:00 close |
| H4 | 22:00-aligned UTC (22/02/06/10/14/18), stamped at the open |
| H1 | UTC hour, stamped at the open |
| M15 | UTC quarter hour, stamped at the open |
| Spread | ASK minus BID on the same completed bar |
| M15 spread | The spread of the last completed H1 bar, applied at the M15 open |

Minute ASK candles were not downloaded. Spread at H1 resolution is sufficient
because the M15 entry rule does not condition on spread, and using the last
**completed** H1 bar means no information from inside the M15 bar leaks into the
fill. This smooths intra-hour spread spikes and is disclosed as a limitation.

Cross-check: 5,752 overlapping days against the native MT5 D1 feed give a median
absolute close difference of 0.028%, a 95th percentile of 0.15%, three days above
1%, and a daily return correlation of 0.9955.

## 2. Warm-up

EMA(200, H4) needs a long history to be meaningful. Trading on an immature
regime filter would be a data artefact, so no signal is taken until 1,000
completed H4 bars have elapsed (about 166 trading days). With the archive
starting in January 2004, the first permissible signal is 2004-08-17. This is a
data-integrity rule, not a strategy parameter, and it applies equally to T2 and
T3 wherever a long average is used.

## 3. Rule readings

Two phrases in Section 8.1 admit more than one operational reading. Both were
fixed before the confirmatory run.

### 3.1 Pullback band

Rule: "Price trades within 0.2 x ATR(14, H1) of EMA(20, M15)."

Chosen reading: the bar's **adverse extreme** falls **inside** the band.

- Long: `EMA20 - k*ATR <= low <= EMA20 + k*ATR`
- Short: `EMA20 - k*ATR <= high <= EMA20 + k*ATR`

The first implementation required only `low <= EMA20 + k*ATR` for longs. That is
satisfied by every EMA20 cross and therefore filtered nothing: it generated
about 128 signals per month and produced a rule indistinguishable from "buy every
EMA20 cross in the H4 trend direction". It was rejected as degenerate before any
confirmatory run. Requiring the extreme to be inside the band is what makes the
pullback condition bind, and it matches the plain meaning of "trades within
k x ATR of the EMA".

### 3.2 Trigger

Rule: "M15 close back in the trend direction beyond EMA(20, M15)."

Chosen reading: a close cross.

- Long: `close > EMA20` and the previous close `<= EMA20`
- Short: `close < EMA20` and the previous close `>= EMA20`

This makes each entry a discrete event and prevents immediate re-entry after a
stop-out while price is still beyond the average. The reading is the literal
"back ... beyond" construction.

### 3.3 Other readings

| Rule | Reading |
| --- | --- |
| RSI band | RSI(14, M15) in [40, 60] for both directions |
| Initial stop | `max(stop_mult * ATR(14,H1), 2 * spread)` from the entry fill |
| Trailing stop | `best +/- 2.0 * ATR(14,H1)`, tighter than the initial stop, never loosening |
| Regime exit | Opposite H4 EMA50/EMA200 state, executed at the next open |
| Stop-out | Position flat; a new entry needs a new trigger |
| Rollover | No new entries 21:45-22:15 UTC |
| Gap | If the open is beyond the stop, fill at the open |

## 4. Risk allocation

Section 11.7 fixes the confirmatory T1 grid at 8 trials with risk at 0.5%.
Section 15.2 also lists 0.25 / 0.5 / 1.0 as a risk grid, which would imply 24
trials. This note follows Section 11.7: the 8 confirmatory trials run at 0.5%,
and 0.25% / 1.0% are reported as sensitivity analyses, exactly as Section 8.1's
rules table describes them. No extra confirmatory trial is created.

## 5. Deferred gate

The T1 gate "Net Sharpe is not at least 0.10 higher than T2's net Sharpe" cannot
be evaluated until T2 has run. It is recorded as DEFERRED. Because the mandatory
order is T1 -> T2 -> T3, the deferral caps the best possible T1 verdict at
CONDITIONAL; if any other gate fails, the verdict is FAIL regardless.

## 6. Cost model

The full specification is in the T1 report, Section B. In summary: spread from
the data, 0.5x spread entry slippage, 0.5x signal-exit slippage, 1.0x stop-exit
slippage, USD 0.07/oz round-turn commission, and MT5 Demo swap rates
(-0.126 long, -0.046 short per oz per day, triple Wednesday). All components are
stressed at 1.0x, 1.5x and 2.0x.

Round-trip friction is approximately two spreads. Against a stop of 1.0 or 1.5
x ATR(14,H1), this consumes a fixed fraction of one R per trade before the signal
can add value. The fraction is a property of the data and the pre-registered
stop, not of a trial outcome, and is tabulated by year in the report.

## 7. What was not done

- No parameter outside the Section 11.7 grid was tested.
- No trial was dropped.
- No discretionary rule was added.
- No post-hoc change was made after seeing an OOS result.
- The USD 25 scenario was not used as a selection constraint.
- No strategy was selected on net profit alone.

## 8. Post-run reporting decisions (recorded after the T1 run)

These affect presentation only. No rule, parameter, gate or trade was changed.

1. **Ruin and rebasing.** At 0.5% fixed-fractional risk the account loses
   essentially all of its value in the in-sample window. `period_report`
   rebases each period to USD 100,000 at its start, which makes the IS and OOS
   rows non-additive and makes the compounded OOS dollar P&L uninterpretable.
   The report says so explicitly next to the table.
2. **Constant-risk notional curve.** Every trial is additionally run with risk
   fixed at 0.5% of the initial USD 100,000 (no compounding). This keeps the
   same rule, signals, costs and stop distances but removes the size collapse,
   so Sharpe, drawdown, cost stress, regime attribution and the statistical
   tests are computed on an interpretable curve. It is a sensitivity analysis,
   not a second strategy.
3. **Trade set divergence.** After ruin, position size is zero, so the
   compounded run skips some signals. The constant-risk run therefore has a
   slightly different trade set. Trade-level ratios are reported from the
   constant-risk run for like-for-like comparison across trials.
4. **Statistics.** Deflated Sharpe, White's Reality Check, the Harvey-Liu-Zhu
   t-statistic and the stationary bootstrap use the constant-risk daily
   returns (USD P&L on a fixed USD 100,000 base). A bootstrap CAGR interval is
   not reported because a non-compounding curve has no compound growth rate.
5. **Random-entry control.** The control reuses each trade's direction, stop
   distance and holding period, and shifts all entry times by a random offset,
   with constant risk. It is therefore matched on exposure and cost structure,
   not on entry timing.


---

## 9. Post-run correction: swap sign bug (2026-11-06)

**This is a bug correction, not a parameter change.** No rule, grid point,
gate, split or trade selection was altered.

The first T1 and T2 runs accrued swap as `swap_accrued += rate * ...` with a
negative `rate`, then computed `net = frictionless - ... - swap_accrued`. That
*added* the absolute value of the swap instead of subtracting it, so swap
acted as a subsidy. The equity mark-to-market line and the random-entry
control contained the same sign error. The symptom was visible in T2, where
stressing costs at 1.5x and 2.0x *raised* net P&L and where net P&L exceeded
gross minus the reported costs.

**Correction.** The accrual is now stored as a positive cost
(`swap_accrued -= rate * ...`, with `rate < 0`), and every downstream use
continues to subtract it. The random-entry controls now compute
`swap_cost = -rate * ...` and subtract that. `CostModel.swap()` also returns a
positive cost. As a result:

- `net = gross - spread_slip - commission - swap_cost` holds exactly;
- `total_cost = spread_slip + commission + swap_cost`;
- escalating cost multiples can only reduce net P&L.

All T1 results, statistics and the T1 report were regenerated after the fix.
The T1 verdict is unchanged.

**Second correction (reporting only, same date).** The robustness lenses
labelled "OOS" for macro regimes, subperiods and beta/alpha were computed on
the full-sample return series and then labelled OOS. They are now restricted
to 2017-01-01 through 2026-06-30. The volatility-regime lens was already
effectively OOS because its regime series was reindexed to OOS dates.
Selection, gates and P&L are unaffected; only the attribution tables change.
