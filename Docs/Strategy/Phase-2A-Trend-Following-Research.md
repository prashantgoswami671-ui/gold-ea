# Phase 2A - Trend-Following Research

Project: Gold EA
Document type: Research and candidate selection
Status: revised draft for review (v0.2)
Scope: XAUUSD, discretionary-free systematic trend following
Out of scope: MQL5 implementation, EA modification, parameter optimisation

---

## 1. Document control

| Item | Value |
| --- | --- |
| Phase | 2A - Research |
| Depends on | Phase 0 (environment), Phase 1 (execution and risk engine) |
| Followed by | Phase 2B - Backtesting |
| Instrument | XAUUSD (spot gold vs USD) |
| Strategy family under review | Trend following |
| Deliverable | Evidence review, four candidate definitions, recommendation of 1-3 candidates to backtest |
| Code changes | None |
| EA changes | None |
| Files changed by this phase | This document only |

### 1.1 Why this document exists

The project charter allows four strategy families. Before any of them is coded
or optimised, the project needs a written position on what the published
evidence actually supports, what it does not, and which specific hypotheses are
worth spending backtest time on.

This document does three things:

1. It separates **established findings** from **plausible but unproven
   hypotheses** and from **claims that the literature contradicts**.
2. It turns the surviving hypotheses into **four concrete, mutually distinct
   trend-following candidates** for XAUUSD.
3. It recommends **which of those candidates deserve a Phase 2B backtest**, and
   states in advance what result would count as failure.

It deliberately does **not** claim that any candidate is profitable. Nothing in
this document has been tested on this project's data. Every candidate is a
hypothesis with a pre-registered falsification test.

### 1.2 How to read the evidence grades

Every substantive claim in this document carries a grade. The grades describe
**the state of published evidence**, not the author's confidence in a trading
outcome.

| Grade | Meaning | Typical basis |
| --- | --- | --- |
| **E1 - Established** | Replicated across independent samples, markets and methods; survives reasonable robustness checks. Safe to treat as background fact. | Multiple peer-reviewed studies, different data, consistent direction |
| **E2 - Supported** | Consistent evidence in good studies, but narrower sample, one methodology family, or known replication limits. | One strong study plus partial confirmation |
| **E3 - Mixed** | Credible studies disagree, or the effect exists only under specific conditions. | Contradictory peer-reviewed results |
| **E4 - Hypothesis** | Plausible mechanism, weak or indirect evidence, not established for this instrument. Must be tested, not assumed. | Theory, analogy, practitioner claims, small samples |
| **E5 - Not supported** | Evidence points against the claim, or the claim fails standard robustness tests. | Direct contrary evidence |

Two rules govern use of the grades:

- **A grade attaches to a claim, not to a paper.** A single paper can support an
  E2 claim in one section and an E5 claim in another.
- **An E4 claim may still be worth backtesting.** Low evidence grade means "do
  not assume", not "do not test". The whole point of Phase 2B is to convert E4
  into evidence for or against, on this instrument, with this cost model.

### 1.3 A note on the difference between "trend following works" and "this EA will make money"

The literature mostly studies **diversified portfolios of 50-70 futures
markets**, rebalanced continuously, with institutional cost assumptions, sized
by volatility, and held for months. Those studies can be simultaneously correct
and irrelevant to a single-instrument, single-account retail EA.

Three gaps must be crossed before a published result becomes a reason to trade
XAUUSD on a retail account:

| Gap | Why it matters here |
| --- | --- |
| **Diversification gap** | Trend following's statistical strength comes largely from averaging weak signals across many uncorrelated markets. One instrument removes that averaging. |
| **Cost gap** | Published results use institutional commissions and deep liquidity. Retail XAUUSD spreads, swaps and slippage are larger and vary by session. |
| **Implementation gap** | Whether an edge is tradeable depends on the actual broker contract size, minimum volume, tick value, spread, swap and execution quality. These are implementation facts, not evidence about the edge, and they are evaluated only after the edge and its robustness are established (Section 7). |

Every recommendation in Section 10 is conditioned on these gaps. Section 1.4
formalises them as an evidence hierarchy that is applied throughout the
document.

### 1.4 Evidence hierarchy: Level A, B and C

Not all evidence is evidence about the same thing. This document separates three
levels, and every strong claim is labelled with the level it belongs to.

| Level | What it covers | Typical sources | What it can establish | What it cannot establish |
| --- | --- | --- | --- | --- |
| **Level A - Broad** | Trend following across many markets and asset classes | Hurst et al. 2017; Moskowitz et al. 2012; Lempérière et al. 2014; Szakmary et al. 2010 | That the phenomenon exists and has persisted across markets and time | That it survives on XAUUSD, at retail costs, with our execution |
| **Level B - Gold-specific** | Gold and precious-metals evidence | Batten et al. 2018; Jin 2022; Dichtl 2020; Baur et al. 2020; Erb & Harvey 2013 | That gold behaves differently from a generic asset, and that some rule families have failed on it | That our exact rule, timeframe and cost model will fail |
| **Level C - Implementation** | Our broker, symbol, timeframe, costs, sizing and execution | Phase 0/1 probes; our own Phase 2B results | What is actually executable, and what our tested specification does | That trend following as a family works or fails |

Three rules follow, and they are applied throughout:

1. **A strong Level A result does not prove Level C profitability.** The
   diversified-portfolio evidence is not a licence to assume a single-instrument
   retail edge.
2. **A poor Level C result does not invalidate Level A.** One failed
   specification is one failed specification.
3. **Level B evidence is the best prior available for this project, but it is
   still about gold in general, not about our exact rules.**

Where a claim crosses levels, the weakest relevant level sets the conclusion.

---

## 2. Executive summary

### 2.1 What the evidence says

1. **Trend following has been a real, persistent, diversifying return source for
   over a century** across futures, currencies, bonds and commodities, in
   samples going back to 1880 and to 1800 depending on the study. This is
   **E2**, close to E1 for the diversified-portfolio version. (Hurst, Ooi &
   Pedersen 2017; Lempérière et al. 2014; Moskowitz, Ooi & Pedersen 2012.)

2. **The evidence for single-market trend following is much weaker than the
   evidence for the diversified portfolio.** Time-series momentum is positive
   for most individual contracts, but per-market Sharpe ratios are around 0.4
   and individual markets frequently have multi-year flat or losing stretches.
   This is **E2** for "positive on average", **E3** for "reliable per
   instrument".

3. **A significant part of the headline time-series momentum result is
   attributable to volatility scaling rather than to the sign of past
   returns.** Unscaled time-series momentum looks much more like unscaled
   buy-and-hold. This is **E2**. (Kim, Tse & Wald 2016.)

4. **The statistical case for time-series momentum as a distinct predictive
   effect (as opposed to a time-varying long bias) is contested.** Credible
   work finds little out-of-sample time-series predictability once the test is
   specified carefully. This is **E3**. (Huang et al. 2020; Goyal & Jegadeesh
   2018.)

5. **Technical trading rules on gold specifically have a poor out-of-sample
   record once data snooping and costs are handled.** Studies of gold and
   precious-metals intraday rules find no persistent predictive power after
   correction for multiple testing. This is **E2/E3**. (Batten et al. 2018; Jin
   2022; Dichtl 2020; Baur et al. 2020.)

6. **Gold has unusual, regime-dependent drivers** - real interest rates, the US
   dollar, central-bank reserve demand, ETF flows, and crisis demand - and its
   relationship with real yields appears to have weakened after 2022. This is
   **E1** for the existence of these drivers, **E3** for the stability of their
   relative weights.

7. **The evidence is strongest at Level A and weakest at Level C.** The
   century-long, multi-market record justifies testing trend following on gold.
   It does not establish that any specific gold implementation is profitable.
   Only a Level C test - our data, our costs, our execution - can do that. See
   Section 1.4.

### 2.2 What this document recommends

**Recommendation: backtest T2 and T3. Treat T1 as a conditional incremental
test. Do not make T4 a primary candidate.**

| Candidate | Short name | Recommendation | Reason |
| --- | --- | --- | --- |
| **T2** | Daily dual-EMA trend | **Primary - backtest first** | Cheapest to implement, lowest turnover, most robust to cost assumptions, best matches the horizon where the Level A evidence is strongest, easiest to falsify |
| **T3** | Time-series momentum overlay | **Secondary - backtest second** | Directly tests the best-documented effect, but requires volatility targeting and exposes the vol-scaling critique; useful as an independent check on T2 |
| **T1** | Multi-timeframe EMA pullback | **Tertiary - only as an incremental test** | Plausible and popular, but sits in the intraday region where gold-specific evidence is weakest and costs are highest |
| **T4** | Filtered trend system | **Not a primary candidate** | Not a distinct hypothesis; a complexity ablation on T1/T2. Run only as an attribution exercise after T1/T2 are measured |

**The order matters.** T2 answers "does this specific slow daily EMA
implementation of trend following survive on XAUUSD, net of realistic costs?"
with the fewest degrees of freedom. If T2 fails its pre-registered gates, the
evidence is against **that implementation** - not against trend following as a
family, and not against every gold trend system. T1 and T4 must still not be
used to rescue T2 inside the same confirmatory phase, because that would be
exactly the data-snooping behaviour the literature warns about. T3 answers a
different question: "is the effect specifically time-series momentum, or just
long gold exposure?"

### 2.3 What would change this recommendation

The recommendation is contingent on the following, all of which must be
verified in Phase 2B or before:

- **Broker contract specification.** Phase 0 observed a 100 oz contract, a 0.01
  lot minimum and a 0.01 tick size on the Exness XAUUSD symbol. If another
  account or broker reports a different specification, the account-size figures
  in Section 7 scale accordingly. This is a deployment consideration and does
  not affect candidate selection.
- **Cost data.** If measured round-trip cost exceeds roughly 25% of the average
  gross profit per trade for T1, T1 should be dropped without further work.
- **Data availability.** T2 and T3 need clean daily data over at least 20 years
  including the 2011-2015 gold bear market. If only a few years of reliable
  history exist, the regime tests cannot be run and the candidates downgrade to
  E4 indefinitely.

---

## 3. Scope, definitions and non-goals

### 3.1 Definitions used in this document

| Term | Definition used here |
| --- | --- |
| **Trend following** | A rule that takes a position in the direction of a past price change, expecting continuation. Includes moving-average crossovers, time-series momentum, and channel breakouts. |
| **Time-series momentum (TSMOM)** | The sign of an asset's own past return predicts its own future return. Distinct from cross-sectional momentum, which ranks assets against each other. |
| **Diversified trend portfolio** | A portfolio holding trend signals across many markets simultaneously, usually volatility-scaled. The object of most academic studies. |
| **Single-instrument trend system** | A rule applied to one symbol only. The object of this project. |
| **Regime** | A persistent market state (e.g. trending vs range-bound, high vs low volatility, positive vs negative real yields) within which a rule's performance may differ. |
| **Data snooping** | Selecting a rule or parameter because it performed well in the same data used to evaluate it. Inflates apparent performance. |
| **Deflated Sharpe ratio** | A Sharpe ratio adjusted for the number of trials, non-normality and sample length. (Bailey & López de Prado 2014.) |
| **Turnover** | The rate at which positions are opened and closed; a proxy for cost exposure. |
| **Net** | After spread, commission, swap and modelled slippage. |
| **Gross** | Before those costs. |

### 3.2 In scope

- Evidence on trend following as a phenomenon, with emphasis on commodities,
  futures and gold.
- Evidence specific to gold and precious metals.
- Structural facts about the XAUUSD market that constrain strategy design:
  contract size, tick value, spread behaviour, swap, volatility, session
  effects, event risk.
- Four candidate strategy definitions at a level precise enough to implement
  and falsify.
- A pre-registered backtest protocol and decision gates for Phase 2B.

### 3.3 Explicit non-goals

This document does **not**:

- write, modify or review MQL5 code;
- modify the EA, `ROADMAP.md`, `CHANGELOG.md` or any Phase 1 artefact;
- claim any candidate is profitable;
- select final parameters (it names pre-registered grids, not chosen values);
- cover breakout strategies in detail - pure Donchian/ATR-channel breakout is a
  Phase 3 topic and is excluded here to keep the families separable;
- cover mean reversion, grid, or martingale approaches;
- provide trading advice or a signal service;
- estimate future returns.

### 3.4 Relationship to the roadmap's four strategy families

The roadmap contemplates several families. This document addresses only trend
following. Two boundaries are worth stating so later phases do not duplicate
work:

- **Trend vs breakout.** A Donchian channel breakout is mechanically a trend
  rule, but its evidence base, parameter sensitivity and cost profile are
  different enough that Phase 3 should own it. T1 and T2 here use moving
  averages and momentum signs; they do not use channel breakouts.
- **Trend vs mean reversion.** Some of gold's behaviour around real-yield
  extremes is mean-reverting (Erb & Harvey 2013). That is a separate family and
  is not mixed into these candidates, because blending them would make failure
  attribution impossible.

---

## 4. Evidence in favour of trend following

This section states the strongest credible case. It is deliberately generous to
trend following, because a candidate should be tested against the best version
of the argument, not a straw man.

### 4.1 The effect has survived more than a century of out-of-sample time

**Claim:** Trend-following returns are not an artefact of a single post-1980
sample. They appear in markets and periods that predate modern futures trading,
electronic execution and published academic research.

**Grade: E2. Evidence level: A (broad, multi-market).**

| Study | Sample | Finding |
| --- | --- | --- |
| Hurst, Ooi & Pedersen (2017) | 67 markets, 1880-2016 | A simple combination of 1-, 3- and 12-month trend signals produced positive average returns in **every decade** of the 137-year sample |
| Lempérière et al. (2014) | Four asset classes, spot data back to 1800 | Aggregate trend-following t-statistic of 10.5 (9.8 after de-biasing); no evidence of long-term decay |
| Moskowitz, Ooi & Pedersen (2012) | 58 futures and forwards, 1965-2009 | Positive 12-month time-series momentum for **every one** of the 58 contracts |

**Interpretation.** The breadth of the sample is the strongest single argument
for trend following. It is very difficult to attribute a 137-year, 67-market
result to a specific institutional accident, a single data vendor, or a
particular cost regime. The effect predates the existence of the academic
literature that studies it.

**Limits on this claim.** These are all **diversified portfolio** results. The
positive aggregate return does not imply that any individual market, and
certainly not gold, produced a usable standalone return in every decade. The
Hurst et al. figure is an average across markets; a single market's dispersion
around that average is large.

### 4.2 Per-market returns are positive on average, with meaningful dispersion

**Claim:** Individual futures markets show positive trend-following returns on
average, and diversification is what converts a weak per-market edge into a
strong portfolio result.

**Grade: E2**

Hurst, Ooi & Pedersen (2017) report an average per-market Sharpe ratio of
approximately **0.4** for a simple trend strategy. A Sharpe of 0.4 is a real
but modest edge: it implies a long, psychologically difficult ride with
multi-year drawdowns, and it is only attractive when averaged across many
weakly correlated markets.

**Interpretation for this project.** A per-market Sharpe near 0.4 is roughly the
ceiling a single-instrument trend system should expect to *approach*, not
exceed, before costs. Any backtest on XAUUSD alone showing a Sharpe far above
0.4-0.6 over a long sample should be treated as a red flag for overfitting or
cost understatement, not as a discovery.

### 4.3 Trend following performs relatively well in extreme markets

**Claim:** Trend-following returns have a positive relationship with market
stress, producing "crisis alpha" - the ability to make money in prolonged
directional dislocations.

**Grade: E2**

| Evidence | Finding |
| --- | --- |
| Hurst, Ooi & Pedersen (2017) | The strategy was positive in **8 of the 10 largest drawdowns** of a 60/40 portfolio over 1880-2016 |
| Fung & Hsieh (2001) | Trend-following returns have an option-like payoff that is better explained by lookback straddles than by linear exposure to standard asset indices |
| Moskowitz, Ooi & Pedersen (2012) | Time-series momentum performs best in extreme market environments |

**Interpretation.** This is the property that makes trend following attractive
as a portfolio diversifier even when its standalone Sharpe is modest. It is
also the property most likely to be relevant to gold, which has large
directional episodes (2008-2011, 2019-2020, 2024-2026).

**Important caveat.** Crisis alpha is not the same as reliable crisis alpha. It
is a statement about average behaviour across many markets and crises, not a
guarantee for one instrument in the next crisis. Fung & Hsieh's option-like
characterisation also implies the strategy *loses* in whipsaw conditions, which
are common in gold.

### 4.4 Commodity trend rules survive costs in broad samples

**Claim:** Classic trend rules on commodity futures remain profitable net of
costs across a wide sample, not just gross.

**Grade: E2**

Szakmary, Shen & Sharma (2010) examined 28 commodity markets over 48 years and
found that dual moving-average crossover and channel strategies produced
positive returns **net of costs in at least 22 of 28 markets**, with pooled
results highly statistically significant.

**Interpretation.** This is one of the more directly relevant studies for this
project, because it uses the same rule family (moving-average crossover) that
T2 proposes, on commodity futures, with costs. It is evidence that the *rule
family* is not inherently fragile.

**Limits.** Commodity futures are not spot XAUUSD. Futures have exchange
clearing, tight spreads and explicit commissions; retail spot gold has wider
spreads, swap charges and broker-dependent execution. "Net of costs" in a
futures study is a much lower cost bar than the one this project faces.

### 4.5 The effect is not confined to one asset class

**Claim:** Time-series momentum appears across equities, currencies, bonds and
commodities, which argues for a common behavioural or risk-premium mechanism
rather than a data artefact in one market.

**Grade: E2**

Georgopoulou & Wang (2017) document a significant time-series momentum effect
across conventional asset classes over 1969-2015. The cross-asset consistency is
the main reason the effect is taken seriously: a genuine artefact would be
unlikely to appear independently in four unrelated markets.

**Candidate mechanisms** (each **E4** on its own):

- **Under-reaction and slow information diffusion.** Investors update
  partially, so prices drift after news.
- **Herding and trend-chasing flows.** Systematic and discretionary managers
  add to winners, extending moves.
- **Risk management and stop cascades.** Forced de-risking amplifies
  directional moves.
- **Time-varying risk premia.** Trend exposure proxies for a compensated risk
  factor.

None of these mechanisms is established well enough to justify a rule on its
own. They matter because they make the effect *plausible* rather than
coincidental, which is a precondition for spending backtest time on it.

### 4.6 Recent commodity evidence does not show clear decay

**Claim:** The reliability of trend signals in commodity futures has not
collapsed in recent decades.

**Grade: E3**

Auer (2021) examined whether trend-rule reliability in commodity futures has
declined and found **no significant decay for most commodity futures**, with
cross-sectional accuracy higher than time-series accuracy.

**Interpretation and tension.** This is genuinely useful counter-evidence to the
"trend following is dead" narrative. But it sits against strong evidence that
*practitioner* trend-following returns were poor through the 2010s (Section
5.5). The reconciliation is probably that rule *reliability* (sign accuracy) and
investable *returns* (after volatility scaling, costs and diversification
collapse) are different quantities. A rule can be right slightly more often than
not and still produce a disappointing Sharpe.

### 4.7 Why this section is not enough on its own

Every positive result above shares one of three properties:

1. It is a **diversified portfolio** result (4.1, 4.2, 4.3).
2. It is a **futures** result with institutional costs (4.4).
3. It is a **statistical** result about sign accuracy, not an investable
   single-instrument return (4.6).

None of them is a single-instrument, retail-cost, spot-gold result. That gap is
the entire reason Phase 2B exists, and it is why Section 5 carries as much weight
as this section. In the hierarchy of Section 1.4, everything above is Level A
evidence; the project needs Level C evidence before it can conclude anything
about its own implementation.

---

## 5. Evidence against trend following

This section is not a balancing ritual. Several of these findings are strong
enough to change candidate design, and two of them (5.1 and 5.6) directly shape
the recommendation in Section 10.

### 5.1 The time-series momentum effect is statistically fragile

**Claim:** Once the test is specified carefully, there is little robust evidence
that an asset's own past return predicts its own future return, in-sample or
out-of-sample.

**Grade: E3** (contested, but the critique is serious and peer-reviewed)

Huang, Li, Wang & Zhou (2020) re-examined the time-series momentum evidence and
found:

- **47 of 55 assets** had individual t-statistics below 1.65 - i.e. most
  individual assets do not show significant time-series predictability.
- The commonly reported pooled t-statistic is **unreliable under bootstrap**;
  it overstates significance because of cross-sectional correlation.
- A time-series momentum strategy is profitable, but its performance is
  **virtually identical to a strategy that simply uses each asset's historical
  sample mean** - raising the question of whether "momentum" is doing any work
  beyond a time-varying long bias.

**Interpretation for this project.** This is the most important statistical
caveat in the document. It means:

- The correct null hypothesis for T2/T3 is **not** "trend following does not
  work anywhere". It is "XAUUSD's own past return does not predict XAUUSD's
  future return beyond what a constant long bias would capture".
- A candidate that beats zero but does not beat **buy-and-hold gold** has not
  demonstrated a trend effect. It has demonstrated long exposure.
- This is why Section 11 mandates a buy-and-hold benchmark and a
  random-entry/same-exposure control.

### 5.2 Much of the headline result is volatility scaling, not signal

**Claim:** A large part of the reported time-series momentum alpha comes from
scaling positions inversely to recent volatility, not from the direction
signal.

**Grade: E2**

Kim, Tse & Wald (2016) show that:

- Large time-series momentum alphas are **largely driven by volatility
  scaling**.
- **Unscaled** time-series momentum alphas are similar to **unscaled
  buy-and-hold**.
- Performance of the strategy has diminished in recent periods.

**Interpretation.** Volatility scaling is a legitimate risk-management choice,
and it genuinely improves risk-adjusted returns. But it is not "trend
prediction". If T3's performance comes mostly from vol scaling, then T3 is
really a risk-management overlay with a directional tilt, and it should be
judged and reported as such. Section 8.3 requires T3 to report unscaled
results alongside scaled results for exactly this reason.

### 5.3 Time-series and cross-sectional momentum are not the same effect

**Claim:** Part of what looks like time-series predictability is a
time-varying net long exposure, which is a different economic phenomenon from
cross-sectional momentum.

**Grade: E2**

Goyal & Jegadeesh (2018) show that the difference between cross-sectional and
time-series tests of return predictability is largely attributable to
**time-varying net long exposure**. A strategy that is long more often than
short in a rising market will look like it has time-series skill.

**Interpretation.** For a single instrument, this is close to fatal unless
controlled. XAUUSD rose substantially over most of the sample period. A
long-biased trend rule will therefore look good for reasons that have nothing to
do with trend. Section 11 requires long/short attribution and a
beta-to-buy-and-hold decomposition.

### 5.4 Technical rules on gold fail out-of-sample once snooping is handled

**Claim:** For gold and precious metals specifically, technical trading rules
have not demonstrated persistent predictive power after correcting for data
snooping, transaction costs and market conditions.

**Grade: E2** (multiple independent studies, consistent direction). **Evidence
level: B (gold-specific), not C.**

| Study | Market and sample | Finding |
| --- | --- | --- |
| Batten, Lucey, McGroarty, Peat & Urquhart (2018) | Precious metals, intraday | Standard moving-average parameters offer **no predictive power**; with a large parameter universe some gold combinations appear significant, but not silver; longer parameters do better |
| Jin (2022) | Shanghai Futures Exchange gold, 5-minute bars, 2018-2021 | After data snooping, transaction costs, market conditions and rebalancing, **no persistent out-of-sample performance**; concludes predictive power "is illusory" |
| Dichtl (2020) | Gold excess returns | None of technical indicators, diffusion indices or restricted predictive regressions **improves gold return forecasts**; predictor power is highly regime-dependent |
| Baur, Dichtl, Drobetz & Wendt (2020) | >4,000 gold timing strategies, 1990-2015 | Some timing ability and economic gains, but **not robust to data-snooping biases** and limited to specific periods |

**Interpretation.** This cluster is the strongest direct evidence *against* T1
and against naive technical rules on gold. It does not condemn T2 by itself,
because T2 is a slow daily rule and the studies above are mostly intraday or
short-horizon. But it does mean:

- **Short-horizon gold rules should be presumed guilty until proven innocent.**
  T1 carries the burden of proof.
- **Parameter universes must be pre-registered and reported in full.** The
  Batten et al. and Baur et al. results show that a large enough search will
  find "significant" gold rules by chance.
- **The longer the holding period, the better the prior.** Batten et al.
  explicitly found longer parameters more successful, which is consistent with
  T2 and inconsistent with T1.

### 5.5 Practitioner trend-following returns were poor for a decade

**Claim:** Even if the statistical effect persists, investable trend-following
returns went through a long, deep drought in the 2010s.

**Grade: E2** (industry index data; descriptive, not peer-reviewed)

The SG Trend Index returned roughly **1.8% per annum during the 2010s**, against
a long-run average nearer **5.7% per annum**. Long-run index CAGR is around
5.3% with a maximum drawdown around 20.6%; 2024 and 2025 were both around
+2.4%.

**Interpretation.** This is the practical counterweight to Section 4.1. A
century-long positive average can coexist with a decade in which the strategy
underperformed cash. For a single-instrument retail system, a similar drought
would be fatal to the account long before the century average reasserted
itself.

**Caveat on the data.** These are net-of-fee industry index figures, not
peer-reviewed. They are included because they describe what an investor
actually experienced, which the academic gross-return tables do not. They
should be read as **E2 descriptive**, not as a precise performance estimate.

### 5.6 Faster trend is worse after costs

**Claim:** Increasing trend speed raises turnover and cost drag faster than it
raises gross edge, so net risk-adjusted returns fall as the strategy gets
faster.

**Grade: E2**

Man Group's analysis of trend speed finds that, after costs, risk-adjusted
returns are **materially lower for faster trend speeds**, while crisis alpha is
stronger for fast models. There is a genuine trade-off, not a free lunch.

**Interpretation.** This directly undercuts T1, which is the fastest candidate
(M15 entries). It also explains why T2 (daily, low turnover) is the better first
test: it sits on the favourable side of the cost/speed trade-off, and its
failure would be informative rather than ambiguous.

### 5.7 Stop-losses do not automatically reduce risk

**Claim:** Under a random walk, a stop-loss rule lowers expected return without
improving the risk profile enough to compensate. Stops add value only when
returns actually exhibit momentum.

**Grade: E2**

Kaminski & Lo (2014) show that:

- Under a random walk, stop-loss rules **reduce expected return**.
- With momentum in the underlying process, stop-loss rules **can add value**.
- Monthly stop-loss rules added roughly **50-100 basis points per month**
  during stop-out periods in their sample.

**Interpretation.** This is a conditional endorsement, not a rejection. It means
the stop-loss in T1 and T2 is **part of the hypothesis**, not a neutral safety
feature. If trend following does not work on XAUUSD, the stops will make results
worse, not better. Backtests must therefore report results with and without the
disaster stop, so the stop's contribution can be attributed rather than assumed.

### 5.8 Backtest overfitting is the dominant practical risk

**Claim:** Most published "profitable" rule discoveries, and most retail
backtest discoveries, are artefacts of searching too many rules on too little
data.

**Grade: E1** (methodological, not empirical about markets)

| Source | Contribution |
| --- | --- |
| Sullivan, Timmermann & White (1999) | Bootstrap reality-check for technical rule universes; naive best-rule selection is biased |
| White (2000) | Formal Reality Check test for data snooping |
| Bajgrowicz & Scaillet (2012) | False-discovery-rate control on DJIA 1897-2011; **no ex-ante ability to select future best rules**; even in-sample performance is offset by low transaction costs |
| Bailey, Borwein, López de Prado & Zhu (2014) | Backtest overfitting degrades out-of-sample performance predictably; reports the mathematics of how many trials destroy a strategy |
| Bailey & López de Prado (2014) | Deflated Sharpe ratio adjusts for trials, skew and kurtosis |
| Harvey & Liu (2015) | Sharpe ratios should be haircut for multiple testing |
| Harvey, Liu & Zhu (2016) | New factors should clear a **t > 3** threshold, not t > 2 |

**Interpretation.** This is not a reason to avoid backtesting. It is a reason to
pre-register the tests. Section 11 therefore fixes:

- the data split before any test is run;
- the parameter grid before any result is seen;
- the decision gates before any result is seen;
- the requirement to report **all** trials, including failures.

A candidate that only passes after the grid is expanded is a failed candidate.

### 5.9 Gold may be structurally mean-reverting at long horizons

**Claim:** At long horizons, the real gold price has tended to mean-revert, so a
long-horizon trend rule may be fighting valuation.

**Grade: E3**

Erb & Harvey (2013) argue that the real gold price mean-reverts and that a high
real price is associated with low subsequent real returns; they also argue gold
is an unreliable inflation and currency hedge. This is contested, and the
post-2022 experience is not obviously consistent with a simple real-price
anchoring story.

**Interpretation.** This matters for T3 in particular. A 12-month momentum rule
that goes long after a large real-price run may be buying exactly when
long-horizon expected returns are lowest. The tension between 5.9 and 4.1 is
real and unresolved. It is a reason to test T3 across multiple regimes rather
than to reject it outright.

### 5.10 Summary of the adversarial case

| Objection | Strength | Consequence for design |
| --- | --- | --- |
| Time-series momentum may be a long-bias artefact | Strong (5.1, 5.3) | Must benchmark against buy-and-hold and report long/short attribution |
| Vol scaling drives the result | Strong (5.2) | T3 must report unscaled results |
| Gold-specific technical rules fail out-of-sample | Strong (5.4) | T1 carries the burden of proof; parameter grid pre-registered |
| Trend returns had a lost decade | Moderate (5.5) | Regime tests mandatory; do not judge on full-sample average alone |
| Fast trend loses after costs | Strong (5.6) | T2 before T1; cost stress at 1.5x and 2x |
| Stops hurt under random walk | Moderate (5.7) | Report with/without stop |
| Overfitting dominates | Very strong (5.8) | Pre-registration, deflated Sharpe, full trial reporting |
| Gold mean-reverts at long horizon | Moderate (5.9) | T3 tested across regimes, not just full sample |

---

## 6. Gold-specific market facts

The generic trend-following literature is about a diversified basket. XAUUSD has
properties that change which rules are plausible. This section records only
facts that affect design or evaluation, and it flags what must be verified
against the actual broker rather than assumed.

### 6.1 What drives gold

**Claim:** Gold's price is driven by a small set of identifiable macro factors
whose relative importance varies over time.

**Grade: E1** for the existence of the drivers; **E3** for the stability of
their weights.

| Driver | Mechanism | Evidence |
| --- | --- | --- |
| **Real interest rates** | Gold pays no coupon; higher real yields raise the opportunity cost of holding it | Barsky & Summers (1988); Erb & Harvey (2013) |
| **US dollar** | Gold is priced in USD; a stronger dollar mechanically lowers the USD price and signals tighter global liquidity | Pukthuanthong & Roll (2011) |
| **Central-bank reserves** | Official-sector buying is price-insensitive demand that removes supply from the market | World Gold Council demand data |
| **ETF and bar/coin flows** | Financial demand; amplifies directional moves | World Gold Council demand data |
| **Crisis and inflation demand** | Gold acts as a hedge or safe haven in extreme equity downturns | Baur & McDermott (2010) |
| **Mine supply and recycling** | Slow-moving supply response; second-order at horizons under a year | O'Connor et al. (2015) |

**Why this matters for a trend rule.** If gold's direction is set by macro
factors that move in regimes, then trend signals will work in some regimes and
fail in others. A rule that ignores regime will show a full-sample average that
conceals long losing stretches. This is the core reason Section 11 requires
regime attribution rather than a single full-sample number.

### 6.2 The gold-real-yield relationship has weakened

**Claim:** The historically tight inverse relationship between gold and real
yields has become less reliable since around 2022, coinciding with a step-change
in central-bank buying.

**Grade: E3**

Analyses from Janus Henderson, RBC Wealth Management and PIMCO converge on a
similar description: the gold-real-yield correlation weakened after 2022, while
central-bank purchases averaged roughly **1,000 tonnes per year in 2022-2024**
against roughly **500 tonnes per year in the prior decade**. Real yields still
influence short-horizon direction, but no longer appear to set a floor under the
price.

**Interpretation.** This is a genuine structural break candidate, and it is
dangerous for backtesting. A rule calibrated on 2004-2021 gold may be fitting a
relationship that has changed. Section 11 therefore treats 2022-2026 as a
distinct evaluation window and does not allow it to be used for parameter
selection.

### 6.3 Official-sector demand changed the demand base

**Claim:** Central-bank buying has become a large, persistent, price-insensitive
component of gold demand.

**Grade: E1** (demand data), **E4** for its precise effect on trend persistence.

| Period | Central-bank net purchases |
| --- | --- |
| 2010-2021 average | ~473 tonnes/year |
| 2022 | ~1,080 tonnes |
| 2023 | ~1,037 tonnes |
| 2024 | ~1,045 tonnes (third consecutive year above 1,000 t; 15th consecutive year of net buying) |

World Gold Council data for 2025 and 2026 shows continued but more uneven
official-sector demand, with survey evidence that a record share of central
banks plan to increase their own holdings.

**Interpretation.** Persistent official buying is a plausible mechanism for
longer, smoother gold uptrends than the 1990s-2000s experience would suggest.
It is **not** established that this makes trend following more profitable. It
could equally create a slow one-way drift that a long-only position captures
better than a symmetric long/short trend rule. This is one reason T3's
long/short attribution matters.

### 6.4 Gold demand and price context, 2024-2026

**Grade: E1** (reported data)

| Period | Reported fact |
| --- | --- |
| Full year 2024 | Central banks bought ~1,045 t; third consecutive year above 1,000 t |
| Full year 2025 | Total demand including OTC exceeded 5,000 t for the first time; 53 new all-time highs; value ~US$555 bn (+45% y/y); ETF holdings +801 t; bar and coin demand at a 12-year high |
| Q1 2026 | Demand 1,231 t; value a record ~US$193 bn; bar and coin drove gains; ETF buying slowed; central banks continued buying; jewellery weak |
| Q2 2026 | Central-bank demand continued but uneven; 89% of survey respondents expect global reserves to rise; a record 45% plan to increase their own holdings |

**Interpretation for backtesting.** The 2024-2026 period is an extreme
outlier in gold's history: consecutive all-time highs, record nominal demand
value, and a large ETF flow reversal. A trend system tested only on this period
will look excellent for reasons that may not repeat. Conversely, a system tested
*excluding* this period may understate trend performance in the current regime.
Both must be reported separately. Section 11 does this.

### 6.5 Volatility structure

**Claim:** Gold exhibits volatility clustering and asymmetric volatility, so
volatility-scaled position sizing and volatility-aware stops are structurally
appropriate.

**Grade: E2**

Tully & Lucey (2007) document volatility clustering and asymmetric volatility
in gold using power GARCH methods. In practical terms:

- Quiet periods persist, then break into high-volatility clusters.
- Downside moves tend to be more volatile than upside moves.
- Volatility regime shifts are large enough that a fixed-dollar stop is badly
  mis-specified across a multi-year sample.

**Design consequence.** All stops and position sizes in this document are
expressed in **ATR multiples or percentages**, never in fixed dollar amounts.
Gold traded near $250/oz in 2001, $1,900/oz in 2011, $1,050/oz in 2015 and above
$4,000/oz in 2026. A fixed $5 stop would have been a wide stop in 2001 and a
noise-level stop in 2026.

### 6.6 Session and liquidity structure

**Claim:** XAUUSD liquidity, spread and volatility vary systematically by
session, and the differences are large enough to affect a rule's net result.

**Grade: E2** (market microstructure; broker-specific magnitudes)

| Session (approx. UTC) | Characteristics |
| --- | --- |
| Asian session | Thinner liquidity, wider spreads, lower volatility; trends that start here often reverse in London |
| London open | Liquidity and volatility jump; frequent false breakouts around the open |
| London/New York overlap | Deepest liquidity, tightest spreads, largest directional moves; the best window for execution-sensitive rules |
| New York close / rollover | Spreads widen sharply; swap is applied; avoid new entries |

**Design consequence.** T1, which enters on M15, is highly exposed to this
structure. Its measured edge can be destroyed or created purely by session
filtering, which is exactly why session filters belong in T4's ablation rather
than in T1's core definition. T2 enters on daily opens and is far less exposed.

### 6.7 Cost structure

**Claim:** Retail XAUUSD costs are dominated by spread and swap, not commission,
and are large relative to the per-trade edge a trend system can expect.

**Grade: E1** (arithmetic) / **E4** for the exact magnitudes, which are
broker-specific and must be measured.

| Cost component | Typical retail magnitude | Behaviour |
| --- | --- | --- |
| **Spread** | 10-30 points ($0.10-$0.30/oz) on a standard account; wider in Asian session and at rollover | Variable; the dominant cost for short holds |
| **Commission** | ~$3.50 per lot per side on a raw/ECN account (~$7 round turn per 100 oz, i.e. ~$0.07 per 0.01 lot round turn) | Fixed per volume |
| **Swap** | Applied daily at rollover; can be positive or negative; short gold often costs more | Accumulates with holding period; matters for T2/T3 |
| **Slippage** | Small in liquid sessions, large around news and at the open | Worst exactly when stops trigger |

**Design consequence.** A daily trend system (T2) pays spread rarely but pays
swap continuously. An intraday system (T1) pays spread often but little swap.
These are different cost structures and must be modelled separately, not with a
single average "cost per trade" number.

These figures are **general retail ranges**, not measurements from this
project's account. Section 6.8 separates verified observations from testing
assumptions, and Section 11.4 requires the actual cost model to be built from
measured data. The abnormal Phase 0 spread reading (Section 6.8.2) must not be
used here.

### 6.8 Observed specifications, assumptions and testing assumptions

This section separates four categories that are easy to confuse. Mixing them is
a common source of false precision, so they are kept apart deliberately.

#### 6.8.1 Verified implementation observations (Phase 0/1 probe)

These values were read from the Exness XAUUSD symbol by the Phase 0/1
specification probe and recorded in the Phase 1 test log. They are **observations
of one symbol on one broker**, not universal gold specifications.

| Property | Observed value | Source |
| --- | --- | --- |
| Symbol | XAUUSD | Phase 0/1 probe |
| Digits | 2 | Phase 1 test log |
| Point | 0.01 | Phase 1 test log |
| Tick size | 0.01 | Phase 1 test log |
| Tick value | 0.10 | Phase 1 test log |
| Contract size | 100 oz | Phase 1 test log |
| Minimum volume | 0.01 lot | Phase 1 test log |
| Maximum volume | 100 lot | Phase 1 test log |
| Volume step | 0.01 lot | Phase 1 test log |
| Stops level | 0 | Phase 1 test log |
| Freeze level | 0 | Phase 1 test log |
| Trade mode | Full | Phase 1 test log |
| Execution | Market, FOK/IOC, FOK selected | Phase 1 test log |

Under this observed specification, **0.01 lot corresponds to approximately 1 troy
ounce**.

Two cautions apply to this table:

- **These are not universal.** Another broker, another account type, or another
  gold symbol may report a different contract size, tick value or minimum
  volume. The EA must read every one of these at runtime; it must never hardcode
  them.
- **The reported tick value must be reconciled at runtime.** Tick size
  multiplied by contract size is 0.01 x 100 = $1.00, which does not equal the
  reported tick value of $0.10. This discrepancy does not affect the candidate
  definitions, but it does mean that monetary risk must be derived from the
  terminal's actual `SYMBOL_TRADE_TICK_VALUE` and `SYMBOL_TRADE_TICK_SIZE` at
  runtime, never from an arithmetic assumption.

#### 6.8.2 Abnormal spread observation

The Phase 0 probe recorded a spread reading of approximately **$58.12** at a time
when the symbol was not actively quoting normally.

This reading is **not a normal active-market gold spread** and must not be used
as a backtest cost assumption, a spread filter setting, or a profitability input.
It is recorded here only so it is not mistaken for representative data. Section
11.4 requires the spread model to be built from a measured distribution of active
quotes, not from this observation.

A separate Phase 1 result is relevant: the Strategy Tester produced a 70-point
spread which the default 50-point spread gate correctly rejected. That is a
validation of the guard, not a market observation.

#### 6.8.3 Assumptions still requiring confirmation

These are not yet verified for the target trading account:

| Assumption | Status | How to confirm |
| --- | --- | --- |
| The live account uses the same symbol specification as the probe | Unconfirmed | Re-read the symbol at runtime |
| Swap long and short schedules | Unconfirmed | Symbol specification, live |
| Commission schedule | Unconfirmed | Broker contract page |
| Margin currency and leverage | Unconfirmed | Account settings |
| Spread distribution by session | Unconfirmed | Measure from tick history |
| Slippage on market and stop orders | Unconfirmed | Compare backtest fills to demo fills |

#### 6.8.4 Testing assumptions used in Phase 2B

These are the assumptions the backtest will *use*, stated explicitly so they can
be challenged. They are not claims about the live account.

| Assumption | Working value | Basis |
| --- | --- | --- |
| Spread | Measured distribution, with 10-30 points as a working range | General retail observation; to be replaced by measured data |
| Commission | ~$0.07 per 0.01 lot round turn | Raw-account schedule; to be confirmed |
| Slippage | 0.5 x spread on entry, 1.0 x spread on stop exit | Conservative modelling choice |
| Swap | Broker schedule applied daily | To be confirmed |
| Contract size | 100 oz | Phase 0 observation |
| Minimum volume | 0.01 lot | Phase 0 observation |

#### 6.8.5 General gold-market information

Everything in Sections 6.1 to 6.7 describes gold as a market. It does not depend
on our broker and is not evidence about our implementation. It is Level B
evidence in the Section 1.4 hierarchy.

**Why the separation matters.** A backtest result is only as good as the
implementation assumptions behind it. If a spread figure from a stale quote is
mistaken for a normal spread, every net result is wrong. If a probe value from
one broker is mistaken for a universal contract specification, every position
size is wrong. Keeping the four categories apart is a precondition for a valid
Phase 2B.

---

## 7. Practical account-size case study

> **This section is separate from strategy evaluation.**
>
> Account size does **not** determine whether a strategy is accepted, rejected,
> prioritised, or scored in this document. It is recorded because the project
> will eventually need to size positions, and because the arithmetic is
> routinely misunderstood. The evaluation order is fixed in Section 7.1, and
> account sizing comes last.

### 7.1 The correct order of evaluation

Every candidate is judged in this order, and no step may be skipped:

1. Does the strategy show evidence of an **edge**?
2. Is the edge **robust** - across sub-periods, regimes and nearby parameters?
3. Does it survive realistic **transaction costs**?
4. What are its **drawdown and risk** characteristics?
5. **Then**, and only then, what account size and position sizing are practical?

Steps 1-4 determine the research verdict. Step 5 determines deployment, and it
is a separate decision made after a candidate has already passed. Reversing this
order - rejecting a hypothesis because it is inconvenient to fund - is a
selection bias, not an evaluation.

This section covers step 5 only.

### 7.2 The basic relationship

Using the Phase 0 observations (Section 6.8.1), with a 100 oz contract and a 0.01
lot minimum:

```text
position size      = 0.01 lot = approximately 1 troy ounce
risk per trade     = stop distance in USD/oz x 1 oz
required equity    = risk per trade / risk fraction
```

With a 0.01 lot floor, the smallest possible position is about 1 oz, so the
dollar risk is fixed by the stop width alone. Position sizing cannot reduce it
further. This is a granularity fact about the observed specification - it is not
an argument about any strategy.

### 7.3 Required equity by stop width

Illustrative, at the observed 100 oz contract and 0.01 lot minimum:

| Stop width (USD/oz) | Risk at 0.01 lot | Equity for 1% risk | Equity for 2% risk | Equity for 5% risk |
| --- | --- | --- | --- | --- |
| $2 | $2 | $200 | $100 | $40 |
| $5 | $5 | $500 | $250 | $100 |
| $10 | $10 | $1,000 | $500 | $200 |
| $20 | $20 | $2,000 | $1,000 | $400 |
| $40 | $40 | $4,000 | $2,000 | $800 |
| $80 | $80 | $8,000 | $4,000 | $1,600 |
| $120 | $120 | $12,000 | $6,000 | $2,400 |
| $180 | $180 | $18,000 | $9,000 | $3,600 |

**How to read this table.** Find the stop width a strategy actually uses, then
read across to the risk fraction that would be acceptable. That is the implied
account size, assuming the 0.01 lot floor.

### 7.4 What stop widths are realistic on gold

At a gold price near $4,000/oz, typical true ranges are roughly:

| Measure | Illustrative size | As % of price |
| --- | --- | --- |
| Hourly ATR (normal) | $8 - $15 | 0.2% - 0.4% |
| Daily ATR (normal) | $40 - $60 | 1.0% - 1.5% |
| Daily ATR (stress) | $80 - $120 | 2.0% - 3.0% |
| Weekly ATR (normal) | $120 - $180 | 3.0% - 4.5% |

**These are illustrative and must be recomputed from actual data.** They show
order of magnitude only and are not parameters.

Under these illustrative ranges:

- A **T1** stop of 1.0 x hourly ATR is roughly **$10-$15**.
- A **T2** disaster stop of 3.0 x daily ATR is roughly **$120-$180**.
- A **T3** volatility-targeted position is not stop-based, but the 0.01 lot floor
  creates the same granularity problem.

### 7.5 Cost as a fraction of risk

A round-trip cost of roughly **$0.27 per 0.01 lot** (20-point spread plus
commission) is small in dollars and large relative to a tight stop:

| Stop width | Round-trip cost | Cost as % of risk |
| --- | --- | --- |
| $2 | $0.27 | 13.5% |
| $5 | $0.27 | 5.4% |
| $10 | $0.27 | 2.7% |
| $20 | $0.27 | 1.35% |
| $40 | $0.27 | 0.68% |
| $80 | $0.27 | 0.34% |

**Interpretation.** A strategy with a $5 stop gives up more than 5% of its
per-trade risk to costs before any slippage. This is a cost-robustness point
(Section 5.6), and it belongs to step 3 of the evaluation order, not to step 5.
It is reproduced here only because the same stop width drives both the cost
ratio and the account requirement.

### 7.6 The $25 scenario (illustrative only)

A $25 account has been discussed as a possible future experimental account. It
is treated here as a worked example of the arithmetic, not as a project
constraint and not as a test of any strategy.

At $25 of equity, the risk budget per trade would be:

| Risk fraction | Risk budget | Maximum stop distance at 0.01 lot |
| --- | --- | --- |
| 1% | $0.25 | 25 points ($0.25/oz) |
| 2% | $0.50 | 50 points ($0.50/oz) |
| 5% | $1.25 | 125 points ($1.25/oz) |
| 10% | $2.50 | 250 points ($2.50/oz) |

Compare these to the cost and noise floor:

- A 20-point spread would consume most of a 25-point stop budget at 1% risk.
- A 250-point stop (10% risk) is roughly 5-6% of a normal daily true range.
- A single 1-oz position with a $40 stop risks $40, which is 160% of a $25
  account.

**What this shows.** A $25 account cannot express these stop widths at 1-2% risk
under the observed 100 oz specification. That is a statement about **account
granularity**, not about any strategy's edge. It appears in no acceptance gate,
no scorecard and no candidate ranking. If the account is larger, or the broker's
contract size is smaller, the arithmetic changes; the strategy evaluation does
not.

### 7.7 Margin is not the binding constraint - risk is

| Leverage | Margin for 0.01 lot at $4,000/oz | Free margin on a $25 account |
| --- | --- | --- |
| 1:100 | $40 | **Insufficient - order rejected** |
| 1:200 | $20 | $5 |
| 1:500 | $8 | $17 |
| 1:1000 | $4 | $21 |

Higher leverage makes an order *possible*. It does not make it *safe*. At 1:500,
a $25 account could open a position whose normal stop-loss is larger than the
account. Margin satisfied, risk not controlled. This is a deployment warning,
not a research finding.

### 7.8 Indicative deployment capital by candidate

These are planning estimates for **after** a candidate has passed its research
gates. They are not selection criteria and must not be read as a ranking.

| Candidate | Typical stop | Implied equity at 2% risk | Comment |
| --- | --- | --- | --- |
| **T1** | 1.0 x hourly ATR (~$10-$15) | ~$500 - $750 | Lowest deployment capital; highest cost drag |
| **T2** | 3.0 x daily ATR (~$120-$180) | ~$6,000 - $9,000 | Highest deployment capital; lowest cost drag |
| **T3** | Volatility-targeted, no fixed stop | ~$3,000 - $6,000 | Granularity-limited; at a 10% vol target and ~15% realised gold vol, the 1 oz minimum is already ~$4,000 notional |
| **T4** | Inherits T1 or T2 | Inherits | Filters do not change the sizing floor |

**If a broker reports a 10 oz contract, divide every figure by 10.**

Two points must be stated plainly so this section cannot leak into selection:

- **Nothing here rejects a candidate.** A strategy with a high deployment
  capital requirement is still a valid research target. The research question is
  whether the edge exists, not whether it is convenient to fund today.
- **Backtests are not constrained by account size.** A historical test fixes the
  risk fraction and derives position size; it does not need margin. Section 11
  therefore fixes the risk fraction, not the lot size, and reports the implied
  equity alongside the result as context.

The correct reading of this section is: *"if this candidate passes, what would it
take to run it?"* It is not: *"this candidate is impractical, therefore it
fails."*

---

## 8. The four candidates

The four candidates are **distinct hypotheses**, not parameter variants of one
idea. Each answers a different question, and each can fail independently. This
matters: if they were variants, a failure could be blamed on the wrong
parameter; as distinct hypotheses, a failure is informative.

### 8.0 Design constraints applied to all four

| Constraint | Rule | Reason |
| --- | --- | --- |
| No look-ahead | Signals use closed bars only; entries execute at the next bar open | Prevents the most common backtest inflation |
| ATR-based risk | Stops and sizing in ATR or percentage terms | Gold's price level changed ~16x over the sample (Section 6.5) |
| One position at a time | No pyramiding, no hedging, no grid | Keeps attribution clean and matches Phase 1 execution engine |
| Long and short | Symmetric signals unless stated | Otherwise the result is long-gold beta, not trend |
| Costs modelled | Spread, commission, swap, slippage | Section 5.8 |
| Fixed risk fraction | Risk % fixed; lot size derived | Prevents "risk" from silently scaling with equity |

### 8.1 T1 - Multi-timeframe EMA pullback continuation

**Hypothesis.** Within an established higher-timeframe trend, short-term
pullbacks to a fast moving average resolve in the direction of the trend often
enough to be traded profitably after costs.

**What it tests.** Whether *intraday timing* adds anything to a trend bias on
gold - i.e. whether the entry timing carries information beyond the H4 regime.

**Relationship to the roadmap.** T1 is the closest match to the candidate logic
named in `ROADMAP.md` for Phase 2: higher-timeframe trend filter, lower-timeframe
entry, EMA-based identification, optional RSI confirmation, clear stop and exit
rules, small predefined parameter set. This document does not discard that
candidate. It defines it precisely as T1, tests it against the evidence, and
sequences it behind T2 for the reasons in Section 10.4.

**Grade of underlying hypothesis: E4.** Popular in practice, but Section 5.4
shows gold intraday technical rules have a poor out-of-sample record, and
Section 5.6 shows fast trend loses more to costs.

#### Rules

| Component | Specification |
| --- | --- |
| **Timeframes** | H4 regime, M15 entry, H1 for ATR |
| **Regime filter** | Long only if EMA(50, H4) > EMA(200, H4); short only if EMA(50, H4) < EMA(200, H4) |
| **Pullback condition** | Price trades within 0.2 x ATR(14, H1) of EMA(20, M15) |
| **Trigger** | M15 close back in the trend direction beyond EMA(20, M15) |
| **Optional confirmation** | RSI(14, M15) between 40 and 60 for longs, 60 and 40 for shorts (i.e. not overbought/oversold at entry) |
| **Initial stop** | 1.0 x ATR(14, H1), floored at 2 x current spread |
| **Trailing stop** | 2.0 x ATR(14, H1) from the best price since entry |
| **Exit** | Trailing stop, or H4 regime flip, whichever comes first |
| **Take profit** | None |
| **Max positions** | 1 |
| **Risk per trade** | 0.5% of equity (baseline); 0.25% and 1.0% as sensitivity |
| **Expected frequency** | 2-10 trades per month depending on regime |
| **Expected holding period** | Hours to a few days |

#### Why these values

The H4 50/200 regime filter is the slowest component and therefore the most
robust; it is doing most of the work. The M15 entry is the fast, fragile
component and is the part under test. Splitting the rule this way means a
failure can be attributed: if T1 fails while T2 (same 50/200 logic on D1)
succeeds, the problem is the M15 timing, not the trend premise.

#### Falsification gates

T1 is rejected if any of the following holds on out-of-sample data:

- Net profit factor < 1.20 after all costs.
- Net Sharpe is not at least 0.10 higher than T2's net Sharpe (i.e. the intraday
  timing adds nothing over the daily version).
- Fewer than 300 trades (insufficient sample to distinguish edge from luck).
- Total costs exceed 25% of gross profit.
- Performance is not positive in at least 3 of the 4 volatility regimes in
  Section 11.6.

#### Known weaknesses

- **Highest cost drag** of the four (Section 7.5).
- **Weakest direct evidence** of the four (Section 5.4).
- **Most parameters** of the four (regime pair, pullback distance, trigger,
  RSI band, stop multiple, trail multiple) - highest overfitting surface.
- **Session-sensitive**: results will depend heavily on which hours are traded,
  which T4 tests explicitly.

### 8.2 T2 - Daily dual-EMA trend system

**Hypothesis.** A slow moving-average crossover on daily gold captures
multi-month trends, and the trends are large enough to pay for the relatively
few trades the rule generates.

**What it tests.** The core question of this phase: **does this specific slow
daily trend implementation survive on XAUUSD at the horizon where the broad
evidence is strongest and the costs are lowest?** It does not test whether every
trend-following approach works on gold.

**Grade of underlying hypothesis: E2/E3.** The diversified-portfolio version is
E2; the single-instrument, spot-gold, retail-cost version is closer to E3.

#### Rules

| Component | Specification |
| --- | --- |
| **Timeframe** | D1 |
| **Fast average** | EMA(50, D1) |
| **Slow average** | EMA(200, D1) |
| **Long signal** | EMA(50) crosses above EMA(200) |
| **Short signal** | EMA(50) crosses below EMA(200) |
| **Entry** | Next D1 open after the crossing bar closes |
| **Primary exit** | Opposite crossover (position flips, never flat for long) |
| **Disaster stop** | 3.0 x ATR(14, D1) from entry |
| **Take profit** | None |
| **Max positions** | 1 |
| **Risk per trade** | 1.0% of equity at the disaster stop (baseline); 0.5% as sensitivity |
| **Expected frequency** | Roughly 2-6 position flips per year |
| **Expected holding period** | Months |

#### Why these values

- **D1 rather than H4 or M15** because Section 5.6 shows slower trend survives
  costs better, and Section 4.1's evidence is strongest at multi-month horizons.
- **50/200** because it is the most widely published pair, which makes the test
  comparable to existing literature and reduces the appearance of a tuned
  choice. It is *not* chosen because it is optimal - Section 11 pre-registers
  20/100 and 100/400 as alternatives precisely to check that the result is not
  pair-specific.
- **Flip exit rather than a profit target** because trend following's return
  distribution depends on capturing the full tail; a profit target truncates
  exactly the trades that pay for the losers.
- **Disaster stop at 3.0 x ATR** because Section 5.7 shows stops are not free
  under a random walk; the stop exists to cap tail loss and broker risk, not to
  generate the edge. It is deliberately wide enough that it should rarely bind
  in normal conditions.

#### Falsification gates

T2 is rejected if any of the following holds on out-of-sample data:

- Net profit factor < 1.20 after all costs.
- Net Sharpe < 0.50.
- Maximum drawdown > 25%.
- Fewer than 100 trades (i.e. fewer than ~4.5 flips per year over 22 years) -
  in which case the sample is too small to conclude anything and the result is
  reported as **inconclusive**, not as a pass.
- Not positive in at least 3 of the 4 volatility regimes in Section 11.6.
- Does not beat buy-and-hold gold on a risk-adjusted basis.
- Deflated Sharpe p-value >= 0.10 after accounting for all trials run.

#### Known weaknesses

- **Very few trades.** This is the central statistical problem. With 2-6 flips
  per year over 22 years, the effective sample is roughly 50-130 trades, and
  those trades are highly serially dependent because each lasts months. A
  Sharpe estimated from ~100 overlapping multi-month trades has wide confidence
  intervals.
- **Highest deployment capital** of the four (Section 7.8) - a deployment
  consideration, not an evidence weakness.
- **Slow to fail.** A bad decade looks like a drawdown, not a broken rule, so
  live validation takes years.
- **Swap drag** on multi-month holds, especially shorts.

### 8.3 T3 - Time-series momentum overlay

**Hypothesis.** Gold's own trailing 12-month return predicts its next-month
return, and a volatility-targeted long/short position exploiting this produces
a positive risk-adjusted return that is not merely long-gold beta.

**What it tests.** Whether the best-documented academic effect (Section 4.1)
survives on a single instrument at retail costs, and specifically whether it
survives the vol-scaling critique (Section 5.2).

**Grade of underlying hypothesis: E2** for the diversified version; **E3** for
the single-instrument version after Huang et al. (2020) and Kim, Tse & Wald
(2016).

#### Rules

| Component | Specification |
| --- | --- |
| **Signal** | Sign of trailing 12-month total return (252 trading days) |
| **Rebalance frequency** | Monthly, last trading day of the month |
| **Position** | Long if signal > 0, short if signal < 0 |
| **Volatility estimate** | 60-day exponentially weighted realised volatility |
| **Target volatility** | 10% annualised |
| **Position weight** | target vol / realised vol, capped at 2.0x notional exposure to equity |
| **Stop loss** | None (the monthly rebalance and the sign flip are the risk control) |
| **Max positions** | 1 |
| **Expected frequency** | 12 rebalances per year, ~1-3 sign flips per year |
| **Expected holding period** | Months |

#### Reporting requirements specific to T3

T3 is only meaningful if it is reported alongside three controls:

1. **Unscaled T3** - same signal, fixed notional rather than vol-targeted. If
   scaled and unscaled results are similar, the vol scaling is not doing the
   work (good for the trend hypothesis); if scaled is much better, the result is
   a risk-management effect (Section 5.2).
2. **Buy-and-hold gold** - same period, same costs. If T3 does not beat this,
   the "momentum" is long exposure (Section 5.3).
3. **Long/short attribution** - separate P&L for long and short periods. A
   strategy that only makes money when long is a long-biased rule in disguise.

#### Falsification gates

T3 is rejected if any of the following holds on out-of-sample data:

- Net Sharpe < 0.40.
- Maximum drawdown > 25%.
- Not positive in at least 2 of the 3 macro regimes in Section 11.6.
- Fails specifically in 2011-2015 (the gold bear market) **and** the failure is
  not explained by a single outlier period.
- Returns are statistically indistinguishable from buy-and-hold gold beta.
- Scaled performance is strong but unscaled performance is not, **and** the
  document cannot articulate why vol scaling should be considered part of the
  strategy rather than a separate risk overlay.

#### Known weaknesses

- **Granularity.** At 0.01 lot the minimum position is about 1 oz. At ~15%
  realised gold volatility, a 10% vol target implies a weight of roughly 0.67x
  equity, so the 1 oz minimum only matches the target at roughly **$6,000** of
  equity (Section 7.8). Below that, the position is either zero or materially
  oversized. This is a deployment constraint, not an evidence weakness.
- **Regime dependence.** Section 5.9 suggests a 12-month rule may buy after
  large real-price run-ups, exactly when long-horizon expected returns are
  lowest.
- **Single lookback.** A 12-month lookback gives roughly one independent
  observation per year; 22 years is ~22 observations.
- **No stop.** A sustained adverse move is only exited at the next monthly
  rebalance, which can be costly in a gap.

### 8.4 T4 - Filtered trend system (complexity ablation)

**Hypothesis.** Adding regime, volatility and event filters to T1 or T2 improves
net risk-adjusted performance enough to justify the added parameters.

**What it tests.** Whether the filters that practitioners commonly add actually
add value on gold, or merely reduce trade count and increase overfitting risk.

**Grade of underlying hypothesis: E4, leaning E5.** The published evidence on
regime filters is mixed at best, and Section 5.8 implies every added filter is
another opportunity to overfit.

**T4 is not a standalone strategy.** It is a structured ablation on T1 and T2.
Running it as a separate candidate would confuse "the filters help" with "the
base strategy helps".

#### Filters to test, one at a time and then together

| Filter | Rule | Rationale |
| --- | --- | --- |
| **Trend strength** | ADX(14) > 25 | Only trade when a trend is measurably present |
| **Volatility floor** | ATR(14) percentile > 30 over trailing 252 days | Avoid dead, spread-dominated conditions |
| **Volatility ceiling** | ATR(14) percentile < 95 over trailing 252 days | Avoid panic regimes where stops gap through |
| **Session (T1 only)** | Entries only 07:00-16:00 UTC (London and New York overlap) | Section 6.6 |
| **Event blackout** | No new entries within 30 minutes of CPI, NFP or FOMC releases | Avoid slippage and gap risk around scheduled shocks |
| **Day of week** | No new entries on Friday after 18:00 UTC | Avoid weekend gap exposure and rollover spread |

#### Acceptance rule for a filter

A filter is accepted only if, on out-of-sample data, it:

- improves net profit factor by at least **10%**, **and**
- improves maximum drawdown by at least **10%**, **and**
- leaves at least **100 trades** in the sample.

Otherwise it is rejected. This rule is deliberately strict because the default
expectation (Section 5.8) is that most filters are noise.

#### Why T4 is not recommended as a primary candidate

1. **It does not test a distinct market hypothesis.** It tests whether
   complexity helps, which is a secondary question.
2. **It multiplies the search space.** Six filters, each with parameters, on top
   of T1 or T2's parameters, produces a grid large enough that a "significant"
   result is likely by chance (Section 5.8).
3. **It cannot rescue a failed base strategy.** If T2 fails, a filtered T2 that
   passes is more likely to be overfit than to be a discovery.
4. **It is better run as attribution.** After T1 and T2 are measured, the
   natural question is "which conditions drove the losses?" - and the filters
   answer that descriptively. That is a Phase 2B analysis, not a candidate.

### 8.5 Summary of the four candidates

| | **T1** | **T2** | **T3** | **T4** |
| --- | --- | --- | --- | --- |
| **Question tested** | Does intraday timing add value? | Does a simple slow daily trend rule work on XAUUSD? | Is it time-series momentum or long beta? | Do filters add value? |
| **Timeframe** | H4 / M15 | D1 | Monthly | Inherits |
| **Trades per year** | 25-120 | 2-6 | 1-3 flips | Fewer than base |
| **Holding period** | Hours-days | Months | Months | Inherits |
| **Parameters** | ~7 | ~4 | ~5 | Base + ~8 |
| **Cost sensitivity** | High | Low | Low-medium | Higher than base |
| **Evidence grade** | E4 | E2/E3 | E2/E3 | E4/E5 |
| **Overfitting risk** | High | Low | Low-medium | Very high |
| **Statistical power** | Good (many trades) | Poor (few trades) | Poor (few trades) | Worse than base |

**Deployment capital is deliberately absent from this table.** It is a
post-research consideration (Section 7) and must not influence the comparison.

---

## 9. Comparative evaluation

### 9.1 Evaluation criteria

The candidates are compared on six criteria, weighted by what actually
determines whether a Phase 2B test will produce a trustworthy answer:

| Criterion | Weight | Why it matters |
| --- | --- | --- |
| **Strength of prior evidence** | High | A test of a plausible hypothesis is more informative than a fishing expedition |
| **Cost robustness** | High | Retail XAUUSD costs are the binding constraint on fast rules |
| **Statistical power** | High | A rule with 50 trades cannot be validated in 22 years |
| **Overfitting surface** | High | Section 5.8 is the dominant practical risk |
| **Implementation simplicity** | Medium | Fewer moving parts means cleaner attribution |
| **Falsifiability** | High | A candidate that cannot fail cleanly wastes Phase 2B time |

**Deployment capital is intentionally not a criterion.** Following Section 7.1,
account size is evaluated after a candidate has already passed, and it must not
affect the research ranking.

### 9.2 Scorecard

Scores are 1 (poor) to 5 (good) **for the purpose of producing a trustworthy
Phase 2B answer**, not for expected profitability.

| Criterion | T1 | T2 | T3 | T4 |
| --- | --- | --- | --- | --- |
| Prior evidence | 2 | 4 | 3 | 1 |
| Cost robustness | 2 | 5 | 4 | 2 |
| Statistical power | 4 | 2 | 2 | 1 |
| Low overfitting surface | 2 | 5 | 4 | 1 |
| Implementation simplicity | 2 | 5 | 4 | 1 |
| Falsifiability | 4 | 4 | 3 | 1 |
| **Total (max 30)** | **16** | **25** | **20** | **7** |

### 9.3 Interpretation of the scores

**T2 scores highest (25/30).** It wins on the criteria that determine whether a
result can be trusted: strong prior, low cost sensitivity, low overfitting
surface, simple implementation. It loses on statistical power, which is a real
and unavoidable weakness. The protocol can mitigate it by reporting confidence
intervals and labelling a low-power result as inconclusive rather than as a
pass. A low-power test that is honestly reported is still useful.

**T3 scores second (20/30).** It shares T2's low cost sensitivity and relatively
low overfitting surface, and it has a strong prior. It loses on statistical power
(one observation per year) and on implementation complexity. Its unique value is
that it tests a *different* hypothesis: whether the effect is specifically
time-series momentum rather than generic trend.

**T1 scores third (16/30).** It has the best statistical power (many trades) and
the best falsifiability, which are genuine advantages. But it has the weakest
prior on gold specifically, the highest cost drag, and the largest parameter
surface. Its high trade count is a double-edged sword: it produces a precise
estimate of a possibly worthless edge.

**T4 scores lowest (7/30).** It fails almost every criterion by construction:
weakest prior, highest overfitting surface, worst implementation simplicity,
least falsifiable. This is not a criticism of the idea of filtering; it is a
criticism of testing filters as a *primary* candidate.

### 9.4 What each candidate would prove if it passed

| Candidate | If it passes | If it fails |
| --- | --- | --- |
| **T1** | Intraday timing adds value on gold beyond a daily trend bias, for this specification | This intraday timing rule does not survive retail costs on gold - consistent with Batten et al. and Jin, but not proof that every intraday trend rule fails |
| **T2** | This slow daily trend specification shows a net, out-of-sample edge on XAUUSD | This daily-EMA implementation does not survive costs on XAUUSD - evidence against this specification, not against trend following as a family |
| **T3** | Time-series momentum is present in gold and is not just long beta | This 12-month momentum specification does not transfer to a single instrument at retail scale - not a refutation of time-series momentum in general |
| **T4** | Filters improve trend systems enough to justify complexity | Filters are noise for the tested base strategies - the expected result, and a useful confirmation of Section 5.8 |

**The most valuable single test is T2**, because its failure is informative
*and cheap*. If this slow, low-parameter daily rule cannot beat buy-and-hold
gold net of costs, the project learns that **this specification** does not work
under these conditions. That does not license a conclusion about trend following
generally: a different horizon, exit, market state or implementation may behave
differently. What it does mean is that the burden of proof shifts - the next
candidate needs its own pre-registered test, not an extension of T2's grid.

### 9.5 The correlation between candidates

The candidates are not independent tests:

- **T1 and T2 share the 50/200 trend premise.** If gold trends, both should
  work; if gold does not trend, both should fail. They are correlated bets on
  the same underlying phenomenon, at different speeds.
- **T3 is partially independent.** A 12-month sign rule and a 50/200 EMA cross
  will often agree on direction but can diverge at turning points. T3 adds
  genuine information about *which* trend definition matters.
- **T4 is nested inside T1/T2** and adds no independent information.

**Consequence for multiple testing.** Running T1, T2 and T3 is roughly 2.5
independent tests, not 3. The deflation in Section 11.8 should reflect this,
and the document should state the effective number of trials rather than the
raw count.

---

## 10. Recommendation

### 10.1 The recommendation

**Backtest T2 first. Backtest T3 second. Treat T1 as a conditional incremental
test. Do not run T4 as a primary candidate.**

| Priority | Candidate | Decision | Condition |
| --- | --- | --- | --- |
| **1** | **T2** - Daily dual-EMA | **Proceed to Phase 2B** | None - this is the primary test |
| **2** | **T3** - TSMOM overlay | **Proceed to Phase 2B** | After T2 is measured, so results can be compared |
| **3** | **T1** - MTF pullback | **Conditional** | Only if T2 shows a positive trend effect, as an incremental test of whether intraday timing adds anything |
| **-** | **T4** - Filtered trend | **Deferred** | Run only as a descriptive attribution after T1/T2, never as a candidate |

### 10.2 Why T2 is first

1. **It is the cleanest test of the shared premise.** Strip away intraday timing,
   filters and volatility targeting, and what remains is: does a slow, low-cost
   daily trend rule capture anything on gold? That premise underlies every other
   candidate, so a clean answer here is the most useful single result.
2. **It has the lowest cost drag.** Roughly 2-6 flips per year means spread and
   commission are almost irrelevant. The result will be about the signal, not
   about execution.
3. **It has the smallest overfitting surface.** Four parameters, one of which
   (the EMA pair) is pre-registered with two alternatives. There is very little
   room to accidentally fit noise.
4. **Its failure is informative and cheap.** If this slow daily rule fails on 22
   years of gold, the project learns that this specification does not work under
   these costs - a clear, bounded negative result. It does not prove that trend
   following fails on gold, only that this implementation did.
5. **It matches the horizon where the literature is strongest.** Hurst et al.
   use 1/3/12-month signals; Moskowitz et al. find persistence at 1-12 months.
   T2's multi-month holding period is in the same region.

### 10.3 Why T3 is second, not first

T3 is arguably a purer test of the academic effect, and it has a strong prior.
It is second for three reasons:

1. **It requires volatility targeting**, which Section 5.2 shows can drive the
   result independently of the signal. That makes attribution harder, not
   easier.
2. **Its granularity problem is worse.** A vol-targeted position on a small
   account rounds to a size far from target, which contaminates the test. This is
   a deployment issue (Section 7), not an evidence issue, but it does affect data
   quality in a live trial.
3. **It is a better *second* question.** Once T2 has produced a clean result for
   a slow daily rule, T3 can ask whether the specific 12-month momentum
   definition adds anything beyond generic trend exposure. Asking T3 first risks
   attributing a generic trend effect to momentum specifically.

### 10.4 Why T1 is conditional, not recommended

T1 is not rejected. It is deferred behind a condition, because its value depends
on T2's result:

- **If T2 passes**, T1 becomes a legitimate incremental question: can intraday
  timing improve on the daily rule? That is worth testing, and T1's high trade
  count gives it the statistical power T2 lacks.
- **If T2 fails**, T1 does not automatically follow. A fast version of a failed
  slow rule is not evidence of an edge, and running T1 immediately as a rescue
  would turn the confirmatory phase into a search. T1 would remain a separate,
  independently pre-registered hypothesis that could be tested later; its result
  would be recorded as a new trial, not as a repair of T2.

This conditional structure is deliberate. It prevents the project from using T1
to "rescue" a failed T2 by adding speed, which is the most common form of
data-snooping in retail strategy development. It does **not** claim that T1 must
be wrong if T2 is wrong - only that T1 must earn its own test.

**A note on the roadmap.** The candidate logic named in `ROADMAP.md` for Phase 2
- higher-timeframe trend filter, lower-timeframe entry, EMA-based identification,
optional RSI confirmation, clear stop and exit - is essentially T1. This
document does not override that. It tests the roadmap's candidate, but
*recommends* sequencing it behind a cheaper test of the same underlying premise.
The recommendation is advice to the project owner, not a governance decision:
`ROADMAP.md` remains authoritative (Section 10.8).

### 10.5 Why T4 is not a candidate

T4 is excluded as a primary candidate for the reasons in Section 8.4. It remains
in the document for two purposes:

1. **As a pre-registered ablation** to run after T1/T2, answering "which
   conditions drove the results?"
2. **As a guard against complexity creep.** By specifying the acceptance rule
   in advance (10% PF, 10% DD, 100 trades), the project commits to rejecting
   filters that do not clear a real bar.

### 10.6 What the recommendation does not say

- It does not say T2 will be profitable. It says T2 is the most informative test.
- It does not say T1 is worthless. It says T1's value is conditional.
- It does not say trend following works on gold. It says the diversified
  evidence is strong enough to justify one clean single-instrument test.
- It does not say anything about account size. Section 7 is a deployment case
  study and is deliberately excluded from candidate selection (Section 7.1).

### 10.7 Decision record

| Decision | Rationale | Reversible? |
| --- | --- | --- |
| T2 first | Cleanest, cheapest, most robust test of the core hypothesis | Yes, if data quality fails |
| T3 second | Tests a distinct, well-documented effect | Yes |
| T1 conditional on T2 | Prevents rescuing a failed trend premise with speed | Yes, if T2 shows a positive effect |
| T4 deferred | Highest overfitting surface, no independent hypothesis | Yes, as ablation only |
| No MQL5 in Phase 2A | Roadmap constraint; research precedes implementation | No |
| No parameter optimisation in Phase 2A | Pre-registration requires parameters to be fixed before results | No |

### 10.8 Governance: research recommendation versus roadmap

`ROADMAP.md` is authoritative for project scope and phase ordering. This
document does not modify it and cannot override it.

| Question | Authority | Status in this document |
| --- | --- | --- |
| Which strategy families exist | `ROADMAP.md` | Unchanged |
| Which candidate is tested first | `ROADMAP.md`, informed by this research | **Recommendation only** |
| Candidate rules and parameters | This document (Sections 8 and 11.7) | Proposed, pre-registered |
| Pass/fail gates | This document (Section 8) | Proposed, pre-registered |
| Phase ordering and start dates | `ROADMAP.md` | Unchanged |

**If the roadmap mandates a particular candidate order, the roadmap prevails.**
In that case this document's recommendation is recorded as a dissent with its
reasons, and the test proceeds in the mandated order using the corresponding
specification and gates from this document. No governance decision is made in
code, and no phase is started outside the roadmap.

This is stated explicitly because there is a genuine tension: the roadmap's Phase
2 candidate logic is closest to T1, while the evidence in Sections 4, 5 and 9
points to T2 as the more informative first test. That tension should be resolved
by the project owner, in writing, before Phase 2B begins - not silently by
whichever document was edited most recently.

---

## 11. Proposed Phase 2B backtest protocol

This section is written **before any backtest is run**. Its purpose is to make
the test falsifiable and to prevent the most common failure mode in retail
strategy development: running many variants, then reporting the one that worked.

Everything in this section is a commitment. If Phase 2B deviates, the deviation
must be recorded with a reason, and the result must be labelled exploratory
rather than confirmatory.

### 11.1 Data requirements

| Requirement | Specification | Reason |
| --- | --- | --- |
| **Instrument** | XAUUSD spot | Matches the traded instrument |
| **Period** | 2004-01-01 to 2026-06-30 | Covers multiple full cycles including the 2011-2015 bear market |
| **Granularity** | M1 for intraday execution; D1 for daily signals | M1 allows realistic intrabar stop handling |
| **Bid/ask** | Separate bid and ask series, or a documented spread model | Stops trigger on the correct side |
| **Ticks** | Real ticks preferred; M1 OHLC acceptable for daily-only rules with stress testing | Section 11.5 |
| **Corporate actions** | Not applicable to spot gold | - |
| **Gaps** | Preserved, not forward-filled | Weekend and holiday gaps are real risk |

**Why 2004?** The gold ETF complex launched in late 2004, which coincides with
the modern retail XAUUSD market and with reasonably reliable broker data. Data
before 2004 exists (LBMA fixings go back much further) but is not representative
of retail execution conditions.

### 11.2 Data sources and cross-validation

| Source | Use | Role |
| --- | --- | --- |
| **Exness MT5, real ticks** | Primary backtest data | Matches the target broker |
| **Dukascopy tick data** | Independent cross-check | Detects vendor-specific artefacts |
| **LBMA Gold Price PM** | Daily reference close | Validates the daily series and detects obvious errors |
| **COMEX GC futures** | Signal robustness | Tests whether results depend on spot-specific microstructure |

**Cross-validation rule.** If the daily series from the broker differs from the
LBMA PM fix by more than 1% on more than 0.5% of days, the data is rejected and
the discrepancy is investigated before any backtest.

**Futures cross-check.** T2 and T3 should be re-run on COMEX GC continuous
futures. If the sign of the result flips between spot and futures, the finding
is instrument-specific and must be reported as such.

### 11.3 Sample split

| Window | Dates | Purpose |
| --- | --- | --- |
| **In-sample (IS)** | 2004-01-01 to 2016-12-31 | Parameter selection and model development |
| **Out-of-sample (OOS)** | 2017-01-01 to 2026-06-30 | Confirmatory evaluation only |
| **Holdout** | 2022-01-01 to 2026-06-30 | Structural-break check; not used for selection |

The OOS period contains a full cycle: the 2018-2020 rally, the 2021 drawdown,
the 2022 real-yield break, and the 2024-2026 record run. This is deliberate - a
OOS period consisting only of a bull market would not test the rule.

**Subperiods for attribution** (reported separately, never used for selection):

| Subperiod | Character |
| --- | --- |
| 2004-2007 | Secular bull, weak dollar, pre-crisis |
| 2008-2011 | Crisis, QE, gold peak |
| 2012-2015 | Bear market, taper, strong dollar |
| 2016-2018 | Range, reflation |
| 2019-2020 | Pandemic shock and stimulus |
| 2021-2023 | Drawdown, then real-yield regime break |
| 2024-2026 | Record highs, central-bank-led demand |

**Rule.** If a candidate only passes because of one subperiod, that is reported
as **CONDITIONAL**, not PASS.

### 11.4 Cost model

Costs are the most common source of backtest inflation. The model must be
explicit and stress-tested.

| Cost | Baseline assumption | Stress assumption | Notes |
| --- | --- | --- | --- |
| **Spread** | Measured distribution by hour and session from broker data | 1.5x and 2.0x measured | Do not use a single average; use the actual distribution |
| **Commission** | Actual broker schedule | 1.5x | ~$7 per 100 oz round turn on a raw account |
| **Swap** | Actual broker schedule, applied daily at rollover | 1.5x | Critical for T2/T3 multi-month holds |
| **Slippage** | 0.5 x spread on market entries; 1.0 x spread on stop exits | 2.0x | Stops slip more than entries |
| **Gap slippage** | Modelled from historical weekend and news gaps | - | Stops fill at the gap price, not the stop price |

**Excluded observation.** The abnormal Phase 0 spread reading (Section 6.8.2)
must not be used as the baseline, as a stress level, or as a spread-filter
setting. The baseline must come from measured active-market quotes.

**Cost stress rule.** Every candidate must be reported at baseline, 1.5x and
2.0x costs. A candidate that only passes at baseline costs is **rejected**.

**Why this matters.** Section 7.5 shows a $5 stop loses 5.4% of its risk to a
20-point spread before slippage. At 2x costs that becomes ~11%. Any rule with a
tight stop must clear that bar.

### 11.5 Execution model

| Rule | Specification |
| --- | --- |
| **Signal timing** | Signals computed on closed bars only |
| **Entry price** | Next bar open after the signal bar closes |
| **Stop handling** | Intrabar, using bid for longs and ask for shorts |
| **Stop priority** | If a bar contains both stop and target, assume stop first (conservative) |
| **Gap handling** | If the open is beyond the stop, fill at the open |
| **No look-ahead** | No use of the signal bar's high/low for entry price |
| **No partial fills** | Assume full fill at modelled price; note as a limitation |
| **Rollover** | No new entries within 15 minutes of daily rollover |

**Tester mode.** "Every tick based on real ticks" is preferred. "1 minute OHLC"
is acceptable only for daily-signal strategies and only if results are shown to
be insensitive to intrabar assumptions. "Open prices only" is not acceptable for
any candidate with a stop.

### 11.6 Regime definitions

Two independent regime lenses are used, because a single one can be gamed.

**Lens A - volatility quartiles.** Trailing 60-day realised volatility,
classified into quartiles over a rolling 5-year window:

| Regime | Definition |
| --- | --- |
| **V1 - quiet** | Bottom quartile |
| **V2 - normal** | Second quartile |
| **V3 - elevated** | Third quartile |
| **V4 - stress** | Top quartile |

**Lens B - macro regimes.** Hand-labelled from the historical record:

| Regime | Dates | Character |
| --- | --- | --- |
| **M1 - secular bull** | 2004-2011 | Weak dollar, rising investment demand, GFC |
| **M2 - bear / range** | 2012-2015 | Taper, strong dollar, ETF outflows |
| **M3 - reflation / range** | 2016-2019 | Mixed, low real yields late in period |
| **M4 - shock and stimulus** | 2020-2021 | Pandemic, massive fiscal and monetary response |
| **M5 - regime break** | 2022-2026 | Real-yield relationship weakened, central-bank demand |

**Reporting rule.** Every candidate reports performance by both lenses. A rule
that only works in V4/M4 is a crisis rule, not a trend rule, and must be labelled
as such.

### 11.7 Pre-registered parameter grids

These grids are fixed **before** any result is seen. Every combination is run
and reported. No parameter outside these grids may be tested in the confirmatory
phase; any additional test is exploratory and labelled as such.

**T1 - MTF pullback**

| Parameter | Values |
| --- | --- |
| H4 EMA pair | (50, 200) only |
| Pullback distance | 0.2, 0.5 x ATR(14, H1) |
| Stop multiple | 1.0, 1.5 x ATR(14, H1) |
| Trail multiple | 2.0 x ATR(14, H1) only |
| RSI filter | off, on |

That is 2 x 2 x 2 = 8 combinations.

**T2 - Daily dual-EMA**

| Parameter | Values |
| --- | --- |
| EMA pair | (20, 100), (50, 200), (100, 400) |
| Disaster stop | 2.0, 3.0, 4.0 x ATR(14, D1) |
| Risk fraction | 0.5%, 1.0% |

That is 3 x 3 x 2 = 18 combinations.

**T3 - TSMOM overlay**

| Parameter | Values |
| --- | --- |
| Lookback | 6, 12, 24 months |
| Volatility estimate | 60-day EWMA only |
| Target vol | 10% only |
| Leverage cap | 2.0x only |
| Scaling | scaled, unscaled |

That is 3 x 2 = 6 combinations.

**T4 - Filters** (ablation only, not a candidate)

Six filters, each tested individually on the best T1 and best T2
configuration, then all together. 7 tests per base.

**Total confirmatory trials:** 8 + 18 + 6 = 32, plus 14 ablation tests. The
effective number of independent tests is lower (Section 9.5), but the raw count
is what must be disclosed.

### 11.8 Multiple testing and deflation

With 32+ trials, the best result is expected to look good by chance. Three
corrections are mandatory:

| Method | Purpose | Threshold |
| --- | --- | --- |
| **Deflated Sharpe ratio** (Bailey & López de Prado 2014) | Adjusts Sharpe for number of trials, skew, kurtosis, sample length | p < 0.10 to pass |
| **White's Reality Check** (White 2000) | Tests whether the best rule beats the benchmark after snooping | p < 0.10 to pass |
| **Harvey-Liu-Zhu haircut** (2016) | Raises the t-statistic bar for multiple testing | t > 3.0 for a new claim |

**Disclosure rule.** The report must include a table of **all** trials, with
net Sharpe, net profit factor, maximum drawdown and trade count for each. A
result that only appears in the text, without the full table, is not accepted.

**Effective trials note.** Because T1 and T2 are correlated (Section 9.5), the
effective number of independent trials is closer to 15-20 than 32. The deflation
should use the conservative (higher) number, not the lower one.

### 11.9 Metrics

Every candidate reports the standard roadmap report plus the following:

**Return and risk**

| Metric | Definition |
| --- | --- |
| CAGR | Compound annual growth rate, net |
| Sharpe ratio | Annualised, net of costs, on daily returns |
| Sortino ratio | Downside-deviation adjusted |
| MAR ratio | CAGR / maximum drawdown |
| Ulcer index | Depth and duration of drawdowns |
| Maximum drawdown | Peak-to-trough, net |
| Max DD duration | Time from peak to recovery |
| Calmar ratio | CAGR / max DD |

**Trade statistics**

| Metric | Definition |
| --- | --- |
| Trade count | Total closed trades |
| Win rate | Percent profitable |
| Expectancy | Average net P&L per trade, in R |
| Payoff ratio | Average win / average loss |
| Average holding period | In days |
| Turnover | Round trips per year |
| Total costs | Sum of spread, commission, swap, slippage |
| Cost as % of gross P&L | The key cost-robustness number |

**Attribution**

| Metric | Definition |
| --- | --- |
| Long P&L | P&L from long positions only |
| Short P&L | P&L from short positions only |
| Beta to buy-and-hold gold | Regression of strategy returns on gold returns |
| Alpha vs buy-and-hold | Intercept from that regression |
| Exposure | Average fraction of time in market |
| Performance by regime | Both lenses from 11.6 |
| Performance by year | Calendar-year returns |
| Start-date sensitivity | Results for starting in each year 2004-2010 |

**Statistical**

| Metric | Definition |
| --- | --- |
| Bootstrap confidence intervals | 95% CI on Sharpe and CAGR, block bootstrap |
| Deflated Sharpe | As above |
| Reality Check p-value | As above |
| Probability of backtest overfitting | As per Bailey et al. (2014) |

### 11.10 Benchmarks and controls

A candidate that beats zero has proven nothing. Every candidate is compared
against four controls:

| Control | Purpose | What a pass requires |
| --- | --- | --- |
| **Buy-and-hold gold** | Separates trend alpha from long gold beta | Higher Sharpe, or similar Sharpe with materially lower drawdown |
| **60/40 portfolio** | Context for risk-adjusted return | Not required to beat, but reported |
| **Random entry, same exposure** | Tests whether the signal matters at all | Candidate must beat the 95th percentile of random-entry runs |
| **Always-long, same vol target** | Tests whether the short side or the timing adds value | Candidate must beat this on Sharpe, not just on return |

**The random-entry control is the most important.** It holds exposure, holding
period and costs constant and randomises only the entry timing. If a trend rule
cannot beat random entry with the same exposure, the "trend" component is not
doing any work - it is just a long-biased exposure profile.

### 11.11 Mandatory reporting template

Every completed Phase 2B trial must be reported in the structure below. A trial
that omits any mandatory field is not accepted as evidence and is recorded as
incomplete.

#### 11.11.1 Test identity

| Field | Required content |
| --- | --- |
| **Trial ID** | Unique identifier, e.g. `T2-IS-50-200-3.0-1.0` |
| **Strategy hypothesis** | One sentence stating what this trial tests |
| **Exact parameter set** | Every parameter value, no omissions, no "defaults" |
| **Data source** | Vendor, feed and retrieval date |
| **Symbol** | Exact broker symbol name and contract specification used |
| **Timeframe** | Signal timeframe and execution timeframe |
| **Test period** | Full date range |
| **In-sample period** | Exact dates |
| **Out-of-sample period** | Exact dates |

#### 11.11.2 Capital and execution assumptions

| Field | Required content |
| --- | --- |
| **Initial capital** | Fixed amount, stated in account currency |
| **Position sizing method** | Fixed-fractional / volatility-targeted / fixed-lot, with formula |
| **Lot and contract assumptions** | Contract size, minimum volume, volume step used |
| **Spread assumption** | Distribution or value, and its source |
| **Slippage assumption** | Entry and stop-exit slippage, and its source |
| **Commission assumption** | Per-lot or per-trade, per side or round turn |
| **Swap / financing assumption** | Schedule applied, and whether it is included |
| **Other transaction costs** | Any additional charge modelled |
| **Execution model** | Bar open / intrabar, and tester mode used |

#### 11.11.3 Performance

| Metric | Unit |
| --- | --- |
| Final equity | Account currency |
| Net profit | Account currency |
| Return | % |
| Profit factor | Ratio |
| Maximum drawdown | Account currency |
| Maximum drawdown | % |
| Number of trades | Count |
| Win rate | % |
| Average win | Account currency and R |
| Average loss | Account currency and R |
| Largest win | Account currency |
| Largest loss | Account currency |
| Maximum consecutive wins | Count |
| Maximum consecutive losses | Count |

Additional reporting required by Section 11.9 (CAGR, Sharpe, Sortino, MAR,
Ulcer, expectancy, payoff, holding period, turnover, total costs, cost as % of
gross P&L, long and short attribution, beta and alpha versus buy-and-hold).

#### 11.11.4 Benchmark and control comparison

| Comparison | Required |
| --- | --- |
| Buy-and-hold return | Yes |
| Buy-and-hold maximum drawdown | Yes |
| Random-entry, matched-exposure result | Yes - median and 95th percentile of runs |
| Strategy versus buy-and-hold | Explicit statement, with the metric used |
| Strategy versus random-entry control | Explicit statement, with the metric used |

#### 11.11.5 Robustness

| Test | Required output |
| --- | --- |
| Cost 1.0x | Full performance table |
| Cost 1.5x | Full performance table |
| Cost 2.0x | Full performance table |
| Parameter sensitivity | Performance across the pre-registered grid |
| Sub-period performance | All seven subperiods from Section 11.3 |
| In-sample versus out-of-sample | Side-by-side, never blended |
| Regime attribution | Both lenses from Section 11.6 |

#### 11.11.6 Statistical and research tests

Where applicable, and mandatory for any PASS or CONDITIONAL verdict:

| Test | Requirement |
| --- | --- |
| Deflated Sharpe Ratio | Reported with its p-value and the trial count used |
| White's Reality Check | Reported with its p-value |
| Multiple-testing statement | Number of trials run, effective trials, and the adjustment applied |
| Bootstrap confidence intervals | 95% CI on Sharpe and CAGR |

#### 11.11.7 Final decision

Exactly one verdict must be recorded:

| Verdict | Meaning |
| --- | --- |
| **PASS** | All pre-registered gates met on out-of-sample data, including cost stress and statistical tests |
| **CONDITIONAL** | Gates met only with a stated qualification, such as dependence on one subperiod or on baseline costs |
| **FAIL** | One or more pre-registered gates failed |
| **INCONCLUSIVE** | Sample too small, data inadequate, or result not separable from noise - explicitly not a pass |

Every verdict must be followed by a short evidence-based reason that cites the
specific metrics and gates, not a general impression.

#### 11.11.8 Context fields (not gates)

The following are reported for completeness but must **not** affect the verdict:

- Implied deployment equity, from Section 7 arithmetic at the tested risk
  fraction.
- Broker-specific execution notes.
- Any deviation from this protocol, with its reason and its effect on
  interpretation.

### 11.12 Kill criteria and stopping rules

| Situation | Action |
| --- | --- |
| Candidate fails its gates on OOS | Record as failed. Do not re-tune on OOS. |
| Candidate passes IS but fails OOS | Record as overfit. Do not expand the grid. |
| Fewer than 100 trades for T2/T3 | Report as **inconclusive**, not pass or fail |
| Cost stress at 1.5x flips the sign | Record as cost-fragile; reject |
| Result depends on one subperiod | CONDITIONAL only |
| Data quality check fails | Stop. Fix data before any conclusion. |
| A candidate only passes after adding a filter | Reject the candidate; report the filter as an exploratory finding |

**The most important stopping rule:** once the OOS period has been examined, it
is spent. Any subsequent change to the rules turns the OOS period into an
in-sample period. The project gets one clean OOS look per candidate.

### 11.13 Protocol status: no change proposed

This revision of the document **does not propose any change** to the
pre-registered Phase 2B protocol. The following commitments are preserved
exactly as previously defined:

| Commitment | Value | Status |
| --- | --- | --- |
| Data split | In-sample 2004-2016; out-of-sample 2017-2026 | Unchanged |
| Confirmatory trials | 32 (T1: 8, T2: 18, T3: 6) | Unchanged |
| Cost stress | 1.0x, 1.5x, 2.0x | Unchanged |
| Deflated Sharpe Ratio | Required for PASS/CONDITIONAL | Unchanged |
| White's Reality Check | Required for PASS/CONDITIONAL | Unchanged |
| Buy-and-hold benchmark | Required | Unchanged |
| Random-entry matched-exposure control | Required | Unchanged |
| OOS examined once | Enforced | Unchanged |

If a future revision judges that a methodological change is necessary, it must
**not** be applied silently. It must be recorded in a section titled
`Proposed Protocol Change`, containing:

1. What is being changed.
2. Why the change is necessary.
3. What evidence supports the change.
4. Which trials, results and conclusions would be affected.

Such a change is not implemented until it has been explicitly approved. None is
proposed here.

---

## 12. Threats to validity

This section lists what could make the Phase 2B conclusions wrong, and what
mitigates each threat.

### 12.1 Threats to internal validity

| Threat | Description | Mitigation |
| --- | --- | --- |
| **Look-ahead bias** | Using information not available at decision time | Closed-bar signals, next-bar execution, code review of signal timing |
| **Survivorship / vendor bias** | Broker data may be cleaned or interpolated | Cross-check against Dukascopy and LBMA fixes |
| **Intrabar ambiguity** | M1 OHLC cannot resolve tick-level stop order | Use real ticks; stress test with pessimistic stop priority |
| **Cost understatement** | Backtest costs lower than live | Measure from broker data; stress at 2x; report cost as % of gross |
| **Swap omission** | Multi-month holds ignore financing | Model actual swap schedule; report with and without |
| **Parameter leakage** | Parameters chosen with knowledge of OOS | Pre-registered grids; OOS examined once |
| **Multiple testing** | Best of 32 trials looks good by chance | Deflated Sharpe, Reality Check, full trial disclosure |

### 12.2 Threats to external validity

| Threat | Description | Mitigation |
| --- | --- | --- |
| **Single instrument** | Results may not generalise beyond XAUUSD | Futures cross-check; acknowledge limitation |
| **Single broker** | Spreads and execution are broker-specific | Report broker; cross-check with a second feed |
| **Period specificity** | 2004-2026 includes unusual gold behaviour | Subperiod attribution; regime tests; explicit 2022-2026 break analysis |
| **Structural break** | Central-bank demand may have changed gold permanently | Separate 2022-2026 evaluation; do not extrapolate pre-2022 relationships |
| **Regime change after the sample** | The next decade may differ | State the conditional nature of all conclusions |

### 12.3 Threats to construct validity

| Threat | Description | Mitigation |
| --- | --- | --- |
| **Trend alpha vs long beta** | A long-biased rule looks like trend skill in a bull market | Buy-and-hold and always-long controls; long/short attribution |
| **Vol scaling vs signal** | Vol targeting drives results independently of direction | Scaled vs unscaled comparison for T3 |
| **Few trades** | T2/T3 have low statistical power | Report confidence intervals; label inconclusive rather than pass |
| **Overlapping trades** | Multi-month trades are not independent observations | Block bootstrap; do not treat trade count as sample size |
| **Benchmark choice** | Different benchmarks give different verdicts | Report all four controls, not a selected one |

### 12.4 Threats specific to this project

| Threat | Description | Mitigation |
| --- | --- | --- |
| **Deployment capital** | A passing candidate may be impractical to fund at the tested risk fraction (Section 7) | Report implied deployment equity as context only; it must not affect the verdict |
| **Contract specification** | Phase 0 observed 100 oz on one broker; another account may differ | Read the symbol at runtime; verify before any deployment decision |
| **Phase 1 execution constraints** | Execution engine may not support all candidate requirements | Review Phase 1 API before implementation; do not modify EA in Phase 2A |
| **Data licensing** | Real tick data may be limited in history | Verify available history before committing to 2004 start |
| **Researcher degrees of freedom** | The person running the test also wrote the protocol | Pre-registration, full disclosure, external review of the report |

### 12.5 What would falsify this document's recommendation

The recommendation to test T2 first would be wrong if:

- Daily gold data of adequate quality is not available before 2010, making the
  regime tests impossible.
- The Phase 1 execution engine cannot support daily-bar signals at the next
  open without modification, which is out of scope for Phase 2B.
- A prior, credible, published study already tests exactly this rule on XAUUSD
  and finds a clear negative result. (No such study was found in this review;
  if one exists, it should be added.)

The recommendation to treat T3 as second would be wrong if vol scaling turns
out to be inseparable from the signal in a way that makes attribution
impossible. That would downgrade T3 to exploratory.

The recommendation to defer T1 would be wrong if T2's trades are so few that its
confidence intervals span zero, in which case T1's higher trade count becomes
the only way to get a statistically usable answer - but only as a *different*
test, not as a rescue.

---

## 13. References

References are grouped by type. Industry sources are included only where no
peer-reviewed equivalent exists, and they are labelled as such throughout the
document. DOIs are given where available.

### 13.1 Peer-reviewed academic literature

1. **Auer, B. R.** (2021). Have trend-following signals in commodity futures
   markets become less reliable in recent years? *Financial Markets and
   Portfolio Management*, 35(4), 533-553.
   https://doi.org/10.1007/s11408-021-00385-5

2. **Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J.** (2014).
   Pseudo-mathematics and financial charlatanism: The effects of backtest
   overfitting on out-of-sample performance. *Notices of the American
   Mathematical Society*, 61(5), 458-471.

3. **Bailey, D. H., & López de Prado, M.** (2014). The deflated Sharpe ratio:
   Correcting for selection bias, backtest overfitting, and non-normality.
   *Journal of Portfolio Management*, 40(5), 94-107.

4. **Bajgrowicz, P., & Scaillet, O.** (2012). Technical trading revisited: False
   discoveries, persistence tests, and transaction costs. *Journal of Financial
   Economics*, 106(3), 473-491.
   https://doi.org/10.1016/j.jfineco.2012.06.001

5. **Barsky, R. B., & Summers, L. H.** (1988). Gibson's paradox and the gold
   standard. *Journal of Political Economy*, 96(3), 528-550.

6. **Batten, J. A., Lucey, B. M., McGroarty, F., Peat, M., & Urquhart, A.**
   (2018). Does intraday technical trading have predictive power in precious
   metal markets? *Journal of International Financial Markets, Institutions and
   Money*, 52, 102-113. https://doi.org/10.1016/j.intfin.2017.06.005

7. **Baur, D. G., Dichtl, H., Drobetz, W., & Wendt, V.-S.** (2020). Investing in
   gold - Market timing or buy-and-hold? *International Review of Financial
   Analysis*, 71, 101281. https://doi.org/10.1016/j.irfa.2018.11.008

8. **Baur, D. G., & McDermott, T. K.** (2010). Is gold a safe haven?
   International evidence. *Journal of Banking & Finance*, 34(8), 1886-1898.

9. **Dichtl, H.** (2020). Forecasting excess returns of the gold market: Can we
   learn from stock market predictions? *Journal of Commodity Markets*, 19,
   100106. https://doi.org/10.1016/j.jcomm.2019.100106

10. **Erb, C. B., & Harvey, C. R.** (2013). The golden dilemma. *Financial
    Analysts Journal*, 69(4), 10-42.
    https://doi.org/10.2469/faj.v69.n4.1

11. **Fung, W., & Hsieh, D. A.** (2001). The risk in hedge fund strategies:
    Theory and evidence from trend followers. *Review of Financial Studies*,
    14(2), 313-341. https://doi.org/10.1093/rfs/14.2.313

12. **Georgopoulou, A., & Wang, J.** (2017). The trend is your friend:
    Time-series momentum strategies across equity and commodity markets.
    *Review of Finance*, 21(4), 1557-1592.

13. **Goyal, A., & Jegadeesh, N.** (2018). Cross-sectional and time-series tests
    of return predictability: What is the difference? *Review of Financial
    Studies*, 31(5), 1784-1824.

14. **Harvey, C. R., & Liu, Y.** (2015). Backtesting. *Journal of Portfolio
    Management*, 42(1), 13-28.
    https://doi.org/10.3905/jpm.2015.42.1.013

15. **Harvey, C. R., Liu, Y., & Zhu, H.** (2016). ... and the cross-section of
    expected returns. *Review of Financial Studies*, 29(1), 5-68.

16. **Huang, D., Li, J., Wang, L., & Zhou, G.** (2020). Time series momentum: Is
    it there? *Journal of Financial Economics*, 135(3), 774-794.
    https://doi.org/10.1016/j.jfineco.2019.08.004

17. **Hurst, B., Ooi, Y. H., & Pedersen, L. H.** (2017). A century of evidence on
    trend-following investing. *Journal of Portfolio Management*, 44(1), 15-29.
    https://doi.org/10.3905/jpm.2017.44.1.015

18. **Jin, X.** (2022). Performance of intraday technical trading in China's gold
    market. *Journal of International Financial Markets, Institutions and
    Money*, 76, 101481. https://doi.org/10.1016/j.intfin.2021.101481

19. **Kaminski, K. M., & Lo, A. W.** (2014). When do stop-loss rules stop
    losses? *Journal of Financial Markets*, 18, 234-254.
    https://doi.org/10.1016/j.finmar.2013.07.001

20. **Kim, A. Y., Tse, Y., & Wald, J. K.** (2016). Time series momentum and
    volatility scaling. *Journal of Financial Markets*, 30, 103-124.
    https://doi.org/10.1016/j.finmar.2016.05.003

21. **Lempérière, Y., Deremble, C., Seager, P., Potters, M., & Bouchaud, J.-P.**
    (2014). Two centuries of trend following. *Journal of Investment
    Strategies*, 3(3), 41-61. arXiv:1404.3274.

22. **Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H.** (2012). Time series
    momentum. *Journal of Financial Economics*, 104(2), 228-250.
    https://doi.org/10.1016/j.jfineco.2011.11.003

23. **O'Connor, F. A., Lucey, B. M., Batten, J. A., & Baur, D. G.** (2015). The
    financial economics of gold - A survey. *International Review of Financial
    Analysis*, 41, 186-205.

24. **Park, C.-H., & Irwin, S. H.** (2007). What do we know about the
    profitability of technical analysis? *Journal of Economic Surveys*, 21(4),
    786-826.

25. **Pukthuanthong, K., & Roll, R.** (2011). Gold and the dollar (and the euro,
    pound, and yen). *Journal of Banking & Finance*, 35(8), 2070-2083.

26. **Sullivan, R., Timmermann, A., & White, H.** (1999). Data-snooping,
    technical trading rule performance, and the bootstrap. *Journal of
    Finance*, 54(5), 1647-1691.

27. **Szakmary, A. C., Shen, Q., & Sharma, S. C.** (2010). Trend-following
    trading strategies in commodity futures: A re-examination. *Journal of
    Banking & Finance*, 34(2), 409-426.

28. **Tully, E., & Lucey, B. M.** (2007). A power GARCH examination of the gold
    market. *Research in International Business and Finance*, 21(2), 316-325.

29. **White, H.** (2000). A reality check for data snooping. *Econometrica*,
    68(5), 1097-1126.

### 13.2 Industry and institutional sources

These are used for factual market data and for practitioner experience where no
peer-reviewed source exists. They are not used to support statistical claims
about trend-following profitability.

30. **World Gold Council.** *Gold Demand Trends: Full Year 2024.*
    https://www.gold.org/goldhub/research

31. **World Gold Council.** *Gold Demand Trends: Full Year 2025.*
    https://www.gold.org/goldhub/research

32. **World Gold Council.** *Gold Demand Trends: Q1 2026.*
    https://www.gold.org/goldhub/research

33. **World Gold Council.** *Gold Demand Trends: Q2 2026* and *Central Bank
    Gold Reserves Survey 2026.* https://www.gold.org/goldhub/research

34. **Palmberg, J.** (2025). *Gold's long-run returns.* SUERF Policy Brief
    No. 1119. https://www.suerf.org/publications/suerf-policy-notes-and-briefs/

35. **Man Group.** *The need for speed in trend-following strategies.*
    Man Institute.

36. **Welton Investment Partners.** (2019). *Trend following: A decade of
    disappointment?*

37. **SG Trend Index** performance data, as reported by Top Traders Unplugged
    (December 2025).

38. **Janus Henderson, RBC Wealth Management, and PIMCO** commentary on the
    gold-real yield relationship after 2022.

### 13.3 Technical documentation

39. **MetaTrader 5.** *Strategy Tester documentation* - testing modes ("Every
    tick based on real ticks", "1 minute OHLC", "Open prices only").
    https://www.metatrader5.com/en/terminal/help/algotrading/testing

### 13.4 Project documents

40. **Gold EA project.** `ROADMAP.md` - phase structure and constraints.
41. **Gold EA project.** `Docs/Phase-1-Execution-Engine.md` - execution and risk
    engine specification.
42. **Gold EA project.** `README.md` - repository structure and status.

---

## 14. Claim ledger

Every substantive claim, its grade, its source, and where it is used. This table
exists so that a reviewer can challenge a specific claim without re-reading the
document.

### 14.1 Claims about trend following

| # | Claim | Grade | Source | Used in |
| --- | --- | --- | --- | --- |
| C1 | Trend following has produced positive average returns for over a century across many markets | E2 | Hurst et al. 2017; Lempérière et al. 2014 | 2.1, 4.1, 10.2 |
| C2 | The effect appears in every decade of a 137-year sample | E2 | Hurst et al. 2017 | 4.1 |
| C3 | 12-month time-series momentum was positive for all 58 futures contracts studied | E2 | Moskowitz et al. 2012 | 4.1 |
| C4 | Average per-market trend Sharpe is approximately 0.4 | E2 | Hurst et al. 2017 | 4.2, 9.2 |
| C5 | Trend following performs relatively well in extreme markets | E2 | Hurst et al. 2017; Fung & Hsieh 2001; Moskowitz et al. 2012 | 4.3 |
| C6 | Trend-following returns are option-like and better explained by lookback straddles | E2 | Fung & Hsieh 2001 | 4.3 |
| C7 | Commodity trend rules were profitable net of costs in at least 22 of 28 markets | E2 | Szakmary et al. 2010 | 4.4 |
| C8 | Time-series momentum appears across equities, currencies, bonds and commodities | E2 | Georgopoulou & Wang 2017 | 4.5 |
| C9 | Commodity trend-signal reliability has not significantly decayed in recent years | E3 | Auer 2021 | 4.6 |
| C10 | Time-series momentum is statistically fragile; most individual assets show t < 1.65 | E3 | Huang et al. 2020 | 2.1, 5.1 |
| C11 | TSMOM performance is similar to a historical-sample-mean strategy | E3 | Huang et al. 2020 | 5.1 |
| C12 | Much of TSMOM alpha is driven by volatility scaling | E2 | Kim, Tse & Wald 2016 | 5.2, 8.3, 10.3 |
| C13 | Unscaled TSMOM alphas are similar to unscaled buy-and-hold | E2 | Kim, Tse & Wald 2016 | 5.2 |
| C14 | The TS vs CS momentum difference is largely time-varying net long exposure | E2 | Goyal & Jegadeesh 2018 | 5.3 |
| C15 | Trend-following industry returns were poor through the 2010s | E2 (descriptive) | SG Trend Index; Welton 2019 | 5.5 |
| C16 | Faster trend has materially lower net risk-adjusted returns | E2 | Man Group | 5.6, 8.1 |
| C17 | Stop-losses reduce expected return under a random walk and add value only with momentum | E2 | Kaminski & Lo 2014 | 5.7, 8.2 |
| C18 | Overfitting is the dominant practical risk in rule discovery | E1 (methodological) | Sullivan et al. 1999; White 2000; Bajgrowicz & Scaillet 2012; Bailey et al. 2014 | 5.8, 11.8 |
| C19 | No ex-ante ability to select future best technical rules | E2 | Bajgrowicz & Scaillet 2012 | 5.8 |
| C20 | New factors should clear t > 3 | E2 | Harvey, Liu & Zhu 2016 | 5.8, 11.8 |

### 14.2 Claims about gold

| # | Claim | Grade | Source | Used in |
| --- | --- | --- | --- | --- |
| C21 | Standard MA rules have no predictive power in precious metals intraday | E2 | Batten et al. 2018 | 2.1, 5.4, 8.1 |
| C22 | Longer MA parameters perform better than shorter ones in precious metals | E2 | Batten et al. 2018 | 5.4, 8.2 |
| C23 | Intraday technical trading in Chinese gold shows no persistent out-of-sample performance | E2 | Jin 2022 | 2.1, 5.4 |
| C24 | Technical indicators do not improve gold excess-return forecasts | E2 | Dichtl 2020 | 2.1, 5.4 |
| C25 | Gold timing strategies are not robust to data-snooping biases | E2 | Baur et al. 2020 | 2.1, 5.4 |
| C26 | Gold is a hedge and safe haven, especially in extreme equity downturns | E1 | Baur & McDermott 2010 | 6.1 |
| C27 | Real interest rates are inversely related to the real gold price | E1 | Barsky & Summers 1988; Erb & Harvey 2013 | 6.1 |
| C28 | The gold-real-yield relationship weakened after 2022 | E3 | Janus Henderson; RBC; PIMCO | 6.2, 11.6 |
| C29 | Central-bank purchases averaged ~1,000 t/year in 2022-2024 vs ~500 t prior | E1 | World Gold Council | 6.2, 6.3 |
| C30 | Central banks bought ~1,045 t in 2024, the third consecutive year above 1,000 t | E1 | World Gold Council | 6.3 |
| C31 | Total gold demand including OTC exceeded 5,000 t in 2025 | E1 | World Gold Council | 6.4 |
| C32 | Gold exhibits volatility clustering and asymmetric volatility | E2 | Tully & Lucey 2007 | 6.5 |
| C33 | The real gold price mean-reverts at long horizons | E3 | Erb & Harvey 2013 | 5.9, 8.3 |
| C34 | Gold's long-run real return is contested | E3 | Palmberg 2025 vs Erb & Harvey 2013 | 5.9 |

### 14.3 Claims about this project's arithmetic

| # | Claim | Grade | Basis | Used in |
| --- | --- | --- | --- | --- |
| C35 | Under the observed 100 oz/0.01 lot specification, dollar risk equals the stop distance in USD/oz | E1 | Arithmetic on Phase 0 observation | 7.2, 7.3 |
| C36 | A $25 scenario can only support a $0.25-$2.50 stop at 1-10% risk | E1 | Arithmetic (case study only) | 7.6 |
| C37 | A $25 scenario cannot express these stop widths at 1-2% risk - an account-granularity statement, not a strategy verdict | E1 | Arithmetic (case study only) | 7.6 |
| C38 | A $2-$2.50 stop is at or below typical noise and spread | E1/E2 | Spread data; ATR estimates | 7.6 |
| C39 | Margin can pass at 1:200 while risk remains uncontrolled | E1 | Arithmetic | 7.7 |
| C40 | Indicative deployment equity for T2 is several thousand dollars at 2% risk | E4 (estimate) | Section 7 arithmetic + illustrative ATR | 7.8, 10.6 |

### 14.4 Claims about observed implementation data

| # | Claim | Grade | Source | Used in |
| --- | --- | --- | --- | --- |
| C41 | Phase 0/1 observed a 100 oz contract, 0.01 lot minimum, 0.01 tick size and 0.10 tick value on the Exness XAUUSD symbol | E1 (observation, one broker) | Phase 1 test log | 6.8.1, 7.2 |
| C42 | The Phase 0 spread reading of approximately $58.12 was abnormal and is not a representative active-market spread | E1 (observation) | Phase 0 probe | 6.8.2, 11.4 |
| C43 | A strong Level A result does not establish Level C profitability, and a failed Level C specification does not invalidate Level A | E1 (methodological) | Section 1.4 | 1.4, 2.1, 9.4, 18 |

### 14.5 Claims that are explicitly hypotheses, not findings

These are flagged separately so they are not mistaken for evidence.

| # | Hypothesis | Grade | Why it is not established |
| --- | --- | --- | --- |
| H1 | Intraday pullbacks in an H4 trend resume often enough to trade profitably on gold | E4 | Direct gold evidence is negative (C21-C25); rule is popular but untested here |
| H2 | A 50/200 daily EMA cross captures usable gold trends | E4 | Diversified evidence is positive, single-instrument gold evidence is absent |
| H3 | 12-month TSMOM works on gold at retail costs | E4 | Academic effect is contested (C10-C14); gold-specific test absent |
| H4 | ADX, volatility and session filters improve gold trend systems | E4/E5 | No direct evidence; overfitting risk is high (C18) |
| H5 | Central-bank demand makes gold trends longer and smoother | E4 | Plausible mechanism, no direct test |
| H6 | Gold's trend behaviour changed permanently after 2022 | E4 | One regime is not evidence of a permanent break |

---

## 15. Appendix A - Consolidated parameter sheet

This sheet is the single reference for what Phase 2B must implement. It
contains no optimised values. Where a value is listed as "baseline", the
corresponding grid in Section 11.7 defines the alternatives.

### 15.1 Global settings

| Parameter | Value | Notes |
| --- | --- | --- |
| Symbol | XAUUSD | Use the exact broker symbol name |
| Contract size | 100 oz/lot | Phase 0 observation (Section 6.8.1); read at runtime, never hardcode |
| Minimum volume | 0.01 lot | Phase 0 observation; read at runtime |
| Volume step | 0.01 lot | Phase 0 observation; read at runtime |
| Tick size | 0.01 | Phase 0 observation; read at runtime |
| Tick value | 0.10 | Phase 0 observation; read at runtime and reconcile against tick size x contract size |
| Point value | 0.01 | Phase 0 observation |
| Account currency | USD | Assumed; confirm |
| Risk fraction | Fixed per candidate | Never scaled to equity during a test |
| Max open positions | 1 | All candidates |
| Pyramiding | None | All candidates |
| Hedging | None | All candidates |
| Grid / martingale | None | All candidates |
| Entry execution | Next bar open | All candidates |
| Signal data | Closed bars only | All candidates |

**Dynamic detection requirement.** None of the broker values above may be
hardcoded. The Phase 1 symbol layer already reads them at runtime
(`GoldEASymbol.mqh`); Phase 2B must use that layer rather than introducing
constants.

### 15.2 T1 - MTF EMA pullback

| Parameter | Baseline | Grid |
| --- | --- | --- |
| Regime timeframe | H4 | Fixed |
| Entry timeframe | M15 | Fixed |
| ATR timeframe | H1 | Fixed |
| Fast EMA (regime) | 50 | Fixed |
| Slow EMA (regime) | 200 | Fixed |
| Pullback EMA | 20 (M15) | Fixed |
| Pullback distance | 0.2 x ATR(14, H1) | 0.2, 0.5 |
| Confirmation | Close beyond EMA20 | Fixed |
| RSI filter | Off | Off, On |
| RSI period | 14 | Fixed |
| RSI band (long) | 40-60 | Fixed |
| RSI band (short) | 40-60 | Fixed |
| Stop | 1.0 x ATR(14, H1) | 1.0, 1.5 |
| Stop floor | 2 x spread | Fixed |
| Trail | 2.0 x ATR(14, H1) | Fixed |
| Take profit | None | Fixed |
| Exit | Trail or H4 regime flip | Fixed |
| Risk per trade | 0.5% | 0.25%, 0.5%, 1.0% |

### 15.3 T2 - Daily dual-EMA

| Parameter | Baseline | Grid |
| --- | --- | --- |
| Timeframe | D1 | Fixed |
| Fast EMA | 50 | 20, 50, 100 |
| Slow EMA | 200 | 100, 200, 400 |
| Entry | Next D1 open after cross | Fixed |
| Exit | Opposite cross (flip) | Fixed |
| Disaster stop | 3.0 x ATR(14, D1) | 2.0, 3.0, 4.0 |
| ATR period | 14 | Fixed |
| Take profit | None | Fixed |
| Risk per trade | 1.0% | 0.5%, 1.0% |
| Max positions | 1 | Fixed |
| Minimum holding | None | Fixed |

### 15.4 T3 - TSMOM overlay

| Parameter | Baseline | Grid |
| --- | --- | --- |
| Signal | Sign of trailing return | Fixed |
| Lookback | 12 months (252 days) | 6, 12, 24 |
| Rebalance | Monthly, last trading day | Fixed |
| Volatility estimate | 60-day EWMA | Fixed |
| Target volatility | 10% annualised | Fixed |
| Leverage cap | 2.0x | Fixed |
| Scaling | Vol-targeted | Scaled, unscaled |
| Stop | None | Fixed |
| Max positions | 1 | Fixed |

### 15.5 T4 - Filter ablation (not a candidate)

| Filter | Parameter | Test levels |
| --- | --- | --- |
| ADX | Period 14, threshold 25 | Off, On |
| ATR percentile floor | 252-day lookback, 30th percentile | Off, On |
| ATR percentile ceiling | 252-day lookback, 95th percentile | Off, On |
| Session | 07:00-16:00 UTC | Off, On |
| Event blackout | 30 min around CPI, NFP, FOMC | Off, On |
| Friday cutoff | 18:00 UTC | Off, On |

**Acceptance:** >= 10% net PF improvement, >= 10% max DD improvement, >= 100
trades retained. Otherwise rejected.

### 15.6 Cost defaults

| Cost | Baseline | Stress |
| --- | --- | --- |
| Spread | Measured distribution | 1.5x, 2.0x |
| Commission | $7 per 100 oz round turn | 1.5x |
| Swap | Broker schedule | 1.5x |
| Entry slippage | 0.5 x spread | 2.0x |
| Stop slippage | 1.0 x spread | 2.0x |

### 15.7 Data and sample

| Item | Value |
| --- | --- |
| Start | 2004-01-01 |
| End | 2026-06-30 |
| In-sample | 2004-01-01 to 2016-12-31 |
| Out-of-sample | 2017-01-01 to 2026-06-30 |
| Structural-break window | 2022-01-01 to 2026-06-30 |
| Primary data | Exness MT5 real ticks |
| Cross-check | Dukascopy ticks; LBMA PM fix |
| Futures check | COMEX GC continuous |

---

## 16. Appendix B - Pre-flight verification checklist

Before Phase 2B begins, every item below must be confirmed and recorded. Any
item that cannot be confirmed is a reason to delay, not to proceed with an
assumption.

### 16.1 Broker and instrument

Phase 0/1 already observed the following on the Exness XAUUSD symbol (Section
6.8.1): 100 oz contract, 0.01 lot minimum, 0.01 lot step, 0.01 tick size, 0.10
tick value. The checklist below confirms they still hold for the account that
will be used, and fills the gaps that were not observed.

- [ ] Exact XAUUSD symbol name in the terminal.
- [ ] Re-read contract size at runtime (observed 100 oz; must not be hardcoded).
- [ ] Re-read minimum volume and volume step (observed 0.01 / 0.01).
- [ ] Re-read tick size and tick value, and reconcile tick value against tick size x contract size.
- [ ] Minimum stop distance (observed 0; confirm).
- [ ] Swap long and swap short, including triple-swap day.
- [ ] Commission schedule (per lot, per side, or included in spread).
- [ ] Spread distribution by hour, from actual active-market tick data.
- [ ] Confirm the abnormal Phase 0 spread reading is excluded from that distribution.
- [ ] Account leverage and margin currency.
- [ ] Whether the account is raw/ECN or standard.

### 16.2 Data

- [ ] Real tick history available back to 2004 (or the agreed start).
- [ ] M1 history available for the full period.
- [ ] D1 history cross-checked against LBMA PM fix.
- [ ] Gap handling verified for weekends and holidays.
- [ ] Data licence permits the intended use.

### 16.3 Engine

- [ ] Phase 1 execution engine supports next-bar-open entry.
- [ ] Phase 1 supports ATR-based stop placement.
- [ ] Phase 1 supports position flipping without an intermediate flat state
      (or the flip is modelled as two orders).
- [ ] Phase 1 risk checks do not block the intended position sizes.
- [ ] No EA modification is required for Phase 2B.

### 16.4 Protocol

- [ ] Parameter grids from Section 11.7 are fixed and recorded.
- [ ] Decision gates from Section 8 are fixed and recorded.
- [ ] Benchmarks from Section 11.10 are implemented.
- [ ] Deflated Sharpe and Reality Check tooling is available.
- [ ] Full trial disclosure template is ready.
- [ ] The OOS period has not been examined in any form.

### 16.5 Project

- [ ] `ROADMAP.md` unchanged by this phase.
- [ ] No MQL5 code written in this phase.
- [ ] This document reviewed by a second reader.
- [ ] Any deviation from this protocol will be logged with a reason.

---

## 17. Open questions

These are unresolved and are recorded so they are not silently assumed away.

| # | Question | Why it matters | How it could be resolved |
| --- | --- | --- | --- |
| Q1 | What is the actual contract size and minimum volume on the target account? | Determines whether any candidate is tradeable (Section 7) | Read the symbol specification |
| Q2 | Is the gold-real-yield relationship permanently changed, or is 2022-2026 a transient regime? | Determines whether pre-2022 backtests are relevant | Longer sample; monitor as new data arrives |
| Q3 | Does central-bank demand create trend persistence, or a slow one-way drift? | Distinguishes trend from long bias | Compare long/short attribution in T2 and T3 |
| Q4 | How much of T3's result is vol scaling rather than signal? | Determines whether T3 is a trend strategy or a risk overlay | Scaled vs unscaled comparison (Section 8.3) |
| Q5 | Is the 50/200 EMA pair robust across gold's history, or is it a post-2000 artefact? | Determines whether T2 is a real test or a fitted one | Pre-registered 20/100 and 100/400 comparison |
| Q6 | Can a single-instrument trend system achieve a Sharpe near the diversified 0.4 benchmark? | Sets expectations for what "success" means | Phase 2B results |
| Q7 | What deployment account size and risk fraction would be used if a candidate passes? | Determines whether a passing result can be funded, without influencing the verdict | Decide after Phase 2B, using Section 7 arithmetic |
| Q8 | Does the project have access to enough real tick history for T1? | T1 requires M1/ticks for intrabar stops | Verify data licence |

---

## 18. Conclusion

The evidence supports testing trend following on XAUUSD, but not with the
confidence that the popular literature implies.

Three findings should shape Phase 2B:

1. **The strongest evidence is for diversified, slow, low-turnover trend
   following.** That points to T2 as the first test, not T1.
2. **The weakest evidence is for intraday technical rules on gold
   specifically.** That points away from T1 as a primary candidate, and toward
   treating it as a conditional incremental test.
3. **The evidence hierarchy matters more than any single result.** A strong
   Level A finding does not prove Level C profitability, and one failed Level C
   specification does not invalidate Level A. Conclusions must be scoped to the
   level they were tested at.

The recommendation is therefore narrow and deliberate:

> **Backtest T2 and T3. Treat T1 as conditional on T2. Do not run T4 as a
> candidate. Pre-register every parameter and every decision gate before the
> first backtest. Report all trials, including the failures.**

If T2 fails its gates, the correct response is not to add filters or shorten the
timeframe. It is to record that **this specification** failed under these costs,
and then decide - separately, and with a new pre-registration - whether another
trend specification deserves its own test, or whether the project should move to
a different strategy family. That would be a successful Phase 2, not a failed
one.

---

## 19. Document history

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-01 | Initial draft: evidence review, four candidates, recommendation, Phase 2B protocol |
| 0.2 | 2026-11-01 | Corrections: scoped T2 conclusions to the tested implementation; removed account size from strategy selection and relabelled Section 7 as a deployment case study; rebuilt the contract-specification section around verified observations, assumptions and testing assumptions; added the Level A/B/C evidence hierarchy; standardized the Phase 2B reporting template; added an explicit protocol-preservation statement and a governance section |

**Constraints honoured by this document:**

- No MQL5 code written.
- No EA files modified.
- `ROADMAP.md` not modified.
- No other project files created or edited.
- All quantitative figures are labelled as illustrative or arithmetic, not as
  tested results.
- Account size is not used as a selection, rejection or scoring criterion.
- The pre-registered Phase 2B protocol is unchanged.
