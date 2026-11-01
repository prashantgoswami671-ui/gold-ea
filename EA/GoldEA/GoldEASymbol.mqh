//+------------------------------------------------------------------+
//|                                               GoldEASymbol.mqh |
//|                          Gold EA Project - Phase 1 Symbol Layer  |
//|                                                                  |
//|  Reads every broker symbol property dynamically. No Exness       |
//|  XAUUSD value is hardcoded.                                      |
//+------------------------------------------------------------------+
#ifndef GEA_SYMBOL_MQH
#define GEA_SYMBOL_MQH

#include "GoldEALog.mqh"

//+------------------------------------------------------------------+
//| Broker symbol specification                                      |
//+------------------------------------------------------------------+
struct GoldEASymbolSpec
{
   string symbol;
   bool   valid;
   int    digits;
   double point;
   double tickSize;
   double tickValue;
   double tickValueProfit;
   double tickValueLoss;
   double contractSize;
   double volumeMin;
   double volumeMax;
   double volumeStep;
   double volumeLimit;
   long   stopsLevelPoints;
   long   freezeLevelPoints;
   long   tradeMode;
   long   fillingFlags;
   long   selectedFilling;
   long   executionMode;
   string loadError;
};

//--- Single process-wide symbol specification ----------------------
GoldEASymbolSpec g_symbolSpec;

//+------------------------------------------------------------------+
//| Market snapshot                                                  |
//+------------------------------------------------------------------+
struct GoldEAMarketSnapshot
{
   bool     valid;
   double   bid;
   double   ask;
   double   point;
   double   spreadPrice;
   double   spreadPoints;
   datetime tickTime;
   string   error;
};

//+------------------------------------------------------------------+
//| Enum text helpers                                                |
//+------------------------------------------------------------------+
string GEA_SymbolTradeModeText(const long mode)
{
   switch((ENUM_SYMBOL_TRADE_MODE)mode)
     {
      case SYMBOL_TRADE_MODE_DISABLED:  return("Disabled");
      case SYMBOL_TRADE_MODE_LONGONLY:  return("Long only");
      case SYMBOL_TRADE_MODE_SHORTONLY: return("Short only");
      case SYMBOL_TRADE_MODE_CLOSEONLY: return("Close only");
      case SYMBOL_TRADE_MODE_FULL:      return("Full");
     }
   return("Unknown (" + IntegerToString(mode) + ")");
}

string GEA_ExecutionModeText(const long mode)
{
   switch((ENUM_SYMBOL_TRADE_EXECUTION)mode)
     {
      case SYMBOL_TRADE_EXECUTION_REQUEST:  return("Request");
      case SYMBOL_TRADE_EXECUTION_INSTANT:  return("Instant");
      case SYMBOL_TRADE_EXECUTION_MARKET:   return("Market");
      case SYMBOL_TRADE_EXECUTION_EXCHANGE: return("Exchange");
     }
   return("Unknown (" + IntegerToString(mode) + ")");
}

//+------------------------------------------------------------------+
//| Pick a filling mode supported by the broker for MARKET orders    |
//|                                                                  |
//|  BOC (Book or Cancel) is only valid for limit orders, so it must  |
//|  never be selected for TRADE_ACTION_DEAL. If the broker reports   |
//|  neither FOK nor IOC, fall back to RETURN.                        |
//+------------------------------------------------------------------+
long GEA_SelectFillingMode(const long flags)
{
   if(((long)flags & (long)SYMBOL_FILLING_FOK) != 0)
      return((long)ORDER_FILLING_FOK);
   if(((long)flags & (long)SYMBOL_FILLING_IOC) != 0)
      return((long)ORDER_FILLING_IOC);
   return((long)ORDER_FILLING_RETURN);
}

//+------------------------------------------------------------------+
//| Load the symbol specification from the broker                    |
//+------------------------------------------------------------------+
bool GEA_LoadSymbolSpec(const string symbol, GoldEASymbolSpec &spec)
{
   GoldEASymbolSpec temp;
   temp.symbol           = symbol;
   temp.valid            = false;
   temp.digits           = 0;
   temp.point            = 0.0;
   temp.tickSize         = 0.0;
   temp.tickValue        = 0.0;
   temp.tickValueProfit  = 0.0;
   temp.tickValueLoss    = 0.0;
   temp.contractSize     = 0.0;
   temp.volumeMin        = 0.0;
   temp.volumeMax        = 0.0;
   temp.volumeStep       = 0.0;
   temp.volumeLimit      = 0.0;
   temp.stopsLevelPoints = 0;
   temp.freezeLevelPoints = 0;
   temp.tradeMode        = 0;
   temp.fillingFlags     = 0;
   temp.selectedFilling  = (long)ORDER_FILLING_RETURN;
   temp.executionMode    = 0;
   temp.loadError        = "";

   if(symbol == "")
     {
      temp.loadError = "empty symbol name";
      spec = temp;
      return(false);
     }

   if(SymbolInfoInteger(symbol, SYMBOL_EXIST) == 0)
     {
      temp.loadError = "symbol does not exist in this terminal";
      spec = temp;
      return(false);
     }

   if(!SymbolSelect(symbol, true))
     {
      temp.loadError = "SymbolSelect failed, error " + IntegerToString(GetLastError());
      spec = temp;
      return(false);
     }

   long   digits           = 0;
   long   stopsLevel        = 0;
   long   freezeLevel       = 0;
   long   tradeMode         = 0;
   long   fillingFlags      = 0;
   long   executionMode     = 0;
   double point            = 0.0;
   double tickSize         = 0.0;
   double tickValue        = 0.0;
   double tickValueProfit  = 0.0;
   double tickValueLoss    = 0.0;
   double contractSize     = 0.0;
   double volumeMin        = 0.0;
   double volumeMax        = 0.0;
   double volumeStep       = 0.0;
   double volumeLimit      = 0.0;

   if(!SymbolInfoInteger(symbol, SYMBOL_DIGITS, digits) ||
      !SymbolInfoInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL, stopsLevel) ||
      !SymbolInfoInteger(symbol, SYMBOL_TRADE_FREEZE_LEVEL, freezeLevel) ||
      !SymbolInfoInteger(symbol, SYMBOL_TRADE_MODE, tradeMode) ||
      !SymbolInfoInteger(symbol, SYMBOL_FILLING_MODE, fillingFlags) ||
      !SymbolInfoInteger(symbol, SYMBOL_TRADE_EXEMODE, executionMode))
     {
      temp.loadError = "failed to read integer symbol properties";
      spec = temp;
      return(false);
     }

   if(!SymbolInfoDouble(symbol, SYMBOL_POINT, point) ||
      !SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE, tickSize) ||
      !SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE, tickValue) ||
      !SymbolInfoDouble(symbol, SYMBOL_TRADE_CONTRACT_SIZE, contractSize) ||
      !SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN, volumeMin) ||
      !SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX, volumeMax) ||
      !SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP, volumeStep) ||
      !SymbolInfoDouble(symbol, SYMBOL_VOLUME_LIMIT, volumeLimit))
     {
      temp.loadError = "failed to read double symbol properties";
      spec = temp;
      return(false);
     }

   //--- Profit/loss tick values are useful but not fatal if unavailable.
   if(!SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE_PROFIT, tickValueProfit))
      tickValueProfit = 0.0;
   if(!SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE_LOSS, tickValueLoss))
      tickValueLoss = 0.0;

   temp.digits           = (int)digits;
   temp.point            = point;
   temp.tickSize         = tickSize;
   temp.tickValue        = tickValue;
   temp.tickValueProfit  = tickValueProfit;
   temp.tickValueLoss    = tickValueLoss;
   temp.contractSize     = contractSize;
   temp.volumeMin        = volumeMin;
   temp.volumeMax        = volumeMax;
   temp.volumeStep       = volumeStep;
   temp.volumeLimit      = volumeLimit;
   temp.stopsLevelPoints = stopsLevel;
   temp.freezeLevelPoints = freezeLevel;
   temp.tradeMode        = tradeMode;
   temp.fillingFlags     = fillingFlags;
   temp.selectedFilling  = GEA_SelectFillingMode(fillingFlags);
   temp.executionMode    = executionMode;

   if(point <= 0.0)
     {
      temp.loadError = "invalid Point (must be > 0)";
      spec = temp;
      return(false);
     }
   if(temp.digits < 0 || temp.digits > 8)
     {
      temp.loadError = "invalid Digits";
      spec = temp;
      return(false);
     }
   if(tickSize <= 0.0)
     {
      temp.loadError = "invalid tick size (must be > 0)";
      spec = temp;
      return(false);
     }
   if(contractSize <= 0.0)
     {
      temp.loadError = "invalid contract size (must be > 0)";
      spec = temp;
      return(false);
     }
   if(volumeStep <= 0.0)
     {
      temp.loadError = "invalid volume step (must be > 0)";
      spec = temp;
      return(false);
     }
   if(volumeMin <= 0.0)
     {
      temp.loadError = "invalid minimum volume (must be > 0)";
      spec = temp;
      return(false);
     }
   if(volumeMax < volumeMin)
     {
      temp.loadError = "maximum volume is below minimum volume";
      spec = temp;
      return(false);
     }

   temp.valid = true;
   spec = temp;
   return(true);
}

//+------------------------------------------------------------------+
//| Log the loaded specification                                     |
//+------------------------------------------------------------------+
void GEA_LogSymbolSpec(const GoldEASymbolSpec &spec)
{
   GEA_LogSection("BROKER SYMBOL SPECIFICATION (DYNAMIC)");
   GEA_LogInfo("Symbol                 : " + spec.symbol);
   GEA_LogInfo("Specification valid    : " + GEA_YesNo(spec.valid));
   if(!spec.valid)
     {
      GEA_LogError("Symbol specification load error: " + spec.loadError);
      return;
     }
   GEA_LogInfo("Digits                 : " + IntegerToString(spec.digits));
   GEA_LogInfo("Point                  : " + DoubleToString(spec.point, 10));
   GEA_LogInfo("Tick size              : " + DoubleToString(spec.tickSize, 10));
   GEA_LogInfo("Tick value             : " + DoubleToString(spec.tickValue, 5));
   GEA_LogInfo("Tick value (profit)    : " + DoubleToString(spec.tickValueProfit, 5));
   GEA_LogInfo("Tick value (loss)      : " + DoubleToString(spec.tickValueLoss, 5));
   GEA_LogInfo("Contract size          : " + DoubleToString(spec.contractSize, 2));
   GEA_LogInfo("Volume minimum         : " + GEA_VolumeText(spec.volumeMin));
   GEA_LogInfo("Volume maximum         : " + GEA_VolumeText(spec.volumeMax));
   GEA_LogInfo("Volume step            : " + GEA_VolumeText(spec.volumeStep));
   GEA_LogInfo("Volume limit           : " + (spec.volumeLimit > 0.0 ? GEA_VolumeText(spec.volumeLimit) : "not specified"));
   GEA_LogInfo("Stops level (points)   : " + IntegerToString(spec.stopsLevelPoints));
   GEA_LogInfo("Freeze level (points)  : " + IntegerToString(spec.freezeLevelPoints));
   GEA_LogInfo("Trade mode             : " + GEA_SymbolTradeModeText(spec.tradeMode));
   GEA_LogInfo("Execution mode         : " + GEA_ExecutionModeText(spec.executionMode));
   GEA_LogInfo("Filling flags          : " + GEA_FillingFlagsText(spec.fillingFlags));
   GEA_LogInfo("Selected filling mode  : " + GEA_OrderFillingText(spec.selectedFilling));

   if(spec.fillingFlags == 0)
      GEA_LogWarn("Broker reported no filling-mode flags. ORDER_FILLING_RETURN is the fallback; verify before live use.");

   if(spec.tickValue <= 0.0)
      GEA_LogWarn("Tick value is not currently available. It can be zero outside market hours.");
   if(spec.tradeMode != SYMBOL_TRADE_MODE_FULL)
      GEA_LogWarn("Symbol trade mode is not FULL. New entries may be restricted.");
}

//+------------------------------------------------------------------+
//| Decimal precision implied by the broker volume step              |
//+------------------------------------------------------------------+
int GEA_VolumeDigits(const double step)
{
   if(step <= 0.0)
      return(3);
   for(int digits = 0; digits <= 8; digits++)
     {
      double scaled = step * MathPow(10.0, (double)digits);
      if(MathAbs(scaled - MathRound(scaled)) < 1e-8)
         return(digits);
     }
   return(8);
}

//+------------------------------------------------------------------+
//| Normalise a price to the broker tick size and symbol digits      |
//+------------------------------------------------------------------+
double GEA_NormalizePrice(const GoldEASymbolSpec &spec, const double price)
{
   if(!spec.valid || !MathIsValidNumber(price))
      return(price);

   double tick = (spec.tickSize > 0.0) ? spec.tickSize : spec.point;
   if(tick <= 0.0)
      return(NormalizeDouble(price, spec.digits));

   double ticks = MathRound(price / tick);
   return(NormalizeDouble(ticks * tick, spec.digits));
}

//+------------------------------------------------------------------+
//| Normalise and validate a requested volume                        |
//|                                                                  |
//|  - never rounds exposure upward                                  |
//|  - rejects values below minimum or above maximum                 |
//|  - rejects NaN / infinity / non-positive values                  |
//+------------------------------------------------------------------+
bool GEA_NormalizeVolume(const GoldEASymbolSpec &spec,
                         const double requested,
                         double &normalized,
                         string &reason)
{
   normalized = 0.0;
   reason = "";

   if(!spec.valid)
     {
      reason = "symbol specification is not valid";
      return(false);
     }
   if(!MathIsValidNumber(requested) || requested <= 0.0)
     {
      reason = "volume must be a finite value greater than zero";
      return(false);
     }
   if(!MathIsValidNumber(spec.volumeStep) || spec.volumeStep <= 0.0)
     {
      reason = "broker volume step is invalid";
      return(false);
     }

   double tolerance = MathMax(spec.volumeStep * 1e-7, 1e-9);

   if(requested < spec.volumeMin - tolerance)
     {
      reason = "requested volume " + GEA_VolumeText(requested) +
               " is below broker minimum " + GEA_VolumeText(spec.volumeMin);
      return(false);
     }
   if(requested > spec.volumeMax + tolerance)
     {
      reason = "requested volume " + GEA_VolumeText(requested) +
               " is above broker maximum " + GEA_VolumeText(spec.volumeMax);
      return(false);
     }
   if(spec.volumeLimit > 0.0 && requested > spec.volumeLimit + tolerance)
     {
      reason = "requested volume " + GEA_VolumeText(requested) +
               " is above broker volume limit " + GEA_VolumeText(spec.volumeLimit);
      return(false);
     }

   int volumeDigits = GEA_VolumeDigits(spec.volumeStep);
   double steps = MathFloor((requested + tolerance) / spec.volumeStep);
   double candidate = NormalizeDouble(steps * spec.volumeStep, volumeDigits);

   if(candidate < spec.volumeMin - tolerance)
     {
      reason = "volume " + GEA_VolumeText(requested) + " normalises to " +
               GEA_VolumeText(candidate) + ", below broker minimum " +
               GEA_VolumeText(spec.volumeMin);
      return(false);
     }
   if(candidate > spec.volumeMax + tolerance)
     {
      reason = "normalised volume " + GEA_VolumeText(candidate) +
               " exceeds broker maximum " + GEA_VolumeText(spec.volumeMax);
      return(false);
     }
   if(spec.volumeLimit > 0.0 && candidate > spec.volumeLimit + tolerance)
     {
      reason = "normalised volume " + GEA_VolumeText(candidate) +
               " exceeds broker volume limit " + GEA_VolumeText(spec.volumeLimit);
      return(false);
     }
   if(candidate <= 0.0)
     {
      reason = "normalised volume is zero";
      return(false);
     }

   normalized = candidate;
   return(true);
}

//+------------------------------------------------------------------+
//| Read the current quote                                           |
//+------------------------------------------------------------------+
bool GEA_GetMarketSnapshot(const GoldEASymbolSpec &spec, GoldEAMarketSnapshot &snapshot)
{
   snapshot.valid        = false;
   snapshot.bid          = 0.0;
   snapshot.ask          = 0.0;
   snapshot.point        = spec.point;
   snapshot.spreadPrice  = 0.0;
   snapshot.spreadPoints = 0.0;
   snapshot.tickTime     = 0;
   snapshot.error        = "";

   if(!spec.valid)
     {
      snapshot.error = "symbol specification is not valid";
      return(false);
     }

   MqlTick tick;
   bool haveTick = SymbolInfoTick(spec.symbol, tick);

   if(haveTick && tick.bid > 0.0 && tick.ask > 0.0)
     {
      snapshot.bid      = tick.bid;
      snapshot.ask      = tick.ask;
      snapshot.tickTime = tick.time;
     }
   else
     {
      snapshot.bid = SymbolInfoDouble(spec.symbol, SYMBOL_BID);
      snapshot.ask = SymbolInfoDouble(spec.symbol, SYMBOL_ASK);
     }

   if(snapshot.bid <= 0.0 || snapshot.ask <= 0.0)
     {
      snapshot.error = "no valid Bid/Ask quote is currently available";
      return(false);
     }
   if(snapshot.ask < snapshot.bid)
     {
      snapshot.error = "invalid crossed quote: Ask is below Bid";
      return(false);
     }
   if(snapshot.point <= 0.0)
     {
      snapshot.error = "symbol point is invalid";
      return(false);
     }

   snapshot.spreadPrice  = snapshot.ask - snapshot.bid;
   snapshot.spreadPoints = snapshot.spreadPrice / snapshot.point;
   snapshot.valid        = true;
   return(true);
}

void GEA_LogMarketSnapshot(const GoldEAMarketSnapshot &snapshot, const int digits)
{
   if(!snapshot.valid)
     {
      GEA_LogWarn("Market snapshot unavailable: " + snapshot.error);
      return;
     }
   GEA_LogInfo("Quote                  : Bid " + GEA_PriceText(snapshot.bid, digits) +
               " / Ask " + GEA_PriceText(snapshot.ask, digits) +
               " | spread " + GEA_PointsText(snapshot.spreadPoints) + " points");
   if(snapshot.tickTime > 0)
      GEA_LogInfo("Last tick time         : " + TimeToString(snapshot.tickTime, TIME_DATE | TIME_SECONDS));
}

//+------------------------------------------------------------------+
//| Spread protection                                                |
//|                                                                  |
//|  The maximum is always supplied by configuration. This function  |
//|  contains no assumption about a "normal" Gold spread.            |
//+------------------------------------------------------------------+
bool GEA_EvaluateSpread(const double bid,
                        const double ask,
                        const double point,
                        const int maxSpreadPoints,
                        double &spreadPoints,
                        string &reason)
{
   spreadPoints = 0.0;
   reason = "";

   if(!MathIsValidNumber(bid) || !MathIsValidNumber(ask) || bid <= 0.0 || ask <= 0.0)
     {
      reason = "no valid Bid/Ask quote is available";
      return(false);
     }
   if(!MathIsValidNumber(point) || point <= 0.0)
     {
      reason = "symbol point is invalid";
      return(false);
     }
   if(ask < bid)
     {
      reason = "invalid crossed quote: Ask is below Bid";
      return(false);
     }
   if(maxSpreadPoints <= 0)
     {
      reason = "maximum spread is not configured";
      return(false);
     }

   spreadPoints = (ask - bid) / point;
   if(spreadPoints > (double)maxSpreadPoints + 1e-6)
     {
      reason = "spread " + GEA_PointsText(spreadPoints) + " points exceeds configured maximum " +
               IntegerToString(maxSpreadPoints) + " points";
      return(false);
     }

   return(true);
}

#endif // GEA_SYMBOL_MQH
//+------------------------------------------------------------------+
