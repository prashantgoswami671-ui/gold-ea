GOLD EA — MASTER ROADMAP

Project: Automated XAUUSD Trading System

Version: 1.0

Status: LOCKED ROADMAP

Primary rule: Finish the current phase before starting the next. No scope creep.

1\. PROJECT OBJECTIVE

Build, test, compare, and select a robust automated trading strategy for Gold (XAUUSD) on MetaTrader 5.



The final EA must be selected by evidence from testing — not by assumption, social-media claims, or a desire to keep adding features.

Success means

\- A clearly defined strategy with measurable rules.

\- Reproducible backtest results.

\- Acceptable drawdown and risk.

\- Robustness across different market conditions.

\- Successful Demo forward testing.

\- Only then: a decision about very small real-money testing.

Non-goals

\- Guaranteed profits.

\- Guaranteed win rate.

\- Building a huge multi-strategy EA.

\- Adding features just because they sound useful.

\- Going live before testing is complete.

2\. NON-NEGOTIABLE PROJECT RULES

Rule 1 — One phase at a time

Do not start work from a later phase while the current phase is unfinished.

Rule 2 — No scope creep

A new idea does NOT automatically become a task.



Put it in the IDEA PARKING LOT and continue the roadmap.

Rule 3 — Evidence decides

A strategy is selected because testing supports it, not because it sounds sophisticated.

Rule 4 — Complexity must earn its place

Every additional indicator, filter, grid rule, news filter, AI component, or optimization must demonstrate measurable benefit.

Rule 5 — No live money during development

Development and testing happen on historical data and Demo first.

Rule 6 — No parameter optimization without a reason

Do not endlessly optimize settings until the backtest looks perfect.

Rule 7 — Preserve baselines

Never overwrite the original test results. Every meaningful change gets its own version and comparison.

Rule 8 — Safety before profit

Execution safety, position limits, drawdown control, and failure handling come before performance optimization.

3\. FIXED PROJECT SCOPE

Instrument

\- Primary: Gold / XAUUSD

\- Broker environment: MetaTrader 5 / Exness for initial testing

\- Exact symbol name must be detected/verified automatically.

Initial platform

\- MetaTrader 5

\- Language: MQL5

Account approach

1\. Historical testing

2\. MT5 Strategy Tester

3\. Demo forward testing

4\. Only after successful validation: consider tiny real-money testing

Initial account size for future consideration

\- $25 is a possible experimental starting amount.

\- It is NOT an assumption that the strategy is safe for $25.

\- Margin, drawdown, and execution requirements must be checked first.

4\. PHASE 0 — PROJECT SETUP \& BASELINE

Goal

Create the foundation and testing process.

Tasks

\- Define project folders/versioning.

\- Define EA naming convention.

\- Define Magic Number policy.

\- Verify MT5/Exness symbol specifications.

\- Verify contract size, point size, tick size, tick value, volume min/max/step.

\- Verify account type requirements.

\- Establish a standard backtest report format.

\- Establish baseline test periods and data quality requirements.

Exit criteria

\- Testing environment works.

\- Instrument specifications are known.

\- Versioning is established.

\- Standard performance report exists.

DO NOT build the final strategy yet.

5\. PHASE 1 — EXECUTION \& RISK ENGINE

Goal

Build a safe EA framework before strategy logic.

Tasks

\- Market data handling.

\- Order execution.

\- Position identification using Magic Number.

\- Volume normalization.

\- Broker filling-mode detection.

\- Spread measurement.

\- Margin checks.

\- Error/rejection handling.

\- Duplicate-entry protection.

\- Position-count limits.

\- Logging.

\- Basic emergency close capability.

Exit criteria

\- EA can safely open/close test positions.

\- It does not interfere with unrelated trades.

\- Broker constraints are handled.

\- Execution errors are logged.

\- Risk limits work.

No strategy optimization yet.

6\. PHASE 2 — STRATEGY A: TREND FOLLOWING

Goal

Find out whether a simple Gold trend strategy has an edge.

Candidate logic

\- Higher timeframe trend filter.

\- Lower timeframe entry.

\- EMA-based trend identification.

\- Optional RSI/price-action confirmation.

\- Clear stop/exit rules.

Test

Use a small, predefined parameter set.



Measure:

\- Net profit

\- Profit factor

\- Win rate

\- Maximum drawdown

\- Average trade

\- Losing streak

\- Trade count

\- Costs

\- Performance by market regime

Exit criteria

A complete baseline result is recorded.



Do not endlessly optimize.

7\. PHASE 3 — STRATEGY B: BREAKOUT

Goal

Test whether Gold breakout behavior provides a better edge.

Candidate logic

\- Define a measurable consolidation/range.

\- Detect breakout.

\- Require confirmation.

\- Define objective exit/risk rules.

Measure

Use the same reporting framework as Phase 2.

Exit criteria

Complete baseline results recorded.

8\. PHASE 4 — STRATEGY C: MEAN REVERSION / SCALPING

Goal

Test the opposite market assumption: Gold temporarily deviates from a reference/range and then reverts.

Candidate logic

\- Define overextension objectively.

\- Require confirmation.

\- Fixed risk.

\- Objective exit.

Measure

Use the exact same core metrics.

Exit criteria

Complete baseline results recorded.

9\. PHASE 5 — STRATEGY D: CONTROLLED GRID

Goal

Test our original grid concept as a strategy — without assuming it is profitable.

Candidate design

\- One-direction only.

\- No hedging.

\- No Martingale.

\- Fixed lot.

\- Maximum position limit.

\- Grid entries only under valid directional conditions.

\- Basket-level risk control.

\- Individual trade exits where justified.

Important

The earlier candidate settings:

\- 0.01 lot

\- maximum 5 positions

\- $1.50 individual TP

\- $5 basket TP

\- $5 basket SL

\- approximately $0.50 Gold spacing

are TEST PARAMETERS, NOT PERMANENT RULES.



They may be changed or rejected based on evidence.

Exit criteria

Complete baseline grid results recorded.

10\. PHASE 6 — STRATEGY COMPARISON

Goal

Compare all tested approaches fairly.



Compare:

\- Trend

\- Breakout

\- Mean reversion/scalping

\- Controlled grid

Primary metrics

1\. Profit factor

2\. Maximum drawdown

3\. Net profit

4\. Return relative to risk

5\. Losing streak

6\. Average trade/cycle

7\. Stability across periods

8\. Trading costs

9\. Worst observed market regime

10\. Complexity

Decision

Choose:

\- One strategy, OR

\- A very small combination of complementary components.

Rule

Do not combine strategies merely because each one looks profitable separately.

11\. PHASE 7 — ROBUSTNESS \& STRESS TESTING

Goal

Try to break the selected strategy.



Test:

\- Different historical periods.

\- Bullish Gold markets.

\- Bearish Gold markets.

\- Sideways markets.

\- High-volatility periods.

\- Low-volatility periods.

\- Large price spikes.

\- High-spread conditions.

\- Slippage assumptions.

\- Different reasonable parameter values.

\- Out-of-sample data.

Key question

Does the strategy still behave acceptably when conditions are not ideal?



Exit criteria

The strategy demonstrates reasonable robustness.



If it fails:

\- Return to the appropriate strategy phase.

\- Do NOT add random filters just to rescue the backtest.

12\. PHASE 8 — FINAL EA BUILD

Goal

Turn the validated strategy into the production-quality EA.



Only now finalize:

\- Entry rules.

\- Exit rules.

\- Position sizing.

\- Grid rules, if selected.

\- Risk limits.

\- Trading sessions.

\- Volatility filters.

\- Spread filters.

\- News handling, if justified.

\- State management.

\- Restart behavior.

\- Dashboard.

\- User controls.

Rule

Features must have a demonstrated purpose.

13\. PHASE 9 — DEMO FORWARD TEST

Goal

Validate behavior in live market conditions without real money.



Track:

\- Backtest vs Demo differences.

\- Execution quality.

\- Spread.

\- Slippage.

\- Missed/rejected orders.

\- Actual trade frequency.

\- Drawdown.

\- Strategy behavior.

Exit criteria

Demo behavior is consistent enough with expectations to justify the next review.

14\. PHASE 10 — FINAL REVIEW

Before any real-money decision, review:

Strategy

\- Is the edge still credible?

\- Is it understandable?

\- Is it robust?

Risk

\- Maximum exposure?

\- Maximum drawdown?

\- Worst losing streak?

\- What happens during abnormal Gold moves?

Execution

\- Broker conditions?

\- Spread?

\- Slippage?

\- Margin?

Operational

\- VPS/reliability?

\- Restart recovery?

\- Logging?

\- Manual emergency controls?

Decision

One of:

\- REJECT

\- REVISE

\- CONTINUE DEMO

\- APPROVE FOR TINY EXPERIMENTAL LIVE TEST

Approval is NOT automatic.

15\. IDEA PARKING LOT

Any new idea goes here first.



Examples:

\- AI/ML prediction

\- Additional indicators

\- Smart money concepts

\- Order blocks

\- Machine-learning optimization

\- Multiple symbols

\- Crypto

\- Forex pairs

\- More complex hedging

\- Advanced news trading

\- Copy trading

\- Sentiment analysis

\- More dashboards

\- Mobile notifications

\- Extra entry modes

Rule

An idea stays parked unless it solves a demonstrated problem in the current roadmap.

16\. CHANGE CONTROL

When someone proposes a new task, ask:

Question 1

Does it directly support the current phase?

\- YES → consider it.

\- NO → parking lot.

Question 2

Is it necessary to pass the current phase exit criteria?

\- YES → add it.

\- NO → parking lot.

Question 3

Does it materially improve safety, validity, or measurement?

\- YES → consider it.

\- NO → reject/park.

Question 4

Are we adding it because the current strategy is failing?



If YES:

\- First understand WHY it is failing.

\- Do not blindly add another filter.

17\. STANDARD TEST REPORT

Every strategy/version must report:

Strategy:

Version:

Symbol:

Broker:

Timeframe:

Test period:

Initial balance:

Lot/risk model:



Net profit:

Profit factor:

Maximum drawdown:

Maximum drawdown %:

Win rate:

Total trades:

Average winning trade:

Average losing trade:

Largest win:

Largest loss:

Maximum consecutive wins:

Maximum consecutive losses:

Total costs:

Average trade duration:



Worst month/period:

Best month/period:



Notes:

Known weaknesses:

Decision:

18\. VERSIONING

Use:



GOLD-EA-v0.x = research/testing



GOLD-EA-v1.x = validated strategy development



GOLD-EA-v2.x = future major revision



Example:

\- v0.1 — framework

\- v0.2 — execution engine

\- v0.3 — trend baseline

\- v0.4 — breakout baseline

\- v0.5 — mean-reversion baseline

\- v0.6 — grid baseline

\- v0.7 — comparison

\- v0.8 — robustness

\- v1.0 — validated final EA

Never silently replace an old version.

19\. CURRENT STATUS

Current phase: Phase 0 — Project Setup \& Baseline



Next action: Build the project/testing foundation.



Do not jump to:

\- Final grid implementation

\- AI

\- Live trading

\- Multiple instruments

\- Extra strategies outside the planned comparison

\- Complex dashboards

20\. DEFINITION OF DONE

The project is considered complete only when:

\- \[ ] A strategy was selected using evidence.

\- \[ ] The strategy survived robustness testing.

\- \[ ] The final EA was implemented safely.

\- \[ ] Demo forward testing was completed.

\- \[ ] Results were reviewed.

\- \[ ] Real-money risk was explicitly evaluated.

\- \[ ] No unresolved critical execution/risk bugs remain.

FINAL PROJECT RULE

BUILD LESS. TEST MORE. MEASURE EVERYTHING.

We are not trying to create the most complicated trading bot.



We are trying to discover whether we can build a simple, measurable, robust Gold trading system with controlled risk.



If a feature does not help us reach that gold, it waits.

