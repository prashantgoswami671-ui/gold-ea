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



Phase 0 — Project Setup \& Baseline



Current objective:



Create the project foundation and verify that the development environment can correctly communicate with MetaTrader 5 and identify the required Gold symbol and account specifications.



\## Repository Structure



```text

gold-ea/

├── README.md

├── ROADMAP.md

├── CHANGELOG.md

├── .gitignore

├── EA/

│   └── GoldEA.mq5

├── Tests/

│   ├── Phase-0/

│   └── Results/

├── Docs/

│   ├── Strategy/

│   └── Testing/

└── Config/

&#x20;   └── README.md



