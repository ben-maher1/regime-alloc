# Experiments log

Every experiment gets: hypothesis, change, results vs baseline, verdict. Failures included.

---

## 2026-10-22 · Upside-capture study: harness and method

**Goal.** Raise upside capture vs static 80/15/5 (monthly) materially above baseline, with
walk-forward CAGR ≥ 11%, MaxDD no worse than −20%, and Sharpe no more than ~0.1 below baseline.
No leverage.

> **Data status: NOT RUN ON REAL DATA YET.** The cloud session that built this could not reach
> Yahoo (`query1/query2.finance.yahoo.com`) or FRED (`fred.stlouisfed.org`); the egress proxy
> refused both. `FRED_API_KEY` was also unset and `data_cache/` was empty. Everything below was
> built and smoke-tested on `--synthetic` data only. Synthetic numbers mean nothing and are
> deliberately **not** recorded here. Each "Results" section says *pending* until it has been
> run on real data. To fill them in:
>
> ```bash
> export FRED_API_KEY=...
> python run_research.py grid baseline        # 1. must reproduce the CLAUDE.md baseline table
> python run_research.py diagnose             # 2. gap decomposition
> python run_research.py lookahead all        # 3. must print ALL PASS
> python run_research.py grid all             # 4. every lever family's grid and walk-forward
> python run_research.py frontier all         # 5. CAGR vs MaxDD frontier
> ```
>
> Output goes to `research_results/*.md` and `*.csv`. These are tracked so they can be reviewed.

### Harness (`regime_alloc/research.py`, `run_research.py`, `experiments/`)

- **Config-driven runs.** A run is a flat dict: `exposure` ∈ {regime, none, trend}, `regime_*`,
  `band`, plus any `build_targets(params=...)` key. `{}` is production. The production code path
  is unchanged. `build_targets(prices, exposure)` with no `params` gives bit-identical targets to
  `main`; this was checked on synthetic data with and without the trend overlay.
- **Metrics.** CAGR, vol, Sharpe (excess over SGOV/BIL), MaxDD, Calmar, **monthly geometric
  up/down capture vs static 80/15/5** (daily-rebalanced, frictionless, same as
  `run_backtest.py`), average risky exposure and rebalances per year. Per-year returns are
  reported for the lag years 2009, 2012, 2019, 2023 and 2026 YTD.
- **Walk-forward.** Each lever family's grid is run over the full history. All signals are
  causal, so slicing full-history runs is valid; the lookahead check enforces this. Every Jan 1
  from 2010, the cell that scores best on the expanding training window (start → Dec 31 of the
  prior year) is held for the next year. Out-of-sample years are stitched together. A switch
  pays costs on the gap between the two configs' held weights. Three selection objectives are
  reported: `sharpe`, `calmar`, and `cagr_dd20` (max CAGR among cells whose training MaxDD is
  ≥ −20%, otherwise by Calmar). Reporting all three keeps the result from depending on the
  objective. Fixed grid cells are reported over the same 2010+ window next to the WF rows.
  - Caveat: the baseline parameters themselves were picked in-sample on 2004–2026, so
    "baseline over 2010+" is a sub-period, not a true OOS number. The `WF[...]` rows are the
    honest ones.
- **Decomposition (`diagnose`).** A sequential waterfall from the frictionless benchmark to the
  full system. Each step's annualized log-return gap is split by benchmark phase: *falling*
  (peak → trough of a >10% benchmark drawdown), *recovery* (trough → regained peak) and
  *normal*. Phase labels use hindsight and are only for diagnosis.

  | step | what it isolates |
  |---|---|
  | 80/15/5 + band/costs | friction |
  | inverse-vol mix, always invested | (e) mix difference vs 80/15/5 (not in the brief, but likely large: inv-vol puts roughly half in GLDM) |
  | + per-sleeve caps | (d) |
  | + binary trend filter (score > 0 → full base weight) | on/off trend filter |
  | + partial scaling (SIGNAL_CAP 0.5) | (a) signal-strength cash drag |
  | + regime caps | (b) → full system |
  | *recovery* column, summed | (c) slow re-risking |

  There's also a one-at-a-time removal table from the full system (checks interaction effects)
  and a per-episode re-risking table: exposure at the trough, average exposure in the first
  63 days, and days to get back to 80% of pre-episode exposure.
- **Lookahead check.** `lookahead_check` multiplies every price and market input after a random
  cut date by a random-walk factor and asserts that targets on or before the cut are unchanged
  (5 cuts per config). It also asserts the perturbation does move later targets, so the check
  can't pass vacuously. `run_research.py lookahead all` runs it on every config in every family.
  It passes on synthetic data for the baseline family.

### Diagnosis results

*Pending a real-data run.* Paste `research_results/diagnose.md` tables here with a verdict on
which of (a)–(e) is the biggest source.

---

## 2026-10-22 · Lever family (c): faster re-entry · branch `claude/kind-mendel-krlcu2-reentry`

**Hypothesis.** After a V-bottom the 126d and 252d horizons stay negative for months, and the
EWMA(10) score smoothing adds more lag, so sleeves sit in SGOV through the steepest part of
the rebound. A fast component that only *adds* exposure (a Donchian breakout floor) should
recover the rebound and leave crash behavior alone. A symmetric fast blend also re-risks
sooner but should whipsaw more, so watch rebalances per year.

**Change.** `signals.breakout_state()`, a Donchian on/off state: on at a new N-day high and
off at a new N-day low, using closes through t. `signals.reentry_score()` works at the score
level, so sizing is untouched: (i) while a breakout is on, the score is lifted to at least
`breakout_strength × SIGNAL_CAP`; (ii) or the score is blended with a 10/20d vol-adjusted score
(EWMA hl 3). `experiments/reentry.py`:

| cells | values |
|---|---|
| breakout floor | 20d / 50d high → strength ≥ 0.5 / 1.0 |
| fast blend | a = 0.25 / 0.5 |
| score smoothing | EWMA halflife 5 / 2 (vs 10) |

**Lookahead.** All 9 cells pass on synthetic data. This check touches signal code, so it
must be re-run on real data before adopting anything.

**Results.** *Pending a real-data run* (`python run_research.py grid reentry`). Read the
recovery-episode table from `diagnose` next to it: the fix should cut "days to 80% exp".

**Verdict.** *Pending.*
