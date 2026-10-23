"""Lever family: rebalance cadence and band, on the current production system.

Hypothesis: about 22 trades a year includes a lot of churn (2023: 36 trades,
several gold in-out-in round trips). Deciding less often, or only trading when
a sleeve drifts further from target, should cut turnover at no cost to
CAGR/Sharpe/MaxDD. The exploratory check vs 60/30/10 (EXPERIMENTS.md
2026-10-23) suggested weekly or a 10-point band do this; this is the
walk-forward test. "baseline" here is PRODUCTION (daily, 5-point band), not
the pre-study system.

Grid (production signals throughout):
  daily     band 0.05 (production) / 0.075 / 0.10 / 0.15
  weekly    band 0.05 / 0.075 / 0.10   (targets updated on Fridays only)
  monthly   band 0.05                  (context: how far can cadence go?)
"""
from regime_alloc.research import PRODUCTION

GRID = {"baseline": {**PRODUCTION}}
for b in [0.075, 0.10, 0.15]:
    GRID[f"daily band {b:g}"] = {**PRODUCTION, "band": b}
for b in [0.05, 0.075, 0.10]:
    GRID[f"weekly band {b:g}"] = {**PRODUCTION, "rebalance": "weekly", "band": b}
GRID["monthly band 0.05"] = {**PRODUCTION, "rebalance": "monthly", "band": 0.05}
