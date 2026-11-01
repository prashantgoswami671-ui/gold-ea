//+------------------------------------------------------------------+
//|                                                 GoldEATypes.mqh |
//|                          Gold EA Project - Phase 1 Shared Types  |
//+------------------------------------------------------------------+
#ifndef GEA_TYPES_MQH
#define GEA_TYPES_MQH

//+------------------------------------------------------------------+
//| Snapshot of one EA-owned position                                |
//+------------------------------------------------------------------+
struct GoldEAPositionInfo
{
   ulong             ticket;
   long              magic;
   string            symbol;
   ENUM_POSITION_TYPE type;
   double            volume;
   double            priceOpen;
   double            sl;
   double            tp;
   double            profit;
   double            swap;
   datetime          time;
   string            comment;
};

//+------------------------------------------------------------------+
//| Position counts used by the safety limits                        |
//+------------------------------------------------------------------+
struct GoldEAPositionStats
{
   int    totalAccount;
   int    totalSymbol;
   int    eaCount;
   int    eaBuys;
   int    eaSells;
   double eaVolume;
   double eaBuyVolume;
   double eaSellVolume;
};

void GEA_ResetPositionStats(GoldEAPositionStats &stats)
{
   stats.totalAccount = 0;
   stats.totalSymbol  = 0;
   stats.eaCount      = 0;
   stats.eaBuys       = 0;
   stats.eaSells      = 0;
   stats.eaVolume     = 0.0;
   stats.eaBuyVolume  = 0.0;
   stats.eaSellVolume = 0.0;
}

//+------------------------------------------------------------------+
//| Result returned by every execution / close / modify request      |
//|                                                                  |
//|  success          : validations passed and either the broker     |
//|                     accepted the request or DRY_RUN simulated it. |
//|  validationPassed : every local safety check passed.             |
//|  dryRun           : no order was sent.                           |
//|  sent             : OrderSend() was actually called.             |
//+------------------------------------------------------------------+
struct GoldEAExecutionResult
{
   bool     success;
   bool     validationPassed;
   bool     dryRun;
   bool     sent;
   string   stage;
   string   reason;
   long     retcode;
   string   retcodeText;
   double   requestedVolume;
   double   validatedVolume;
   double   price;
   double   sl;
   double   tp;
   ulong    orderTicket;
   ulong    dealTicket;
   double   executedVolume;
   string   brokerComment;
};

void GEA_ResetExecutionResult(GoldEAExecutionResult &result)
{
   result.success          = false;
   result.validationPassed = false;
   result.dryRun           = false;
   result.sent             = false;
   result.stage            = "";
   result.reason           = "";
   result.retcode          = 0;
   result.retcodeText      = "";
   result.requestedVolume  = 0.0;
   result.validatedVolume  = 0.0;
   result.price            = 0.0;
   result.sl               = 0.0;
   result.tp               = 0.0;
   result.orderTicket      = 0;
   result.dealTicket       = 0;
   result.executedVolume   = 0.0;
   result.brokerComment    = "";
}

#endif // GEA_TYPES_MQH
//+------------------------------------------------------------------+
