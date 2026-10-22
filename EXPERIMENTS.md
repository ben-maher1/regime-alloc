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

## 2026-10-22 · Lever family (a): signal-strength cash drag · branch `claude/kind-mendel-krlcu2-sizing`

**Hypothesis.** `clip(score/0.5, 0, 1)` holds a large share of a positive-trend sleeve's
baseline in cash. Lowering SIGNAL_CAP, flooring strength for sleeves in an uptrend, or sending
unused weight to live sleeves instead of SGOV should raise upside capture. The regime caps
stay on, so drawdown protection should mostly survive.

**Change.** `target_weights(strength_floor=, trend_up=, redistribute=)`. These are
research-only kwargs and production defaults are unchanged. `backtest.trend_up()` defines
"uptrend" as score > 0, close > n-day SMA, or either. `experiments/sizing.py`:

| cells | values |
|---|---|
| SIGNAL_CAP | 0.5 (base), 0.35, 0.25, 0.1, binary |
| strength floor (cap 0.5) | 0.25 / 0.5 / 1.0 when close > 200d SMA; 0.5 when score > 0 |
| redistribute | `zero` (dead sleeves' baseline → live sleeves), `normalize` (risky sums to 1 when anything is on), each at cap 0.5 / 0.25 |

**Lookahead.** All 13 cells pass on synthetic data.

**Prior / what to watch.** `normalize` and `zero` remove *all* cash except regime and sleeve
caps. On the synthetic smoke test they roughly doubled MaxDD. Expect the same direction on
real data: they buy upside with drawdown, so they may need the vol-target family as a brake.

**Results.** *Pending a real-data run* (`python run_research.py grid sizing`).
## 2026-10-22 · Lever family (b): regime caps and asymmetric deadband · branch `claude/kind-mendel-krlcu2-regime`

**Hypothesis.** The 0.5 risk-off cap costs the most upside after the risk axis has turned
up but before it clears +0.15. Raising the risk-off cap or flipping back to risk-on sooner
should recover V-shaped rebounds. Going risk-off is left untouched, so crash protection is
kept.

**Change.** `sticky_sign(band_up=)` and `compute_regime(band_up=)`. `band_up` sets the
threshold for flipping *back* to risk-on and applies to the risk axis only. The risk-off
threshold stays −0.15. With `band_up=None` the regime is identical to production; this is
asserted on synthetic data. `experiments/regime.py`:

| cells | values |
|---|---|
| risk-off cap (regimes 3/4) | 0.25 / 0.5 (base) / 0.75 / 1.0 (= regime off) |
| × risk-on flip band | 0.15 (symmetric, base) / 0.05 / 0.0 |
| + regime EWMA halflife | 2 (vs 5) at cap 0.5, symmetric and band_up 0 |

**Lookahead.** All 12 cells pass on synthetic data.

**Overfit note.** Known finding: Sharpe is flat across regime smoothing × deadband. The
question here is narrower: does *asymmetry* buy upside capture without moving MaxDD? Only adopt
it if the band_up 0.05 and 0.0 rows agree. One good cell isn't enough.

**Results.** *Pending a real-data run* (`python run_research.py grid regime`).
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
## 2026-10-22 · Lever family (vol target + sleeve caps) · branch `claude/kind-mendel-krlcu2-voltarget`

**Hypothesis.** Partial strengths (score/0.5) leave cash even when the whole book's risk is
low. Normalizing base × strength to a fully invested shape, then sizing the book to a 10–15%
vol target, should invest more in calm uptrends and de-risk on its own when vol spikes. The
target never takes the book above the regime cap, so there's no leverage. Upside capture
should rise without giving back drawdown control.

**Why the sleeve caps (d) live here.** With the inverse-vol baseline, IBIT gets about 10% of
the base and GLDM about 45%, against caps of 20% and 60%. Since w = base × strength ≤ base,
the caps almost never bind in production; the `diagnose` waterfall step (d) will confirm this.
Raising them only matters once weight is scaled up, which is what this family does.

**Change.** `target_weights(port_vol_target=, port_vol_halflife=)` and
`sizing.ewma_port_vol()`: a zero-mean EWMA covariance (hl 30) of daily returns through t.
Checked against single-sleeve `ewma_vol`: it matches to 3 dp. Book weight
= shape × min(target / σ̂, regime cap). `experiments/voltarget.py`:

| cells | values |
|---|---|
| target vol × shape | 10 / 12 / 15% × binary (score > 0) / scaled (cap 0.5) |
| sleeve caps at 12% binary | IBIT .3 / GLDM .8 and IBIT .4 / GLDM 1.0 |
| 12% binary, no regime | regime off: is the vol target alone enough? |

**Lookahead.** All 10 cells pass on synthetic data.

**Prior / what to watch.** EWMA vol reacts *after* a shock, so a fast crash (Mar 2020) hits
the book at full size before the target cuts it. MaxDD is the binding constraint here. On the
synthetic smoke test every cell landed worse than −20%. Real data may differ, but expect this
family to need the regime caps or a lower target.

**Results.** *Pending a real-data run* (`python run_research.py grid voltarget`).

**Verdict.** *Pending.*

---

## 2026-10-22 · Combined factorial + frontier · branch `claude/kind-mendel-krlcu2-combined`

**What.** This branch merges the four lever branches. Conflicts were resolved by hand and no
lever logic changed. `experiments/combined.py` crosses round-number settings of each lever
(no best cells): sizing {cap 0.5, cap 0.25, binary, normalize cap 0.25, vol target 12% binary}
× regime {risk-off 0.5 symmetric, risk-off 0.75 with risk-on flip at 0} × reentry {none,
20d breakout → full}, which is 19 cells plus baseline. `run_research.py frontier all` pools
*every* config from every family. It marks the Pareto set on (CAGR, MaxDD) over the
walk-forward window and adds `WF[...]` rows that re-select among all ~70 configs each Jan 1.
The fixed frontier cells are chosen with hindsight; the WF rows are the numbers to judge by.

**Lookahead.** `lookahead all` prints ALL PASS on synthetic data, covering every config in
every family. The production path is bit-identical to `main`.

### Frontier (CAGR vs MaxDD, walk-forward window)

*Pending a real-data run* (`python run_research.py frontier all`). Paste the efficient set
(3–5 rows), the WF rows, criteria and lag-year tables here.

### Decision rule, fixed *before* seeing real results

Writing it down now so the choice can't be fitted to the outcome:

1. **Data sanity.** `grid baseline` must reproduce the CLAUDE.md table (9.7% / 0.96 / −11.7%
   full system) within about ±0.2% CAGR and ±0.02 Sharpe. Otherwise stop and fix the data.
2. **Only WF evidence counts.** A lever family is adopted only if its *own grid's* WF row meets
   the brief under at least 2 of the 3 selection objectives, **and** the neighboring cells in
   its grid point the same way (a flat region, not a spike). Sharpe differences under 0.05 are
   noise.
3. **Simplest passing config wins.** Among frontier configs within 0.05 Sharpe and 1% CAGR of
   the best one that passes, pick the one with the fewest levers and the roundest numbers.
4. **Re-run lookahead on real data** for the chosen config before any change to `main` or
   `run_daily.py`. Any merge waits for Ben's approval.

### Prior expectation (to check against, not a result)

- (e) the inverse-vol mix and the binary trend filter are probably bigger sources of the gap
  than (a) or (b). Inverse-vol puts about 45% in GLDM against the benchmark's 15%. If
  `diagnose` confirms this, the cheapest upside lever (fixed or tilted base weights) is not in
  the brief and should be the next experiment.
- (d) sleeve caps should come out near zero in `diagnose`, because they can't bind when
  w ≤ base.
- **CAGR ≥ 11% with MaxDD ≥ −20% and no leverage may not be feasible.** It needs most of the
  benchmark's upside plus real timing value. Momentum-only, at about 59% average exposure,
  already reaches 10.0% with −18.7% MaxDD, so reaching 11% at −20% means about 80%+ average
  exposure *and* keeping the crash exits. The frontier will show whether any WF row reaches it.
  If none does, the honest recommendation is the best WF point on the frontier, with the
  shortfall stated. Loosening the criteria after seeing results isn't an option.

**Verdict.** *Pending a real-data run.*
