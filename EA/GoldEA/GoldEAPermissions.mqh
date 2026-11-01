//+------------------------------------------------------------------+
//|                                          GoldEAPermissions.mqh |
//|                          Gold EA Project - Phase 1 Permissions   |
//+------------------------------------------------------------------+
#ifndef GEA_PERMISSIONS_MQH
#define GEA_PERMISSIONS_MQH

#include "GoldEALog.mqh"
#include "GoldEASymbol.mqh"

struct GoldEAPermissionState
{
   string symbol;
   bool   terminalTradeAllowed;
   bool   eaTradeAllowed;
   bool   accountTradeAllowed;
   bool   accountExpertAllowed;
   bool   terminalConnected;
   long   symbolTradeMode;
};

void GEA_CollectPermissions(const string symbol, GoldEAPermissionState &state)
{
   state.symbol                = symbol;
   state.terminalTradeAllowed  = (TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) != 0);
   state.eaTradeAllowed        = (MQLInfoInteger(MQL_TRADE_ALLOWED) != 0);
   state.accountTradeAllowed   = (AccountInfoInteger(ACCOUNT_TRADE_ALLOWED) != 0);
   state.accountExpertAllowed  = (AccountInfoInteger(ACCOUNT_TRADE_EXPERT) != 0);
   state.terminalConnected     = (TerminalInfoInteger(TERMINAL_CONNECTED) != 0);
   state.symbolTradeMode       = SymbolInfoInteger(symbol, SYMBOL_TRADE_MODE);
}

//+------------------------------------------------------------------+
//| Evaluate all permission gates                                    |
//|                                                                  |
//|  forOpening = true  -> new entries are checked against symbol     |
//|                        long-only / short-only / close-only modes. |
//|  forOpening = false -> closing an existing position is still      |
//|                        blocked only when the symbol is disabled.  |
//+------------------------------------------------------------------+
bool GEA_EvaluatePermissions(const GoldEAPermissionState &state,
                             const ENUM_ORDER_TYPE orderType,
                             const bool forOpening,
                             string &reason)
{
   reason = "";

   if(!state.terminalTradeAllowed)
      reason = GEA_AppendReason(reason, "terminal trading disabled (AutoTrading is off)");
   if(!state.eaTradeAllowed)
      reason = GEA_AppendReason(reason, "EA trading disabled (MQL_TRADE_ALLOWED is false)");
   if(!state.accountTradeAllowed)
      reason = GEA_AppendReason(reason, "account trading disabled (ACCOUNT_TRADE_ALLOWED is false)");
   if(!state.accountExpertAllowed)
      reason = GEA_AppendReason(reason, "expert trading disabled for account (ACCOUNT_TRADE_EXPERT is false)");

   if(state.symbolTradeMode == SYMBOL_TRADE_MODE_DISABLED)
      reason = GEA_AppendReason(reason, "symbol trading is disabled");

   if(forOpening)
     {
      if(state.symbolTradeMode == SYMBOL_TRADE_MODE_CLOSEONLY)
         reason = GEA_AppendReason(reason, "symbol is close-only");
      if(state.symbolTradeMode == SYMBOL_TRADE_MODE_LONGONLY && orderType == ORDER_TYPE_SELL)
         reason = GEA_AppendReason(reason, "symbol allows long positions only");
      if(state.symbolTradeMode == SYMBOL_TRADE_MODE_SHORTONLY && orderType == ORDER_TYPE_BUY)
         reason = GEA_AppendReason(reason, "symbol allows short positions only");
     }

   return(reason == "");
}

void GEA_LogPermissionState(const GoldEAPermissionState &state, const bool includeConnected)
{
   GEA_LogInfo("Terminal trade allowed : " + GEA_YesNo(state.terminalTradeAllowed));
   GEA_LogInfo("EA trade allowed       : " + GEA_YesNo(state.eaTradeAllowed));
   GEA_LogInfo("Account trade allowed  : " + GEA_YesNo(state.accountTradeAllowed));
   GEA_LogInfo("Account expert allowed : " + GEA_YesNo(state.accountExpertAllowed));
   if(includeConnected)
      GEA_LogInfo("Terminal connected     : " + GEA_YesNo(state.terminalConnected));
   GEA_LogInfo("Symbol trade mode      : " + GEA_SymbolTradeModeText(state.symbolTradeMode));
}

#endif // GEA_PERMISSIONS_MQH
//+------------------------------------------------------------------+
