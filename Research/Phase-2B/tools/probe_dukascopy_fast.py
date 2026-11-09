"""Fast targeted probe of Dukascopy XAUUSD endpoints (no broad scanning)."""

import lzma
import struct
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (research; gold-ea)"}
BASE = "https://datafeed.dukascopy.com/datafeed/XAUUSD"


def fetch(url, tries=3, timeout=20):
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(0.8 * (attempt + 1))
    return None, last


def decode(raw, rec=24):
    if not raw:
        return "empty"
    data = lzma.decompress(raw)
    n = len(data) // rec
    first = struct.unpack(">" + "i" * (rec // 4), data[:rec]) if n else None
    return f"{n} records, first={first}"


def probe(label, url):
    status, raw = fetch(url)
    if not status:
        print(f"  {label:24s} ERROR {raw}")
        return
    try:
        msg = decode(raw)
    except Exception as e:  # noqa: BLE001
        msg = f"decode error {e}"
    print(f"  {label:24s} HTTP {status}  {msg}")


print("=== minute candles ===")
for y, m, d in [(2004, 0, 5), (2004, 5, 15), (2008, 8, 15), (2012, 1, 15), (2024, 4, 15)]:
    probe(f"{y}-{m+1:02d}-{d:02d}", f"{BASE}/{y}/{m:02d}/{d:02d}/BID_candles_min_1.bi5")

print("\n=== hour candles ===")
for y, m in [(2004, 0), (2004, 5), (2008, 8), (2012, 1), (2024, 4)]:
    probe(f"{y}-{m+1:02d}", f"{BASE}/{y}/{m:02d}/BID_candles_hour_1.bi5")

print("\n=== day candles ===")
for y, m in [(2004, 0), (2004, 5), (2008, 8), (2012, 1), (2024, 4)]:
    probe(f"{y}-{m+1:02d}", f"{BASE}/{y}/{m:02d}/BID_candles_day_1.bi5")

print("\n=== early-year minute spot checks ===")
for y, m, d in [(2003, 0, 2), (2003, 6, 1), (2004, 0, 2), (2004, 1, 2), (2004, 2, 1), (2004, 3, 1), (2004, 4, 3), (2004, 5, 1)]:
    probe(f"{y}-{m+1:02d}-{d:02d}", f"{BASE}/{y}/{m:02d}/{d:02d}/BID_candles_min_1.bi5")
