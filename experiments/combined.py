"""Cross-family factorial for the CAGR-vs-MaxDD frontier.

Each family's grid shows where its own lever is flat. This crosses the
plausible settings of each lever (round numbers, not best cells) so the
interactions show up: e.g. does a breakout floor still help once the cash drag
is gone, and do the regime caps still pay for themselves under a vol target?

  sizing   cap 0.5 (base) / cap 0.25 / binary / normalize cap 0.25 / vol target 12% binary
  regime   risk-off 0.5 symmetric (base) / risk-off 0.75 with risk-on flip at 0
  reentry  none / 20d breakout -> full strength
"""
SIZING = {
    "cap.5": {},
    "cap.25": {"signal_cap": 0.25},
    "binary": {"signal_cap": 1e-9},
    "norm.25": {"redistribute": "normalize", "signal_cap": 0.25},
    "tv12": {"port_vol_target": 0.12, "signal_cap": 1e-9},
}
REGIME = {
    "off.5": {},
    "off.75/up0": {"regime_exposure": {1: 1.0, 2: 1.0, 3: 0.75, 4: 0.75}, "regime_band_up": 0.0},
}
REENTRY = {
    "": {},
    "+bo20": {"breakout_high": 20, "breakout_strength": 1.0},
}
GRID = {"baseline": {}}
for sn, s in SIZING.items():
    for rn, r in REGIME.items():
        for en, e in REENTRY.items():
            name = f"{sn} {rn}{en}"
            if not (s or r or e):
                continue
            GRID[name] = {**s, **r, **e}
