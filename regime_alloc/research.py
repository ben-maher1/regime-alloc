"""Research harness: config-driven runs, capture ratios, phase-split gap
decomposition, expanding-window walk-forward selection, lookahead check.

A run config is a flat dict. Keys:
  exposure          "regime" (default) | "none" | "trend"
  regime_*          see REGIME_KEYS; passed to compute_regime / regime_exposure
  band              rebalance band
  anything else     forwarded to backtest.build_targets(params=...)
An empty dict is the pre-study system (main before the 2026-10-22 upside-capture
study): PRE_STUDY is laid under every config so logged results stay reproducible.
PRODUCTION is the current config.py defaults written out explicitly.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .backtest import benchmark, build_targets, run
from .regime import compute_regime, regime_exposure, trend_filter_exposure

BENCH = {"VT": 0.80, "GLDM": 0.15, "IBIT": 0.05}
BENCH2 = {"VT": 0.60, "GLDM": 0.30, "IBIT": 0.10}   # ~ the system's own average mix (EXPERIMENTS.md 2026-10-23)
LAG_YEARS = [2009, 2012, 2019, 2023, 2026]
OOS_START = 2010                       # first walk-forward year (train = 2004-10 .. 2009 at minimum)
NO_CAPS = {"VT": 1.0, "GLDM": 1.0, "IBIT": 1.0}
STAT_COLS = ["CAGR", "Vol", "Sharpe", "MaxDD", "Calmar", "UpCap", "DownCap", "AvgExp", "Rebal/yr"]

# regime-side keys -> compute_regime kwargs (lever branches may extend this)
REGIME_KEYS = {"regime_smoothing": "smoothing", "regime_deadband": "band", "regime_band_up": "band_up"}
RUN_KEYS = {"exposure", "regime_exposure", "band", "rebalance"} | set(REGIME_KEYS)
PRE_STUDY = {"redistribute": None, "breakout_high": None}
PRE_STUDY_BAND = 0.05                  # configs without "band" keep the band every logged result used
PRODUCTION = {"redistribute": C.REDISTRIBUTE, "breakout_high": C.BREAKOUT_HIGH,
              "breakout_strength": C.BREAKOUT_STRENGTH, "band": C.REBALANCE_BAND}


# ---------------------------------------------------------------- lab
class Lab:
    """Holds data once; runs configs; caches regime computations."""

    def __init__(self, prices: pd.DataFrame, market: pd.DataFrame | None):
        self.prices = prices
        self.market = market
        self.rf = prices[C.CASH].pct_change()
        self._reg: dict = {}

    @classmethod
    def load(cls, synthetic: bool = False, refresh: bool = False) -> "Lab":
        from .data import (load_asset_prices, load_market_data, synthetic_market,
                           synthetic_prices)
        if synthetic:
            p = synthetic_prices(n=252 * 22)
            return cls(p, synthetic_market(p))
        return cls(load_asset_prices(refresh=refresh), load_market_data(refresh=refresh))

    def regime(self, cfg: dict) -> pd.DataFrame:
        kw = {v: cfg[k] for k, v in REGIME_KEYS.items() if k in cfg}
        key = tuple(sorted((k, repr(v)) for k, v in kw.items()))
        if key not in self._reg:
            self._reg[key] = compute_regime(self.market, **kw).reindex(self.prices.index).ffill()
        return self._reg[key]

    def exposure(self, cfg: dict) -> pd.Series | None:
        mode = cfg.get("exposure", "regime")
        if mode == "none":
            return None
        if mode == "trend":
            return trend_filter_exposure(self.prices["VT"])
        return regime_exposure(self.regime(cfg), cfg.get("regime_exposure", C.REGIME_EXPOSURE))

    def targets(self, cfg: dict) -> pd.DataFrame:
        params = {**PRE_STUDY, **{k: v for k, v in cfg.items() if k not in RUN_KEYS}}
        tw = build_targets(self.prices, self.exposure(cfg), params)
        return decision_days(tw, cfg.get("rebalance", "daily"))

    def run(self, cfg: dict) -> dict:
        res = run(self.prices, self.targets(cfg), band=cfg.get("band", PRE_STUDY_BAND))
        res["bench"] = benchmark(self.prices, BENCH, res["returns"].index)
        res["bench2"] = static_mix(self.prices, BENCH2, res["returns"].index)
        return res


def decision_days(tw: pd.DataFrame, rebalance: str = "daily") -> pd.DataFrame:
    """Only update targets on decision days and hold them in between:
    "weekly" = Fridays, "monthly" = last trading day of the month (calendar
    facts known in advance, so still causal)."""
    if rebalance == "daily":
        return tw
    d = tw.index
    if rebalance == "weekly":
        on = d.dayofweek == 4
    elif rebalance == "monthly":
        on = np.r_[d.month[1:] != d.month[:-1], True]
    else:
        raise ValueError(f"rebalance={rebalance!r}")
    return tw.where(pd.Series(on, index=d), axis=0).ffill()


def static_mix(prices: pd.DataFrame, weights: dict, index: pd.DatetimeIndex) -> pd.Series:
    """Daily-rebalanced, frictionless static mix; a sleeve with no data yet
    (IBIT/BTC before 2014) is dropped and the rest renormalized."""
    rets = prices[list(weights)].pct_change().reindex(index)
    w = pd.DataFrame(np.tile(list(weights.values()), (len(index), 1)), index=index,
                     columns=list(weights)).where(rets.notna())
    w = w.div(w.sum(axis=1), axis=0)
    return (w * rets.fillna(0.0)).sum(axis=1)


# ---------------------------------------------------------------- metrics
def _geo(x: pd.Series) -> float:
    return float(np.prod(1 + x) ** (1 / len(x)) - 1) if len(x) else np.nan


def monthly(r: pd.Series) -> pd.Series:
    return (1 + r).resample("ME").prod() - 1


def capture(r: pd.Series, bm: pd.Series) -> tuple[float, float]:
    """Monthly geometric up/down capture vs `bm`."""
    rm, bmm = monthly(r), monthly(bm.reindex(r.index).fillna(0.0))
    up, dn = bmm > 0, bmm < 0
    return _geo(rm[up]) / _geo(bmm[up]), _geo(rm[dn]) / _geo(bmm[dn])


def full_stats(r: pd.Series, bm: pd.Series, rf: pd.Series, res: dict | None = None) -> pd.Series:
    r = r.dropna()
    yrs = len(r) / 252
    eq = (1 + r).cumprod()
    dd = (eq / eq.cummax() - 1).min()
    cagr = eq.iloc[-1] ** (1 / yrs) - 1
    ex = r - rf.reindex(r.index).fillna(0.0)
    up, dn = capture(r, bm)
    out = {"CAGR": cagr, "Vol": r.std() * np.sqrt(252),
           "Sharpe": ex.mean() / r.std() * np.sqrt(252),
           "MaxDD": dd, "Calmar": cagr / abs(dd) if dd else np.nan,
           "UpCap": up, "DownCap": dn}
    if res is not None:
        w = res["weights"].reindex(r.index).dropna()
        t = res["trades"].reindex(r.index).fillna(0.0)
        out["AvgExp"] = w.drop(columns=C.CASH).sum(axis=1).mean()
        out["Rebal/yr"] = (t.abs().sum(axis=1) > 1e-9).sum() / yrs
    return pd.Series(out)


def per_year(r: pd.Series) -> pd.Series:
    return (1 + r).groupby(r.index.year).prod() - 1


def criteria(s: pd.Series, base: pd.Series, min_upcap_gain: float = 0.05) -> pd.Series:
    """The success criteria from the upside-capture brief, vs `base` stats."""
    ok = {"UpCap+": s["UpCap"] >= base["UpCap"] + min_upcap_gain,
          "CAGR>=11%": s["CAGR"] >= 0.11,
          "DD>=-20%": s["MaxDD"] >= -0.20,
          "Sharpe>=base-0.1": s["Sharpe"] >= base["Sharpe"] - 0.10}
    ok["ALL"] = all(ok.values())
    return pd.Series(ok)


# ---------------------------------------------------------------- phases / decomposition
def phases(bm: pd.Series, depth: float = 0.10) -> pd.Series:
    """Label each day of the benchmark path: 'falling' (peak -> trough of a
    drawdown deeper than `depth`), 'recovery' (trough -> regained peak) or
    'normal'. Uses hindsight; for diagnosis only, never for signals."""
    eq = (1 + bm.fillna(0.0)).cumprod()
    peak = eq.cummax()
    under = eq < peak
    lab = pd.Series("normal", index=bm.index)
    ep = (~under).cumsum()[under]               # episode id for underwater days
    for _, days in ep.groupby(ep):
        seg = eq.loc[days.index]
        if (seg / peak.loc[days.index] - 1).min() > -depth:
            continue
        trough = seg.idxmin()
        lab.loc[days.index[0]:trough] = "falling"
        lab.loc[days.index[days.index > trough]] = "recovery"
    return lab


def episodes(bm: pd.Series, depth: float = 0.10) -> list[tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]]:
    lab = phases(bm, depth)
    out, i = [], 0
    vals, idx = lab.values, lab.index
    while i < len(vals):
        if vals[i] == "falling":
            j = i
            while j < len(vals) and vals[j] == "falling":
                j += 1
            k = j
            while k < len(vals) and vals[k] == "recovery":
                k += 1
            out.append((idx[i], idx[j - 1], idx[min(k, len(vals)) - 1]))
            i = k
        else:
            i += 1
    return out


DECOMP_LAYERS = [
    # name, cfg, what the step from the previous layer measures
    ("80/15/5 w/ band+costs", {"exposure": "none", "base_weights": BENCH, "use_signal": False,
                               "max_weight": NO_CAPS}, "friction (band, costs)"),
    ("inv-vol mix, always in", {"exposure": "none", "use_signal": False, "max_weight": NO_CAPS},
     "(e) inverse-vol mix vs 80/15/5"),
    ("+ sleeve caps", {"exposure": "none", "use_signal": False}, "(d) per-sleeve caps"),
    ("+ binary trend filter", {"exposure": "none", "signal_cap": 1e-9}, "trend on/off filter"),
    ("+ partial scaling", {"exposure": "none"}, "(a) signal-strength cash drag"),
    ("+ regime caps (= full)", {}, "(b) regime caps"),
]


def decompose(lab: Lab, start: str | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sequential waterfall from the frictionless benchmark to the full system.
    Each step's annualized log-return gap is split by benchmark phase; the
    'recovery' column is (c) slow re-risking. Returns (waterfall, layer stats)."""
    runs = {n: lab.run(cfg) for n, cfg, _ in DECOMP_LAYERS}
    idx = runs[DECOMP_LAYERS[-1][0]]["returns"].index
    if start:
        idx = idx[idx >= start]
    bm = runs[DECOMP_LAYERS[-1][0]]["bench"].reindex(idx)
    lab_ph = phases(bm)
    yrs = len(idx) / 252
    series = [("static 80/15/5 (frictionless)", bm, None)] + [
        (n, runs[n]["returns"].reindex(idx).fillna(0.0), runs[n]) for n, _, _ in DECOMP_LAYERS]
    rows, stats = [], {}
    for (pn, pr, _), (n, r, res), (_, _, what) in zip(series[:-1], series[1:], DECOMP_LAYERS):
        d = np.log1p(r) - np.log1p(pr)
        row = {"step": what, "layer": n}
        for ph in ["falling", "recovery", "normal"]:
            row[ph] = d[lab_ph == ph].sum() / yrs
        row["total"] = d.sum() / yrs
        rows.append(row)
    for n, r, res in series:
        stats[n] = full_stats(r, bm, lab.rf, res)
    wf = pd.DataFrame(rows).set_index("step")
    tot = {"layer": "full system - benchmark"} | wf[["falling", "recovery", "normal", "total"]].sum().to_dict()
    wf.loc["TOTAL"] = pd.Series(tot)
    return wf, pd.DataFrame(stats).T.reindex(columns=STAT_COLS)


ONE_AT_A_TIME = {
    "full system": {},
    "- regime caps": {"exposure": "none"},
    "- partial scaling (binary)": {"signal_cap": 1e-9},
    "- sleeve caps": {"max_weight": NO_CAPS},
    "80/15/5 base instead of inv-vol": {"base_weights": BENCH},
}


def recovery_table(lab: Lab, res: dict, depth: float = 0.10) -> pd.DataFrame:
    """Per benchmark drawdown episode: recovery return of bench vs strategy and
    how invested the strategy was in the first 3 months off the trough."""
    r, bm = res["returns"], res["bench"]
    w = res["weights"].reindex(r.index)
    exp = w.drop(columns=C.CASH).sum(axis=1)
    rows = []
    for s, t, e in episodes(bm, depth):
        win = slice(t + pd.Timedelta(days=1), e)
        rows.append({"peak": s.date(), "trough": t.date(), "recovered": e.date(),
                     "bench DD": (1 + bm[s:t]).prod() - 1,
                     "strat DD": (1 + r[s:t]).prod() - 1,
                     "bench recov": (1 + bm[win]).prod() - 1,
                     "strat recov": (1 + r[win]).prod() - 1,
                     "exp @trough": exp.asof(t),
                     "avg exp 0-63d": exp[win].iloc[:63].mean(),
                     "days to 80% exp": _days_to(exp[win], 0.8 * exp[:s].iloc[-252:].mean())})
    return pd.DataFrame(rows)


def _days_to(x: pd.Series, level: float):
    hit = np.flatnonzero(x.values >= level)
    return int(hit[0]) if len(hit) else np.nan


# ---------------------------------------------------------------- walk-forward
def _obj_sharpe(r, rf):
    ex = r - rf.reindex(r.index).fillna(0.0)
    return ex.mean() / r.std()


def _obj_calmar(r, rf):
    eq = (1 + r).cumprod()
    cagr = eq.iloc[-1] ** (252 / len(r)) - 1
    return cagr / abs((eq / eq.cummax() - 1).min())


def _obj_cagr_dd20(r, rf):
    """Max CAGR among configs whose training MaxDD is no worse than -20%;
    configs breaching it rank below every compliant one (then by Calmar)."""
    eq = (1 + r).cumprod()
    dd = (eq / eq.cummax() - 1).min()
    cagr = eq.iloc[-1] ** (252 / len(r)) - 1
    return cagr if dd >= -0.20 else -10 + _obj_calmar(r, rf)


OBJECTIVES = {"sharpe": _obj_sharpe, "calmar": _obj_calmar, "cagr_dd20": _obj_cagr_dd20}


def walk_forward(results: dict[str, dict], rf: pd.Series, objective: str = "cagr_dd20",
                 oos_start: int = OOS_START, min_train: int = 756) -> tuple[pd.Series, pd.Series]:
    """Expanding-window selection: at each Jan 1 from `oos_start`, pick the
    config with the best training-window objective and hold it for the year.
    All configs' signals are causal, so slicing full-history runs is valid.
    A switch pays the cost of moving between the two configs' held weights.
    Returns (stitched OOS daily returns, pick per year)."""
    f = OBJECTIVES[objective]
    names = list(results)
    idx = results[names[0]]["returns"].index
    years = sorted({y for y in idx.year if y >= oos_start
                    and (idx < pd.Timestamp(f"{y}-01-01")).sum() >= min_train})
    cost = pd.Series(C.COST_BPS) / 1e4
    pieces, picks, prev = [], {}, None
    for y in years:
        cut = pd.Timestamp(f"{y}-01-01")
        score = {n: f(res["returns"][res["returns"].index < cut], rf) for n, res in results.items()}
        pick = max(names, key=lambda n: (score[n], -names.index(n)))   # ties -> earlier (baseline first)
        r = results[pick]["returns"][str(y)].copy()
        if prev is not None and prev != pick and len(r):
            w0 = results[prev]["weights"].loc[:cut].iloc[-1]
            w1 = results[pick]["weights"].loc[:cut].iloc[-1]
            r.iloc[0] -= float(((w1 - w0).abs() * cost.reindex(w1.index).fillna(0)).sum())
        pieces.append(r)
        picks[y] = pick
        prev = pick
    return pd.concat(pieces), pd.Series(picks, name=objective)


# ---------------------------------------------------------------- lookahead
def lookahead_check(lab: Lab, cfg: dict, n_cuts: int = 5, seed: int = 0, tol: float = 1e-10) -> float:
    """Perturb every price / market input strictly after a cut date; targets
    on or before the cut must not move. Returns the max abs change (0 = pass)."""
    rng = np.random.default_rng(seed)
    base = lab.targets(cfg)
    idx = lab.prices.index
    valid = base.dropna().index
    cuts = pd.DatetimeIndex(rng.choice(valid[300:-50], n_cuts, replace=False)).sort_values()
    worst = 0.0
    for cut in cuts:
        def bump(df):
            f = pd.DataFrame(np.exp(rng.normal(0, 0.05, df.shape)), index=df.index, columns=df.columns)
            f[df.index <= cut] = 1.0
            return df * f.cumprod()
        alt = Lab(bump(lab.prices), None if lab.market is None else bump(lab.market))
        t = alt.targets(cfg)
        d = (t.loc[:cut] - base.loc[:cut]).abs().max().max()
        worst = max(worst, float(np.nan_to_num(d)))
        assert (t.loc[cut:].iloc[1:] - base.loc[cut:].iloc[1:]).abs().max().max() > 0, \
            "perturbation had no effect -- check is vacuous"
    return worst if worst > tol else 0.0
