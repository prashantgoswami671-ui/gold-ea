# Phase 1 - Execution & Risk Engine Testing

Version tested: Gold EA v0.2  
Test date: 2026-11-01  
Test status: automated checks performed; remaining manual/live checks listed at the end

## Test environment

- Platform: MetaTrader 5, terminal build 6296
- Compiler: MetaEditor 5
- Account used by the available tester: MetaQuotes-Demo, login 5058194810
- Symbol: `XAUUSD`
- Tester period: M1, 2026-10-30 to 2026-10-31
- Model: Open prices only
- Deposit: 10,000 USD
- Leverage: 1:100
- `DRY_RUN=true` for every test run

The automated tester available in this environment used MetaQuotes-Demo `XAUUSD`.
Exness-specific live/demo quote and execution validation was **not** performed in
this session. The EA reads all broker symbol values dynamically, so no Exness
value is compiled into the EA.

## Compilation

Command:

```text
metaeditor64.exe /compile:"C:\Users\sunit\gold-ea\EA\GoldEA.mq5" /log:"...\compile.log"
```

Result:

```text
0 errors, 0 warnings
```

## Strategy Tester runs

Three runs used the final compiled build. The second and third runs deliberately
widened test-only inputs to exercise paths that the live tester spread blocked.
Those widened values are **not** code defaults.

### Run A - default safety configuration

- `InpMaxSpreadPoints=50` (code default)
- `InpMinFreeMarginPct=30`, `InpMinMarginLevelPct=150` (code defaults)
- `InpSafetyLockAtStartup=false`
- `InpSelfTestOnInit=true`

Observed:

```text
Passed : 26
Failed : 0
Skipped: 3
REJECTED OPEN BUY | stage spread | reason: spread 70.0 points exceeds configured maximum 50 points
SKIP dry-run-execution | live precondition rejected (spread)
No order was sent. No position was modified.
```

The live tester spread was 70 points, so the default spread gate correctly
rejected the dry-run request. This validates the spread rejection path with a
real quote rather than only synthetic values.

### Run B - widened spread to exercise the dry-run path

- `InpMaxSpreadPoints=200` (test-only)
- `InpMinFreeMarginPct=0`, `InpMinMarginLevelPct=0` (test-only)
- `InpSafetyLockAtStartup=false`
- `InpSelfTestOnInit=true`

Observed:

```text
Passed : 27
Failed : 0
Skipped: 2
EXECUTION REQUEST : OPEN BUY | volume 0.010 | ... | dryRun=true
DRY-RUN OPEN BUY | validation passed | ... | NO ORDER SENT
PASS dry-run-execution | validation passed; result.dryRun=true, result.sent=false
No order was sent. No position was modified.
```

### Run C - startup safety lock

- `InpMaxSpreadPoints=200` (test-only)
- `InpSafetyLockAtStartup=true`
- `InpSelfTestOnInit=true`

Observed:

```text
SAFETY LOCK ACTIVE | source=configuration | reason=safety lock enabled by input
PASS safety-lock-blocks-entry
REJECTED OPEN BUY | stage safety-lock | reason: safety lock active: safety lock enabled by input (source: configuration)
Passed : 26
Failed : 0
Skipped: 3
No order was sent. No position was modified.
```

The configuration-driven lock prevented the new entry. Diagnostics and the
self-test continued.

## Test matrix

| # | Test | Result | Evidence / notes |
|---:|---|---|---|
| 1 | EA initialization | PASS | Strategy Tester `OnInit()` completed and logged `Phase 1 initialization complete`; tester reported `Test passed`. |
| 2 | Symbol specification loading | PASS | Dynamic `XAUUSD` spec logged: digits 2, point 0.01, tick size 0.01, tick value 0.10, contract 100, min 0.01, max 100, step 0.01, stops 0, freeze 0, trade mode Full, execution Market, FOK/IOC, selected FOK. |
| 3 | Volume below minimum | PASS | Self-test requested 0.005 with minimum 0.010; rejected with the exact reason. |
| 4 | Volume above maximum | PASS | Self-test requested 1.01 with maximum 1.000; rejected. |
| 5 | Invalid volume step | PASS | Self-test: 0.015 with step 0.01 normalised down to 0.010; a broker step of 0 was also rejected as invalid. |
| 6 | Spread above limit | PASS | Synthetic 50 points > 20 rejected; live tester quote 70 points > default 50 rejected at stage `spread`. |
| 7 | Spread within limit | PASS | Synthetic 10 points <= 20 accepted; Run B live 70 points <= test-only 200 allowed dry-run. |
| 8 | Insufficient margin | PASS | Synthetic projected free margin 200 below required buffer 300 rejected. |
| 9 | Trading permissions disabled | PASS (gate logic) | Synthetic terminal-trading-disabled state rejected with the exact reason. A live AutoTrading toggle test was not performed. |
| 10 | Invalid SL | PASS | Self-test rejected a BUY SL closer than the stops level and a BUY SL on the wrong side of Bid. |
| 11 | Invalid TP | PASS | Self-test rejected a BUY TP closer than the stops level and a BUY TP on the wrong side of Ask. |
| 12 | Maximum-position limit | PASS (logic) | Self-test rejected a buy when the buy count limit was reached and rejected a new entry when the total account-position limit was reached. Live position limits were not exercised because no strategy opened trades. |
| 13 | Magic-number isolation | PASS (logic) | Self-test confirmed same symbol + same magic is owned; different magic and different symbol are rejected. A live foreign-position close/modify test was not performed. |
| 14 | Dry-run execution | PASS | Run B: all validations passed, `result.dryRun=true`, `result.sent=false`, no order sent. |
| 15 | Safety lock | PASS | Self-test verified the lock blocks new entries; Run C verified configuration activation and rejection at stage `safety-lock`. Critical-error activation was not induced with a real broker rejection. |
| 16 | Restart/reinitialization | PENDING | Recovery is read-only and logs existing positions, but a restart/re-attach with open EA positions was not performed. This requires a controlled test position and is deferred until a strategy or a controlled test path can create one. |
| 17 | Zero automatic trades without a strategy | PASS | Static check: `OnTick()` only calls `GEA_StatusHeartbeat()`; the main file contains no execution/close/modify calls. Tester ran 1,380 M1 bars with no order sent. The self-test marks this as a manual item, but the static and tester evidence was collected separately. |

## Static safety checks performed

- `OrderSend` appears only in:
  - `EA/GoldEA/GoldEAExecution.mqh` (market open)
  - `EA/GoldEA/GoldEAPositions.mqh` (close and SL/TP modify)
- `OnTick()` body is only `GEA_StatusHeartbeat();`.
- `EA/GoldEA.mq5` contains no call to `GEA_ExecuteMarket`,
  `GEA_CloseEAPosition`, `GEA_ModifyEAPositionSLTP`, or
  `GEA_CloseAllEAPositions` outside comments.
- `DRY_RUN` input default is `true`.
- No strategy, indicator, entry signal or automatic order-generation code was
  added.
- Phase 0 report functions are preserved in `GoldEA/GoldEAPhase0.mqh` and were
  observed in the tester journal.

## Not performed / still pending

The following must not be reported as passed:

1. Exness demo live quote and spread validation while the market is actively
   quoting.
2. Restart or chart re-attach with open EA-owned positions (Test 16).
3. Live permission toggles for terminal/EA/account/symbol trading (Test 9 used a
   synthetic gate state).
4. Live foreign manual/other-EA position protection with real positions
   (Test 13 used the ownership logic).
5. Real broker rejection and critical-error lock activation. Inducing a real
   rejection was outside Phase 1 dry-run testing.
6. Real close/modify of an EA-owned position. No strategy and no controlled
   position existed in the tester.
7. Strategy Tester run on the Exness server. The available tester used
   MetaQuotes-Demo.

## How to run the built-in self-test

1. Compile the EA.
2. Attach it to `XAUUSD` with `DRY_RUN=true`.
3. Set `InpSelfTestOnInit=true`.
4. Read the Experts journal.
5. Confirm `Failed : 0` and `No order was sent. No position was modified.`
6. Set `InpSelfTestOnInit=false` again for normal Phase 1 operation.

The self-test is validation-only and forces dry-run even if `DRY_RUN=false`.
