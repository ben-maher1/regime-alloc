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
