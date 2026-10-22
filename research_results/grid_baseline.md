# Grid: baseline

Baseline and the reference stand-ins from CLAUDE.md (production config,
momentum only, 200d-MA overlay). No new code; sanity check that the harness
reproduces the documented numbers.

## Walk-forward window 2010-01-01+ (grid cells are fixed configs; WF[...] rows re-select the cell each Jan 1 on the expanding window by that objective)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| baseline | +10.2% | 8.8% | 1.00 | -11.7% | 0.88 | 0.58 | 0.33 | 59.8% | 30 |
| momentum only | +10.4% | 10.0% | 0.91 | -18.7% | 0.56 | 0.64 | 0.43 | 67.9% | 36 |
| 200d-MA overlay | +9.9% | 9.2% | 0.93 | -12.6% | 0.78 | 0.60 | 0.40 | 64.4% | 36 |
| static 80/15/5 | +11.8% | 15.0% | 0.73 | -29.6% | 0.40 | 1.00 | 1.00 |  |  |
| WF[sharpe] | +9.7% | 9.0% | 0.93 | -12.6% | 0.77 | 0.59 | 0.38 |  |  |
| WF[calmar] | +9.9% | 8.9% | 0.95 | -12.6% | 0.79 | 0.59 | 0.37 |  |  |
| WF[cagr_dd20] | +10.0% | 9.2% | 0.94 | -12.6% | 0.79 | 0.60 | 0.40 |  |  |

### Success criteria (walk-forward window, vs baseline)

|  | UpCap+ | CAGR>=11% | DD>=-20% | Sharpe>=base-0.1 | ALL |
|---|---|---|---|---|---|
| baseline | ✗ | ✗ | ✓ | ✓ | ✗ |
| momentum only | ✓ | ✗ | ✓ | ✓ | ✗ |
| 200d-MA overlay | ✗ | ✗ | ✓ | ✓ | ✗ |
| WF[sharpe] | ✗ | ✗ | ✓ | ✓ | ✗ |
| WF[calmar] | ✗ | ✗ | ✓ | ✓ | ✗ |
| WF[cagr_dd20] | ✗ | ✗ | ✓ | ✓ | ✗ |

### Walk-forward picks per year

|  | sharpe | calmar | cagr_dd20 |
|---|---|---|---|
| 2010 | 200d-MA overlay | 200d-MA overlay | 200d-MA overlay |
| 2011 | 200d-MA overlay | 200d-MA overlay | 200d-MA overlay |
| 2012 | 200d-MA overlay | 200d-MA overlay | 200d-MA overlay |
| 2013 | 200d-MA overlay | 200d-MA overlay | 200d-MA overlay |
| 2014 | 200d-MA overlay | 200d-MA overlay | 200d-MA overlay |
| 2015 | 200d-MA overlay | 200d-MA overlay | 200d-MA overlay |
| 2016 | 200d-MA overlay | 200d-MA overlay | 200d-MA overlay |
| 2017 | 200d-MA overlay | 200d-MA overlay | 200d-MA overlay |
| 2018 | 200d-MA overlay | 200d-MA overlay | 200d-MA overlay |
| 2019 | 200d-MA overlay | 200d-MA overlay | 200d-MA overlay |
| 2020 | 200d-MA overlay | 200d-MA overlay | 200d-MA overlay |
| 2021 | baseline | baseline | 200d-MA overlay |
| 2022 | baseline | baseline | 200d-MA overlay |
| 2023 | baseline | baseline | 200d-MA overlay |
| 2024 | baseline | baseline | 200d-MA overlay |
| 2025 | baseline | baseline | 200d-MA overlay |
| 2026 | 200d-MA overlay | baseline | momentum only |

## Full period (in-sample)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| baseline | +9.7% | 8.7% | 0.96 | -11.7% | 0.83 | 0.56 | 0.29 | 58.8% | 30 |
| momentum only | +10.0% | 10.0% | 0.88 | -18.7% | 0.54 | 0.63 | 0.38 | 67.4% | 36 |
| 200d-MA overlay | +9.9% | 9.1% | 0.95 | -12.6% | 0.78 | 0.60 | 0.35 | 63.4% | 36 |
| static 80/15/5 | +10.0% | 16.4% | 0.59 | -47.8% | 0.21 | 1.00 | 1.00 |  |  |

## Lag years

|  | 2009 | 2012 | 2019 | 2023 | 2026 |
|---|---|---|---|---|---|
| baseline | +15.6% | +0.4% | +9.7% | +8.8% | +4.5% |
| momentum only | +15.8% | +1.9% | +13.4% | +11.7% | +2.3% |
| 200d-MA overlay | +15.6% | +1.2% | +12.3% | +9.8% | +1.2% |
| static 80/15/5 | +30.8% | +14.8% | +29.9% | +26.0% | +8.6% |
| WF[sharpe] |  | +1.2% | +12.3% | +8.8% | +1.2% |
| WF[calmar] |  | +1.2% | +12.3% | +8.8% | +4.5% |
| WF[cagr_dd20] |  | +1.2% | +12.3% | +9.8% | +2.3% |
