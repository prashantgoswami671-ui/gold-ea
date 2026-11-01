//+------------------------------------------------------------------+
//|                                            GoldEAExecution.mqh |
//|                          Gold EA Project - Phase 1 Execution     |
//|                                                                  |
//|  Reusable market BUY / SELL wrapper. Every request passes the    |
//|  same safety pipeline. DRY_RUN stops the request before send.    |
//+------------------------------------------------------------------+
#ifndef GEA_EXECUTION_MQH
#define GEA_EXECUTION_MQH

#include "GoldEALog.mqh"
#include "GoldEAConfig.mqh"
#include "GoldEATypes.mqh"
#include "GoldEASymbol.mqh"
#include "GoldEASafety.mqh"
#include "GoldEAPermissions.mqh"
#include "GoldEARisk.mqh"
#include "GoldEAPositions.mqh"
#include "GoldEATradeResult.mqh"

//+------------------------------------------------------------------+
//| Fully validated market order                                     |
//+------------------------------------------------------------------+
struct GoldEAPreparedOrder
{
   bool             valid;
   ENUM_ORDER_TYPE  type;
   string           symbol;
   double           volume;
   double           price;
   double           sl;
   double           tp;
   int              deviation;
   long             magic;
   long             filling;
   string           comment;
   double           requiredMargin;
};

//+------------------------------------------------------------------+
//| Validate every pre-trade safety gate                             |
//+------------------------------------------------------------------+
bool GEA_PrepareMarketOrder(const ENUM_ORDER_TYPE orderType,
                            const double requestedVolume,
                            const double requestedSL,
                            const double requestedTP,
                            const string comment,
                            GoldEAPreparedOrder &prepared,
                            GoldEAExecutionResult &result)
{
   prepared.valid          = false;
   prepared.type           = orderType;
   prepared.symbol         = _Symbol;
   prepared.volume         = 0.0;
   prepared.price          = 0.0;
   prepared.sl             = 0.0;
   prepared.tp             = 0.0;
   prepared.deviation      = g_config.deviationPoints;
   prepared.magic          = g_config.magicNumber;
   prepared.filling        = g_symbolSpec.selectedFilling;
   string effectiveComment = (comment == "") ? g_config.orderComment : comment;
   prepared.comment        = GEA_SanitizeComment(effectiveComment);
   prepared.requiredMargin = 0.0;

   result.requestedVolume = requestedVolume;
   result.stage           = "prepare";

   if(orderType != ORDER_TYPE_BUY && orderType != ORDER_TYPE_SELL)
     {
      result.reason = "only market BUY and SELL are supported";
      result.stage  = "order-type";
      return(false);
     }

   string lockReason = "";
   if(!GEA_SafetyAllowNewTrades(lockReason))
     {
      result.reason = lockReason;
      result.stage  = "safety-lock";
      return(false);
     }

   GoldEAPermissionState permissions;
   GEA_CollectPermissions(_Symbol, permissions);
   string permissionReason = "";
   if(!GEA_EvaluatePermissions(permissions, orderType, true, permissionReason))
     {
      result.reason = permissionReason;
      result.stage  = "permissions";
      return(false);
     }

   if(!g_symbolSpec.valid)
     {
      result.reason = "symbol specification is not valid";
      result.stage  = "symbol-spec";
      return(false);
     }

   GoldEAMarketSnapshot snapshot;
   if(!GEA_GetMarketSnapshot(g_symbolSpec, snapshot))
     {
      result.reason = snapshot.error;
      result.stage  = "market-data";
      return(false);
     }

   double normalizedVolume = 0.0;
   string volumeReason = "";
   if(!GEA_NormalizeVolume(g_symbolSpec, requestedVolume, normalizedVolume, volumeReason))
     {
      result.reason = volumeReason;
      result.stage  = "volume";
      return(false);
     }
   result.validatedVolume = normalizedVolume;

   GEA_LogInfo("Validated volume       : " + GEA_VolumeText(requestedVolume) +
               " requested -> " + GEA_VolumeText(normalizedVolume) + " executable");

   double spreadPoints = 0.0;
   string spreadReason = "";
   if(!GEA_EvaluateSpread(snapshot.bid, snapshot.ask, snapshot.point,
                          g_config.maxSpreadPoints, spreadPoints, spreadReason))
     {
      result.reason = spreadReason;
      result.stage  = "spread";
      return(false);
     }
   GEA_LogInfo("Spread check           : " + GEA_PointsText(spreadPoints) +
               " points <= maximum " + IntegerToString(g_config.maxSpreadPoints));

   double normalizedSL = 0.0;
   double normalizedTP = 0.0;
   string stopReason = "";
   if(!GEA_ValidateStops(g_symbolSpec, orderType, snapshot.bid, snapshot.ask,
                         requestedSL, requestedTP, normalizedSL, normalizedTP, stopReason))
     {
      result.reason = stopReason;
      result.stage  = "stops";
      return(false);
     }
   result.sl = normalizedSL;
   result.tp = normalizedTP;

   GoldEAPositionStats stats;
   GEA_CollectPositionStats(stats);
   string limitReason = "";
   if(!GEA_EvaluatePositionLimits(stats, orderType, normalizedVolume, g_config, limitReason))
     {
      result.reason = limitReason;
      result.stage  = "position-limits";
      return(false);
     }

   double price = (orderType == ORDER_TYPE_BUY) ? snapshot.ask : snapshot.bid;
   double requiredMargin = 0.0;
   string marginReason = "";
   if(!GEA_CalcRequiredMargin(g_symbolSpec, orderType, normalizedVolume, price, requiredMargin, marginReason))
     {
      result.reason = marginReason;
      result.stage  = "margin-calculation";
      return(false);
     }

   double equity      = AccountInfoDouble(ACCOUNT_EQUITY);
   double freeMargin  = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   double marginUsed  = AccountInfoDouble(ACCOUNT_MARGIN);
   if(!GEA_EvaluateMargin(equity, freeMargin, marginUsed, requiredMargin,
                          g_config.minFreeMarginPct, g_config.minMarginLevelPct, marginReason))
     {
      result.reason = marginReason;
      result.stage  = "margin";
      return(false);
     }

   GEA_LogInfo("Margin check           : required " + DoubleToString(requiredMargin, 2) +
               " | equity " + DoubleToString(equity, 2) +
               " | free " + DoubleToString(freeMargin, 2) +
               " | used " + DoubleToString(marginUsed, 2));

   prepared.valid          = true;
   prepared.volume         = normalizedVolume;
   prepared.price          = price;
   prepared.sl             = normalizedSL;
   prepared.tp             = normalizedTP;
   prepared.requiredMargin = requiredMargin;

   result.price           = price;
   result.validationPassed = true;
   result.stage           = "prepared";
   return(true);
}

//+------------------------------------------------------------------+
//| Execute a validated market order, or simulate it in DRY_RUN      |
//|                                                                  |
//|  forceDryRun is for the controlled internal self-test only. It   |
//|  can never turn a DRY_RUN request into a live request.           |
//+------------------------------------------------------------------+
bool GEA_ExecuteMarket(const ENUM_ORDER_TYPE orderType,
                       const double requestedVolume,
                       const double requestedSL,
                       const double requestedTP,
                       const string comment,
                       GoldEAExecutionResult &result,
                       const bool forceDryRun = false)
{
   GEA_ResetExecutionResult(result);
   bool effectiveDryRun = (g_config.dryRun || forceDryRun);
   result.dryRun = effectiveDryRun;

   string action = (orderType == ORDER_TYPE_BUY) ? "OPEN BUY" : "OPEN SELL";
   GoldEAPreparedOrder prepared;

   if(!GEA_PrepareMarketOrder(orderType, requestedVolume, requestedSL, requestedTP,
                              comment, prepared, result))
     {
      result.dryRun = effectiveDryRun;
      GEA_LogExecutionResult(action, result);
      return(false);
     }

   GEA_LogInfo("EXECUTION REQUEST      : " + action +
               " | symbol " + prepared.symbol +
               " | volume " + GEA_VolumeText(prepared.volume) +
               " | price " + DoubleToString(prepared.price, g_symbolSpec.digits) +
               " | SL " + DoubleToString(prepared.sl, g_symbolSpec.digits) +
               " | TP " + DoubleToString(prepared.tp, g_symbolSpec.digits) +
               " | deviation " + IntegerToString(prepared.deviation) + " points" +
               " | magic " + IntegerToString(prepared.magic) +
               " | fill " + GEA_OrderFillingText(prepared.filling) +
               " | comment " + prepared.comment +
               " | dryRun=" + GEA_BoolText(effectiveDryRun));

   if(effectiveDryRun)
     {
      result.success          = true;
      result.validationPassed = true;
      result.sent             = false;
      result.stage            = "dry-run-open";
      result.reason           = "dry-run: order not sent";
      GEA_LogExecutionResult(action, result);
      return(true);
     }

   MqlTradeRequest request;
   MqlTradeResult  tradeResult;
   ZeroMemory(request);
   ZeroMemory(tradeResult);

   request.action       = TRADE_ACTION_DEAL;
   request.symbol       = prepared.symbol;
   request.volume       = prepared.volume;
   request.type         = prepared.type;
   request.price        = prepared.price;
   request.sl           = prepared.sl;
   request.tp           = prepared.tp;
   request.deviation    = prepared.deviation;
   request.magic        = (ulong)prepared.magic;
   request.comment      = prepared.comment;
   request.type_time    = ORDER_TIME_GTC;
   request.type_filling = (ENUM_ORDER_TYPE_FILLING)prepared.filling;

   result.sent = true;
   bool sent = OrderSend(request, tradeResult);
   GEA_ApplyTradeResult(tradeResult, "open", result);
   if(!sent && result.retcode == 0)
      result.reason = "OrderSend returned false, error " + IntegerToString(GetLastError());

   GEA_LogExecutionResult(action, result);
   return(result.success);
}

bool GEA_ExecuteMarketBuy(const double volume,
                          const double sl,
                          const double tp,
                          const string comment,
                          GoldEAExecutionResult &result)
{
   return(GEA_ExecuteMarket(ORDER_TYPE_BUY, volume, sl, tp, comment, result, false));
}

bool GEA_ExecuteMarketSell(const double volume,
                           const double sl,
                           const double tp,
                           const string comment,
                           GoldEAExecutionResult &result)
{
   return(GEA_ExecuteMarket(ORDER_TYPE_SELL, volume, sl, tp, comment, result, false));
}

#endif // GEA_EXECUTION_MQH
//+------------------------------------------------------------------+
