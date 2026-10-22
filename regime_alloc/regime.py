"""Top-down regime layer.

Two composite axes, each the average of clipped rolling z-scores:

  RISK APPETITE (+ = risk-on)
    vix      -z(log VIX)                   implied equity vol, high = stress
    move     -z(log MOVE)                  implied bond vol
    credit   -z(63d change in Baa-10y)     spreads widening = stress
    trend    +z(S&P / 200d MA - 1)         equity trend
    dollar   -z(63d log change in DXY)     dollar spikes = global risk-off

  MACRO PRESSURE (+ = reflationary / hawkish)
    cu_au    +z(63d log change copper/gold)
    infl     +z(63d change 10y breakeven)
    yld      +z(63d change 10y yield)
    curve    +z(63d change 10y-2y)

Each axis is EWMA-smoothed and turned into a sticky sign (it must cross
+/- REGIME_DEADBAND to flip), giving four regimes:

    1 Goldilocks  risk+  pressure-      2 Reflation    risk+  pressure+
    3 Slowdown    risk-  pressure-      4 Stagflation  risk-  pressure+

Exposure per regime comes from config.REGIME_EXPOSURE. Everything at date t
uses data through t only.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C

RISK_FEATURES = ["vix", "move", "credit", "trend", "dollar"]
PRESSURE_FEATURES = ["cu_au", "infl", "yld", "curve"]


def _z(s: pd.Series, window=C.Z_WINDOW, min_periods=C.Z_MIN, clip=C.Z_CLIP) -> pd.Series:
    r = s.rolling(window, min_periods=min_periods)
    return ((s - r.mean()) / r.std()).clip(-clip, clip)


def features(m: pd.DataFrame, n: int = C.CHANGE_DAYS) -> pd.DataFrame:
    f = pd.DataFrame(index=m.index)
    f["vix"] = -_z(np.log(m["^VIX"]))
    f["move"] = -_z(np.log(m["^MOVE"]))
    f["credit"] = -_z(m["baa_spread"].diff(n))
    f["trend"] = _z(m["^GSPC"] / m["^GSPC"].rolling(200).mean() - 1)
    f["dollar"] = -_z(np.log(m["DX-Y.NYB"]).diff(n))
    f["cu_au"] = _z(np.log(m["HG=F"] / m["GC=F"]).diff(n))
    f["infl"] = _z(m["breakeven10y"].diff(n))
    f["yld"] = _z(m["ust10y"].diff(n))
    f["curve"] = _z((m["ust10y"] - m["ust2y"]).diff(n))
    return f


def sticky_sign(x: pd.Series, band: float = C.REGIME_DEADBAND) -> pd.Series:
    out = np.full(len(x), np.nan)
    state = np.nan
    for i, v in enumerate(x.values):
        if np.isnan(v):
            out[i] = state
            continue
        if np.isnan(state):
            state = 1.0 if v >= 0 else -1.0
        elif state > 0 and v < -band:
            state = -1.0
        elif state < 0 and v > band:
            state = 1.0
        out[i] = state
    return pd.Series(out, index=x.index)


def compute_regime(m: pd.DataFrame, smoothing: int = C.REGIME_SMOOTHING,
                   band: float = C.REGIME_DEADBAND) -> pd.DataFrame:
    f = features(m)
    risk = f[RISK_FEATURES].mean(axis=1, skipna=True).where(f[RISK_FEATURES].notna().sum(axis=1) >= 3)
    pres = f[PRESSURE_FEATURES].mean(axis=1, skipna=True).where(f[PRESSURE_FEATURES].notna().sum(axis=1) >= 2)
    risk_s = risk.ewm(halflife=smoothing).mean()
    pres_s = pres.ewm(halflife=smoothing).mean()
    rs, ps = sticky_sign(risk_s, band), sticky_sign(pres_s, band)
    regime = pd.Series(np.select(
        [(rs > 0) & (ps <= 0), (rs > 0) & (ps > 0), (rs <= 0) & (ps <= 0), (rs <= 0) & (ps > 0)],
        [1, 2, 3, 4], default=np.nan), index=m.index)
    regime[rs.isna() | ps.isna()] = np.nan
    return pd.concat([f, risk_s.rename("risk"), pres_s.rename("pressure"),
                      regime.rename("regime")], axis=1)


def regime_exposure(reg: pd.DataFrame, mapping: dict = C.REGIME_EXPOSURE,
                    default: float = 1.0) -> pd.Series:
    return reg["regime"].map(mapping).fillna(default).rename("exposure")


# ---- simple stand-ins kept for comparison ----
def constant_exposure(index: pd.DatetimeIndex, level: float = 1.0) -> pd.Series:
    return pd.Series(level, index=index, name="exposure")


def trend_filter_exposure(prices: pd.Series, window: int = 200,
                          on: float = 1.0, off: float = 0.5) -> pd.Series:
    above = prices > prices.rolling(window).mean()
    return above.map({True: on, False: off}).rename("exposure")
