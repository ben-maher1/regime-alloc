"""Data loading with on-disk caching and proxy splicing.

All outputs are business-day-indexed DataFrames of adjusted closes / levels.
BTC (7-day market) is aligned to the business-day calendar by taking the
last available print on or before each business day.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

from . import config as C


def _cache_path(name: str) -> Path:
    p = Path(C.CACHE_DIR)
    p.mkdir(exist_ok=True)
    return p / f"{name.replace('^', '').replace('=', '_')}.parquet"


def fetch_yf(tickers: list[str], start: str = C.START, refresh: bool = False) -> pd.DataFrame:
    import yfinance as yf

    out = {}
    for t in tickers:
        path = _cache_path(t)
        if path.exists() and not refresh:
            s = pd.read_parquet(path).iloc[:, 0]
        else:
            df = yf.download(t, start=start, auto_adjust=True, progress=False)
            if df.empty:
                print(f"[warn] no data for {t}")
                continue
            s = df["Close"].squeeze().rename(t)
            s.to_frame().to_parquet(path)
        out[t] = s
    return pd.DataFrame(out)


def fetch_fred(series: dict[str, str] = C.FRED_SERIES, start: str = C.START,
               refresh: bool = False) -> pd.DataFrame:
    """Needs FRED_API_KEY env var (free at fred.stlouisfed.org)."""
    from fredapi import Fred

    fred = Fred(api_key=os.environ["FRED_API_KEY"])
    out = {}
    for sid, name in series.items():
        path = _cache_path(f"fred_{sid}")
        if path.exists() and not refresh:
            s = pd.read_parquet(path).iloc[:, 0]
        else:
            s = fred.get_series(sid, observation_start=start).rename(name)
            s.to_frame().to_parquet(path)
        out[name] = s
    return pd.DataFrame(out)


def to_bday(df: pd.DataFrame) -> pd.DataFrame:
    idx = pd.bdate_range(df.index.min(), df.index.max())
    return df.sort_index().reindex(df.index.union(idx)).ffill().reindex(idx)


def splice(primary: pd.Series, proxy: pd.Series) -> pd.Series:
    """Chain proxy returns before `primary` starts, so the level series is
    continuous and equals `primary` from its first date onward."""
    primary = primary.dropna()
    proxy = proxy.dropna()
    if primary.empty:
        return proxy
    start = primary.index[0]
    pre = proxy[proxy.index <= start]
    if pre.empty:
        return primary
    scale = primary.iloc[0] / pre.iloc[-1]
    return pd.concat([pre.iloc[:-1] * scale, primary])


def load_asset_prices(refresh: bool = False) -> pd.DataFrame:
    tickers = set(C.ASSETS) | {v["proxy"] for v in C.ASSETS.values()}
    tickers |= set(C.EXTRA_PROXY.values()) | {C.CASH, C.CASH_PROXY}
    raw = to_bday(fetch_yf(sorted(tickers), refresh=refresh))

    out = {}
    for a, spec in C.ASSETS.items():
        s = splice(raw.get(a, pd.Series(dtype=float)), raw[spec["proxy"]])
        if a in C.EXTRA_PROXY:
            s = splice(s, raw[C.EXTRA_PROXY[a]])
        out[a] = s
    out[C.CASH] = splice(raw.get(C.CASH, pd.Series(dtype=float)), raw[C.CASH_PROXY])
    return pd.DataFrame(out)


def load_market_data(refresh: bool = False) -> pd.DataFrame:
    """Inputs for the regime model (phase 2)."""
    mkt = fetch_yf(C.MARKET_TICKERS, start=C.MARKET_START, refresh=refresh)
    try:
        fred = fetch_fred(start=C.MARKET_START, refresh=refresh)
        mkt = mkt.join(fred, how="outer")
    except KeyError:
        print("[warn] FRED_API_KEY not set; skipping FRED series")
    return to_bday(mkt)


def synthetic_prices(n: int = 252 * 12, seed: int = 0) -> pd.DataFrame:
    """Regime-switching fake prices for offline testing."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2012-01-02", periods=n)
    params = {"VT": (0.07, 0.16), "GLDM": (0.05, 0.15), "IBIT": (0.40, 0.70)}
    regime = np.repeat(rng.choice([-1, 1], size=n // 126 + 1, p=[0.35, 0.65]), 126)[:n]
    out = {}
    for a, (mu, vol) in params.items():
        drift = mu / 252 * np.where(regime > 0, 1.5, -1.0)
        r = drift + vol / np.sqrt(252) * rng.standard_t(5, n) * np.sqrt(3 / 5)
        out[a] = 100 * np.exp(np.cumsum(r))
    out[C.CASH] = 100 * np.exp(np.cumsum(np.full(n, 0.03 / 252)))
    return pd.DataFrame(out, index=idx)
