# Phase 1 - Execution & Risk Engine

Project: Gold EA  
Phase version: v0.2  
Status: implementation complete, pending review before Phase 2

## Purpose

Phase 1 provides the reusable execution, position, risk, safety and logging
foundation that future strategies (A, B, C and D) will call.

It contains **no strategy**:

- no trend-following logic
- no breakout logic
- no mean-reversion logic
- no grid logic
- no EMA / RSI entries
- no entry signals
- no strategy-specific exits
- no martingale
- no hedging strategy
- no optimization logic
- no profit-target strategy

`OnTick()` contains no entry logic. The EA cannot open a trade simply because it
is attached to a chart. A future strategy must explicitly call the execution
engine.

## Architecture

```text
GoldEA.mq5                    lifecycle, inputs, no strategy
 |
 +-- GoldEAPhase0.mqh         preserved Phase 0 environment diagnostics
 |
 +-- GoldEAConfig.mqh         inputs -> validated process configuration
 +-- GoldEALog.mqh            structured logging, retcode text
 +-- GoldEATypes.mqh          result and position data structures
 +-- GoldEASymbol.mqh         dynamic broker symbol specification
 |                            volume normalisation, quote/spread checks
 +-- GoldEASafety.mqh         EA-level no-new-trades lock
 +-- GoldEAPermissions.mqh    terminal/EA/account/symbol permission gates
 +-- GoldEARisk.mqh           position limits, margin, SL/TP validation
 +-- GoldEAPositions.mqh      ownership-safe close / modify / discovery
 +-- GoldEATradeResult.mqh    broker retcode handling and critical-error lock
 +-- GoldEAExecution.mqh      reusable market BUY / SELL wrapper
 +-- GoldEASelfTest.mqh       optional validation-only test path
```

All source modules live under `EA/GoldEA/`. The EA entry point remains
`EA/GoldEA.mq5`.

## Safety pipeline

Every new market order passes these gates in order:

1. Requested order type is market BUY or SELL.
2. EA safety lock is clear.
3. Terminal, EA, account and symbol permissions allow the direction.
4. Broker symbol specification is valid.
5. Valid Bid/Ask quote is available.
6. Volume is finite, positive, normalised down to the broker step, and within
   broker minimum, maximum and volume limit.
7. Spread in points is within the configured maximum.
8. SL/TP are on the correct side of the market, respect the broker stops level,
   and are normalised to the symbol tick size/digits.
9. Account-wide position count and EA-owned count/direction/volume are within
   the configured limits.
10. `OrderCalcMargin` succeeds; projected free margin and projected margin level
    remain above the configured buffers.
11. Only then is `OrderSend` called, unless `DRY_RUN` is true.

Any failed gate returns `success=false`, records the failing stage and reason,
and logs the exact rejection. No gate forces a trade through.

## Configuration

Inputs are defined in `EA/GoldEA.mq5`.

| Input | Default | Meaning |
|---|---:|---|
| `DRY_RUN` | `true` | Validate only; no real order or position change |
| `InpMagicNumber` | `20261101` | Dedicated EA magic number |
| `InpSafetyLockAtStartup` | `false` | Activate no-new-trades lock at startup |
| `InpLockOnCriticalError` | `true` | Lock new entries after a critical broker retcode |
| `InpMaxSpreadPoints` | `50` | Maximum allowed spread in broker points |
| `InpDeviationPoints` | `30` | Maximum price deviation/slippage in points |
| `InpOrderComment` | `GoldEA-P1` | Broker order comment, maximum 31 characters |
| `InpMaxTotalPositions` | `10` | Maximum open positions in the whole account |
| `InpMaxEAPositions` | `5` | Maximum open positions owned by this EA |
| `InpMaxBuyPositions` | `3` | Maximum EA-owned buy positions |
| `InpMaxSellPositions` | `3` | Maximum EA-owned sell positions |
| `InpMaxEATotalVolume` | `1.00` | Maximum total EA-owned volume in lots |
| `InpMinFreeMarginPct` | `30.0` | Minimum free margin after trade, % of equity |
| `InpMinMarginLevelPct` | `150.0` | Minimum projected margin level, % |
| `InpRunPhase0Diagnostics` | `true` | Run the preserved Phase 0 report |
| `InpLogExistingPositionsOnStart` | `true` | Log EA positions during recovery |
| `InpStatusLogIntervalSeconds` | `300` | Periodic status log interval, 0 disables |
| `InpSelfTestOnInit` | `false` | Run validation-only self-test, forced dry-run |

Configuration is validated during `OnInit()`. Invalid safety values cause
`INIT_FAILED` with a logged reason.

`InpMaxTotalPositions` counts **all account positions**, including manual and
other-EA positions. It only blocks a new EA entry; it never modifies or closes a
foreign position. The other limits count only positions whose symbol and magic
number both match this EA.

## Ownership and magic-number rules

An EA-owned position must match **both**:

- `POSITION_SYMBOL == _Symbol`
- `POSITION_MAGIC == InpMagicNumber`

The same magic number on another symbol is not treated as owned. Another magic
number on the same symbol is not treated as owned.

`GEA_CloseEAPosition()` and `GEA_ModifyEAPositionSLTP()` re-read the position and
verify ownership immediately before acting. If ownership does not match, the
operation is refused and logged. Manual trades, other EAs and other magic
numbers are never touched.

The magic number must be unique across EAs on the same account and symbol. Two
EAs using the same magic on the same symbol cannot be distinguished.

## Public API for future strategies

```mql5
bool GEA_ExecuteMarket(ENUM_ORDER_TYPE orderType,
                       double requestedVolume,
                       double requestedSL,
                       double requestedTP,
                       string comment,
                       GoldEAExecutionResult &result,
                       bool forceDryRun = false);

bool GEA_ExecuteMarketBuy(double volume, double sl, double tp,
                          string comment, GoldEAExecutionResult &result);

bool GEA_ExecuteMarketSell(double volume, double sl, double tp,
                           string comment, GoldEAExecutionResult &result);

bool GEA_CloseEAPosition(ulong ticket, GoldEAExecutionResult &result);

bool GEA_ModifyEAPositionSLTP(ulong ticket, double sl, double tp,
                              GoldEAExecutionResult &result);

int GEA_CloseAllEAPositions(string reason,
                            int &closedCount,
                            int &failedCount);

int  GEA_CollectEAPositions(GoldEAPositionInfo &positions[]);
void GEA_CollectPositionStats(GoldEAPositionStats &stats);
bool GEA_HasEAPosition(ENUM_POSITION_TYPE type);

void GEA_SafetyLockActivate(string source, string reason);
void GEA_SafetyLockDeactivate(string source, string reason);
bool GEA_SafetyIsLocked();
bool GEA_SafetyAllowNewTrades(string &reason);
```

Validation helpers are also reusable and side-effect free:

```mql5
bool GEA_NormalizeVolume(const GoldEASymbolSpec &spec, double requested,
                         double &normalized, string &reason);

bool GEA_EvaluateSpread(double bid, double ask, double point,
                        int maxSpreadPoints, double &spreadPoints,
                        string &reason);

bool GEA_EvaluateMargin(double equity, double freeMargin, double marginUsed,
                        double requiredMargin, double minFreePct,
                        double minLevelPct, string &reason);

bool GEA_ValidateStops(const GoldEASymbolSpec &spec,
                       ENUM_ORDER_TYPE orderType, double bid, double ask,
                       double sl, double tp, double &normalizedSL,
                       double &normalizedTP, string &reason);
```

`GEA_ExecuteMarket()` returns `success=true` in dry-run when all validations
pass. Callers must check `result.dryRun` and `result.sent`; a dry-run result has
`sent=false` and no order was sent.

## Dry-run behaviour

`DRY_RUN` defaults to `true`.

When `DRY_RUN=true` or the self-test forces dry-run:

- every validation still runs
- margin is calculated with `OrderCalcMargin`
- permissions, spread, volume, position limits and SL/TP are checked
- the intended order is logged in full
- `OrderSend` is not called
- no position is closed or modified

`GEA_CloseEAPosition()` and `GEA_ModifyEAPositionSLTP()` also honour `DRY_RUN`
and only log the simulated action.

## Safety lock

The lock blocks **new entries only**.

- diagnostics and logging continue
- position discovery continues
- closing an existing EA position is allowed
- SL/TP modification is allowed

Activation sources:

- configuration: `InpSafetyLockAtStartup=true`
- critical execution error: automatic when `InpLockOnCriticalError=true` and a
  non-transient critical retcode is returned
- risk limit violation: a strategy or operator can call
  `GEA_SafetyLockActivate("risk-limit", reason)`
- future strategy instruction: same API

Critical retcodes that trigger automatic locking are:
`TRADE_RETCODE_TRADE_DISABLED`, `TRADE_RETCODE_NO_MONEY`,
`TRADE_RETCODE_INVALID_VOLUME`, `TRADE_RETCODE_INVALID_STOPS`,
`TRADE_RETCODE_INVALID_FILL`, `TRADE_RETCODE_INVALID_ORDER`,
`TRADE_RETCODE_ONLY_REAL`, `TRADE_RETCODE_LIMIT_POSITIONS` and
`TRADE_RETCODE_LIMIT_VOLUME`.

Transient conditions such as requote, price changed, timeout, connection loss,
market closed and too many requests do not activate the lock automatically.

The runtime lock is **not persisted across a terminal restart** in Phase 1. A
configuration lock is re-applied at every initialization. Persistence can be
added when a strategy needs it.

## SL/TP rules

- BUY: SL below Bid, TP above Ask.
- SELL: SL above Ask, TP below Bid.
- Broker `SYMBOL_TRADE_STOPS_LEVEL` is respected in price distance.
- Prices are normalised to the broker tick size and symbol digits.
- Zero SL/TP means "not set".
- No strategy-specific distance is invented by this engine.

`SYMBOL_TRADE_FREEZE_LEVEL` is loaded and exposed through
`GEA_IsFreezeBlocked()` for future pending-order work. Per MQL5 semantics, the
freeze level applies to pending orders, not to market execution or position
SL/TP modification, so market orders and position SL/TP are not blocked by it.

## Position discovery and recovery

`GEA_RecoverOnInit()` runs during initialization and is strictly read-only:

- counts account positions
- counts positions on the current symbol
- counts EA-owned positions by direction and volume
- logs existing EA positions if configured
- never opens, closes or modifies anything

Because the normal EA has no strategy and no entry signal, a restart cannot
duplicate positions. Future strategies must consult the position helpers before
requesting a new entry.

## Logging

Logs are prefixed with `[GoldEA]` and include:

- project/phase/version
- full configuration, including `DRY_RUN`
- dynamic symbol specification
- permissions at startup
- safety-lock state
- recovery/position discovery
- volume validation result
- spread check result
- margin values and required margin
- execution request details
- dry-run actions
- broker retcodes and error text
- close/modify requests and results
- periodic read-only status snapshots

## Build and deployment

Repository build:

1. Open `EA/GoldEA.mq5` in MetaEditor.
2. Compile. Include files resolve from `EA/GoldEA/`.
3. The generated `EA/GoldEA.ex5` is ignored by Git.

Terminal deployment:

1. Copy `EA/GoldEA.mq5` and the `EA/GoldEA/` folder into
   `<terminal data folder>/MQL5/Experts/GoldEA/`, preserving the folder layout.
2. Compile `GoldEA.mq5` in MetaEditor.
3. Attach the EA to an `XAUUSD` chart.
4. Leave `DRY_RUN=true` for Phase 1 validation.

The EA reads all broker symbol properties at runtime. No Exness XAUUSD values
are hardcoded.

## Self-test

`InpSelfTestOnInit=true` runs a validation-only suite. It:

- is disabled by default
- forces dry-run for every execution call
- never sends an order
- never modifies a position
- tests synthetic volume, spread, margin, permission, SL/TP, limit, magic and
  safety-lock cases
- exercises the live dry-run path when market preconditions allow it

The normal EA does not use the self-test path.
