"""Lever family (b): regime caps and re-risking speed of the regime layer.

Hypothesis: the risk-off cap (0.5) costs upside mainly *after* the risk axis
has turned up but before it clears +0.15. Raising the risk-off cap or making
the deadband asymmetric (flip back to risk-on sooner) should recover V-shaped
rebounds; going faster risk-off is not touched, so crash protection is kept.

Grid:
  risk-off cap (regimes 3/4)   0.25 / 0.5 (base) / 0.75 / 1.0 (= regime off)
  × risk-on flip band          0.15 (symmetric, base) / 0.05 / 0.0  (risk-off band stays 0.15)
  + regime EWMA halflife 2 (vs 5) at cap 0.5, symmetric and band_up 0
"""
GRID = {"baseline": {}}
for cap in [0.25, 0.5, 0.75, 1.0]:
    for up in [0.15, 0.05, 0.0]:
        if cap == 0.5 and up == 0.15:
            continue
        cfg = {"regime_exposure": {1: 1.0, 2: 1.0, 3: cap, 4: cap}}
        if up != 0.15:
            cfg["regime_band_up"] = up
        if cap == 1.0 and up != 0.15:
            continue                      # band irrelevant when both sides are 1.0
        GRID[f"off {cap} / up {up}"] = cfg
GRID["hl 2 / up 0.15"] = {"regime_smoothing": 2}
GRID["hl 2 / up 0.0"] = {"regime_smoothing": 2, "regime_band_up": 0.0}
