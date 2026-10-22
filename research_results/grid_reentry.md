# Grid: reentry

Lever family (c): slow re-risking after drawdowns.

Hypothesis: after a V-bottom the 126/252d horizons stay negative for months,
and the EWMA(10) smoothing adds more lag, so the sleeve sits in cash through
the steepest part of the rebound. A fast component that only *adds* exposure
(a Donchian breakout floor) should recover the rebound and leave crash
behaviour alone. A symmetric fast blend also re-risks sooner but whipsaws more.

Grid (all with regime caps on):
  breakout floor   new 20d / 50d high -> strength >= 0.5 / 1.0, until new 20d / 50d low
  fast blend       a = 0.25 / 0.5 of a 10/20d vol-adjusted score (EWMA hl 3)
  score smoothing  EWMA halflife 5 / 2 (vs 10)

## Walk-forward window 2010-01-01+ (grid cells are fixed configs; WF[...] rows re-select the cell each Jan 1 on the expanding window by that objective)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| baseline | +10.2% | 8.8% | 1.00 | -11.7% | 0.88 | 0.58 | 0.33 | 59.8% | 30 |
| breakout 20d -> 0.5 | +10.9% | 8.9% | 1.06 | -11.6% | 0.94 | 0.62 | 0.36 | 63.0% | 29 |
| breakout 20d -> 1.0 | +12.1% | 9.4% | 1.12 | -11.6% | 1.04 | 0.69 | 0.40 | 67.5% | 25 |
| breakout 50d -> 0.5 | +10.5% | 8.9% | 1.02 | -11.7% | 0.90 | 0.60 | 0.35 | 61.6% | 26 |
| breakout 50d -> 1.0 | +11.1% | 9.2% | 1.04 | -11.7% | 0.95 | 0.64 | 0.39 | 64.6% | 20 |
| fast blend 0.25 | +9.8% | 8.3% | 1.00 | -12.6% | 0.77 | 0.56 | 0.34 | 56.8% | 44 |
| fast blend 0.5 | +9.4% | 8.1% | 0.98 | -14.1% | 0.66 | 0.54 | 0.32 | 54.4% | 44 |
| smoothing 5 | +10.3% | 8.6% | 1.03 | -10.4% | 0.99 | 0.56 | 0.29 | 57.8% | 38 |
| smoothing 2 | +9.7% | 8.3% | 0.99 | -13.0% | 0.74 | 0.55 | 0.32 | 56.8% | 43 |
| static 80/15/5 | +11.8% | 15.0% | 0.73 | -29.6% | 0.40 | 1.00 | 1.00 |  |  |
| WF[sharpe] | +12.1% | 9.4% | 1.12 | -11.6% | 1.04 | 0.69 | 0.40 |  |  |
| WF[calmar] | +12.1% | 9.4% | 1.12 | -11.6% | 1.04 | 0.69 | 0.40 |  |  |
| WF[cagr_dd20] | +12.1% | 9.4% | 1.12 | -11.6% | 1.04 | 0.69 | 0.40 |  |  |

### Success criteria (walk-forward window, vs baseline)

|  | UpCap+ | CAGR>=11% | DD>=-20% | Sharpe>=base-0.1 | ALL |
|---|---|---|---|---|---|
| baseline | ✗ | ✗ | ✓ | ✓ | ✗ |
| breakout 20d -> 0.5 | ✗ | ✗ | ✓ | ✓ | ✗ |
| breakout 20d -> 1.0 | ✓ | ✓ | ✓ | ✓ | ✓ |
| breakout 50d -> 0.5 | ✗ | ✗ | ✓ | ✓ | ✗ |
| breakout 50d -> 1.0 | ✓ | ✓ | ✓ | ✓ | ✓ |
| fast blend 0.25 | ✗ | ✗ | ✓ | ✓ | ✗ |
| fast blend 0.5 | ✗ | ✗ | ✓ | ✓ | ✗ |
| smoothing 5 | ✗ | ✗ | ✓ | ✓ | ✗ |
| smoothing 2 | ✗ | ✗ | ✓ | ✓ | ✗ |
| WF[sharpe] | ✓ | ✓ | ✓ | ✓ | ✓ |
| WF[calmar] | ✓ | ✓ | ✓ | ✓ | ✓ |
| WF[cagr_dd20] | ✓ | ✓ | ✓ | ✓ | ✓ |

### Walk-forward picks per year

|  | sharpe | calmar | cagr_dd20 |
|---|---|---|---|
| 2010 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2011 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2012 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2013 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2014 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2015 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2016 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2017 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2018 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2019 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2020 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2021 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2022 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2023 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2024 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2025 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |
| 2026 | breakout 20d -> 1.0 | breakout 20d -> 1.0 | breakout 20d -> 1.0 |

## Full period (in-sample)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| baseline | +9.7% | 8.7% | 0.96 | -11.7% | 0.83 | 0.56 | 0.29 | 58.8% | 30 |
| breakout 20d -> 0.5 | +10.3% | 8.8% | 1.01 | -11.6% | 0.88 | 0.60 | 0.32 | 61.7% | 29 |
| breakout 20d -> 1.0 | +11.4% | 9.3% | 1.08 | -11.6% | 0.98 | 0.66 | 0.35 | 65.9% | 25 |
| breakout 50d -> 0.5 | +9.9% | 8.8% | 0.98 | -11.7% | 0.85 | 0.59 | 0.32 | 60.5% | 26 |
| breakout 50d -> 1.0 | +10.5% | 9.1% | 1.00 | -12.9% | 0.81 | 0.63 | 0.35 | 63.4% | 19 |
| fast blend 0.25 | +9.1% | 8.3% | 0.94 | -12.6% | 0.72 | 0.55 | 0.30 | 56.0% | 43 |
| fast blend 0.5 | +8.6% | 8.1% | 0.91 | -14.1% | 0.61 | 0.52 | 0.29 | 53.5% | 42 |
| smoothing 5 | +9.7% | 8.5% | 0.99 | -10.4% | 0.93 | 0.55 | 0.27 | 56.9% | 37 |
| smoothing 2 | +9.2% | 8.3% | 0.96 | -13.0% | 0.71 | 0.55 | 0.29 | 55.8% | 42 |
| static 80/15/5 | +10.0% | 16.4% | 0.59 | -47.8% | 0.21 | 1.00 | 1.00 |  |  |

## Lag years

|  | 2009 | 2012 | 2019 | 2023 | 2026 |
|---|---|---|---|---|---|
| baseline | +15.6% | +0.4% | +9.7% | +8.8% | +4.5% |
| breakout 20d -> 0.5 | +16.3% | +2.2% | +11.0% | +13.4% | +5.9% |
| breakout 20d -> 1.0 | +19.8% | +4.5% | +13.9% | +18.2% | +7.5% |
| breakout 50d -> 0.5 | +16.9% | +1.0% | +9.7% | +12.4% | +4.7% |
| breakout 50d -> 1.0 | +21.7% | +1.8% | +11.4% | +16.5% | +5.2% |
| fast blend 0.25 | +13.5% | +3.5% | +12.9% | +13.4% | +5.3% |
| fast blend 0.5 | +12.4% | +3.1% | +12.3% | +17.3% | +5.7% |
| smoothing 5 | +15.2% | +2.6% | +10.8% | +10.3% | +5.1% |
| smoothing 2 | +17.0% | +3.2% | +12.6% | +10.8% | +6.5% |
| static 80/15/5 | +30.8% | +14.8% | +29.9% | +26.0% | +8.6% |
| WF[sharpe] |  | +4.5% | +13.9% | +18.2% | +7.5% |
| WF[calmar] |  | +4.5% | +13.9% | +18.2% | +7.5% |
| WF[cagr_dd20] |  | +4.5% | +13.9% | +18.2% | +7.5% |
