"""Turn signals + regime exposure into target weights.

  1. Baseline risk budget: inverse-vol weights across the risky sleeves
     (so IBIT gets far less capital than VT for the same risk).
  2. Each sleeve's signal strength in [0, 1] scales its baseline weight
     (score <= floor -> 0, score >= cap -> full baseline).
  3. Multiply by the regime's total exposure; apply per-sleeve caps.
  4. Optional portfolio vol targeting (scale down only).
  5. Whatever is left goes to cash.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C


def signal_strength(score: pd.DataFrame, floor: float = C.SIGNAL_FLOOR,
                    cap: float = C.SIGNAL_CAP) -> pd.DataFrame:
    return ((score - floor) / (cap - floor)).clip(0, 1)


def target_weights(score: pd.DataFrame, vol: pd.DataFrame, exposure: pd.Series,
                   returns: pd.DataFrame | None = None,
                   max_weight: dict = C.MAX_WEIGHT,
                   target_vol: float | None = C.TARGET_VOL,
                   cash: str = C.CASH,
                   signal_floor: float = C.SIGNAL_FLOOR,
                   signal_cap: float = C.SIGNAL_CAP,
                   base_weights: dict | None = None,
                   use_signal: bool = True,
                   strength_floor: float = 0.0,
                   trend_up: pd.DataFrame | None = None,
                   redistribute: str | None = C.REDISTRIBUTE,
                   port_vol_target: float | None = None,
                   port_vol_halflife: int = C.VOL_HALFLIFE) -> pd.DataFrame:
    """`base_weights` (fixed dict) replaces the inverse-vol baseline and
    `use_signal=False` sets every strength to 1. Both exist for diagnostics.

    Upside-capture levers (research; defaults = production):
      strength_floor  min strength for sleeves where `trend_up` is True
      redistribute    None   unused weight -> cash
                      "zero" baseline of zero-strength sleeves is re-spread
                             (inverse-vol) over sleeves with strength > 0
                      "normalize" scale risky weights to sum to 1 whenever any
                             sleeve is on (no cash drag from partial strength)
      port_vol_target instead of leaving partial strength in cash, normalize
                      base x strength to a fully-invested shape and size the
                      whole risky book to the target vol (EWMA covariance), up
                      or down, never above the regime exposure -- no leverage
    Regime cap and per-sleeve caps apply after; anything clipped goes to cash."""
    assets = list(score.columns)
    if base_weights is None:
        inv = 1.0 / vol[assets]
        base = inv.div(inv.sum(axis=1), axis=0)
    else:
        bw = pd.Series(base_weights).reindex(assets).fillna(0.0)
        base = pd.DataFrame(np.tile(bw.values, (len(score), 1)), index=score.index, columns=assets)
        base = base.where(score.notna())          # sleeve not live yet -> no weight
    strength = signal_strength(score, signal_floor, signal_cap) if use_signal else score.notna().astype(float).where(score.notna())
    if strength_floor and trend_up is not None:
        up = trend_up.reindex(index=score.index, columns=assets).fillna(False).astype(bool)
        strength = strength.where(~up | (strength >= strength_floor), strength_floor)
    if redistribute == "zero":
        base = base.where(strength > 0)
        base = base.div(base.sum(axis=1), axis=0)
    w = base * strength
    if redistribute == "normalize":
        w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(w)
    elif redistribute not in (None, "zero"):
        raise ValueError(f"redistribute={redistribute!r}")
    expo = exposure.reindex(w.index).ffill()
    if port_vol_target is not None:
        if returns is None:
            raise ValueError("port_vol_target needs returns")
        shape = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
        pv = ewma_port_vol(shape, returns[assets], port_vol_halflife)
        k = (port_vol_target / pv).replace(np.inf, np.nan)
        w = shape.mul(np.minimum(k, expo), axis=0)      # NaN k (warm-up) -> NaN -> cash
    else:
        w = w.mul(expo, axis=0)
    w = w.clip(upper=pd.Series(max_weight).reindex(assets), axis=1)

    if target_vol is not None and returns is not None:
        cov_vol = _rolling_port_vol(w, returns[assets])
        scale = (target_vol / cov_vol).clip(upper=1.0).fillna(1.0)
        w = w.mul(scale, axis=0)

    w = w.fillna(0.0)
    w[cash] = (1.0 - w.sum(axis=1)).clip(lower=0.0)  # clip float noise
    return w


def ewma_port_vol(w: pd.DataFrame, rets: pd.DataFrame, halflife: int = C.VOL_HALFLIFE,
                  ann: int = 252) -> pd.Series:
    """Annualized vol of portfolio `w` under a zero-mean EWMA covariance of
    daily returns through t (RiskMetrics style). NaN until `halflife` obs."""
    r = rets.reindex(columns=w.columns).fillna(0.0).values
    lam = 0.5 ** (1 / halflife)
    S = np.zeros((r.shape[1], r.shape[1]))
    out = np.full(len(r), np.nan)
    W = w.fillna(0.0).values
    for i in range(len(r)):
        S = lam * S + (1 - lam) * np.outer(r[i], r[i])
        if i >= halflife:
            out[i] = np.sqrt(max(W[i] @ S @ W[i], 0.0) * ann)
    return pd.Series(out, index=w.index)


def _rolling_port_vol(w: pd.DataFrame, rets: pd.DataFrame, window: int = 63) -> pd.Series:
    covs = rets.rolling(window).cov() * 252
    out = pd.Series(np.nan, index=w.index)
    for dt in w.index:
        if dt not in covs.index.get_level_values(0):
            continue
        S = covs.loc[dt].values
        x = w.loc[dt].values
        if np.isnan(S).any() or np.isnan(x).any():
            continue
        out[dt] = float(np.sqrt(x @ S @ x))
    return out


def apply_rebalance_band(targets: pd.DataFrame, rets: pd.DataFrame,
                         band: float = C.REBALANCE_BAND) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Path-dependent holdings. Weights decided at close t earn t+1 returns,
    then drift. A trade happens at close t only if some sleeve's drifted weight
    is more than `band` from target. Returns (held_weights, trades)."""
    cols = targets.columns
    nxt = rets[cols].shift(-1).reindex(targets.index).fillna(0.0)
    held = np.full(targets.shape, np.nan)
    trades = np.zeros(targets.shape)
    T = targets.values
    R = nxt.values
    cur = None
    for i in range(len(targets)):
        tgt = T[i]
        if np.isnan(tgt).any():
            continue
        pre = np.zeros_like(tgt) if cur is None else cur
        if cur is None or np.abs(tgt - pre).max() > band:
            new = tgt.copy()
        else:
            new = pre
        trades[i] = new - pre
        held[i] = new
        grown = new * (1 + R[i])
        cur = grown / grown.sum()
    return (pd.DataFrame(held, index=targets.index, columns=cols),
            pd.DataFrame(trades, index=targets.index, columns=cols))
