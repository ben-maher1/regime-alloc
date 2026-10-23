# CLAUDE.md: regime-alloc

## What this is
A DIY replacement for a paid ($75/mo) allocation service. It sets daily target weights for **VT, GLDM, IBIT**, with **SGOV** as cash:
1. **Regime layer** (`regime_alloc/regime.py`). Two composite axes (risk appetite, macro pressure) from VIX, MOVE, Baa−10y spread, S&P trend, DXY, copper/gold, breakevens, the 10y yield and the 10y−2y curve. These give 4 regimes, and each regime maps to a total exposure cap.
2. **Momentum sizing** (`signals.py`, `sizing.py`). Score = average rolling Sharpe over 21/63/126/252 days, EWMA-smoothed. A 20-day breakout floor lifts a sleeve's strength to 1 while it is on (new 20d high, until a new 20d low). Weight = inverse-vol baseline × clip(score/0.5, 0, 1), normalized so live sleeves sum to 1, then × regime cap, with per-sleeve caps. The remainder goes to SGOV. (The normalize step and the breakout floor were added by the 2026-10-22 upside-capture study; see EXPERIMENTS.md.)
3. **Execution realism.** Weights decided at close t earn t+1 returns. There's a 10-point rebalance band (5 points before 2026-10-23) and per-asset cost bps.

All parameters live in `regime_alloc/config.py`.

The owner (Ben) is comfortable with quant concepts: vectorized backtests, walk-forward testing, EWMA vol, lookahead and survivorship bias. Be direct and skip the basics.

## Running
- `FRED_API_KEY` must be set in the environment. Never write it into a tracked file.
- `python run_backtest.py` runs the full system. `--no-regime` and `--trend-overlay` run comparisons.
- `python run_daily.py [--holdings holdings.json]` prints today's report. This is what production runs.
- `python run_research.py {diagnose|grid|lookahead|frontier} [family ...]` is the research harness: walk-forward, capture ratios, gap decomposition and the lookahead check. Lever grids live in `experiments/<family>.py`, and output goes to `research_results/`.
- Data comes from Yahoo (yfinance) and FRED, cached in `data_cache/` (gitignored). Use `--refresh` to re-download.

## Baseline (2004-10 → 2026-10, in-sample)
| | CAGR | Vol | Sharpe | MaxDD |
|---|---|---|---|---|
| Full system (normalize + 20d breakout, 10-pt band) | 13.4% | 11.2% | 1.06 | −18.3% |
| Static 60/30/10 (VT/GLDM/IBIT, daily, no costs) | 12.3% | 15.6% | 0.75 | −41.1% |
| Pre-study system (`{}` in the research harness) | 9.7% | 8.7% | 0.96 | −11.7% |
| Momentum only | 10.0% | 10.0% | 0.88 | −18.7% |
| 200d-MA overlay | 9.9% | 9.1% | 0.95 | −12.6% |
| VT buy&hold | 7.9% | 19.1% | 0.43 | −58.6% |

Known findings:
- The risk axis does the work. The macro-pressure axis did not help exposure or tilts, so it's kept for labels only.
- Sharpe is flat (0.91–0.98) across smoothing ∈ {2,5,10,20} × deadband ∈ {0, .15, .3}. No single indicator dominates in ablation.
- The pre-study system made about 30 rebalances a year and lagged in V-shaped recoveries (2009, 2012, 2019, 2023, 2026 YTD). The breakout floor fixed most of that. The current system trades on about 14 days a year (22 with the old 5-point band, at equal performance), and its MaxDD (Aug 2011–Jul 2012) sits about 2 points inside the −20% limit. VT/GLDM caps are the drawdown dial (EXPERIMENTS.md, caps family).
- Against static 60/30/10, which is close to the system's own average mix, the timing adds roughly 0–0.7%/yr of return but cuts vol by a third and MaxDD by a third to a half. Treat it as a drawdown-control overlay: return-raising levers converge toward 60/30/10, so judge new ideas against it (it's a row in every harness stats table).
- In the research harness, `{}` is the pre-study system and configs without `band` use 0.05 (`PRE_STUDY_BAND`); `PRODUCTION` is current config.py.
- The momentum-only and 200d-MA rows above are pre-study variants.
- ICE HY OAS on FRED only covers 3 years, which is why Baa10Y is used for credit.

## Rules for autonomous research
- **Production is `main`.** Do experiments on branches. Merge only with Ben's approval, and never change `run_daily.py` behavior silently.
- **Log every experiment** in `EXPERIMENTS.md`: hypothesis, change, results table vs baseline, verdict. Include failures.
- **Guard against overfitting.** Prefer walk-forward or out-of-sample evidence. Favor flat parameter regions and round numbers. Report a grid rather than just its best cell. Treat Sharpe differences under ~0.05 as noise.
- **No lookahead.** Any new feature must use data through close t only. Re-run the lookahead check (perturb future prices; earlier targets must not change) after touching signal code.
- **No live trading** without explicit approval. Any Alpaca integration stays in "recommend, human approves" mode.

## Research backlog (rough priority)
1. Walk-forward validation harness: expanding-window refits of the key params, and an out-of-sample stats table.
2. A daily log (`logs/signals.csv`) of regime, axes and targets, for side-by-side comparison with the paid service.
3. Dropping the 21d lookback. (Risk-off caps and weekly-vs-daily cadence are done: see EXPERIMENTS.md.)
4. Faster re-risking after V-shaped recoveries, e.g. a lower deadband for risk-on flips only. Watch for overfit.
5. Optional Alpaca module that generates orders for approval.
