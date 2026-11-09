"""Probe external gold data sources for long-history intraday and daily data."""

import lzma
import struct
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (research; gold-ea)"}


def head(url, timeout=20):
    req = urllib.request.Request(url, headers=UA, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.headers.get("Content-Length"), r.read(64)


def dukascopy_probe(year, month0, day, hour):
    url = (
        f"https://datafeed.dukascopy.com/datafeed/XAUUSD/"
        f"{year}/{month0:02d}/{day:02d}/{hour:02d}h_ticks.bi5"
    )
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read()
        status = r.status
    except Exception as e:  # noqa: BLE001
        return url, f"ERROR {e}", 0
    if not raw:
        return url, f"HTTP {status}, empty body", 0
    try:
        data = lzma.decompress(raw)
    except Exception as e:  # noqa: BLE001
        return url, f"HTTP {status}, {len(raw)} bytes, lzma error {e}", 0
    n = len(data) // 20
    # tick record: uint32 ms offset, uint32 ask, uint32 bid, float32 askvol, float32 bidvol
    if n:
        ms, ask, bid, av, bv = struct.unpack(">IIIff", data[:20])
        return url, f"HTTP {status}, {n} ticks, first ask={ask} bid={bid}", n
    return url, f"HTTP {status}, 0 ticks", 0


print("=== Dukascopy XAUUSD tick files ===")
for args in [
    (2004, 5, 15, 12),
    (2008, 8, 15, 12),
    (2012, 2, 15, 12),
    (2018, 5, 15, 12),
    (2024, 5, 15, 12),
]:
    url, msg, n = dukascopy_probe(*args)
    print(f"{args} -> {msg}")

print()
print("=== Stooq daily XAUUSD ===")
try:
    req = urllib.request.Request(
        "https://stooq.com/q/d/l/?s=xauusd&i=d", headers=UA
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        body = r.read().decode("utf-8", "replace")
    lines = body.strip().splitlines()
    print("status ok, lines:", len(lines))
    print("head:", lines[:3])
    print("tail:", lines[-2:])
except Exception as e:  # noqa: BLE001
    print("ERROR", e)

print()
print("=== Yahoo chart API (XAUUSD=X) ===")
try:
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X"
        "?period1=1072915200&period2=1790000000&interval=1d"
    )
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        body = r.read().decode("utf-8", "replace")
    print("bytes:", len(body), "has timestamps:", '"timestamp"' in body)
except Exception as e:  # noqa: BLE001
    print("ERROR", e)
