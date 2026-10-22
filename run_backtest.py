"""Backtest the full system (regime overlay + momentum sizing).

    python run_backtest.py                 # real data, regime model (needs FRED_API_KEY)
    python run_backtest.py --no-regime     # momentum + sizing only
    python run_backtest.py --trend-overlay # 200d-MA exposure stand-in instead of the regime model
    python run_backtest.py --synthetic     # offline smoke test (no regime)
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from regime_alloc import config as C
from regime_alloc.backtest import benchmark, build_targets, run, stats, turnover_stats
from regime_alloc.data import load_asset_prices, load_market_data, synthetic_prices
from regime_alloc.regime import compute_regime, regime_exposure, trend_filter_exposure

ap = argparse.ArgumentParser()
ap.add_argument("--synthetic", action="store_true")
ap.add_argument("--trend-overlay", action="store_true")
ap.add_argument("--no-regime", action="store_true")
ap.add_argument("--refresh", action="store_true", help="re-download data")
ap.add_argument("--out", default="results")
args = ap.parse_args()
out = Path(args.out); out.mkdir(exist_ok=True)

prices = synthetic_prices() if args.synthetic else load_asset_prices(refresh=args.refresh)
reg = None
if args.trend_overlay:
    exposure = trend_filter_exposure(prices["VT"])
elif args.no_regime or args.synthetic:
    exposure = None
else:
    reg = compute_regime(load_market_data(refresh=args.refresh)).reindex(prices.index).ffill()
    exposure = regime_exposure(reg)
    reg.to_csv(out / "regime.csv")

res = run(prices, build_targets(prices, exposure))
r = res["returns"]
rf = prices[C.CASH].pct_change()

bm = {
    "Strategy": r,
    "VT buy&hold": benchmark(prices, {"VT": 1.0}, r.index),
    "Static 80/15/5": benchmark(prices, {"VT": .80, "GLDM": .15, "IBIT": .05}, r.index),
}
table = pd.DataFrame({k: stats(v, rf, k) for k, v in bm.items()}).T

pd.set_option("display.float_format", "{:,.3f}".format)
print(f"\nPeriod: {r.index[0].date()} -> {r.index[-1].date()}\n")
print(table)
print("\n", turnover_stats(res).to_string(), "\n")
table.to_csv(out / "stats.csv")
res["weights"].to_csv(out / "weights.csv")

n = 3 if reg is not None else 2
fig, ax = plt.subplots(n, 1, figsize=(11, 3.2 * n + 1), sharex=True,
                       gridspec_kw={"height_ratios": [2, 1, 0.5][:n]})
for k, v in bm.items():
    (1 + v).cumprod().plot(ax=ax[0], label=k, logy=True)
ax[0].legend(); ax[0].set_title("Growth of $1 (log)")
res["weights"].loc[r.index].clip(lower=0).plot.area(ax=ax[1], linewidth=0)
ax[1].set_ylim(0, 1); ax[1].set_title("Held weights"); ax[1].legend(loc="upper left", ncol=4)
if reg is not None:
    colors = {1: "#3a9d5d", 2: "#9fc65a", 3: "#e3a33b", 4: "#c8483f"}
    rr = reg["regime"].loc[r.index]
    for k, c in colors.items():
        ax[2].fill_between(rr.index, 0, 1, where=(rr == k), color=c, step="post",
                           label=C.REGIME_NAMES[k], linewidth=0)
    ax[2].set_yticks([]); ax[2].set_title("Regime")
    ax[2].legend(loc="upper left", ncol=4, fontsize=8)
plt.tight_layout(); plt.savefig(out / "backtest.png", dpi=120)
print(f"Saved results to {out}/")
