"""Lever family (d, revisited): per-sleeve max allocations on the candidate configs.

Hypothesis: in production the caps (VT 1.0 / GLDM 0.6 / IBIT 0.2) can't bind
because w <= inverse-vol base (diagnose: (d) ~ 0). Once `normalize` scales a
lone live sleeve toward 100%, they bind often, and whatever they clip goes to
SGOV. Raising GLDM/IBIT caps should buy CAGR at a drawdown cost; lowering them
(or capping VT) should trade the other way. Clipped weight still goes to cash.

Bases (round-number settings of the levers that passed walk-forward):
  bo20         SIGNAL_CAP 0.5 + 20d breakout floor -> full (the Sharpe pick)
  norm.25+bo20 normalize, SIGNAL_CAP 0.25, + bo20 (the CAGR pick)
  norm.5+bo20  normalize at production SIGNAL_CAP 0.5, + bo20 (one fewer change)
Caps, full cross per base:
  VT    1.0 (base) / 0.8
  GLDM  0.4 / 0.6 (base) / 0.8 / 1.0
  IBIT  0.1 / 0.2 (base) / 0.3 / 0.4

Bias warning: IBIT's proxy is BTC-USD from 2014. Any in-sample gain from a
higher IBIT cap is mostly bitcoin's 2015-2021 run; weigh the WF rows, not the cells.
"""
BO20 = {"breakout_high": 20, "breakout_strength": 1.0}
BASES = {
    "bo20": {**BO20},
    "norm.25+bo20": {"redistribute": "normalize", "signal_cap": 0.25, **BO20},
    "norm.5+bo20": {"redistribute": "normalize", **BO20},
}
GRID = {"baseline": {}}
for bn, b in BASES.items():
    for vt in [1.0, 0.8]:
        for g in [0.4, 0.6, 0.8, 1.0]:
            for i in [0.1, 0.2, 0.3, 0.4]:
                GRID[f"{bn} VT{vt:g} G{g:g} I{i:g}"] = {**b, "max_weight": {"VT": vt, "GLDM": g, "IBIT": i}}
