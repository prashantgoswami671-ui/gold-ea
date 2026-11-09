"""Compact timezone and bar-boundary probe for the connected MT5 feed.

Read-only. Prints:
  1. System UTC vs last tick time (implied server offset).
  2. D1 bar timestamp hour distribution (bar boundary convention).
  3. H4 bar timestamp hour distribution.
  4. Earliest date with usable M15 / H1 data.
"""

from datetime import datetime, timezone

import MetaTrader5 as mt5
import pandas as pd

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]

mt5.initialize()
mt5.symbol_select("XAUUSD", True)

# 1. offset
tick = mt5.symbol_info_tick("XAUUSD")
now_utc = datetime.now(timezone.utc)
if tick:
    tick_utc = datetime.fromtimestamp(tick.time, tz=timezone.utc)
    delta_h = (tick_utc - now_utc).total_seconds() / 3600.0
    print(f"system UTC        : {now_utc:%Y-%m-%d %H:%M:%S}")
    print(f"last tick (epoch) : {tick_utc:%Y-%m-%d %H:%M:%S}")
    print(f"implied offset    : {delta_h:+.2f} h")
else:
    print("tick: None")

# 2/3. bar boundary conventions from the extracted files
for label in ("D1", "H4"):
    df = pd.read_csv(ROOT / f"data/raw/mt5demo_XAUUSD_{label}.csv", parse_dates=["time"])
    hours = df["time"].dt.hour.value_counts().sort_index()
    print(f"\n{label} bar timestamp hours (count per hour):")
    print(hours.to_string())

# 4. first usable intraday date
print("\nfirst month with > 100 bars:")
for label, tf in (("H1", mt5.TIMEFRAME_H1), ("M15", mt5.TIMEFRAME_M15)):
    for year in range(2004, 2027):
        r = mt5.copy_rates_range(
            "XAUUSD", tf, datetime(year, 1, 1), datetime(year, 12, 31, 23, 59)
        )
        n = 0 if r is None else len(r)
        if n > 100:
            first = datetime.fromtimestamp(int(r[0]["time"]), tz=timezone.utc)
            print(f"  {label}: first usable year {year}, {n} bars, first={first:%Y-%m-%d %H:%M}")
            break
    else:
        print(f"  {label}: none")

mt5.shutdown()
