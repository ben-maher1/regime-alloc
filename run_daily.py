"""Daily signal report: regime, momentum scores, target weights, and trades.

    python run_daily.py                       # report only
    python run_daily.py --holdings holdings.json

holdings.json (current weights, any subset; missing = 0), e.g.
    {"VT": 0.62, "GLDM": 0.18, "IBIT": 0.05, "SGOV": 0.15}

Needs FRED_API_KEY in the environment. Output is plain text so it can be
piped to email / Slack / ntfy from cron or GitHub Actions.
"""
import argparse
import json

import pandas as pd

from regime_alloc import config as C
from regime_alloc.backtest import build_targets
from regime_alloc.data import load_asset_prices, load_market_data
from regime_alloc.regime import (PRESSURE_FEATURES, RISK_FEATURES, compute_regime,
                                 regime_exposure)
from regime_alloc.signals import ewma_vol, vol_adjusted_momentum

ap = argparse.ArgumentParser()
ap.add_argument("--holdings")
args = ap.parse_args()

prices = load_asset_prices(refresh=True)
reg = compute_regime(load_market_data(refresh=True)).reindex(prices.index).ffill()
exposure = regime_exposure(reg)
risky = list(C.ASSETS)
score = vol_adjusted_momentum(prices[risky]).iloc[-1]
vol = ewma_vol(prices[risky]).iloc[-1]
target = build_targets(prices, exposure).iloc[-1]
today = reg.iloc[-1]
rid = int(today["regime"])
asof = prices.index[-1].date()

# regime history: how long in this regime, what it was before
r = reg["regime"].dropna()
spell = (r != r.shift()).cumsum()
days_in = int((spell == spell.iloc[-1]).sum())
prev = r[spell < spell.iloc[-1]]
prev_txt = C.REGIME_NAMES[int(prev.iloc[-1])] if len(prev) else "n/a"

L = [f"Allocation signal as of {asof}", "",
     f"REGIME: {rid} {C.REGIME_NAMES[rid]}  ->  exposure cap {exposure.iloc[-1]:.0%}",
     f"  in regime {days_in} trading days (previous: {prev_txt})",
     f"  risk appetite {today['risk']:+.2f}   macro pressure {today['pressure']:+.2f}"
     f"   (flip at +/-{C.REGIME_DEADBAND})",
     "  risk:     " + "  ".join(f"{k} {today[k]:+.1f}" for k in RISK_FEATURES),
     "  pressure: " + "  ".join(f"{k} {today[k]:+.1f}" for k in PRESSURE_FEATURES),
     "", f"{'Asset':6} {'Score':>7} {'Vol':>7} {'Target':>8}"]
for a in risky:
    L.append(f"{a:6} {score[a]:7.2f} {vol[a]:7.1%} {target[a]:8.1%}")
L.append(f"{C.CASH:6} {'':7} {'':7} {target[C.CASH]:8.1%}")

if args.holdings:
    cur = pd.Series(json.load(open(args.holdings))).reindex(target.index).fillna(0.0)
    diff = target - cur
    trade = diff.abs().max() > C.REBALANCE_BAND
    L += ["", f"Rebalance needed: {'YES' if trade else 'no'} (band {C.REBALANCE_BAND:.0%})"]
    if trade:
        for a, d in diff.items():
            if abs(d) > 1e-4:
                L.append(f"  {'BUY ' if d > 0 else 'SELL'} {a:5} {abs(d):6.1%} of portfolio")

print("\n".join(L))
