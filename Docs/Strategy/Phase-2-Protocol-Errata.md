# Phase 2 Protocol Errata

Project: Gold EA  
Document type: Protocol errata and historical record  
Status: Draft for owner review; separate errata record  
Prepared: 2026-11-09 (errata preparation date; not a Phase 2A or Phase 2B approval date)  
Supplements: Phase 2A v0.2, Phase 2B Final Review, Phase 2B reports  
Code changes: None  
EA changes: None  
Files changed by this document: This document only

---

## 1. Purpose and status

### 1.1 Why this errata exists

Phase 2A v0.2 was preserved byte-for-byte as the historical pre-Phase-2B research
and pre-registration record. Phase 2B was then executed, closed and frozen. A
review of the Phase 2A document against the Phase 2B record identified:

- ten material Phase 2A documentation or protocol-definition issues (A1-A10);
- seven minor documentation issues (B1-B7);
- ten Phase 2B execution deviations from the Phase 2A protocol (C1-C10).

The Phase 2A document cannot be silently corrected without destroying its value
as a pre-registration record. The Phase 2B closure document is also frozen. This
errata therefore records the identified issues and deviations in one separate,
traceable document.

### 1.2 Records this errata supplements

| Record | Role | Status |
| --- | --- | --- |
| `Docs/Strategy/Phase-2A-Trend-Following-Research.md` | Phase 2A research and pre-registered Phase 2B protocol, v0.2 | Preserved byte-for-byte; SHA-256 `475C8B8B72C5AD5D9845EAFC05ACA781C57BA6272063E1278F09A6B47F9A1697`; committed as `04fc1c82e9e16c606ee56886c1cf5ad021fd289d` |
| `Docs/Strategy/Phase-2B-Final-Review.md` | Phase 2B closure and decision record | Frozen at `c226958b40df74f2e4d78efdbecad07d311cf3c4`; tag `v0.3-phase2b-frozen` |
| `Research/Phase-2B/reports/Phase-2B-comparative-report.md` | Cross-family comparison | Preserved in place |
| `Research/Phase-2B/reports/T1-report.md` | T1 family evidence and verdict | Preserved in place |
| `Research/Phase-2B/reports/T2-report.md` | T2 family evidence and verdict | Preserved in place |
| `Research/Phase-2B/reports/T3-report.md` | T3 family evidence and verdict | Preserved in place |
| `Research/Phase-2B/reports/data-readiness.md` | Data and methodology readiness, including disclosed deviations | Preserved in place |

### 1.3 What this errata does and does not do

This errata:

- records identified inconsistencies and deviations;
- distinguishes facts, owner decisions, assumptions and recommendations;
- preserves the existing Phase 2B verdicts;
- provides safeguards for Phase 3A onward.

This errata does **not**:

- replace, amend or supersede Phase 2A v0.2;
- replace, amend or supersede the Phase 2B Final Review or any Phase 2B report;
- rerun, recompute or alter any trial, metric or result;
- upgrade, downgrade or reclassify any Phase 2B verdict;
- promote any strategy;
- create a new approval, date or data source;
- claim that an omitted cross-check was completed.

### 1.4 Evidence conventions used in this document

| Label | Meaning |
| --- | --- |
| **Fact** | Directly documented in the repository records listed in Section 1.2. |
| **Owner decision (conversation)** | A decision recorded in the project conversation, not necessarily committed to the repository before testing. |
| **Assumption** | A testing or modelling assumption, not a verified historical fact. |
| **Recommendation** | A proposed control for future phases; not an approval and not evidence that the control existed in Phase 2B. |
| **Not established in the available project record** | The exact evidence was not found in the reviewed repository records. This is not proof that the event did not occur. |

---

## 2. Phase 2A protocol and documentation corrections

These items are corrections to the historical record, not edits to Phase 2A v0.2.
The original document remains unchanged.

### 2.1 Material issues A1-A10

#### A1. Metadata, version and date ambiguity

- **Where:** Phase 2A header line 5; Section 1; Section 19.
- **Specified or recorded:** The header says `Status: revised draft for review (v0.2)`. Section 1 has no explicit research-date field. Section 19 records versions 0.1 and 0.2, both dated 2026-11-01.
- **Issue:** Phase 2B Final Review Section 1.2 treats v0.2 as the fixed protocol. A document still labelled “draft for review” is ambiguous as a frozen pre-registration record. The research date is inferable from Section 19 but is not stated in document control.
- **Record treatment:** This errata records v0.2 as the preserved pre-Phase-2B record. It does not change the Phase 2A status line.
- **Effect on Phase 2B:** No numerical result or verdict change. Traceability and metadata clarity are affected.

#### A2. T1 risk-grid trial-count inconsistency

- **Where:** Phase 2A Section 8.1; Section 11.7; Appendix 15.2.
- **Specified or recorded:** Section 8.1 gives a 0.5% risk baseline with 0.25% and 1.0% as sensitivity values. Section 11.7 defines the T1 grid as 2 pullback distances x 2 stop multiples x 2 RSI states = 8 trials, with risk not listed as a grid dimension. Appendix 15.2 lists risk per trade as `0.5% | 0.25%, 0.5%, 1.0%`.
- **Issue:** Read literally, Appendix 15.2 implies 24 T1 trials, not 8, and a total confirmatory count of 48, not 32. Phase 2B Final Review Section 2.2 confirms T1 ran 8 trials at 0.5% risk.
- **Record treatment:** The 8-trial Section 11.7 grid and the Phase 2B 8-trial allocation governed the test. The 0.25% and 1.0% values are not established in the Phase 2B record as confirmatory T1 trials.
- **Effect on Phase 2B:** No numerical result or verdict change. Pre-registration clarity and trial accounting are affected.

#### A3. T2 EMA-grid trial-count inconsistency

- **Where:** Phase 2A Section 11.7; Appendix 15.3.
- **Specified or recorded:** Section 11.7 lists three paired EMA combinations: (20,100), (50,200), (100,400), producing 3 pairs x 3 stops x 2 risk fractions = 18 trials. Appendix 15.3 lists fast EMA values `20, 50, 100` and slow EMA values `100, 200, 400` as separate grids.
- **Issue:** Read independently, Appendix 15.3 implies nine EMA pairs and 54 T2 trials. Phase 2B Final Review Section 2.3 confirms 18 trials using the three paired combinations.
- **Record treatment:** The Section 11.7 paired grid and the Phase 2B 18-trial allocation governed the test. Appendix 15.3 should be read as the component values of the three pairs, not as independent grids.
- **Effect on Phase 2B:** No numerical result or verdict change. Pre-registration clarity and trial accounting are affected.

#### A4. T3 macro-regime count inconsistency

- **Where:** Phase 2A Section 8.3; Section 11.6.
- **Specified or recorded:** Section 8.3 says T3 is rejected if it is “not positive in at least 2 of the 3 macro regimes in Section 11.6.” Section 11.6 defines five macro regimes: M1 (2004-2011), M2 (2012-2015), M3 (2016-2019), M4 (2020-2021) and M5 (2022-2026).
- **Issue:** The gate says three, while the regime definition contains five. Only three regimes are observable in the out-of-sample period (M3-M5). The T3 report explicitly resolves the ambiguity as “at least 2 of the 3 OOS regimes.”
- **Record treatment:** Phase 2B applied the gate to the three observable OOS regimes (M3-M5). T3 was positive in one of those three, so the gate failed under the resolved reading. This errata makes no finding about how a gate applied to all five defined regimes would have resolved; only the three observable OOS regimes establish a result in the available record.
- **Effect on Phase 2B:** No numerical result or verdict change. T3 remains INCONCLUSIVE. Gate interpretation is affected.

#### A5. Swap-cost direction assumption reversed

- **Where:** Phase 2A Section 6.7; Section 8.2.
- **Specified or recorded:** Section 6.7 says swap “can be positive or negative; short gold often costs more.” Section 8.2 lists “Swap drag on multi-month holds, especially shorts” as a T2 weakness.
- **Actual Phase 2B assumption:** Phase 2B Final Review Section 1.2 and the T2/T3 reports apply swap long = USD -0.126/oz/day and swap short = USD -0.046/oz/day. Long gold carries the larger negative swap in the tested model.
- **Issue:** The Phase 2A directional statement is reversed relative to the actual Phase 2B testing assumption. Swap direction is broker-specific, so the general statement is not necessarily wrong for every broker, but it does not describe the tested model.
- **Record treatment:** The Phase 2B testing assumption governs the Phase 2B results. This errata does not recalculate swap or net P&L.
- **Effect on Phase 2B:** No numerical result or verdict change established. Cost interpretation is affected because swap is the dominant cost in T2 and T3.

#### A6. Drawdown gate definition ambiguity

- **Where:** Phase 2A Section 8.2; Section 11.9.
- **Specified or recorded:** Section 8.2 rejects T2 if maximum drawdown exceeds 25%. Section 11.9 defines maximum drawdown as “peak-to-trough, net” but does not state whether the basis is compounded account equity or constant-risk notional equity.
- **Actual Phase 2B record:** T2 OOS maximum drawdown is -21.4% on the compounded basis and -30.2% on the constant-risk notional basis. Phase 2B Final Review Section 3.3 records the gate as PASS on the compounded basis.
- **Issue:** The pre-registration did not define which basis is binding. If the constant-risk basis were binding, the T2 drawdown gate would fail, although T2 would remain INCONCLUSIVE because of the trade-count rule.
- **Record treatment:** The Phase 2B Final Review’s compounded-basis PASS is the recorded gate result. This errata does not substitute the constant-risk basis or recalculate the verdict.
- **Effect on Phase 2B:** No verdict change. A gate result is basis-sensitive; this is an interpretation and pre-registration clarity issue.

#### A7. Verdict precedence ambiguity

- **Where:** Phase 2A Section 8.2; Section 8.3; Section 11.11.7; Section 11.12.
- **Specified or recorded:** Section 8.2/8.3 say fewer than 100 trades for T2/T3 is reported as INCONCLUSIVE, not PASS or FAIL. The same sections also list economic and statistical gates. Section 11.11.7 defines FAIL as one or more failed gates and INCONCLUSIVE as sample too small, data inadequate or result not separable from noise. Section 11.12 lists “candidate fails its gates on OOS” and “fewer than 100 trades” without stating which rule takes precedence.
- **Actual Phase 2B record:** T2 and T3 failed several economic gates but were recorded INCONCLUSIVE because of the trade-count rule. The Phase 2B Final Review treats INCONCLUSIVE as controlling.
- **Issue:** The pre-registration did not state the precedence rule explicitly. Phase 2B had to resolve it.
- **Record treatment:** The Phase 2B Final Review’s INCONCLUSIVE verdicts are preserved. This errata does not reclassify them as FAIL.
- **Effect on Phase 2B:** No numerical result or verdict change. Verdict interpretation and pre-registration clarity are affected.

#### A8. Expected trade-frequency inconsistency

- **Where:** Phase 2A Section 8.1; Section 8.2; Section 8.5.
- **Specified or recorded:** Section 8.1 expects T1 to produce 2-10 trades per month; Section 8.5 summarizes T1 as 25-120 trades per year. Section 8.2 expects T2 to produce roughly 2-6 position flips per year and estimates an effective sample of roughly 50-130 trades over 22 years; Section 8.5 summarizes T2 as 2-6 trades per year.
- **Actual Phase 2B record:** The selected T1 trial produced 6,353 full-sample trades over approximately 18.7 years, roughly 340 trades per year and about 28 per month. The selected T2 trial produced 20 full-sample trades over approximately 18.66 years, roughly 1.07 per year.
- **Issue:** The ex-ante expectations were materially different from the actual counts. The T2 power discussion overestimated the likely sample size. The pre-registered 100-trade rule did correctly identify the low-power outcome.
- **Record treatment:** The Phase 2B actual counts govern the record. This errata does not retroactively change the Phase 2A expectations or the trial rules.
- **Effect on Phase 2B:** No numerical result or verdict change. Statistical-power interpretation is affected.

#### A9. E1 evidence-grade definition and application inconsistency

- **Where:** Phase 2A Section 1.2; Section 14.3; Section 14.4; claims C18 and C43.
- **Specified or recorded:** Section 1.2 defines E1 as replicated across independent samples, markets and methods. Section 14.3 grades arithmetic claims C35-C40 as E1. Section 14.4 grades single-broker observations C41-C42 as E1. C18 and C43 are methodological claims also graded E1.
- **Issue:** Arithmetic, single-broker observations and methodology are not “replicated across independent samples” in the sense of the Section 1.2 definition. The document uses E1 more broadly than the definition states.
- **Record treatment:** This errata records the definition/application inconsistency. It does not change any claim or evidence grade in Phase 2A.
- **Effect on Phase 2B:** No numerical result or verdict change. Evidence-taxonomy interpretation is affected.

#### A10. Spread example versus measured spread data

- **Where:** Phase 2A Section 6.7; Section 7.5; Section 11.4.
- **Specified or recorded:** Section 6.7 gives a general retail spread range of 10-30 points (USD 0.10-0.30/oz). Section 7.5 uses a 20-point spread and a round-trip cost of roughly USD 0.27 per 0.01 lot. Section 11.4 requires a measured spread distribution.
- **Actual Phase 2B record:** The T2 report records a Dukascopy median spread of USD 0.418 and a 95th percentile of USD 0.677, roughly 41.8 points at the median. The native MetaQuotes demo probe recorded a current active-market spread of 13 points. The Phase 2B cost model used the measured Dukascopy BID/ASK spread, not the Section 7.5 example.
- **Issue:** The Section 7.5 example is below the measured Dukascopy spread used in Phase 2B. It remains an order-of-magnitude illustration and is not the Phase 2B cost model.
- **Record treatment:** The measured Phase 2B spread governs the Phase 2B results. This errata does not recalculate costs.
- **Effect on Phase 2B:** No numerical result or verdict change. Cost-realism interpretation is affected.

### 2.2 Minor issues B1-B7

| ID | Issue | Where | Record treatment | Effect on Phase 2B |
| --- | --- | --- | --- | --- |
| **B1** | The “Costs modelled” row cites Section 5.8, which is the overfitting section, not the cost section. | Section 8.0 | Read as a cross-reference error; the relevant cost material is Section 6.7 and Section 11.4. | None. |
| **B2** | The Bajgrowicz & Scaillet row says “even in-sample performance is offset by low transaction costs,” which is internally contradictory. | Section 5.8 | Recorded as a wording issue. The intended wording is not established in the available record; it should be verified against the cited paper before reuse. | None. |
| **B3** | Gold technical-rule evidence is graded E2/E3 in the executive summary and E2 in the detailed section and claim ledger. | Section 2.1 item 5; Section 5.4; claim ledger C21-C25 | Recorded as a grade inconsistency. The detailed E2 grade is the more specific statement. | None. |
| **B4** | MAR and Calmar ratios are both defined as “CAGR / maximum drawdown.” | Section 11.9 | Recorded as an imprecise metric definition. They should not be treated as interchangeable without a stated lookback convention. | None. |
| **B5** | Section 19 says “All quantitative figures are labelled as illustrative or arithmetic, not as tested results,” but the document also contains sourced historical and industry figures. | Section 19 | Recorded as an overbroad statement. The correct scope is strategy-performance figures; market data are sourced and graded separately. | None. |
| **B6** | The T3 gate “Fails specifically in 2011-2015 … and the failure is not explained by a single outlier period” is syntactically ambiguous. | Section 8.3 | Recorded as a wording ambiguity. The intended condition is not restated as a new rule. | None. |
| **B7** | Section 11.13 says this revision proposes no protocol change, while Section 19 says v0.2 added a reporting template, protocol-preservation statement and governance section. | Section 11.13; Section 19 | Recorded as a documentation-scope ambiguity. The v0.2 changes are documentation changes; they are not established here as changes to the pre-registered commitments. | None. |

---

## 3. Phase 2B execution deviations

These items describe what Phase 2A specified or assumed, what the Phase 2B record
shows was actually done, and the traceability status of the difference.

### C1. Execution order: T1 -> T2 -> T3

- **Phase 2A specification or recommendation:** Section 10.1 recommends T2 first,
  T3 second, and T1 as a conditional incremental test. Section 10.8 says the
  roadmap prevails if it mandates a particular order and that the project owner
  should resolve the T1-vs-T2 tension in writing before Phase 2B.
- **Owner decision (conversation):** The project owner explicitly selected the
  T1 -> T2 -> T3 execution order in the project conversation, overriding the
  earlier T2-first recommendation.
- **Repository record:** Phase 2B Final Review Section 1.2 lists
  `Mandatory order | T1 -> T2 -> T3`. The data-readiness report line 264 calls
  T1-first the “mandatory” order. The T1, T2 and T3 reports describe themselves
  as family 1, 2 and 3 of 3 in that order.
- **Traceability distinction:** The owner decision is recorded in the project
  conversation. It is **not** described here as a repository commit. No
  pre-test commit containing the execution-order decision was found in the
  repository records reviewed for this errata. This is a traceability gap, not
  evidence that the decision was absent.
- **Effect on Phase 2B:** The order changed relative to Phase 2A Section 10.1.
  No numerical result was recalculated. The T1 FAIL is consistent with Phase 2A’s
  weak prior for T1. The existing verdicts are preserved.

### C2. Primary data source: Dukascopy instead of Exness MT5 real ticks

- **Phase 2A specification:** Section 11.2 and Appendix 15.7 name Exness MT5
  real ticks as the primary backtest data and Dukascopy as an independent
  cross-check.
- **Actual Phase 2B execution:** Dukascopy XAUUSD BID/ASK candles, retrieved
  2026-11-05, were the primary price source. The MetaQuotes demo D1/H4 series
  was used as an independent cross-check. The data-readiness report states that
  the connected feed is MetaQuotes-Demo, not Exness, and that using it as Exness
  would misrepresent execution data.
- **Traceability:** The substitution is disclosed in the data-readiness report
  and Phase 2B Final Review Section 8.1.
- **Effect on Phase 2B:** Data provenance and cost realism are affected. This is
  not broker execution data. No numerical result or verdict change was
  recalculated. The existing verdicts are preserved.

### C3. Execution model: Python bar simulator and OHLC stop approximation

- **Phase 2A specification:** Section 11.1 requires M1 granularity for intraday
  execution. Section 11.5 prefers “Every tick based on real ticks,” accepts
  “1 minute OHLC” only for daily-signal strategies, and does not accept “Open
  prices only” for a stop-based candidate.
- **Actual Phase 2B execution:** All results come from a vectorised Python bar
  simulator, not the MT5 tester. T1 used M15 entries and H1 ATR; T2 and T3 used
  D1. Intrabar stops and trails were approximated from bar OHLC, with stop-first
  priority and gap fills at the open.
- **Traceability:** Disclosed in Phase 2B Final Review Section 8.4.
- **Effect on Phase 2B:** Execution approximation and model risk are affected,
  most notably for T1’s high trade count and tight stops. No numerical result or
  verdict was recalculated. T1 remains FAIL; the exact magnitude is approximate,
  not recomputed.

### C4. No LBMA PM fix cross-check

- **Phase 2A specification:** Section 11.2 requires a daily-series cross-check
  against the LBMA Gold Price PM and rejection if the series differs by more
  than 1% on more than 0.5% of days. Section 12.1 also names LBMA fixes as a
  vendor-bias mitigation.
- **Actual Phase 2B execution:** The Dukascopy D1 series was cross-checked
  against the MT5 demo D1 series: 5,752 common dates, median absolute close
  difference 0.0277%, 95th percentile 0.1497%, maximum 1.6102%, and daily
  log-return correlation 0.99549. No LBMA PM fix cross-check is reported in the
  available project record.
- **Traceability:** Disclosed as part of the data-source discussion, but the
  LBMA check itself is not reported as completed.
- **Effect on Phase 2B:** The pre-registered validation gate was substituted,
  not applied as written. Reproducibility and confidence are affected. No
  numerical result or verdict change was recalculated.

### C5. No COMEX GC futures cross-check

- **Phase 2A specification:** Section 11.2 says T2 and T3 should be re-run on
  COMEX GC continuous futures, and that a sign flip between spot and futures
  must be reported as instrument-specific.
- **Actual Phase 2B execution:** The universe was gold only. No COMEX GC
  continuous-futures cross-check is reported in the available project record.
- **Traceability:** The single-instrument limitation is acknowledged, but the
  futures cross-check is not reported as completed.
- **Effect on Phase 2B:** The instrument-specificity check is missing.
  Reproducibility and interpretation are affected. No numerical result or
  verdict change was recalculated.

### C6. Missing 60/40 and always-long controls

- **Phase 2A specification:** Section 11.10 lists four controls: buy-and-hold
  gold, a 60/40 portfolio, random entry with matched exposure, and always-long
  with the same volatility target. The always-long control is a pass condition
  for the short side/timing question: the candidate must beat it on Sharpe, not
  just on return.
- **Actual Phase 2B execution:** Buy-and-hold and random-entry controls were
  implemented. The 60/40 and always-long controls were not implemented. The
  explanations differ by control and by family:
  - **60/40 portfolio:** the approved Phase 2B data set contains only gold.
    Constructing a 60/40 portfolio would require non-gold asset data and a
    portfolio definition that are not in the approved data set.
  - **Always-long control for T2:** the pre-registered form is always-long with
    the same volatility target. Phase 2B Final Review Section 4.4 states that T2
    has no volatility target, so that form would require inventing a definition.
  - **Always-long control for T3:** the T2-specific rationale does not explain
    the omission for T3. The T3 report attributes the omission to the
    single-instrument data set (Section G, item 10) and, in its missing-controls
    section (Section D), to the gold-only data and the unapproved assumptions a
    60/40 definition would require. A T3-specific always-long definition, and
    whether such a definition was approved, is **not established in the
    available project record**. This control is directly relevant to T3 because
    Phase 2A Section 11.10 makes the always-long comparator a pass condition:
    the candidate must beat it on Sharpe, not just on return.

  Phase 2B Final Review Section 4.4 and the comparative report disclose the
  omission.
- **Traceability:** Disclosed as missing, not treated as passes.
- **Effect on Phase 2B:** Control completeness and interpretation are affected.
  T3 was already INCONCLUSIVE, so the missing always-long control does not
  convert T3 to a pass. No numerical result or verdict change was recalculated.

### C7. Current MT5 demo swap schedule applied historically

- **Phase 2A specification:** Section 11.4 names “Actual broker schedule,
  applied daily at rollover” for swap. Sections 6.8.3 and 6.8.4 also flag swap
  as unconfirmed and as a testing assumption.
- **Actual Phase 2B execution:** The current MT5 demo swap schedule was applied
  to the entire 2004-2026 history: long USD -0.126/oz/day, short USD -0.046/oz/day,
  triple swap on Wednesday. Historical swap schedules were not verified.
- **Traceability:** Disclosed in Phase 2B Final Review Section 7.1.
- **Effect on Phase 2B:** Cost realism is materially affected because swap is
  96.0% of T2 OOS costs and 93.9% of T3 OOS costs. The current schedule is a
  testing assumption, not verified historical cost. No numerical result or
  verdict change was recalculated.

### C8. T4 ablation not run

- **Phase 2A specification:** Section 10.5 and Section 11.7 pre-register T4 as a
  descriptive ablation: six filters individually on the best T1 and best T2
  configuration, then all together, for 7 tests per base and 14 ablation tests
  in total.
- **Actual Phase 2B execution:** The 14 pre-registered ablation tests were not
  run.
- **Phase 2B execution rationale:** Phase 2B Final Review Section 2.1 states
  that T4 is not a standalone candidate and that the ablation would only have
  meaning after a T1 or T2 candidate passed. That is the Phase 2B execution-stage
  rationale for not running T4.
- **Distinction from the Phase 2A preregistration:** Phase 2A Section 10.5 and
  Section 11.7 pre-register T4 as part of the protocol independently of whether
  a candidate later passed. The Phase 2B section 2.1 rationale is an
  execution-stage judgement made against that preregistration, not a change to
  the Phase 2A specification. Whether the decision was separately approved
  before or during Phase 2B is **not established in the available project
  record**.
- **Traceability:** Disclosed in the final review.
- **Effect on Phase 2B:** The pre-registered descriptive attribution is
  missing. No confirmatory trial was lost, and no numerical result or verdict
  change was recalculated.

### C9. Phase 1 runtime symbol/specification layer: use and derivation not established

- **Phase 2A specification:** Section 15.1 requires Phase 2B to use the Phase 1
  symbol layer (`GoldEASymbol.mqh`) and not introduce hardcoded broker values.
- **Actual Phase 2B execution:** The Python simulator used fixed instrument
  specifications in the form stated in Phase 2B Final Review Section 1.2:
  XAUUSD, 2 digits, 100 oz per lot, minimum volume 0.01, volume step 0.01.
- **Two separate questions — direct runtime use versus derivation:**
  - **Direct use of the Phase 1 runtime layer:** `GoldEASymbol.mqh` is MQL5 code.
    It is **not established in the available project record** that the Python
    simulator called, loaded or read the Phase 1 MQL5 runtime symbol layer, or
    that the Phase 1 layer was executed at all during Phase 2B.
  - **Derivation of the Python specifications:** it is also **not established in
    the available project record** whether the fixed values above were exported
    from, copied from, or otherwise derived from the Phase 1 layer, or were
    independently re-entered as constants in the Python simulator. Derivation
    and direct runtime use are distinct: a value could be derived from the Phase
    1 layer without the layer being used at runtime, and vice versa.
- **Traceability:** The tested specifications are disclosed. Neither direct use
  of the Phase 1 runtime layer nor derivation of the Python specifications from
  it is established in the available record.
- **Effect on Phase 2B:** The implementation control is not demonstrated in the
  available record. The tested specifications match the Phase 0 observation, so
  a numerical error is not established. No numerical result or verdict change
  was recalculated.

### C10. Required `Proposed Protocol Change` section absent or insufficient

- **Phase 2A specification:** Section 11.13 requires any methodological change
  to be recorded in a section titled `Proposed Protocol Change`, stating what is
  changed, why, what evidence supports it, and which trials, results and
  conclusions are affected.
- **Actual Phase 2B execution:** The data-readiness report recommended recording
  the Dukascopy substitution under that required heading. The Phase 2B Final
  Review documents data and execution deviations in Sections 7-8, but it does not
  contain a section titled `Proposed Protocol Change`, and Section 1.2 says
  “Phase 2B did not change them.”
- **Traceability:** The deviations are disclosed in the final review, but not in
  the required section or format.
- **Effect on Phase 2B:** Traceability and change control are affected. No
  numerical result or verdict change was recalculated.

---

## 4. Impact assessment

### 4.1 Legend

| Symbol | Meaning |
| --- | --- |
| **Yes** | The item can materially affect this dimension. |
| **Partial** | The item affects this dimension only under a stated condition or to a limited degree. |
| **No** | No material effect identified. |
| **No change established** | No recalculation was performed and no existing Phase 2B numerical result or verdict is altered. |

The dimensions are: **Repro** = reproducibility; **Cost** = cost realism;
**Power** = statistical power; **Interp** = interpretation and confidence;
**Result** = numerical result or verdict change.

### 4.2 Consolidated impact matrix

| ID | Specified or assumed | Actually documented or executed | Repro | Cost | Power | Interp | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **A1** | v0.2 as the fixed pre-registered protocol; research date in Section 19 | Header still says “revised draft for review”; no research-date field in Section 1 | Partial | No | No | Yes | No change established |
| **A2** | T1 grid = 8 trials, risk fixed at 0.5% for confirmatory trials | Appendix 15.2 lists three risk values; Phase 2B ran 8 trials at 0.5% | Yes | No | No | Yes | No change established |
| **A3** | T2 grid = 18 trials using three paired EMA combinations | Appendix 15.3 lists fast/slow values separately; Phase 2B ran 18 paired trials | Yes | No | No | Yes | No change established |
| **A4** | T3 gate: 2 of 3 macro regimes; Section 11.6 defines five | Phase 2B applied 2 of 3 observable OOS regimes (M3-M5) | Partial | No | No | Yes | No change established; T3 gate fails on the three observable OOS regimes; no finding on a five-regime reading |
| **A5** | Short gold often costs more; “especially shorts” | Tested model: long swap -0.126/oz/day, short -0.046/oz/day; long costs more | No | Yes | No | Yes | No change established |
| **A6** | T2 drawdown gate >25%; basis unspecified | -21.4% compounded (PASS) vs -30.2% constant-risk | Partial | No | No | Yes | No verdict change; gate result is basis-sensitive |
| **A7** | Low trade count -> INCONCLUSIVE; failed gates -> FAIL | Phase 2B treated INCONCLUSIVE as controlling | Partial | No | Yes | Yes | No change established; verdicts preserved |
| **A8** | T1 2-10 trades/month; T2 2-6 flips/year; T2 effective sample 50-130 | T1 ~340/year; T2 ~1.07/year and 20 trades | No | No | Yes | Yes | No change established |
| **A9** | E1 = replicated across independent samples, markets and methods | Arithmetic and single-broker observations also graded E1 | No | No | No | Yes | No change established |
| **A10** | 10-30 point spread; USD 0.27 round-trip example | Measured Dukascopy median USD 0.418; p95 USD 0.677 | No | Yes | No | Yes | No change established |
| **B1** | Cost row should cite the cost section | Section 8.0 cites Section 5.8 | Partial | No | No | Yes | No change established |
| **B2** | “Offset by transaction costs” | Text says “offset by low transaction costs” | No | No | No | Yes | No change established |
| **B3** | Consistent E2 grading for gold technical rules | E2/E3 in summary; E2 in detail and ledger | No | No | No | Yes | No change established |
| **B4** | Distinct MAR and Calmar definitions | Both defined as CAGR / maximum drawdown | No | No | No | Yes | No change established |
| **B5** | All quantitative figures labelled illustrative or arithmetic | Document contains sourced historical and industry figures | No | No | No | Yes | No change established |
| **B6** | Unambiguous T3 bear-market gate | Gate wording admits two readings | No | No | No | Yes | No change established |
| **B7** | v0.2 proposes no protocol change | v0.2 added reporting-template and governance text | Partial | No | No | Yes | No change established |
| **C1** | T2 first, T3 second, T1 conditional (Phase 2A Section 10.1) | Owner selected T1 -> T2 -> T3 in conversation; repository records T1-first | Yes | No | No | Yes | No change established |
| **C2** | Exness MT5 real ticks primary; Dukascopy cross-check | Dukascopy primary; MetaQuotes demo cross-check | Yes | Yes | No | Yes | No change established |
| **C3** | M1/real-tick execution; MT5 tester preferred | Python bar simulator; M15/H1/D1 bars; OHLC stop approximation | Yes | Partial | Partial | Yes | No change established; T1 magnitude approximate |
| **C4** | LBMA PM fix cross-check | No LBMA PM fix check reported | Yes | No | No | Yes | No change established |
| **C5** | COMEX GC futures cross-check | Not run; single instrument | Yes | No | No | Yes | No change established |
| **C6** | Four controls, including 60/40 and always-long | Buy-and-hold and random entry only. 60/40: gold-only data. Always-long: T2 had no volatility target; a T3-specific definition is not established | Yes | No | No | Yes | No change established |
| **C7** | Actual broker swap schedule | Current MT5 demo schedule applied to 2004-2026 | Yes | Yes | No | Yes | No change established |
| **C8** | T4 14-test descriptive ablation | Not run; Phase 2B execution rationale recorded in the final review | Yes | No | No | Yes | No change established |
| **C9** | Phase 1 runtime symbol layer required | Python simulator used fixed specifications; neither direct runtime use nor derivation from the Phase 1 layer is established | Yes | No | No | Yes | No change established |
| **C10** | Required `Proposed Protocol Change` section | Deviations disclosed in Sections 7-8, not in the required section | Yes | No | No | Yes | No change established |

### 4.3 Impact summary

- **No Phase 2B numerical result or verdict was recalculated for this errata.**
- The items with the clearest effect on cost realism are A5, A10, C2 and C7.
  None of them changes a recorded verdict; they change how the existing results
  should be interpreted.
- The item with the clearest effect on statistical power is A8. The Phase 2B
  trade counts were far below the Phase 2A T2 expectation; the pre-registered
  100-trade rule correctly produced INCONCLUSIVE.
- The item with the clearest effect on a specific gate is A6. T2’s drawdown gate
  passes on the compounded basis and would fail on the constant-risk basis. The
  existing INCONCLUSIVE verdict is preserved either way.
- The item with the clearest governance effect is C1. The owner’s execution-order
  decision is recorded in the project conversation but was not found as a
  pre-test repository commit.
- The item with the clearest traceability effect is C10. The required
  `Proposed Protocol Change` section is absent or insufficient, even though the
  deviations themselves are disclosed in the final review.

---

## 5. Final verdict preservation

The existing Phase 2B verdicts are recorded here exactly as stated in the Phase
2B Final Review. They are not recalculated, upgraded or downgraded by this
errata.

| Family | Verdict | Recorded basis |
| --- | --- | --- |
| **T1** | **FAIL** for the tested implementation/configurations | OOS Sharpe -1.787; OOS profit factor 0.734; OOS net USD -206,352; 6,353 full-sample trades and 2,823 OOS trades; negative at 1.0x, 1.5x and 2.0x costs and across the OOS regimes/subperiods. |
| **T2** | **INCONCLUSIVE** | OOS Sharpe 0.374; OOS profit factor 4.436; OOS net USD 40,052; 20 full-sample trades and 13 OOS trades; below the 100-trade power threshold; OOS maximum drawdown -21.4% compounded and -30.2% constant-risk. |
| **T3** | **INCONCLUSIVE** | OOS Sharpe 0.147; OOS profit factor 1.452; OOS net USD 15,905; 35 full-sample episodes and 19 OOS episodes; below the 100-episode power threshold; OOS maximum drawdown -49.2%. |

**No strategy is promoted.** No family is PASS or CONDITIONAL. No parameter set
is carried forward as a candidate. No live, demo or MQL5 implementation is
approved by this errata.

The T1 verdict is a rejection of the tested implementation/configurations, not
proof that every trend-following approach fails on gold. The T2 and T3 verdicts
are INCONCLUSIVE, which is not a soft pass. This errata does not change those
scopes.

---

## 6. Lessons and safeguards for Phase 3A onward

The following are recommendations for future phases. They are not retroactive
approvals and do not imply that the controls existed in Phase 2B.

| # | Safeguard | Practical implementation |
| --- | --- | --- |
| 1 | **Explicit owner approval and execution order recorded in-repository before a test begins** | Commit a short decision record naming the approved candidate order, the date/session of approval, and any override of a research recommendation. Do not rely on a conversation record alone. |
| 2 | **Trial counts and parameter grids reconciled mechanically** | Maintain a machine-readable grid file and generate the trial count from it. Reconcile the count against the pre-registration before running. Treat sensitivity runs as a separate, clearly labelled category. |
| 3 | **Data-source hierarchy and fallback approvals recorded before testing** | State the primary source, the approved fallback, the approval, and the consequences. Record the fallback as a protocol change, not as an undocumented substitution. |
| 4 | **Execution model and fill assumptions disclosed** | State whether the test uses real ticks, M1 OHLC, bar OHLC or another model; how stops/trails are resolved; how gaps are filled; and what is approximate. |
| 5 | **Historical spread, commission, swap and slippage assumptions separately identified** | Report each cost component separately. Distinguish measured data from testing assumptions. Do not present current broker settings as verified historical costs. |
| 6 | **Required benchmark and control checklist completed** | List every required benchmark/control, mark it implemented, missing or not applicable, and record the reason. A missing control must never be reported as a pass. |
| 7 | **Statistical power and verdict precedence defined in advance** | State the minimum trade/episode count, the power logic, and which rule controls when a candidate both fails an economic gate and has insufficient observations. |
| 8 | **Every deviation logged with approval, rationale and impact** | Use a single deviation table with the deviation, the approval, the reason, the affected trials/results, and whether it changes interpretation. |
| 9 | **Phase closure includes a protocol-deviation section** | The closure record must contain a `Proposed Protocol Change` or equivalent section, even when the conclusion is that no change was approved. |

Additional practical controls:

- Freeze the pre-registration document hash and line count at the start of the
  phase, and record the hash in the closure document.
- Keep a “planned versus executed” table for data source, execution model,
  controls, trials and cost assumptions.
- Do not silently edit a frozen pre-registration. Corrections belong in a
  separate errata record.
- Do not describe a conversation-level decision as a repository commit. If the
  decision matters to the test, commit a written record before the test.
- When a required control is missing, state the effect on interpretation
  explicitly and preserve the existing verdict rather than inventing a
  replacement result.

---

## Appendix A. Source and traceability map

| Item | Path or reference | Status |
| --- | --- | --- |
| Phase 2A v0.2 | `Docs/Strategy/Phase-2A-Trend-Following-Research.md` | Preserved; 2,637 lines; 132,463 bytes; SHA-256 `475C8B8B72C5AD5D9845EAFC05ACA781C57BA6272063E1278F09A6B47F9A1697`; commit `04fc1c82e9e16c606ee56886c1cf5ad021fd289d` |
| Phase 2B closure | `Docs/Strategy/Phase-2B-Final-Review.md` | Frozen at `c226958b40df74f2e4d78efdbecad07d311cf3c4`; tag `v0.3-phase2b-frozen` |
| Phase 2B comparative report | `Research/Phase-2B/reports/Phase-2B-comparative-report.md` | Preserved in place |
| T1 report | `Research/Phase-2B/reports/T1-report.md` | Preserved in place |
| T2 report | `Research/Phase-2B/reports/T2-report.md` | Preserved in place |
| T3 report | `Research/Phase-2B/reports/T3-report.md` | Preserved in place |
| Data readiness | `Research/Phase-2B/reports/data-readiness.md` | Preserved in place |
| Phase 1 tag | `v0.2-phase1` -> `bf69e93239c9af589faf034e9f30cfd7f2b3f92e` | Unchanged |
| ROADMAP | `ROADMAP.md` | Unchanged; SHA-256 `3E205E3F74D9AC1AFAE1064F622B14F14B5C03E372ACD693E0CB5ED0A6605571` |

## Appendix B. Terminology

- **Fact:** Directly documented in the repository records listed above.
- **Owner decision (conversation):** A decision recorded in the project
  conversation. It is not described here as a repository commit unless a commit
  is explicitly identified.
- **Assumption:** A testing or modelling assumption, not a verified historical
  fact.
- **Recommendation:** A proposed control for future phases. It is not an
  approval and not evidence that the control existed in Phase 2B.
- **Not established in the available project record:** The exact evidence was
  not found in the reviewed repository records. This is not proof that the event
  did not occur.

## Appendix C. Errata change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-09 | Initial errata draft: records A1-A10, B1-B7 and C1-C10; preserves the Phase 2B verdicts; adds Phase 3A safeguards. |
