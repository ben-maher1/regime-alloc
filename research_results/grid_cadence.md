# Grid: cadence

Lever family: rebalance cadence and band, on the current production system.

Hypothesis: about 22 trades a year includes a lot of churn (2023: 36 trades,
several gold in-out-in round trips). Deciding less often, or only trading when
a sleeve drifts further from target, should cut turnover at no cost to
CAGR/Sharpe/MaxDD. The exploratory check vs 60/30/10 (EXPERIMENTS.md
2026-10-23) suggested weekly or a 10-point band do this; this is the
walk-forward test. "baseline" here is PRODUCTION (daily, 5-point band), not
the pre-study system.

Grid (production signals throughout):
  daily     band 0.05 (production) / 0.075 / 0.10 / 0.15
  weekly    band 0.05 / 0.075 / 0.10   (targets updated on Fridays only)
  monthly   band 0.05                  (context: how far can cadence go?)

## Walk-forward window 2010-01-01+ (grid cells are fixed configs; WF[...] rows re-select the cell each Jan 1 on the expanding window by that objective)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| baseline | +13.8% | 11.1% | 1.10 | -18.1% | 0.76 | 0.81 | 0.52 | 79.5% | 24 |
| daily band 0.075 | +13.9% | 11.1% | 1.10 | -18.4% | 0.75 | 0.81 | 0.51 | 79.5% | 19 |
| daily band 0.1 | +14.2% | 11.2% | 1.12 | -18.3% | 0.78 | 0.82 | 0.50 | 79.6% | 15 |
| daily band 0.15 | +13.6% | 11.3% | 1.06 | -18.7% | 0.73 | 0.81 | 0.52 | 79.7% | 12 |
| weekly band 0.05 | +13.8% | 11.2% | 1.09 | -17.5% | 0.79 | 0.81 | 0.51 | 79.5% | 16 |
| weekly band 0.075 | +14.2% | 11.2% | 1.12 | -17.7% | 0.80 | 0.82 | 0.51 | 79.6% | 14 |
| weekly band 0.1 | +13.7% | 11.3% | 1.08 | -17.7% | 0.77 | 0.81 | 0.52 | 79.6% | 12 |
| monthly band 0.05 | +12.2% | 11.5% | 0.94 | -18.3% | 0.67 | 0.76 | 0.53 | 79.9% | 9 |
| static 80/15/5 | +11.8% | 15.0% | 0.73 | -29.6% | 0.40 | 1.00 | 1.00 |  |  |
| static 60/30/10 | +13.7% | 14.5% | 0.87 | -27.5% | 0.50 | 1.04 | 0.94 |  |  |
| WF[sharpe] | +13.7% | 11.2% | 1.09 | -17.7% | 0.77 | 0.81 | 0.52 |  |  |
| WF[calmar] | +13.8% | 11.2% | 1.09 | -18.4% | 0.75 | 0.81 | 0.52 |  |  |
| WF[cagr_dd20] | +14.0% | 11.2% | 1.11 | -17.7% | 0.79 | 0.82 | 0.52 |  |  |

### Success criteria (walk-forward window, vs baseline)

|  | UpCap+ | CAGR>=11% | DD>=-20% | Sharpe>=base-0.1 | ALL |
|---|---|---|---|---|---|
| baseline | ✗ | ✓ | ✓ | ✓ | ✗ |
| daily band 0.075 | ✗ | ✓ | ✓ | ✓ | ✗ |
| daily band 0.1 | ✗ | ✓ | ✓ | ✓ | ✗ |
| daily band 0.15 | ✗ | ✓ | ✓ | ✓ | ✗ |
| weekly band 0.05 | ✗ | ✓ | ✓ | ✓ | ✗ |
| weekly band 0.075 | ✗ | ✓ | ✓ | ✓ | ✗ |
| weekly band 0.1 | ✗ | ✓ | ✓ | ✓ | ✗ |
| monthly band 0.05 | ✗ | ✓ | ✓ | ✗ | ✗ |
| static 60/30/10 | ✓ | ✓ | ✗ | ✗ | ✗ |
| WF[sharpe] | ✗ | ✓ | ✓ | ✓ | ✗ |
| WF[calmar] | ✗ | ✓ | ✓ | ✓ | ✗ |
| WF[cagr_dd20] | ✗ | ✓ | ✓ | ✓ | ✗ |

### Walk-forward picks per year

|  | sharpe | calmar | cagr_dd20 |
|---|---|---|---|
| 2010 | weekly band 0.1 | daily band 0.075 | weekly band 0.1 |
| 2011 | weekly band 0.1 | daily band 0.075 | weekly band 0.1 |
| 2012 | weekly band 0.1 | daily band 0.075 | weekly band 0.1 |
| 2013 | weekly band 0.1 | weekly band 0.1 | weekly band 0.1 |
| 2014 | weekly band 0.1 | weekly band 0.1 | weekly band 0.1 |
| 2015 | weekly band 0.1 | weekly band 0.1 | weekly band 0.1 |
| 2016 | weekly band 0.1 | weekly band 0.05 | weekly band 0.1 |
| 2017 | daily band 0.1 | weekly band 0.05 | daily band 0.1 |
| 2018 | daily band 0.1 | daily band 0.1 | daily band 0.1 |
| 2019 | daily band 0.1 | weekly band 0.075 | daily band 0.1 |
| 2020 | daily band 0.1 | weekly band 0.075 | weekly band 0.075 |
| 2021 | daily band 0.075 | weekly band 0.05 | weekly band 0.075 |
| 2022 | weekly band 0.075 | weekly band 0.075 | weekly band 0.075 |
| 2023 | weekly band 0.075 | weekly band 0.075 | weekly band 0.075 |
| 2024 | weekly band 0.075 | weekly band 0.075 | weekly band 0.075 |
| 2025 | weekly band 0.075 | weekly band 0.075 | weekly band 0.075 |
| 2026 | weekly band 0.075 | weekly band 0.075 | weekly band 0.075 |

## Full period (in-sample)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| baseline | +13.0% | 11.1% | 1.04 | -18.1% | 0.72 | 0.79 | 0.45 | 78.2% | 22 |
| daily band 0.075 | +13.1% | 11.2% | 1.05 | -18.4% | 0.71 | 0.79 | 0.44 | 78.2% | 18 |
| daily band 0.1 | +13.4% | 11.2% | 1.06 | -18.3% | 0.73 | 0.79 | 0.44 | 78.3% | 14 |
| daily band 0.15 | +12.9% | 11.3% | 1.02 | -18.7% | 0.69 | 0.78 | 0.45 | 78.3% | 11 |
| weekly band 0.05 | +13.1% | 11.2% | 1.05 | -17.5% | 0.75 | 0.79 | 0.45 | 78.1% | 15 |
| weekly band 0.075 | +13.4% | 11.2% | 1.07 | -17.7% | 0.76 | 0.80 | 0.45 | 78.2% | 13 |
| weekly band 0.1 | +13.1% | 11.3% | 1.04 | -17.7% | 0.74 | 0.79 | 0.46 | 78.2% | 12 |
| monthly band 0.05 | +11.4% | 11.5% | 0.90 | -21.8% | 0.53 | 0.75 | 0.49 | 78.7% | 8 |
| static 80/15/5 | +10.0% | 16.4% | 0.59 | -47.8% | 0.21 | 1.00 | 1.00 |  |  |
| static 60/30/10 | +12.3% | 15.6% | 0.75 | -41.1% | 0.30 | 1.04 | 0.91 |  |  |

## Lag years

|  | 2009 | 2012 | 2019 | 2023 | 2026 |
|---|---|---|---|---|---|
| baseline | +32.6% | +1.9% | +17.3% | +20.5% | +9.6% |
| daily band 0.075 | +32.2% | +1.5% | +17.7% | +20.7% | +9.0% |
| daily band 0.1 | +32.4% | +2.2% | +16.2% | +20.6% | +10.9% |
| daily band 0.15 | +31.0% | +2.2% | +16.7% | +21.3% | +10.1% |
| weekly band 0.05 | +34.0% | -0.5% | +18.6% | +21.8% | +4.6% |
| weekly band 0.075 | +34.0% | -0.8% | +18.6% | +21.8% | +4.9% |
| weekly band 0.1 | +33.7% | -0.6% | +17.2% | +21.4% | +4.6% |
| monthly band 0.05 | +21.4% | -3.7% | +19.0% | +14.8% | +4.0% |
| static 80/15/5 | +30.8% | +14.8% | +29.9% | +26.0% | +8.6% |
| WF[sharpe] |  | -0.6% | +16.2% | +21.8% | +4.9% |
| WF[calmar] |  | +1.5% | +18.6% | +21.8% | +4.9% |
| WF[cagr_dd20] |  | -0.6% | +16.2% | +21.8% | +4.9% |
