"""Extract XAUUSD D1/H4 from the connected MT5 terminal and run a QA pass.

Writes raw CSVs plus a metadata file and a QA report under Research/Phase-2B/.
Read-only with respect to the terminal and the production EA.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"
RAW.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

START = datetime(2004, 1, 1)
END = datetime(2026, 11, 5)

mt5.initialize()
mt5.symbol_select("XAUUSD", True)
info = mt5.symbol_info("XAUUSD")
acct = mt5.account_info()
term = mt5.terminal_info()

meta = {
    "extracted_utc": datetime.now(timezone.utc).isoformat(),
    "terminal": term.name if term else None,
    "terminal_build": term.build if term else None,
    "company": term.company if term else None,
    "server": acct.server if acct else None,
    "account_login": acct.login if acct else None,
    "symbol": "XAUUSD",
    "digits": info.digits,
    "point": info.point,
    "tick_size": info.trade_tick_size,
    "tick_value_reported": info.trade_tick_value,
    "contract_size": info.trade_contract_size,
    "volume_min": info.volume_min,
    "volume_step": info.volume_step,
    "swap_long": info.swap_long,
    "swap_short": info.swap_short,
    "swap_mode": info.swap_mode,
    "currency_profit": info.currency_profit,
}

frames = {}
for label, tf in (("D1", mt5.TIMEFRAME_D1), ("H4", mt5.TIMEFRAME_H4)):
    rates = mt5.copy_rates_range("XAUUSD", tf, START, END)
    if rates is None or len(rates) == 0:
        raise SystemExit(f"no data for {label}")
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df[["time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"]]
    frames[label] = df
    out = RAW / f"mt5demo_XAUUSD_{label}.csv"
    df.to_csv(out, index=False, date_format="%Y-%m-%d %H:%M:%S")
    meta[f"{label}_rows"] = int(len(df))
    meta[f"{label}_sha256"] = hashlib.sha256(out.read_bytes()).hexdigest()
    meta[f"{label}_first"] = str(df["time"].iloc[0])
    meta[f"{label}_last"] = str(df["time"].iloc[-1])

mt5.shutdown()

(RAW / "mt5demo_XAUUSD_metadata.json").write_text(
    json.dumps(meta, indent=2), encoding="utf-8"
)

lines = ["# Data QA - MT5 demo XAUUSD", ""]
lines.append(f"Extracted (UTC): {meta['extracted_utc']}")
lines.append(f"Server: {meta['server']} / {meta['company']}")
lines.append("")

for label, df in frames.items():
    d = df.copy()
    dup = int(d["time"].duplicated().sum())
    if label == "D1":
        weekend = int((d["time"].dt.dayofweek >= 5).sum())
    else:
        weekend = 0
    bad_ohlc = int(
        (
            (d["high"] < d[["open", "close"]].max(axis=1))
            | (d["low"] > d[["open", "close"]].min(axis=1))
            | (d["high"] < d["low"])
        ).sum()
    )
    nonpos = int((d[["open", "high", "low", "close"]] <= 0).any(axis=1).sum())
    zerovol = int((d["tick_volume"] == 0).sum())
    gaps = d["time"].diff().dt.total_seconds() / 86400.0
    big_gaps = d.loc[gaps > (5 if label == "D1" else 4), "time"].dt.date.tolist()

    lines.append(f"## {label}")
    lines.append(f"- rows: {len(d)}")
    lines.append(f"- first: {d['time'].iloc[0]}  last: {d['time'].iloc[-1]}")
    lines.append(f"- duplicate timestamps: {dup}")
    lines.append(f"- weekend-stamped rows: {weekend}")
    lines.append(f"- OHLC inconsistencies: {bad_ohlc}")
    lines.append(f"- non-positive prices: {nonpos}")
    lines.append(f"- zero tick-volume rows: {zerovol}")
    lines.append(f"- close range: {d['close'].min():.2f} - {d['close'].max():.2f}")
    lines.append(f"- spread field: min {d['spread'].min()}, median {d['spread'].median()}, max {d['spread'].max()}")
    lines.append(f"- gaps > threshold: {len(big_gaps)} {big_gaps[:12]}")
    ret = np.log(d["close"]).diff().dropna()
    lines.append(
        f"- daily log-return std: {ret.std():.5f}  max abs: {ret.abs().max():.4f}"
        f"  skew {ret.skew():.2f}  kurt {ret.kurt():.2f}"
    )
    worst = ret.abs().sort_values(ascending=False).head(5)
    lines.append("- largest absolute log returns: " + ", ".join(
        f"{d['time'].iloc[i].date()} {ret.iloc[i]:+.4f}" for i in worst.index
    ))
    lines.append("")

(REPORTS / "data-qa-mt5demo.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
