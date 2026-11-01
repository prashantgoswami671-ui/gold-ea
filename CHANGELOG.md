\# Changelog



All important project changes are recorded here.



\## \[v0.2] - 2026-11-01



\### Phase 1 - Execution \& Risk Engine

\- Added the reusable Phase 1 execution and risk engine foundation for future strategies.

\- Added dynamic broker symbol specification loading: point, digits, tick size, tick value, contract size, volume minimum/maximum/step/limit, stops level, freeze level, trade mode, execution mode and filling-mode selection.

\- Added volume validation and normalisation that rounds down to the broker volume step and rejects invalid, below-minimum, above-maximum and above-limit volumes.

\- Added configurable spread protection in broker points. The default maximum spread is an input, not strategy logic.

\- Added account/EA/buy/sell position-count limits and a maximum EA-owned volume limit.

\- Added margin protection using `OrderCalcMargin`, projected free margin and projected margin level.

\- Added a dedicated configurable magic number. Position close/modify paths require both the EA symbol and magic number to match, so manual trades and other EAs are not touched.

\- Added a reusable market BUY/SELL execution wrapper with validated volume, deviation, magic number, comment, broker filling mode, retcode handling and structured error logging.

\- Fixed market-order filling-mode selection: BOC is valid only for limit orders, so it is never selected for `TRADE_ACTION_DEAL`. FOK and IOC are preferred, with RETURN as the fallback. This prevents an `INVALID_FILL` rejection on symbols that report BOC.

\- Added position discovery, counting, volume calculation, safe close and safe SL/TP modification. Closing and SL/TP modification are allowed while the safety lock is active; new entries are not.

\- Added broker stops-level and price-side validation for SL/TP, with tick-size/digits normalisation. Freeze level is loaded and exposed for future pending-order operations.

\- Added an EA-level safety lock with configuration, critical-execution-error, risk-violation and future-strategy activation paths. Diagnostics and logging continue while locked.

\- Added `DRY_RUN`, defaulting to `true`. Dry-run performs all validations and logs the intended action without calling `OrderSend` or modifying positions.

\- Added terminal, EA, account and symbol trading-permission checks with exact rejection reasons.

\- Added read-only restart/recovery discovery. Existing EA positions are logged; nothing is opened, closed or modified during recovery.

\- Added structured logging for configuration, symbol specifications, permissions, validation decisions, execution attempts/results, position discovery, safety-lock state and dry-run actions.

\- Added an optional validation-only self-test (`InpSelfTestOnInit`, default `false`) that forces dry-run and never sends orders.

\- Preserved all Phase 0 environment diagnostics in `EA/GoldEA/GoldEAPhase0.mqh`.

\- No strategy, entry signal, indicator, grid, martingale, hedging strategy, optimization or profit-target strategy was added. `OnTick()` contains no entry logic.

\- Added Phase 1 architecture documentation in `Docs/Phase-1-Execution-Engine.md`.

\- Added the Phase 1 test matrix and actual test results in `Tests/Phase-1/Phase-1-Testing.md`.

\- Compile result: 0 errors, 0 warnings (MetaEditor 5, terminal build 6296).

\- Strategy Tester self-test result: 27 passed, 0 failed, 2 manual skips with a widened test-only spread limit; 26 passed, 0 failed, 3 skips with the default spread limit (the 70-point tester spread was correctly rejected against the 50-point default).

\- Pending: Exness live/demo quote validation, restart/re-attach with open EA positions, live permission toggles, live foreign-position protection and real broker-rejection/critical-lock tests.

\- `ROADMAP.md` was not modified.



\## \[Unreleased]



\### Phase 0 — Project Setup \& Baseline



\- Created initial Git repository structure.

\- Added project README.

\- Added locked project roadmap.

\- Added EA source directory.

\- Added testing directories.

\- Added documentation directories.

\- Added configuration directory.

\- No trading strategy has been implemented yet.

\- No live trading is permitted during development.

\- Fixed MetaEditor warning: changed the MQL5 version property from \`0.1\` to \`1.00\`. MQL5 Market requires the \`xxx.yyy\` format and a major version of at least 1; the project phase remains v0.1. No EA logic changed.



\### Project Rule



Build less. Test more. Measure everything.



