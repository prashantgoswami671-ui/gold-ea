"""Shared backtest core for Phase 2B: data, indicators, metrics, statistics.

No strategy logic lives here. Everything is deterministic and reproducible.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

TRADING_DAYS = 252
INITIAL_CAPITAL = 100_000.0

IS_START = pd.Timestamp("2004-01-01", tz="UTC")
IS_END = pd.Timestamp("2016-12-31 23:59:59", tz="UTC")
OOS_START = pd.Timestamp("2017-01-01", tz="UTC")
OOS_END = pd.Timestamp("2026-06-30 23:59:59", tz="UTC")
HOLDOUT_START = pd.Timestamp("2022-01-01", tz="UTC")

SUBPERIODS = [
    ("2004-2007", "2004-01-01", "2007-12-31"),
    ("2008-2011", "2008-01-01", "2011-12-31"),
    ("2012-2015", "2012-01-01", "2015-12-31"),
    ("2016-2018", "2016-01-01", "2018-12-31"),
    ("2019-2020", "2019-01-01", "2020-12-31"),
    ("2021-2023", "2021-01-01", "2023-12-31"),
    ("2024-2026", "2024-01-01", "2026-06-30"),
]

MACRO_REGIMES = [
    ("M1 secular bull", "2004-01-01", "2011-12-31"),
    ("M2 bear/range", "2012-01-01", "2015-12-31"),
    ("M3 reflation/range", "2016-01-01", "2019-12-31"),
    ("M4 shock/stimulus", "2020-01-01", "2021-12-31"),
    ("M5 regime break", "2022-01-01", "2026-06-30"),
]


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

def load_series(name: str) -> pd.DataFrame:
    path = PROCESSED / f"XAUUSD_{name}.parquet"
    df = pd.read_parquet(path)
    df["time"] = pd.to_datetime(df["time"], utc=True)
    return df.sort_values("time").reset_index(drop=True)


def slice_period(df: pd.DataFrame, start, end) -> pd.DataFrame:
    return df.loc[(df["time"] >= start) & (df["time"] <= end)].reset_index(drop=True)


# --------------------------------------------------------------------------
# Indicators (Wilder smoothing where applicable)
# --------------------------------------------------------------------------

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr.ewm(alpha=1.0 / period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0.0)
    down = (-delta).clip(lower=0.0)
    roll_up = up.ewm(alpha=1.0 / period, adjust=False).mean()
    roll_down = down.ewm(alpha=1.0 / period, adjust=False).mean()
    rs = roll_up / roll_down.replace(0.0, np.nan)
    return (100.0 - 100.0 / (1.0 + rs)).fillna(50.0)


def realised_vol(close: pd.Series, span: int = 60, annualise: bool = True) -> pd.Series:
    r = np.log(close).diff()
    v = r.ewm(span=span, adjust=False).std()
    return v * np.sqrt(TRADING_DAYS) if annualise else v


# --------------------------------------------------------------------------
# Cost model
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class CostModel:
    multiplier: float = 1.0
    commission_per_oz_round_turn: float = 0.07   # $7 per 100 oz round turn
    swap_long_per_oz_day: float = -0.126         # -12.6 points x $0.01
    swap_short_per_oz_day: float = -0.046        # -4.6 points x $0.01
    entry_slip_frac: float = 0.5                 # of spread
    exit_slip_frac: float = 0.5                  # of spread, signal exit
    stop_slip_frac: float = 1.0                  # of spread, stop exit

    def scaled(self) -> "CostModel":
        return CostModel(
            multiplier=self.multiplier,
            commission_per_oz_round_turn=self.commission_per_oz_round_turn * self.multiplier,
            swap_long_per_oz_day=self.swap_long_per_oz_day * self.multiplier,
            swap_short_per_oz_day=self.swap_short_per_oz_day * self.multiplier,
            entry_slip_frac=self.entry_slip_frac,
            exit_slip_frac=self.exit_slip_frac,
            stop_slip_frac=self.stop_slip_frac,
        )

    def entry_fill(self, raw: float, spread: float, direction: int) -> tuple[float, float]:
        """Return (fill, frictionless_reference).

        Raw is a bid price. A long buys at ask plus entry slippage; a short
        sells at bid minus entry slippage.
        """
        s = spread * self.multiplier
        if direction > 0:
            return raw + s + self.entry_slip_frac * s, raw
        return raw - self.entry_slip_frac * s, raw

    def exit_fill(self, raw: float, spread: float, direction: int, is_stop: bool) -> tuple[float, float]:
        s = spread * self.multiplier
        slip = self.stop_slip_frac if is_stop else self.exit_slip_frac
        if direction > 0:
            return raw - slip * s, raw
        return raw + s + slip * s, raw

    def commission(self, size_oz: float) -> float:
        return self.commission_per_oz_round_turn * size_oz * self.multiplier

    def swap(self, direction: int, size_oz: float, days: float) -> float:
        """Return swap as a positive cost.

        The configured swap rates are negative when they are a charge to the
        trader, so the sign is inverted here. Every caller should subtract the
        returned value; returning the raw rate would turn the cost into a
        subsidy.
        """
        rate = self.swap_long_per_oz_day if direction > 0 else self.swap_short_per_oz_day
        return -rate * self.multiplier * size_oz * days


# --------------------------------------------------------------------------
# Trade statistics and equity metrics
# --------------------------------------------------------------------------

def equity_metrics(equity: pd.Series, initial: float = INITIAL_CAPITAL) -> dict:
    equity = equity.dropna()
    if len(equity) < 2:
        return {}
    ret = equity.pct_change().dropna()
    n = len(ret)
    years = n / TRADING_DAYS
    final = float(equity.iloc[-1])
    net = final - initial
    cagr = (final / initial) ** (1.0 / years) - 1.0 if years > 0 and final > 0 else np.nan
    std = float(ret.std())
    sharpe = float(ret.mean() / std * np.sqrt(TRADING_DAYS)) if std > 0 else np.nan
    downside = ret[ret < 0]
    dstd = float(downside.std())
    sortino = float(ret.mean() / dstd * np.sqrt(TRADING_DAYS)) if dstd > 0 else np.nan
    cummax = equity.cummax()
    dd = equity / cummax - 1.0
    max_dd = float(dd.min())
    max_dd_abs = float((equity - cummax).min())
    ulcer = float(np.sqrt(np.mean(dd.to_numpy() ** 2)))
    mar = float(cagr / abs(max_dd)) if max_dd < 0 else np.nan
    # drawdown duration
    peak_dates = equity.index[equity == cummax]
    recovery = 0
    cur = pd.Timestamp(equity.index[0])
    max_dur = 0
    for idx, val in equity.items():
        if val >= cummax.loc[idx]:
            cur = idx
        else:
            max_dur = max(max_dur, (idx - cur).days)
    return {
        "final_equity": final,
        "net_profit": net,
        "return_pct": net / initial * 100.0,
        "cagr_pct": cagr * 100.0,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_dd_pct": max_dd * 100.0,
        "max_dd_abs": max_dd_abs,
        "max_dd_duration_days": int(max_dur),
        "ulcer_pct": ulcer * 100.0,
        "mar": mar,
        "calmar": mar,
        "volatility_pct": std * np.sqrt(TRADING_DAYS) * 100.0,
        "n_days": n,
        "years": years,
    }


def trade_metrics(trades: pd.DataFrame) -> dict:
    if trades is None or trades.empty:
        return {
            "trades": 0,
            "win_rate_pct": np.nan,
            "profit_factor": np.nan,
            "avg_win": np.nan,
            "avg_loss": np.nan,
            "largest_win": np.nan,
            "largest_loss": np.nan,
            "max_consec_wins": 0,
            "max_consec_losses": 0,
            "expectancy_r": np.nan,
            "payoff_ratio": np.nan,
            "avg_holding_days": np.nan,
            "turnover_per_year": np.nan,
            "total_costs": np.nan,
            "gross_pnl": np.nan,
            "net_pnl": np.nan,
            "cost_pct_of_gross": np.nan,
            "long_pnl": np.nan,
            "short_pnl": np.nan,
            "spread_slip_cost": np.nan,
            "commission_cost": np.nan,
            "swap_cost": np.nan,
        }
    pnl = trades["net_pnl"]
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    gross_profit = float(wins.sum())
    gross_loss = float(-losses.sum())
    pf = gross_profit / gross_loss if gross_loss > 0 else np.nan
    consec_w = consec_l = cur_w = cur_l = 0
    for p in pnl:
        if p > 0:
            cur_w += 1
            cur_l = 0
        elif p < 0:
            cur_l += 1
            cur_w = 0
        else:
            cur_w = cur_l = 0
        consec_w = max(consec_w, cur_w)
        consec_l = max(consec_l, cur_l)
    total_costs = float(trades["total_cost"].sum())
    gross = float(trades["gross_pnl"].sum())
    holding = trades["holding_days"]
    span_years = (
        (trades["exit_time"].max() - trades["entry_time"].min()).days / 365.25
        if len(trades)
        else np.nan
    )
    risk_unit = trades["risk_dollars"].replace(0, np.nan)
    avg_risk = float(risk_unit.mean())
    return {
        "trades": int(len(trades)),
        "win_rate_pct": float((pnl > 0).mean() * 100.0),
        "profit_factor": float(pf),
        "avg_win": float(wins.mean()) if len(wins) else np.nan,
        "avg_loss": float(losses.mean()) if len(losses) else np.nan,
        "avg_risk": avg_risk,
        "avg_win_r": float(wins.mean() / avg_risk) if len(wins) and avg_risk > 0 else np.nan,
        "avg_loss_r": float(losses.mean() / avg_risk) if len(losses) and avg_risk > 0 else np.nan,
        "largest_win": float(pnl.max()),
        "largest_loss": float(pnl.min()),
        "max_consec_wins": int(consec_w),
        "max_consec_losses": int(consec_l),
        "expectancy_r": float((pnl / risk_unit).mean()),
        "payoff_ratio": float(wins.mean() / abs(losses.mean())) if len(wins) and len(losses) else np.nan,
        "avg_holding_days": float(holding.mean()),
        "turnover_per_year": float(len(trades) / span_years) if span_years else np.nan,
        "total_costs": total_costs,
        "gross_pnl": gross,
        "net_pnl": float(pnl.sum()),
        "cost_pct_of_gross": float(total_costs / gross * 100.0) if gross > 0 else np.nan,
        "long_pnl": float(trades.loc[trades["direction"] > 0, "net_pnl"].sum()),
        "short_pnl": float(trades.loc[trades["direction"] < 0, "net_pnl"].sum()),
        "spread_slip_cost": float(trades["spread_slip_cost"].sum()),
        "commission_cost": float(trades["commission_cost"].sum()),
        "swap_cost": float(trades["swap_cost"].sum()),
    }


# --------------------------------------------------------------------------
# Benchmarks
# --------------------------------------------------------------------------

def buy_and_hold(df: pd.DataFrame, costs: CostModel, initial: float = INITIAL_CAPITAL) -> dict:
    """Buy at the first open, hold to the last close, one round-trip of costs."""
    if df.empty:
        return {}
    entry_raw = float(df["open"].iloc[0])
    spread0 = float(df["spread"].iloc[0])
    fill, _ = costs.entry_fill(entry_raw, spread0, +1)
    size = initial / fill
    equity = size * df["close"]
    # exit cost at the end
    exit_raw = float(df["close"].iloc[-1])
    spread1 = float(df["spread"].iloc[-1])
    exit_fill, _ = costs.exit_fill(exit_raw, spread1, +1, is_stop=False)
    final = size * exit_fill - costs.commission(size)
    equity = equity.copy()
    equity.iloc[-1] = final
    equity.index = df["time"]
    m = equity_metrics(equity, initial)
    m["size_oz"] = size
    return m


# --------------------------------------------------------------------------
# Statistics
# --------------------------------------------------------------------------

def _norm_cdf(x: float) -> float:
    from math import erf, sqrt

    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _norm_ppf(p: float) -> float:
    """Inverse standard normal by bisection on erf. Robust and adequate."""
    if not (0.0 < p < 1.0):
        raise ValueError("p must be in (0,1)")
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def deflated_sharpe(returns: pd.Series, n_trials: int, sr_variance: float) -> dict:
    """Bailey & Lopez de Prado (2014) deflated Sharpe ratio."""
    r = returns.dropna()
    T = len(r)
    if T < 30 or r.std() == 0:
        return {"dsr": np.nan, "p_value": np.nan, "sr_daily": np.nan, "sr0": np.nan}
    sr = float(r.mean() / r.std())
    skew = float(r.skew())
    kurt = float(r.kurt() + 3.0)  # pandas kurt is excess
    gamma = 0.5772156649015329
    if n_trials < 2 or sr_variance <= 0:
        return {"dsr": np.nan, "p_value": np.nan, "sr_daily": sr, "sr0": np.nan}
    z1 = _norm_ppf(1.0 - 1.0 / n_trials)
    z2 = _norm_ppf(1.0 - 1.0 / (n_trials * np.e))
    sr0 = float(np.sqrt(sr_variance) * ((1 - gamma) * z1 + gamma * z2))
    denom = np.sqrt(max(1e-12, 1 - skew * sr + ((kurt - 1) / 4.0) * sr * sr))
    z = (sr - sr0) * np.sqrt(T - 1) / denom
    return {
        "dsr": float(_norm_cdf(z)),
        "p_value": float(1.0 - _norm_cdf(z)),
        "sr_daily": sr,
        "sr0": sr0,
        "skew": skew,
        "kurtosis": kurt,
        "T": T,
    }


def stationary_bootstrap_indices(n: int, block: float, rng: np.random.Generator) -> np.ndarray:
    """Politis-Romano stationary bootstrap index array."""
    p = 1.0 / block
    idx = np.empty(n, dtype=np.int64)
    idx[0] = rng.integers(0, n)
    for t in range(1, n):
        if rng.random() < p:
            idx[t] = rng.integers(0, n)
        else:
            idx[t] = (idx[t - 1] + 1) % n
    return idx


def whites_reality_check(
    return_matrix: pd.DataFrame,
    benchmark: pd.Series | None = None,
    n_boot: int = 1000,
    seed: int = 20261105,
) -> dict:
    """White's Reality Check on the best of several return series.

    return_matrix columns are trials, rows are observations. If a benchmark is
    supplied, each trial's series is evaluated as excess over the benchmark.
    """
    rng = np.random.default_rng(seed)
    X = return_matrix.dropna(how="all").fillna(0.0)
    if benchmark is not None:
        X = X.sub(benchmark.reindex(X.index).fillna(0.0), axis=0)
    T, K = X.shape
    if T < 30 or K < 1:
        return {"stat": np.nan, "p_value": np.nan, "best": None}
    f = X.to_numpy()
    means = f.mean(axis=0)
    stat = float(np.sqrt(T) * means.max())
    best = str(X.columns[int(means.argmax())])
    block = max(5.0, np.sqrt(T))
    exceed = 0
    for _ in range(n_boot):
        idx = stationary_bootstrap_indices(T, block, rng)
        boot_means = f[idx].mean(axis=0)
        boot_stat = float(np.sqrt(T) * (boot_means - means).max())
        if boot_stat >= stat:
            exceed += 1
    return {"stat": stat, "p_value": (exceed + 1) / (n_boot + 1), "best": best}


def bootstrap_sharpe_ci(returns: pd.Series, n_boot: int = 1000, seed: int = 20261105) -> dict:
    r = returns.dropna().to_numpy()
    if len(r) < 30:
        return {"sharpe_ci_low": np.nan, "sharpe_ci_high": np.nan}
    rng = np.random.default_rng(seed)
    block = max(5.0, np.sqrt(len(r)))
    out = np.empty(n_boot)
    for b in range(n_boot):
        idx = stationary_bootstrap_indices(len(r), block, rng)
        s = r[idx]
        out[b] = s.mean() / s.std() * np.sqrt(TRADING_DAYS) if s.std() > 0 else np.nan
    return {
        "sharpe_ci_low": float(np.nanpercentile(out, 2.5)),
        "sharpe_ci_high": float(np.nanpercentile(out, 97.5)),
    }


def beta_alpha(strategy: pd.Series, benchmark: pd.Series) -> dict:
    df = pd.concat([strategy.rename("s"), benchmark.rename("b")], axis=1).dropna()
    if len(df) < 30:
        return {"beta": np.nan, "alpha_annual": np.nan}
    cov = np.cov(df["s"], df["b"])
    beta = float(cov[0, 1] / cov[1, 1]) if cov[1, 1] > 0 else np.nan
    alpha_daily = float(df["s"].mean() - beta * df["b"].mean())
    return {"beta": beta, "alpha_annual": alpha_daily * TRADING_DAYS * 100.0}


def regime_series(daily_close: pd.Series) -> pd.DataFrame:
    """Volatility quartiles over a rolling five-year window."""
    r = np.log(daily_close).diff()
    vol = r.rolling(60).std() * np.sqrt(TRADING_DAYS)
    q = vol.rolling(TRADING_DAYS * 5, min_periods=TRADING_DAYS).rank(pct=True)
    bucket = pd.cut(q, [0, 0.25, 0.5, 0.75, 1.0], labels=["V1", "V2", "V3", "V4"])
    return pd.DataFrame({"vol": vol, "quartile": q, "regime": bucket}, index=daily_close.index)


def macro_regime(dates: pd.DatetimeIndex) -> pd.Series:
    out = pd.Series(index=dates, dtype=object)
    for name, start, end in MACRO_REGIMES:
        mask = (dates >= pd.Timestamp(start, tz="UTC")) & (dates <= pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1))
        out.loc[mask] = name
    return out


def subperiod(dates: pd.DatetimeIndex) -> pd.Series:
    out = pd.Series(index=dates, dtype=object)
    for name, start, end in SUBPERIODS:
        mask = (dates >= pd.Timestamp(start, tz="UTC")) & (
            dates <= pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1)
        )
        out.loc[mask] = name
    return out


def perf_by_group(returns: pd.Series, groups: pd.Series) -> dict:
    out = {}
    for g in groups.dropna().unique():
        r = returns.loc[groups == g].dropna()
        if len(r) < 2 or r.std() == 0:
            out[str(g)] = {"n": int(len(r)), "sharpe": np.nan, "total_return_pct": np.nan}
            continue
        out[str(g)] = {
            "n": int(len(r)),
            "sharpe": float(r.mean() / r.std() * np.sqrt(TRADING_DAYS)),
            "total_return_pct": float(((1 + r).prod() - 1) * 100.0),
        }
    return out


def save_json(obj: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")
