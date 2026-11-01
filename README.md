\# Gold EA



An automated MetaTrader 5 Expert Advisor project focused on systematic Gold (XAUUSD) trading.



\## Project Goal



The goal of this project is to research, build, test, compare, and validate automated trading strategies for Gold before considering live deployment.



The project will not assume that one strategy is automatically the best.



Different strategy families will be developed and tested independently before deciding whether any strategy should be combined into a final EA.



\## Platform



\- Platform: MetaTrader 5

\- Programming Language: MQL5

\- Primary Instrument: Gold (XAUUSD / broker-specific Gold symbol)

\- Development Environment: MetaEditor

\- Version Control: Git + GitHub



\## Development Philosophy



Build less. Test more. Measure everything.



Every strategy must be:



1\. Defined clearly

2\. Implemented systematically

3\. Backtested

4\. Stress tested

5\. Compared with alternatives

6\. Forward tested on Demo

7\. Reviewed before live deployment



\## Strategy Research



The project will investigate multiple strategy families:



\- Trend Following

\- Breakout

\- Mean Reversion / Scalping

\- Controlled Grid



No strategy will be considered successful based only on a small number of profitable trades.



Performance must be evaluated using objective test results and robustness checks.



\## Risk Philosophy



Risk management is more important than trade frequency.



The EA must prioritize:



\- Controlled position sizing

\- Maximum exposure limits

\- Maximum drawdown control

\- Spread protection

\- Margin protection

\- Execution-error handling

\- Trading lock mechanisms where required



\## Testing Philosophy



Testing will progress through stages:



Research

→ Development

→ Backtesting

→ Stress Testing

→ Strategy Comparison

→ Demo Forward Testing

→ Final Review

→ Possible Live Deployment



Live trading will only be considered after successful testing.



\## Current Status



Phase 1 - Execution \& Risk Engine (v0.2)



Current objective:



The reusable execution and risk engine foundation is implemented. Phase 0 diagnostics are preserved. No strategy is attached, `OnTick()` contains no entry logic, and `DRY_RUN` defaults to `true`.



Phase 1 automated self-test result: 27 passed, 0 failed, 2 manual skips with a widened test-only spread limit; 26 passed, 0 failed, 3 skips with the default spread limit. Exness-specific live/demo quote validation and restart-with-open-positions testing remain pending.



See `Docs/Phase-1-Execution-Engine.md` and `Tests/Phase-1/Phase-1-Testing.md`.



Next step: review Phase 1 before starting Phase 2.



\## Repository Structure



```text

gold-ea/

├── README.md

├── ROADMAP.md

├── CHANGELOG.md

├── .gitignore

├── EA/

│   ├── GoldEA.mq5

│   └── GoldEA/

│       ├── GoldEALog.mqh

│       ├── GoldEAConfig.mqh

│       ├── GoldEATypes.mqh

│       ├── GoldEASymbol.mqh

│       ├── GoldEASafety.mqh

│       ├── GoldEAPermissions.mqh

│       ├── GoldEARisk.mqh

│       ├── GoldEAPositions.mqh

│       ├── GoldEATradeResult.mqh

│       ├── GoldEAExecution.mqh

│       ├── GoldEASelfTest.mqh

│       └── GoldEAPhase0.mqh

├── Tests/

│   ├── Phase-0/

│   ├── Phase-1/

│   │   └── Phase-1-Testing.md

│   └── Results/

├── Docs/

│   ├── Phase-1-Execution-Engine.md

│   ├── Strategy/

│   └── Testing/

└── Config/

&#x20;   └── README.md

```



