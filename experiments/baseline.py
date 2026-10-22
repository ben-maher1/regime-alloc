"""Baseline and the reference stand-ins from CLAUDE.md (production config,
momentum only, 200d-MA overlay). No new code; sanity check that the harness
reproduces the documented numbers."""
GRID = {
    "baseline": {},
    "momentum only": {"exposure": "none"},
    "200d-MA overlay": {"exposure": "trend"},
}
