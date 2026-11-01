//+------------------------------------------------------------------+
//|                                                       GoldEA.mq5 |
//|                   Gold EA Project - Phase 0 + Phase 1 Framework  |
//|                                                                  |
//|  PURPOSE                                                         |
//|  Preserve the Phase 0 environment diagnostics and add the Phase 1 |
//|  execution and risk engine foundation for future strategies.     |
//|                                                                  |
//|  SAFETY                                                          |
//|  This EA contains NO strategy and NO entry signal. OnTick() does  |
//|  not place orders. Execution is only possible when a future       |
//|  strategy explicitly calls the engine. DRY_RUN defaults to true.  |
//+------------------------------------------------------------------+
#property copyright   "Gold EA Project"
#property version     "1.00"   // MQL5 requires major >= 1; project phase is v0.2
#property strict
#property description "Gold EA Phase 0 diagnostics + Phase 1 execution/risk engine."
#property description "No strategy and no automatic entries. DRY_RUN defaults to true."

#include "GoldEA/GoldEALog.mqh"
#include "GoldEA/GoldEAConfig.mqh"
#include "GoldEA/GoldEATypes.mqh"
#include "GoldEA/GoldEASymbol.mqh"
#include "GoldEA/GoldEASafety.mqh"
#include "GoldEA/GoldEAPermissions.mqh"
#include "GoldEA/GoldEARisk.mqh"
#include "GoldEA/GoldEAPositions.mqh"
#include "GoldEA/GoldEATradeResult.mqh"
#include "GoldEA/GoldEAExecution.mqh"
#include "GoldEA/GoldEASelfTest.mqh"
#include "GoldEA/GoldEAPhase0.mqh"

//+------------------------------------------------------------------+
//| Inputs                                                           |
//+------------------------------------------------------------------+
input group "=== Phase 1 - Execution safety ==="
input bool   DRY_RUN = true;                       // DRY_RUN: validate only, never send orders
input long   InpMagicNumber = 20261101;            // EA magic number (dedicated to this EA)
input bool   InpSafetyLockAtStartup = false;       // Activate the no-new-trades safety lock at startup
input bool   InpLockOnCriticalError = true;        // Lock new entries after a critical execution error

input group "=== Phase 1 - Spread and execution ==="
input int    InpMaxSpreadPoints = 50;              // Maximum allowed spread in broker points
input int    InpDeviationPoints = 30;              // Maximum price deviation / slippage in points
input string InpOrderComment = "GoldEA-P1";        // Order comment (maximum 31 characters)

input group "=== Phase 1 - Position limits ==="
input int    InpMaxTotalPositions = 10;            // Maximum open positions in the account
input int    InpMaxEAPositions = 5;                // Maximum open positions owned by this EA
input int    InpMaxBuyPositions = 3;               // Maximum EA-owned buy positions
input int    InpMaxSellPositions = 3;              // Maximum EA-owned sell positions
input double InpMaxEATotalVolume = 1.00;           // Maximum total EA-owned volume in lots

input group "=== Phase 1 - Margin protection ==="
input double InpMinFreeMarginPct = 30.0;           // Minimum free margin after trade (% of equity)
input double InpMinMarginLevelPct = 150.0;         // Minimum projected margin level (%)

input group "=== Phase 1 - Diagnostics ==="
input bool   InpRunPhase0Diagnostics = true;       // Run the Phase 0 environment report
input bool   InpLogExistingPositionsOnStart = true; // Log EA-owned positions during recovery
input int    InpStatusLogIntervalSeconds = 300;    // Periodic status log interval (0 = disable)
input bool   InpSelfTestOnInit = false;            // Run validation-only self-test (forced DRY_RUN)

//+------------------------------------------------------------------+
//| Globals                                                          |
//+------------------------------------------------------------------+
datetime g_lastStatusLog = 0;

//+------------------------------------------------------------------+
//| Copy inputs into the engine configuration                        |
//+------------------------------------------------------------------+
void GEA_LoadConfigFromInputs()
{
   g_config.dryRun                    = DRY_RUN;
   g_config.magicNumber               = InpMagicNumber;
   g_config.maxSpreadPoints           = InpMaxSpreadPoints;
   g_config.deviationPoints           = InpDeviationPoints;
   g_config.maxTotalPositions         = InpMaxTotalPositions;
   g_config.maxEAPositions            = InpMaxEAPositions;
   g_config.maxBuyPositions           = InpMaxBuyPositions;
   g_config.maxSellPositions          = InpMaxSellPositions;
   g_config.maxEATotalVolume          = InpMaxEATotalVolume;
   g_config.minFreeMarginPct          = InpMinFreeMarginPct;
   g_config.minMarginLevelPct         = InpMinMarginLevelPct;
   g_config.safetyLockAtStartup       = InpSafetyLockAtStartup;
   g_config.lockOnCriticalError       = InpLockOnCriticalError;
   g_config.statusLogIntervalSeconds  = InpStatusLogIntervalSeconds;
   g_config.orderComment              = InpOrderComment;
   g_config.runPhase0Diagnostics      = InpRunPhase0Diagnostics;
   g_config.logExistingPositionsOnStart = InpLogExistingPositionsOnStart;
   g_config.selfTestOnInit            = InpSelfTestOnInit;
}

//+------------------------------------------------------------------+
//| Engine header                                                    |
//+------------------------------------------------------------------+
void GEA_LogEngineHeader()
{
   Print("");
   Print("############################################################");
   Print("#  GoldEA v" + GEA_VERSION + " - " + GEA_PHASE);
   Print("#  Execution and risk foundation only. NO STRATEGY.");
   Print("#  No automatic entries. DRY_RUN=" + GEA_BoolText(DRY_RUN));
   Print("############################################################");
}

//+------------------------------------------------------------------+
//| Periodic read-only status snapshot                               |
//+------------------------------------------------------------------+
void GEA_LogStatusSnapshot()
{
   GoldEAMarketSnapshot snapshot;
   if(GEA_GetMarketSnapshot(g_symbolSpec, snapshot))
     {
      GEA_LogInfo("STATUS | Bid " + GEA_PriceText(snapshot.bid, g_symbolSpec.digits) +
                  " / Ask " + GEA_PriceText(snapshot.ask, g_symbolSpec.digits) +
                  " | spread " + GEA_PointsText(snapshot.spreadPoints) +
                  " / max " + IntegerToString(g_config.maxSpreadPoints) + " points" +
                  " | lock " + (GEA_SafetyIsLocked() ? "ACTIVE" : "clear") +
                  " | DRY_RUN " + GEA_BoolText(g_config.dryRun));
     }
   else
     {
      GEA_LogWarn("STATUS | quote unavailable: " + snapshot.error +
                  " | lock " + (GEA_SafetyIsLocked() ? "ACTIVE" : "clear") +
                  " | DRY_RUN " + GEA_BoolText(g_config.dryRun));
     }

   GoldEAPositionStats stats;
   GEA_CollectPositionStats(stats);
   GEA_LogInfo("STATUS | account positions " + IntegerToString(stats.totalAccount) +
               " | EA positions " + IntegerToString(stats.eaCount) +
               " | EA volume " + GEA_VolumeText(stats.eaVolume));
}

void GEA_StatusHeartbeat()
{
   if(g_config.statusLogIntervalSeconds <= 0)
      return;

   datetime now = TimeLocal();
   if(g_lastStatusLog == 0)
     {
      g_lastStatusLog = now;
      return;
     }
   if((now - g_lastStatusLog) < g_config.statusLogIntervalSeconds)
      return;

   g_lastStatusLog = now;
   GEA_LogStatusSnapshot();
}

//+------------------------------------------------------------------+
//| Engine initialisation after configuration and symbol load        |
//+------------------------------------------------------------------+
void GEA_InitialiseEngine()
{
   GEA_LogConfig(g_config);
   GEA_LogSymbolSpec(g_symbolSpec);

   GEA_LogSection("TRADING PERMISSIONS AT STARTUP");
   GoldEAPermissionState permissions;
   GEA_CollectPermissions(_Symbol, permissions);
   GEA_LogPermissionState(permissions, true);
   string permissionReason = "";
   if(!GEA_EvaluatePermissions(permissions, ORDER_TYPE_BUY, true, permissionReason))
      GEA_LogWarn("New entries are currently blocked: " + permissionReason);
   else
      GEA_LogInfo("Permission gates currently allow new entries.");

   GEA_LogSection("SAFETY LOCK STATE");
   GEA_LogSafetyState();

   GEA_RecoverOnInit();
}

//+------------------------------------------------------------------+
//| Expert initialization                                            |
//+------------------------------------------------------------------+
int OnInit()
{
   GEA_LoadConfigFromInputs();

   GEA_LogEngineHeader();

   string configReason = "";
   if(!GEA_ConfigValidate(g_config, configReason))
     {
      GEA_LogError("Invalid Phase 1 configuration: " + configReason);
      return(INIT_FAILED);
     }

   if(_Symbol == "")
     {
      GEA_LogError("No symbol is attached to the chart.");
      return(INIT_FAILED);
     }

   GEA_SafetyInit();
   if(g_config.safetyLockAtStartup)
      GEA_SafetyLockActivate("configuration", "safety lock enabled by input");

   if(!GEA_LoadSymbolSpec(_Symbol, g_symbolSpec))
     {
      GEA_LogError("Unable to load symbol specification for '" + _Symbol + "': " +
                   g_symbolSpec.loadError);
      return(INIT_FAILED);
     }

   GEA_InitialiseEngine();

   if(g_config.runPhase0Diagnostics)
      RunPhase0Diagnostics(_Symbol);
   else
      GEA_LogInfo("Phase 0 diagnostics disabled by input.");

   if(g_config.selfTestOnInit)
      GEA_RunSelfTest();

   g_lastStatusLog = TimeLocal();
   EventSetTimer(5);

   GEA_LogSection("PHASE 1 ENGINE READY");
   GEA_LogInfo("No strategy is attached. OnTick() contains no entry logic.");
   GEA_LogInfo("Execution remains idle until a future strategy explicitly calls the engine.");
   GEA_LogInfo("DRY_RUN=" + GEA_BoolText(g_config.dryRun) +
               " | magic=" + IntegerToString(g_config.magicNumber) +
               " | safety lock=" + GEA_SafetyLockSummary());
   GEA_LogInfo("Phase 1 initialization complete.");

   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//|                                                                  |
//|  PHASE 1 RULE: no strategy entry logic lives here. This function  |
//|  only performs read-only status/logging work. It never calls      |
//|  GEA_ExecuteMarket(), GEA_CloseEAPosition() or                    |
//|  GEA_ModifyEAPositionSLTP().                                     |
//+------------------------------------------------------------------+
void OnTick()
{
   GEA_StatusHeartbeat();
}

//+------------------------------------------------------------------+
//| Timer keeps diagnostics alive even when no ticks arrive           |
//+------------------------------------------------------------------+
void OnTimer()
{
   GEA_StatusHeartbeat();
}

//+------------------------------------------------------------------+
//| Expert deinitialization                                          |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   GEA_LogInfo("GoldEA stopped. Reason: " + DeinitReasonText(reason));
   GEA_LogSafetyState();
   GEA_LogInfo("OnDeinit does not close positions. Open EA positions remain untouched.");
}
//+------------------------------------------------------------------+
