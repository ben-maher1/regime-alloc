# Experiments log

Every experiment gets: hypothesis, change, results vs baseline, verdict. Failures included.

---

## 2026-10-22 · Upside-capture study: harness and method

**Goal.** Raise upside capture vs static 80/15/5 (monthly) materially above baseline, with
walk-forward CAGR ≥ 11%, MaxDD no worse than −20%, and Sharpe no more than ~0.1 below baseline.
No leverage.

> **Data status: run on real data 2026-10-22** (Yahoo + FRED, history through 2026-10-21). The
> harness was built on `--synthetic` data in an earlier session that had no network access;
> every number below comes from the real-data run. Sequence used:
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
> The real-data lookahead log is in `research_results/lookahead.txt`.
>
> **Gate 1 (data sanity): PASS.** `grid baseline` reproduces the CLAUDE.md table exactly over
> the full period: full system 9.7% / 8.7% vol / 0.96 / −11.7%; momentum-only 10.0% / 0.88 /
> −18.7%; 200d-MA overlay 9.9% / 0.95 / −12.6%.
>
> **Gate 3 (lookahead): ALL PASS on real data**, covering all 67 configs in all six families,
> the chosen config included.
>
> **Walk-forward window reference (2010-01-01+).** Baseline 10.2% CAGR / 8.8% vol / 1.00
> Sharpe / −11.7% MaxDD / UpCap 0.58. Static 80/15/5 11.8% / 0.73 / −29.6%. So the brief
> needs UpCap ≥ 0.63, CAGR ≥ 11%, MaxDD ≥ −20% and Sharpe ≥ 0.90.

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

Full tables: `research_results/diagnose.md`. Annualized log-return gap vs frictionless 80/15/5:

| step | falling | recovery | normal | total (full) | total (2010+) |
|---|---|---|---|---|---|
| friction (band, costs) | +0.1% | −0.2% | +0.4% | +0.3% | +0.3% |
| (e) inverse-vol mix | +3.4% | −0.8% | +0.0% | **+2.7%** | **+1.7%** |
| (d) per-sleeve caps | −0.1% | −0.1% | −0.0% | −0.2% | −0.1% |
| binary trend filter | +3.3% | **−3.7%** | −0.8% | −1.2% | −1.8% |
| (a) partial scaling (cap 0.5) | +0.0% | −1.1% | −0.5% | **−1.6%** | −1.2% |
| (b) regime caps | +1.0% | −0.8% | −0.5% | −0.3% | −0.2% |
| **total** | +7.8% | **−6.7%** | −1.4% | −0.3% | −1.4% |

One-at-a-time removals from the full system (full period):

| | CAGR | Sharpe | MaxDD | UpCap | Rebal/yr |
|---|---|---|---|---|---|
| full system | 9.7% | 0.96 | −11.7% | 0.56 | 30 |
| − regime caps | 10.0% | 0.88 | −18.7% | 0.63 | 36 |
| − partial scaling (binary) | **11.0%** | **1.06** | −11.6% | 0.64 | **11** |
| − sleeve caps | 9.7% | 0.97 | −11.7% | 0.57 | 30 |
| 80/15/5 base instead of inv-vol | 7.5% | 0.72 | −15.6% | 0.57 | 22 |

Re-risking: after each >10% benchmark drawdown, exposure at the trough is 4–34% and averages
19–44% over the next 63 days. Getting back to 80% of pre-episode exposure takes 49–88 trading
days. In 2009 the strategy made +26.5% over the trough-to-new-high recovery; the benchmark made
+91%.

**Verdict.**
- **The prior on (e) was wrong.** The inverse-vol mix doesn't cost upside. It *adds* 2.7%/yr
  over 80/15/5, and swapping 80/15/5 base weights into the full system drops CAGR to 7.5%. GLDM
  has earned its weight. Fixed or tilted base weights are *not* the next experiment.
- **(c) slow re-risking is the dominant source.** Every timing layer gives back in recoveries
  what it saves in falls (−6.7%/yr recovery vs +7.8%/yr falling). The trend filter accounts
  for most of the recovery loss (−3.7%).
- **(a) is the biggest pure cost.** Partial scaling loses 1.6%/yr. Without regime caps it does
  cut MaxDD (−22.5% → −18.7%), but once the caps are on it saves nothing (−11.6% binary vs
  −11.7%). It also triples turnover (11 → 30 rebalances a year in the full system).
- **(d) is ~0, as predicted.** The caps can't bind while w ≤ base.
- **(b) regime caps are cheap.** They cost 0.3%/yr and take MaxDD from −18.7% to −11.7%.

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

**Results** (walk-forward window 2010+, `research_results/grid_sizing.md`):

| | CAGR | Vol | Sharpe | MaxDD | UpCap | AvgExp | Rebal/yr | brief |
|---|---|---|---|---|---|---|---|---|
| baseline (cap 0.5) | 10.2% | 8.8% | 1.00 | −11.7% | 0.58 | 60% | 30 | ✗ |
| cap 0.35 | 10.5% | 8.9% | 1.01 | −11.3% | 0.59 | 61% | 27 | ✗ |
| cap 0.25 | 10.7% | 9.0% | 1.03 | −11.4% | 0.61 | 62% | 24 | ✗ |
| cap 0.1 | 11.0% | 9.1% | 1.05 | −11.6% | 0.62 | 63% | 17 | ✗ (UpCap) |
| binary | 11.5% | 9.2% | 1.08 | −11.6% | 0.65 | 64% | 11 | ✓ |
| floor 0.25 >200d | 10.4% | 8.8% | 1.02 | −11.7% | 0.59 | 61% | 33 | ✗ |
| floor 0.5 >200d | 10.5% | 8.9% | 1.02 | −11.7% | 0.60 | 62% | 30 | ✗ |
| floor 1.0 >200d | 11.1% | 9.2% | 1.04 | −12.1% | 0.64 | 66% | 24 | ✓ |
| floor 0.5 score>0 | 10.6% | 8.9% | 1.03 | −11.9% | 0.59 | 61% | 24 | ✗ |
| zero cap 0.5 | 11.9% | 10.6% | 0.99 | −13.5% | 0.70 | 72% | 37 | ✓ |
| zero cap 0.25 | 12.4% | 10.8% | 1.01 | −12.9% | 0.73 | 75% | 28 | ✓ |
| normalize cap 0.5 | 13.0% | 11.1% | 1.04 | −14.4% | 0.75 | 77% | 27 | ✓ |
| normalize cap 0.25 | 13.0% | 11.0% | 1.04 | −14.3% | 0.76 | 77% | 22 | ✓ |
| **WF[sharpe]** | 11.3% | 9.2% | 1.07 | −11.6% | 0.63 | | | ✓ |
| **WF[calmar]** | 11.4% | 9.2% | 1.08 | −11.6% | 0.64 | | | ✓ |
| **WF[cagr_dd20]** | 12.6% | 10.7% | 1.03 | −13.3% | 0.73 | | | ✓ |

The WF selectors pick cap 0.1 or binary (sharpe, calmar) and normalize cap 0.25 (cagr_dd20).

**Verdict: PASS (rule 2), 3 of 3 objectives.** The region is flat and monotone: CAGR, Sharpe
and UpCap rise steadily from cap 0.5 to binary, with MaxDD unchanged and turnover falling by
two-thirds. That's a smooth slope, not a spike. The prior about drawdown was wrong:
`normalize`/`zero` cost only 1–3 points of MaxDD on real data, not the doubling seen on
synthetic data, because the regime caps still bound the book. The 2012 lag year gets slightly
*worse* under binary and normalize, so this lever doesn't fix the V-recovery problem. It adds
exposure across the board.
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

**Results** (walk-forward window 2010+, `research_results/grid_regime.md`):

| risk-off cap \ risk-on flip | 0.15 (sym) | 0.05 | 0.0 |
|---|---|---|---|
| 0.25 | 10.2% / 1.04 / −9.4% | 10.2% / 1.03 / −9.4% | 10.4% / 1.04 / −9.4% |
| 0.5 (base) | 10.2% / 1.00 / −11.7% | 10.2% / 1.00 / −11.7% | 10.3% / 1.00 / −11.7% |
| 0.75 | 10.3% / 0.96 / −14.5% | 10.3% / 0.95 / −14.5% | 10.3% / 0.96 / −14.5% |
| 1.0 (regime off) | 10.4% / 0.91 / −18.7% | | |

(CAGR / Sharpe / MaxDD.) EWMA halflife 2: 9.5% / 0.95 / −10.6% (sym), 9.6% / 0.94 / −10.6% (up 0).
WF[sharpe] 10.4% / 1.04 / −9.4%; WF[calmar] 10.2% / 1.00 / −11.7%; WF[cagr_dd20] 9.7% / 0.89 /
−18.7%. UpCap stays in 0.55–0.64 in every cell.

**Verdict: FAIL, 0 of 3 objectives.** The asymmetric deadband does nothing: band_up 0.05 and 0.0
change CAGR by ≤ 0.2% at every cap. The risk-off cap trades MaxDD against nothing. CAGR is flat
at 10.2–10.4% from cap 0.25 to 1.0, while MaxDD runs from −9.4% to −18.7%. **Side finding (not
part of this brief):** risk-off 0.25 is a free drawdown improvement (−9.4% vs −11.7%, same CAGR,
Sharpe +0.04 which is noise) and is flat across the three flip bands. That's worth a separate
look if drawdown ever becomes the goal; backlog item 3 now has an answer.
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

**Results** (walk-forward window 2010+, `research_results/grid_reentry.md`):

| | CAGR | Vol | Sharpe | MaxDD | UpCap | Rebal/yr | 2012 | 2019 | 2023 | brief |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 10.2% | 8.8% | 1.00 | −11.7% | 0.58 | 30 | +0.4% | +9.7% | +8.8% | ✗ |
| breakout 20d → 0.5 | 10.9% | 8.9% | 1.06 | −11.6% | 0.62 | 29 | +2.2% | +11.0% | +13.4% | ✗ (UpCap) |
| **breakout 20d → 1.0** | **12.1%** | 9.4% | **1.12** | **−11.6%** | **0.69** | 25 | +4.5% | +13.9% | +18.2% | ✓ |
| breakout 50d → 0.5 | 10.5% | 8.9% | 1.02 | −11.7% | 0.60 | 26 | +1.0% | +9.7% | +12.4% | ✗ |
| breakout 50d → 1.0 | 11.1% | 9.2% | 1.04 | −11.7% | 0.64 | 20 | +1.8% | +11.4% | +16.5% | ✓ |
| fast blend 0.25 | 9.8% | 8.3% | 1.00 | −12.6% | 0.56 | 44 | +3.5% | +12.9% | +13.4% | ✗ |
| fast blend 0.5 | 9.4% | 8.1% | 0.98 | −14.1% | 0.54 | 44 | +3.1% | +12.3% | +17.3% | ✗ |
| smoothing 5 | 10.3% | 8.6% | 1.03 | −10.4% | 0.56 | 38 | +2.6% | +10.8% | +10.3% | ✗ |
| smoothing 2 | 9.7% | 8.3% | 0.99 | −13.0% | 0.55 | 43 | +3.2% | +12.6% | +10.8% | ✗ |
| **WF[all three objectives]** | 12.1% | 9.4% | 1.12 | −11.6% | 0.69 | | | | | ✓ |

All three WF selectors pick `breakout 20d → 1.0` in **every** year from 2010. In other words,
it was already the best cell on the 2004–2009 training window alone, and the WF row matches
the fixed cell with no degradation. Full period (in-sample): 11.4% / 1.08 / −11.6%, against
the baseline's 9.7% / 0.96 / −11.7%.

**Verdict: PASS (rule 2), 3 of 3 objectives, for the breakout floor only.** All four breakout
cells beat baseline on CAGR, Sharpe and UpCap with MaxDD unchanged. Strength 1.0 beats 0.5 and
20d beats 50d in both pairings, so the direction is consistent even though only 20d → 1.0
clears the full brief. It's also the only lever that improves *every* lag year (2009 +4.2,
2012 +4.1, 2019 +4.2, 2023 +9.4, 2026 +3.0 points vs baseline): it targets the V-recovery
problem directly, as hypothesized. Because it only ever adds exposure, crash behavior is
unchanged (MaxDD −11.6%). The symmetric fast blend and lighter smoothing **fail**: they whipsaw
(43–44 rebalances a year) and lower CAGR, also as predicted.

Caveat: this family was designed *after* the V-recovery lag in this same history was known
(CLAUDE.md lag years). The 2010+ WF window removes parameter selection bias but not
hypothesis-selection bias. The 2004–2009 pick consistency and the clean 2×2 pattern are the
best evidence available in-sample.
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

**Results** (walk-forward window 2010+, `research_results/grid_voltarget.md`):

| | CAGR | Vol | Sharpe | MaxDD | UpCap | Rebal/yr | brief |
|---|---|---|---|---|---|---|---|
| baseline | 10.2% | 8.8% | 1.00 | −11.7% | 0.58 | 30 | ✗ |
| tv 10% binary / scaled | 10.5% / 10.6% | 8.9% | 1.02 / 1.03 | −12.9% / −13.8% | 0.63 / 0.62 | 18 / 32 | ✗ |
| tv 12% binary / scaled | 11.6% / 11.6% | 9.9% | 1.03 / 1.02 | −13.3% / −14.2% | 0.70 / 0.68 | 15 / 30 | ✓ |
| tv 15% binary / scaled | 12.3% / 12.3% | 10.6% | 1.02 / 1.02 | −14.3% / −14.2% | 0.74 / 0.72 | 13 / 29 | ✓ |
| tv 12% binary, IBIT .3 GLDM .8 | 11.9% | 10.0% | 1.04 | −13.4% | 0.71 | 16 | ✓ |
| tv 12% binary, IBIT .4 GLDM 1 | 12.0% | 10.0% | 1.05 | −13.4% | 0.71 | 16 | ✓ |
| tv 12% binary, no regime | 11.5% | 10.7% | 0.94 | −19.2% | 0.74 | 16 | ✓ (barely) |
| WF[sharpe] | 10.8% | 10.2% | 0.93 | −15.1% | 0.68 | | ✗ (CAGR) |
| WF[calmar] | 10.0% | 9.1% | 0.94 | −13.8% | 0.61 | | ✗ |
| WF[cagr_dd20] | 11.1% | 10.6% | 0.92 | −19.2% | 0.70 | | ✓ |

**Verdict: FAIL (rule 2), 1 of 3 objectives.** This is the hindsight trap the decision rule was
written to catch. Seven of the ten fixed cells pass the brief, but the WF rows lose 0.5–1.6% of
CAGR and about 0.1 Sharpe against them. The selectors keep switching between cells, including
the no-regime cell with −19% MaxDD, and pay for it. MaxDD did stay inside −20% (better than the
synthetic prior), and the regime caps are clearly needed: without them MaxDD goes −13% → −19%.
Raising the sleeve caps helps a little (+0.3–0.4% CAGR), confirming (d) only matters once
weights are scaled up. Not adopted. The vol target adds a parameter and a covariance estimate,
and its gain is matched more simply by the binary/breakout levers.

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

Full tables: `research_results/frontier.md`. Pareto set on (CAGR, MaxDD) over 2010+, among
all 67 configs, plus the WF rows that re-select among all of them each Jan 1:

| | CAGR | Vol | Sharpe | MaxDD | UpCap | Rebal/yr | CAGR / MaxDD full | brief |
|---|---|---|---|---|---|---|---|---|
| regime: off 0.25 / up 0.0 | 10.4% | 8.5% | 1.04 | −9.4% | 0.56 | 27 | 9.8% / −10.9% | ✗ |
| sizing: cap 0.25 | 10.7% | 9.0% | 1.03 | −11.4% | 0.61 | 24 | 10.3% / −11.4% | ✗ |
| **combined: cap.25 off.5 + bo20** | 12.3% | 9.5% | **1.13** | −11.5% | 0.70 | 21 | 11.7% / −11.5% | ✓ |
| baseline | 10.2% | 8.8% | 1.00 | −11.7% | 0.58 | 30 | 9.7% / −11.7% | ✗ |
| sizing: zero cap 0.25 | 12.4% | 10.8% | 1.01 | −12.9% | 0.73 | 28 | 11.6% / −14.9% | ✓ |
| sizing: normalize cap 0.25 | 13.0% | 11.0% | 1.04 | −14.3% | 0.76 | 22 | 12.4% / −14.3% | ✓ |
| combined: norm.25 off.75/up0 | 13.2% | 11.8% | 1.00 | −17.9% | 0.80 | 24 | 12.9% / −17.9% | ✓ |
| combined: norm.25 off.5 + bo20 | 13.8% | 11.1% | 1.11 | −18.1% | 0.82 | 21 | 13.0% / −18.1% | ✓ |
| combined: norm.25 off.75/up0 + bo20 | 14.1% | 12.0% | 1.05 | −19.1% | 0.88 | 22 | 13.6% / −19.1% | ✓ |
| static 80/15/5 | 11.8% | 15.0% | 0.73 | −29.6% | 1.00 | | 10.0% / −47.8% | ✗ |
| **WF[sharpe], all configs** | 11.3% | 9.4% | 1.04 | −12.3% | 0.66 | | | ✓ |
| **WF[calmar], all configs** | 11.5% | 9.9% | 1.02 | −17.5% | 0.70 | | | ✓ |
| **WF[cagr_dd20], all configs** | 12.2% | 11.7% | 0.93 | −19.0% | 0.80 | | | ✓ |

Off-frontier, single-lever points referenced below (2010+): `breakout 20d → 1.0` (= combined
`cap.5 off.5+bo20`) 12.1% / 1.12 / −11.6% / UpCap 0.69 / 25 rebal; `binary` 11.5% / 1.08 /
−11.6% / 0.65 / 11 rebal; `binary + bo20` 12.2% / 1.11 / −12.8% / 0.71 / 14 rebal. The first
sits 0.2% CAGR and 0.1 pt MaxDD inside the frontier.

Reading it:
- **The brief is feasible.** The prior that "≥ 11% at ≥ −20% with no leverage may not be
  feasible" was too pessimistic. Every WF row passes, including the WF over all 67 configs
  under all three objectives.
- **The frontier has a kink at about −11.5% MaxDD.** Up to there, the breakout floor adds about
  2% CAGR at no drawdown cost. Beyond it, each extra 1% of CAGR costs 2–3 points of MaxDD
  (`normalize`), and Sharpe stops improving.
- **Aggressive configs degrade out of sample, the conservative ones don't.** The top fixed cell
  (14.1%) becomes 12.2% / 0.93 Sharpe / −19.0% under WF[cagr_dd20]: the selector chases the
  high-CAGR corner and lands at the drawdown limit. Compare the breakout floor: 12.1% fixed,
  12.1% WF, −11.6%.
- **Combined factorial interactions.** The breakout floor adds 0.7–2.4% CAGR on every sizing
  base and regime setting except `tv12`, where it adds nothing and costs 3.5 points of MaxDD. On binary it
  overlaps (both add exposure to trending sleeves): +0.7% CAGR, −1.2 pt MaxDD. Lowering the cap
  from 0.5 to 0.25 adds only +0.2% on top of bo20 (12.1 → 12.3), which is noise.

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

How the priors held up: (e) **wrong**, since inverse-vol is a gain, not a gap. Binary trend
filter as a big source: **right** (it holds most of the recovery loss). (d) ≈ 0: **right**.
Feasibility: **too pessimistic**.

### Verdict: applying the decision rule

1. **Data sanity: PASS.** Exact reproduction of the CLAUDE.md table.
2. **WF evidence, per family:**

   | family | WF objectives passing | flat region? | result |
   |---|---|---|---|
   | (a) sizing | 3 / 3 | yes, monotone cap 0.5 → binary | **adopt-eligible** |
   | (b) regime / asymmetric band | 0 / 3 | flat, but flat at no gain | reject |
   | (c) reentry: breakout floor | 3 / 3 | yes, consistent 2×2; same pick every year | **adopt-eligible** |
   | (c) reentry: fast blend, smoothing | (cells fail) | — | reject |
   | vol target | 1 / 3 | fixed cells pass, WF doesn't | reject |

3. **Simplest passing config.** The best passing config is `cap.25 off.5 + bo20` (highest Sharpe
   on the frontier, 1.13). The rule doesn't say what "best" means; I've read it as best by
   Sharpe, which matches the repo's Sharpe-first framing. Within 0.05 Sharpe and 1% CAGR of it:
   `breakout 20d → 1.0` alone (12.1% / 1.12), `binary` alone (11.5% / 1.08), and
   `binary + bo20` (12.2% / 1.11). Two of those are single-lever with round numbers.
   **The breakout floor wins the tie on the brief's own goal:** UpCap 0.69 vs 0.65, and it's the
   only lever that lifts every lag year. Binary wins on turnover (11 vs 25 rebalances a year),
   and the cost model already charges for that, so it's in the CAGR figures.
   *Under the other reading* (best = max CAGR), the pick would be `norm.25 off.5 + bo20`
   (13.8%, −18.1%). I'm rejecting that reading on evidence, not taste: the high-CAGR corner is
   exactly where WF degrades (WF[cagr_dd20] 12.2% at −19.0% and Sharpe 0.93). It would also
   spend 6.4 of the 8.3 points of drawdown room to buy 1.7% CAGR.
4. **Lookahead re-run on real data: PASS** for `breakout 20d → 1.0` (and every other config).

> **Superseded the same day.** Ben chose best-*CAGR* as the reading of rule 3. See
> "CAGR-first decision + sleeve caps" below: production is now `normalize` + this breakout
> floor. The Sharpe-reading analysis is kept here for the record.

**Recommendation (Sharpe reading).** Adopt the **20-day Donchian breakout floor at full strength**
(`breakout_high=20, breakout_strength=1.0`) on top of the current system. Everything else stays
as is: SIGNAL_CAP 0.5, regime caps 1/1/.5/.5, symmetric deadband, inverse-vol base.

| 2010+ (WF window) | CAGR | Vol | Sharpe | MaxDD | UpCap | DownCap | Rebal/yr |
|---|---|---|---|---|---|---|---|
| baseline | 10.2% | 8.8% | 1.00 | −11.7% | 0.58 | 0.33 | 30 |
| **+ breakout 20d → 1.0** | **12.1%** | 9.4% | **1.12** | **−11.6%** | **0.69** | 0.40 | 25 |
| static 80/15/5 | 11.8% | 15.0% | 0.73 | −29.6% | 1.00 | 1.00 | |
| *full period, in-sample* | 11.4% | 9.3% | 1.08 | −11.6% | 0.66 | 0.35 | 25 |

It meets every criterion with room to spare: UpCap +0.11 against the +0.05 bar, CAGR 12.1%
against 11%, MaxDD −11.6% against −20%, and Sharpe *up* 0.12. That makes it a Sharpe
improvement, not a trade-off. It beats static 80/15/5 on CAGR over 2010+ with 40% of its
drawdown.

**Runner-up / possible follow-up:** `binary` (SIGNAL_CAP → 0) gives 11.5% / 1.08 / −11.6% with
less than half the turnover. Stacking both (`binary + bo20`) gives 12.2% / 1.11 / −12.8%, which
is no better than bo20 alone, so they're substitutes. Pick one.

**Not done, and why:**
- No change to `main`, `config.py` defaults or `run_daily.py`. Adopting this needs Ben's
  approval (CLAUDE.md). `build_targets` already calls `reentry_score` when the breakout keys
  are passed, so the change is small: add `BREAKOUT_HIGH = 20` and `BREAKOUT_STRENGTH = 1.0`
  to `config.py`, make them the defaults when `params` omits them, and have `run_daily.py`'s
  report say when a sleeve is held up by the breakout floor.
- Caveat to weigh before merging: the breakout family was hypothesized from the known lag years
  in this same sample. The WF removes parameter-picking bias, not idea-picking bias. The best
  available mitigation is to run it in shadow mode (log both targets daily, as in backlog
  item 2) for a few months before switching.

---

## 2026-10-22 · CAGR-first decision + sleeve caps · branch `claude/kind-mendel-krlcu2-combined`

**Instruction (Ben).** Read rule 3's "best" as best CAGR, not best Sharpe. Also try different
max allocations for the three sleeves. Changes to `config.py` / `run_daily.py` are approved on
this branch. Merging to `main` is still a separate approval.

### Rule 3 under best-CAGR

Among the 67 study configs that pass the brief (2010+), the best CAGR is
`combined:norm.25 off.75/up0+bo20` at 14.1% / 1.05 / −19.1%. **It uses the regime lever, which
failed rule 2** (0/3 WF objectives), so it isn't adoptable. Restricted to levers that passed
rule 2 (sizing, breakout reentry), the best is `norm.25 off.5+bo20` at 13.8% / 1.11 / −18.1%.
No single-lever config is within 1% CAGR *and* 0.05 Sharpe of it (`normalize` alone: 13.0% /
1.04). The caps family below shows `normalize` at the production SIGNAL_CAP 0.5 matches cap 0.25
to within 0.1% in every cap cell, so the rounder pick is **`normalize` + `bo20`, SIGNAL_CAP left
at 0.5**.

### Sleeve caps (`experiments/caps.py`, `research_results/grid_caps.md`)

**Hypothesis.** Under `normalize`, a lone live sleeve gets scaled toward 100%, so the caps bind
and the excess goes to SGOV. Higher GLDM/IBIT caps should buy CAGR at a drawdown cost, and lower
caps (or a VT cap) should do the reverse.

**Grid.** 3 bases (`bo20`, `norm.25+bo20`, `norm.5+bo20`) × VT {1.0, 0.8} × GLDM {0.4, 0.6,
0.8, 1.0} × IBIT {0.1, 0.2, 0.3, 0.4} = 96 cells + baseline. Lookahead: ALL PASS on real data
(`research_results/lookahead_caps.txt`).

**Results, `norm.5+bo20`, 2010+, CAGR / Sharpe / MaxDD** (rows GLDM cap, columns IBIT cap):

| VT 1.0 | IBIT 0.1 | 0.2 | 0.3 | 0.4 |
|---|---|---|---|---|
| GLDM 0.4 | 11.4 / 1.00 / −16.2 | 13.2 / 1.10 / −16.2 | 13.5 / 1.10 / −16.2 | 13.6 / 1.09 / −16.2 |
| **0.6** | 11.9 / 1.01 / −18.1 | **13.8 / 1.10 / −18.1** | 14.1 / 1.11 / −18.1 | 14.1 / 1.09 / −18.1 |
| 0.8 | 12.1 / 1.01 / −18.1 | 13.9 / 1.11 / −18.1 | 14.2 / 1.11 / −18.1 | 14.3 / 1.10 / −18.1 |
| 1.0 | 12.2 / 1.02 / −18.1 | 14.0 / 1.11 / −18.1 | 14.3 / 1.12 / −18.1 | 14.4 / 1.10 / −18.1 |

| VT 0.8 | IBIT 0.1 | 0.2 | 0.3 | 0.4 |
|---|---|---|---|---|
| GLDM 0.4 | 11.2 / 1.00 / −14.5 | 13.0 / 1.10 / −14.5 | 13.3 / 1.11 / −14.5 | 13.3 / 1.09 / −14.6 |
| 0.6 | 11.7 / 1.01 / −16.5 | 13.5 / 1.10 / −16.5 | 13.8 / 1.11 / −16.5 | 13.9 / 1.10 / −16.5 |
| 0.8 | 11.9 / 1.02 / −16.5 | 13.7 / 1.11 / −16.5 | 14.0 / 1.12 / −16.5 | 14.0 / 1.10 / −16.5 |
| 1.0 | 12.0 / 1.02 / −16.5 | 13.8 / 1.12 / −16.5 | 14.1 / 1.12 / −16.5 | 14.1 / 1.11 / −16.5 |

`norm.25+bo20` is within ±0.2% of these numbers in every cell. On `bo20` without normalize the
caps barely matter: every cell is 12.1% / 1.12–1.13 / −11.6% except GLDM 0.4 (11.6%) and IBIT
0.1 (−0.9%), which confirms they only bind once weights are scaled up.

WF over the caps family: sharpe 11.1% / 1.03 / −14.4%; calmar 11.8% / 1.10 / −11.6% (picks
`bo20` cells); cagr_dd20 **13.7% / 1.10 / −18.1%**. From 2016 on, cagr_dd20 picks
`norm.5+bo20 VT1 G1 I0.4`. Its 2010–15 picks are IBIT 0.1 cells; those are ties broken by grid
order, since IBIT has no data before 2014.

Full period (in-sample), for the cells that matter:

| | CAGR | Vol | Sharpe | MaxDD | UpCap |
|---|---|---|---|---|---|
| pre-study baseline | 9.7% | 8.7% | 0.96 | −11.7% | 0.56 |
| `bo20` | 11.4% | 9.3% | 1.08 | −11.6% | 0.66 |
| **`norm.5+bo20`, current caps** | **13.0%** | 11.1% | 1.04 | −18.1% | 0.79 |
| `norm.5+bo20`, GLDM 1.0 / IBIT 0.4 | 13.3% | 11.7% | 1.03 | −18.1% | 0.79 |
| `norm.5+bo20`, VT 0.8 | 12.8% | 10.9% | 1.05 | −16.5% | 0.77 |
| `norm.5+bo20`, GLDM 0.4 | 12.5% | 10.5% | 1.06 | −16.2% | 0.76 |
| `norm.5+bo20`, VT 0.8 / GLDM 0.4 / IBIT 0.3 | 12.5% | 10.4% | 1.07 | −14.5% | 0.75 |

**Reading it.**
- **Raising caps is nearly flat.** GLDM 0.6 → 1.0 adds 0.2–0.3% and IBIT 0.2 → 0.4 adds
  0.3%, both with no MaxDD change and Sharpe within noise. Over the full period the loosest cell
  adds only 0.3% CAGR and loses Sharpe. The IBIT part is bitcoin's 2015–2021 run, the most
  hindsight-prone input in the dataset.
- **IBIT 0.1 is clearly bad** (−1.9% CAGR, −0.09 Sharpe): the 0.2 cap is earning its keep.
- **The caps that bind on drawdown are GLDM and VT, not IBIT.** The −18.1% MaxDD is
  Aug 2011 → Jul 2012: gold topped and chopped while the book was concentrated. GLDM ≤ 0.4 or
  VT ≤ 0.8 cuts it by about 2 points for −0.3 to −0.6% CAGR. Both together reach −14.5% for
  −0.8% (−0.5% if IBIT goes to 0.3). That's a clean drawdown dial if one is ever wanted.

**Verdict.** Rule 3 (within 1% CAGR and 0.05 Sharpe of the best, then fewest changes and
roundest numbers): the best caps cell (14.4%) is within 0.6% of the current caps (13.8%) at the
same Sharpe and MaxDD. **The caps stay at VT 1.0 / GLDM 0.6 / IBIT 0.2.** If you want the last
~0.3–0.6% anyway, the least hindsight-prone version is GLDM 0.8–1.0 with IBIT left at 0.2.

### Production change (this branch; `main` untouched)

- `config.py`: `REDISTRIBUTE = "normalize"`, `BREAKOUT_HIGH = 20`, `BREAKOUT_STRENGTH = 1.0`.
  SIGNAL_CAP, caps, regime and band are unchanged.
- `sizing.target_weights` defaults `redistribute` to `C.REDISTRIBUTE`. `build_targets` applies
  the breakout floor from config unless `params` overrides it (`breakout_high=None` disables).
- `research.py`: `PRE_STUDY` is laid under every config, so `{}` still means the pre-study
  system and every logged result above reproduces. This was checked: baseline, `bo20` and
  `norm.5+bo20` match the logged CAGRs to 4 dp. `PRODUCTION` holds the new defaults, and
  `build_targets(prices, exposure)` with no params is bit-identical to
  `caps:norm.5+bo20 VT1 G0.6 I0.2`.
- `run_daily.py`: adds a SIZING line and a `Brkout` column, and flags any sleeve
  "held up by breakout floor" (breakout on and raw score below `BREAKOUT_STRENGTH × SIGNAL_CAP`).
- **Not yet run in this session:** `run_daily.py` and `run_backtest.py`. The session's permission
  policy blocked running the production entry points. Run them once before merging.

| new production | CAGR | Vol | Sharpe | MaxDD | UpCap | Rebal/yr |
|---|---|---|---|---|---|---|
| 2010+ (WF window) | 13.8% | 11.1% | 1.10 | −18.1% | 0.81 | 24 |
| full period (in-sample) | 13.0% | 11.1% | 1.04 | −18.1% | 0.79 | 22 |
| pre-study, 2010+ | 10.2% | 8.8% | 1.00 | −11.7% | 0.58 | 30 |

**What this costs vs the Sharpe pick (`bo20` alone):** +1.7% CAGR and +0.12 UpCap for 6.5 points
of MaxDD, leaving 1.9 points of room to the −20% limit. Out of sample, the
CAGR-first pooled selection lands at 12.2% / −19.0% (WF[cagr_dd20] over all study configs), so
expect a live drawdown near the limit at some point. The VT/GLDM caps above are the dial if that
becomes uncomfortable.

---

## 2026-10-23 · Benchmark check: static 60/30/10 (exploratory, in-sample)

**Question (Ben).** The new system and a static 60% VT / 30% GLDM / 10% IBIT mix are close
since 2020. Does that change the design?

**Why this benchmark matters.** The study measured upside capture against 80/15/5. But the
system's own average holding is close to 60/30/10: since 2004 it averages VT 44% / GLDM 30% /
IBIT 5% / SGOV 22%, and since 2020 VT 40% / GLDM 31% / IBIT 10%. Against 80/15/5, part of the
measured edge is just the gold tilt. Against 60/30/10, what's left is the timing alone.

**Static mix construction.** Daily rebalanced, no costs. Before IBIT/BTC data exists (pre-2014)
the weights renormalize to 2/3 VT and 1/3 GLDM. Ad hoc script, not yet in the harness.

| | 2004-10+ CAGR / Sharpe / MaxDD | 2010+ | 2020+ | trades/yr |
|---|---|---|---|---|
| production | 13.0% / 1.04 / −18.1% | 13.8% / 1.10 / −18.1% | 19.0% / 1.23 / −15.5% | 22 |
| static 60/30/10 | 12.3% / 0.75 / −41.1% | 13.7% / 0.87 / −27.5% | 17.5% / 0.89 / −27.5% | — |
| fixed 60/30/10 base + timing (`base_weights`) | 13.2% / 1.03 / −18.4% | 13.9% / 1.08 / −18.4% | 18.3% / 1.20 / −16.1% | 20 |
| 50% production + 50% static | 12.8% / 0.94 / −26.1% | 13.8% / 1.03 / −20.3% | 18.5% / 1.10 / −20.3% | — |
| production, weekly decisions (Fri) | 13.1% / 1.05 / −17.5% | 13.8% / 1.09 / −17.5% | 19.1% / 1.23 / −13.2% | 15 |
| production, 10-point band | 13.4% / 1.06 / −18.3% | 14.2% / 1.12 / −18.3% | 19.7% / 1.26 / −15.2% | 14 |

Calendar years, production vs static: production wins in down years (2008 −0.4% vs −26.1%,
2018 −7.8% vs −15.9%, 2022 −7.9% vs −18.3%). It loses in strong bull years (2017 +41.6% vs
+61.6%, 2019 +17.3% vs +32.6%, 2023 +20.5% vs +29.9%). Production is ahead in only 45% of
rolling 3-year windows.

**Reading.**
- **Against its own average mix, the timing adds almost no return** (+0.1%/yr since 2010,
  +0.7% since 2004). It cuts volatility by about a third and MaxDD by a third to a half. The
  system is a drawdown-control overlay on a 60/30/10-like portfolio, not a return engine.
- **Chasing more CAGR has a ceiling.** Every exposure lever pushes the system toward being
  always invested, i.e. toward static 60/30/10 with extra turnover. That makes 60/30/10 roughly
  the upper bound for return-raising levers. Further work should target turnover and drawdown,
  not CAGR.
- **The base weighting doesn't matter.** A fixed 60/30/10 base performs within noise of
  inverse-vol, so the earlier (e) finding was about 80/15/5 specifically.
- **Blending with the static mix is dominated.** It gets the same CAGR as production, with a
  worse Sharpe and a deeper drawdown.
- **Turnover is the one clear lever.** Weekly decisions or a 10-point band cut trades by
  roughly a third while matching or slightly beating every metric. The Sharpe differences are
  under 0.05, which counts as noise. This is backlog item 3.

**Verdict.** No production change from this. Next experiment: walk-forward test of a weekly
cadence and a band of {0.05, 0.075, 0.10}, with 60/30/10 added to the harness as a second
benchmark (and the brief's UpCap metric measured against it too).

---

## 2026-10-23 · Lever family: rebalance cadence and band · `experiments/cadence.py`

**Hypothesis.** Production makes about 22 trades a year, some of them churn (2023 had 36,
with several gold in-out-in round trips). Deciding less often, or trading only on a larger
drift, should cut turnover at no cost to CAGR, Sharpe or MaxDD.

**Change (harness only).** A new run key, `rebalance` ∈ {daily, weekly, monthly}.
`research.decision_days` updates targets only on Fridays or on the month's last trading day
and holds them in between. That's a calendar fact known in advance, so it stays causal.
`static 60/30/10` (`BENCH2`, renormalized before IBIT/BTC data exists) is now a row in every
stats table. In this family, "baseline" is **production** (daily, 5-point band). Lookahead:
ALL PASS on real data (8 cells).

**Results, walk-forward window 2010+** (`research_results/grid_cadence.md`):

| | CAGR | Vol | Sharpe | MaxDD | Trade days/yr |
|---|---|---|---|---|---|
| **production (daily, band 0.05)** | 13.8% | 11.1% | 1.10 | −18.1% | 24 |
| daily, band 0.075 | 13.9% | 11.1% | 1.10 | −18.4% | 19 |
| **daily, band 0.10** | 14.2% | 11.2% | 1.12 | −18.3% | **15** |
| daily, band 0.15 | 13.6% | 11.3% | 1.06 | −18.7% | 12 |
| weekly, band 0.05 | 13.8% | 11.2% | 1.09 | −17.5% | 16 |
| weekly, band 0.075 | 14.2% | 11.2% | 1.12 | −17.7% | 14 |
| weekly, band 0.10 | 13.7% | 11.3% | 1.08 | −17.7% | 12 |
| monthly, band 0.05 | 12.2% | 11.5% | 0.94 | −18.3% | 9 |
| static 60/30/10 | 13.7% | 14.5% | 0.87 | −27.5% | — |
| WF[sharpe] / [calmar] / [cagr_dd20] | 13.7 / 13.8 / 14.0% | 11.2% | 1.09 / 1.09 / 1.11 | −17.7 / −18.4 / −17.7% | — |

Full period (2004-10+): production 13.0% / 1.04 / −18.1% (22 trade days a year); daily 0.10
13.4% / 1.06 / −18.3% (14); weekly 0.05 13.1% / 1.05 / −17.5% (15); monthly 11.4% / 0.90 /
−21.8% (8).

One-way turnover barely moves: 3.88/yr for production, 3.64 for daily 0.10, 3.74 for weekly
0.05. Cost drag falls only from 20.7 to about 19 bp/yr. Fewer, larger trades: the turnover comes
from real signal changes, not band noise.

**Reading.**
- **Flat region from daily 0.05 to weekly 0.10.** Every cell is within 0.5% CAGR and 0.04
  Sharpe of production, which is noise. The WF rows match production, so selecting among
  cadences adds nothing. Two cells degrade: **monthly** (−1.6% CAGR, −0.16 Sharpe, and the
  full-period MaxDD goes past −20%) and, mildly, **band 0.15**. That marks the edge.
- **Weekly is noisier year to year.** Same totals, but which day the decision lands on
  matters: 2026 YTD is +4.6–4.9% weekly against +9.6% daily, and 2012 is −0.5% against +1.9%.
  Daily band 0.10 tracks production year by year (2026 +10.9%, 2012 +2.2%).
- **The gain is fewer trade days, not lower costs.** For a human-approved process that is the
  benefit that matters: about 9 fewer trade/alert days a year.

**Verdict: PASS for daily, band 0.10.** It's the simplest cell in the flat region: one
parameter changed, no new production code path, a round number, 24 → 15 trade days a year at
equal performance, and it tracks production's year-by-year path. Weekly cadence is **not**
adopted: same totals, more path noise, and it would need new production code.

**Applied 2026-10-23 (Ben approved):** `REBALANCE_BAND = 0.10`. To keep logged results
reproducible, the harness now defaults configs without `band` to `PRE_STUDY_BAND = 0.05`, and
`PRODUCTION` carries `band` explicitly. Checked: caps and cadence cells reproduce their logged
CAGRs to 4 dp, and `run(prices, build_targets(prices, exposure))` with config defaults is
identical to `cadence:daily band 0.1`. New production, full period: 13.4% / 11.2% vol / 1.06 /
−18.3%, 14 trade days a year. Side effect visible today: the model book keeps about 5% GLDM
because the Sep 25 sale of the last 5% no longer clears the band.

---

## 2026-10-23 · Cash model: fed funds − 30bp (production change, Ben's spec)

**Change.** The risk-off asset is a cash balance, not SGOV. `config.CASH = "CASH"`, earning
`max(DFF − 0.30%, 0)` from FRED. It accrues act/360 over calendar days at the prior business
day's rate, has zero trading cost, and is floored at 0 because a cash account doesn't charge
negative rates. `data.cash_index` builds it. BIL/SGOV are no longer downloaded.

**Effect.** Small. Production over the full period goes from 13.4% / 1.06 / −18.3% to
13.5% / 1.04 / −18.2%. The Sharpe moves because the risk-free series is now this cash.
Cash returns 0.00% in 2012, 1.45% in 2022, 4.89% in 2023, 5.08% in 2024 and 4.05% in 2025.
Logged results before this entry used SGOV/BIL and will differ in the second decimal place if
re-run. Not worth a compatibility flag.

---

## 2026-10-23 · Taxable account viability + a correction to the 60/30/10 finding

**Question (Ben).** Is the strategy viable in a taxable account? The IRA is non-taxable.

**Tax model** (`regime_alloc/tax.py`, `run_tax.py`, `research_results/tax.md`). It works at
lot level and sells highest-cost lots first (specific ID). Gains are short-term if held ≤ 365
days, else long-term. GLDM's long-term gains are collectibles, capped at 28%. It applies
wash-sale disallowance both ways (±30 days) and IRS netting across the ST / 28% / 15–20%
buckets, with losses carried forward. The $3k ordinary offset is ignored. VT dividends (2%/yr,
qualified) and cash interest are taxed as they arrive. Each year's tax is paid on the first
trading day after Apr 15, by selling all holdings pro rata. Validation: with all rates at 0 the
account reproduces the backtest within 0.04 bp/day. Scenarios are federal only: 24%/15%,
32%/15% + 3.8% NIIT, and 37%/20% + NIIT.

**Correction first.** Every earlier "vs 60/30/10" result used a **daily**-rebalanced static
mix. A real investor rebalances maybe yearly, and with bitcoin in the mix that makes a large
difference:

| pre-tax CAGR, start → 2026-10-21 | strategy | 60/30/10 yearly | 60/30/10 daily |
|---|---|---|---|
| 2005 | 13.4% (MaxDD −18.2%) | **14.9%** (−39.7%) | 12.2% (−41.1%) |
| 2010 | 14.2% (−18.2%) | **17.1%** (−31.3%) | 13.6% (−27.5%) |
| 2015 | 17.4% (−15.2%) | **21.9%** (−31.3%) | 17.0% (−27.5%) |
| 2020 | **19.9%** (−15.2%) | 19.2% (−29.0%) | 17.7% (−27.5%) |
| 2005–2013 only (no BTC) | **9.6%** (−18.2%) | 7.7% (−39.7%) | 7.7% (−41.1%) |

The gap is all bitcoin. Before BTC, yearly and daily rebalancing are identical and the strategy
wins by 1.9%/yr. Since 2014, a yearly reset to 10% BTC rides BTC's within-year runs, which daily
rebalancing keeps selling. The strategy captures less: its inverse-vol base gives BTC only about
10%, it goes to 0 on negative trends, and it caps at 20%. That puts the 2026-10-23 finding that
timing adds "0–0.7%/yr over its own mix" against the wrong benchmark. **Against a
yearly-rebalanced 60/30/10 the strategy trails pre-tax by 1.5–4.5%/yr since 2005–2015 and ties
since 2020.** It still has about half the drawdown. Caveat: the static mix's edge is having held
bitcoin through a roughly 300× run, which may not repeat.

**After tax** (32%/15% + NIIT, everything sold at the end):

| start | strategy | 60/30/10 yearly | gap |
|---|---|---|---|
| 2005 | 9.9% | 12.8% | −2.9%/yr |
| 2010 | 10.5% | 14.7% | −4.2%/yr |
| 2015 | 12.8% | 18.6% | −5.8%/yr |
| 2020 | 14.3% | 15.4% | −1.1%/yr |

The strategy's tax drag is 3.5–5.6%/yr (2015+: 17.4% → 12.8%), against 2.3–3.8% for yearly
60/30/10. Its realized gains are mostly short-term: 2015–2025 ST net 1.61×, LT 1.24×,
collectibles 0.30× of the starting balance. Even from 2020, where it wins pre-tax by 0.7%/yr, it
loses by 1.1%/yr after tax. Every bracket scenario points the same way (`tax.md`).

**Verdict.** **Not viable as-is in the taxable account.** It gives up 1–6%/yr after tax to a
yearly-rebalanced 60/30/10 in exchange for roughly half the drawdown (−15 to −18% vs −29 to
−40% pre-tax). In the IRA, taxes don't apply but the correction does: there too it trails yearly
60/30/10 on return since 2010 and wins only on drawdown. Possible next steps, all untested:
(1) asset location, holding the high-turnover and collectibles sleeves in the IRA; (2) a
tax-aware variant for taxable that only acts on regime flips, uses a wider band and holds lots
to long-term; (3) lifting the BTC sleeve (base weight or cap), since BTC treatment is the
pre-tax gap. That one is high hindsight risk.

---

## 2026-10-23 · Bitcoin treatment · `run_btc.py`, `research_results/btc.md`

**Hypothesis.** The pre-tax gap to yearly 60/30/10 comes from how the strategy handles BTC.
It averages 8.3% IBIT since 2015 and holds 0 on 26% of days, through an inverse-vol base, trend
exits and a 20% cap. Holding BTC as a fixed sleeve, or timing it inside a fixed slot, should
close the gap.

**Variants** (pre-tax; sleeves rebalanced yearly; BTC data starts 2014, so windows run from 2015):

| 2015–2026 | CAGR | Vol | Sharpe | MaxDD |
|---|---|---|---|---|
| **production** | 17.3% | 11.2% | **1.31** | **−15.2%** |
| production, IBIT cap 0.3 | 17.5% | 11.5% | 1.31 | −15.0% |
| VT/GLDM timed + BTC fixed 5% | 15.6% | 11.8% | 1.13 | −18.6% |
| VT/GLDM timed + BTC fixed 10% | 21.0% | 15.3% | 1.21 | −25.5% |
| VT/GLDM timed + BTC fixed 15% | 25.7% | 18.6% | 1.22 | −30.5% |
| VT/GLDM timed 90% + BTC timed alone 10% | 20.9% | 15.0% | 1.21 | −25.4% |
| VT/GLDM timed, no BTC | 8.8% | 9.2% | 0.77 | −15.7% |
| static 60/30/10 yearly | 22.3% | 17.5% | 1.13 | −29.2% |
| static 67/33 yearly, no BTC | 10.6% | 12.7% | 0.71 | −24.0% |
| BTC buy & hold / BTC timed alone | 57.1% / 62.5% | 65% / 58% | 1.00 / 1.10 | −83% / −78% |

Split halves: 2015–2019, BTC fixed 10% returns 25.0% vs production's 14.0%. 2020–2026,
**production wins on both axes** (19.7% / 1.27 / −15.2% against BTC fixed 10% at 18.2% / 1.13 /
−20.5%, and static 60/30/10 at 18.7% / 0.94 / −29.2%).

**Reading.**
- **Size, not timing.** Timing BTC inside a fixed 10% slot returns the same as holding it
  (20.9% vs 21.0%) with a slightly smaller DD. Timing BTC alone helped in 2015–19 (106% vs 82%/yr)
  and roughly tied in 2020–26 with a much smaller DD (−58% vs −77%). That fits the crypto
  momentum literature. The gap is how *much* BTC the book holds, not when.
- **More BTC is a risk dial, not an optimization.** Each extra 5% of fixed BTC adds about 5%/yr
  CAGR and 5–6 points of MaxDD at a flat Sharpe of about 1.2. Production has the best Sharpe and
  the smallest DD of any variant.
- **The gap is a 2015–2019 story.** That was BTC's run from about $300 to $7k on a tiny base.
  Since 2020 the production treatment beats every fixed sleeve on return and risk.
- **The data can't pick a BTC weight.** BTC's mean return has a standard error of about
  σ/√T ≈ 65%/√12 ≈ 19%/yr, so the 57% CAGR is roughly ±37% at 95%.
- **Side finding.** Since 2015, VT/GLDM timing without BTC trails static 67/33 (8.8% vs 10.6%)
  with a smaller DD (−15.7% vs −24.0%). In 2005–2013 the timing won. A long bull market hurts
  timing on return.

**Verdict.** No change to BTC handling. A larger BTC position is a risk-appetite decision for
Ben, not something the backtest can justify. If he wants one, a fixed sleeve of N% held
outside the timing is the clean implementation: its return and drawdown scale roughly
linearly with N.
