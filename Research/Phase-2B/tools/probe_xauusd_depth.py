"""Probe usable history depth for XAUUSD on the connected terminal."""

from datetime import datetime, timezone

import MetaTrader5 as mt5

mt5.initialize()

name = "XAUUSD"
s = mt5.symbol_info(name)
print("symbol selected:", mt5.symbol_select(name, True))
print(
    "spec:",
    dict(
        digits=s.digits,
        point=s.point,
        tick_size=s.trade_tick_size,
        tick_value=s.trade_tick_value,
        contract=s.trade_contract_size,
        vol_min=s.volume_min,
        vol_step=s.volume_step,
        swaps=(s.swap_long, s.swap_short, s.swap_mode),
        spread=s.spread,
    ),
)

ranges = [
    ("D1", mt5.TIMEFRAME_D1, datetime(2004, 1, 1), datetime(2026, 11, 5)),
    ("H4", mt5.TIMEFRAME_H4, datetime(2004, 1, 1), datetime(2026, 11, 5)),
    ("H1", mt5.TIMEFRAME_H1, datetime(2010, 1, 1), datetime(2026, 11, 5)),
    ("M15", mt5.TIMEFRAME_M15, datetime(2010, 1, 1), datetime(2026, 11, 5)),
    ("M1", mt5.TIMEFRAME_M1, datetime(2024, 1, 1), datetime(2026, 11, 5)),
]

for label, tf, start, end in ranges:
    r = mt5.copy_rates_range(name, tf, start, end)
    if r is None:
        print(f"{label}: None {mt5.last_error()}")
        continue
    if len(r) == 0:
        print(f"{label}: 0 bars")
        continue
    first = datetime.fromtimestamp(int(r[0]["time"]), tz=timezone.utc)
    last = datetime.fromtimestamp(int(r[-1]["time"]), tz=timezone.utc)
    print(f"{label}: bars={len(r)} first={first:%Y-%m-%d %H:%M} last={last:%Y-%m-%d %H:%M}")

mt5.shutdown()
