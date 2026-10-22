"""Lever family (a/d alt): portfolio vol target instead of per-sleeve partial sizing,
plus the per-sleeve caps (d), which only bind once weight is scaled up.

Hypothesis: partial strengths (score/0.5) leave cash even when the whole book's
risk is low. Normalizing base x strength to a fully-invested shape and sizing the
book to a 10-15% vol target (never above the regime cap, no leverage) should
invest more in calm uptrends and de-risk on its own when vol spikes, so
upside capture rises without giving back the drawdown control.

Grid (regime caps on unless noted):
  target vol   0.10 / 0.12 / 0.15
  x shape      binary (score > 0 -> full base) / scaled (SIGNAL_CAP 0.5)
  caps         IBIT 0.3 / GLDM 0.8 and IBIT 0.4 / GLDM 1.0 at 12% binary
  no regime    12% binary with exposure "none"
"""
GRID = {"baseline": {}}
for tv in [0.10, 0.12, 0.15]:
    GRID[f"tv {tv:.0%} binary"] = {"port_vol_target": tv, "signal_cap": 1e-9}
    GRID[f"tv {tv:.0%} scaled"] = {"port_vol_target": tv}
GRID["tv 12% binary, IBIT .3 GLDM .8"] = {"port_vol_target": 0.12, "signal_cap": 1e-9,
                                         "max_weight": {"VT": 1.0, "GLDM": 0.8, "IBIT": 0.3}}
GRID["tv 12% binary, IBIT .4 GLDM 1"] = {"port_vol_target": 0.12, "signal_cap": 1e-9,
                                        "max_weight": {"VT": 1.0, "GLDM": 1.0, "IBIT": 0.4}}
GRID["tv 12% binary, no regime"] = {"port_vol_target": 0.12, "signal_cap": 1e-9, "exposure": "none"}
