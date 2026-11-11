# Phase 3A - Breakout Research

> **DRAFT - NOT APPROVED**
>
> This document is a research draft. It has not been reviewed, approved or
> accepted by the project owner. It does not authorise implementation, EA
> changes, backtesting, optimisation, parameter selection, commit, tag or push.
> Nothing in it is a recommendation to trade.

Project: Gold EA
Document type: Research and candidate selection (draft)
Status: **DRAFT / NOT APPROVED** (v0.2)
Phase: 3A - Breakout research
Scope: XAUUSD, spot gold and gold futures breakout hypotheses
Out of scope: MQL5 implementation, EA modification, backtesting, optimisation,
parameter selection, live deployment

---

## 1. Document control

| Item | Value |
| --- | --- |
| Phase | 3A - Research |
| Version | 0.2 (revised draft) |
| Depends on | Phase 0 (environment), Phase 1 (execution and risk engine), Phase 2A/2B (trend-following research and closure) |
| Followed by | Phase 3B - controlled breakout backtesting (not yet authorised) |
| Instrument | XAUUSD spot / CFD, with COMEX gold futures as a reference market |
| Strategy family under review | Breakout |
| Deliverable | Evidence review, six family definitions, rule dimensions, failure modes, comparison matrix, testability requirements, shortlist and open questions |
| Code changes | None |
| EA changes | None |
| Files changed by this phase | This document only |
| Approval status | **NOT APPROVED** |
| Commit status | Not committed |

### 1.1 Why this document exists

The roadmap's Phase 3 asks one question: *does gold breakout behaviour provide a
better edge than the families already tested?* Phase 2A and Phase 2B answered
that question for trend following only. Phase 2B closed with T1 **FAIL**, T2
**INCONCLUSIVE** and T3 **INCONCLUSIVE**, and explicitly did not promote any
strategy. Breakout has not been tested on this project's data.

This document does four things before any code is written:

1. It fixes what "breakout" means for this project, so that six families are not
   conflated in later tests.
2. It separates the evidence by source class, because most public breakout
   material is not peer-reviewed and much of it is marketing.
3. It records the gold-specific microstructure facts that determine whether a
   breakout rule can survive costs.
4. It states which families, if any, are worth a controlled test, and what data
   and protocol that test would require.

It deliberately **does not** claim that any breakout strategy is profitable. No
breakout rule has been tested on this project's data. Every candidate is a
hypothesis with a proposed falsification test.

### 1.2 How to read the evidence grades

This document reuses the Phase 2A grading scheme, so the two research documents
can be read side by side. A grade describes **the state of published evidence**,
not the author's confidence in a trading outcome.

| Grade | Meaning | Typical basis |
| --- | --- | --- |
| **E1 - Established** | Replicated across independent samples, markets and methods; survives reasonable robustness checks. Safe to treat as background fact. | Multiple peer-reviewed studies, different data, consistent direction |
| **E2 - Supported** | Consistent evidence in good studies, but narrower sample, one methodology family, or known replication limits. | One strong study plus partial confirmation |
| **E3 - Mixed** | Credible studies disagree, or the effect exists only under specific conditions. | Contradictory peer-reviewed results |
| **E4 - Hypothesis** | Plausible mechanism, weak or indirect evidence, not established for this instrument. Must be tested, not assumed. | Theory, analogy, practitioner claims, small samples |
| **E5 - Not supported** | Evidence points against the claim, or the claim fails standard robustness tests. | Direct contrary evidence |

Two rules govern use of the grades:

- **A grade attaches to a claim, not to a paper or a website.** One study can
  support an E2 claim in one section and an E5 claim in another.
- **E4 does not mean "do not test".** It means "do not assume". A low grade is a
  reason to pre-register a clean test, not a reason to skip it.

### 1.3 Evidence classes used in this document

Because breakout is heavily marketed, the source class is stated separately from
the evidence grade.

| Class | What it is | How it is treated here |
| --- | --- | --- |
| **P - Peer-reviewed** | Journal articles, published conference papers, working papers with identifiable methods and data | Primary evidence. DOIs given where available. |
| **I - Professional / industry** | Exchange, central-bank, bullion-market and data-vendor publications | Used for market structure and contract facts, not for strategy profitability claims. |
| **N - Independent / non-peer-reviewed** | Public backtests, research blogs, theses, vendor studies | Reported as claims with their stated method and sample. Never treated as independently verified. |
| **A - Anecdotal** | Marketing posts, social-media claims, paid strategy articles, unsourced screenshots | Recorded only to show what is circulating. Not evidence. |

### 1.4 What this document is not

- It is **not** an approval to trade, implement or optimise breakout.
- It is **not** a claim that any family is profitable, or more profitable than
  trend following.
- It is **not** a substitute for a pre-registered Phase 3B protocol.
- It is **not** a revision of `ROADMAP.md`, Phase 1, Phase 2A, Phase 2B or the
  Phase 2 errata.

---

## 2. Executive summary

### 2.1 What the evidence says

1. **Channel breakout is the best-studied breakout family on futures, and its
   academic record is mixed rather than positive.** Broad commodity studies find
   positive net returns for some channel rules after costs, while studies that
   correct for data snooping across thousands of rules find that the apparent
   profitability largely disappears. The studies differ in data frequency,
   sample period and rule universe, so this is a tension to be tested rather
   than a settled verdict. This is **E2/E3**, and it is the single most
   important prior in this document. (Szakmary, Shen & Sharma 2010; Marshall,
   Cahan & Cahan 2008; Sullivan, Timmermann & White 1999; White 2000;
   Bajgrowicz & Scaillet 2012.)

2. **The cleanest gold-specific evidence within the channel-breakout literature is
   negative, but it is not a single-instrument study.** Anderson and Faff (2005)
   tested a dual moving average rule and a channel breakout rule across five
   futures markets, including COMEX gold, over 1990-1998. They found no
   statistically significant gross or net profit in any of the five markets;
   positive profits in four of the five were neither economically nor
   statistically significant. This is a small, old sample, so it is **E3**
   rather than E5, but it is direct evidence that must not be omitted.
   (Anderson & Faff 2005, DOI 10.1108/10309610580000677.)

3. **Opening-range breakout (ORB) has supportive peer-reviewed evidence in other
   markets, but not a clean gold result.** Holmberg, Lönnbark and Lundström
   (2013) found significant ORB returns on crude oil, driven mainly by the
   2001-2011 high-volatility period; Tsai et al. (2019) found positive
   after-cost returns for a timely ORB on five index futures, using in-sample
   parameter selection. Neither studies gold. This is **E4** for gold ORB.
   (Holmberg et al. 2013, DOI 10.1016/j.frl.2012.09.001; Tsai et al. 2019,
   DOI 10.1109/ACCESS.2019.2899177.)

4. **The independent, non-peer-reviewed record is mixed and cannot establish a
   break-even baseline.** The reviewed tests report a range of outcomes:
   profit factors below 1.0 after costs, a few positive out-of-sample periods,
   and one very small sample killed by its own pre-registered rule. Because the
   vendors use different instruments, samples, cost models and selection
   procedures, and because failures may be under-reported, these results are
   hypothesis-generating anecdotes, not a representative distribution of
   after-cost performance. This is **N-class evidence** only.

5. **Gold's intraday liquidity and volatility are strongly periodic.** Activity
   clusters around the London open, the London-New York overlap, the COMEX
   open and US macro releases. Spreads and volatility are therefore not
   constants, and a breakout rule's measured edge depends heavily on the clock.
   This is **E1/E2**. (Batten et al. 2017; Caporin, Ranaldo & Velo 2015; Cai,
   Cheung & Wong 2001.)

6. **The most fragile part of any breakout design is not the entry, it is the
   definition of the range and the treatment of false breaks.** Stop-order
   clustering around round numbers and recent extremes is documented in FX order
   flow, and stop cascades are a plausible mechanism there. Whether the same
   mechanism operates in gold, and how often it turns a breakout into a false
   break, is not established by the cited evidence. This is **E2** for the FX
   mechanism, **E4** for gold. (Osler 2003; Kaminski & Lo 2014.)

7. **No family in this document has passed a controlled test on this project's
   data.** The shortlist in Section 11 is a testing order, not a ranking of
   expected profitability.

### 2.2 What this document recommends

**Recommendation: do not select a winner. Prepare controlled tests for B4
(channel/Donchian), B2 (previous-day high/low) and, conditionally, B3
(London-session range breakout). Treat B1 (opening range) as a conditional
intraday test only if the data prerequisite is met. Treat B5
(volatility-compression) and B6 (volatility-band) as overlays or ablations, not
as standalone families.**

| Family | Short name | Recommendation | Reason |
| --- | --- | --- | --- |
| **B4** | Channel / Donchian breakout | **Primary test candidate** | Best academic coverage, lowest data requirement (daily bars), few parameters, directly falsifiable against data-snooping benchmarks |
| **B2** | Previous-day high/low breakout | **Primary test candidate** | Simple, objective level, cheap to compute, testable on daily and intraday bars; gold-specific evidence is indirect |
| **B3** | London-session range breakout | **Conditional test candidate** | Plausible session mechanism, but requires reliable intraday data, timezone handling and DST discipline |
| **B1** | Opening-range breakout | **Conditional intraday test** | Peer-reviewed support exists in other markets; gold-specific public evidence is non-peer-reviewed and mixed |
| **B5** | Volatility-compression breakout | **Overlay / ablation, not standalone** | The "compression precedes expansion" claim is a filter, not a complete strategy; risks post-hoc range selection |
| **B6** | Volatility-band breakout (Keltner/Bollinger) | **Overlay / ablation, not standalone** | Highly parameter-sensitive, overlaps B4, and public gold tests are negative after costs |

The ordering is justified by testability and by the strength of the prior, not by
expected return. Section 11 states the unresolved questions that must be answered
before any of these becomes a Phase 3B trial.

### 2.3 What would change this recommendation

- A data audit showing that only daily bars are reliable would remove B1 and B3
  from the shortlist and leave B4 and B2.
- A finding that the broker's XAUUSD history does not match any independent
  XAUUSD series would make all intraday conclusions conditional on a data-source
  decision, as happened in Phase 2B.
- A peer-reviewed gold-specific ORB study with a clean out-of-sample design
  would raise B1's prior, but would still not replace a Level C test.
- Evidence that gold breakout returns are concentrated in a single regime (for
  example, 2008-2012 or 2020-2022) would make regime-conditional design the main
  question rather than family selection.

---

## 3. Scope, definitions and non-goals

### 3.1 Instruments: futures, spot and CFD are not interchangeable

This distinction matters more for breakout than for slow trend following,
because breakout results are dominated by intrabar path, spread and execution.

| Instrument | What it is | Why it matters for breakout |
| --- | --- | --- |
| **COMEX gold futures** | Exchange-traded contracts: GC (100 oz), MGC (10 oz), 1OZ (1 oz). USD per troy ounce. Rolls between contract months. | Centralised price discovery, exchange volume, published settlement. The academic and public backtests mostly use futures. A futures result is not automatically a CFD result. |
| **Spot gold (XAU/USD)** | Over-the-counter unallocated gold quoted in USD per ounce; London OTC is the dominant venue by turnover. | 24/5 quoting, no single official tape, venue-dependent spreads. The LBMA Gold Price is a benchmark, not a tradable bid/offer. |
| **XAUUSD CFD** | A retail broker contract that tracks spot gold, with broker-defined spread, swap, stop level and contract size. | The EA actually trades this. Its history, spread and execution are broker-specific, and its intraday highs/lows can differ from futures and from another broker's XAUUSD. |

Three consequences follow and are applied throughout:

1. A breakout level computed from one instrument cannot be assumed to be the same
   level on another. Cross-instrument confirmation is a research question, not a
   design assumption.
2. A futures backtest with exchange fees is not a cost model for a CFD with
   spread and swap.
3. "Gold" in a public study must be read as the specific instrument that study
   used. Section 6 records this per source.

### 3.2 Definitions used in this document

| Term | Definition used here |
| --- | --- |
| **Range** | A price interval defined by a high and a low over a stated lookback or session, with an explicit start and end time and an explicit timezone. |
| **Breakout** | A trade signal generated when price crosses a stated boundary of the range, under a stated trigger rule. |
| **False breakout / whipsaw** | A breakout that moves beyond the boundary and then returns inside the range within a stated horizon. |
| **Confirmation** | Any additional condition required after the boundary cross before entry is allowed. |
| **Trigger** | The event that generates the order: intrabar touch, bar close beyond the level, or a stop order resting beyond the level. |
| **Entry** | The actual fill: market, stop, or limit, with a stated reference price and slippage assumption. |
| **Stop** | The initial risk exit, defined before entry. |
| **Exit** | The profit-taking, trailing, time-based or signal-based close. |
| **Session** | A named clock interval, always stated with its timezone and DST rule. |
| **Frequency** | Expected trades per unit time under the rule, before filtering. |
| **Direction** | Long-only, short-only or symmetric, and whether a trend or regime filter is applied. |

### 3.3 In scope

- Six breakout families, defined precisely enough to be implemented without
  discretion.
- The rule dimensions that every family must specify.
- A graded review of peer-reviewed, professional, independent and anecdotal
  evidence.
- Gold-specific intraday volatility, liquidity, session and news facts.
- Failure modes and the conditions under which a measured edge would be an
  artefact.
- A comparison matrix and a testing order.
- Data and protocol prerequisites for a future Phase 3B.

### 3.4 Explicit non-goals

- No MQL5 code, no EA modification, no indicator implementation.
- No backtest, no optimisation, no walk-forward run, no parameter grid search.
- No selection of a "best" family, timeframe, session or parameter set.
- No claim of profitability or of superiority over trend following.
- No change to `ROADMAP.md`, Phase 1, Phase 2A, Phase 2B, the Phase 2 errata,
  or any frozen tag.
- No commit, tag or push as part of this draft.

---

## 4. The six breakout families

The six families below are defined so that each is a distinct hypothesis. Two
families that differ only by a parameter value are not separate families. Two
families that use the same range but a different confirmation rule are separate
only if the confirmation is the thing being tested.

### 4.1 B1 - Opening-range breakout (ORB)

**Hypothesis.** The range formed in the first part of a trading session contains
information about the direction of the rest of that session; a sustained move
outside it predicts continuation.

**Range.** The high and low of a fixed opening window, for example the first 15,
30 or 60 minutes after a defined session open (COMEX/New York, London or Asia).

**Trigger.** Price trades through the opening-range high or low.

**Why it might work.** Order flow at the open reflects overnight information and
the resolution of pre-open orders. If the open is a period of price discovery,
the first sustained departure may signal the day's direction.

**Why it might fail.** The open is a plausible window for false breaks, because
liquidity and information arrive at the same time. A one-tick poke beyond the
range is not the same event as a close beyond it, and the difference is where
most of the cost and most of the apparent edge live. The "liquidity sweep"
mechanism is documented mainly in FX, so for gold it is a hypothesis to test,
not a measured fact.

**Key ambiguity.** "Opening range" is meaningless without a stated session and
timezone. New York, London and Asia opens produce different ranges on the same
day.

### 4.2 B2 - Previous-day high/low breakout (PDH/PDL)

**Hypothesis.** The prior session's high and low are salient reference levels;
a sustained break of either level predicts continuation in that direction.

**Range.** The high and low of the previous completed trading day, defined by an
explicit daily boundary (for example 22:00-to-22:00 server time, or the COMEX
settlement-to-settlement day).

**Trigger.** Price trades through the prior high or prior low.

**Why it might work.** The levels are widely watched, are cheap to compute, and
can act as coordination points for stop and breakout orders. The transferable
evidence is about attention, not direction: Mizrach and Weerts (2009) find that
turnover rises on n-day highs and lows in US equities. Their return evidence
points the other way. In 849 NYSE/NASDAQ stocks over 1993-2003, they report
reversal after n-day highs and abnormal positive returns after n-day lows, not
continuation. That is equity-market reversal evidence and must not be cited as
support for a gold PDH/PDL continuation edge.

**Why it might fail.** Widely watched levels may also attract false breaks; the
stop-order mechanism is documented mainly in FX (Section 6.1.4) and is an
analogy for gold. The prior day's range is a single observation, so it carries
little information about the current day's volatility.

**Key ambiguity.** "Day" is a convention, not a fact. Broker day, exchange day and
UTC day produce different highs and lows.

### 4.3 B3 - Session-range breakout (Asian range / London open)

**Hypothesis.** A quiet session range (typically Asia) followed by the arrival of
a more liquid session (London or New York) produces a directional resolution;
the first sustained break of the quiet range predicts the active session's
direction.

**Range.** The high and low of a named quiet window, for example 00:00-07:00
London time, or the Asian session defined in Tokyo hours.

**Trigger.** Price breaks the range after the active session opens.

**Why it might work.** Liquidity and information arrival change discretely at
session opens. A range built in low-liquidity hours may be more likely to be
broken when the dominant venue opens.

**Why it might fail.** The London open is a plausible false-break window; two
non-peer-reviewed gold studies report a high rate of two-sided range breaks
around it (Section 6.3). Those are vendor and practitioner claims, not
controlled evidence. DST shifts the clock relative to the market, so a fixed
server-time window silently changes the economic event being traded.

**Key ambiguity.** "Asian session" is not a single clock interval across venues,
and London/New York DST transitions do not occur on the same dates.

### 4.4 B4 - Channel / Donchian breakout

**Hypothesis.** A move beyond the highest high or lowest low of the last N bars
signals the start of a directional move that persists long enough to cover costs.

**Range.** The high and low of the last N completed bars (for example N = 20, 55
or 100), on a stated timeframe.

**Trigger.** A bar close beyond the channel, or an intrabar trade through it,
depending on the variant.

**Why it might work.** It is the simplest formalisation of trend inception and
has been studied extensively in futures. Szakmary, Shen and Sharma (2010)
report positive mean excess returns net of transaction costs in at least 22 of
28 commodity futures for all parameterisations of the dual moving average and
channel strategies they implement. The study uses monthly data over 48 years and
pooled tests across markets; it is not a single-market gold result.

**Why it might fail.** The same literature that reports gross profitability also
shows that it weakens sharply once data snooping and realistic costs are handled
(Marshall et al. 2008; Sullivan et al. 1999). On COMEX gold, Anderson and Faff
(2005) found no significant profit over 1990-1998.

**Key ambiguity.** "N bars" is a free parameter. The family is only testable if N
is pre-registered or the entire grid is reported with a multiple-testing
correction.

### 4.5 B5 - Volatility-compression breakout

**Hypothesis.** Periods of unusually low range or volatility are followed by
disproportionate expansion; entering on the expansion captures a move larger
than the cost of being early.

**Range.** A compression condition, for example the narrowest range in seven
bars (NR7), an inside day, a Bollinger-band squeeze, or ATR below a stated
percentile over a lookback.

**Trigger.** A break of the compression bar's high or low, or of the compression
period's range.

**Why it might work.** Volatility clusters and mean-reverts; low realised
volatility is a documented precursor of expansion in many markets.

**Why it might fail.** The compression condition is a filter on B1-B4, not a
standalone entry. Testing it as a family risks selecting the compression
definition after seeing which one worked, which is textbook data snooping.

**Key ambiguity.** "Compression" has no canonical definition. The family should
therefore be treated as an overlay applied to a primary family, with the overlay
pre-registered.

### 4.6 B6 - Volatility-band breakout (Keltner / Bollinger)

**Hypothesis.** A close outside a volatility-scaled band (for example a Keltner
channel or a Bollinger band) signals a directional move strong enough to persist.

**Range.** A moving average plus or minus a multiple of a volatility measure
(ATR for Keltner, standard deviation for Bollinger).

**Trigger.** A bar close outside the band, or a re-entry after a close outside.

**Why it might work.** Scaling the boundary by volatility adapts the trigger to
market conditions and avoids a fixed price distance that is too tight in high
volatility and too wide in low volatility.

**Why it might fail.** It is a repackaging of a channel breakout with two extra
parameters (lookback and multiplier), and public gold tests of Keltner variants
report no edge after costs. The extra parameters increase the multiple-testing
burden without adding a distinct economic mechanism.

**Key ambiguity.** Band width and lookback interact; a grid over both is a large
search space and must be deflated accordingly.

### 4.7 What is deliberately excluded

- **News-event breakout** as a standalone family: it requires an event calendar,
  a surprise measure and a latency model that this project does not have. It is
  treated as a risk condition in Section 7.4, not as a candidate.
- **Tick-level liquidity-sweep reversal** as a breakout: it is a mean-reversion
  hypothesis in breakout clothing, and belongs to Phase 4.
- **Multi-day pattern breakouts** (triangles, flags, head-and-shoulders) as
  standalone families: the pattern definitions are discretionary and fail the
  "implementable without judgement" test. They may appear only as a
  pre-registered geometric rule.

---

## 5. Rule dimensions every candidate must specify

A breakout claim is not testable until all of the following are fixed. This list
is the minimum specification for any Phase 3B trial.

### 5.1 Range definition

| Dimension | Options | Why it matters |
| --- | --- | --- |
| **Lookback type** | Session window, calendar day, N bars, compression condition | Changes the hypothesis, not just the parameter |
| **Window length** | 15/30/60 min, N = 10/20/55/100 bars | Directly controls trade frequency and noise |
| **Bar boundary** | Bar open/close convention, completed vs forming bar | A forming-bar range repaints; a completed-bar range does not |
| **Inclusion rules** | Does the triggering bar count in the range? Are gaps included? | Can change the level by a full bar |

### 5.2 Timezone and DST

Every session-based family must state:

- the reference timezone (UTC, London, New York, or broker server time);
- the DST rule for each venue involved;
- how the window is mapped when London and New York DST dates differ;
- whether the window is fixed in local time (economically meaningful) or fixed
  in server time (reproducible but drifts against the market).

A fixed server-time window is the most common silent error in public breakout
tests. It is reproducible, but it changes the economic event by one hour for
several weeks each year. Both choices must be tested, not assumed.

### 5.3 Trigger

| Trigger | Definition | Main risk |
| --- | --- | --- |
| **Intrabar touch** | Any trade at or beyond the level | Maximises false breaks and slippage; needs tick or M1 data |
| **Bar close beyond** | A completed bar closes beyond the level | Fewer signals, later entry, easier to test |
| **Stop order beyond** | A resting stop at level plus buffer | Fill assumes liquidity at the level; slippage and gaps matter |
| **Close plus buffer** | Close beyond level by k ticks or k × ATR | Adds a parameter and reduces false breaks |

### 5.4 Entry

- Order type: market on close, market on next open, stop, or limit on retest.
- Entry price reference: close of signal bar, next bar open, or the level itself.
- Slippage assumption and whether it is spread-aware.
- Whether entry is allowed in the same bar as the range is formed.

### 5.5 Confirmation

Confirmation must be defined before the test. Common variants:

- **Close confirmation:** the signal bar closes beyond the level.
- **Retest confirmation:** price returns to the level and holds.
- **Second-bar confirmation:** the next bar also closes beyond the level.
- **Volume confirmation:** breakout bar volume exceeds a stated threshold. This
  is unreliable on CFD/spot data, where volume is broker-specific or absent.
- **Trend filter:** only trade breakouts aligned with a higher-timeframe trend.
- **Time filter:** only trade inside a named session window.
- **Volatility filter:** only trade when ATR or realised volatility is in a
  stated range.

Each confirmation added is a degree of freedom. The protocol must count them.

### 5.6 Stop

| Stop type | Definition | Consideration |
| --- | --- | --- |
| **Opposite side of range** | Stop at the range low for a long, range high for a short | Wide in volatile ranges; risk varies per trade |
| **ATR multiple** | Stop at entry minus k × ATR | Constant risk in volatility units; k is a parameter |
| **Fixed distance** | Stop at entry minus a fixed USD/point distance | Ignores volatility; likely to be too tight or too wide |
| **Structure stop** | Stop beyond a recent swing | Requires a swing definition; can be discretionary |
| **Time stop** | Exit after a stated number of bars | Not a price stop; changes the return distribution |

Stop placement may interact with the clustering of stop orders around round
numbers and recent extremes documented in FX order flow (Osler 2003). If a
similar mechanism exists in gold, a stop just beyond the range is not a neutral
choice; that is a plausible mechanism, not a measured gold result.

### 5.7 Exit

- Fixed R multiple (for example 1R, 2R, 3R).
- Trailing stop (ATR or channel based).
- Opposite signal.
- Session close or time stop.
- Partial exits.

Exit choice changes the win rate and the payoff ratio jointly, so a strategy
cannot be judged on win rate alone.

### 5.8 Frequency and direction

- Expected trades per month and per year, before and after filters.
- Minimum trade count required for the planned statistical test.
- Long-only, short-only or symmetric.
- Whether a trend, volatility or session filter is applied, and whether it is
  counted as part of the family or as a separate overlay.

---

## 6. Evidence review

The review is split by source class. Within each class, the instrument, sample
and method are stated, because a result on index futures is not a result on gold.

### 6.1 Peer-reviewed evidence

#### 6.1.1 Channel breakout on commodities and gold

**Szakmary, Shen and Sharma (2010)**, "Trend-following trading strategies in
commodity futures: A re-examination", *Journal of Banking & Finance* 34(2),
409-426. DOI: 10.1016/j.jbankfin.2009.08.004.

- Uses a monthly dataset spanning 48 years and 28 commodity futures markets.
- Reports that all parameterisations of the dual moving average crossover and
  channel strategies they implement yield positive mean excess returns net of
  transaction costs in at least 22 of the 28 markets. The authors report that
  pooled results are statistically significant and robust to their data-mining
  adjustments.
- This is **E2** for "channel breakout has historically paid in a broad
  commodity panel". It is not a single-market gold result, the data are monthly
  rather than intraday, and the result is pooled across markets. It does not
  establish that a specific gold rule at retail costs would be profitable.

**Marshall, Cahan and Cahan (2008)**, "Can commodity futures be profitably traded
with quantitative market timing strategies?", *Journal of Banking & Finance*
32(9), 1810-1819. DOI: 10.1016/j.jbankfin.2007.12.011.

- Tests 7,846 trading rules across 15 major commodity futures.
- Uses two bootstrapping methodologies and accounts for data-snooping bias.
- Concludes that quantitative market timing is not consistently profitable
  across the 15 series; the data-snooping-adjusted tests do not support a
  general profitability claim.
- The precise number of markets in which a particular rule survives depends on
  the test and the rule; the paper's headline conclusion is "not consistently
  profitable", not "no rule ever worked".
- This is **E3/E5** for "a researcher can find a profitable commodity breakout
  rule by searching". It is the key counterweight to Szakmary et al., but the
  two studies differ in data frequency, sample period, rule universe and test
  design, so they should not be read as a direct contradiction.

**Anderson and Faff (2005)**, "Profitability of trading rules in futures
markets", *Accounting Research Journal* 18(2), 83-92.
DOI: 10.1108/10309610580000677.

- Tests a dual moving average rule and a channel breakout rule across five
  futures contracts - S&P 500, British pound, US T-bonds, COMEX gold and corn -
  using daily data over 1990-1998.
- Finds that the rules produced no statistically significant gross or net
  profits in any of the five markets; positive gross and net profits in four of
  the five markets were neither economically nor statistically significant.
- This is **E3** for gold channel breakout: direct evidence, but a short and
  dated sample, and only one rule family.

**Sullivan, Timmermann and White (1999)**, "Data-snooping, technical trading
rule performance, and the bootstrap", *Journal of Finance* 54(5), 1647-1691.
DOI: 10.1111/0022-1082.00163.

- Provides the canonical framework for correcting technical-rule searches for
  data snooping.
- Its substantive finding is that the best rules in a large search often do not
  survive the correction in the original long daily US equity-index sample.
- This is **E1** for the methodological claim, not for gold profitability; it
  is not a commodity or gold study.

**White (2000)**, "A reality check for data snooping", *Econometrica* 68(5),
1097-1126. DOI: 10.1111/1468-0262.00152.

- The Reality Check bootstrap for testing whether the best of many strategies
  beats a benchmark.
- This is **E1** methodology and should be mandatory in any Phase 3B grid.

**Bajgrowicz and Scaillet (2012)**, "Technical trading revisited: False
discoveries, persistence tests, and transaction costs", *Journal of Financial
Economics* 106(3), 473-491. DOI: 10.1016/j.jfineco.2012.06.001.

- Applies false-discovery-rate control to a large set of technical rules on a
  long US equity-index sample.
- Finds that few rules survive once false discoveries and costs are handled.
- This is **E2** for "the technical-rule universe is mostly false discoveries".
  It is not gold-specific.

#### 6.1.2 Opening-range and intraday breakout

**Holmberg, Lönnbark and Lundström (2013)**, "Assessing the profitability of
intraday opening range breakout strategies", *Finance Research Letters* 10(1),
27-33. DOI: 10.1016/j.frl.2012.09.001.

- Tests an ORB strategy on crude oil futures using a normal-distribution
  threshold.
- Finds significantly positive returns over the full sample and a higher success
  rate than a fair game.
- The result is driven mainly by the 2001-2011 high-volatility period.
- The paper's baseline construction assumes a zero bid-ask spread and zero
  commissions; it reports a transaction-cost sensitivity of about 0.04%
  one-way and 0.08% round trip. That cost treatment is lighter than a retail
  CFD model.
- This is **E2** for crude-oil ORB, **E4** for gold ORB.

**Tsai, Wu, Syu, Lei, Wu, Ho and Wang (2019)**, "Assessing the profitability of
timely opening range breakout on index futures markets", *IEEE Access* 7,
32061-32071. DOI: 10.1109/ACCESS.2019.2899177.

- Tests a "timely" ORB on five index futures, 2003-2013.
- Reports more than 8% annual return after costs.
- Selects parameters in-sample, so the out-of-sample claim is limited.
- This is **E3** for index-futures ORB and **E4** for gold.

**Mizrach and Weerts (2009)**, "Highs and lows: A behavioural and technical
analysis", *Applied Financial Economics* 19(10), 767-777.
DOI: 10.1080/09603100802199679.

- US equity-market study: 849 NYSE/NASDAQ stocks, daily data, 1993-2003.
- Finds that turnover rises on n-day highs and lows and is increasing in n.
- The return findings are contrarian, not continuation: reversal after n-day
  highs and abnormal positive returns after n-day lows for several trading days.
- It is not a gold study and not an intraday breakout study. It cannot be used
  as evidence for a gold PDH/PDL continuation edge.
- This is **E2** only for the behavioural claim that highs and lows attract
  attention and turnover; **not applicable** as evidence for the directional
  prediction in B2.

#### 6.1.3 Gold and precious-metals microstructure

**Batten, Lucey, McGroarty, Peat and Urquhart (2017)**, "Stylized facts of
intraday precious metals", *PLOS ONE* 12(4), e0174232.
DOI: 10.1371/journal.pone.0174232.

- Studies 5-minute gold, silver, platinum and palladium data from May 2000 to
  April 2015.
- Finds strong periodicity in returns, volatility, volume and bid-ask spread,
  linked to the opening and closing of major markets; the bid-ask spread is
  lowest when European markets are open.
- This is **E2** for the existence of session-driven periodicity.

**Caporin, Ranaldo and Velo (2015)**, "Precious metals under the microscope: A
high-frequency analysis", *Quantitative Finance* 15(5), 743-759.
DOI: 10.1080/14697688.2014.947313.

- Uses a trades-and-quotes database for spot gold, silver, palladium and
  platinum.
- Finds periodic patterns matching the trading hours of the most active markets,
  fat tails, asymmetry, volatility clustering and strong commonality in
  liquidity.
- Gold is the most liquid and least volatile of the four.
- This is **E2** for the microstructure facts and **E1** for "gold is not
  uniformly liquid across the day".

**Cai, Cheung and Wong (2001)**, "What moves the gold market?", *Journal of
Futures Markets* 21(3), 257-278.
DOI: 10.1002/1096-9934(200103)21:3<257::AID-FUT4>3.0.CO;2-W.

- Studies COMEX gold intraday volatility around 23 macro announcements.
- Employment, GDP, CPI and personal income announcements have the largest
  effects.
- This is **E2** for "scheduled US macro news moves gold intraday".

**Elder, Miao and Ramchander (2012)**, "Impact of macroeconomic news on metal
futures", *Journal of Banking & Finance* 36(1), 51-65.
DOI: 10.1016/j.jbankfin.2011.06.007.

- Documents the response of metal futures to macroeconomic surprises.
- Supports the view that news is a first-order driver of intraday metal
  volatility.

**Hauptfleisch, Putniņš and Lucey (2016)**, "Who sets the price of gold? London
or New York?", *Journal of Futures Markets* 36(6), 564-586.
DOI: 10.1002/fut.21775.

- Examines price discovery between London and New York.
- This is **E2** for "session location matters for price formation", which is
  directly relevant to B1 and B3.

#### 6.1.4 Stops, false breaks and liquidity

**Osler (2003)**, "Currency orders and exchange rate dynamics: An explanation
for the predictive success of technical analysis", *Journal of Finance* 58(5),
1791-1819. DOI: 10.1111/1540-6261.00588.

- Uses order-flow data from a large foreign-exchange dealer, not gold.
- Documents clustering of stop-loss and take-profit orders around round numbers
  and recent extremes, and reports stop cascades, in that FX dealer's order flow.
- This is **E2** for the FX mechanism; **E3/E4** for gold. It is an analogy, not
  direct evidence that gold breakouts fail, and it does not quantify how often
  a gold breakout is a stop cascade rather than a genuine continuation.

**Kaminski and Lo (2014)**, "When do stop-loss rules stop losses?", *Journal of
Financial Markets* 18, 234-254.
DOI: 10.1016/j.finmar.2013.07.001.

- Shows that stop-loss rules add value only under momentum or positive
  autocorrelation, and can hurt under mean reversion.
- This is **E2** and is a direct warning for breakout systems: the stop is part
  of the hypothesis, not a free risk control.

#### 6.1.5 Why the evidence is thin on gold breakout

**Park and Irwin (2007)**, "What do we know about the profitability of technical
analysis?", *Journal of Economic Surveys* 21(4), 786-826.
DOI: 10.1111/j.1467-6419.2007.00519.x.

- Surveys the technical-analysis literature and finds that early positive
  results are often weakened by data-snooping, ex-post rule selection and
  cost assumptions.
- This is **E2** for the general caution, not a gold result.

**Harvey, Liu and Zhu (2016)**, "… and the cross-section of expected returns",
*Review of Financial Studies* 29(1), 5-68. DOI: 10.1093/rfs/hhv059.

- Argues that a new factor in the cross-section of expected returns should clear
  a t-statistic hurdle above 3.0 rather than the conventional 2.0, because so
  many factors have been tested.
- This is **E1** for factor-research methodology. It is a conservative heuristic
  when applied to a single strategy backtest, not a formal threshold mandated
  for every trading rule. It is directly relevant to any breakout rule selected
  from a grid, but the exact hurdle and its justification belong in the Phase 3B
  protocol.

**Bailey and López de Prado (2014)**, "The deflated Sharpe ratio: Correcting for
selection bias, backtest overfitting and non-normality", *Journal of Portfolio
Management* 40(5), 94-107. DOI: 10.3905/jpm.2014.40.5.094.

- Provides a deflated Sharpe ratio that accounts for the number of trials,
  non-normality and selection.
- This is **E1** methodology and should be applied to any reported breakout
  Sharpe ratio.

### 6.2 Professional and industry evidence

These sources establish market structure and contract facts. They do not
establish that a breakout rule is profitable, and they are not used as if they
did.

**World Gold Council - Gold Market Primer: market size and structure.**

- Reports 2025 average daily gold turnover of about US$361bn.
- London OTC about US$180bn/day; on-exchange about US$174bn/day; COMEX about
  US$114bn/day; Shanghai Futures Exchange about US$51bn/day.
- Establishes that gold is a deep, multi-venue market, and that London OTC and
  COMEX futures are the dominant price-discovery venues.
- These are estimates assembled from multiple sources, not a single consolidated
  tape; they should be treated as approximate. The page does not give a separate
  ETF turnover figure, so none is quoted here.

**LBMA trade data, Q1 2025.**

- Gold average daily volume 48.36 million ounces, average daily value
  US$137.67bn.
- Establishes the scale of the London OTC market and supports the claim that
  spot gold liquidity is not the constraint for a retail-size order.

**CME Group contract specifications and liquidity notes.**

- GC is 100 troy ounces; MGC is 10 troy ounces; 1OZ is 1 troy ounce.
- MGC average bid/offer is about 2.01 ticks overall and about 1.98 ticks in
  Asian hours in Q2 2025.
- Asian hours account for about 42% of MGC volume and more than one third of GC
  volume in Q2 2025.
- Establishes contract sizes and the fact that micro gold spreads are wider than
  the headline GC market.
- The bid/offer figure is a period average, not a guarantee of an executable
  spread at a particular time.

**Crabel (1990), *Day Trading with Short Term Price Patterns and Opening Range
Breakout*.**

- The practitioner origin of much ORB and compression terminology.
- **N-class** as evidence: it is a trading book, not a controlled study. It is
  cited for the definition of the family, not for profitability.

**Clenow (2013), *Following the Trend*.**

- A practitioner treatment of channel/Donchian breakout and trend following.
- **N-class** as evidence; useful for implementation conventions, not for
  proving an edge.

### 6.3 Independent and non-peer-reviewed evidence

These sources are reported with their stated method and sample. They are **not**
independently verified, their code and data are not available to this project,
and their results must not be treated as replication.

None of the results below is a controlled replication. The vendors differ in
instrument (MGC, MYM, MCL, MNQ, XAUUSD), timeframe, sample period, cost model
and selection procedure. Several report only the best variant, and failures may
be under-reported. A profit factor below 1.0 in one test is therefore not
evidence that the family fails on gold, and a profit factor above 1.0 in another
is not evidence that it succeeds. The only defensible reading is that the public
record is mixed and that any candidate requires a pre-registered test on this
project's data.

#### 6.3.1 QuantReplay

QuantReplay publishes strategy tests on CME futures with commission, slippage
and an out-of-sample split. The site states that it publishes failures as well
as successes; that is a useful selection property, but it is still a
non-peer-reviewed vendor.

| Test | Instrument / bars | Sample | Reported result | Relevance |
| --- | --- | --- | --- | --- |
| **London breakout** | MGC, 5-minute | 2016-2026, 1,696 trades | In-sample profit factor 0.90 (about -0.05R); out-of-sample profit factor 1.29 (about +0.08R, 488 trades); 25/25 parameter settings profitable out of sample | Suggests the London window matters and that the result is period-dependent. Costs: US$0.75 commission each way plus one tick slippage. DST shifts fixed New York-time windows against London. |
| **Keltner channel breakout** | MGC, 15-minute | 2,121 trades, 2016-2026 | Out-of-sample profit factor 0.87; no edge after costs | Directly negative for B6 on gold. |
| **Previous-day high/low** | MYM (micro Dow), not gold | 1,094 trades | In-sample -0.14R, profit factor 0.78; out-of-sample -0.08R, profit factor 0.89; 0/16 settings profitable out of sample | Negative, but on a different instrument. Weak evidence for B2 on gold. |
| **Donchian breakout** | MCL (micro crude), not gold | 2,789 trades, 15-minute | Out-of-sample profit factor 0.79 | Negative, different instrument. |
| **Asia-range breakout** | MNQ, not gold | Not stated on the page | Out-of-sample profit factor 0.90 | Negative, different instrument. |

What this class supports: the claim that public breakout tests on gold are
sensitive to session, period and cost assumptions. What it does not support: a
claim that B1-B6 fail or succeed on this project's data.

The London result is the most striking entry in the table: 25 of 25 parameter
settings were reported profitable out of sample. That pattern is more consistent
with a period effect or a shared exposure than with 25 independent edges, and it
remains a vendor claim. The costs quoted are CME futures commissions and one
tick of slippage, not XAUUSD CFD spread and swap.

#### 6.3.2 BacktestingMax

BacktestingMax publishes multi-market tests with costs and two sub-periods. The
figures are vendor claims; the exact cost model is not independently verified.

- **London breakout:** 18 tests; 5 profitable; 4 profitable in both periods.
  Gold was only marginally positive on the 5-minute chart; stop orders were
  described as roughly break-even after half-spread. "Roughly break-even" is
  the vendor's summary, not a measured after-cost distribution.
- **New York open breakout:** 0 of 10 tests profitable. MGC lost 16.2% on the
  5-minute chart and 20.8% on the 15-minute chart. On report days, 4,834 trades
  produced -366.1R, versus +44.4R on non-report days. A one-hour-range variant
  made +16.1% / +9.5% on MGC, but the variant was selected after the fact and
  only 1 of 50 settings was profitable in both periods. The post-hoc variant
  should not be counted as evidence for the family.

What this class supports: scheduled US reports are a plausible confounder for
session breakout, and post-hoc variant selection can manufacture a positive
result. What it does not support: a general claim about gold ORB, or a precise
after-cost break-even level.

#### 6.3.3 CRTLAB

- XAU/USD, 5-minute data, 3 January 2017 to 19 October 2026.
- New York ORB: first break of the 09:30-09:45 New York range, stop at the
  other side, held to 16:00. About +0.12R, standard error about 0.04, over
  2,394 trades; about +0.09R when exited at 2R.
- Ranked 4th of 13 markets tested.
- Spread and slippage were excluded from the headline result.
- The standard error is reported by the vendor, not recomputed here.
- The +0.12R is gross of spread and slippage, so it cannot be read as an
  after-cost edge.

What this supports: a small gross effect may exist in the New York ORB on gold.
What it does not support: an after-cost edge, because the cost exclusion is
decisive for a strategy with a ~0.1R mean, and the result is one of 13 market
tests, so selection across markets is also a live concern.

#### 6.3.4 Delta Terminal

- XAU/USD spot, Dukascopy 5-minute data, 3 January 2023 to 3 August 2026; 923
  valid days, of which 742 are classified as normal days and 181 as US release
  days.
- The paper's "2,303-breakout" total is the count of break events over all 923
  days and both break definitions: 801 morning wick + 724 morning close + 390
  afternoon primary wick + 388 afternoon primary close. It is not the
  denominator for the 75.7% figure.
- The 75.7% statistic uses the **630 normal-day morning wick breaks** (a wick
  beyond the Asia high or low between 09:00 and 14:25, followed by an M5 close
  back inside within 30 minutes), a subset of the 801 morning wick breaks; the
  remaining 171 are outside the normal-day cell and are not separately tabulated
  in the source. The 95% interval is 72.2-78.9%. The parallel normal-day morning
  close-break cell is 571. The 630 denominator is the one reported for the
  headline statistic and is retained here.
- **Close** breaks were close to a coin flip.
- "Phantom" levels half a range-width away behaved similarly (76.0%), and
  afternoon breaks of the same range reverted 69.0% of the time, so the effect
  is not specific to Asia or to the morning.
- The 75.7% figure is a descriptive frequency, not a strategy return. The study
  does not report spread, slippage or a trading rule.
- The vendor reports that the first run was re-checked by three auditors; it is
  still a vendor publication, not peer-reviewed evidence.

What this supports: the trigger definition (wick vs close) is the dominant
design choice for Asia-range breakout, and wick-based entries are systematically
exposed to false breaks. It is gold-specific, but it is descriptive: it does not
show that a wick-entry rule loses money after costs.

#### 6.3.5 Open Market Journal

- Gold ORB over 7,948 London and New York sessions and 16 years.
- Overall resolved success rate about 32%.
- London: 47% of sessions swept both sides; New York: 22%.
- Conclusion: the session matters more than the ORB itself.
- "Resolved success" is the publisher's definition and is not independently
  verified.

Caveat: the page describes itself as "AI-assisted research and commentary". It is
**N-class** and must be treated as a hypothesis source, not as a verified study.

#### 6.3.6 untilnextsession

- London-open XAUUSD breakout, 2 January to 31 August 2026: 89 trades;
  +449.3 USD/oz after spread; about 1.5 standard errors versus a random-entry
  benchmark.
- A pre-registered 2-standard-error kill rule was not met, so the author killed
  the strategy.
- Very short sample.
- 89 trades is far below the provisional sample thresholds in Section 10.5; the
  +449.3 USD/oz is a point estimate after spread, not a statistically
  established edge.
- The author's decision to kill the strategy on a pre-registered rule is a model
  of discipline, not evidence that the strategy is profitable.

What this supports: a disciplined example of a pre-registered kill rule, and a
warning that a positive point estimate can be statistically indistinguishable
from noise.

#### 6.3.7 Sönnert (2015)

- Bachelor thesis, Umeå School of Business and Economics, Umeå University.
- Gold futures ORB, 2009-2014, daily high/low/open/close data from NYMEX.
- The thesis reports significantly positive ORB returns; the result is not
  independently reproduced here.
- Not peer-reviewed, student work, short sample, and the data are daily rather
  than intraday. The daily data mean the intrabar path and execution cannot be
  reconstructed, and the result cannot be treated as an after-cost backtest of
  an intraday rule.

What this supports: **E4** that gold ORB is worth testing. What it does not
support: a profitability claim.

### 6.4 Anecdotal evidence

- A paid Substack article titled "Insane Gold Breakout Strategy: 1.85 Profit
  Factor Over 28 Years" reports 104 trades on daily XAUUSD with a 1.85 profit
  factor and a 1.38% maximum drawdown. Execution details, data source and
  transaction costs are not disclosed in the public portion.
- This is **A-class**. It is recorded to show what is circulating, not as
  evidence. A 104-trade daily sample over 28 years is too sparse for the claimed
  precision, and the 1.38% maximum drawdown is not credible without stated
  position sizing, leverage and cost assumptions.

### 6.5 What the evidence review establishes

| Claim | Grade | Basis and qualification |
| --- | --- | --- |
| Channel breakout has historically paid in a broad commodity panel | E2 | Szakmary et al. 2010; monthly data, 28 markets, pooled; not a single-market gold result |
| Apparent commodity breakout profits often fail data-snooping corrections | E2/E3 | Marshall et al. 2008; Sullivan et al. 1999; White 2000; Bajgrowicz & Scaillet 2012; different samples and rule universes |
| Channel breakout on COMEX gold showed no significant profit in 1990-1998 | E3 | Anderson & Faff 2005; five-market study, not a standalone gold paper |
| ORB has positive evidence in crude oil and index futures | E2/E3 | Holmberg et al. 2013; Tsai et al. 2019; neither is gold |
| ORB has no clean peer-reviewed gold result | E4 | Absence of evidence, not evidence of absence |
| Gold intraday volatility, volume and spreads are session-periodic | E1/E2 | Batten et al. 2017; Caporin et al. 2015; Cai et al. 2001 |
| Stops cluster around salient levels and can cascade | E2 for FX; E4 for gold | Osler 2003; FX order-flow study, not gold |
| Stop rules add value only under momentum | E2 | Kaminski & Lo 2014; conditional on the return process |
| A new rule should clear a t-hurdle above 3.0 | E1 for factor research; heuristic for strategy tests | Harvey, Liu & Zhu 2016 |
| Reported Sharpe ratios should be deflated for trials | E1 | Bailey & López de Prado 2014 |

---

## 7. Gold-specific intraday volatility, liquidity, sessions and news

Breakout is a claim about the path of price through a level. Everything in this
section changes that path, and therefore changes whether a measured breakout
result is real or an artefact of the clock.

### 7.1 Volatility is periodic, not constant

Gold intraday volatility is not evenly distributed. It clusters around:

- the London open and the London morning;
- the London-New York overlap;
- the COMEX open and the US morning data window;
- the LBMA Gold Price auctions (10:30 and 15:00 London);
- scheduled US macro releases, especially employment, CPI, GDP and personal
  income (Cai et al. 2001).

Consequences:

- A fixed-distance breakout threshold is a different economic bet in Asian hours
  than in the New York overlap.
- ATR-scaled thresholds adapt, but introduce their own lookback and estimation
  error.
- Any comparison of breakout rules across sessions must report results by
  session, not pooled.

### 7.2 Liquidity and spreads are session-dependent

- Gold is the most liquid and least volatile of the major precious metals
  (Caporin et al. 2015).
- Liquidity commonality across precious metals is strong.
- Spreads widen in thin hours and around news; they do not scale linearly with
  volatility.
- CME micro gold (MGC) averages about 2 ticks bid/offer, and Asian-hour spreads
  are slightly wider.
- A retail XAUUSD CFD spread is not the CME spread. Phase 2B's testing
  assumptions included a D1 spread series with a median of USD 0.418/oz and a
  p95 of USD 0.677/oz. That series was derived from H1 bar spreads inside the
  22:00-to-22:00 session on the connected feed (MetaQuotes-Demo, not Exness); it
  is not a point-in-time quote and should not be treated as a verified
  historical cost.
- Phase 2B's swap assumptions were about -0.126/oz/day for longs and
  -0.046/oz/day for shorts, with triple swap on Wednesday. These were current
  settings, not a verified historical schedule.

Consequences:

- Cost as a fraction of the breakout distance is the binding constraint. A
  breakout rule that risks 0.5 × ATR can have a cost-to-risk ratio that makes a
  small gross edge untradeable.
- Intraday breakout frequency is highest exactly when spreads are widest
  (news), which is the worst combination for a naive test.

### 7.3 Sessions, timezones and DST

The relevant clocks are indicative, not definitions:

| Venue / event | Local time | UTC, normal winter weeks | UTC, normal summer weeks | Qualification |
| --- | --- | --- | --- | --- |
| Sydney open | about 07:00 Sydney | about 20:00 previous day (AEDT, UTC+11) | about 21:00 previous day (AEST, UTC+10) | Sydney DST is opposite to the Northern Hemisphere; the UTC time moves with Southern DST. |
| Tokyo open | 09:00 JST | 00:00 | 00:00 | Japan has no DST. |
| London open | 08:00 London | 08:00 (GMT) | 07:00 (BST) | A market convention, not an exchange-defined open for spot gold. |
| London session (full) | 08:00-16:30 London | 08:00-16:30 (GMT) | 07:00-15:30 (BST) | The full London session, not the London-New York overlap. A convention for spot gold, not an exchange-defined interval. |
| London-New York overlap | 13:00-16:30 London (08:00-11:30 New York) | 13:00-16:30 | 12:00-15:30 | The intersection of the full London session with a New York session taken as starting at 08:00 ET. Local London hours are unchanged in normal weeks; the UTC hours move with UK DST. |
| London-New York overlap, DST-mismatch weeks | 12:00-16:30 London (08:00-12:30 New York) | not applicable | not applicable | Under the DST rules in force since 2007, the US is on DST while the UK is not, so the offset is 4 hours, not 5. This affects roughly two weeks in March and one week in late October/early November; the overlap is 12:00-16:30 London and 12:00-16:30 UTC, 4.5 hours rather than 3.5. |
| COMEX/New York open | 08:20 ET | 13:20 (EST) | 12:20 (EDT) | COMEX floor/open outcry; Globex electronic trading is nearly 24 hours. |
| US data window | 08:30 ET | 13:30 | 12:30 | Most US macro releases; the calendar is not exhaustive. |
| LBMA Gold Price AM | 10:30 London | 10:30 | 09:30 | An auction, not a continuous quote. |
| LBMA Gold Price PM | 15:00 London | 15:00 | 14:00 | An auction, not a continuous quote. |

The full London session and the London-New York overlap are different windows.
The full session is 08:00-16:30 London. The overlap is only the part of that
session that coincides with a New York session taken as 08:00-17:00 ET:
13:00-16:30 London (08:00-11:30 New York) in normal weeks, not 08:00-16:30
London. Under the rules in force since 2007, UK DST is nested inside US DST, so
the mismatch weeks are always US-on-DST and UK-on-GMT, and the overlap runs from
12:00 to 16:30 London (12:00-16:30 UTC), 4.5 hours rather than 3.5. For data
before 2007, the US dates were different (April to late October), so the
mismatch windows and the direction of the shift must be computed from the
historical rules rather than the current ones.

DST qualifications:

- Since 2007, the US starts DST on the second Sunday in March and ends on the
  first Sunday in November; the UK/EU starts on the last Sunday in March and
  ends on the last Sunday in October. For roughly two weeks in March and one
  week in late October/early November, the London-New York offset is 4 hours
  rather than 5. For data before 2007, the US dates were different (April to late
  October), so the mismatch windows must be computed from the historical rules.
- A window fixed in server time is not the same as a window fixed in London or
  New York local time. The difference is one hour for those weeks and can change
  which session a trade belongs to.
- "Asian session" is not a single clock interval: Tokyo, Hong Kong, Singapore and
  Shanghai have different hours and holidays. "London session" and "New York
  session" are conventions, not exchange-defined intervals for spot gold.
- The table is indicative and should not be hard-coded. The protocol must use a
  named timezone library, state the DST rule, and report results for the
  DST-mismatch weeks separately or exclude them under a pre-registered rule.

Consequences:

- A "London open" rule fixed in server time drifts by one hour for the weeks
  between the US and UK DST changes, and a "New York open" rule has the same
  problem in the other direction.
- A test that spans several years must either fix the window in local time or
  report the DST-shift period separately; it must not silently pool both.
- A Sydney session rule must also handle Southern Hemisphere DST, which moves
  in the opposite direction to the Northern Hemisphere; Tokyo has no DST.

### 7.4 News and event risk

- Scheduled US macro releases are the largest identified intraday volatility
  driver in COMEX gold (Cai et al. 2001; Elder et al. 2012).
- BacktestingMax's New York open test reports that report days accounted for
  -366.1R versus +44.4R on non-report days. This is a vendor claim, not an
  independently verified result, but the difference is large enough that pooling
  the two without a pre-registered news policy would be misleading.
- Unscheduled geopolitical and central-bank news is not in any calendar and
  cannot be filtered ex ante.

Consequences:

- The protocol must define a news calendar and a policy: exclude, include, or
  report separately.
- The policy must be fixed before the test. Choosing it afterwards is a
  degree of freedom.
- A breakout rule that relies on news-driven continuation is a different
  hypothesis from one that trades quiet-session expansion.

### 7.5 Gaps, rolls and contract conventions

- Futures contracts roll; a continuous back-adjusted series can contain
  artificial gaps at the roll.
- Spot/CFD data have weekend gaps and broker-specific session boundaries.
- A daily high/low computed on a rolled futures series may not equal the level a
  spot trader sees.
- The Phase 2B data audit found that the connected feed was MetaQuotes-Demo
  rather than Exness, and that the intraday history did not cover the
  pre-registered period. That limitation applies equally to Phase 3A.

### 7.6 What this section implies for test design

1. Breakout results must be reported by session and by volatility regime, not
   only pooled.
2. Costs must be session-aware and must include spread, slippage and, for
   multi-day holds, swap.
3. The trigger definition (wick vs close) must be fixed in advance, because it
   changes the false-break rate more than most parameter choices.
4. News days must be handled by a pre-registered rule.
5. The data source and instrument must be named in every result table.

---

## 8. Failure modes

The following are the ways a breakout backtest can look good and be wrong, or
look bad for the wrong reason. Each is a required check in Phase 3B.

### 8.1 False breakouts and whipsaw

The dominant failure mode in the public tests reviewed here. Price crosses the
level, triggers entry, and returns inside the range. The result is a small loss
plus costs, repeated often. Two non-peer-reviewed gold studies report two-sided
range-break rates of roughly 20-47% depending on session (Section 6.3); these are
vendor and practitioner estimates, not independent measurements.

Mitigations: close confirmation, buffer, retest, time filter, session filter.
Each mitigation is a parameter and must be counted.

### 8.2 Stop hunting and liquidity sweeps

Stops cluster beyond salient highs and lows in FX order flow (Osler 2003). A
breakout entry placed exactly at the level may therefore be exposed to a sweep
that takes out both the breakout traders and the protective stops before the
real move. For gold this is a plausible mechanism analogy, not a measured gold
result; no gold-specific study in this review quantifies it.

Mitigation: place the trigger beyond the level by a buffer, or require a close.
Both change the hypothesis.

### 8.3 Spread and slippage on the trigger bar

The trigger bar is often the widest-spread, fastest-moving bar. A backtest that
fills at the level with a fixed spread underestimates cost. A backtest that fills
at the close of the signal bar may be optimistic or pessimistic depending on the
next open.

Mitigation: use bid/ask data where available, model slippage as a function of
volatility, and stress costs at 1.5× and 2× the baseline.

### 8.4 Timezone and DST drift

A fixed server-time window changes the economic event for weeks each year. This
can create or destroy an apparent edge without any change in the market.

Mitigation: define windows in the relevant local timezone; test both fixed-local
and fixed-server variants; report the DST-shift subperiod.

### 8.5 Range definition mining

Choosing the lookback, session, or compression definition after seeing results
is data snooping. It is especially likely in breakout research because the
"range" is intuitively adjustable.

Mitigation: pre-register a small set of range definitions, report all of them,
and apply a multiple-testing correction across the full set.

### 8.6 Regime dependence

Breakout profitability is plausibly concentrated in high-volatility, trending
regimes. Holmberg et al. (2013) found that their crude-oil result was driven by
2001-2011. A full-sample average can therefore hide a strategy that only works
in a regime that may not recur.

Mitigation: report results by volatility regime and by subperiod; do not select
the regime after the fact.

### 8.7 Survivorship and publication bias

Public backtests are more likely to be published when they show a positive
result, and paid strategy articles have an incentive to show a high profit
factor. The independent sources in Section 6.3 are not a random sample of all
tests that were run.

Mitigation: treat the independent record as illustrative, not as a meta-analysis;
weight peer-reviewed evidence above it.

### 8.8 Instrument mismatch

A result on MGC is not a result on XAUUSD CFD. Contract size, tick size, spread,
session hours and roll behaviour differ.

Mitigation: state the instrument in every table; do not pool futures and CFD
results.

### 8.9 Cost model error

Phase 2B documented that its spread series were bar-level averages derived from
H1 bars, and that its swap assumptions (about -0.126/oz/day long and
-0.046/oz/day short, triple swap Wednesday) were current settings, not verified
historical costs. The same errors are easy to repeat in Phase 3A.

Mitigation: separate spread, commission, slippage and swap; stress each; state
which are measured and which are assumptions.

### 8.10 Exit-driven results

A breakout entry with a 5R target and a wide stop can show a low win rate and a
positive expectancy, or the reverse. Reporting only win rate or only profit
factor hides the trade-off.

Mitigation: report the full distribution, average R, profit factor, expectancy,
maximum drawdown and the R-multiple histogram.

### 8.11 Time-stop and session-close artefacts

Closing all trades at a fixed session time can manufacture a result if the exit
time is chosen after the fact. It also interacts with DST.

Mitigation: pre-register the exit time and test alternatives.

### 8.12 Multiple testing across six families

Testing six families with several variants each is a large search. A single
"significant" result at t = 2.1 is not credible without a deflation adjustment
(Harvey et al. 2016; Bailey & López de Prado 2014).

Mitigation: count every trial, report the full search, and apply a Reality Check
or deflated Sharpe ratio.

---

## 9. Candidate comparison matrix

Scores are qualitative and are about **testability and prior evidence**, not
expected profitability. Each row uses a 1-5 ordinal scale, where 5 is the most
favourable for a controlled test and 1 the least.

### 9.1 Scoring rubric

| Score | Meaning |
| ---: | --- |
| **5** | Strong, direct, replicated or unambiguous; low risk. |
| **4** | Good, but with a known limitation. |
| **3** | Moderate or mixed. |
| **2** | Weak or indirect. |
| **1** | Absent, very weak, or high risk. |

For rows labelled "higher = easier", "higher = less sensitive", "higher =
fewer", "higher = less risk" or "higher = more freedom", the score has already
been oriented so that 5 is always the better testability outcome. The
**Overall testability** row is the unweighted arithmetic mean of the ten rows.
It is an orientation aid, not a decision rule or a measurement. The scores are
the author's judgements and should be reviewed independently; a low average does
not disqualify a family that tests a distinct hypothesis, and a high average does
not imply profitability. A weighted score would change the ranking, and no
weights have been agreed.

| Criterion | B1 ORB | B2 PDH/PDL | B3 London range | B4 Channel | B5 Compression | B6 Vol band |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Peer-reviewed evidence (any market) | 3 | 2 | 2 | 4 | 2 | 2 |
| Peer-reviewed evidence on gold | 1 | 1 | 1 | 2 | 1 | 1 |
| Independent evidence on gold | 3 | 1 | 3 | 2 | 2 | 1 |
| Clarity of economic mechanism | 3 | 3 | 4 | 4 | 3 | 2 |
| Objectivity of definition | 3 | 4 | 3 | 4 | 2 | 3 |
| Data requirement (higher = easier) | 1 | 3 | 1 | 5 | 4 | 4 |
| Cost sensitivity (higher = less sensitive) | 1 | 2 | 1 | 3 | 2 | 2 |
| Parameter count (higher = fewer) | 3 | 4 | 3 | 4 | 2 | 2 |
| DST / timezone risk (higher = less risk) | 2 | 3 | 1 | 5 | 5 | 5 |
| Freedom from post-hoc selection | 2 | 3 | 2 | 3 | 1 | 1 |
| **Overall testability** | **2.2** | **2.6** | **2.1** | **3.6** | **2.4** | **2.3** |

### 9.2 Interpretation

- **B4 (channel/Donchian)** scores highest on testability because it needs only
  daily bars, has few parameters, has no session/DST dependence and has the
  strongest academic coverage. Its weakness is that the academic record is
  mixed and the gold-specific result is negative.
- **B2 (PDH/PDL)** is the second-easiest to test and has a clear, objective
  level. Its weakness is that the independent evidence is on a different
  instrument and the level is a single observation.
- **B1 (ORB)** and **B3 (London range)** have the most interesting economic
  mechanism but the worst data and DST risk. They cannot be tested credibly
  without intraday history that the project has not yet qualified.
- **B5** and **B6** are overlays. Their low scores reflect the fact that they
  multiply the search space without adding an independent hypothesis.

### 9.3 What the matrix does not say

- It does not say B4 is profitable.
- It does not say B1/B3 should be abandoned.
- It does not rank by expected return.
- It does not replace a pre-registered protocol.

### 9.4 Correlation between candidates

The six families are not independent:

- B1 and B3 overlap when the opening range is also the session range.
- B4 and B6 overlap when the channel is volatility-scaled.
- B2 and B4 overlap when the prior day's high/low is also an N-bar extreme.
- B5 is a filter on all of the others.

A Phase 3B protocol that tests all six must therefore report the correlation of
their signals and returns; otherwise it will overstate the amount of independent
evidence.

---

## 10. Testability and data requirements

### 10.1 What each family needs

| Family | Minimum data | Preferred data | Sample needed | Main data risk |
| --- | --- | --- | --- | --- |
| B1 ORB | M1 or M5 bars with bid/ask | Tick data with bid/ask and volume | 5+ years, 500+ trades | Intraday history, session boundaries, DST |
| B2 PDH/PDL | D1 bars, or M15 for intrabar triggers | M1 with bid/ask | 10+ years, 300+ trades | Day boundary convention |
| B3 London range | M5 or M1 with bid/ask | Tick data | 5+ years, 500+ trades | Timezone/DST, session definition |
| B4 Channel | D1 bars | D1 with adjusted continuous series | 15+ years, 300+ trades | Roll adjustment, survivorship |
| B5 Compression | D1 or intraday bars | Same as the base family | Same as base | Post-hoc compression definition |
| B6 Vol band | D1 or intraday bars | Same as base | Same as base | Parameter search space |

The sample-needed column is provisional; it is a planning range, not a
statistical gate. Section 10.5 explains the assumptions.

### 10.2 Data prerequisites from Phase 2B

Phase 2B's data-readiness report found:

- D1 and H4 series usable, 2004-06-11 to 2026-11-04.
- H1 series started 5.75 years late.
- M15 series started 18.2 years late.
- The connected feed was MetaQuotes-Demo, not Exness.
- Historical tick/spread data from the feed was recent only.
- The in-sample/out-of-sample split was conditional on a data decision.

These are project-internal testing conditions, not market facts, and the Phase
2B verdicts (T1 FAIL, T2/T3 INCONCLUSIVE, no promotion) are unchanged. They
apply to Phase 3A. In particular:

- B1 and B3 cannot be tested on the current M15 history without accepting a
  much shorter sample.
- B2 and B4 can be tested on D1, but the D1 day boundary and roll convention
  must be fixed first.
- All families require a spread model; Phase 2B's bar-level spread averages are
  not a substitute for point-in-time quotes.

### 10.3 Protocol requirements

Any Phase 3B test must include:

1. **A written protocol before running.** Families, ranges, triggers, entries,
   stops, exits, filters, costs, sample split and kill criteria.
2. **A fixed sample split.** In-sample for specification, out-of-sample for
   evaluation. No re-specification after seeing out-of-sample results.
3. **A full trial count.** Every parameter combination run, including failures.
4. **A multiple-testing correction.** Reality Check, deflated Sharpe, or an
   equivalent, applied to the full search.
5. **Cost stress.** Baseline, 1.5× and 2× spread/slippage; swap included for
   multi-day holds.
6. **Benchmarks.** Buy-and-hold, random-entry with the same exits, and a
   random-sign control.
7. **Regime and session breakdowns.** Not only pooled results.
8. **A kill rule.** Pre-registered, e.g. "kill if out-of-sample profit factor
   < 1.0 or if the result is within 2 standard errors of the random-entry
   benchmark".
9. **A preserved artefact set.** Code, data snapshot, logs and results, with a
   hash, as in Phase 2B.

### 10.4 Instrument and symbol

- The EA trades a broker-specific XAUUSD symbol. The protocol must name it.
- Gold futures (GC/MGC) may be used as a reference or robustness check, but a
  futures result cannot be transplanted to the CFD without a cost and session
  bridge.
- Contract size, tick value, minimum volume, stop level and swap must be read
  from the broker specification, not assumed.

### 10.5 Provisional sample-size thresholds

The following is a rough two-standard-error approximation, not a formal power
calculation and not a Phase 3B gate:

| Mean edge | Approximate trades | Status |
| ---: | ---: | --- |
| 0.05R | 1,600 | Provisional planning threshold |
| 0.10R | 400 | Provisional planning threshold |
| 0.20R | 100 | Provisional planning threshold |

Formula: n ≈ (2 × SD / edge)², with SD = 1R.

These figures assume independent trades, stable variance, normal returns, no
multiple testing and a one-sided 2 SE criterion. They ignore autocorrelation,
volatility clustering, regime shifts, the effect of the stop and exit rules on
the R distribution, and the fact that a search over several families raises the
effective hurdle. They are provisional only; a formal power calculation should
be part of the Phase 3B protocol.

Two different Phase 2B rules are sometimes conflated and must be kept apart:

- **T1 out-of-sample trade-count gate.** The frozen Phase 2B protocol required
  at least 300 completed out-of-sample trades for T1. That gate passed with
  2,823 trades, but T1 still failed its family verdict on the profit-factor,
  cost and volatility-regime gates (Phase 2B Final Review). The 300 figure is a
  project convention for T1, not a general statistical requirement.
- **T2/T3 minimum-observation rule.** T2 and T3 were recorded as **INCONCLUSIVE**
  below 100 full-sample trades or position episodes. T2 had 20 trades in the
  selected trial (53 across the pre-registered grid) and T3 had 35 episodes (41
  across the grid), so both were INCONCLUSIVE. This is a minimum-observation
  floor, not a power calculation and not a 300-trade OOS gate.

The 1,600 / 400 / 100 rows above are illustrative two-standard-error
approximations. Only the 0.20R/100 row coincides with the T2/T3 floor, and that
coincidence is arithmetic, not a project rule. The "300+ trades" entries in
Section 10.1 are likewise planning ranges, not a restatement of the T1 gate.
None of these numbers should be copied into Phase 3B without a stated power
calculation.

This is why the independent tests with 89 or 104 trades cannot establish an
edge, and why a high-frequency intraday family is easier to power than a sparse
daily one. It is also why a low-frequency daily breakout with a large apparent
edge can still be statistically fragile.

### 10.6 What cannot be tested with the current data

- Tick-level trigger and slippage behaviour.
- Intraday session structure before the M15 history begins.
- Broker-specific spread behaviour in stress.
- Historical swap schedules.

These are data limitations, not findings. They must be disclosed, not worked
around.

---

## 11. Recommended shortlist and unresolved questions

### 11.1 The shortlist

**No winner is selected.** The shortlist is a testing order.

| Priority | Family | Status | What a test would establish |
| --- | --- | --- | --- |
| 1 | **B4 - Channel / Donchian** | **Recommended for a controlled test** | Whether the best-studied breakout family survives on gold at this project's costs |
| 2 | **B2 - Previous-day high/low** | **Recommended for a controlled test** | Whether a simple, objective level carries a tradeable edge on gold |
| 3 | **B3 - London-session range** | **Conditional** | Whether session-driven expansion is real after DST, spread and news controls |
| 4 | **B1 - Opening-range breakout** | **Conditional, intraday data required** | Whether the peer-reviewed ORB result generalises to gold |
| 5 | **B5 - Volatility compression** | **Overlay only** | Whether a compression filter improves B2/B4, tested as an ablation |
| 6 | **B6 - Volatility band** | **Overlay only** | Whether volatility scaling adds anything over B4 |

### 11.2 Why B4 first

- Lowest data requirement: daily bars.
- Fewest parameters: lookback and trigger convention.
- No session/DST dependence.
- Strongest academic coverage, including a direct gold test.
- Easiest to deflate: the search space is small and countable.
- Directly comparable to the Phase 2B T2/T3 framework, which already exists.

### 11.3 Why B2 second

- Objective, cheap to compute, and available on daily data.
- Tests a different mechanism (salient level) from B4 (N-bar extreme).
- Can be run on the same daily sample as B4, which makes the comparison clean.
- Its weakness is that the public evidence is on a different instrument.

### 11.4 Why B3 and B1 are conditional

- Both require intraday history that Phase 2B found unreliable or too short.
- Both are highly sensitive to DST and session definition.
- Both have a plausible mechanism but a weak gold-specific evidence base.
- Testing them without fixing the data and clock conventions would produce a
  result that cannot be interpreted.

### 11.5 Why B5 and B6 are overlays

- Neither is a complete hypothesis; both modify a base family.
- Testing them standalone multiplies the search space and the data-snooping
  burden.
- The correct test is an ablation: B4 with and without the compression or
  volatility-band filter, on the same sample, with the same costs.

### 11.6 Unresolved research questions

These must be answered before a Phase 3B trial is designed.

1. **Which instrument is the research instrument?** XAUUSD CFD, spot XAU/USD,
   or COMEX GC/MGC? The answer determines the data, the session and the cost
   model.
2. **Which day boundary defines PDH/PDL?** Broker server day, UTC day, London
   day, or COMEX settlement day?
3. **Which clock defines the London and New York sessions?** Fixed local time,
   fixed UTC, or fixed server time? How are the DST mismatch weeks handled?
4. **Is the available intraday history good enough for B1/B3?** If not, are
   those families deferred rather than tested on a short sample?
5. **What is the point-in-time spread model?** Phase 2B used bar-level averages;
   a breakout test needs a spread at the trigger instant.
6. **How are news days handled?** Excluded, included, or reported separately?
7. **What is the pre-registered range of N for B4?** A small grid with a
   correction, or a single N chosen from prior literature?
8. **What counts as a false breakout for the kill rule?** A fixed time horizon,
   a return inside the range, or a stop-out?
9. **What is the benchmark?** Buy-and-hold, random entry with the same exits, or
   a random-sign control?
10. **What is the provisional minimum trade count?** Phase 2B used two distinct
    rules, not one universal gate: a 300-completed-trade out-of-sample
    requirement for T1 (a project convention), and a 100 full-sample
    trade-or-episode floor below which T2 and T3 were INCONCLUSIVE. Neither is a
    substitute for a power calculation. The Phase 3B protocol should state a
    power-based minimum for each family, justify it, and apply it consistently.
11. **Does gold breakout add anything to the Phase 2B trend results?** If the
    signal correlation is high, it is not a new family.
12. **What would make the project stop?** A pre-registered kill rule, as in the
    untilnextsession example, is required before the first run.

### 11.7 What this shortlist does not do

- It does not approve Phase 3B.
- It does not commit to a parameter set.
- It does not claim B4 or B2 will pass.
- It does not demote B1/B3 permanently; it defers them pending data.

---

## 12. Threats to validity

### 12.1 Internal validity

- **Data snooping** across six families and multiple variants.
- **Post-hoc range selection** (lookback, session, compression definition).
- **Cost model error** (bar-level spreads, missing slippage, current swap used
  as historical).
- **Look-ahead** from forming bars, revised data, or a range that includes the
  trigger bar.
- **Survivorship** in the independent evidence.

### 12.2 External validity

- Futures results transplanted to a CFD.
- A single broker's XAUUSD history treated as "the" gold market.
- A sample period dominated by one regime (2008-2012, 2020-2022).
- A result that depends on a session that has changed character over time.

### 12.3 Construct validity

- "Breakout" measured by a proxy (bar close) that is not the economic event
  (sustained order flow).
- "False breakout" defined by a horizon that is chosen after the fact.
- "Edge" measured by profit factor alone, ignoring drawdown and trade count.

### 12.4 Threats specific to this project

- The Phase 2B data source was MetaQuotes-Demo, not the live broker.
- The Phase 2B spread and swap figures are testing assumptions, not verified
  historical costs.
- Intraday history is short.
- The project has no tick data with reliable bid/ask.
- The EA is not designed for intraday breakout execution; Phase 1's execution
  engine assumptions may not fit.
- A chat-level decision is not a repository commit; nothing in this document is
  approved until it is separately reviewed and committed under the roadmap.

### 12.5 What would falsify this document's recommendation

- A data audit showing that daily bars are also unreliable would remove B4 and
  B2 and force a data-remediation phase.
- A finding that the six families' signals are almost perfectly correlated would
  reduce the shortlist to one family.
- A peer-reviewed gold ORB study with a clean out-of-sample design would raise
  B1's priority.
- A demonstration that costs exceed the plausible breakout distance on the
  broker's XAUUSD would make all intraday families untestable at retail size.

---

## 13. References

References are grouped by class. DOIs are given where available. Exact URLs are
given for non-DOI sources. Unless stated otherwise, every non-DOI URL below was
accessed on 2026-11-10. DOIs are identifiers, not access records, and were not
all re-fetched. Vendor and practitioner pages can change; the figures recorded
here are as accessed on that date and are not independently verified. Print
books without a stable URL are labelled as such.

### 13.1 Peer-reviewed academic literature

1. **Anderson, J. A., & Faff, R. W.** (2005). Profitability of trading rules in
   futures markets. *Accounting Research Journal*, 18(2), 83-92.
   https://doi.org/10.1108/10309610580000677

2. **Bailey, D. H., & López de Prado, M.** (2014). The deflated Sharpe ratio:
   Correcting for selection bias, backtest overfitting and non-normality.
   *Journal of Portfolio Management*, 40(5), 94-107.
   https://doi.org/10.3905/jpm.2014.40.5.094

3. **Bajgrowicz, P., & Scaillet, O.** (2012). Technical trading revisited: False
   discoveries, persistence tests, and transaction costs. *Journal of Financial
   Economics*, 106(3), 473-491.
   https://doi.org/10.1016/j.jfineco.2012.06.001

4. **Batten, J. A., Lucey, B. M., McGroarty, F., Peat, M., & Urquhart, A.**
   (2017). Stylized facts of intraday precious metals. *PLOS ONE*, 12(4),
   e0174232. https://doi.org/10.1371/journal.pone.0174232

5. **Baur, D. G., & Lucey, B. M.** (2010). Is gold a hedge or a safe haven? An
   analysis of stocks, bonds and gold. *Financial Review*, 45(2), 217-229.
   https://doi.org/10.1111/j.1540-6288.2010.00244.x

6. **Cai, J., Cheung, Y.-L., & Wong, M. C. S.** (2001). What moves the gold
   market? *Journal of Futures Markets*, 21(3), 257-278.
   https://doi.org/10.1002/1096-9934(200103)21:3<257::AID-FUT4>3.0.CO;2-W

7. **Caporin, M., Ranaldo, A., & Velo, G. G.** (2015). Precious metals under the
   microscope: A high-frequency analysis. *Quantitative Finance*, 15(5),
   743-759. https://doi.org/10.1080/14697688.2014.947313

8. **Elder, J., Miao, H., & Ramchander, S.** (2012). Impact of macroeconomic news
   on metal futures. *Journal of Banking & Finance*, 36(1), 51-65.
   https://doi.org/10.1016/j.jbankfin.2011.06.007

9. **Erb, C. B., & Harvey, C. R.** (2013). The golden dilemma. *Financial
   Analysts Journal*, 69(4), 10-42.
   https://doi.org/10.2469/faj.v69.n4.1

10. **Harvey, C. R., Liu, Y., & Zhu, H.** (2016). … and the cross-section of
    expected returns. *Review of Financial Studies*, 29(1), 5-68.
    https://doi.org/10.1093/rfs/hhv059

11. **Hauptfleisch, M., Putniņš, T. J., & Lucey, B. M.** (2016). Who sets the
    price of gold? London or New York? *Journal of Futures Markets*, 36(6),
    564-586. https://doi.org/10.1002/fut.21775

12. **Holmberg, U., Lönnbark, C., & Lundström, C.** (2013). Assessing the
    profitability of intraday opening range breakout strategies. *Finance
    Research Letters*, 10(1), 27-33.
    https://doi.org/10.1016/j.frl.2012.09.001

13. **Hurst, B., Ooi, Y. H., & Pedersen, L. H.** (2017). A century of evidence on
    trend-following investing. *Journal of Portfolio Management*, 44(1), 15-29.
    https://doi.org/10.3905/jpm.2017.44.1.015

14. **Kaminski, K. M., & Lo, A. W.** (2014). When do stop-loss rules stop
    losses? *Journal of Financial Markets*, 18, 234-254.
    https://doi.org/10.1016/j.finmar.2013.07.001

15. **Marshall, B. R., Cahan, R. H., & Cahan, J. M.** (2008). Can commodity
    futures be profitably traded with quantitative market timing strategies?
    *Journal of Banking & Finance*, 32(9), 1810-1819.
    https://doi.org/10.1016/j.jbankfin.2007.12.011

16. **Mizrach, B., & Weerts, S. Z.** (2009). Highs and lows: A behavioural and
    technical analysis. *Applied Financial Economics*, 19(10), 767-777.
    https://doi.org/10.1080/09603100802199679

17. **Osler, C. L.** (2003). Currency orders and exchange rate dynamics: An
    explanation for the predictive success of technical analysis. *Journal of
    Finance*, 58(5), 1791-1819. https://doi.org/10.1111/1540-6261.00588

18. **Park, C.-H., & Irwin, S. H.** (2007). What do we know about the
    profitability of technical analysis? *Journal of Economic Surveys*, 21(4),
    786-826. https://doi.org/10.1111/j.1467-6419.2007.00519.x

19. **Sullivan, R., Timmermann, A., & White, H.** (1999). Data-snooping,
    technical trading rule performance, and the bootstrap. *Journal of
    Finance*, 54(5), 1647-1691.
    https://doi.org/10.1111/0022-1082.00163

20. **Szakmary, A. C., Shen, Q., & Sharma, S. C.** (2010). Trend-following
    trading strategies in commodity futures: A re-examination. *Journal of
    Banking & Finance*, 34(2), 409-426.
    https://doi.org/10.1016/j.jbankfin.2009.08.004

21. **Tsai, Y.-C., Wu, M.-E., Syu, J.-H., Lei, C.-L., Wu, C.-S., Ho, J.-M., &
    Wang, C.-J.** (2019). Assessing the profitability of timely opening range
    breakout on index futures markets. *IEEE Access*, 7, 32061-32071.
    https://doi.org/10.1109/ACCESS.2019.2899177

22. **White, H.** (2000). A reality check for data snooping. *Econometrica*,
    68(5), 1097-1126. https://doi.org/10.1111/1468-0262.00152

### 13.2 Professional and institutional sources

23. **World Gold Council.** *Gold Market Primer: Market size and structure*.
    3 November 2026.
    https://www.gold.org/goldhub/research/market-primer/gold-market-primer-market-size-and-structure
    (Accessed 2026-11-10. 2025 turnover: total about US$361bn/day; London OTC
    about US$180bn/day; on-exchange about US$174bn/day; COMEX about
    US$114bn/day; SHFE about US$51bn/day. The page does not give a separate
    US$7bn ETF figure, so no such figure is used in this document.)

24. **LBMA.** *LBMA Precious Metals Market Report: Q1 2025*. 9 April 2025.
    https://www.lbma.org.uk/articles/lbma-precious-metals-market-report-q1-2025
    (Accessed 2026-11-10. Gold average daily volume 48.36 mn oz; average daily
    value US$137.67bn.)

25. **CME Group.** Gold futures contract specifications (GC, MGC, 1OZ).
    https://www.cmegroup.com/markets/metals/precious/gold.html
    (Accessed 2026-11-10.)

26. **CME Group.** "Asia's Growing Gold Demand Fuels Surging Derivatives
    Market", *OpenMarkets*, 2025.
    https://www.cmegroup.com/openmarkets/metals/2025/Asias-Growing-Gold-Demand-Fuels-Surging-Derivatives-Market.html
    (Accessed 2026-11-10. Contract sizes: GC 100 oz, MGC 10 oz, 1OZ 1 oz. Q2
    2025 MGC bid/offer averaged 2.01 ticks overall and 1.98 ticks in Asian
    hours; Asian hours were about 42% of MGC volume and over one third of GC
    volume.)

### 13.3 Independent and non-peer-reviewed sources

27. **QuantReplay.** London breakout on micro gold (MGC), 5-minute, 2016-2026.
    https://quantreplay.ai/research/london-breakout
    (Accessed 2026-11-10. 1,696 trades; IS PF 0.90; OOS PF 1.29; 488 OOS
    trades; 25/25 parameter settings profitable OOS; costs US$0.75 each way
    plus one tick slippage. Vendor claim, not independently verified.)

28. **QuantReplay.** Keltner channel breakout on MGC, 15-minute, 2016-2026.
    https://quantreplay.ai/research/keltner-breakout
    (Accessed 2026-11-10. 2,121 trades; OOS PF 0.87; no edge after costs.
    Vendor claim, not independently verified.)

29. **QuantReplay.** Previous-day high/low breakout on MYM.
    https://quantreplay.ai/research/pdh-pdl-breakout
    (Accessed 2026-11-10. 1,094 trades; IS -0.14R / PF 0.78; OOS -0.08R /
    PF 0.89; 0/16 settings profitable OOS. Vendor claim; instrument is not
    gold.)

30. **QuantReplay.** Donchian breakout on MCL.
    https://quantreplay.ai/research/donchian-breakout
    (Accessed 2026-11-10. 2,789 trades; OOS PF 0.79. Vendor claim; instrument
    is not gold.)

31. **QuantReplay.** Asia-range breakout on MNQ.
    https://quantreplay.ai/research/asia-range-breakout
    (Accessed 2026-11-10. OOS PF 0.90. Vendor claim; instrument is not gold.)

32. **BacktestingMax.** London breakout backtest.
    https://www.backtestingmax.com/backtests/london-breakout
    (Accessed 2026-11-10. 18 tests; 5 profitable; 4 in both periods; gold only
    marginally positive on 5-minute; stop orders described as roughly break-even
    after half-spread. Vendor summary, not a measured after-cost distribution,
    and not independently verified.)

33. **BacktestingMax.** New York open breakout backtest.
    https://www.backtestingmax.com/backtests/new-york-open-breakout
    (Accessed 2026-11-10. 0/10 profitable; MGC -16.2% 5m and -20.8% 15m;
    report days 4,834 trades -366.1R vs +44.4R non-report; one-hour-range
    variant +16.1%/+9.5% selected post hoc, 1/50 in both periods. Vendor claim.)

34. **CRTLAB.** "Does the Opening Range Breakout Work on Gold?" *CRTLAB
    Answers*.
    https://crtlab.pro/answers/does-the-opening-range-breakout-work-on-gold
    (Accessed 2026-11-10. XAU/USD 5-minute, 3 January 2017 to 19 October 2026;
    09:30-09:45 New York range; +0.12R +/- 0.04 over 2,394 trades held to 16:00;
    +0.09R at 2R; rank 4 of 13 markets; spread and slippage excluded. Vendor
    claim, not independently verified.)

35. **Delta Terminal.** "Does the Asia Range Breakout Fail 73% of the Time? A
    2,303-breakout test on XAU/USD", *Delta Terminal Research*.
    https://deltaterminal.io/research/asia-range-breakout/
    (Accessed 2026-11-10. XAU/USD spot, Dukascopy 5-minute data, 3 January 2023
    to 3 August 2026; 2,303 total break events over 923 days. A wick beyond the
    Asia high or low between 09:00 and 14:25 re-entered the range within 30
    minutes on 75.7% of the 630 normal-day morning wick breaks (95% interval
    72.2-78.9%); similar rates at phantom levels. Descriptive frequency, not a
    strategy return.)

36. **Open Market Journal.** "Gold's Opening-Range Breakout: London vs New
    York".
    https://openmarketjournal.com/research/gold-opening-range-breakout
    (Accessed 2026-11-10. 7,948 London and New York sessions over 16 years;
    resolved success about 32%; London 47% two-sided sweeps; New York 22%. The
    page describes itself as AI-assisted research and is not independently
    verified.)

37. **untilnextsession.** "London breakout on XAUUSD".
    https://untilnextsession.com/experiments/london-breakout-gold/
    Test record: https://untilnextsession.com/research/london-breakout/README.md
    (Accessed 2026-11-10. 2 January to 31 August 2026; 89 trades; +449.3 USD/oz
    after spread; about 1.5 standard errors versus a random-entry benchmark;
    pre-registered 2 s.e. kill rule not met; strategy killed. Author's own test
    record, not peer reviewed.)

38. **Sönnert, T.** (2015). *Intraday Momentum: Day trading on the gold futures
    market using Opening Range Breakouts and GARCH*. Bachelor thesis, Umeå
    School of Business and Economics, Umeå University.
    http://urn.kb.se/resolve?urn=urn:nbn:se:umu:diva-106885
    (Accessed 2026-11-10. Gold futures ORB, 2009-2014, daily
    high/low/open/close data from NYMEX. Result not independently reproduced.)

### 13.4 Anecdotal and practitioner sources

39. **Trading & Investing Strategies.** "Insane Gold Breakout Strategy: 1.85
    Profit Factor Over 28 Years". 18 March 2026.
    https://tradinginvestingstrategies.substack.com/p/gold-breakout-strategy-28-year-backtest
    (Accessed 2026-11-10. Paid article; 104 trades; daily XAUUSD; execution
    details undisclosed. Numerical claims unverified. A-class, not evidence.)

40. **Crabel, T.** (1990). *Day Trading with Short Term Price Patterns and
    Opening Range Breakout*. Greenville Institute. (Print book; no DOI or
    stable URL. Practitioner reference for ORB and compression definitions.)

41. **Clenow, A. F.** (2013). *Following the Trend: Diversified Managed Futures
    Trading*. Wiley. (Print book; no DOI or stable URL. Practitioner treatment
    of channel breakout conventions.)

### 13.5 Project documents

42. `ROADMAP.md` - Phase 3 definition (locked; not modified by this document).
43. `Docs/Strategy/Phase-2A-Trend-Following-Research.md` - evidence grading and
    candidate conventions.
44. `Docs/Strategy/Phase-2B-Final-Review.md` - Phase 2B verdicts, verdict rules
    and cost/data findings.
45. `Docs/Strategy/Phase-2-Protocol-Errata.md` - protocol change control.
46. `Research/Phase-2B/reports/data-readiness.md` - data availability and
    limitations.

---

## 14. Claim ledger

Every substantive claim, its class, its grade and its status.

### 14.1 Claims about breakout evidence

| # | Claim | Class | Grade | Status |
| --- | --- | --- | --- | --- |
| 1 | Channel breakout has positive mean excess returns net of costs in at least 22 of 28 commodity futures, for the parameterisations tested | P | E2 | Szakmary et al. 2010; monthly, 28 markets, pooled; not gold-specific |
| 2 | Apparent commodity timing profits often fail data-snooping corrections | P | E2/E3 | Marshall et al. 2008; Sullivan et al. 1999; different samples and rule universes |
| 3 | Channel breakout on COMEX gold 1990-1998 showed no significant profit | P | E3 | Anderson & Faff 2005; five-market study, not a standalone gold paper |
| 4 | ORB on crude oil was significantly positive, driven by 2001-2011 | P | E2 | Holmberg et al. 2013; baseline assumes zero spread/commission, cost sensitivity lighter than retail CFD |
| 5 | Timely ORB on index futures was positive after costs, with in-sample selection | P | E3 | Tsai et al. 2019; not gold |
| 6 | No clean peer-reviewed gold ORB result exists in the reviewed literature | P | E4 | Absence of evidence |
| 7 | Gold intraday volatility and liquidity are session-periodic | P | E1/E2 | Batten et al. 2017; Caporin et al. 2015 |
| 8 | Scheduled US macro news moves gold intraday | P | E2 | Cai et al. 2001; Elder et al. 2012 |
| 9 | Stops cluster near salient levels and can cascade | P | E2 for FX; E4 for gold | Osler 2003; FX order-flow study, not gold |
| 10 | Stop rules add value only under momentum | P | E2 | Kaminski & Lo 2014 |
| 11 | A new factor should clear t > 3.0 | P | E1 for factor research; heuristic for strategy tests | Harvey et al. 2016 |
| 12 | Reported Sharpe ratios should be deflated for trials | P | E1 | Bailey & López de Prado 2014 |

### 14.2 Claims about gold market structure

| # | Claim | Class | Grade | Status |
| --- | --- | --- | --- | --- |
| 13 | 2025 average daily gold turnover was about US$361bn | I | E1 | WGC; estimate |
| 14 | London OTC is the dominant gold venue by turnover | I | E1 | WGC; LBMA |
| 15 | COMEX gold turnover was about US$114bn/day in 2025 | I | E1 | WGC |
| 16 | GC is 100 oz, MGC is 10 oz, 1OZ is 1 oz | I | E1 | CME specs |
| 17 | MGC average bid/offer is about 2 ticks | I | E1 | CME note |
| 18 | A retail XAUUSD CFD spread is broker-specific | I | E1 | Definitional |
| 19 | Phase 2B's testing assumptions included a D1 spread of median USD 0.418/oz and p95 USD 0.677/oz | Project | E1 | Bar-level H1-derived series; not point-in-time |
| 20 | Phase 2B swap assumptions were current settings, not verified history | Project | E1 | Long about -0.126/oz/day, short about -0.046/oz/day; triple swap Wednesday |

### 14.3 Claims about independent evidence

| # | Claim | Class | Grade | Status |
| --- | --- | --- | --- | --- |
| 21 | QuantReplay London MGC: IS PF 0.90, OOS PF 1.29 | N | E3 | Vendor claim, not replicated |
| 22 | QuantReplay Keltner MGC: OOS PF 0.87 | N | E3 | Vendor claim, not replicated |
| 23 | QuantReplay PDH/PDL MYM: 0/16 settings profitable OOS | N | E3 | Vendor claim, different instrument |
| 24 | BacktestingMax NY open: 0/10 tests profitable | N | E3 | Vendor claim |
| 25 | BacktestingMax London: 4 of 18 profitable in both periods | N | E3 | Vendor claim |
| 26 | CRTLAB gold NY ORB: +0.12R before costs | N | E4 | Vendor claim, costs excluded |
| 27 | Delta Terminal: 75.7% of normal-day morning wick breaks revert within 30 minutes (n = 630) | N | E4 | Vendor claim; 630 is a subset of the 2,303 total break events (morning/afternoon, wick/close, all 923 days); descriptive only |
| 28 | Open Market Journal: 32% resolved success, London 47% two-sided sweeps | N | E4 | AI-assisted, not peer-reviewed |
| 29 | untilnextsession: 89 trades, +449.3 USD/oz, killed on a 2 s.e. rule | N | E4 | Very short sample |
| 30 | Sönnert: positive gold ORB returns 2009-2014 | N | E4 | Bachelor thesis, daily data |
| 31 | Substack: 1.85 profit factor over 28 years | A | E5 | Not evidence; 104 trades; undisclosed method |

### 14.4 Claims about this document's recommendations

| # | Claim | Class | Grade | Status |
| --- | --- | --- | --- | --- |
| 32 | B4 and B2 are the most testable families | Analysis | - | Recommendation, not finding |
| 33 | B1 and B3 are conditional on intraday data | Analysis | - | Recommendation, not finding |
| 34 | B5 and B6 are overlays, not standalone families | Analysis | - | Recommendation, not finding |
| 35 | No family has passed a controlled test on this project's data | Project | E1 | True by inspection |
| 36 | No winner is selected | Project | E1 | True by construction |

### 14.5 Claims that are explicitly hypotheses

- Any statement that a specific breakout rule "works" on gold.
- Any statement that London is better than New York for gold ORB.
- Any statement that volatility compression improves gold breakout.
- Any statement that the independent results would replicate on this project's
  data.
- Any statement that Phase 3 will produce a better result than Phase 2.

### 14.6 Qualification notes

- **Szakmary et al. (2010)** is a monthly, 28-market, pooled study. It supports
  a broad commodity-panel claim, not a gold-specific or intraday claim.
- **Marshall et al. (2008)** and **Sullivan et al. (1999)** use different
  samples, rule universes and test designs from Szakmary et al. Their results
  should be read as a caution about rule searches, not as a direct refutation of
  every channel strategy.
- **Harvey, Liu and Zhu (2016)** is about the cross-section of expected returns.
  The t > 3.0 hurdle is a conservative heuristic for strategy research, not a
  universal legal threshold.
- **Osler (2003)** is an FX order-flow study. The stop-clustering mechanism is an
  analogy for gold, not a measured gold result.
- **Mizrach and Weerts (2009)** is a US equity study of 849 stocks over
  1993-2003. It reports reversal after n-day highs and abnormal positive returns
  after n-day lows, not continuation. It is not evidence for a gold PDH/PDL
  breakout.
- **Phase 2B's** spread and swap figures are project-internal testing
  assumptions. The connected feed was MetaQuotes-Demo, not Exness; the spread
  series is bar-level; the swap schedule is current settings, not history. The
  Phase 2B verdicts (T1 FAIL, T2/T3 INCONCLUSIVE, no promotion) are unchanged.
- **Independent vendor results** are not a representative sample. They differ
  in instrument, sample, costs and selection, and failures may be
  under-reported. No break-even baseline can be inferred from them.
- **Trade-count thresholds** in Section 10.5 are provisional planning figures,
  not gates. Phase 2B's 300-trade OOS requirement (T1) and its 100-trade/episode
  floor (T2/T3) are distinct rules and are described separately in Section 10.5.
- **Comparison scores** in Section 9 are author judgements. The overall column
  is an unweighted mean, not a decision rule.

---

## 15. Appendix A - Consolidated specification sheet

This sheet is a template for Phase 3B. It is not a parameter recommendation.

### 15.1 Global

| Item | Value |
| --- | --- |
| Instrument | TBD: XAUUSD CFD / spot XAU/USD / GC / MGC |
| Timeframe | TBD per family |
| Timezone | Named timezone library, not a fixed UTC offset |
| Day boundary | TBD (server / UTC / London / COMEX) |
| Cost model | Spread + commission + slippage + swap, each stated |
| Sample split | TBD, pre-registered |
| Trial count | All combinations, reported |
| Multiple-testing method | Reality Check / deflated Sharpe |
| Benchmark | Buy-and-hold, random entry, random sign |
| Kill rule | Pre-registered |

### 15.2 B1 - ORB

| Parameter | Template |
| --- | --- |
| Session | New York / London / Asia |
| Opening window | 15 / 30 / 60 minutes |
| Trigger | Intrabar / close / stop |
| Confirmation | None / close / retest / second bar |
| Stop | Opposite side / ATR multiple |
| Exit | R multiple / trail / session close |
| Direction | Both / long-only / trend-filtered |
| News policy | Exclude / include / separate |

### 15.3 B2 - PDH/PDL

| Parameter | Template |
| --- | --- |
| Day boundary | Server / UTC / London / COMEX |
| Trigger | Intrabar / close / stop |
| Buffer | None / k ticks / k × ATR |
| Confirmation | None / close / retest |
| Stop | Opposite level / ATR |
| Exit | R multiple / trail / time |
| Direction | Both / long-only |
| News policy | Exclude / include / separate |

### 15.4 B3 - London range

| Parameter | Template |
| --- | --- |
| Quiet window | 00:00-07:00 London / Tokyo session |
| Active window | London open to London close |
| DST handling | Fixed local / fixed server / both |
| Trigger | Close / stop / intrabar |
| Buffer | None / k ticks |
| Stop | Opposite side / ATR |
| Exit | R multiple / trail / session close |
| News policy | Exclude / include / separate |

### 15.5 B4 - Channel

| Parameter | Template |
| --- | --- |
| Lookback N | 20 / 55 / 100 |
| Timeframe | D1 |
| Trigger | Close / intrabar |
| Stop | ATR × k |
| Exit | Opposite channel / trail / time |
| Direction | Both / long-only |
| Roll convention | Back-adjusted / ratio-adjusted / none |

### 15.6 B5/B6 - Overlays

| Parameter | Template |
| --- | --- |
| Base family | B2 / B4 |
| Compression definition | NR7 / inside day / ATR percentile |
| Band definition | Keltner / Bollinger |
| Lookback | TBD |
| Multiplier | TBD |
| Test design | Ablation: base vs base + overlay |

### 15.7 Cost defaults

| Cost | Value | Source |
| --- | --- | --- |
| Spread | Baseline + stress; Phase 2B D1 testing assumption median USD 0.418/oz, p95 USD 0.677/oz | Broker / Phase 2B; bar-level, not point-in-time |
| Commission | Per contract / per lot | Broker |
| Slippage | Fraction of spread, stress 1.5× / 2× | Assumption |
| Swap | Phase 2B testing assumption: long about -0.126/oz/day, short about -0.046/oz/day | Phase 2B; current settings, not verified history |
| Triple swap | Wednesday | Phase 2B |

---

## 16. Appendix B - Pre-flight checklist for Phase 3B

### 16.1 Governance

- [ ] Protocol written and reviewed before any run.
- [ ] `ROADMAP.md`, Phase 1, Phase 2A, Phase 2B and errata unchanged.
- [ ] No EA change proposed as part of research.
- [ ] Approval recorded separately; a chat decision is not a commit.

### 16.2 Data

- [ ] Instrument and symbol named.
- [ ] Data source named and versioned.
- [ ] Day boundary and session convention fixed.
- [ ] DST handling fixed.
- [ ] Roll convention fixed (futures).
- [ ] Spread model is point-in-time or its limitations are stated.
- [ ] Sample split pre-registered.
- [ ] Data hash recorded.

### 16.3 Protocol

- [ ] Families and variants listed.
- [ ] Every parameter and its grid listed.
- [ ] Trigger, entry, confirmation, stop and exit fixed.
- [ ] News policy fixed.
- [ ] Cost stress levels fixed.
- [ ] Benchmarks fixed.
- [ ] Multiple-testing correction fixed.
- [ ] Kill rule fixed.
- [ ] Reporting template fixed.

### 16.4 Execution

- [ ] No re-specification after out-of-sample results.
- [ ] All trials reported, including failures.
- [ ] Regime and session breakdowns reported.
- [ ] R-multiple distribution reported.
- [ ] Artefacts preserved with a hash.

---

## 17. Open questions

1. Which instrument is the research instrument?
2. Which day boundary defines PDH/PDL?
3. Which clock defines London and New York sessions?
4. Is the intraday history good enough for B1/B3?
5. What is the point-in-time spread model?
6. How are news days handled?
7. What is the pre-registered N range for B4?
8. What counts as a false breakout for the kill rule?
9. What is the benchmark?
10. What is the minimum trade count, and is it the Phase 2B 300-trade OOS gate, the 100-trade/episode floor, or a new power-based figure?
11. Does breakout add anything to the Phase 2B trend results?
12. What would make the project stop?

---

## 18. Conclusion

The evidence does not support selecting a breakout winner. Channel breakout has
the strongest academic coverage but a mixed record and a negative gold-specific
result. Opening-range and session-range breakout have plausible mechanisms and
supportive results in other markets, but no clean gold evidence and severe data
and DST requirements. Volatility compression and volatility-band rules are
overlays, not independent families.

The responsible next step is not to implement or optimise. It is to fix the
instrument, data, clock and cost conventions, then run a pre-registered,
deflated test of B4 and B2, with B3 and B1 conditional on data. Until that test
exists, every statement about gold breakout profitability is a hypothesis.

This document is **DRAFT / NOT APPROVED**. It authorises nothing.

---

## 19. Document history

| Version | Date | Status | Note |
| --- | --- | --- | --- |
| 0.1 | 2026-11-09 | DRAFT / NOT APPROVED | Initial Phase 3A breakout research draft |
| 0.2 | 2026-11-09; revised 2026-11-10; corrected 2026-11-11 | DRAFT / NOT APPROVED | Revised after review: session/DST qualifications; Szakmary, Harvey, Osler and Phase 2B qualifications; independent-source and break-even language; scoring rubric and provisional trade-count caveats; completed document history. Final targeted revision: corrected the London-New York overlap/DST table; reframed Mizrach and Weerts as US equity reversal evidence; audited non-DOI references with exact URLs and 2026-11-10 access dates; separated the Phase 2B T1 300-trade OOS requirement from the T2/T3 100-trade/episode floor in Sections 10.5, 11.6 and 17; softened stop/sweep/cascade claims. 2026-11-11 correction: clarified Delta Terminal's 2,303 total break count versus the 630 normal-day morning wick subset in Sections 6.3.4 and 14.3; the prior 2026-11-10 edit date was confirmed from file metadata. No approval, commit, tag or push. |
