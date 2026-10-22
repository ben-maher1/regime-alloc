"""Lever family (a): cash drag from signal-strength scaling.

Hypothesis: clip(score/0.5, 0, 1) leaves a lot of a positive-trend sleeve's
baseline in cash (a rolling Sharpe of 0.25 is a decent trend but gets only
half weight). Lowering SIGNAL_CAP, flooring strength for positive-trend
sleeves, or re-spreading unused weight across live sleeves instead of to
SGOV should lift upside capture. The regime caps stay on, so drawdown
protection should mostly survive.

Grid (all with regime caps 1/1/.5/.5):
  SIGNAL_CAP          0.5 (base) / 0.35 / 0.25 / 0.1 / binary (score > 0 -> full)
  strength floor      0.25 / 0.5 / 1.0 when close > 200d SMA, at cap 0.5
                      0.5 when score > 0 (alone; same as cap 0.25 on [0, .25])
  redistribute        "zero" (dead sleeves' baseline -> live sleeves) and
                      "normalize" (risky sums to 1 when anything is on), at cap 0.5 / 0.25
"""
GRID = {"baseline": {}}
for c in [0.35, 0.25, 0.1]:
    GRID[f"cap {c}"] = {"signal_cap": c}
GRID["binary"] = {"signal_cap": 1e-9}
for f in [0.25, 0.5, 1.0]:
    GRID[f"floor {f} >200d"] = {"strength_floor": f, "floor_trend": 200}
GRID["floor 0.5 score>0"] = {"strength_floor": 0.5, "floor_trend": "score"}
for mode in ["zero", "normalize"]:
    for c in [0.5, 0.25]:
        GRID[f"{mode} cap {c}"] = {"redistribute": mode, "signal_cap": c}
