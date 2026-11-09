"""Probe Dukascopy minute-candle endpoint and decode record layout."""

import lzma
import struct
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (research; gold-ea)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read()


def try_url(url):
    try:
        status, raw = fetch(url)
    except Exception as e:  # noqa: BLE001
        print(f"{url}\n   ERROR {e}")
        return None
    print(f"{url}\n   HTTP {status}, {len(raw)} bytes compressed")
    if not raw:
        return None
    try:
        data = lzma.decompress(raw)
    except Exception as e:  # noqa: BLE001
        print(f"   lzma error {e}")
        return None
    print(f"   decompressed {len(data)} bytes")
    for rec in (24, 20, 16):
        if len(data) % rec == 0:
            print(f"   divisible by {rec}: {len(data)//rec} records")
    for rec in (24, 20):
        if len(data) >= rec:
            print(f"   first {rec}B:", struct.unpack(">" + "i" * (rec // 4), data[:rec]))
    return data


print("=== candle endpoints ===")
for url in [
    "https://datafeed.dukascopy.com/datafeed/XAUUSD/2015/00/05/BID_candles_min_1.bi5",
    "https://datafeed.dukascopy.com/datafeed/XAUUSD/2004/05/15/BID_candles_min_1.bi5",
    "https://datafeed.dukascopy.com/datafeed/XAUUSD/2015/00/05/ASK_candles_min_1.bi5",
    "https://datafeed.dukascopy.com/datafeed/XAUUSD/2015/00/05/BID_candles_hour_1.bi5",
    "https://datafeed.dukascopy.com/datafeed/XAUUSD/2015/00/BID_candles_day_1.bi5",
]:
    try_url(url)
    print()
