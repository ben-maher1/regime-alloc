# regime-alloc

DIY version of a regime + volatility-adjusted momentum allocator for VT / GLDM / IBIT, with SGOV as cash.

**Status:** Phases 1 and 2 are done: the regime overlay, momentum sizing, the backtest and the daily report. You need a free `FRED_API_KEY` set as an environment variable.

## Pipeline

```
prices ──► signals.vol_adjusted_momentum ──► sizing.signal_strength ─┐
       └─► signals.ewma_vol ──► inverse-vol baseline ────────────────┼─► target weights ─► rebalance band ─► held weights
regime.py ──► total exposure cap (0–1) ──────────────────────────────┘                        (cash = remainder)
```

- **Score:** for each of 21/63/126/252 days, compute annualized mean log return ÷ annualized vol (a rolling Sharpe). Average the horizons, then EWMA-smooth the result (halflife 10).
- **Sizing:** inverse-EWMA-vol baseline × clip(score / 0.5, 0, 1) × regime exposure, subject to per-sleeve caps (IBIT ≤ 20%, GLDM ≤ 60%).
- **Timing:** a weight decided at close *t* earns the *t+1* return. Costs are charged on traded notional. A sleeve only trades when it drifts more than 5 points from target.
- **History:** proxies are spliced in before each ETF existed (GLD→GLDM, BTC-USD→IBIT, ACWI/SPY→VT, BIL→SGOV).

All parameters live in `regime_alloc/config.py`.

## Run

```bash
pip install -r requirements.txt
python run_backtest.py                  # real data -> results/ (stats.csv, weights.csv, backtest.png)
python run_backtest.py --trend-overlay  # with the 200d-MA exposure stand-in
python run_backtest.py --synthetic      # offline smoke test (fake data; numbers are meaningless)
python run_daily.py --holdings holdings.json
```

The first real run downloads and caches data in `data_cache/`. Use `--refresh` to re-download.

## Daily email via GitHub Actions

1. Push the repo to GitHub (private).
2. Add repo secrets: `MAIL_USERNAME`, `MAIL_PASSWORD` (a Gmail app password), `MAIL_TO`, and `FRED_API_KEY` (free; needed in phase 2).
3. Optionally commit `holdings.json` with your current weights to get trade lines in the email.

The workflow in `.github/workflows/daily.yml` runs on weekday evenings. You can also trigger it manually from the Actions tab.

## Things to check on real data

- Rebalances per year and turnover. If it's too twitchy, raise `SCORE_SMOOTHING` or `REBALANCE_BAND`, or drop the 21-day horizon.
- Average risky exposure. The signal-strength scaling keeps a lot in cash by design. Lower `SIGNAL_CAP` to invest more aggressively when trends are clear.
- Results with `SKIP_DAYS=21` versus 0.
- Sensitivity. Prefer parameter regions that are flat over sharp peaks, and walk-forward test before trusting anything.

## Regime layer (`regime.py`)

The model builds two composite axes, each an average of clipped 3-year rolling z-scores:

- **Risk appetite:** VIX, MOVE, the 63-day change in the Baa−10y credit spread, the S&P versus its 200-day MA, and the 63-day dollar change.
- **Macro pressure:** the 63-day changes in copper/gold, 10y breakevens, the 10y yield and the 10y−2y curve.

Each axis is EWMA-smoothed (halflife 5). Its sign is sticky: it only flips after crossing ±0.15. The two signs give four regimes: Goldilocks, Reflation, Slowdown and Stagflation. `REGIME_EXPOSURE` maps each regime to a cap, currently 100/100/50/50.

FRED's ICE high-yield OAS series now only covers 3 years, so the Moody's Baa−10y spread (from 1986) stands in for credit.
