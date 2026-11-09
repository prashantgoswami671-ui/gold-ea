"""Per-year history coverage for XAUUSD on the connected terminal."""

from datetime import datetime, timezone

import MetaTrader5 as mt5

mt5.initialize()
mt5.symbol_select("XAUUSD", True)

TFS = {
    "D1": mt5.TIMEFRAME_D1,
    "H4": mt5.TIMEFRAME_H4,
    "H1": mt5.TIMEFRAME_H1,
    "M15": mt5.TIMEFRAME_M15,
}

print(f"{'year':>6} " + " ".join(f"{k:>8}" for k in TFS))
for year in range(2004, 2027):
    row = []
    for label, tf in TFS.items():
        r = mt5.copy_rates_range(
            "XAUUSD", tf, datetime(year, 1, 1), datetime(year, 12, 31, 23, 59)
        )
        row.append(0 if r is None else len(r))
    print(f"{year:>6} " + " ".join(f"{v:>8}" for v in row))

mt5.shutdown()
