"""Volatility-adjusted momentum.

For each horizon h:  score_h = annualized log return over h / annualized
realized vol over the same h. That's a rolling Sharpe estimate, so horizons
and assets (VT vs IBIT) are on a comparable scale. The final score is a
weighted average across horizons. All values at date t use data through the
close of t only; the backtester applies them to t+1 returns.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return np.log(prices).diff()


def horizon_score(prices: pd.DataFrame, h: int, skip: int = 0, ann: int = 252) -> pd.DataFrame:
    lr = log_returns(prices)
    window = lr.shift(skip).rolling(h, min_periods=int(h * 0.8))
    mu = window.mean() * ann
    sd = window.std() * np.sqrt(ann)
    return mu / sd.replace(0, np.nan)


def vol_adjusted_momentum(prices: pd.DataFrame,
                          lookbacks=C.LOOKBACKS,
                          weights=C.LOOKBACK_WEIGHTS,
                          skip: int = C.SKIP_DAYS,
                          smoothing: int | None = C.SCORE_SMOOTHING) -> pd.DataFrame:
    w = np.ones(len(lookbacks)) if weights is None else np.asarray(weights, float)
    w = w / w.sum()
    scores = [horizon_score(prices, h, skip) * wi for h, wi in zip(lookbacks, w)]
    # sum() propagates NaN, so a score exists only once every horizon is available
    score = sum(scores)
    if smoothing:
        score = score.ewm(halflife=smoothing, min_periods=1).mean().where(score.notna())
    return score


def ewma_vol(prices: pd.DataFrame, halflife: int = C.VOL_HALFLIFE, ann: int = 252) -> pd.DataFrame:
    return log_returns(prices).ewm(halflife=halflife, min_periods=halflife).std() * np.sqrt(ann)


def breakout_state(prices: pd.DataFrame, n_high: int, n_low: int | None = None) -> pd.DataFrame:
    """Donchian state: 1 from a close at a new n_high-day high until a close
    at a new n_low-day low, else 0. Window includes close t (data through t)."""
    n_low = n_low or n_high
    hi = prices >= prices.rolling(n_high, min_periods=n_high).max()
    lo = prices <= prices.rolling(n_low, min_periods=n_low).min()
    st = pd.DataFrame(np.nan, index=prices.index, columns=prices.columns)
    st[lo] = 0.0
    st[hi] = 1.0
    return st.ffill().fillna(0.0)


def reentry_score(prices: pd.DataFrame, score: pd.DataFrame, signal_cap: float = C.SIGNAL_CAP,
                  fast_weight: float = 0.0, fast_lookbacks=(10, 20), fast_smoothing: int | None = 3,
                  breakout_high: int | None = None, breakout_low: int | None = None,
                  breakout_strength: float = 1.0) -> pd.DataFrame:
    """Faster re-entry on top of the slow score (research; defaults = no-op).

    fast_weight  blend (1-a)*slow + a*fast, fast = vol-adjusted momentum over
                 fast_lookbacks with its own EWMA smoothing
    breakout_*   while a Donchian breakout is on, lift the score to at least
                 breakout_strength * signal_cap, i.e. strength >= breakout_strength
    """
    out = score
    if fast_weight:
        fast = vol_adjusted_momentum(prices, lookbacks=list(fast_lookbacks), smoothing=fast_smoothing)
        out = (1 - fast_weight) * out + fast_weight * fast
    if breakout_high:
        on = breakout_state(prices, breakout_high, breakout_low).astype(bool)
        out = out.where(~on | (out >= breakout_strength * signal_cap), breakout_strength * signal_cap)
    return out.where(score.notna())
