# Phase 2B - Data and Methodology Readiness Report

Status: **BLOCKED - project-owner approval required before any trial**
Prepared: 2026-11-05
Author: Phase 2B research tooling
Scope: data availability, provenance, quality, timezone, cost model, split feasibility

---

## 1. Summary

The daily and 4-hour series are usable. The intraday series required by T1 is
not available on the connected feed for the pre-registered period, and the
connected feed is not Exness. Both are protocol-relevant deviations and cannot
be resolved by the research tooling alone.

| Item | Status | Effect |
| --- | --- | --- |
| D1 series, 2004-06-11 to 2026-11-04 | PASS | Usable, QA clean |
| H4 series, 2004-06-11 to 2026-11-04 | PASS | Usable, QA clean |
| H1 series, 2009-10-02 to 2026-11-04 | **FAIL** | Starts 5.75 years late |
| M15 series, 2022-08-03 to 2026-11-04 | **FAIL** | Starts 18.2 years late |
| Primary feed is Exness | **FAIL** | Connected feed is MetaQuotes-Demo |
| Historical tick/spread data from feed | **FAIL** | Feed tick history is recent only |
| D1 starts 2004-01-01 | **FAIL** | Starts 2004-06-11 |
| In-sample / out-of-sample split implementable | **CONDITIONAL** | Depends on the decisions below |
| External source can fill the gaps | PASS | Dukascopy XAUUSD reaches 2004 |

**No trial has been run. No result exists. Phase 2B remains at the validation
gate.**

---

## 2. Environment and feed (verified)

| Field | Value |
| --- | --- |
| Terminal | MetaTrader 5, build 6296 |
| Server | **MetaQuotes-Demo** |
| Company | MetaQuotes Ltd. |
| Account | 5058194810, USD, balance 100,000, leverage 1:100 |
| Symbol | XAUUSD |
| Digits / point / tick size | 2 / 0.01 / 0.01 |
| Contract size | 100 oz (confirmed by `order_calc_profit`: 1.0 lot x 0.01 = $1.00) |
| Minimum volume / step | 0.01 / 0.01 lot |
| Swap long / short | -12.6 / -4.6, mode 1 |
| Server clock offset | **UTC+2** (measured: last tick epoch is 2.00 h ahead of system UTC) |
| D1 bar boundary | 00:00 server time |
| H4 bar boundary | 00/04/08/12/16/20 server time (= 22/02/06/10/14/18 UTC) |

**This is not an Exness account.** Phase 2A names "Exness MT5, real ticks" as the
primary backtest source. The connected feed is a MetaQuotes demo feed. Its
prices are indicative and its historical intraday depth is much shorter than a
real broker's.

---

## 3. Native feed coverage (per calendar year)

`copy_rates_range` returns either a full year of bars or a single placeholder
bar. A count of 1 means "no intraday history for that year".

| Year | D1 | H4 | H1 | M15 |
| ---: | ---: | ---: | ---: | ---: |
| 2004 | 140 | 816 | - | - |
| 2005 | 252 | 1,476 | - | - |
| 2006 | 251 | 1,469 | - | - |
| 2007 | 257 | 1,535 | - | - |
| 2008 | 258 | 1,540 | - | - |
| 2009 | 257 | 1,538 | 1,406 | - |
| 2010 | 256 | 1,528 | 5,634 | - |
| 2011 | 256 | 1,525 | 5,726 | - |
| 2012 | 257 | 1,537 | 5,846 | - |
| 2013 | 258 | 1,544 | 5,875 | - |
| 2014 | 258 | 1,539 | 5,872 | - |
| 2015 | 258 | 1,532 | 5,843 | - |
| 2016 | 258 | 1,542 | 5,889 | - |
| 2017 | 257 | 1,534 | 5,861 | - |
| 2018 | 258 | 1,538 | 5,871 | - |
| 2019 | 258 | 1,540 | 5,871 | - |
| 2020 | 259 | 1,547 | 5,904 | - |
| 2021 | 258 | 1,542 | 5,900 | - |
| 2022 | 258 | 1,549 | 5,919 | 9,768 |
| 2023 | 257 | 1,542 | 5,894 | 23,559 |
| 2024 | 259 | 1,553 | 5,933 | 23,716 |
| 2025 | 258 | 1,545 | 5,899 | 23,547 |
| 2026 | 219 | 1,311 | 4,857 | 19,410 |

Precise first usable timestamps:

- D1: 2004-06-11 00:00
- H4: 2004-06-11 04:00
- H1: 2009-10-02 22:00
- M15: 2022-08-03 11:45

---

## 4. Native feed quality assurance (D1 and H4)

Both series were extracted, hashed and QA'd with
`Research/Phase-2B/tools/extract_and_qa.py`.

| Check | D1 | H4 |
| --- | --- | --- |
| Rows | 5,756 | 34,319 |
| Duplicate timestamps | 0 | 0 |
| Weekend-stamped rows | 0 | 0 |
| OHLC inconsistencies | 0 | 0 |
| Non-positive prices | 0 | 0 |
| Zero-volume rows | 0 | 0 |
| Gaps > 5 days (D1) / > 4 bars (H4) | 0 | 2 (2005-11-28, 2006-11-27, both ~2.2 days) |
| Log-return std | 0.01120 | 0.00448 |
| Skew / kurtosis | -0.41 / 6.00 | -0.19 / 15.15 |

Reference closes sanity check:

| Date | Close | Note |
| --- | ---: | --- |
| 2004-06-11 | 384.10 | first bar |
| 2011-09-06 | 1,875.63 | 2011 peak area |
| 2015-12-17 | 1,051.55 | 2015 low area |
| 2020-08-06 | 2,063.25 | 2020 peak area |
| 2026-11-04 | 4,063.84 | last bar |

Artifacts:

- `Research/Phase-2B/data/raw/mt5demo_XAUUSD_D1.csv`
  SHA-256 `88fd71222dadf82c8eca732dea80f1666dee63221daf77a357b7742587740b67`
- `Research/Phase-2B/data/raw/mt5demo_XAUUSD_H4.csv`
  SHA-256 `c468d1396ea719b0ac1867617e4fb1659a81dcc5886057006d98e94129ea3fe4`

**The spread column is not a cost model.** In D1 it runs 0 / 5 / 100 points
(min / median / max); that is the recorded bar-close spread, not the spread a
retail order would face intraday. The abnormal Phase 0 reading of ~$58.12 is
excluded entirely.

---

## 5. Native feed tick history

`copy_ticks_range` returns zero ticks for every sampled week from 2004 to 2024.
The only non-empty window found is 2026-10-26 onward (1.36 M ticks in one week).
The feed therefore cannot supply a historical intraday spread distribution.

Current live spread at the time of the probe: 13 points ($0.13), which is
consistent with a normal active-market reading and confirms the ~$58.12 Phase 0
value was abnormal.

---

## 6. External source: Dukascopy XAUUSD

Dukascopy is the only external source found that reaches the required period
with intraday granularity. Probes were run with retries; individual requests
intermittently return connection timeouts or HTTP 503, so ingestion must be
retried.

| Endpoint | Granularity | Earliest verified | Record layout |
| --- | --- | --- | --- |
| `.../YYYY/MM/DD/BID_candles_min_1.bi5` | 1 minute, per day | 2004-01-05 (2003 files exist but are flat/zero-volume placeholders) | LZMA, 24-byte records `(sec_offset, open, close, low, high, volume_float)`, prices / 1000 |
| `.../YYYY/MM/BID_candles_hour_1.bi5` | 1 hour, per month | 2004-01 | same 24-byte layout |
| `.../YYYY/MM/BID_candles_day_1.bi5` | 1 day, per month | 2004-01 | same 24-byte layout |
| `.../YYYY/MM/DD/ASK_candles_min_1.bi5` | 1 minute, ask side | same as BID | same |

Verified decoded samples:

- 2004-01-05 minute file: 1,440 records, first open 415.376
- 2004-01 hour file: 744 records, first open 414.922
- 2012-02 minute file: 1,440 records, first open 1,719.322
- 2024-05 minute file: 1,440 records, first open 2,355.695
- 2004-01 day file: 31 records, first open 414.922

Because BID and ASK are both published, a **time-varying historical spread**
(`ask - bid`) can be derived without any broker tick data.

Known limitations:

- 2003 and early-2004 contain flat, zero-volume placeholder days that must be
  filtered.
- The archive is a different venue from both Exness and MetaQuotes. It is
  external gold price data, not broker execution data.
- Ingestion cost: ~16,000 minute files (BID + ASK) for 2004-2026, roughly
  250 MB compressed. With retries and modest concurrency this is a few hours.

---

## 7. Timezone and bar-boundary convention

| Source | Timestamp basis | Evidence |
| --- | --- | --- |
| MT5 D1/H4 | Server time, UTC+2 | Last tick epoch is exactly 2.00 h ahead of system UTC; all D1 bars stamped 00:00; H4 at 0/4/8/12/16/20 |
| Dukascopy | UTC | Standard datafeed convention; to be confirmed on the first ingested file by matching an MT5 D1 close |

**Consequence.** MT5 H4 bars close at 22/02/06/10/14/18 UTC, not at
00/04/08/12/16/20 UTC. If H4 is built from Dukascopy UTC bars, the boundaries
differ from the MT5 series. Whichever convention is used must be fixed in
writing before signal generation and applied to both IS and OOS without change.

---

## 8. Cost-model readiness

| Cost component | Native feed | External source | Status |
| --- | --- | --- | --- |
| Historical spread | Recent ticks only | Dukascopy BID/ASK, 2004+ | Obtainable only from Dukascopy |
| Commission | Not exposed by symbol_info | Not applicable | Testing assumption required |
| Swap / financing | Current schedule only (-12.6 / -4.6, mode 1) | Not available historically | Testing assumption required |
| Slippage | Not measurable historically | Not available | Testing assumption required |

This means the baseline cost model cannot be "measured from the broker" for the
historical period. It will have to be a documented testing assumption, stressed
at 1.0x / 1.5x / 2.0x as the protocol requires. That is a material difference
from what Phase 2A Section 11.4 describes, so it needs approval.

---

## 9. Split feasibility

Pre-registered split:

- In-sample: 2004-01-01 to 2016-12-31
- Out-of-sample: 2017-01-01 to 2026-06-30
- Holdout: 2022-01-01 to 2026-06-30

| Family | Timeframes needed | Native feed satisfies split? | Dukascopy satisfies split? |
| --- | --- | --- | --- |
| T1 | H4 regime, M15 entry, H1 ATR | **No** - M15 starts 2022-08, H1 starts 2009-10. Zero M15 in-sample data. | Yes, 2004-01 onward |
| T2 | D1 | **No** - starts 2004-06-11 (5.5-month shortfall) | Yes, 2004-01 onward |
| T3 | D1 monthly | **No** - same 5.5-month shortfall | Yes, 2004-01 onward |

For T1, the native feed leaves **no in-sample M15 data at all**. Restricting T1
to 2022-2026 would place the entire test inside the holdout window and destroy
the IS/OOS structure. That is not a viable protocol deviation.

---

## 10. Blockers

**B1. T1 cannot run as pre-registered on the connected feed.**
M15 exists only from 2022-08-03 and H1 only from 2009-10-02, against a
2004-01-01 in-sample start. There is no acceptable native-data workaround.

**B2. The primary feed is not Exness.**
Phase 2A names Exness real ticks as primary. The only connected feed is
MetaQuotes-Demo. Using it as if it were Exness would misrepresent execution
data, which the master prompt explicitly forbids.

**B3. D1 starts 2004-06-11, not 2004-01-01.**
A 5.5-month shortfall against the pre-registered in-sample start.

**B4. No historical broker spread, commission or swap data.**
The cost model cannot be built from broker measurements for 2004-2026.

---

## 11. Options requiring project-owner decision

### Decision 1 - T1 intraday data

| Option | What it means | Consequence |
| --- | --- | --- |
| **A. Build M15 + H1 from Dukascopy minute/hour candles, 2004-2026** (recommended) | One external source, documented as a substitution; MT5 D1/H4 kept as an independent cross-check | T1 runs as pre-registered; data provenance changes from "Exness real ticks" to "Dukascopy" |
| B. Restrict T1 to 2022-2026 | Use native M15 only | No in-sample period; entire test inside the holdout; T1 becomes exploratory, not confirmatory |
| C. Defer T1 until Exness access | Run nothing in T1 | Order becomes T2 -> T3 -> T1, which contradicts the mandatory T1-first order |

### Decision 2 - Primary historical price source

| Option | What it means | Consequence |
| --- | --- | --- |
| **A. Dukascopy as the single historical source for all three families, MT5 as cross-check** (recommended) | Consistent provenance, full 2004-2026 coverage, UTC timestamps, BID/ASK for costs | Documented data-source change; still not broker execution data |
| B. MT5 for D1/H4, Dukascopy only for M15/H1 | Uses the "closest to broker" data where available | Mixes feeds and bar boundaries; D1 still starts 2004-06-11 |
| C. MT5 only | No substitution | T1 impossible; D1 short by 5.5 months |

### Decision 3 - D1 start date

| Option | Consequence |
| --- | --- |
| **A. Use Dukascopy D1/H1 from 2004-01-01** (follows from Decision 2A) | Split exactly as pre-registered |
| B. Accept 2004-06-11 as a recorded deviation | 5.5 months lost; split otherwise unchanged |
| C. Source early-2004 data externally only for the gap | Creates a splice artefact at the join |

### Decision 4 - Cost model

| Option | Consequence |
| --- | --- |
| **A. Time-varying spread derived from Dukascopy BID/ASK; commission, swap and slippage as documented testing assumptions, all stressed 1.0x/1.5x/2.0x** (recommended) | Cost model is explicit, reproducible and conservative; not broker-measured |
| B. Flat spread assumption | Simpler, less realistic, hides session effects |
| C. Wait for broker tick history | No data exists for the historical period; would block indefinitely |

### Decision 5 - Bar-boundary convention

| Option | Consequence |
| --- | --- |
| **A. UTC boundaries throughout (00/04/08/12/16/20 for H4)** (recommended with Dukascopy) | Consistent with data timestamps; must be stated in every trial report |
| B. Server-time boundaries (UTC+2) | Matches MT5 H4 bars, but requires re-stamping Dukascopy data |

---

## 12. Recommendation

Approve **Decision 1A, 2A, 3A, 4A and 5A**: use Dukascopy XAUUSD as the single
historical price source for 2004-2026, build D1/H4/H1/M15 from it on UTC
boundaries, derive a time-varying spread from BID/ASK, and keep the extracted
MT5 D1/H4 series as an independent cross-check. Record all of this as a
documented protocol deviation under the `Proposed Protocol Change` section that
Phase 2A Section 11.13 requires.

This is the only combination that lets T1, T2 and T3 run on the pre-registered
period and split without fabricating broker data.

If any of these decisions is not approved, the affected family stops and is
reported as blocked rather than run on an undocumented assumption.

---

## 13. Artifacts produced in this validation step

| File | Purpose |
| --- | --- |
| `Research/Phase-2B/tools/probe_mt5.py` | account, terminal, symbol probe |
| `Research/Phase-2B/tools/probe_xauusd_depth.py` | D1/H4 history depth |
| `Research/Phase-2B/tools/probe_intraday_and_math.py` | intraday depth, P&L and margin arithmetic |
| `Research/Phase-2B/tools/probe_coverage_by_year.py` | per-year coverage table |
| `Research/Phase-2B/tools/probe_external_sources.py` | Dukascopy / Stooq / Yahoo availability |
| `Research/Phase-2B/tools/probe_dukascopy_candles.py` | minute-candle record layout |
| `Research/Phase-2B/tools/probe_dukascopy_fast.py` | minute/hour/day endpoint coverage |
| `Research/Phase-2B/tools/probe_timezone_compact.py` | server offset and bar boundaries |
| `Research/Phase-2B/tools/probe_tick_depth.py` | tick-history depth and current spread |
| `Research/Phase-2B/tools/extract_and_qa.py` | D1/H4 extraction, hashing, QA |
| `Research/Phase-2B/tools/qa_followup.py` | follow-up QA (superseded by the compact probe) |
| `Research/Phase-2B/data/raw/mt5demo_XAUUSD_D1.csv` | D1 series, QA-passed |
| `Research/Phase-2B/data/raw/mt5demo_XAUUSD_H4.csv` | H4 series, QA-passed |
| `Research/Phase-2B/data/raw/mt5demo_XAUUSD_metadata.json` | spec, hashes, row counts |
| `Research/Phase-2B/reports/data-qa-mt5demo.md` | generated QA report |
| `Research/Phase-2B/reports/data-readiness.md` | this report |

No tracked file was modified. `EA/`, `GoldEA.mq5`, Phase 1 code and `ROADMAP.md`
are untouched.
