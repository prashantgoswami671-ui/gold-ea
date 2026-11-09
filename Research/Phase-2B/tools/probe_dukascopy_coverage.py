"""Probe Dukascopy coverage and endpoints for XAUUSD with retries.

Tests, for several historical dates:
  - minute candles (per day)
  - hour candles (per month)
  - whether the record layout decodes

Also determines the earliest date with non-empty data.
"""

import lzma
import struct
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (research; gold-ea)"}
BASE = "https://datafeed.dukascopy.com/datafeed/XAUUSD"


def fetch(url, tries=4, timeout=40):
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (attempt + 1))
    return None, last


def decode(raw, rec=24):
    if not raw:
        return None
    try:
        data = lzma.decompress(raw)
    except Exception as e:  # noqa: BLE001
        return f"lzma error {e}"
    if len(data) % rec != 0:
        return f"{len(data)} bytes, not divisible by {rec}"
    n = len(data) // rec
    first = struct.unpack(">" + "i" * (rec // 4), data[:rec]) if n else None
    return f"{n} records, first={first}"


def minute(year, month0, day):
    return f"{BASE}/{year}/{month0:02d}/{day:02d}/BID_candles_min_1.bi5"


def hour(year, month0):
    return f"{BASE}/{year}/{month0:02d}/BID_candles_hour_1.bi5"


def day(year, month0):
    return f"{BASE}/{year}/{month0:02d}/BID_candles_day_1.bi5"


print("=== minute candles across history ===")
for y, m, d in [(2004, 0, 5), (2004, 5, 15), (2008, 8, 15), (2012, 1, 15), (2018, 4, 15), (2024, 4, 15)]:
    status, raw = fetch(minute(y, m, d))
    msg = decode(raw) if status else f"ERROR {raw}"
    print(f"  {y}-{m+1:02d}-{d:02d}  HTTP {status}  {msg}")

print("\n=== hour candles across history ===")
for y, m in [(2004, 0), (2004, 5), (2008, 8), (2012, 1), (2018, 4), (2024, 4)]:
    status, raw = fetch(hour(y, m))
    msg = decode(raw) if status else f"ERROR {raw}"
    print(f"  {y}-{m+1:02d}  HTTP {status}  {msg}")

print("\n=== day candles across history ===")
for y, m in [(2004, 0), (2004, 5), (2008, 8), (2012, 1), (2018, 4), (2024, 4)]:
    status, raw = fetch(day(y, m))
    msg = decode(raw) if status else f"ERROR {raw}"
    print(f"  {y}-{m+1:02d}  HTTP {status}  {msg}")

print("\n=== earliest minute data: scan 2003-2005 January ===")
for y in (2003, 2004, 2005):
    for m in (0, 1):
        found = None
        for d in range(1, 29):
            status, raw = fetch(minute(y, m, d), tries=1, timeout=15)
            if status and raw:
                # confirm it decodes
                r = decode(raw)
                if isinstance(r, str) and "records" in r and not r.startswith("0 "):
                    found = (d, r)
                    break
        print(f"  {y}-{m+1:02d}: {found}")
