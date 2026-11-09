"""Probe intraday history depth and verify P&L arithmetic for XAUUSD."""

from datetime import datetime, timezone

import MetaTrader5 as mt5

mt5.initialize()
mt5.symbol_select("XAUUSD", True)

print("=== bars available from position 0 ===")
for label, tf in (
    ("D1", mt5.TIMEFRAME_D1),
    ("H4", mt5.TIMEFRAME_H4),
    ("H1", mt5.TIMEFRAME_H1),
    ("M30", mt5.TIMEFRAME_M30),
    ("M15", mt5.TIMEFRAME_M15),
    ("M5", mt5.TIMEFRAME_M5),
    ("M1", mt5.TIMEFRAME_M1),
):
    r = mt5.copy_rates_from_pos("XAUUSD", tf, 0, 2_000_000)
    if r is None or len(r) == 0:
        print(f"{label}: none ({mt5.last_error()})")
        continue
    first = datetime.fromtimestamp(int(r[0]["time"]), tz=timezone.utc)
    last = datetime.fromtimestamp(int(r[-1]["time"]), tz=timezone.utc)
    print(f"{label}: bars={len(r)} first={first:%Y-%m-%d %H:%M} last={last:%Y-%m-%d %H:%M}")

print("=== short-range intraday requests ===")
for label, tf, start in (
    ("M15 2024", mt5.TIMEFRAME_M15, datetime(2024, 1, 1)),
    ("M15 2026", mt5.TIMEFRAME_M15, datetime(2026, 1, 1)),
    ("H1 2024", mt5.TIMEFRAME_H1, datetime(2024, 1, 1)),
):
    r = mt5.copy_rates_range("XAUUSD", tf, start, datetime(2026, 11, 5))
    print(label, "->", None if r is None else len(r), mt5.last_error())

print("=== P&L arithmetic ===")
# 1 lot, buy at 4000.00, close at 4000.01 -> expect (4000.01-4000.00)*100 = $1.00
p1 = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, "XAUUSD", 1.0, 4000.00, 4000.01)
p01 = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, "XAUUSD", 0.01, 4000.00, 4000.01)
print("profit 1.0 lot, +0.01:", p1)
print("profit 0.01 lot, +0.01:", p01)
# 1 lot, +1.00 move
p100 = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, "XAUUSD", 1.0, 4000.00, 4001.00)
print("profit 1.0 lot, +1.00:", p100)

print("=== margin ===")
m = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, "XAUUSD", 0.01, 4000.00)
print("margin 0.01 lot at 4000:", m)

mt5.shutdown()
