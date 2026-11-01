//+------------------------------------------------------------------+
//|                                            GoldEATradeResult.mqh |
//|                          Gold EA Project - Phase 1 Result Handling|
//+------------------------------------------------------------------+
#ifndef GEA_TRADE_RESULT_MQH
#define GEA_TRADE_RESULT_MQH

#include "GoldEALog.mqh"
#include "GoldEAConfig.mqh"
#include "GoldEATypes.mqh"
#include "GoldEASafety.mqh"

bool GEA_IsAcceptedRetcode(const long retcode)
{
   return(retcode == TRADE_RETCODE_DONE ||
          retcode == TRADE_RETCODE_DONE_PARTIAL ||
          retcode == TRADE_RETCODE_PLACED);
}

//+------------------------------------------------------------------+
//| Non-transient failures that justify locking new entries           |
//+------------------------------------------------------------------+
bool GEA_IsCriticalRetcode(const long retcode)
{
   switch((uint)retcode)
     {
      case TRADE_RETCODE_TRADE_DISABLED:
      case TRADE_RETCODE_NO_MONEY:
      case TRADE_RETCODE_INVALID_VOLUME:
      case TRADE_RETCODE_INVALID_STOPS:
      case TRADE_RETCODE_INVALID_FILL:
      case TRADE_RETCODE_INVALID_ORDER:
      case TRADE_RETCODE_ONLY_REAL:
      case TRADE_RETCODE_LIMIT_POSITIONS:
      case TRADE_RETCODE_LIMIT_VOLUME:
         return(true);
     }
   return(false);
}

//+------------------------------------------------------------------+
//| Copy a broker result into the engine result and apply the lock   |
//+------------------------------------------------------------------+
void GEA_ApplyTradeResult(const MqlTradeResult &tradeResult,
                          const string stage,
                          GoldEAExecutionResult &result)
{
   result.retcode       = (long)tradeResult.retcode;
   result.retcodeText   = GEA_RetcodeText(result.retcode);
   result.orderTicket   = tradeResult.order;
   result.dealTicket    = tradeResult.deal;
   result.executedVolume = tradeResult.volume;
   result.brokerComment = tradeResult.comment;
   result.stage         = stage;

   if(GEA_IsAcceptedRetcode(result.retcode))
     {
      result.success          = true;
      result.validationPassed = true;
      result.reason           = "broker accepted the request";
      return;
     }

   result.success = false;
   result.reason  = result.retcodeText + " (retcode " + IntegerToString(result.retcode) + ")";
   if(result.brokerComment != "")
      result.reason += " | broker comment: " + result.brokerComment;

   int lastError = GetLastError();
   if(lastError != 0)
      result.reason += " | terminal error " + IntegerToString(lastError);

   if(g_config.lockOnCriticalError && GEA_IsCriticalRetcode(result.retcode))
     {
      GEA_SafetyLockActivate("critical-execution-error",
         result.reason + " | stage " + stage);
     }
}

//+------------------------------------------------------------------+
//| Common result log                                                |
//+------------------------------------------------------------------+
void GEA_LogExecutionResult(const string action, const GoldEAExecutionResult &result)
{
   if(result.dryRun && result.success)
     {
      GEA_LogWarn("DRY-RUN " + action + " | validation passed | volume " +
                  GEA_VolumeText(result.validatedVolume) + " | price " +
                  DoubleToString(result.price, 8) + " | SL " + DoubleToString(result.sl, 8) +
                  " | TP " + DoubleToString(result.tp, 8) + " | NO ORDER SENT");
      return;
     }

   if(result.success)
     {
      GEA_LogInfo("EXECUTED " + action + " | volume " + GEA_VolumeText(result.executedVolume) +
                  " | price " + DoubleToString(result.price, 8) +
                  " | retcode " + IntegerToString(result.retcode) + " (" + result.retcodeText + ")" +
                  " | order " + IntegerToString((long)result.orderTicket) +
                  " | deal " + IntegerToString((long)result.dealTicket));
      return;
     }

   GEA_LogError("REJECTED " + action + " | stage " + result.stage +
                " | reason: " + result.reason);
}

#endif // GEA_TRADE_RESULT_MQH
//+------------------------------------------------------------------+
