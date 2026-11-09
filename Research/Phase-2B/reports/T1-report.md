# Phase 2B - T1 family report

**Family:** T1 - Multi-timeframe EMA pullback continuation

**Status:** FAIL

**Phase:** 2B controlled backtesting, family 1 of 3 (T1 -> T2 -> T3)

**Source of rules:** `Docs/Strategy/Phase-2A-Trend-Following-Research.md`
(v0.2), Section 8.1, grid in Section 11.7, gates in Section 8.1 and 11.8.

---

## A. Identity

| Item | Value |
| --- | --- |
| Hypothesis | Within an established H4 trend, M15 pullbacks to EMA20 resolve in the trend direction often enough to pay for costs. |
| What it tests | Whether intraday timing adds anything to a trend bias on gold. |
| Grades | E4 hypothesis; fastest and most cost-sensitive of the four candidates. |
| Timeframes | H4 regime, M15 entry, H1 ATR |
| Trials | 8 pre-registered combinations |
| Data | Dukascopy XAUUSD BID/ASK candles, retrieved 2026-11-05; 2004-01-01 to 2026-11-04, truncated at the OOS end |
| Symbol | XAUUSD, 2 digits, 100 oz per lot, minimum volume 0.01, volume step 0.01 |
| Test period | 2004-01-01 to 2026-06-30 |
| IS | 2004-01-01 to 2016-12-31 |
| OOS | 2017-01-01 to 2026-06-30 |
| Trial IDs | T1-01 ... T1-08 (see Appendix) |

Pre-registered grid: pullback 0.2 / 0.5 x ATR(14,H1); initial stop 1.0 / 1.5 x ATR(14,H1) floored at 2 x spread; trailing stop 2.0 x ATR(14,H1); RSI(14,M15) 40-60 filter off / on; risk 0.5% per trade.

## B. Capital and execution

| Item | Value |
| --- | --- |
| Initial capital | USD 100,000 |
| Position sizing | Fixed-fractional: risk = 0.5% x current equity; size_oz = risk / stop_distance; lots = size_oz / 100 (0.01 step), confirmatory |
| Max positions | 1 |
| Contract | 100 oz per lot; P&L = USD 1 per 0.01 move per 1.0 lot |
| Entry | Next M15 open after the signal bar closes |
| Exit | Trailing stop, or H4 regime flip, or end of data |
| Stop priority | Stop assumed hit first; gap fills at the open |
| Execution model | Vectorised Python bar simulator; no MT5 tester |
| Rollover | No new entries 21:45-22:15 UTC |

### Cost model

| Component | Assumption |
| --- | --- |
| Spread | Dukascopy BID/ASK on the completed H1 bar; charged on entry and exit. H1 median USD 0.386, p95 USD 0.712 |
| Entry slippage | 0.5 x spread |
| Signal exit slippage | 0.5 x spread |
| Stop exit slippage | 1.0 x spread |
| Commission | USD 0.07 per oz round turn (USD 7.00 per 100 oz lot) |
| Swap long | USD -0.126 per oz per day |
| Swap short | USD -0.046 per oz per day |
| Triple swap | Wednesday |
| Other costs | None modelled |

All costs are stressed at 1.0x, 1.5x and 2.0x. The abnormal ~USD 58.12 Phase 0 spread is not used anywhere.

## C. Performance

Baseline cost (1.0x), pre-registered fixed-fractional sizing at 0.5% risk per trade. Each period is rebased to USD 100,000 at the start of the period, so the IS, OOS and FULL rows are not additive: the OOS account has already been reduced to a small fraction of its starting balance by in-sample losses. Trade-level metrics (PF, win rate, cost ratio) are scale-invariant and remain comparable across periods.

| Trial | Period | Trades | Final eq (rebased) | Net P&L | PF | Sharpe | Max DD % | Win % | Hold d | Costs % gross | Exposure % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T1-01-PB0.2-ST1.0-RSI0 | IS | 4,021 | 79 | -99,921 | 0.252 | -3.171 | -99.9 | 23.2 | 0.44 | n/a | 37.2 |
| T1-01-PB0.2-ST1.0-RSI0 | OOS | 3,161 | 2,319 | -97,681 | 0.547 | -2.221 | -98.1 | 26.1 | 0.46 | n/a | 42.1 |
| T1-02-PB0.2-ST1.0-RSI1 | IS | 3,942 | 94 | -99,906 | 0.249 | -3.110 | -99.9 | 23.1 | 0.44 | n/a | 36.8 |
| T1-02-PB0.2-ST1.0-RSI1 | OOS | 3,121 | 2,511 | -97,489 | 0.555 | -2.187 | -97.9 | 26.2 | 0.46 | n/a | 41.9 |
| T1-03-PB0.2-ST1.5-RSI0 | IS | 3,587 | 1,736 | -98,264 | 0.478 | -2.605 | -98.3 | 27.7 | 0.56 | 8,097.8 | 42.5 |
| T1-03-PB0.2-ST1.5-RSI0 | OOS | 2,856 | 11,553 | -88,447 | 0.654 | -1.808 | -90.5 | 30.5 | 0.56 | n/a | 46.5 |
| T1-04-PB0.2-ST1.5-RSI1 | IS | 3,530 | 1,973 | -98,027 | 0.477 | -2.537 | -98.0 | 27.8 | 0.57 | 16,918.5 | 42.1 |
| T1-04-PB0.2-ST1.5-RSI1 | OOS | 2,823 | 11,981 | -88,019 | 0.656 | -1.789 | -90.2 | 30.6 | 0.57 | n/a | 46.3 |
| T1-05-PB0.5-ST1.0-RSI0 | IS | 6,641 | 0 | -100,000 | 0.133 | -4.226 | -100.0 | 22.2 | 0.42 | n/a | 58.9 |
| T1-05-PB0.5-ST1.0-RSI0 | OOS | 4,833 | 635 | -99,365 | 0.573 | -2.320 | -99.5 | 26.7 | 0.44 | n/a | 61.5 |
| T1-06-PB0.5-ST1.0-RSI1 | IS | 6,528 | 0 | -100,000 | 0.133 | -4.235 | -100.0 | 22.0 | 0.42 | n/a | 58.1 |
| T1-06-PB0.5-ST1.0-RSI1 | OOS | 4,764 | 771 | -99,229 | 0.581 | -2.248 | -99.4 | 26.9 | 0.44 | n/a | 60.9 |
| T1-07-PB0.5-ST1.5-RSI0 | IS | 5,393 | 176 | -99,824 | 0.366 | -3.223 | -99.8 | 27.4 | 0.56 | n/a | 63.7 |
| T1-07-PB0.5-ST1.5-RSI0 | OOS | 4,107 | 7,436 | -92,564 | 0.695 | -1.755 | -94.6 | 31.6 | 0.55 | 860.5 | 65.5 |
| T1-08-PB0.5-ST1.5-RSI1 | IS | 5,307 | 201 | -99,799 | 0.366 | -3.194 | -99.8 | 27.4 | 0.56 | n/a | 63.0 |
| T1-08-PB0.5-ST1.5-RSI1 | OOS | 4,060 | 8,063 | -91,937 | 0.701 | -1.713 | -94.0 | 31.6 | 0.55 | 772.8 | 65.0 |

`n/a` in the cost column means gross P&L was zero or negative, so the cost-to-gross ratio is undefined; the corresponding gate is recorded as failed.

### Cost stress, OOS constant-risk notional P&L

The compounded OOS account is near zero after in-sample losses, so its dollar P&L is not interpretable. The table below repeats the eight trials with risk fixed at 0.5% of the initial USD 100,000 (no compounding) and stresses all cost components at 1.0x, 1.5x and 2.0x. Values are notional USD on a USD 100,000 risk base. Once the compounded account is ruined, position size collapses to zero and some signals are skipped, so the compounded and constant-risk trade sets diverge; the constant-risk table is the clean like-for-like comparison across trials.

| Trial | Net P&L 1.0x | PF 1.0x | Net P&L 1.5x | PF 1.5x | Net P&L 2.0x | PF 2.0x |
| --- | --- | --- | --- | --- | --- | --- |
| T1-01-PB0.2-ST1.0-RSI0 | -364,909 | 0.687 | -591,706 | 0.556 | -836,696 | 0.448 |
| T1-02-PB0.2-ST1.0-RSI1 | -357,093 | 0.689 | -578,691 | 0.559 | -821,374 | 0.450 |
| T1-03-PB0.2-ST1.5-RSI0 | -209,903 | 0.733 | -339,177 | 0.614 | -468,993 | 0.519 |
| T1-04-PB0.2-ST1.5-RSI1 | -206,352 | 0.734 | -334,566 | 0.614 | -461,760 | 0.520 |
| T1-05-PB0.5-ST1.0-RSI0 | -487,868 | 0.724 | -832,024 | 0.591 | -1,209,550 | 0.482 |
| T1-06-PB0.5-ST1.0-RSI1 | -468,701 | 0.731 | -805,010 | 0.597 | -1,176,641 | 0.487 |
| T1-07-PB0.5-ST1.5-RSI0 | -251,335 | 0.774 | -426,233 | 0.655 | -617,253 | 0.552 |
| T1-08-PB0.5-ST1.5-RSI1 | -243,320 | 0.778 | -415,886 | 0.659 | -603,841 | 0.556 |

### Selected trial

Selected on IS net Sharpe: **T1-04-PB0.2-ST1.5-RSI1** (this is the only selection rule used; OOS is not used for selection).

| Metric | IS | OOS |
| --- | ---: | ---: |
| Trades | 3,530 | 2,823 |
| Profit factor | 0.477 | 0.656 |
| Sharpe | -2.537 | -1.789 |
| Net P&L | -98,027 | -88,019 |
| Max drawdown % | -98.0 | -90.2 |
| Win rate % | 27.8 | 30.6 |
| Average holding days | 0.57 | 0.57 |
| Costs as % of gross | 16,918.5 | n/a |
| Expectancy (R) | -0.219 | -0.146 |
| Exposure % | 42.1 | 46.3 |

Compounded (pre-registered) sizing; each period is rebased to USD 100,000, as explained in Section C. The OOS constant-risk notional P&L for the same rule is USD -206,352, shown below.

### Selected trial, OOS metrics by cost level (constant risk)

| Cost | Trades | Return % | PF | Sharpe | Sortino | DD abs | DD % | Win % | Avg win | Avg loss | Avg win R | Avg loss R | Expect R | Cost % gross |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1.0x | 2,823 | -206.4 | 0.734 | -1.787 | -3.783 | -226,613 | -226.6 | 30.6 | 658 | -395 | 1.32 | -0.79 | -0.146 | 729.2 |
| 1.5x | 2,848 | -334.6 | 0.614 | -2.838 | -5.626 | -350,114 | -350.1 | 28.2 | 662 | -424 | 1.32 | -0.85 | -0.235 | 1,224.8 |
| 2.0x | 2,877 | -461.8 | 0.520 | -3.821 | -7.057 | -472,482 | -472.5 | 26.1 | 665 | -453 | 1.33 | -0.91 | -0.321 | 1,463.5 |

Return % is the OOS period P&L on the USD 100,000 notional risk base; CAGR is not reported for a non-compounding curve.

### Selected trial, trade detail (OOS, 1.0x, constant risk)

| Metric | Value |
| --- | ---: |
| Largest win | 4,959 |
| Largest loss | -1,574 |
| Max consecutive wins | 7 |
| Max consecutive losses | 22 |
| Payoff ratio | 1.663 |
| Turnover per year | 297.6 |
| Total costs | 239,133 |
| Gross P&L | 32,794 |
| Long P&L | -82,695 |
| Short P&L | -123,645 |
| MAR | -0.083 |
| Ulcer % | 146.89 |
| Exposure % | 46.3 |

#### Gross-to-net decomposition (OOS, 1.0x, constant risk)

| Component | USD |
| --- | ---: |
| Gross P&L (frictionless) | 32,794 |
| Spread and slippage | -215,215 |
| Commission | -17,113 |
| Swap | -6,805 |
| Net P&L | -206,340 |
| Total costs | -239,133 |

Trade-level sums; the OOS equity-curve P&L is USD -206,352, which is USD 13 lower than the episode sum because a position that entered before the OOS boundary exits inside it.

### Constant-risk notional results

This is the interpretable economic record. The compounded account is effectively ruined well before the OOS window, so its Sharpe and drawdown are dominated by the size collapse. The same rule is re-run with risk fixed at 0.5% of the initial balance (no compounding). It is a notional, risk-normalised P&L curve with no bankruptcy constraint, so drawdown is reported in dollars.

| Period | Trades | PF | Sharpe | Notional P&L | Max DD abs |
| --- | ---: | ---: | ---: | ---: | ---: |
| IS | 3,530 | 0.630 | -2.534 | -385,225 | -386,204 |
| OOS | 2,823 | 0.734 | -1.787 | -206,352 | -226,613 |
| FULL | 6,353 | 0.674 | -2.213 | -592,230 | -612,490 |

## D. Benchmarks

Buy-and-hold gold, one round trip of costs, same windows.

| Window | Net P&L | CAGR % | Sharpe | Max DD % | Vol % |
| --- | --- | --- | --- | --- | --- |
| IS | 176,683 | 7.88 | 0.499 | -44.7 | 18.8 |
| OOS | 248,260 | 13.71 | 0.889 | -26.2 | 15.8 |
| FULL | 863,985 | 10.29 | 0.646 | -44.7 | 17.6 |

Selected trial, OOS constant-risk: notional P&L -206,352, Sharpe -1.787, max drawdown -226,613 USD. Buy-and-hold gold OOS on the same USD 100,000 base: net P&L 248,260, Sharpe 0.889, max DD -26.2%.

Beta versus buy-and-hold (OOS): 0.130; annualised alpha: -21.72%.

Random-entry matched-exposure control (same directions, same holding periods, entry time shifted to a random point in the sample; 300 runs, constant risk over the full sample):

| Statistic | Value |
| --- | --- |
| Actual net P&L (constant risk) | -592,074 |
| Random median (constant risk) | -322,061 |
| Random 5th percentile | -631,278 |
| Random 95th percentile | -39,916 |
| Percentile of actual | 11.3 |
| Runs | 300 |

**Strategy versus buy-and-hold (metric: OOS net P&L and Sharpe).** The selected trial loses USD 206,352 on a USD 100,000 risk base while buy-and-hold gold earns USD 248,260; the shortfall is USD 454,612. Sharpe is -1.787 versus 0.889.

**Strategy versus random-entry control (metric: full-sample notional net P&L).** The actual rule returns USD -592,074, below the random median of USD -322,061 and at percentile 11.3 of 300 matched random schedules. Entry timing is therefore worse than random, not merely unprofitable after costs.

## E. Robustness

### Cost-to-risk ratio by year

Round-trip friction is approximately two spreads (cross the spread once, plus 1.0 spread of slippage). Against a stop of 1.0 or 1.5 x ATR(14,H1), that fixes the fraction of one R consumed by costs before the signal can add value. This is a property of the data and the pre-registered stop, not of any trial outcome.

| Year | Median close | Median ATR(H1) | Median spread | Cost / 1.0xATR | Cost / 1.5xATR |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2004 | 406 | 1.55 | 0.410 | 0.531 | 0.354 |
| 2005 | 434 | 1.51 | 0.410 | 0.542 | 0.361 |
| 2006 | 611 | 2.59 | 0.412 | 0.318 | 0.212 |
| 2007 | 670 | 2.14 | 0.460 | 0.429 | 0.286 |
| 2008 | 883 | 3.84 | 0.460 | 0.240 | 0.160 |
| 2009 | 947 | 3.29 | 0.504 | 0.306 | 0.204 |
| 2010 | 1,213 | 3.33 | 0.506 | 0.304 | 0.203 |
| 2011 | 1,543 | 4.39 | 0.426 | 0.194 | 0.129 |
| 2012 | 1,663 | 3.86 | 0.364 | 0.188 | 0.126 |
| 2013 | 1,373 | 4.07 | 0.358 | 0.176 | 0.117 |
| 2014 | 1,275 | 2.83 | 0.298 | 0.210 | 0.140 |
| 2015 | 1,168 | 2.74 | 0.315 | 0.230 | 0.153 |
| 2016 | 1,257 | 3.25 | 0.312 | 0.192 | 0.128 |
| 2017 | 1,261 | 2.31 | 0.245 | 0.212 | 0.142 |
| 2018 | 1,263 | 2.24 | 0.240 | 0.214 | 0.143 |
| 2019 | 1,406 | 2.46 | 0.294 | 0.239 | 0.159 |
| 2020 | 1,774 | 5.39 | 0.407 | 0.151 | 0.101 |
| 2021 | 1,794 | 4.16 | 0.357 | 0.171 | 0.114 |
| 2022 | 1,804 | 4.55 | 0.372 | 0.163 | 0.109 |
| 2023 | 1,945 | 4.13 | 0.330 | 0.160 | 0.106 |
| 2024 | 2,381 | 5.89 | 0.377 | 0.128 | 0.085 |
| 2025 | 3,345 | 10.18 | 0.587 | 0.115 | 0.077 |
| 2026 | 4,465 | 18.98 | 0.690 | 0.073 | 0.048 |

### Volatility regimes (OOS, trailing 60-day realised vol quartiles)

| Quartile | Days | Sharpe | Total return % |
| --- | --- | --- | --- |
| V1 | 302 | -1.777 | -21.8 |
| V2 | 327 | -1.344 | -17.5 |
| V3 | 533 | -1.386 | -27.5 |
| V4 | 976 | -1.489 | -48.7 |

### Macro regimes (OOS)

| Regime | Days | Sharpe | Total return % |
| --- | --- | --- | --- |
| M3 reflation/range | 874 | -2.895 | -68.7 |
| M4 shock/stimulus | 585 | -1.665 | -33.2 |
| M5 regime break | 1,312 | -1.031 | -43.2 |

### Subperiods (full sample, IS + OOS)

| Subperiod | Days | Sharpe | Total return % |
| --- | --- | --- | --- |
| 2004-2007 | 1,054 | -3.799 | -76.7 |
| 2008-2011 | 1,248 | -2.246 | -67.0 |
| 2012-2015 | 1,183 | -1.765 | -61.7 |
| 2016-2018 | 874 | -2.783 | -67.5 |
| 2019-2020 | 585 | -2.467 | -45.5 |
| 2021-2023 | 875 | -1.551 | -42.3 |
| 2024-2026 | 729 | -0.812 | -22.5 |

## F. Statistical validation

| Test | Result | Threshold | Verdict |
| --- | ---: | --- | --- |
| Deflated Sharpe (selected, OOS) | p = 1.0000 | p < 0.10 | FAIL |
| White's Reality Check (8 trials vs buy-and-hold) | p = 1.0000 | p < 0.10 | FAIL |
| Harvey-Liu-Zhu t (selected, OOS) | -5.944 | > 3.0 | FAIL |
| Bootstrap 95% Sharpe CI (selected, OOS) | [-2.486, -1.139] | must exclude 0 | FAIL |

All statistical tests use the constant-risk notional daily returns (USD P&L on a fixed USD 100,000 base), not the ruined compounded equity curve. A 95% bootstrap CI on CAGR is not reported because the non-compounding curve has no compound growth rate; the Sharpe CI is the relevant interval for a rejected strategy.

Effective trials used for deflation: 32 (conservative, as pre-registered). Best trial by OOS mean return in the Reality Check: T1-04-PB0.2-ST1.5-RSI1.

**Multiple-testing statement.** 8 of the 32 pre-registered trials have been run in this family report. The Deflated Sharpe is computed with N = 32, the full pre-registered count across T1-T3, so the deflation is conservative for the T1-only search. White's Reality Check covers the 8 T1 trials jointly. No trial was dropped and no extra trial was added.

## G. Weaknesses and limitations

1. **Spread source.** M15 spread is taken from the completed H1 bar, not from tick data. This smooths intra-hour spread spikes, including news spikes, and is likely to understate cost during stress.
2. **Bar resolution.** Intrabar stop and trail fills are approximated from M15 OHLC. No partial fills; stop-first priority.
3. **Swap.** Swap is modelled from the current MT5 Demo schedule applied to history. Historical swap schedules differ.
4. **Slippage.** Slippage is a fixed fraction of spread. Real slippage is state-dependent and worse in fast markets.
5. **Single venue.** Dukascopy prices only. Cross-checks against the MT5 feed show a median daily close difference of 0.028% and a return correlation of 0.9955, but venue-specific spikes remain.
6. **Selection.** The IS-selected trial is chosen on net Sharpe; with 8 trials the selection itself consumes degrees of freedom, which the Deflated Sharpe attempts to correct.
7. **Compounding ruin.** At 0.5% risk the account is effectively wiped out in the IS window under baseline costs, so the compounded OOS equity curve is dominated by the size collapse. Trade-level metrics (PF, cost ratio) are scale-invariant, and the constant-risk notional curve is the interpretable economic record; both are reported.
8. **Gate deferral.** The gate 'Sharpe at least 0.10 above T2' cannot be evaluated until T2 runs.

## H. Decision

| Gate (OOS, baseline cost) | Verdict |
| --- | --- |
| At least 300 OOS trades | PASS |
| Net profit factor >= 1.20 | FAIL |
| Costs <= 25% of gross profit | FAIL |
| Positive in >= 3 of 4 volatility regimes | FAIL |
| Sharpe >= T2 Sharpe + 0.10 | DEFERRED |

**Family verdict: FAIL.**

At least one non-deferred falsification gate fails on out-of-sample data, so T1 is rejected as a candidate irrespective of the deferred T2 comparison.

### Interpretation

1. **The gross edge is approximately zero.** The constant-risk OOS gross P&L is USD 32,794 over 2,823 trades, or USD 11.62 per trade before friction. That is too small to survive execution: total costs are USD 239,133, or USD 84.71 per trade (about 0.169R at the USD 500 initial risk unit).
2. **Cost drag is structural, not incidental.** Round-trip friction is roughly two spreads. Against the pre-registered 1.0xATR(H1) stop it consumed 0.53R per trade in 2004 and 0.07R in 2026, because gold volatility rose far faster than the spread. The strategy needs a gross edge of at least that size simply to break even; it has none.
3. **Entry timing is worse than random.** The actual rule's full-sample notional P&L of USD -592,074 sits at percentile 11.3 of 300 matched-exposure random-entry schedules (median USD -322,061). The pullback filter is not adding information; it is selecting slightly adverse entry points.
4. **No configuration rescues it.** At baseline cost the best OOS profit factor across the eight pre-registered trials is 0.70, against a gate of 1.20, and every trial is negative at 1.0x, 1.5x and 2.0x costs. The failure is not confined to a subperiod or a volatility regime: all seven subperiods and all four volatility quartiles are negative.

T1 is therefore rejected. No T1 parameter set may be carried forward as a candidate, and the deferred T2-relative Sharpe gate cannot change this verdict.

### Pre-run interpretation note

The Phase 2A rules are fixed, but two operational readings had to be chosen and are disclosed here:

1. **Pullback band.** 'Price trades within k x ATR of EMA20' is read as the bar's adverse extreme falling inside the band `EMA20 +/- k*ATR(14,H1)`. The first implementation only required the extreme to be beyond the band on the near side, which is satisfied by every EMA20 cross and therefore filtered nothing; it was discarded before any confirmatory run.
2. **Trigger.** 'Close back in the trend direction beyond EMA20' is read as a close cross: `close > EMA20` with the previous close `<= EMA20` for longs, mirrored for shorts.

These readings are not tuned parameters and were fixed before the full dataset was built. The pre-registered parameters (0.2/0.5 pullback, 1.0/1.5 stop, RSI off/on, 2.0 trail, 0.5% risk) are unchanged.

---

## Appendix: trial identifiers

| Trial | Pullback | Stop | RSI |
| --- | --- | --- | --- |
| T1-01-PB0.2-ST1.0-RSI0 | PB0.2 | ST1.0 | RSI0 |
| T1-02-PB0.2-ST1.0-RSI1 | PB0.2 | ST1.0 | RSI1 |
| T1-03-PB0.2-ST1.5-RSI0 | PB0.2 | ST1.5 | RSI0 |
| T1-04-PB0.2-ST1.5-RSI1 | PB0.2 | ST1.5 | RSI1 |
| T1-05-PB0.5-ST1.0-RSI0 | PB0.5 | ST1.0 | RSI0 |
| T1-06-PB0.5-ST1.0-RSI1 | PB0.5 | ST1.0 | RSI1 |
| T1-07-PB0.5-ST1.5-RSI0 | PB0.5 | ST1.5 | RSI0 |
| T1-08-PB0.5-ST1.5-RSI1 | PB0.5 | ST1.5 | RSI1 |

All figures in this report are generated from `results/T1/` by `tools/report_t1.py`. No number is typed by hand.
