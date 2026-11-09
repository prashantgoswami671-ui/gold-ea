"""Build D1, H4, H1 and M15 XAUUSD series from cached Dukascopy candles.

Timestamp conventions (fixed for all of Phase 2B):

  H1  : UTC hours, stamped at the bar open (00:00, 01:00, ...).
  M15 : UTC quarter hours, stamped at the bar open.
  H4  : 22:00-aligned UTC bars (22, 02, 06, 10, 14, 18), matching the native
        MT5 H4 phase (MT5 server is UTC+2, so 00/04/08/12/16/20 server time is
        22/02/06/10/14/18 UTC).
  D1  : 22:00-to-22:00 UTC trading day, stamped at its close (22:00 UTC on the
        end date). This matches the FX/metals convention and the native MT5 D1
        phase, and avoids counting a two-hour Sunday evening session as a day.

Every bar is stamped at its open except D1, which is stamped at its close. In
both cases the engine executes a signal at the *next row's open*, which is the
first tradeable price after the signal bar closed.

Prices are Dukascopy BID, divided by 1000. Spread is ASK minus BID at the same
bar close. Zero-volume flat records are placeholders and are dropped.

Outputs (under data/processed/):
  XAUUSD_D1.parquet, XAUUSD_H4.parquet, XAUUSD_H1.parquet, XAUUSD_M15.parquet
  series_metadata.json
"""

from __future__ import annotations

import hashlib
import json
import lzma
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "dukascopy"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

START = date(2004, 1, 1)
END = date(2026, 11, 4)


def _decode(raw: bytes) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Decode a .bi5 payload into (seconds, open, high, low, close, volume)."""
    data = lzma.decompress(raw)
    if len(data) % 24 != 0:
        raise ValueError(f"bad payload length {len(data)}")
    arr = np.frombuffer(data, dtype=np.uint8).reshape(-1, 24)
    sec = arr[:, 0:4].copy().view(">i4").ravel().astype(np.int64)
    o = arr[:, 4:8].copy().view(">i4").ravel().astype(np.float64) / 1000.0
    c = arr[:, 8:12].copy().view(">i4").ravel().astype(np.float64) / 1000.0
    lo = arr[:, 12:16].copy().view(">i4").ravel().astype(np.float64) / 1000.0
    hi = arr[:, 16:20].copy().view(">i4").ravel().astype(np.float64) / 1000.0
    vol = arr[:, 20:24].copy().view(">f4").ravel().astype(np.float64)
    return sec, o, hi, lo, c, vol


def load_month(kind: str, side: str, year: int, month0: int) -> pd.DataFrame | None:
    path = CACHE / kind / side / f"{year}" / f"{month0:02d}.bi5"
    if not path.exists() or path.stat().st_size == 0:
        return None
    sec, o, hi, lo, c, vol = _decode(path.read_bytes())
    if len(sec) == 0:
        return None
    base = datetime(year, month0 + 1, 1, tzinfo=timezone.utc)
    times = pd.to_datetime(base) + pd.to_timedelta(sec, unit="s")
    df = pd.DataFrame(
        {"time": times, "open": o, "high": hi, "low": lo, "close": c, "volume": vol}
    )
    placeholder = (df["volume"] <= 0) & (df["high"] == df["low"])
    df = df.loc[~placeholder]
    return df if not df.empty else None


def load_range(kind: str, side: str) -> pd.DataFrame:
    frames = []
    y, m0 = START.year, START.month - 1
    while (y, m0) <= (END.year, END.month - 1):
        df = load_month(kind, side, y, m0)
        if df is not None:
            frames.append(df)
        m0 += 1
        if m0 == 12:
            m0 = 0
            y += 1
    if not frames:
        raise SystemExit(f"no {kind} {side} data cached")
    out = pd.concat(frames, ignore_index=True)
    return out.sort_values("time").drop_duplicates("time").reset_index(drop=True)


def add_spread(bid: pd.DataFrame, ask: pd.DataFrame) -> pd.DataFrame:
    a = ask.set_index("time")["close"].rename("ask_close")
    out = bid.set_index("time").join(a, how="left")
    out["spread"] = (out["ask_close"] - out["close"]).clip(lower=0)
    out = out.drop(columns=["ask_close"])
    out["spread"] = out["spread"].fillna(out["spread"].median())
    return out.reset_index()


def _agg(grouped) -> pd.DataFrame:
    return grouped.agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
        spread=("spread", "mean"),
        bars=("close", "count"),
    )


def build_h1() -> pd.DataFrame:
    bid = load_range("hour", "BID")
    ask = load_range("hour", "ASK")
    return add_spread(bid, ask)


def build_h4(h1: pd.DataFrame) -> pd.DataFrame:
    work = h1.set_index("time")
    shifted = work.copy()
    shifted.index = shifted.index - pd.Timedelta(hours=22)
    agg = _agg(shifted.resample("4h", label="left", closed="left"))
    agg = agg.dropna(subset=["open"])
    agg.index = agg.index + pd.Timedelta(hours=22)
    return agg.reset_index()


def build_d1(h1: pd.DataFrame) -> pd.DataFrame:
    work = h1.copy()
    # Trading day end: 22:00 UTC on the bar's date if the bar opens before
    # 22:00, otherwise 22:00 on the next date.
    t = work["time"]
    end_date = t.dt.normalize()
    after_22 = t.dt.hour >= 22
    end_date = end_date + pd.to_timedelta(after_22.astype(int), unit="D")
    # The Sunday evening session belongs to Monday's trading day. Without this,
    # 2004-2012 produce ~34 spurious one-hour "daily" bars per year.
    is_sunday = end_date.dt.day_of_week == 6
    end_date = end_date + pd.to_timedelta(is_sunday.astype(int), unit="D")
    work["session_end"] = end_date + pd.Timedelta(hours=22)
    agg = _agg(work.groupby("session_end"))
    agg = agg.dropna(subset=["open"])
    agg = agg.reset_index().rename(columns={"session_end": "time"})
    return agg.sort_values("time").reset_index(drop=True)


def minute_path(side: str, d: date) -> Path:
    return CACHE / "minute" / side / f"{d.year}" / f"{d.month - 1:02d}" / f"{d.day:02d}.bi5"


def load_day_minutes(side: str, d: date) -> pd.DataFrame | None:
    path = minute_path(side, d)
    if not path.exists() or path.stat().st_size == 0:
        return None
    sec, o, hi, lo, c, vol = _decode(path.read_bytes())
    if len(sec) == 0:
        return None
    base = pd.Timestamp(datetime(d.year, d.month, d.day, tzinfo=timezone.utc))
    times = base + pd.to_timedelta(sec, unit="s")
    df = pd.DataFrame(
        {"time": times, "open": o, "high": hi, "low": lo, "close": c, "volume": vol}
    )
    placeholder = (df["volume"] <= 0) & (df["high"] == df["low"])
    df = df.loc[~placeholder]
    return df if not df.empty else None


def build_m15(h1: pd.DataFrame, progress_every: int = 500) -> pd.DataFrame:
    """M15 OHLCV from BID minute candles, spread taken from the H1 series.

    Minute ASK data is not downloaded: it doubles the archive size and the
    spread series is available at H1 resolution. Each M15 bar is given the
    spread of the last *completed* H1 bar, so the value is known at the M15
    bar's open and no information from inside the bar leaks in.
    """
    frames = []
    d = START
    n = 0
    while d <= END:
        bid = load_day_minutes("BID", d)
        if bid is not None:
            bid["spread"] = np.nan
            agg = _agg(bid.set_index("time").resample("15min", label="left", closed="left"))
            agg = agg.dropna(subset=["open"])
            frames.append(agg.reset_index())
        n += 1
        if n % progress_every == 0:
            print(f"  minute days processed: {n} ({d})", flush=True)
        d += timedelta(days=1)
    if not frames:
        raise SystemExit("no minute data cached")
    out = pd.concat(frames, ignore_index=True)
    out = out.sort_values("time").drop_duplicates("time").reset_index(drop=True)
    out = out.drop(columns=["spread"])

    # H1 is stamped at the bar open, so shift by one hour to mark its close.
    h1_spread = h1[["time", "spread"]].copy()
    h1_spread["time"] = h1_spread["time"] + pd.Timedelta(hours=1)
    h1_spread = h1_spread.rename(columns={"spread": "spread"})
    out = pd.merge_asof(out, h1_spread, on="time", direction="backward")
    out["spread"] = out["spread"].ffill().bfill()
    return out


def qa(df: pd.DataFrame) -> dict:
    ret = np.log(df["close"]).diff().dropna()
    return {
        "rows": int(len(df)),
        "first": str(df["time"].iloc[0]),
        "last": str(df["time"].iloc[-1]),
        "duplicates": int(df["time"].duplicated().sum()),
        "bad_ohlc": int(
            (
                (df["high"] < df[["open", "close"]].max(axis=1))
                | (df["low"] > df[["open", "close"]].min(axis=1))
                | (df["high"] < df["low"])
            ).sum()
        ),
        "nonpositive": int((df[["open", "high", "low", "close"]] <= 0).any(axis=1).sum()),
        "zero_volume": int((df["volume"] <= 0).sum()),
        "ret_std": float(ret.std()),
        "ret_skew": float(ret.skew()),
        "ret_kurt": float(ret.kurt()),
        "spread_median": float(df["spread"].median()),
        "spread_p95": float(df["spread"].quantile(0.95)),
        "close_min": float(df["close"].min()),
        "close_max": float(df["close"].max()),
    }


def save(df: pd.DataFrame, name: str) -> dict:
    path = OUT / f"XAUUSD_{name}.parquet"
    df.to_parquet(path, index=False)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"path": str(path.relative_to(ROOT)), "sha256": digest, "rows": int(len(df))}


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-m15", action="store_true")
    args = ap.parse_args()

    print("building H1 ...", flush=True)
    h1 = build_h1()
    print(f"  H1 rows: {len(h1)}", flush=True)

    print("building D1 ...", flush=True)
    d1 = build_d1(h1)
    print(f"  D1 rows: {len(d1)}", flush=True)

    print("building H4 ...", flush=True)
    h4 = build_h4(h1)
    print(f"  H4 rows: {len(h4)}", flush=True)

    meta: dict = {
        "source": "Dukascopy XAUUSD BID/ASK candles",
        "price_scale": 1000,
        "d1_convention": "22:00-22:00 UTC, stamped at close (22:00 UTC end date)",
        "h4_convention": "22:00-aligned UTC (22/02/06/10/14/18), stamped at open",
        "h1_convention": "UTC hour open",
        "m15_convention": "UTC quarter hour open",
        "start": str(START),
        "end": str(END),
        "series": {},
    }

    for name, df in (("D1", d1), ("H4", h4), ("H1", h1)):
        meta["series"][name] = qa(df)
        meta["series"][name].update(save(df, name))
        print(name, meta["series"][name], flush=True)

    if not args.skip_m15:
        print("building M15 from minute candles ...", flush=True)
        m15 = build_m15(h1)
        meta["series"]["M15"] = qa(m15)
        meta["series"]["M15"].update(save(m15, "M15"))
        print("M15", meta["series"]["M15"], flush=True)

    (OUT / "series_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("wrote series_metadata.json", flush=True)


if __name__ == "__main__":
    main()
