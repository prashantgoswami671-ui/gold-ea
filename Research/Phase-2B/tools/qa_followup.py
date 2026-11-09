"""Follow-up QA: timezone offset, extreme returns (correctly paired), gap detail."""

from datetime import datetime, timezone

import MetaTrader5 as mt5
import pandas as pd

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]

d1 = pd.read_csv(ROOT / "data/raw/mt5demo_XAUUSD_D1.csv", parse_dates=["time"])
h4 = pd.read_csv(ROOT / "data/raw/mt5demo_XAUUSD_H4.csv", parse_dates=["time"])

mt5.initialize()
tick = mt5.symbol_info_tick("XAUUSD")
now_utc = datetime.now(timezone.utc)
tick_utc = datetime.fromtimestamp(tick.time, tz=timezone.utc) if tick else None
print("system UTC      :", now_utc.strftime("%Y-%m-%d %H:%M:%S"))
print("last tick (as-if):", tick_utc.strftime("%Y-%m-%d %H:%M:%S") if tick_utc else None)
if tick_utc:
    print("implied offset  :", round((tick_utc - now_utc).total_seconds() / 3600, 2), "hours")
mt5.shutdown()

print("\n=== extreme daily returns (date paired to the return it belongs to) ===")
d1["ret"] = d1["close"].pct_change()
ext = d1.dropna(subset=["ret"]).reindex(d1["ret"].abs().sort_values(ascending=False).index[:8])
for _, r in ext.iterrows():
    print(f"{r['time'].date()}  ret={r['ret']:+.4%}  close={r['close']:.2f}  vol={int(r['tick_volume'])}")

print("\n=== H4 gap detail ===")
h4["gap_days"] = h4["time"].diff().dt.total_seconds() / 86400
for _, r in h4[h4["gap_days"] > 2].iterrows():
    print(f"gap ending {r['time']}  length={r['gap_days']:.2f} days")

print("\n=== D1 calendar-year bar counts ===")
print(d1.groupby(d1["time"].dt.year).size().to_string())

print("\n=== D1 close vs known reference points ===")
for date, claim in [
    ("2004-06-11", "first bar"),
    ("2011-09-06", "2011 peak area"),
    ("2015-12-17", "2015 low area"),
    ("2020-08-06", "2020 peak area"),
    ("2026-11-04", "last bar"),
]:
    row = d1[d1["time"] == date]
    if len(row):
        print(f"{date}: close={row['close'].iloc[0]:.2f} ({claim})")
    else:
        print(f"{date}: not a bar ({claim})")
