//+------------------------------------------------------------------+
//|                                              GoldEAPhase0.mqh |
//|                          Gold EA Project - Phase 0 Diagnostics   |
//|                                                                  |
//|  Phase 0 environment reporting is preserved. It is diagnostic     |
//|  only and never sends orders.                                    |
//+------------------------------------------------------------------+
#ifndef GEA_PHASE0_MQH
#define GEA_PHASE0_MQH

#include "GoldEALog.mqh"
#include "GoldEAConfig.mqh"
#include "GoldEASafety.mqh"

//+------------------------------------------------------------------+
//| Small formatting helpers                                         |
//+------------------------------------------------------------------+
string YesNo(const bool value)
{
   return(value ? "Yes" : "No");
}

string Unavailable()
{
   return("<unavailable>");
}

string AddItem(const string current, const string item)
{
   if(current == "")
      return(item);
   return(current + ", " + item);
}

string WithUnit(const string value, const string unit)
{
   if(value == Unavailable())
      return(value);
   return(value + unit);
}

string PadRight(const string text, const int width)
{
   string result = text;
   int length = StringLen(result);
   while(length < width)
     {
      result += " ";
      length++;
     }
   return(result);
}

void PrintField(const string label, const string value)
{
   Print(PadRight(label, 30), ": ", value);
}

void PrintSection(const string title)
{
   Print("");
   Print(GEA_SEPARATOR);
   Print(title);
   Print(GEA_SEPARATOR);
}

//+------------------------------------------------------------------+
//| Safe property readers                                            |
//+------------------------------------------------------------------+
string SymbolString(const string symbol, const ENUM_SYMBOL_INFO_STRING property)
{
   string value = SymbolInfoString(symbol, property);
   if(value == "")
      return(Unavailable());
   return(value);
}

string SymbolInteger(const string symbol, const ENUM_SYMBOL_INFO_INTEGER property)
{
   long value = 0;
   if(!SymbolInfoInteger(symbol, property, value))
      return(Unavailable());
   return(IntegerToString(value));
}

string SymbolDouble(const string symbol, const ENUM_SYMBOL_INFO_DOUBLE property, const int digits)
{
   double value = 0.0;
   if(!SymbolInfoDouble(symbol, property, value))
      return(Unavailable());
   return(DoubleToString(value, digits));
}

string AccountString(const ENUM_ACCOUNT_INFO_STRING property)
{
   string value = AccountInfoString(property);
   if(value == "")
      return(Unavailable());
   return(value);
}

string AccountDouble(const ENUM_ACCOUNT_INFO_DOUBLE property, const int digits)
{
   return(DoubleToString(AccountInfoDouble(property), digits));
}

string Money(const ENUM_ACCOUNT_INFO_DOUBLE property, const string currency, const int digits)
{
   return(DoubleToString(AccountInfoDouble(property), digits) + " " + currency);
}

//+------------------------------------------------------------------+
//| Gold symbol verification                                         |
//|                                                                  |
//| Diagnostic only. This does not affect any trading behavior.      |
//| Supports broker-specific Gold naming by looking for XAU or GOLD  |
//| in the symbol name, description and symbol path.                 |
//+------------------------------------------------------------------+
string GoldSymbolCheck(const string symbol, string &basis)
{
   string name = symbol;
   StringToUpper(name);
   if(StringFind(name, "XAU") >= 0)
     {
      basis = "XAU token in symbol name";
      return("PASS");
     }
   if(StringFind(name, "GOLD") >= 0)
     {
      basis = "GOLD token in symbol name";
      return("PASS");
     }

   string description = SymbolInfoString(symbol, SYMBOL_DESCRIPTION);
   StringToUpper(description);
   if(StringFind(description, "XAU") >= 0)
     {
      basis = "XAU token in symbol description";
      return("PASS");
     }
   if(StringFind(description, "GOLD") >= 0)
     {
      basis = "GOLD token in symbol description";
      return("PASS");
     }

   string path = SymbolInfoString(symbol, SYMBOL_PATH);
   StringToUpper(path);
   if(StringFind(path, "XAU") >= 0)
     {
      basis = "XAU token in symbol path";
      return("PASS");
     }
   if(StringFind(path, "GOLD") >= 0)
     {
      basis = "GOLD token in symbol path";
      return("PASS");
     }

   basis = "no XAU/GOLD token found in symbol name, description or path";
   return("WARNING - attached symbol does not appear to be Gold/XAU");
}

//+------------------------------------------------------------------+
//| Enum to readable text helpers                                    |
//+------------------------------------------------------------------+
string AccountTradeModeText(const long mode)
{
   switch((ENUM_ACCOUNT_TRADE_MODE)mode)
     {
      case ACCOUNT_TRADE_MODE_DEMO:    return("Demo");
      case ACCOUNT_TRADE_MODE_CONTEST: return("Contest");
      case ACCOUNT_TRADE_MODE_REAL:    return("Real");
     }
   return("Unknown (" + IntegerToString(mode) + ")");
}

string AccountMarginModeText(const long mode)
{
   switch((ENUM_ACCOUNT_MARGIN_MODE)mode)
     {
      case ACCOUNT_MARGIN_MODE_RETAIL_NETTING: return("Retail netting");
      case ACCOUNT_MARGIN_MODE_EXCHANGE:       return("Exchange netting");
      case ACCOUNT_MARGIN_MODE_RETAIL_HEDGING: return("Retail hedging");
     }
   return("Unknown (" + IntegerToString(mode) + ")");
}

string PositionAccountingText(const long mode)
{
   if(mode == ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
      return("Hedging");
   if(mode == ACCOUNT_MARGIN_MODE_RETAIL_NETTING || mode == ACCOUNT_MARGIN_MODE_EXCHANGE)
      return("Netting");
   return("Unknown (" + IntegerToString(mode) + ")");
}

string StopOutModeText(const long mode)
{
   if(mode == ACCOUNT_STOPOUT_MODE_PERCENT)
      return("Percent");
   if(mode == ACCOUNT_STOPOUT_MODE_MONEY)
      return("Money");
   return("Unknown (" + IntegerToString(mode) + ")");
}

string SymbolTradeModeText(const long mode)
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

string SymbolExecutionModeText(const long mode)
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

string SymbolCalcModeText(const long mode)
{
   switch((ENUM_SYMBOL_CALC_MODE)mode)
     {
      case SYMBOL_CALC_MODE_FOREX:               return("Forex");
      case SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE:   return("Forex no leverage");
      case SYMBOL_CALC_MODE_FUTURES:             return("Futures");
      case SYMBOL_CALC_MODE_CFD:                 return("CFD");
      case SYMBOL_CALC_MODE_CFDINDEX:            return("CFD index");
      case SYMBOL_CALC_MODE_CFDLEVERAGE:         return("CFD leverage");
      case SYMBOL_CALC_MODE_EXCH_STOCKS:         return("Exchange stocks");
      case SYMBOL_CALC_MODE_EXCH_FUTURES:        return("Exchange futures");
      case SYMBOL_CALC_MODE_EXCH_FUTURES_FORTS:  return("Exchange futures FORTS");
      case SYMBOL_CALC_MODE_EXCH_BONDS:          return("Exchange bonds");
      case SYMBOL_CALC_MODE_EXCH_STOCKS_MOEX:    return("Exchange stocks MOEX");
      case SYMBOL_CALC_MODE_EXCH_BONDS_MOEX:     return("Exchange bonds MOEX");
      case SYMBOL_CALC_MODE_SERV_COLLATERAL:     return("Collateral");
     }
   return("Unknown (" + IntegerToString(mode) + ")");
}

string SymbolSwapModeText(const long mode)
{
   switch((ENUM_SYMBOL_SWAP_MODE)mode)
     {
      case SYMBOL_SWAP_MODE_DISABLED:          return("Disabled");
      case SYMBOL_SWAP_MODE_POINTS:            return("Points");
      case SYMBOL_SWAP_MODE_CURRENCY_SYMBOL:   return("Symbol base currency");
      case SYMBOL_SWAP_MODE_CURRENCY_MARGIN:   return("Margin currency");
      case SYMBOL_SWAP_MODE_CURRENCY_DEPOSIT:  return("Deposit currency");
      case SYMBOL_SWAP_MODE_CURRENCY_PROFIT:   return("Profit currency");
      case SYMBOL_SWAP_MODE_INTEREST_CURRENT:  return("Interest (current price)");
      case SYMBOL_SWAP_MODE_INTEREST_OPEN:     return("Interest (open price)");
      case SYMBOL_SWAP_MODE_REOPEN_CURRENT:    return("Reopen (current price)");
      case SYMBOL_SWAP_MODE_REOPEN_BID:        return("Reopen (Bid price)");
     }
   return("Unknown (" + IntegerToString(mode) + ")");
}

string DayOfWeekText(const long day)
{
   switch((ENUM_DAY_OF_WEEK)day)
     {
      case SUNDAY:    return("Sunday");
      case MONDAY:    return("Monday");
      case TUESDAY:   return("Tuesday");
      case WEDNESDAY: return("Wednesday");
      case THURSDAY:  return("Thursday");
      case FRIDAY:    return("Friday");
      case SATURDAY:  return("Saturday");
     }
   return("Unknown (" + IntegerToString(day) + ")");
}

string SymbolFillingModeText(const long flags)
{
   string result = "";
   if(((int)flags & (int)SYMBOL_FILLING_FOK) != 0)
      result = AddItem(result, "FOK");
   if(((int)flags & (int)SYMBOL_FILLING_IOC) != 0)
      result = AddItem(result, "IOC");
   if(((int)flags & (int)SYMBOL_FILLING_BOC) != 0)
      result = AddItem(result, "BOC");
   if(result == "")
      result = "None/unknown";
   return(result + " (mask " + IntegerToString(flags) + ")");
}

string SymbolOrderModeText(const long flags)
{
   string result = "";
   if(((int)flags & (int)SYMBOL_ORDER_MARKET) != 0)
      result = AddItem(result, "Market");
   if(((int)flags & (int)SYMBOL_ORDER_LIMIT) != 0)
      result = AddItem(result, "Limit");
   if(((int)flags & (int)SYMBOL_ORDER_STOP) != 0)
      result = AddItem(result, "Stop");
   if(((int)flags & (int)SYMBOL_ORDER_STOP_LIMIT) != 0)
      result = AddItem(result, "Stop limit");
   if(((int)flags & (int)SYMBOL_ORDER_SL) != 0)
      result = AddItem(result, "Stop loss");
   if(((int)flags & (int)SYMBOL_ORDER_TP) != 0)
      result = AddItem(result, "Take profit");
   if(((int)flags & (int)SYMBOL_ORDER_CLOSEBY) != 0)
      result = AddItem(result, "Close by");
   if(result == "")
      result = "None/unknown";
   return(result + " (mask " + IntegerToString(flags) + ")");
}

string DeinitReasonText(const int reason)
{
   switch(reason)
     {
      case REASON_PROGRAM:     return("Program terminated");
      case REASON_REMOVE:      return("EA removed from chart");
      case REASON_RECOMPILE:   return("Program recompiled");
      case REASON_CHARTCHANGE: return("Symbol or timeframe changed");
      case REASON_CHARTCLOSE:  return("Chart closed");
      case REASON_PARAMETERS:  return("Input parameters changed");
      case REASON_ACCOUNT:     return("Account changed");
      case REASON_TEMPLATE:    return("Template applied");
      case REASON_INITFAILED:  return("OnInit failed");
      case REASON_CLOSE:       return("Terminal closed");
     }
   return("Unknown (" + IntegerToString(reason) + ")");
}

//+------------------------------------------------------------------+
//| Report sections                                                  |
//+------------------------------------------------------------------+
void ReportHeader()
{
   Print(GEA_SEPARATOR);
   Print(" GoldEA v" + GEA_VERSION + " - Phase 0 Environment Diagnostics");
   Print(" Phase 1 Execution & Risk Engine attached. Diagnostic mode.");
   Print(GEA_SEPARATOR);
   PrintField("Report time (local)", TimeToString(TimeLocal(), TIME_DATE | TIME_SECONDS));
   PrintField("Report time (server)", TimeToString(TimeTradeServer(), TIME_DATE | TIME_SECONDS));
}

void ReportSymbol(const string symbol)
{
   long digits = 0;
   SymbolInfoInteger(symbol, SYMBOL_DIGITS, digits);
   int priceDigits = (int)digits;
   if(priceDigits < 0)
      priceDigits = 0;

   PrintSection("SYMBOL INFORMATION");
   PrintField("Attached symbol", symbol);

   string goldBasis = "";
   string goldCheck = GoldSymbolCheck(symbol, goldBasis);
   Print("Gold symbol check: ", goldCheck);
   Print("Gold detection basis: ", goldBasis);
   Print("");

   PrintField("Description", SymbolString(symbol, SYMBOL_DESCRIPTION));
   PrintField("Symbol path", SymbolString(symbol, SYMBOL_PATH));
   PrintField("Base currency", SymbolString(symbol, SYMBOL_CURRENCY_BASE));
   PrintField("Profit currency", SymbolString(symbol, SYMBOL_CURRENCY_PROFIT));
   PrintField("Margin currency", SymbolString(symbol, SYMBOL_CURRENCY_MARGIN));
   PrintField("Digits", IntegerToString(digits));
   PrintField("Point size", SymbolDouble(symbol, SYMBOL_POINT, priceDigits));
   PrintField("Tick size", SymbolDouble(symbol, SYMBOL_TRADE_TICK_SIZE, priceDigits));
   PrintField("Tick value", SymbolDouble(symbol, SYMBOL_TRADE_TICK_VALUE, 5));
   PrintField("Tick value (profit)", SymbolDouble(symbol, SYMBOL_TRADE_TICK_VALUE_PROFIT, 5));
   PrintField("Tick value (loss)", SymbolDouble(symbol, SYMBOL_TRADE_TICK_VALUE_LOSS, 5));
   PrintField("Contract size", SymbolDouble(symbol, SYMBOL_TRADE_CONTRACT_SIZE, 2));
   PrintField("Volume min", SymbolDouble(symbol, SYMBOL_VOLUME_MIN, 3));
   PrintField("Volume max", SymbolDouble(symbol, SYMBOL_VOLUME_MAX, 3));
   PrintField("Volume step", SymbolDouble(symbol, SYMBOL_VOLUME_STEP, 3));
   PrintField("Bid", SymbolDouble(symbol, SYMBOL_BID, priceDigits));
   PrintField("Ask", SymbolDouble(symbol, SYMBOL_ASK, priceDigits));

   double point  = 0.0;
   double bid    = 0.0;
   double ask    = 0.0;
   SymbolInfoDouble(symbol, SYMBOL_POINT, point);
   SymbolInfoDouble(symbol, SYMBOL_BID, bid);
   SymbolInfoDouble(symbol, SYMBOL_ASK, ask);

   double spreadPrice  = (ask > bid) ? (ask - bid) : 0.0;
   double spreadPoints = (point > 0.0) ? (spreadPrice / point) : 0.0;

   PrintField("Spread (broker, points)", SymbolInteger(symbol, SYMBOL_SPREAD));
   PrintField("Spread (calculated, price)", DoubleToString(spreadPrice, priceDigits));
   PrintField("Spread (calculated, points)", DoubleToString(spreadPoints, 1));
   PrintField("Floating spread", YesNo(SymbolInfoInteger(symbol, SYMBOL_SPREAD_FLOAT) != 0));
   PrintField("Quote data available", YesNo(bid > 0.0 && ask > 0.0));

   MqlTick tick;
   if(SymbolInfoTick(symbol, tick))
      PrintField("Last tick time", TimeToString(tick.time, TIME_DATE | TIME_SECONDS));
   else
      PrintField("Last tick time", Unavailable());
}

void ReportSymbolTradingRules(const string symbol)
{
   long tradeMode = 0;
   long executionMode = 0;
   long calcMode = 0;
   long fillingMode = 0;
   long orderMode = 0;
   long swapMode = 0;
   long rolloverDay = 0;

   SymbolInfoInteger(symbol, SYMBOL_TRADE_MODE, tradeMode);
   SymbolInfoInteger(symbol, SYMBOL_TRADE_EXEMODE, executionMode);
   SymbolInfoInteger(symbol, SYMBOL_TRADE_CALC_MODE, calcMode);
   SymbolInfoInteger(symbol, SYMBOL_FILLING_MODE, fillingMode);
   SymbolInfoInteger(symbol, SYMBOL_ORDER_MODE, orderMode);
   SymbolInfoInteger(symbol, SYMBOL_SWAP_MODE, swapMode);
   SymbolInfoInteger(symbol, SYMBOL_SWAP_ROLLOVER3DAYS, rolloverDay);

   PrintSection("SYMBOL TRADING RULES");
   PrintField("Trading mode", SymbolTradeModeText(tradeMode));
   PrintField("Execution mode", SymbolExecutionModeText(executionMode));
   PrintField("Calculation mode", SymbolCalcModeText(calcMode));
   PrintField("Filling modes", SymbolFillingModeText(fillingMode));
   PrintField("Order types", SymbolOrderModeText(orderMode));
   PrintField("Stops level (points)", SymbolInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL));
   PrintField("Freeze level (points)", SymbolInteger(symbol, SYMBOL_TRADE_FREEZE_LEVEL));
   PrintField("Volume limit", SymbolDouble(symbol, SYMBOL_VOLUME_LIMIT, 3));
   PrintField("Margin initial", SymbolDouble(symbol, SYMBOL_MARGIN_INITIAL, 5));
   PrintField("Margin maintenance", SymbolDouble(symbol, SYMBOL_MARGIN_MAINTENANCE, 5));
   PrintField("Hedged margin", SymbolDouble(symbol, SYMBOL_MARGIN_HEDGED, 5));
   PrintField("Swap mode", SymbolSwapModeText(swapMode));
   PrintField("Swap long", SymbolDouble(symbol, SYMBOL_SWAP_LONG, 5));
   PrintField("Swap short", SymbolDouble(symbol, SYMBOL_SWAP_SHORT, 5));
   PrintField("3-day swap day", DayOfWeekText(rolloverDay));
}

void ReportAccount()
{
   string currency = AccountInfoString(ACCOUNT_CURRENCY);
   if(currency == "")
      currency = "?";

   long currencyDigits = AccountInfoInteger(ACCOUNT_CURRENCY_DIGITS);
   if(currencyDigits < 0 || currencyDigits > 8)
      currencyDigits = 2;

   long login = AccountInfoInteger(ACCOUNT_LOGIN);
   long leverage = AccountInfoInteger(ACCOUNT_LEVERAGE);
   long tradeMode = AccountInfoInteger(ACCOUNT_TRADE_MODE);
   long marginMode = AccountInfoInteger(ACCOUNT_MARGIN_MODE);
   long stopOutMode = AccountInfoInteger(ACCOUNT_MARGIN_SO_MODE);

   string stopOutUnit = (stopOutMode == ACCOUNT_STOPOUT_MODE_MONEY) ? (" " + currency) : " %";

   PrintSection("ACCOUNT INFORMATION");
   PrintField("Login", IntegerToString(login));
   PrintField("Account name", AccountString(ACCOUNT_NAME));
   PrintField("Broker company", AccountString(ACCOUNT_COMPANY));
   PrintField("Server", AccountString(ACCOUNT_SERVER));
   PrintField("Currency", currency);
   PrintField("Account type", AccountTradeModeText(tradeMode));
   PrintField("Leverage", "1:" + IntegerToString(leverage));
   PrintField("Margin mode", AccountMarginModeText(marginMode));
   PrintField("Position accounting", PositionAccountingText(marginMode));
   PrintField("Hedging allowed", YesNo(AccountInfoInteger(ACCOUNT_HEDGE_ALLOWED) != 0));
   PrintField("FIFO close required", YesNo(AccountInfoInteger(ACCOUNT_FIFO_CLOSE) != 0));

   Print("");
   PrintField("Balance", Money(ACCOUNT_BALANCE, currency, (int)currencyDigits));
   PrintField("Equity", Money(ACCOUNT_EQUITY, currency, (int)currencyDigits));
   PrintField("Margin", Money(ACCOUNT_MARGIN, currency, (int)currencyDigits));
   PrintField("Free margin", Money(ACCOUNT_MARGIN_FREE, currency, (int)currencyDigits));
   PrintField("Margin level", WithUnit(AccountDouble(ACCOUNT_MARGIN_LEVEL, 2), " %"));
   PrintField("Stop out mode", StopOutModeText(stopOutMode));
   PrintField("Margin call level", WithUnit(AccountDouble(ACCOUNT_MARGIN_SO_CALL, 2), stopOutUnit));
   PrintField("Stop out level", WithUnit(AccountDouble(ACCOUNT_MARGIN_SO_SO, 2), stopOutUnit));
}

void ReportEnvironment(const string symbol)
{
   PrintSection("BROKER / TRADING ENVIRONMENT");
   PrintField("Terminal", TerminalInfoString(TERMINAL_NAME));
   PrintField("Terminal build", IntegerToString(TerminalInfoInteger(TERMINAL_BUILD)));
   PrintField("Terminal company", TerminalInfoString(TERMINAL_COMPANY));
   PrintField("Terminal language", TerminalInfoString(TERMINAL_LANGUAGE));
   PrintField("Terminal connected", YesNo(TerminalInfoInteger(TERMINAL_CONNECTED) != 0));
   PrintField("Ping (microseconds)", IntegerToString(TerminalInfoInteger(TERMINAL_PING_LAST)));
   PrintField("Terminal trade allowed", YesNo(TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) != 0));
   PrintField("Account trade allowed", YesNo(AccountInfoInteger(ACCOUNT_TRADE_ALLOWED) != 0));
   PrintField("Account expert allowed", YesNo(AccountInfoInteger(ACCOUNT_TRADE_EXPERT) != 0));
   PrintField("EA trade allowed", YesNo(MQLInfoInteger(MQL_TRADE_ALLOWED) != 0));
   PrintField("Running in tester", YesNo(MQLInfoInteger(MQL_TESTER) != 0));
   PrintField("Visual mode", YesNo(MQLInfoInteger(MQL_VISUAL_MODE) != 0));
   PrintField("Symbol in Market Watch", YesNo(SymbolInfoInteger(symbol, SYMBOL_SELECT) != 0));
   PrintField("Symbol visible", YesNo(SymbolInfoInteger(symbol, SYMBOL_VISIBLE) != 0));
   PrintField("Market book depth", SymbolInteger(symbol, SYMBOL_TICKS_BOOKDEPTH));
}

void ReportSafety()
{
   PrintSection("SAFETY STATUS");
   Print("Automatic entry logic    : NONE");
   Print("Phase 1 execution engine : installed, idle");
   Print("Execution is only callable by a future strategy.");
   Print("DRY_RUN                  : " + GEA_BoolText(g_config.dryRun));
   Print("Safety lock              : " + GEA_SafetyLockSummary());
   Print("This EA does not open, modify or close positions automatically.");
}

void RunPhase0Diagnostics(const string symbol)
{
   ReportHeader();
   ReportSymbol(symbol);
   ReportSymbolTradingRules(symbol);
   ReportAccount();
   ReportEnvironment(symbol);
   ReportSafety();
   Print("");
   Print("Phase 0 environment report complete.");
   Print(GEA_SEPARATOR);
}

#endif // GEA_PHASE0_MQH
//+------------------------------------------------------------------+
