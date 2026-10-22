"""Daily backtest. Weights decided at close t earn simple returns on t+1;
trading costs are charged on t+1 for trades made at close t."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .regime import constant_exposure
from .signals import ewma_vol, vol_adjusted_momentum
from .sizing import apply_rebalance_band, target_weights


SIGNAL_PARAMS = ("lookbacks", "weights", "skip", "smoothing")
SIZING_PARAMS = ("max_weight", "target_vol", "signal_floor", "signal_cap", "base_weights", "use_signal",
                 "strength_floor", "redistribute")
EXTRA_PARAMS = {"vol_halflife", "floor_trend"}


def build_targets(prices: pd.DataFrame, exposure: pd.Series | None = None,
                  params: dict | None = None) -> pd.DataFrame:
    """`params` overrides config defaults for research runs: keys from
    SIGNAL_PARAMS, SIZING_PARAMS, plus "vol_halflife". Empty = production."""
    params = dict(params or {})
    unknown = set(params) - set(SIGNAL_PARAMS) - set(SIZING_PARAMS) - EXTRA_PARAMS
    if unknown:
        raise KeyError(f"unknown target params: {sorted(unknown)}")
    risky = [a for a in C.ASSETS if a in prices.columns]
    p = prices[risky]
    score = vol_adjusted_momentum(p, **{k: params[k] for k in SIGNAL_PARAMS if k in params})
    vol = ewma_vol(p, halflife=params.get("vol_halflife", C.VOL_HALFLIFE))
    if exposure is None:
        exposure = constant_exposure(prices.index)
    rets = prices.pct_change()
    extra = {}
    if params.get("strength_floor"):
        extra["trend_up"] = trend_up(p, score, params.get("floor_trend", 200))
    tw = target_weights(score, vol, exposure, returns=rets, **extra,
                        **{k: params[k] for k in SIZING_PARAMS if k in params})
    # rows where no risky signal is available yet -> NaN (warm-up)
    tw[score.isna().all(axis=1)] = np.nan
    return tw


def trend_up(p: pd.DataFrame, score: pd.DataFrame, rule="score|200") -> pd.DataFrame:
    """Which sleeves count as 'positive trend' for strength_floor. `rule`:
    "score" (momentum score > 0), an int n (close above n-day SMA), or
    "score|n" (either). Uses closes through t only."""
    if rule == "score":
        return score > 0
    if isinstance(rule, str) and rule.startswith("score|"):
        return (score > 0) | trend_up(p, score, int(rule.split("|")[1]))
    return p > p.rolling(int(rule), min_periods=int(rule)).mean()


def run(prices: pd.DataFrame, targets: pd.DataFrame, band: float = C.REBALANCE_BAND) -> dict:
    rets = prices[targets.columns].pct_change()
    # treat sleeves without data yet (e.g. pre-history NaNs) as zero return
    held, trades = apply_rebalance_band(targets, rets.fillna(0.0), band)
    cost = pd.Series(C.COST_BPS).reindex(targets.columns).fillna(0) / 1e4
    tc = (trades.abs() * cost).sum(axis=1)
    gross = (held.shift(1) * rets.fillna(0.0)).sum(axis=1, min_count=1)
    net = (gross - tc.shift(1).fillna(0.0)).dropna()
    net = net[held.shift(1).notna().all(axis=1).reindex(net.index, fill_value=False)]
    return {"returns": net, "weights": held, "trades": trades, "costs": tc}


def stats(r: pd.Series, rf: pd.Series | None = None, name: str = "") -> pd.Series:
    r = r.dropna()
    yrs = len(r) / 252
    eq = (1 + r).cumprod()
    cagr = eq.iloc[-1] ** (1 / yrs) - 1
    vol = r.std() * np.sqrt(252)
    ex = r - (rf.reindex(r.index).fillna(0) if rf is not None else 0)
    sharpe = ex.mean() / r.std() * np.sqrt(252)
    dd = eq / eq.cummax() - 1
    down = r[r < 0].std() * np.sqrt(252)
    return pd.Series({
        "CAGR": cagr, "Vol": vol, "Sharpe": sharpe,
        "Sortino": (ex.mean() * 252) / down if down else np.nan,
        "MaxDD": dd.min(), "Calmar": cagr / abs(dd.min()) if dd.min() else np.nan,
        "Years": yrs,
    }, name=name)


def turnover_stats(res: dict) -> pd.Series:
    t = res["trades"]
    yrs = len(res["returns"]) / 252
    w = res["weights"].dropna()
    risky = [c for c in w.columns if c != C.CASH]
    return pd.Series({
        "Turnover/yr (one-way)": t.abs().sum(axis=1).sum() / 2 / yrs,
        "Rebalances/yr": (t.abs().sum(axis=1) > 1e-9).sum() / yrs,
        "Avg risky exposure": w[risky].sum(axis=1).mean(),
        "Cost drag/yr": res["costs"].sum() / yrs,
    })


def benchmark(prices: pd.DataFrame, weights: dict, index: pd.DatetimeIndex) -> pd.Series:
    """Daily-rebalanced static mix (cheap approximation)."""
    rets = prices[list(weights)].pct_change().reindex(index).fillna(0.0)
    return (rets * pd.Series(weights)).sum(axis=1)
