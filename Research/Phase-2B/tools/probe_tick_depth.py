"""Probe available tick history depth and point-spread statistics on the feed."""

from datetime import datetime

import MetaTrader5 as mt5

mt5.initialize()
mt5.symbol_select("XAUUSD", True)

print("=== tick history depth ===")
for start, end in [
    (datetime(2004, 6, 14), datetime(2004, 6, 18)),
    (datetime(2010, 1, 4), datetime(2010, 1, 8)),
    (datetime(2015, 1, 5), datetime(2015, 1, 9)),
    (datetime(2020, 1, 6), datetime(2020, 1, 10)),
    (datetime(2024, 1, 8), datetime(2024, 1, 12)),
    (datetime(2026, 10, 26), datetime(2026, 10, 30)),
]:
    ticks = mt5.copy_ticks_range("XAUUSD", start, end, mt5.COPY_TICKS_ALL)
    print(f"  {start.date()} .. {end.date()} -> {0 if ticks is None else len(ticks)} ticks  {mt5.last_error()}")

print("\n=== current spread ===")
s = mt5.symbol_info("XAUUSD")
t = mt5.symbol_info_tick("XAUUSD")
print("  symbol.spread (points):", s.spread)
print("  tick bid/ask:", t.bid, t.ask, "diff:", round(t.ask - t.bid, 2))
print("  commission fields: not exposed by symbol_info")

mt5.shutdown()
