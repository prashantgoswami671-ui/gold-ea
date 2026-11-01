//+------------------------------------------------------------------+
//|                                                GoldEAConfig.mqh |
//|                          Gold EA Project - Phase 1 Configuration |
//|                                                                  |
//|  All configurable safety values live here. Strategy modules must  |
//|  not hardcode execution limits.                                  |
//+------------------------------------------------------------------+
#ifndef GEA_CONFIG_MQH
#define GEA_CONFIG_MQH

#include "GoldEALog.mqh"

const string GEA_VERSION   = "0.2";
const string GEA_PHASE     = "Phase 1 - Execution & Risk Engine";
const string GEA_SEPARATOR = "============================================================";

struct GoldEAConfig
{
   bool     dryRun;
   long     magicNumber;
   int      maxSpreadPoints;
   int      deviationPoints;
   int      maxTotalPositions;
   int      maxEAPositions;
   int      maxBuyPositions;
   int      maxSellPositions;
   double   maxEATotalVolume;
   double   minFreeMarginPct;
   double   minMarginLevelPct;
   bool     safetyLockAtStartup;
   bool     lockOnCriticalError;
   int      statusLogIntervalSeconds;
   string   orderComment;
   bool     runPhase0Diagnostics;
   bool     logExistingPositionsOnStart;
   bool     selfTestOnInit;
};

//--- Single process-wide configuration instance -------------------
GoldEAConfig g_config;

//+------------------------------------------------------------------+
//| Defaults (used for documentation and defensive initialisation)   |
//+------------------------------------------------------------------+
void GEA_ConfigDefaults(GoldEAConfig &cfg)
{
   cfg.dryRun                    = true;
   cfg.magicNumber               = 20261101;
   cfg.maxSpreadPoints           = 50;
   cfg.deviationPoints           = 30;
   cfg.maxTotalPositions         = 10;
   cfg.maxEAPositions            = 5;
   cfg.maxBuyPositions           = 3;
   cfg.maxSellPositions          = 3;
   cfg.maxEATotalVolume          = 1.00;
   cfg.minFreeMarginPct          = 30.0;
   cfg.minMarginLevelPct         = 150.0;
   cfg.safetyLockAtStartup       = false;
   cfg.lockOnCriticalError       = true;
   cfg.statusLogIntervalSeconds  = 300;
   cfg.orderComment              = "GoldEA-P1";
   cfg.runPhase0Diagnostics      = true;
   cfg.logExistingPositionsOnStart = true;
   cfg.selfTestOnInit            = false;
}

//+------------------------------------------------------------------+
//| Validate configuration before the engine is allowed to run       |
//+------------------------------------------------------------------+
bool GEA_ConfigValidate(const GoldEAConfig &cfg, string &reason)
{
   reason = "";

   if(cfg.magicNumber <= 0)
      reason = GEA_AppendReason(reason, "magic number must be greater than zero");

   if(cfg.maxSpreadPoints <= 0)
      reason = GEA_AppendReason(reason, "maximum spread must be greater than zero");

   if(cfg.deviationPoints < 0)
      reason = GEA_AppendReason(reason, "deviation/slippage cannot be negative");

   if(cfg.maxTotalPositions <= 0)
      reason = GEA_AppendReason(reason, "maximum total positions must be greater than zero");

   if(cfg.maxEAPositions <= 0)
      reason = GEA_AppendReason(reason, "maximum EA positions must be greater than zero");

   if(cfg.maxBuyPositions < 0)
      reason = GEA_AppendReason(reason, "maximum buy positions cannot be negative");

   if(cfg.maxSellPositions < 0)
      reason = GEA_AppendReason(reason, "maximum sell positions cannot be negative");

   if(!MathIsValidNumber(cfg.maxEATotalVolume) || cfg.maxEATotalVolume <= 0.0)
      reason = GEA_AppendReason(reason, "maximum EA total volume must be greater than zero");

   if(!MathIsValidNumber(cfg.minFreeMarginPct) ||
      cfg.minFreeMarginPct < 0.0 || cfg.minFreeMarginPct > 100.0)
      reason = GEA_AppendReason(reason, "minimum free-margin percentage must be between 0 and 100");

   if(!MathIsValidNumber(cfg.minMarginLevelPct) || cfg.minMarginLevelPct < 0.0)
      reason = GEA_AppendReason(reason, "minimum margin level must be zero or greater");

   if(cfg.statusLogIntervalSeconds < 0)
      reason = GEA_AppendReason(reason, "status log interval cannot be negative");

   if(StringLen(cfg.orderComment) > 31)
      reason = GEA_AppendReason(reason, "order comment cannot exceed 31 characters");

   return(reason == "");
}

//+------------------------------------------------------------------+
//| Keep broker comments short and free of line breaks               |
//+------------------------------------------------------------------+
string GEA_SanitizeComment(const string comment)
{
   string result = comment;
   StringReplace(result, "\r", " ");
   StringReplace(result, "\n", " ");
   if(StringLen(result) > 31)
      result = StringSubstr(result, 0, 31);
   if(result == "")
      result = "GoldEA";
   return(result);
}

//+------------------------------------------------------------------+
//| Configuration log                                                |
//+------------------------------------------------------------------+
void GEA_LogConfig(const GoldEAConfig &cfg)
{
   GEA_LogSection("PHASE 1 CONFIGURATION");
   GEA_LogInfo("Project version        : v" + GEA_VERSION);
   GEA_LogInfo("Phase                  : " + GEA_PHASE);
   GEA_LogInfo("DRY_RUN                : " + GEA_BoolText(cfg.dryRun) +
               (cfg.dryRun ? " (NO ORDERS WILL BE SENT)" : " (LIVE EXECUTION ENABLED)"));
   GEA_LogInfo("Magic number           : " + IntegerToString(cfg.magicNumber));
   GEA_LogInfo("Max spread (points)    : " + IntegerToString(cfg.maxSpreadPoints));
   GEA_LogInfo("Deviation (points)     : " + IntegerToString(cfg.deviationPoints));
   GEA_LogInfo("Max total positions    : " + IntegerToString(cfg.maxTotalPositions));
   GEA_LogInfo("Max EA positions       : " + IntegerToString(cfg.maxEAPositions));
   GEA_LogInfo("Max buy positions      : " + IntegerToString(cfg.maxBuyPositions));
   GEA_LogInfo("Max sell positions     : " + IntegerToString(cfg.maxSellPositions));
   GEA_LogInfo("Max EA total volume    : " + GEA_VolumeText(cfg.maxEATotalVolume));
   GEA_LogInfo("Min free margin after  : " + GEA_PercentText(cfg.minFreeMarginPct) + " of equity");
   GEA_LogInfo("Min projected margin   : " + GEA_PercentText(cfg.minMarginLevelPct));
   GEA_LogInfo("Safety lock at startup : " + GEA_YesNo(cfg.safetyLockAtStartup));
   GEA_LogInfo("Lock on critical error : " + GEA_YesNo(cfg.lockOnCriticalError));
   GEA_LogInfo("Status log interval    : " + IntegerToString(cfg.statusLogIntervalSeconds) + " s");
   GEA_LogInfo("Order comment          : " + cfg.orderComment);
   GEA_LogInfo("Existing positions log : " + GEA_YesNo(cfg.logExistingPositionsOnStart));
   GEA_LogInfo("Startup self-test      : " + GEA_YesNo(cfg.selfTestOnInit));
}

#endif // GEA_CONFIG_MQH
//+------------------------------------------------------------------+
