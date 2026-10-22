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
                   redistribute: str | None = None) -> pd.DataFrame:
    """`base_weights` (fixed dict) replaces the inverse-vol baseline and
    `use_signal=False` sets every strength to 1. Both exist for diagnostics.

    Upside-capture levers (research; defaults = production):
      strength_floor  min strength for sleeves where `trend_up` is True
      redistribute    None   unused weight -> cash
                      "zero" baseline of zero-strength sleeves is re-spread
                             (inverse-vol) over sleeves with strength > 0
                      "normalize" scale risky weights to sum to 1 whenever any
                             sleeve is on (no cash drag from partial strength)
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
    w = w.mul(exposure.reindex(w.index).ffill(), axis=0)
    w = w.clip(upper=pd.Series(max_weight).reindex(assets), axis=1)

    if target_vol is not None and returns is not None:
        cov_vol = _rolling_port_vol(w, returns[assets])
        scale = (target_vol / cov_vol).clip(upper=1.0).fillna(1.0)
        w = w.mul(scale, axis=0)

    w = w.fillna(0.0)
    w[cash] = (1.0 - w.sum(axis=1)).clip(lower=0.0)  # clip float noise
    return w


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
