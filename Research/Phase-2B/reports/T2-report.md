# Phase 2B - T2 family report

**Family:** T2 - Daily dual-EMA trend system

**Status:** INCONCLUSIVE

**Phase:** 2B controlled backtesting, family 2 of 3 (T1 -> T2 -> T3)

**Source of rules:** `Docs/Strategy/Phase-2A-Trend-Following-Research.md`
(v0.2), Section 8.2, grid in Section 11.7, gates in Section 8.2 and 11.12.

---

## A. Identity

| Item | Value |
| --- | --- |
| Hypothesis | A slow daily EMA crossover captures multi-month gold trends well enough to pay for costs and beat a passive long position. |
| What it tests | Whether a simple, widely published trend rule has a real edge on a single instrument at retail costs. |
| Grade | E2/E3 hypothesis; the most standard and least parameterised of the four candidates. |
| Timeframe | D1, 22:00-to-22:00 UTC, stamped at the close |
| Trials | 18 pre-registered combinations |
| Data | Dukascopy XAUUSD BID/ASK candles, retrieved 2026-11-05; truncated at the OOS end |
| Symbol | XAUUSD, 2 digits, 100 oz per lot, minimum volume 0.01, volume step 0.01 |
| Test period | 2004-01-01 to 2026-06-30 |
| IS | 2004-01-01 to 2016-12-31 |
| OOS | 2017-01-01 to 2026-06-30 |
| Warm-up | 1,000 completed D1 bars; first signal bar 2007-11-01 22:00:00+00:00 |
| Trial IDs | T2-01 ... T2-18 (see Appendix) |

Pre-registered grid: EMA pairs (20,100), (50,200), (100,400); disaster stop 2.0 / 3.0 / 4.0 x ATR(14,D1); risk 0.5% / 1.0% per trade. That is 3 x 3 x 2 = 18 confirmatory trials.

## B. Capital and execution

| Item | Value |
| --- | --- |
| Initial capital | USD 100,000 |
| Position sizing | Fixed-fractional: risk = r x equity at entry, r = 0.5% or 1.0% per grid; size_oz = risk / (k x ATR(14,D1)) |
| Max positions | 1 |
| Contract | 100 oz per lot; P&L = USD 1 per 0.01 move per 1.0 lot |
| Entry | Next D1 open after the crossing bar closes |
| Primary exit | Opposite crossover; the position flips at the next open |
| Disaster stop | k x ATR(14,D1) from entry, intrabar; k = 2.0 / 3.0 / 4.0 |
| After a stop | Flat until the next crossover (no re-entry without a new cross) |
| Stop priority | Stop assumed hit first; a gap fills at the open |
| Execution model | Vectorised Python bar simulator; no MT5 tester |
| Rollover | Every D1 bar; triple swap on the Wednesday 22:00 rollover |

### Cost model

| Component | Assumption |
| --- | --- |
| Spread | Dukascopy BID/ASK, daily mean of the H1 spreads inside the 22:00-to-22:00 session. Median USD 0.418, p95 USD 0.677 |
| Entry slippage | 0.5 x spread |
| Signal exit slippage | 0.5 x spread |
| Stop exit slippage | 1.0 x spread |
| Commission | USD 0.07 per oz round turn (USD 7.00 per 100 oz lot) |
| Swap long | USD -0.126 per oz per day |
| Swap short | USD -0.046 per oz per day |
| Other costs | None modelled |

All costs are stressed at 1.0x, 1.5x and 2.0x. The abnormal ~USD 58.12 Phase 0 spread is not used anywhere. The D1 spread is a daily average, not a point-in-time quote at the entry or exit instant; this is the only spread available at D1 resolution and is disclosed as a limitation.

## C. Performance

Baseline cost (1.0x), pre-registered fixed-fractional sizing. Each period is rebased to USD 100,000 at its start, so IS and OOS are not additive. Trade-level metrics (PF, win rate, cost ratio) are scale-invariant and remain comparable across periods.

| Trial | Period | Trades | PF | Sharpe | Net P&L | Max DD % | Win % | Hold d | Costs % gross | Exposure % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T2-01-E20x100-ST2.0-R0.5 | IS | 25 | 0.686 | -0.120 | -3,159 | -8.6 | 12.0 | 97 | n/a | 51.2 |
| T2-01-E20x100-ST2.0-R0.5 | OOS | 28 | 4.014 | 0.597 | 30,531 | -8.5 | 28.6 | 112 | 15.6 | 90.1 |
| T2-02-E20x100-ST2.0-R1.0 | IS | 25 | 0.670 | -0.120 | -6,534 | -16.2 | 12.0 | 97 | n/a | 51.2 |
| T2-02-E20x100-ST2.0-R1.0 | OOS | 28 | 4.039 | 0.621 | 61,839 | -15.3 | 28.6 | 112 | 15.3 | 90.1 |
| T2-03-E20x100-ST3.0-R0.5 | IS | 25 | 0.864 | -0.052 | -1,148 | -4.2 | 16.0 | 119 | 200.5 | 62.4 |
| T2-03-E20x100-ST3.0-R0.5 | OOS | 28 | 3.254 | 0.534 | 18,445 | -6.4 | 28.6 | 121 | 17.3 | 97.7 |
| T2-04-E20x100-ST3.0-R1.0 | IS | 25 | 0.850 | -0.052 | -2,514 | -8.3 | 16.0 | 119 | 226.9 | 62.4 |
| T2-04-E20x100-ST3.0-R1.0 | OOS | 28 | 3.252 | 0.551 | 36,718 | -11.9 | 28.6 | 121 | 17.1 | 97.7 |
| T2-05-E20x100-ST4.0-R0.5 | IS | 25 | 0.859 | -0.053 | -900 | -3.3 | 20.0 | 124 | 202.8 | 65.3 |
| T2-05-E20x100-ST4.0-R0.5 | OOS | 28 | 3.127 | 0.519 | 13,560 | -4.8 | 28.6 | 122 | 17.6 | 98.4 |
| T2-06-E20x100-ST4.0-R1.0 | IS | 25 | 0.849 | -0.053 | -1,927 | -6.5 | 20.0 | 124 | 221.7 | 65.3 |
| T2-06-E20x100-ST4.0-R1.0 | OOS | 28 | 3.125 | 0.533 | 26,984 | -9.1 | 28.6 | 122 | 17.5 | 98.4 |
| T2-07-E50x200-ST2.0-R0.5 | IS | 7 | 3.046 | 0.286 | 7,839 | -4.4 | 28.6 | 397 | 30.2 | 57.8 |
| T2-07-E50x200-ST2.0-R0.5 | OOS | 13 | 4.331 | 0.420 | 19,709 | -11.9 | 15.4 | 179 | 16.3 | 68.0 |
| T2-08-E50x200-ST2.0-R1.0 | IS | 7 | 2.939 | 0.296 | 15,737 | -8.3 | 28.6 | 397 | 30.7 | 57.8 |
| T2-08-E50x200-ST2.0-R1.0 | OOS | 13 | 4.227 | 0.449 | 38,652 | -21.4 | 15.4 | 179 | 16.3 | 68.0 |
| T2-09-E50x200-ST3.0-R0.5 | IS | 7 | 2.351 | 0.252 | 4,693 | -3.4 | 28.6 | 399 | 33.6 | 58.0 |
| T2-09-E50x200-ST3.0-R0.5 | OOS | 13 | 3.440 | 0.360 | 11,822 | -9.2 | 15.4 | 212 | 19.6 | 80.5 |
| T2-10-E50x200-ST3.0-R1.0 | IS | 7 | 2.298 | 0.259 | 9,361 | -6.4 | 28.6 | 399 | 34.1 | 58.0 |
| T2-10-E50x200-ST3.0-R1.0 | OOS | 13 | 3.370 | 0.379 | 23,020 | -16.9 | 15.4 | 212 | 19.8 | 80.5 |
| T2-11-E50x200-ST4.0-R0.5 | IS | 7 | 1.919 | 0.222 | 3,154 | -2.8 | 28.6 | 422 | 38.9 | 61.0 |
| T2-11-E50x200-ST4.0-R0.5 | OOS | 13 | 2.927 | 0.321 | 8,035 | -7.5 | 15.4 | 221 | 21.0 | 84.4 |
| T2-12-E50x200-ST4.0-R1.0 | IS | 7 | 1.888 | 0.226 | 6,268 | -5.4 | 28.6 | 422 | 39.4 | 61.0 |
| T2-12-E50x200-ST4.0-R1.0 | OOS | 13 | 2.876 | 0.334 | 15,585 | -14.2 | 15.4 | 221 | 21.3 | 84.4 |
| T2-13-E100x400-ST2.0-R0.5 | IS | 3 | 0.000 | -0.478 | -1,589 | -1.7 | 0.0 | 15 | n/a | 0.9 |
| T2-13-E100x400-ST2.0-R0.5 | OOS | 5 | 0.000 | -0.343 | -2,812 | -3.3 | 0.0 | 54 | n/a | 7.8 |
| T2-14-E100x400-ST2.0-R1.0 | IS | 3 | 0.000 | -0.478 | -3,161 | -3.4 | 0.0 | 15 | n/a | 0.9 |
| T2-14-E100x400-ST2.0-R1.0 | OOS | 5 | 0.000 | -0.341 | -5,560 | -6.5 | 0.0 | 54 | n/a | 7.8 |
| T2-15-E100x400-ST3.0-R0.5 | IS | 3 | 0.000 | -0.294 | -1,439 | -2.0 | 0.0 | 78 | n/a | 4.8 |
| T2-15-E100x400-ST3.0-R0.5 | OOS | 5 | 0.000 | -0.508 | -3,041 | -3.0 | 0.0 | 69 | n/a | 10.1 |
| T2-16-E100x400-ST3.0-R1.0 | IS | 3 | 0.000 | -0.294 | -2,866 | -3.9 | 0.0 | 78 | n/a | 4.8 |
| T2-16-E100x400-ST3.0-R1.0 | OOS | 5 | 0.000 | -0.507 | -6,006 | -6.0 | 0.0 | 69 | n/a | 10.1 |
| T2-17-E100x400-ST4.0-R0.5 | IS | 3 | 0.192 | -0.098 | -607 | -1.6 | 33.3 | 447 | n/a | 28.0 |
| T2-17-E100x400-ST4.0-R0.5 | OOS | 5 | 0.000 | -0.632 | -3,042 | -3.0 | 0.0 | 77 | n/a | 11.5 |
| T2-18-E100x400-ST4.0-R1.0 | IS | 3 | 0.192 | -0.097 | -1,216 | -3.2 | 33.3 | 447 | n/a | 28.0 |
| T2-18-E100x400-ST4.0-R1.0 | OOS | 5 | 0.000 | -0.631 | -6,009 | -6.0 | 0.0 | 77 | n/a | 11.5 |

`n/a` in the cost column means gross P&L was zero or negative, so the cost-to-gross ratio is undefined. A PF of 0.000 means the trial had no winning trades in that period.

### Cost stress, OOS constant-risk notional P&L

The table repeats all 18 trials with risk fixed at the trial's r on the initial USD 100,000 (no compounding) and stresses all cost components at 1.0x, 1.5x and 2.0x. Values are notional USD on a USD 100,000 risk base.

| Trial | Net P&L 1.0x | PF 1.0x | Net P&L 1.5x | PF 1.5x | Net P&L 2.0x | PF 2.0x |
| --- | --- | --- | --- | --- | --- | --- |
| T2-01-E20x100-ST2.0-R0.5 | 29,941 | 3.979 | 27,136 | 3.494 | 24,331 | 3.078 |
| T2-02-E20x100-ST2.0-R1.0 | 59,883 | 3.979 | 54,272 | 3.494 | 48,661 | 3.078 |
| T2-03-E20x100-ST3.0-R0.5 | 18,465 | 3.253 | 16,530 | 2.875 | 14,589 | 2.546 |
| T2-04-E20x100-ST3.0-R1.0 | 36,930 | 3.253 | 33,059 | 2.875 | 29,178 | 2.546 |
| T2-05-E20x100-ST4.0-R0.5 | 13,601 | 3.127 | 12,138 | 2.767 | 10,675 | 2.453 |
| T2-06-E20x100-ST4.0-R1.0 | 27,202 | 3.127 | 24,276 | 2.767 | 21,350 | 2.453 |
| T2-07-E50x200-ST2.0-R0.5 | 20,026 | 4.436 | 18,018 | 3.967 | 16,009 | 3.539 |
| T2-08-E50x200-ST2.0-R1.0 | 40,052 | 4.436 | 36,035 | 3.967 | 32,018 | 3.539 |
| T2-09-E50x200-ST3.0-R0.5 | 12,117 | 3.511 | 10,570 | 3.050 | 9,032 | 2.656 |
| T2-10-E50x200-ST3.0-R1.0 | 24,235 | 3.511 | 21,141 | 3.050 | 18,064 | 2.656 |
| T2-11-E50x200-ST4.0-R0.5 | 8,273 | 2.979 | 7,089 | 2.606 | 5,906 | 2.279 |
| T2-12-E50x200-ST4.0-R1.0 | 16,547 | 2.979 | 14,179 | 2.606 | 11,811 | 2.279 |
| T2-13-E100x400-ST2.0-R0.5 | -2,844 | 0.000 | -3,016 | 0.000 | -3,187 | 0.000 |
| T2-14-E100x400-ST2.0-R1.0 | -5,687 | 0.000 | -6,031 | 0.000 | -6,375 | 0.000 |
| T2-15-E100x400-ST3.0-R0.5 | -3,079 | 0.000 | -3,257 | 0.000 | -3,436 | 0.000 |
| T2-16-E100x400-ST3.0-R1.0 | -6,157 | 0.000 | -6,515 | 0.000 | -6,872 | 0.000 |
| T2-17-E100x400-ST4.0-R0.5 | -3,081 | 0.000 | -3,224 | 0.000 | -3,368 | 0.000 |
| T2-18-E100x400-ST4.0-R1.0 | -6,162 | 0.000 | -6,448 | 0.000 | -6,737 | 0.000 |

### Selected trial

Selected on IS net Sharpe: **T2-08-E50x200-ST2.0-R1.0** (EMA [50, 200], stop 2.0 x ATR, risk 1.0% per trade). This is the only selection rule used; OOS is not used for selection.

| Metric | IS | OOS |
| --- | ---: | ---: |
| Trades | 7 | 13 |
| Profit factor | 2.939 | 4.227 |
| Sharpe | 0.296 | 0.449 |
| Net P&L | 15,737 | 38,652 |
| Max drawdown % | -8.3 | -21.4 |
| Win rate % | 28.6 | 15.4 |
| Average holding days | 397 | 179 |
| Costs as % of gross | 30.7 | 16.3 |
| Expectancy (R) | 1.962 | 3.210 |
| Exposure % | 57.8 | 68.0 |

The selected trial has only 7 IS trades and 13 OOS trades. An IS Sharpe estimated from 7 multi-month trades is extremely noisy; it is the pre-registered selection variable, not a reliable estimate of skill.

### Selected trial, OOS metrics by cost level (constant risk)

| Cost | Trades | Return % | PF | Sharpe | Sortino | DD abs | Win % | Avg win | Avg loss | Payoff | Expect R | Cost % gross |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1.0x | 13 | 40.1 | 4.436 | 0.374 | 0.343 | -30,247 | 15.4 | 26,935 | -1,104 | 24.40 | 3.210 | 16.2 |
| 1.5x | 13 | 36.0 | 3.967 | 0.336 | 0.309 | -30,441 | 15.4 | 25,227 | -1,156 | 21.82 | 2.903 | 24.3 |
| 2.0x | 13 | 32.0 | 3.539 | 0.299 | 0.274 | -30,635 | 15.4 | 23,519 | -1,208 | 19.47 | 2.596 | 32.4 |

Return % is the OOS period P&L on the USD 100,000 notional risk base; CAGR is not reported for a non-compounding curve.

### Selected trial, trade detail (OOS, 1.0x, constant risk)

| Metric | Value |
| --- | ---: |
| Largest win | 40,395 |
| Largest loss | -1,439 |
| Max consecutive wins | 1 |
| Max consecutive losses | 9 |
| Payoff ratio | 24.396 |
| Turnover per year | 1.41 |
| Total costs | 8,072 |
| Gross P&L | 49,798 |
| Long P&L | 48,486 |
| Short P&L | -6,761 |
| MAR | 0.136 |
| Ulcer % | 14.56 |
| Exposure % | 68.0 |

#### Concentration of the selected trial

| Measure | Full sample | OOS |
| --- | ---: | ---: |
| Trades (constant risk) | 20 | 13 |
| Winning trades | 4 | 2 |
| Net P&L | 55,456 | 41,725 |
| Largest single win | 40,395 | 40,395 |
| Largest win as % of net | 72.8 | 96.8 |
| Top-3 wins as % of net | 116.3 | n/a |

The result is a classic trend-following payoff: a low win rate and a small number of very large winners. It also means the OOS P&L is not a broad-based sample of independent evidence; it is dominated by the final multi-year long trade that is still open at the sample end.

#### Gross-to-net decomposition (OOS, 1.0x, constant risk)

| Component | USD |
| --- | ---: |
| Gross P&L (frictionless) | 49,798 |
| Spread and slippage | -302 |
| Commission | -24 |
| Swap | -7,746 |
| Net P&L | 41,725 |
| Total costs | -8,072 |

This table is trade-level: episodes are attributed to the date they were entered. The OOS equity-curve P&L is USD 40,052, which is USD 1,673 lower because one short position entered 2016-11-25 and exited 2017-02-02 straddles the boundary. The equity-curve convention is the economic record; the trade-level sum is the cost-accounting attribution.

### Constant-risk notional results

The same rule re-run with risk fixed at the trial's r on the initial balance (no compounding). It is a notional, risk-normalised P&L curve with no bankruptcy constraint, so drawdown is reported in dollars. T2 does not ruin the compounded account in the way T1 did, so the two curves are close; the constant-risk curve is still the basis for the statistics and for cross-family comparison.

| Period | Trades | PF | Sharpe | Notional P&L | Max DD abs |
| --- | ---: | ---: | ---: | ---: | ---: |
| IS | 7 | 3.161 | 0.274 | 15,603 | -9,518 |
| OOS | 13 | 4.436 | 0.374 | 40,052 | -30,247 |
| FULL | 20 | 3.998 | 0.306 | 55,456 | -30,247 |

## D. Benchmarks

Buy-and-hold gold, one round trip of costs, same windows.

| Window | Net P&L | CAGR % | Sharpe | Max DD % | Vol % |
| --- | --- | --- | --- | --- | --- |
| IS | 176,683 | 7.88 | 0.499 | -44.7 | 18.8 |
| OOS | 248,260 | 13.71 | 0.889 | -26.2 | 15.8 |
| FULL | 863,985 | 10.29 | 0.646 | -44.7 | 17.6 |

**Strategy versus buy-and-hold (metric: OOS Sharpe and net P&L).** The selected trial earns USD 38,652 compounded (USD 40,052 constant-risk) on the USD 100,000 base, with Sharpe 0.449 compounded (0.374 constant-risk). Buy-and-hold gold earns USD 248,260 with Sharpe 0.889. The strategy does not beat buy-and-hold on the pre-registered risk-adjusted comparator, so this gate fails.

Beta versus buy-and-hold (OOS, constant-risk returns): 0.535; annualised alpha: -3.44%. The low beta shows the result is not simply long gold beta, but it is also not enough to beat the passive benchmark on Sharpe.

### Random-entry matched-exposure control

| Statistic | Value |
| --- | --- |
| Trades in control | 19 |
| Maximum shift | 702 bars (995 days) |
| Actual net P&L (control schedule) | 15,061 |
| Actual net P&L (full, incl. terminal trade) | 55,456 |
| Random median | -3,802 |
| Random 5th percentile | -14,700 |
| Random 95th percentile | 18,189 |
| Percentile of actual | 90.7 |
| Runs | 300 |

**Control design.** T2 holds positions for months to years. A naive forward shift of the whole schedule pushes most trades past the end of the sample and silently drops them, which makes the percentile meaningless; the first implementation did exactly that and is not reported. The corrected control excludes the terminal end_of_data trade (its exit is an artefact of the sample end) and draws the shift from the range that keeps every remaining trade inside the sample. The actual non-terminal schedule is at percentile 90.7 of 300 runs, against the 95th percentile of USD 18,189. That is a failure on the control requirement in Section 11.10. The full actual P&L of USD 55,456 includes the terminal trade and is not comparable to the control.

## E. Robustness

### Signal frequency and the 100-trade gate

Crossovers after the 1,000-bar warm-up. The warm-up is a data-integrity rule, but it removes the first 3.8 years, so the trade-count gate is evaluated over 2008-2026 (18.66 years), not the full 22-year price history.

| Pair | Full 2008-2026 | IS | OOS | Per year | First cross | 100-trade gate |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| 20/100 | 53 | 25 | 28 | 2.84 | 2008-05-07 22:00:00+00:00 | FAIL |
| 50/200 | 20 | 7 | 13 | 1.07 | 2008-09-02 22:00:00+00:00 | FAIL |
| 100/400 | 8 | 3 | 5 | 0.43 | 2013-04-15 22:00:00+00:00 | FAIL |

No pre-registered T2 pair reaches 100 trades. The 20/100 pair is the closest at 53; the 50/200 pair has 20 and the 100/400 pair has 8. This is the binding reason for the INCONCLUSIVE verdict, and it is structural: slower EMA pairs produce fewer crossovers, and the 1,000-bar warm-up removes the early sample.

### Pair-level OOS summary

| Pair | Best OOS trial | Full trades | OOS trades | OOS PF | OOS Sharpe | OOS net | OOS DD % | OOS win % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20/100 | T2-02-E20x100-ST2.0-R1.0 | 53 | 28 | 4.039 | 0.621 | 61,839 | -15.3 | 28.6 |
| 50/200 | T2-08-E50x200-ST2.0-R1.0 | 20 | 13 | 4.227 | 0.449 | 38,652 | -21.4 | 15.4 |
| 100/400 | T2-14-E100x400-ST2.0-R1.0 | 8 | 5 | 0.000 | -0.341 | -5,560 | -6.5 | 0.0 |

The 20/100 pair is the strongest out of sample (OOS Sharpe 0.52-0.62 across its six stop/risk combinations, OOS PF 3.12-4.04), but its IS Sharpe is -0.12 to -0.05, so the pre-registered IS selection rule does not pick it. The 50/200 pair is the more consistent pair (IS Sharpe 0.22 to 0.30, OOS Sharpe 0.32 to 0.45) and is the selected pair. The 100/400 pair is negative in every OOS configuration (OOS PF 0.00-0.00, OOS Sharpe -0.63 to -0.34) with only 5 OOS trades. None of these differences is statistically resolvable at this sample size.

### Cost-to-risk ratio by year

Round-trip friction is approximated as two spreads. Against a stop of k x ATR(14,D1), the fraction of one R consumed by costs is small for all three stop multiples. Unlike T1, cost drag is not the reason T2 fails.

| Year | Median close | Median ATR(D1) | Median spread | Cost / 2xATR | Cost / 3xATR | Cost / 4xATR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2004 | 406 | 6.24 | 0.444 | 0.0712 | 0.0475 | 0.0356 |
| 2005 | 434 | 5.32 | 0.445 | 0.0836 | 0.0557 | 0.0418 |
| 2006 | 613 | 12.49 | 0.445 | 0.0356 | 0.0238 | 0.0178 |
| 2007 | 671 | 9.83 | 0.455 | 0.0463 | 0.0309 | 0.0232 |
| 2008 | 882 | 21.02 | 0.455 | 0.0216 | 0.0144 | 0.0108 |
| 2009 | 947 | 17.13 | 0.465 | 0.0271 | 0.0181 | 0.0136 |
| 2010 | 1,213 | 19.05 | 0.522 | 0.0274 | 0.0183 | 0.0137 |
| 2011 | 1,544 | 20.85 | 0.449 | 0.0215 | 0.0144 | 0.0108 |
| 2012 | 1,663 | 22.84 | 0.394 | 0.0173 | 0.0115 | 0.0086 |
| 2013 | 1,369 | 25.57 | 0.373 | 0.0146 | 0.0097 | 0.0073 |
| 2014 | 1,276 | 16.58 | 0.321 | 0.0194 | 0.0129 | 0.0097 |
| 2015 | 1,167 | 15.87 | 0.342 | 0.0215 | 0.0144 | 0.0108 |
| 2016 | 1,256 | 18.47 | 0.365 | 0.0198 | 0.0132 | 0.0099 |
| 2017 | 1,260 | 12.63 | 0.313 | 0.0248 | 0.0165 | 0.0124 |
| 2018 | 1,262 | 12.02 | 0.251 | 0.0209 | 0.0139 | 0.0104 |
| 2019 | 1,409 | 13.27 | 0.315 | 0.0237 | 0.0158 | 0.0119 |
| 2020 | 1,775 | 28.90 | 0.430 | 0.0149 | 0.0099 | 0.0074 |
| 2021 | 1,793 | 23.45 | 0.378 | 0.0161 | 0.0107 | 0.0081 |
| 2022 | 1,804 | 24.84 | 0.382 | 0.0154 | 0.0102 | 0.0077 |
| 2023 | 1,943 | 23.65 | 0.363 | 0.0153 | 0.0102 | 0.0077 |
| 2024 | 2,382 | 33.20 | 0.399 | 0.0120 | 0.0080 | 0.0060 |
| 2025 | 3,345 | 52.31 | 0.631 | 0.0121 | 0.0080 | 0.0060 |
| 2026 | 4,676 | 122.77 | 0.796 | 0.0065 | 0.0043 | 0.0032 |

### Volatility regimes (OOS, trailing 60-day realised vol quartiles)

| Quartile | Days | Sharpe | Total return % |
| --- | --- | --- | --- |
| V1 | 302 | 3.206 | 19.5 |
| V2 | 327 | 1.997 | 19.3 |
| V3 | 533 | 1.064 | 13.8 |
| V4 | 976 | -0.103 | -10.9 |

### Macro regimes (OOS)

| Regime | Days | Sharpe | Total return % |
| --- | --- | --- | --- |
| M3 reflation/range | 773 | 0.252 | 3.3 |
| M4 shock/stimulus | 517 | 0.011 | -1.0 |
| M5 regime break | 1,159 | 0.573 | 37.2 |

The OOS window falls inside M3 (2017-2019), M4 (2020-2021) and M5 (2022-2026); M1 and M2 are in-sample and are not shown. 3 of 3 OOS macro regimes are positive on the constant-risk basis (M3 reflation/range, M4 shock/stimulus, M5 regime break); the day counts are small and each regime contains only a handful of trades.

### Subperiods (full sample, IS + OOS)

| Subperiod | Days | Sharpe | Total return % |
| --- | --- | --- | --- |
| 2004-2007 | 1,042 | n/a | n/a |
| 2008-2011 | 1,044 | 0.520 | 8.9 |
| 2012-2015 | 1,036 | 0.513 | 12.7 |
| 2016-2018 | 773 | -0.907 | -9.8 |
| 2019-2020 | 517 | 0.949 | 23.1 |
| 2021-2023 | 773 | -1.181 | -15.7 |
| 2024-2026 | 644 | 0.837 | 41.0 |

## F. Statistical validation

| Test | Result | Threshold | Verdict |
| --- | ---: | --- | --- |
| Deflated Sharpe (selected, OOS) | p = 0.9670 | p < 0.10 | FAIL |
| White's Reality Check (18 trials vs buy-and-hold) | p = 0.9990 | p < 0.10 | FAIL |
| Harvey-Liu-Zhu t (selected, OOS) | 1.160 | > 3.0 | FAIL |
| Bootstrap 95% Sharpe CI (selected, OOS) | [-0.312, 1.001] | must exclude 0 | FAIL |

All statistical tests use the constant-risk notional daily returns (USD P&L on a fixed USD 100,000 base). The selected trial's constant-risk OOS Sharpe is 0.374; the Deflated Sharpe threshold is 0.061 in daily units against an observed 0.023, so the result is far below the multiple-testing bar. The bootstrap CI includes zero.

Effective trials used for deflation: 32 (the full pre-registered T1+T2+T3 count, conservative for a T2-only search). Best trial by OOS mean return in the Reality Check: T2-02-E20x100-ST2.0-R1.0. Note that the Reality Check's best trial (20/100) is not the IS-selected trial (50/200); that is itself evidence that the OOS ordering is not stable.

**Multiple-testing statement.** 18 of the 32 pre-registered trials have been run in this family report. The Deflated Sharpe uses N = 32. White's Reality Check covers the 18 T2 trials jointly. No trial was dropped and no extra trial was added.

## G. Weaknesses and limitations

1. **Few trades / low power (central).** The selected trial has 20 full-sample trades and 13 OOS trades. The closest pair (20/100) has 53. No T2 pair reaches the pre-registered 100-trade threshold. Multi-month trades are also serially dependent, so the effective sample is smaller than the trade count suggests. This is the reason the verdict is INCONCLUSIVE rather than PASS or FAIL.
2. **Concentration.** One trade (the 2023-2026 long closed at the sample end) is 96.8% of the OOS constant-risk P&L and 72.8% of the full-sample P&L. The result is not a broad sample of independent trend episodes.
3. **Selection on a 7-trade IS Sharpe.** The IS-selected trial is chosen on a Sharpe estimated from 7 multi-month trades. The 20/100 pair looks much better OOS but is not selected; reselecting on OOS would spend the OOS period and is prohibited. This is reported as an observation, not a promotion.
4. **D1 spread is a daily average.** The cost model uses the mean H1 spread inside each D1 session, not the quote at the entry or exit instant. This smooths news spikes and is likely to understate cost in stress.
5. **Swap schedule.** The current MT5 Demo swap schedule is applied to history; historical schedules differ. Multi-month holds make T2 more sensitive to this than T1.
6. **Single venue.** Dukascopy prices only. The MT5 cross-check shows a median daily close difference of 0.028% and a return correlation of 0.9955, but venue-specific spikes remain.
7. **Bar resolution.** Intrabar stop fills are approximated from D1 OHLC with stop-first priority. No partial fills.
8. **After-stop behaviour.** The engine is flat until the next crossover, per the project owner's resolution. A re-entry rule would change the trade count and was not tested.
9. **100/400 is structurally untestable.** With 8 full-sample trades and 5 OOS trades, all but one losing, the pair cannot distinguish a bad rule from an unlucky sample. It is reported, not interpreted.
10. **Warm-up cost.** The 1,000-bar warm-up removes 2004-2007. The 100-trade gate is therefore applied to 18.66 years, not 22. The gate is still applied as pre-registered.
11. **Missing controls.** Phase 2A Section 11.10 also lists a 60/40 portfolio and an always-long, same-vol-target control. They are not implemented here: the approved Phase 2B data set contains only gold, and T2 has no vol target, so both would require inventing a definition. The report relies on buy-and-hold and the random-entry control, as specified in the Phase 2B task requirements.
12. **No re-tune.** The OOS period is spent. No T2 parameter may be changed and no T2 trial may be re-run on OOS.

## H. Decision

| Gate or control (baseline cost unless noted) | Verdict |
| --- | --- |
| At least 100 trades, full sample 2008-2026 | FAIL |
| Net profit factor >= 1.20 (OOS) | PASS |
| Net Sharpe >= 0.50 (OOS) | FAIL |
| Maximum drawdown <= 25% (OOS) | PASS |
| Positive in >= 3 of 4 OOS volatility regimes | PASS |
| Beats buy-and-hold gold on OOS Sharpe | FAIL |
| Deflated Sharpe p < 0.10 | FAIL |
| OOS P&L sign stable at 1.5x costs | PASS |
| OOS P&L sign stable at 2.0x costs | PASS |
| Beats 95th percentile of random-entry control (Section 11.10, full-sample notional) | FAIL |

**Formal family verdict: INCONCLUSIVE.**

Section 11.12 is explicit: fewer than 100 trades for T2 is reported as **inconclusive**, not pass or fail. The selected trial has 20 full-sample trades; the closest pair has 53. No pre-registered T2 configuration reaches 100.

INCONCLUSIVE is not a soft pass. The point estimates are mixed:

- The 20/100 pair is positive at all six stop/risk combinations (OOS PF 3.12-4.04, OOS Sharpe 0.52-0.62) but has 53 trades and a weak, negative IS Sharpe (-0.12 to -0.05).
- The 50/200 pair, which the IS rule selects, is also positive (OOS PF 2.88-4.33, OOS Sharpe 0.32-0.45) but has only 20 trades.
- The 100/400 pair is negative in every OOS configuration (OOS PF 0.00-0.00, OOS Sharpe -0.63 to -0.34) with 5 OOS trades.

Even if the trade count were sufficient, the selected trial fails 3 further gates: Net Sharpe >= 0.50 (OOS), Beats buy-and-hold gold on OOS Sharpe, Deflated Sharpe p < 0.10. It does not beat buy-and-hold on OOS Sharpe (0.449 versus 0.889), its Deflated Sharpe p-value is 0.967, and the bootstrap Sharpe interval [-0.312, 1.001] includes zero. It also fails the Section 11.10 random-entry control: the actual schedule is at percentile 90.7, below the 95th-percentile bar. The family therefore cannot be promoted on the available evidence, and it cannot be declared failed with confidence either.

The 20/100 observation is the only part of T2 that looks economically interesting. It is not a discovery: it was not selected by the pre-registered rule, it is not statistically significant after 32-trial deflation, and it is concentrated in a few large trend episodes. It must not be carried forward as a candidate without a new, separate pre-registered test.

### Pre-run interpretation note

The Phase 2A rules were fixed before the run. Three operational readings were resolved by the project owner on 2026-11-06 and recorded in `T2-methodology-note.md` before any T2 result was seen:

1. **After a disaster stop, flat until the next crossover.** The rules define entry only at a crossover, so a stopped-out position is not re-entered in the prevailing trend.
2. **The 100-trade gate uses the full sample, 2008-2026.** The gate list says 'on out-of-sample data', but the parenthetical '~4.5 flips per year over 22 years' is a full-sample statement. The full sample is the only basis consistent with that parenthetical; all other gates use OOS.
3. **The T3 macro-regime gate will be applied as at least 2 of 5 regimes.** This is recorded now, before T3, so the T3 decision is not made after seeing T3 results.

Two further implementation readings are disclosed: the stop distance uses ATR(14,D1) of the last completed bar (the entry bar's range is not known at its open), and the random-entry control excludes the terminal end_of_data trade and uses a bounded shift so every control trade stays in sample.

---

## Appendix: trial identifiers

| Trial | EMA pair | Stop (x ATR) | Risk |
| --- | --- | --- | --- |
| T2-01-E20x100-ST2.0-R0.5 | 20 / 100 | 2.0 | 0.5% |
| T2-02-E20x100-ST2.0-R1.0 | 20 / 100 | 2.0 | 1.0% |
| T2-03-E20x100-ST3.0-R0.5 | 20 / 100 | 3.0 | 0.5% |
| T2-04-E20x100-ST3.0-R1.0 | 20 / 100 | 3.0 | 1.0% |
| T2-05-E20x100-ST4.0-R0.5 | 20 / 100 | 4.0 | 0.5% |
| T2-06-E20x100-ST4.0-R1.0 | 20 / 100 | 4.0 | 1.0% |
| T2-07-E50x200-ST2.0-R0.5 | 50 / 200 | 2.0 | 0.5% |
| T2-08-E50x200-ST2.0-R1.0 | 50 / 200 | 2.0 | 1.0% |
| T2-09-E50x200-ST3.0-R0.5 | 50 / 200 | 3.0 | 0.5% |
| T2-10-E50x200-ST3.0-R1.0 | 50 / 200 | 3.0 | 1.0% |
| T2-11-E50x200-ST4.0-R0.5 | 50 / 200 | 4.0 | 0.5% |
| T2-12-E50x200-ST4.0-R1.0 | 50 / 200 | 4.0 | 1.0% |
| T2-13-E100x400-ST2.0-R0.5 | 100 / 400 | 2.0 | 0.5% |
| T2-14-E100x400-ST2.0-R1.0 | 100 / 400 | 2.0 | 1.0% |
| T2-15-E100x400-ST3.0-R0.5 | 100 / 400 | 3.0 | 0.5% |
| T2-16-E100x400-ST3.0-R1.0 | 100 / 400 | 3.0 | 1.0% |
| T2-17-E100x400-ST4.0-R0.5 | 100 / 400 | 4.0 | 0.5% |
| T2-18-E100x400-ST4.0-R1.0 | 100 / 400 | 4.0 | 1.0% |

All figures in this report are generated from `results/T2/` by `tools/report_t2.py`. No number is typed by hand.
