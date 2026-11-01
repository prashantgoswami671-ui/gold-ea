//+------------------------------------------------------------------+
//|                                            GoldEAPositions.mqh |
//|                          Gold EA Project - Phase 1 Position Mgmt |
//|                                                                  |
//|  Every close/modify path verifies symbol AND magic number first.  |
//|  Foreign positions are never modified or closed.                 |
//+------------------------------------------------------------------+
#ifndef GEA_POSITIONS_MQH
#define GEA_POSITIONS_MQH

#include "GoldEALog.mqh"
#include "GoldEAConfig.mqh"
#include "GoldEATypes.mqh"
#include "GoldEASymbol.mqh"
#include "GoldEAPermissions.mqh"
#include "GoldEARisk.mqh"
#include "GoldEATradeResult.mqh"

//+------------------------------------------------------------------+
//| Pure ownership test (also used by the self-test)                 |
//+------------------------------------------------------------------+
bool GEA_IsOwnedPosition(const string positionSymbol,
                         const long positionMagic,
                         const string eaSymbol,
                         const long eaMagic)
{
   return(positionSymbol == eaSymbol && positionMagic == eaMagic);
}

string GEA_PositionTypeText(const ENUM_POSITION_TYPE type)
{
   if(type == POSITION_TYPE_BUY)
      return("BUY");
   if(type == POSITION_TYPE_SELL)
      return("SELL");
   return("UNKNOWN (" + IntegerToString((int)type) + ")");
}

//+------------------------------------------------------------------+
//| Read one position by ticket                                      |
//+------------------------------------------------------------------+
bool GEA_ReadPosition(const ulong ticket, GoldEAPositionInfo &info)
{
   info.ticket    = 0;
   info.magic     = 0;
   info.symbol    = "";
   info.type      = POSITION_TYPE_BUY;
   info.volume    = 0.0;
   info.priceOpen = 0.0;
   info.sl        = 0.0;
   info.tp        = 0.0;
   info.profit    = 0.0;
   info.swap      = 0.0;
   info.time      = 0;
   info.comment   = "";

   if(ticket == 0 || !PositionSelectByTicket(ticket))
      return(false);

   info.ticket    = ticket;
   info.magic     = PositionGetInteger(POSITION_MAGIC);
   info.symbol    = PositionGetString(POSITION_SYMBOL);
   info.type      = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
   info.volume    = PositionGetDouble(POSITION_VOLUME);
   info.priceOpen = PositionGetDouble(POSITION_PRICE_OPEN);
   info.sl        = PositionGetDouble(POSITION_SL);
   info.tp        = PositionGetDouble(POSITION_TP);
   info.profit    = PositionGetDouble(POSITION_PROFIT);
   info.swap      = PositionGetDouble(POSITION_SWAP);
   info.time      = (datetime)PositionGetInteger(POSITION_TIME);
   info.comment   = PositionGetString(POSITION_COMMENT);
   return(true);
}

//+------------------------------------------------------------------+
//| Select a position only if it belongs to this EA                  |
//+------------------------------------------------------------------+
bool GEA_SelectEAPosition(const ulong ticket, GoldEAPositionInfo &info)
{
   if(!GEA_ReadPosition(ticket, info))
     {
      GEA_LogError("Position #" + IntegerToString((long)ticket) + " does not exist.");
      return(false);
     }

   if(!GEA_IsOwnedPosition(info.symbol, info.magic, _Symbol, g_config.magicNumber))
     {
      GEA_LogError("REFUSING to touch position #" + IntegerToString((long)ticket) +
                   " | symbol=" + info.symbol + " | magic=" + IntegerToString(info.magic) +
                   " | this EA owns symbol=" + _Symbol + " magic=" + IntegerToString(g_config.magicNumber));
      return(false);
     }

   return(true);
}

//+------------------------------------------------------------------+
//| Collect all EA-owned positions                                   |
//+------------------------------------------------------------------+
int GEA_CollectEAPositions(GoldEAPositionInfo &positions[])
{
   ArrayResize(positions, 0);
   int count = 0;
   int total = PositionsTotal();

   for(int index = 0; index < total; index++)
     {
      ulong ticket = PositionGetTicket(index);
      if(ticket == 0)
         continue;
      if(!PositionSelectByTicket(ticket))
         continue;

      string symbol = PositionGetString(POSITION_SYMBOL);
      long   magic  = PositionGetInteger(POSITION_MAGIC);
      if(!GEA_IsOwnedPosition(symbol, magic, _Symbol, g_config.magicNumber))
         continue;

      GoldEAPositionInfo info;
      if(!GEA_ReadPosition(ticket, info))
         continue;

      ArrayResize(positions, count + 1);
      positions[count] = info;
      count++;
     }

   return(count);
}

//+------------------------------------------------------------------+
//| Count account, symbol and EA-owned positions                     |
//+------------------------------------------------------------------+
void GEA_CollectPositionStats(GoldEAPositionStats &stats)
{
   GEA_ResetPositionStats(stats);
   int total = PositionsTotal();

   for(int index = 0; index < total; index++)
     {
      ulong ticket = PositionGetTicket(index);
      if(ticket == 0)
         continue;
      if(!PositionSelectByTicket(ticket))
         continue;

      string symbol = PositionGetString(POSITION_SYMBOL);
      long   magic  = PositionGetInteger(POSITION_MAGIC);
      double volume = PositionGetDouble(POSITION_VOLUME);
      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);

      stats.totalAccount++;
      if(symbol == _Symbol)
         stats.totalSymbol++;

      if(!GEA_IsOwnedPosition(symbol, magic, _Symbol, g_config.magicNumber))
         continue;

      stats.eaCount++;
      stats.eaVolume += volume;
      if(type == POSITION_TYPE_BUY)
        {
         stats.eaBuys++;
         stats.eaBuyVolume += volume;
        }
      else if(type == POSITION_TYPE_SELL)
        {
         stats.eaSells++;
         stats.eaSellVolume += volume;
        }
     }
}

bool GEA_HasEAPosition(const ENUM_POSITION_TYPE type)
{
   GoldEAPositionStats stats;
   GEA_CollectPositionStats(stats);
   if(type == POSITION_TYPE_BUY)
      return(stats.eaBuys > 0);
   if(type == POSITION_TYPE_SELL)
      return(stats.eaSells > 0);
   return(stats.eaCount > 0);
}

//+------------------------------------------------------------------+
//| Logging helpers                                                  |
//+------------------------------------------------------------------+
void GEA_LogEAPositions()
{
   GoldEAPositionInfo positions[];
   int count = GEA_CollectEAPositions(positions);

   if(count == 0)
     {
      GEA_LogInfo("EA-owned positions    : none");
      return;
     }

   GEA_LogInfo("EA-owned positions    : " + IntegerToString(count));
   for(int index = 0; index < count; index++)
     {
      GEA_LogInfo("  #" + IntegerToString((long)positions[index].ticket) +
                  " | " + GEA_PositionTypeText(positions[index].type) +
                  " | volume " + GEA_VolumeText(positions[index].volume) +
                  " | open " + DoubleToString(positions[index].priceOpen, g_symbolSpec.digits) +
                  " | SL " + DoubleToString(positions[index].sl, g_symbolSpec.digits) +
                  " | TP " + DoubleToString(positions[index].tp, g_symbolSpec.digits) +
                  " | profit " + DoubleToString(positions[index].profit, 2));
     }
}

//+------------------------------------------------------------------+
//| Restart / reinitialisation foundation                            |
//|                                                                  |
//|  Only discovers and logs. It never opens, closes or modifies.    |
//+------------------------------------------------------------------+
void GEA_RecoverOnInit()
{
   GEA_LogSection("RESTART / RECOVERY CHECK");

   GoldEAPositionStats stats;
   GEA_CollectPositionStats(stats);

   GEA_LogInfo("Account positions      : " + IntegerToString(stats.totalAccount));
   GEA_LogInfo("Positions on " + _Symbol + " : " + IntegerToString(stats.totalSymbol));
   GEA_LogInfo("EA positions (magic+symbol) : " + IntegerToString(stats.eaCount) +
               " | volume " + GEA_VolumeText(stats.eaVolume));
   GEA_LogInfo("EA buys / sells        : " + IntegerToString(stats.eaBuys) +
               " / " + IntegerToString(stats.eaSells));

   if(g_config.logExistingPositionsOnStart)
      GEA_LogEAPositions();

   GEA_LogInfo("Recovery policy        : read-only. No order sent, no position modified.");
   if(stats.eaCount > 0)
      GEA_LogWarn("EA-owned positions already exist after restart. No duplicate entry is generated by the engine.");
}

//+------------------------------------------------------------------+
//| Close one EA-owned position safely                               |
//+------------------------------------------------------------------+
bool GEA_CloseEAPosition(const ulong ticket, GoldEAExecutionResult &result)
{
   GEA_ResetExecutionResult(result);
   result.stage = "close-validate";

   GoldEAPositionInfo position;
   if(!GEA_SelectEAPosition(ticket, position))
     {
      result.reason = "position not found or not owned by this EA";
      result.stage  = "close-ownership";
      GEA_LogExecutionResult("CLOSE #" + IntegerToString((long)ticket), result);
      return(false);
     }

   result.requestedVolume = position.volume;
   result.validatedVolume = position.volume;
   result.sl              = position.sl;
   result.tp              = position.tp;

   if(!MathIsValidNumber(position.volume) || position.volume <= 0.0)
     {
      result.reason = "position volume is invalid";
      result.stage  = "close-volume";
      GEA_LogExecutionResult("CLOSE #" + IntegerToString((long)ticket), result);
      return(false);
     }

   GoldEAMarketSnapshot snapshot;
   if(!GEA_GetMarketSnapshot(g_symbolSpec, snapshot))
     {
      result.reason = snapshot.error;
      result.stage  = "close-market-data";
      GEA_LogExecutionResult("CLOSE #" + IntegerToString((long)ticket), result);
      return(false);
     }

   ENUM_ORDER_TYPE closeType = (position.type == POSITION_TYPE_BUY) ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
   double closePrice = (closeType == ORDER_TYPE_BUY) ? snapshot.ask : snapshot.bid;

   GoldEAPermissionState permissions;
   GEA_CollectPermissions(_Symbol, permissions);
   string permissionReason = "";
   if(!GEA_EvaluatePermissions(permissions, closeType, false, permissionReason))
     {
      result.reason = permissionReason;
      result.stage  = "close-permissions";
      GEA_LogExecutionResult("CLOSE #" + IntegerToString((long)ticket), result);
      return(false);
     }

   if(GEA_SafetyIsLocked())
      GEA_LogWarn("Safety lock is active, but closing an existing EA position is allowed.");

   result.price = closePrice;
   result.stage = "close-ready";

   GEA_LogInfo("CLOSE REQUEST #" + IntegerToString((long)ticket) +
               " | " + GEA_PositionTypeText(position.type) +
               " | volume " + GEA_VolumeText(position.volume) +
               " | price " + DoubleToString(closePrice, g_symbolSpec.digits) +
               " | dryRun=" + GEA_BoolText(g_config.dryRun));

   if(g_config.dryRun)
     {
      result.success          = true;
      result.validationPassed = true;
      result.dryRun           = true;
      result.sent             = false;
      result.stage            = "dry-run-close";
      result.reason           = "dry-run: close order not sent";
      GEA_LogExecutionResult("CLOSE #" + IntegerToString((long)ticket), result);
      return(true);
     }

   MqlTradeRequest request;
   MqlTradeResult  tradeResult;
   ZeroMemory(request);
   ZeroMemory(tradeResult);

   request.action       = TRADE_ACTION_DEAL;
   request.position     = ticket;
   request.symbol       = position.symbol;
   request.volume       = position.volume;
   request.type         = closeType;
   request.price        = closePrice;
   request.deviation    = g_config.deviationPoints;
   request.magic        = (ulong)g_config.magicNumber;
   request.comment      = GEA_SanitizeComment("GEA close");
   request.type_time    = ORDER_TIME_GTC;
   request.type_filling = (ENUM_ORDER_TYPE_FILLING)g_symbolSpec.selectedFilling;

   result.sent = true;
   bool sent = OrderSend(request, tradeResult);
   GEA_ApplyTradeResult(tradeResult, "close", result);
   if(!sent && result.retcode == 0)
      result.reason = "OrderSend returned false, error " + IntegerToString(GetLastError());

   GEA_LogExecutionResult("CLOSE #" + IntegerToString((long)ticket), result);
   return(result.success);
}

//+------------------------------------------------------------------+
//| Modify SL/TP of one EA-owned position safely                     |
//+------------------------------------------------------------------+
bool GEA_ModifyEAPositionSLTP(const ulong ticket,
                              const double sl,
                              const double tp,
                              GoldEAExecutionResult &result)
{
   GEA_ResetExecutionResult(result);
   result.stage = "modify-validate";

   GoldEAPositionInfo position;
   if(!GEA_SelectEAPosition(ticket, position))
     {
      result.reason = "position not found or not owned by this EA";
      result.stage  = "modify-ownership";
      GEA_LogExecutionResult("MODIFY #" + IntegerToString((long)ticket), result);
      return(false);
     }

   GoldEAMarketSnapshot snapshot;
   if(!GEA_GetMarketSnapshot(g_symbolSpec, snapshot))
     {
      result.reason = snapshot.error;
      result.stage  = "modify-market-data";
      GEA_LogExecutionResult("MODIFY #" + IntegerToString((long)ticket), result);
      return(false);
     }

   ENUM_ORDER_TYPE positionSide = (position.type == POSITION_TYPE_BUY) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   double normalizedSL = 0.0;
   double normalizedTP = 0.0;
   string stopReason = "";
   if(!GEA_ValidateStops(g_symbolSpec, positionSide, snapshot.bid, snapshot.ask,
                         sl, tp, normalizedSL, normalizedTP, stopReason))
     {
      result.reason = stopReason;
      result.stage  = "modify-stops";
      GEA_LogExecutionResult("MODIFY #" + IntegerToString((long)ticket), result);
      return(false);
     }

   if(MathAbs(normalizedSL - position.sl) < 1e-12 &&
      MathAbs(normalizedTP - position.tp) < 1e-12)
     {
      result.reason = "requested SL/TP are unchanged";
      result.stage  = "modify-no-change";
      GEA_LogExecutionResult("MODIFY #" + IntegerToString((long)ticket), result);
      return(false);
     }

   GoldEAPermissionState permissions;
   GEA_CollectPermissions(_Symbol, permissions);
   string permissionReason = "";
   if(!GEA_EvaluatePermissions(permissions, positionSide, false, permissionReason))
     {
      result.reason = permissionReason;
      result.stage  = "modify-permissions";
      GEA_LogExecutionResult("MODIFY #" + IntegerToString((long)ticket), result);
      return(false);
     }

   if(GEA_SafetyIsLocked())
      GEA_LogWarn("Safety lock is active, but risk-reducing SL/TP modification is allowed.");

   result.validatedVolume = position.volume;
   result.sl              = normalizedSL;
   result.tp              = normalizedTP;
   result.price           = position.priceOpen;
   result.stage           = "modify-ready";

   GEA_LogInfo("MODIFY REQUEST #" + IntegerToString((long)ticket) +
               " | SL " + DoubleToString(position.sl, g_symbolSpec.digits) +
               " -> " + DoubleToString(normalizedSL, g_symbolSpec.digits) +
               " | TP " + DoubleToString(position.tp, g_symbolSpec.digits) +
               " -> " + DoubleToString(normalizedTP, g_symbolSpec.digits) +
               " | dryRun=" + GEA_BoolText(g_config.dryRun));

   if(g_config.dryRun)
     {
      result.success          = true;
      result.validationPassed = true;
      result.dryRun           = true;
      result.sent             = false;
      result.stage            = "dry-run-modify";
      result.reason           = "dry-run: SL/TP modification not sent";
      GEA_LogExecutionResult("MODIFY #" + IntegerToString((long)ticket), result);
      return(true);
     }

   MqlTradeRequest request;
   MqlTradeResult  tradeResult;
   ZeroMemory(request);
   ZeroMemory(tradeResult);

   request.action    = TRADE_ACTION_SLTP;
   request.position  = ticket;
   request.symbol    = position.symbol;
   request.sl        = normalizedSL;
   request.tp        = normalizedTP;
   request.magic     = (ulong)g_config.magicNumber;
   request.comment   = GEA_SanitizeComment("GEA modify");

   result.sent = true;
   bool sent = OrderSend(request, tradeResult);
   GEA_ApplyTradeResult(tradeResult, "modify", result);
   if(!sent && result.retcode == 0)
      result.reason = "OrderSend returned false, error " + IntegerToString(GetLastError());

   GEA_LogExecutionResult("MODIFY #" + IntegerToString((long)ticket), result);
   return(result.success);
}

//+------------------------------------------------------------------+
//| Emergency close of all EA-owned positions                        |
//|                                                                  |
//|  Public capability only. Nothing calls this automatically.       |
//+------------------------------------------------------------------+
int GEA_CloseAllEAPositions(const string reason, int &closedCount, int &failedCount)
{
   closedCount = 0;
   failedCount = 0;

   GoldEAPositionInfo positions[];
   int count = GEA_CollectEAPositions(positions);
   if(count == 0)
     {
      GEA_LogInfo("Emergency close requested (" + reason + "): no EA-owned positions.");
      return(0);
     }

   GEA_LogWarn("Emergency close requested (" + reason + "): " + IntegerToString(count) +
               " EA-owned position(s). dryRun=" + GEA_BoolText(g_config.dryRun));

   ulong tickets[];
   ArrayResize(tickets, count);
   for(int index = 0; index < count; index++)
      tickets[index] = positions[index].ticket;

   for(int index = 0; index < count; index++)
     {
      GoldEAExecutionResult result;
      if(GEA_CloseEAPosition(tickets[index], result))
         closedCount++;
      else
         failedCount++;
     }

   GEA_LogInfo("Emergency close summary: closed/simulated=" + IntegerToString(closedCount) +
               " | failed=" + IntegerToString(failedCount));
   return(closedCount);
}

#endif // GEA_POSITIONS_MQH
//+------------------------------------------------------------------+
