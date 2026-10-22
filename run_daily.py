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
from regime_alloc.backtest import build_targets, run
from regime_alloc.data import load_asset_prices, load_market_data
from regime_alloc.regime import (PRESSURE_FEATURES, RISK_FEATURES, compute_regime,
                                 regime_exposure)
from regime_alloc.signals import breakout_state, ewma_vol, vol_adjusted_momentum

ap = argparse.ArgumentParser()
ap.add_argument("--holdings")
args = ap.parse_args()

prices = load_asset_prices(refresh=True)
reg = compute_regime(load_market_data(refresh=True)).reindex(prices.index).ffill()
exposure = regime_exposure(reg)
risky = list(C.ASSETS)
score = vol_adjusted_momentum(prices[risky]).iloc[-1]
vol = ewma_vol(prices[risky]).iloc[-1]
# breakout floor on (new N-day high, no new N-day low since) -> strength >= BREAKOUT_STRENGTH
brk = (breakout_state(prices[risky], C.BREAKOUT_HIGH).iloc[-1].astype(bool) if C.BREAKOUT_HIGH
       else pd.Series(False, index=risky))
lifted = brk & (score < C.BREAKOUT_STRENGTH * C.SIGNAL_CAP)
targets = build_targets(prices, exposure)
target = targets.iloc[-1]
# model portfolio: follow the targets since inception with the rebalance band
model = run(prices, targets.dropna())
held, held_prev = model["weights"].iloc[-1], model["weights"].iloc[-2]
rebal_today = model["trades"].iloc[-1].abs().max() > 1e-9
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
     "", f"SIZING: redistribute={C.REDISTRIBUTE}, breakout floor {C.BREAKOUT_HIGH}d high"
     f" -> strength {C.BREAKOUT_STRENGTH:g}",
     "", f"{'Asset':6} {'Score':>7} {'Vol':>7} {'Brkout':>7} {'Target':>8}"]
for a in risky:
    tag = "  <- held up by breakout floor" if lifted[a] else ""
    L.append(f"{a:6} {score[a]:7.2f} {vol[a]:7.1%} {'on' if brk[a] else 'off':>7} {target[a]:8.1%}{tag}")
L.append(f"{C.CASH:6} {'':7} {'':7} {'':7} {target[C.CASH]:8.1%}")

# change vs previous close: alert on a model rebalance (some sleeve > band from target) or a regime flip
regime_flip = days_in == 1
L += ["", f"ALERT: {'YES' if rebal_today or regime_flip else 'no'}"
      f"  (model rebalance today: {'YES' if rebal_today else 'no'}, regime change today:"
      f" {'YES' if regime_flip else 'no'})",
      f"{'Asset':6} {'Held prev':>10} {'Held now':>9} {'Change':>8}"]
for a in held.index:
    L.append(f"{a:6} {held_prev[a]:10.1%} {held[a]:9.1%} {held[a] - held_prev[a]:+8.1%}")

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
