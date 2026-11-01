//+------------------------------------------------------------------+
//|                                                 GoldEARisk.mqh |
//|                          Gold EA Project - Phase 1 Risk Checks   |
//|                                                                  |
//|  Pure, reusable safety checks. These functions never send orders. |
//+------------------------------------------------------------------+
#ifndef GEA_RISK_MQH
#define GEA_RISK_MQH

#include "GoldEALog.mqh"
#include "GoldEAConfig.mqh"
#include "GoldEATypes.mqh"
#include "GoldEASymbol.mqh"

//+------------------------------------------------------------------+
//| Position-count and exposure limits                               |
//|                                                                  |
//|  maxTotalPositions counts ALL open account positions. The limit  |
//|  only blocks a new EA entry; foreign positions are never touched. |
//+------------------------------------------------------------------+
bool GEA_EvaluatePositionLimits(const GoldEAPositionStats &stats,
                                const ENUM_ORDER_TYPE orderType,
                                const double volume,
                                const GoldEAConfig &cfg,
                                string &reason)
{
   reason = "";

   if(!MathIsValidNumber(volume) || volume <= 0.0)
     {
      reason = "position-limit check received an invalid volume";
      return(false);
     }

   if(stats.totalAccount + 1 > cfg.maxTotalPositions)
      reason = GEA_AppendReason(reason,
         "total account positions " + IntegerToString(stats.totalAccount) +
         " would exceed maximum " + IntegerToString(cfg.maxTotalPositions));

   if(stats.eaCount + 1 > cfg.maxEAPositions)
      reason = GEA_AppendReason(reason,
         "EA positions " + IntegerToString(stats.eaCount) +
         " would exceed maximum " + IntegerToString(cfg.maxEAPositions));

   if(orderType == ORDER_TYPE_BUY && stats.eaBuys + 1 > cfg.maxBuyPositions)
      reason = GEA_AppendReason(reason,
         "EA buy positions " + IntegerToString(stats.eaBuys) +
         " would exceed maximum " + IntegerToString(cfg.maxBuyPositions));

   if(orderType == ORDER_TYPE_SELL && stats.eaSells + 1 > cfg.maxSellPositions)
      reason = GEA_AppendReason(reason,
         "EA sell positions " + IntegerToString(stats.eaSells) +
         " would exceed maximum " + IntegerToString(cfg.maxSellPositions));

   double projectedVolume = stats.eaVolume + volume;
   if(projectedVolume > cfg.maxEATotalVolume + 1e-8)
      reason = GEA_AppendReason(reason,
         "projected EA volume " + GEA_VolumeText(projectedVolume) +
         " would exceed maximum " + GEA_VolumeText(cfg.maxEATotalVolume));

   return(reason == "");
}

//+------------------------------------------------------------------+
//| Ask the terminal for the margin required by a market order        |
//+------------------------------------------------------------------+
bool GEA_CalcRequiredMargin(const GoldEASymbolSpec &spec,
                            const ENUM_ORDER_TYPE orderType,
                            const double volume,
                            const double price,
                            double &requiredMargin,
                            string &reason)
{
   requiredMargin = 0.0;
   reason = "";

   double margin = 0.0;
   if(!OrderCalcMargin(orderType, spec.symbol, volume, price, margin))
     {
      reason = "OrderCalcMargin failed, error " + IntegerToString(GetLastError());
      return(false);
     }
   if(!MathIsValidNumber(margin) || margin < 0.0)
     {
      reason = "OrderCalcMargin returned an invalid margin value";
      return(false);
     }

   requiredMargin = margin;
   return(true);
}

//+------------------------------------------------------------------+
//| Margin protection                                                |
//|                                                                  |
//|  Both checks must pass:                                          |
//|   1. free margin remaining after the trade >= minFreePct equity   |
//|   2. projected margin level >= minLevelPct                        |
//+------------------------------------------------------------------+
bool GEA_EvaluateMargin(const double equity,
                        const double freeMargin,
                        const double marginUsed,
                        const double requiredMargin,
                        const double minFreeMarginPct,
                        const double minMarginLevelPct,
                        string &reason)
{
   reason = "";

   if(!MathIsValidNumber(equity) || equity <= 0.0)
     {
      reason = "account equity is not valid";
      return(false);
     }
   if(!MathIsValidNumber(freeMargin) || freeMargin < 0.0)
     {
      reason = "free margin is negative or invalid";
      return(false);
     }
   if(!MathIsValidNumber(marginUsed) || marginUsed < 0.0)
     {
      reason = "used margin is negative or invalid";
      return(false);
     }
   if(!MathIsValidNumber(requiredMargin) || requiredMargin < 0.0)
     {
      reason = "required margin is negative or invalid";
      return(false);
     }

   double projectedFree = freeMargin - requiredMargin;
   double requiredFree  = equity * minFreeMarginPct / 100.0;

   if(projectedFree < 0.0)
     {
      reason = "trade requires " + DoubleToString(requiredMargin, 2) +
               " but only " + DoubleToString(freeMargin, 2) + " free margin is available";
      return(false);
     }
   if(projectedFree < requiredFree - 1e-8)
     {
      reason = "projected free margin " + DoubleToString(projectedFree, 2) +
               " would be below required buffer " + DoubleToString(requiredFree, 2) +
               " (" + DoubleToString(minFreeMarginPct, 2) + "% of equity)";
      return(false);
     }

   double projectedUsed = marginUsed + requiredMargin;
   if(projectedUsed > 0.0 && minMarginLevelPct > 0.0)
     {
      double projectedLevel = equity / projectedUsed * 100.0;
      if(projectedLevel < minMarginLevelPct - 1e-8)
        {
         reason = "projected margin level " + DoubleToString(projectedLevel, 2) +
                  "% would be below minimum " + DoubleToString(minMarginLevelPct, 2) + "%";
         return(false);
        }
     }

   return(true);
}

//+------------------------------------------------------------------+
//| Stop-loss / take-profit validation                               |
//|                                                                  |
//|  Rules:                                                          |
//|   - BUY  SL below Bid, TP above Ask                              |
//|   - SELL SL above Ask, TP below Bid                              |
//|   - broker stops level respected in price distance               |
//|   - returned levels normalised to the symbol's digits            |
//|                                                                  |
//|  No strategy-specific distance is invented here.                 |
//+------------------------------------------------------------------+
bool GEA_ValidateStops(const GoldEASymbolSpec &spec,
                       const ENUM_ORDER_TYPE orderType,
                       const double bid,
                       const double ask,
                       const double sl,
                       const double tp,
                       double &normalizedSL,
                       double &normalizedTP,
                       string &reason)
{
   normalizedSL = 0.0;
   normalizedTP = 0.0;
   reason = "";

   if(orderType != ORDER_TYPE_BUY && orderType != ORDER_TYPE_SELL)
     {
      reason = "SL/TP validation only supports market BUY or SELL";
      return(false);
     }
   if(!spec.valid)
     {
      reason = "symbol specification is not valid";
      return(false);
     }
   if(!MathIsValidNumber(bid) || !MathIsValidNumber(ask) || bid <= 0.0 || ask <= 0.0)
     {
      reason = "no valid Bid/Ask quote is available";
      return(false);
     }
   if(!MathIsValidNumber(sl) || !MathIsValidNumber(tp) || sl < 0.0 || tp < 0.0)
     {
      reason = "SL/TP must be finite, zero or positive";
      return(false);
     }

   normalizedSL = (sl > 0.0) ? GEA_NormalizePrice(spec, sl) : 0.0;
   normalizedTP = (tp > 0.0) ? GEA_NormalizePrice(spec, tp) : 0.0;

   double stopsDistance = (double)spec.stopsLevelPoints * spec.point;
   double tolerance     = MathMax(spec.point * 1e-6, 1e-12);

   if(orderType == ORDER_TYPE_BUY)
     {
      if(normalizedSL > 0.0)
        {
         if(normalizedSL >= bid)
           {
            reason = "BUY stop loss must be below Bid";
            return(false);
           }
         if((bid - normalizedSL) < stopsDistance - tolerance)
           {
            reason = "BUY stop loss is closer than broker stops level (" +
                     IntegerToString(spec.stopsLevelPoints) + " points)";
            return(false);
           }
        }
      if(normalizedTP > 0.0)
        {
         if(normalizedTP <= ask)
           {
            reason = "BUY take profit must be above Ask";
            return(false);
           }
         if((normalizedTP - ask) < stopsDistance - tolerance)
           {
            reason = "BUY take profit is closer than broker stops level (" +
                     IntegerToString(spec.stopsLevelPoints) + " points)";
            return(false);
           }
        }
     }
   else
     {
      if(normalizedSL > 0.0)
        {
         if(normalizedSL <= ask)
           {
            reason = "SELL stop loss must be above Ask";
            return(false);
           }
         if((normalizedSL - ask) < stopsDistance - tolerance)
           {
            reason = "SELL stop loss is closer than broker stops level (" +
                     IntegerToString(spec.stopsLevelPoints) + " points)";
            return(false);
           }
        }
      if(normalizedTP > 0.0)
        {
         if(normalizedTP >= bid)
           {
            reason = "SELL take profit must be below Bid";
            return(false);
           }
         if((bid - normalizedTP) < stopsDistance - tolerance)
           {
            reason = "SELL take profit is closer than broker stops level (" +
                     IntegerToString(spec.stopsLevelPoints) + " points)";
            return(false);
           }
        }
     }

   return(true);
}

//+------------------------------------------------------------------+
//| Freeze-zone helper for future pending-order operations           |
//|                                                                  |
//|  Per MQL5 semantics, the freeze level applies to pending orders,  |
//|  not to market execution or position SL/TP modification. It is    |
//|  exposed here so a future pending-order layer cannot forget it.   |
//+------------------------------------------------------------------+
bool GEA_IsFreezeBlocked(const GoldEASymbolSpec &spec,
                         const double price,
                         const double bid,
                         const double ask)
{
   if(!spec.valid || spec.freezeLevelPoints <= 0 || spec.point <= 0.0)
      return(false);
   if(!MathIsValidNumber(price) || price <= 0.0)
      return(false);

   double freezeDistance = (double)spec.freezeLevelPoints * spec.point;
   double nearest = MathMin(MathAbs(price - bid), MathAbs(price - ask));
   return(nearest < freezeDistance);
}

#endif // GEA_RISK_MQH
//+------------------------------------------------------------------+
