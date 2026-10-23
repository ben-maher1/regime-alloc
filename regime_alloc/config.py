"""Central configuration. Edit here, not in the modules."""

# Tradable sleeves. `proxy` is spliced in before the live ticker existed so the
# backtest has more history (returns are chained, not prices).
ASSETS = {
    "VT":   {"proxy": "ACWI"},     # VT/ACWI both start 2008 -- SPY fallback below
    "GLDM": {"proxy": "GLD"},      # GLDM from 2018; GLD from 2004
    "IBIT": {"proxy": "BTC-USD"},  # IBIT from 2024; BTC-USD from 2014
}
EXTRA_PROXY = {"VT": "SPY"}        # second-level fallback for the deepest history

CASH = "CASH"                      # where un-invested capital sits: a cash balance, not a fund
CASH_RATE_SERIES = "DFF"           # FRED daily effective fed funds rate (%)
CASH_RATE_SPREAD = 0.0030          # cash earns fed funds minus 30bp, floored at 0, accrued act/360
                                   # (SGOV, proxied by BIL, before 2026-10-23)

# Regime-model inputs (used in the next phase; fetched now so the cache is warm)
MARKET_TICKERS = ["^VIX", "^MOVE", "DX-Y.NYB", "HYG", "LQD", "HG=F", "GC=F", "^GSPC"]
FRED_SERIES = {
    "DGS10": "ust10y",
    "DGS2": "ust2y",
    "BAA10Y": "baa_spread",       # Moody's Baa - 10y; ICE HY OAS on FRED only goes back 3 yrs
    "T10YIE": "breakeven10y",
}

START = "2004-01-01"
MARKET_START = "1998-01-01"        # extra history so regime z-scores are warm by 2004
CACHE_DIR = "data_cache"

# ---- Momentum signal ----
# Lookbacks in trading days; each horizon's return is divided by its own
# realized vol, then horizons are averaged (equal weight by default).
LOOKBACKS = [21, 63, 126, 252]
LOOKBACK_WEIGHTS = None            # None = equal weight
SKIP_DAYS = 0                      # set 21 for classic 12-1 style skip
SCORE_SMOOTHING = 10               # EWMA halflife (days) on the final score; cuts whipsaw. None = off
VOL_HALFLIFE = 30                  # EWMA halflife (days) for sizing vol
ANNUALIZATION = {"VT": 252, "GLDM": 252, "IBIT": 252}  # BTC proxy is resampled to business days

# ---- Sizing ----
SIGNAL_FLOOR = 0.0                 # score <= floor -> 0 weight
SIGNAL_CAP = 0.5                   # score >= cap -> full baseline weight (score is a rolling Sharpe)
REDISTRIBUTE = "normalize"         # scale live sleeves so risky weights sum to 1 (then regime cap); None = rest to cash
BREAKOUT_HIGH = 20                 # re-entry floor: close at a new N-day high -> strength >= BREAKOUT_STRENGTH
BREAKOUT_STRENGTH = 1.0            #   until a close at a new N-day low; None disables (EXPERIMENTS.md 2026-10-22)
MAX_WEIGHT = {"VT": 1.0, "GLDM": 0.6, "IBIT": 0.2}
TARGET_VOL = None                  # e.g. 0.12 for portfolio vol targeting; None = off
REBALANCE_BAND = 0.10              # only trade a sleeve if |target - current| > band (0.05 before 2026-10-23; EXPERIMENTS.md cadence family)

# ---- Costs ----
COST_BPS = {"VT": 3, "GLDM": 3, "IBIT": 5, "CASH": 0}

# ---- Regime model ----
Z_WINDOW = 756                     # rolling window (days) for standardizing indicators
Z_MIN = 252
Z_CLIP = 3.0
CHANGE_DAYS = 63                   # lookback for "change" indicators
REGIME_SMOOTHING = 5               # EWMA halflife on the two composite axes
REGIME_DEADBAND = 0.15             # an axis only flips sign after crossing +/- this
# 1 Goldilocks (risk-on, disinflationary)   2 Reflation (risk-on, inflationary)
# 3 Slowdown (risk-off, disinflationary)    4 Stagflation/tightening (risk-off, inflationary)
REGIME_EXPOSURE = {1: 1.0, 2: 1.0, 3: 0.5, 4: 0.5}
REGIME_NAMES = {1: "Goldilocks", 2: "Reflation", 3: "Slowdown", 4: "Stagflation"}
