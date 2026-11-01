//+------------------------------------------------------------------+
//|                                               GoldEASafety.mqh |
//|                          Gold EA Project - Phase 1 Safety Lock   |
//|                                                                  |
//|  An EA-level lock that blocks NEW trades. It never blocks        |
//|  diagnostics, logging, position inspection or emergency closes.  |
//+------------------------------------------------------------------+
#ifndef GEA_SAFETY_MQH
#define GEA_SAFETY_MQH

#include "GoldEALog.mqh"

struct GoldEASafetyState
{
   bool     locked;
   string   source;
   string   reason;
   datetime since;
};

GoldEASafetyState g_safety;

datetime GEA_Now()
{
   datetime now = TimeTradeServer();
   if(now <= 0)
      now = TimeLocal();
   return(now);
}

void GEA_SafetyInit()
{
   g_safety.locked = false;
   g_safety.source = "";
   g_safety.reason = "";
   g_safety.since  = 0;
}

void GEA_SafetyLockActivate(const string source, const string reason)
{
   if(!g_safety.locked)
      g_safety.since = GEA_Now();
   g_safety.locked = true;
   g_safety.source = source;
   g_safety.reason = reason;
   GEA_LogWarn("SAFETY LOCK ACTIVE | source=" + source + " | reason=" + reason);
}

void GEA_SafetyLockDeactivate(const string source, const string reason)
{
   if(!g_safety.locked)
     {
      GEA_LogInfo("Safety lock is already clear (requested by " + source + ").");
      return;
     }
   string previous = g_safety.reason;
   g_safety.locked = false;
   g_safety.source = "";
   g_safety.reason = "";
   g_safety.since  = 0;
   GEA_LogInfo("SAFETY LOCK CLEARED | source=" + source + " | previous reason=" +
               previous + " | clearance reason=" + reason);
}

bool GEA_SafetyIsLocked()
{
   return(g_safety.locked);
}

string GEA_SafetyLockSummary()
{
   if(!g_safety.locked)
      return("clear");
   return("ACTIVE | source=" + g_safety.source + " | reason=" + g_safety.reason);
}

bool GEA_SafetyAllowNewTrades(string &reason)
{
   reason = "";
   if(!g_safety.locked)
      return(true);
   reason = "safety lock active: " + g_safety.reason + " (source: " + g_safety.source + ")";
   return(false);
}

void GEA_LogSafetyState()
{
   if(g_safety.locked)
     {
      GEA_LogWarn("Safety lock            : " + GEA_SafetyLockSummary());
      if(g_safety.since > 0)
         GEA_LogWarn("Safety lock since      : " +
                     TimeToString(g_safety.since, TIME_DATE | TIME_SECONDS));
     }
   else
      GEA_LogInfo("Safety lock            : clear");
}

#endif // GEA_SAFETY_MQH
//+------------------------------------------------------------------+
