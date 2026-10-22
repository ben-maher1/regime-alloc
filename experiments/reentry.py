"""Lever family (c): slow re-risking after drawdowns.

Hypothesis: after a V-bottom the 126/252d horizons stay negative for months,
and the EWMA(10) smoothing adds more lag, so the sleeve sits in cash through
the steepest part of the rebound. A fast component that only *adds* exposure
(a Donchian breakout floor) should recover the rebound and leave crash
behaviour alone. A symmetric fast blend also re-risks sooner but whipsaws more.

Grid (all with regime caps on):
  breakout floor   new 20d / 50d high -> strength >= 0.5 / 1.0, until new 20d / 50d low
  fast blend       a = 0.25 / 0.5 of a 10/20d vol-adjusted score (EWMA hl 3)
  score smoothing  EWMA halflife 5 / 2 (vs 10)
"""
GRID = {"baseline": {}}
for n in [20, 50]:
    for s in [0.5, 1.0]:
        GRID[f"breakout {n}d -> {s}"] = {"breakout_high": n, "breakout_strength": s}
for a in [0.25, 0.5]:
    GRID[f"fast blend {a}"] = {"fast_weight": a}
for h in [5, 2]:
    GRID[f"smoothing {h}"] = {"smoothing": h}
