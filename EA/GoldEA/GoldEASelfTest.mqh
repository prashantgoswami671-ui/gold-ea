//+------------------------------------------------------------------+
//|                                              GoldEASelfTest.mqh |
//|                          Gold EA Project - Phase 1 Self-Test     |
//|                                                                  |
//|  Optional validation-only test path. Forced DRY_RUN. It can      |
//|  never send an order and never modifies a position.              |
//+------------------------------------------------------------------+
#ifndef GEA_SELFTEST_MQH
#define GEA_SELFTEST_MQH

#include "GoldEAExecution.mqh"

int g_selfTestPass = 0;
int g_selfTestFail = 0;
int g_selfTestSkip = 0;

void GEA_STAssert(const string name, const bool condition, const string detail)
{
   if(condition)
     {
      g_selfTestPass++;
      GEA_LogPass(name, detail);
     }
   else
     {
      g_selfTestFail++;
      GEA_LogFail(name, detail);
     }
}

void GEA_STSkip(const string name, const string detail)
{
   g_selfTestSkip++;
   GEA_LogWarn("SKIP  " + name + " | " + detail);
}

//+------------------------------------------------------------------+
//| Run the controlled Phase 1 validation suite                      |
//+------------------------------------------------------------------+
void GEA_RunSelfTest()
{
   g_selfTestPass = 0;
   g_selfTestFail = 0;
   g_selfTestSkip = 0;

   GEA_LogSection("PHASE 1 SELF-TEST (VALIDATION ONLY, FORCED DRY-RUN)");
   GEA_LogWarn("Self-test never sends orders and never modifies positions.");

   //--- 1. Symbol specification --------------------------------
   GEA_STAssert("symbol-spec-loaded",
                g_symbolSpec.valid && g_symbolSpec.point > 0.0 &&
                g_symbolSpec.volumeMin > 0.0 && g_symbolSpec.volumeStep > 0.0,
                g_symbolSpec.valid ? "spec loaded for " + g_symbolSpec.symbol : g_symbolSpec.loadError);

   //--- Synthetic spec for deterministic volume checks ---------
   GoldEASymbolSpec testSpec = g_symbolSpec;
   testSpec.volumeMin   = 0.01;
   testSpec.volumeMax   = 1.00;
   testSpec.volumeStep  = 0.01;
   testSpec.volumeLimit = 0.0;

   double normalized = 0.0;
   string reason = "";

   bool belowOk = GEA_NormalizeVolume(testSpec, 0.005, normalized, reason);
   GEA_STAssert("volume-below-minimum", !belowOk, "request 0.005 -> " + reason);

   bool aboveOk = GEA_NormalizeVolume(testSpec, 1.01, normalized, reason);
   GEA_STAssert("volume-above-maximum", !aboveOk, "request 1.01 -> " + reason);

   bool stepOk = GEA_NormalizeVolume(testSpec, 0.015, normalized, reason);
   GEA_STAssert("volume-step-normalisation",
                stepOk && MathAbs(normalized - 0.01) < 1e-9,
                "request 0.015 -> " + GEA_VolumeText(normalized) + " | " + reason);

   bool zeroOk = GEA_NormalizeVolume(testSpec, 0.0, normalized, reason);
   GEA_STAssert("volume-invalid-zero", !zeroOk, reason);

   GoldEASymbolSpec invalidStepSpec = testSpec;
   invalidStepSpec.volumeStep = 0.0;
   bool invalidStepOk = GEA_NormalizeVolume(invalidStepSpec, 0.01, normalized, reason);
   GEA_STAssert("volume-invalid-broker-step", !invalidStepOk, reason);

   //--- Spread -------------------------------------------------
   double spreadPoints = 0.0;
   bool spreadHigh = GEA_EvaluateSpread(2000.00, 2000.50, 0.01, 20, spreadPoints, reason);
   GEA_STAssert("spread-above-limit", !spreadHigh,
                GEA_PointsText(spreadPoints) + " points | " + reason);

   bool spreadNormal = GEA_EvaluateSpread(2000.00, 2000.10, 0.01, 20, spreadPoints, reason);
   GEA_STAssert("spread-within-limit",
                spreadNormal && MathAbs(spreadPoints - 10.0) < 1e-9,
                GEA_PointsText(spreadPoints) + " points | " + reason);

   //--- Margin -------------------------------------------------
   bool marginBad = GEA_EvaluateMargin(1000.0, 1000.0, 0.0, 800.0, 30.0, 150.0, reason);
   GEA_STAssert("margin-insufficient", !marginBad, reason);

   bool marginGood = GEA_EvaluateMargin(10000.0, 10000.0, 0.0, 1000.0, 30.0, 150.0, reason);
   GEA_STAssert("margin-sufficient", marginGood, "projected free margin remains above buffer");

   //--- Permissions --------------------------------------------
   GoldEAPermissionState permissionState;
   permissionState.symbol               = g_symbolSpec.symbol;
   permissionState.terminalTradeAllowed = true;
   permissionState.eaTradeAllowed       = true;
   permissionState.accountTradeAllowed  = true;
   permissionState.accountExpertAllowed = true;
   permissionState.terminalConnected    = true;
   permissionState.symbolTradeMode      = SYMBOL_TRADE_MODE_FULL;

   string permissionReason = "";
   bool permissionGood = GEA_EvaluatePermissions(permissionState, ORDER_TYPE_BUY, true, permissionReason);
   GEA_STAssert("permissions-enabled", permissionGood, "all synthetic permissions enabled");

   permissionState.terminalTradeAllowed = false;
   bool permissionBad = GEA_EvaluatePermissions(permissionState, ORDER_TYPE_BUY, true, permissionReason);
   GEA_STAssert("permissions-disabled", !permissionBad, permissionReason);

   //--- SL / TP ------------------------------------------------
   double normalizedSL = 0.0;
   double normalizedTP = 0.0;
   GoldEASymbolSpec stopsSpec = g_symbolSpec;
   stopsSpec.digits           = 2;
   stopsSpec.point            = 0.01;
   stopsSpec.tickSize         = 0.01;
   stopsSpec.stopsLevelPoints = 50;

   bool slBad = GEA_ValidateStops(stopsSpec, ORDER_TYPE_BUY, 2000.00, 2000.20,
                                  1999.80, 0.0, normalizedSL, normalizedTP, reason);
   GEA_STAssert("invalid-sl", !slBad, reason);

   bool tpBad = GEA_ValidateStops(stopsSpec, ORDER_TYPE_BUY, 2000.00, 2000.20,
                                  0.0, 2000.40, normalizedSL, normalizedTP, reason);
   GEA_STAssert("invalid-tp", !tpBad, reason);

   bool slWrongSide = GEA_ValidateStops(stopsSpec, ORDER_TYPE_BUY, 2000.00, 2000.20,
                                        2001.00, 0.0, normalizedSL, normalizedTP, reason);
   GEA_STAssert("invalid-sl-wrong-side", !slWrongSide, reason);

   bool tpWrongSide = GEA_ValidateStops(stopsSpec, ORDER_TYPE_BUY, 2000.00, 2000.20,
                                        0.0, 1999.00, normalizedSL, normalizedTP, reason);
   GEA_STAssert("invalid-tp-wrong-side", !tpWrongSide, reason);

   bool stopsGood = GEA_ValidateStops(stopsSpec, ORDER_TYPE_BUY, 2000.00, 2000.20,
                                      1999.00, 2001.00, normalizedSL, normalizedTP, reason);
   GEA_STAssert("valid-sl-tp", stopsGood, "SL 1999.00 / TP 2001.00");

   bool sellStopsGood = GEA_ValidateStops(stopsSpec, ORDER_TYPE_SELL, 2000.00, 2000.20,
                                          2001.00, 1999.00, normalizedSL, normalizedTP, reason);
   GEA_STAssert("valid-sell-sl-tp", sellStopsGood, "SELL SL 2001.00 / TP 1999.00");

   //--- Position limits ----------------------------------------
   GoldEAPositionStats stats;
   GEA_ResetPositionStats(stats);
   stats.totalAccount = 5;
   stats.eaCount      = 4;
   stats.eaBuys       = 3;
   stats.eaSells      = 1;
   stats.eaVolume     = 0.40;

   GoldEAConfig limitConfig = g_config;
   limitConfig.maxTotalPositions = 10;
   limitConfig.maxEAPositions    = 5;
   limitConfig.maxBuyPositions   = 3;
   limitConfig.maxSellPositions  = 3;
   limitConfig.maxEATotalVolume  = 1.00;

   bool buyLimitBad = GEA_EvaluatePositionLimits(stats, ORDER_TYPE_BUY, 0.10, limitConfig, reason);
   GEA_STAssert("max-buy-limit", !buyLimitBad, reason);

   bool sellLimitGood = GEA_EvaluatePositionLimits(stats, ORDER_TYPE_SELL, 0.10, limitConfig, reason);
   GEA_STAssert("sell-within-limits", sellLimitGood, "sell count and volume within configured limits");

   stats.totalAccount = 10;
   bool totalLimitBad = GEA_EvaluatePositionLimits(stats, ORDER_TYPE_SELL, 0.10, limitConfig, reason);
   GEA_STAssert("max-total-positions", !totalLimitBad, reason);

   //--- Magic isolation ----------------------------------------
   GEA_STAssert("magic-isolation-match",
                GEA_IsOwnedPosition(g_symbolSpec.symbol, g_config.magicNumber,
                                    g_symbolSpec.symbol, g_config.magicNumber),
                "same symbol and magic is owned");
   GEA_STAssert("magic-isolation-foreign-magic",
                !GEA_IsOwnedPosition(g_symbolSpec.symbol, g_config.magicNumber + 1,
                                     g_symbolSpec.symbol, g_config.magicNumber),
                "different magic is rejected");
   GEA_STAssert("magic-isolation-foreign-symbol",
                !GEA_IsOwnedPosition(g_symbolSpec.symbol + "-OTHER", g_config.magicNumber,
                                     g_symbolSpec.symbol, g_config.magicNumber),
                "different symbol is rejected");

   //--- Safety lock --------------------------------------------
   GoldEASafetyState savedSafety = g_safety;
   GEA_SafetyLockActivate("self-test", "synthetic safety-lock test");
   string lockReason = "";
   bool lockAllows = GEA_SafetyAllowNewTrades(lockReason);
   GEA_STAssert("safety-lock-blocks-entry", GEA_SafetyIsLocked() && !lockAllows, lockReason);
   g_safety = savedSafety;

   //--- Dry-run execution --------------------------------------
   GoldEAExecutionResult executionResult;
   bool dryRunResult = GEA_ExecuteMarket(ORDER_TYPE_BUY,
                                         g_symbolSpec.volumeMin,
                                         0.0, 0.0,
                                         "GEA-SELFTEST",
                                         executionResult,
                                         true);
   if(executionResult.dryRun && executionResult.success && !executionResult.sent)
     {
      GEA_STAssert("dry-run-execution", true,
                   "validation passed; result.dryRun=true, result.sent=false");
     }
   else if(!executionResult.success && executionResult.stage != "dry-run-open")
     {
      GEA_STSkip("dry-run-execution",
                 "live precondition rejected (" + executionResult.stage + "): " + executionResult.reason);
     }
   else
     {
      GEA_STAssert("dry-run-execution", false,
                   "unexpected dry-run result: sent=" + GEA_BoolText(executionResult.sent) +
                   " success=" + GEA_BoolText(executionResult.success));
     }

   //--- Read-only discovery / restart foundation ----------------
   GoldEAPositionStats liveStats;
   GEA_CollectPositionStats(liveStats);
   GEA_STAssert("position-discovery-readonly",
                liveStats.totalAccount >= 0 && liveStats.eaVolume >= 0.0,
                "account=" + IntegerToString(liveStats.totalAccount) +
                " | EA=" + IntegerToString(liveStats.eaCount) +
                " | EA volume=" + GEA_VolumeText(liveStats.eaVolume));

   GEA_STSkip("restart-reinitialisation", "manual test: remove/re-attach or restart and verify no duplicate orders");
   GEA_STSkip("zero-automatic-trades", "manual/static test: OnTick must contain no entry logic");

   GEA_LogSection("SELF-TEST SUMMARY");
   GEA_LogInfo("Passed : " + IntegerToString(g_selfTestPass));
   GEA_LogInfo("Failed : " + IntegerToString(g_selfTestFail));
   GEA_LogInfo("Skipped: " + IntegerToString(g_selfTestSkip));
   GEA_LogInfo("No order was sent. No position was modified.");
   if(g_selfTestFail > 0)
      GEA_LogError("Self-test reported failures. Review the log before any execution use.");
}

#endif // GEA_SELFTEST_MQH
//+------------------------------------------------------------------+
