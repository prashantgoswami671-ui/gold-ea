//+------------------------------------------------------------------+
//|                                                   GoldEALog.mqh |
//|                          Gold EA Project - Phase 1 Logging       |
//|                                                                  |
//|  Shared, structured logging for the execution and risk engine.   |
//|  Logging never changes trading behavior.                         |
//+------------------------------------------------------------------+
#ifndef GEA_LOG_MQH
#define GEA_LOG_MQH

const string GEA_LOG_PREFIX = "[GoldEA]";

//+------------------------------------------------------------------+
//| Basic log levels                                                 |
//+------------------------------------------------------------------+
void GEA_LogInfo(const string message)
{
   Print(GEA_LOG_PREFIX, "[INFO ] ", message);
}

void GEA_LogWarn(const string message)
{
   Print(GEA_LOG_PREFIX, "[WARN ] ", message);
}

void GEA_LogError(const string message)
{
   Print(GEA_LOG_PREFIX, "[ERROR] ", message);
}

void GEA_LogPass(const string check, const string detail)
{
   Print(GEA_LOG_PREFIX, "[PASS ] ", check, " | ", detail);
}

void GEA_LogFail(const string check, const string detail)
{
   Print(GEA_LOG_PREFIX, "[FAIL ] ", check, " | ", detail);
}

void GEA_LogSection(const string title)
{
   Print("");
   Print(GEA_LOG_PREFIX, " ----- ", title, " -----");
}

//+------------------------------------------------------------------+
//| Formatting helpers                                               |
//+------------------------------------------------------------------+
string GEA_BoolText(const bool value)
{
   return(value ? "true" : "false");
}

string GEA_YesNo(const bool value)
{
   return(value ? "Yes" : "No");
}

string GEA_PriceText(const double price, const int digits)
{
   return(DoubleToString(price, digits));
}

string GEA_VolumeText(const double volume)
{
   return(DoubleToString(volume, 3));
}

string GEA_PointsText(const double points)
{
   return(DoubleToString(points, 1));
}

string GEA_PercentText(const double value)
{
   return(DoubleToString(value, 2) + "%");
}

string GEA_AppendReason(const string existing, const string reason)
{
   if(existing == "")
      return(reason);
   if(reason == "")
      return(existing);
   return(existing + "; " + reason);
}

//+------------------------------------------------------------------+
//| Broker return-code descriptions                                  |
//+------------------------------------------------------------------+
string GEA_RetcodeText(const long retcode)
{
   switch((uint)retcode)
     {
      case TRADE_RETCODE_REQUOTE:            return("Requote");
      case TRADE_RETCODE_REJECT:             return("Request rejected");
      case TRADE_RETCODE_CANCEL:             return("Request cancelled by trader");
      case TRADE_RETCODE_PLACED:             return("Order placed");
      case TRADE_RETCODE_DONE:               return("Done");
      case TRADE_RETCODE_DONE_PARTIAL:       return("Done partially");
      case TRADE_RETCODE_ERROR:              return("Request processing error");
      case TRADE_RETCODE_TIMEOUT:            return("Request timeout");
      case TRADE_RETCODE_INVALID:            return("Invalid request");
      case TRADE_RETCODE_INVALID_VOLUME:     return("Invalid volume");
      case TRADE_RETCODE_INVALID_PRICE:      return("Invalid price");
      case TRADE_RETCODE_INVALID_STOPS:      return("Invalid stops");
      case TRADE_RETCODE_TRADE_DISABLED:     return("Trading disabled");
      case TRADE_RETCODE_MARKET_CLOSED:      return("Market closed");
      case TRADE_RETCODE_NO_MONEY:           return("Insufficient money");
      case TRADE_RETCODE_PRICE_CHANGED:      return("Price changed");
      case TRADE_RETCODE_PRICE_OFF:          return("No quotes to process request");
      case TRADE_RETCODE_INVALID_EXPIRATION: return("Invalid expiration");
      case TRADE_RETCODE_ORDER_CHANGED:      return("Order state changed");
      case TRADE_RETCODE_TOO_MANY_REQUESTS:  return("Too many requests");
      case TRADE_RETCODE_NO_CHANGES:         return("No changes in request");
      case TRADE_RETCODE_SERVER_DISABLES_AT: return("Server disabled at");
      case TRADE_RETCODE_CLIENT_DISABLES_AT: return("Client disabled at");
      case TRADE_RETCODE_LOCKED:             return("Request locked for processing");
      case TRADE_RETCODE_FROZEN:             return("Order or position frozen");
      case TRADE_RETCODE_INVALID_FILL:       return("Unsupported filling mode");
      case TRADE_RETCODE_CONNECTION:         return("No connection with trade server");
      case TRADE_RETCODE_ONLY_REAL:          return("Operation allowed only for live accounts");
      case TRADE_RETCODE_LIMIT_ORDERS:       return("Order limit reached");
      case TRADE_RETCODE_LIMIT_VOLUME:       return("Volume limit reached");
      case TRADE_RETCODE_INVALID_ORDER:      return("Invalid or prohibited order type");
      case TRADE_RETCODE_POSITION_CLOSED:    return("Position already closed");
      case TRADE_RETCODE_INVALID_CLOSE_VOLUME: return("Invalid close volume");
      case TRADE_RETCODE_CLOSE_ORDER_EXIST:  return("Close order already exists");
      case TRADE_RETCODE_LIMIT_POSITIONS:    return("Position limit reached");
      case TRADE_RETCODE_REJECT_CANCEL:      return("Request rejected and cancelled");
      case TRADE_RETCODE_LONG_ONLY:          return("Only long positions allowed");
      case TRADE_RETCODE_SHORT_ONLY:         return("Only short positions allowed");
      case TRADE_RETCODE_CLOSE_ONLY:         return("Only position closing allowed");
      case TRADE_RETCODE_FIFO_CLOSE:         return("FIFO close required");
      case TRADE_RETCODE_HEDGE_PROHIBITED:   return("Hedging prohibited");
     }
   return("Unknown retcode " + IntegerToString(retcode));
}

//+------------------------------------------------------------------+
//| Filling mode helpers                                             |
//+------------------------------------------------------------------+
string GEA_FillingFlagsText(const long flags)
{
   string result = "";
   if(((long)flags & (long)SYMBOL_FILLING_FOK) != 0)
      result = GEA_AppendReason(result, "FOK");
   if(((long)flags & (long)SYMBOL_FILLING_IOC) != 0)
      result = GEA_AppendReason(result, "IOC");
   if(((long)flags & (long)SYMBOL_FILLING_BOC) != 0)
      result = GEA_AppendReason(result, "BOC");
   if(result == "")
      result = "None/unspecified";
   return(result + " (mask " + IntegerToString(flags) + ")");
}

string GEA_OrderFillingText(const long filling)
{
   switch((ENUM_ORDER_TYPE_FILLING)filling)
     {
      case ORDER_FILLING_FOK:    return("FOK");
      case ORDER_FILLING_IOC:    return("IOC");
      case ORDER_FILLING_BOC:    return("BOC");
      case ORDER_FILLING_RETURN: return("RETURN");
     }
   return("Unknown (" + IntegerToString(filling) + ")");
}

#endif // GEA_LOG_MQH
//+------------------------------------------------------------------+
