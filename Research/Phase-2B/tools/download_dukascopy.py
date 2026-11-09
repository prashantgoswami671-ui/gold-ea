"""Download and cache Dukascopy XAUUSD candles for Phase 2B.

Downloads day, hour and minute candles (BID and ASK) for 2004-01-01 to
2026-11-04, caches the compressed .bi5 files, and records a manifest with
SHA-256 hashes so every later series is reproducible.

The datafeed host is slow to establish a TLS connection and rate-limits
aggressively, but is fast on a persistent connection. Each worker therefore
keeps one keep-alive connection and reconnects only on failure.

Safe to re-run: existing non-empty files are skipped.

Usage:
    python download_dukascopy.py [--minutes] [--max-workers N]
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import lzma
import os
import ssl
import struct
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

HOST = "datafeed.dukascopy.com"
BASE_PATH = "/datafeed/XAUUSD"
UA = "Mozilla/5.0 (research; gold-ea)"

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "dukascopy"
CACHE.mkdir(parents=True, exist_ok=True)
MANIFEST = ROOT / "data" / "raw" / "dukascopy_manifest.jsonl"

START = date(2004, 1, 1)
END = date(2026, 11, 4)

_lock = threading.Lock()
_counts = {"new": 0, "skip": 0, "fail": 0, "empty": 0}


class Client:
    """One keep-alive HTTPS connection, owned by a single worker thread."""

    def __init__(self) -> None:
        self.ctx = ssl.create_default_context()
        self.conn: http.client.HTTPSConnection | None = None

    def _connect(self) -> None:
        self.close()
        self.conn = http.client.HTTPSConnection(
            HOST, 443, timeout=45, context=self.ctx
        )

    def close(self) -> None:
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception:  # noqa: BLE001
                pass
            self.conn = None

    def get(self, path: str, tries: int = 6) -> tuple[int, bytes]:
        last: Exception | None = None
        for attempt in range(tries):
            try:
                if self.conn is None:
                    self._connect()
                assert self.conn is not None
                self.conn.request(
                    "GET", path, headers={"User-Agent": UA, "Connection": "keep-alive"}
                )
                resp = self.conn.getresponse()
                body = resp.read()
                if resp.status in (404, 410):
                    return resp.status, b""
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                return resp.status, body
            except Exception as e:  # noqa: BLE001
                last = e
                self.close()
                time.sleep(min(0.5 * (attempt + 1), 4.0))
        raise RuntimeError(f"failed after {tries} tries: {last}")


# A client per worker thread.
_local = threading.local()


def client() -> Client:
    c = getattr(_local, "client", None)
    if c is None:
        c = Client()
        _local.client = c
    return c


def dukascopy_month(d: date) -> str:
    """Dukascopy uses a zero-based month in the URL."""
    return f"{d.month - 1:02d}"


def record(entry: dict) -> None:
    line = json.dumps(entry, sort_keys=True)
    with _lock:
        with MANIFEST.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def validate(raw: bytes) -> int:
    """Return record count, or -1 if the payload is not a valid candle file."""
    if not raw:
        return -1
    try:
        data = lzma.decompress(raw)
    except Exception:  # noqa: BLE001
        return -1
    if len(data) % 24 != 0:
        return -1
    n = len(data) // 24
    if n == 0:
        return -1
    sec, o, c, lo, hi, vol = struct.unpack(">iiiiif", data[:24])
    if not (sec == 0 and 0 < lo <= o <= 10_000_000 and 0 < lo <= c <= 10_000_000):
        return -1
    return n


def target(kind: str, side: str, d: date) -> Path:
    if kind in ("day", "hour"):
        return CACHE / kind / side / f"{d.year}" / f"{dukascopy_month(d)}.bi5"
    return (
        CACHE
        / "minute"
        / side
        / f"{d.year}"
        / f"{dukascopy_month(d)}"
        / f"{d.day:02d}.bi5"
    )


def path_for(kind: str, side: str, d: date) -> str:
    if kind == "day":
        return f"{BASE_PATH}/{d.year}/{dukascopy_month(d)}/{side}_candles_day_1.bi5"
    if kind == "hour":
        return f"{BASE_PATH}/{d.year}/{dukascopy_month(d)}/{side}_candles_hour_1.bi5"
    return (
        f"{BASE_PATH}/{d.year}/{dukascopy_month(d)}/{d.day:02d}/"
        f"{side}_candles_min_1.bi5"
    )


def job(kind: str, side: str, d: date) -> None:
    path = target(kind, side, d)
    if path.exists() and path.stat().st_size > 0:
        with _lock:
            _counts["skip"] += 1
        return

    url_path = path_for(kind, side, d)
    try:
        status, raw = client().get(url_path)
    except Exception as e:  # noqa: BLE001
        with _lock:
            _counts["fail"] += 1
            total = sum(_counts.values())
        record(
            {
                "kind": kind,
                "side": side,
                "date": d.isoformat(),
                "path": url_path,
                "status": "error",
                "error": str(e),
            }
        )
        if total % 250 == 0:
            print(f"  ... {total} {_counts}", flush=True)
        return

    if status in (404, 410) or not raw:
        with _lock:
            _counts["empty"] += 1
            total = sum(_counts.values())
        record(
            {
                "kind": kind,
                "side": side,
                "date": d.isoformat(),
                "path": url_path,
                "status": "not_found",
                "http": status,
            }
        )
        if total % 250 == 0:
            print(f"  ... {total} {_counts}", flush=True)
        return

    n = validate(raw)
    if n < 0:
        with _lock:
            _counts["empty"] += 1
            total = sum(_counts.values())
        record(
            {
                "kind": kind,
                "side": side,
                "date": d.isoformat(),
                "path": url_path,
                "status": "invalid",
                "bytes": len(raw),
            }
        )
        if total % 250 == 0:
            print(f"  ... {total} {_counts}", flush=True)
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(raw)
    os.replace(tmp, path)

    with _lock:
        _counts["new"] += 1
        total = sum(_counts.values())
    record(
        {
            "kind": kind,
            "side": side,
            "date": d.isoformat(),
            "path": url_path,
            "status": "ok",
            "bytes": len(raw),
            "records": n,
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    )
    if total % 500 == 0:
        print(f"  ... {total} {_counts}", flush=True)


def month_starts(start: date, end: date):
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield date(y, m, 1)
        m += 1
        if m == 13:
            m = 1
            y += 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", action="store_true")
    ap.add_argument("--minute-only", action="store_true")
    ap.add_argument("--minute-sides", default="BID", help="comma-separated sides for minute data")
    ap.add_argument("--skip-saturdays", action="store_true")
    ap.add_argument("--max-workers", type=int, default=8)
    args = ap.parse_args()

    jobs: list[tuple[str, str, date]] = []
    if not args.minute_only:
        for d in month_starts(START, END):
            for side in ("BID", "ASK"):
                jobs.append(("day", side, d))
                jobs.append(("hour", side, d))

    if args.minutes or args.minute_only:
        minute_sides = tuple(s.strip().upper() for s in args.minute_sides.split(",") if s.strip())
        d = START
        while d <= END:
            if not (args.skip_saturdays and d.weekday() == 5):
                for side in minute_sides:
                    jobs.append(("minute", side, d))
            d += timedelta(days=1)

    print(f"jobs: {len(jobs)}  workers: {args.max_workers}", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = [pool.submit(job, *j) for j in jobs]
        for _ in as_completed(futures):
            pass

    dt = time.time() - t0
    print(f"done in {dt:.1f}s  {_counts}", flush=True)
    if _counts["fail"]:
        print(f"WARNING: {_counts['fail']} failed; re-run to retry", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
