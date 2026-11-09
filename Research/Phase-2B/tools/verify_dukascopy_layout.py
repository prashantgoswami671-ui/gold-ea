"""Verify Dukascopy record offsets and timestamp convention.

Decodes the first few records of minute, hour and day files and prints the
offsets, so the timestamp reconstruction rule can be fixed before ingestion.
"""

import lzma
import struct
import time
import urllib.request
from datetime import datetime, timedelta, timezone

UA = {"User-Agent": "Mozilla/5.0 (research; gold-ea)"}
BASE = "https://datafeed.dukascopy.com/datafeed/XAUUSD"


def fetch(url, tries=4):
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"failed {url}: {last}")


def records(url):
    raw = fetch(url)
    data = lzma.decompress(raw)
    assert len(data) % 24 == 0, len(data)
    out = []
    for i in range(0, len(data), 24):
        sec, o, c, lo, hi, vol = struct.unpack(">iiiiif", data[i : i + 24])
        out.append((sec, o / 1000, c / 1000, lo / 1000, hi / 1000, vol))
    return out


print("=== minute file 2004-01-05 (offsets should be 0,60,120,...) ===")
rec = records(f"{BASE}/2004/00/05/BID_candles_min_1.bi5")
print("count:", len(rec))
for r in rec[:4]:
    print(" ", r)
print("  last:", rec[-1])

print("\n=== hour file 2004-01 (offsets reveal unit) ===")
rec = records(f"{BASE}/2004/00/BID_candles_hour_1.bi5")
print("count:", len(rec))
for r in rec[:4]:
    print(" ", r)
print("  record 24..27:", rec[24:28])
print("  last:", rec[-1])

print("\n=== day file 2004-01 (offsets reveal unit) ===")
rec = records(f"{BASE}/2004/00/BID_candles_day_1.bi5")
print("count:", len(rec))
for r in rec[:4]:
    print(" ", r)
print("  last:", rec[-1])

print("\n=== hour file 2026-09 (check offsets near end) ===")
rec = records(f"{BASE}/2026/09/BID_candles_hour_1.bi5")
print("count:", len(rec))
for r in rec[:3]:
    print(" ", r)
print("  last:", rec[-1])

print("\n=== sanity: daily close 2004-01-05 from day file vs known ===")
# reconstruct day 5 close from minute data
day = records(f"{BASE}/2004/00/05/BID_candles_min_1.bi5")
print("  minute-day close:", day[-1][2], "high:", max(r[4] for r in day), "low:", min(r[3] for r in day))
