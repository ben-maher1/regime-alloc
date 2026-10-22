# Grid: voltarget

Lever family (a/d alt): portfolio vol target instead of per-sleeve partial sizing,
plus the per-sleeve caps (d), which only bind once weight is scaled up.

Hypothesis: partial strengths (score/0.5) leave cash even when the whole book's
risk is low. Normalizing base x strength to a fully-invested shape and sizing the
book to a 10-15% vol target (never above the regime cap, no leverage) should
invest more in calm uptrends and de-risk on its own when vol spikes, so
upside capture rises without giving back the drawdown control.

Grid (regime caps on unless noted):
  target vol   0.10 / 0.12 / 0.15
  x shape      binary (score > 0 -> full base) / scaled (SIGNAL_CAP 0.5)
  caps         IBIT 0.3 / GLDM 0.8 and IBIT 0.4 / GLDM 1.0 at 12% binary
  no regime    12% binary with exposure "none"

## Walk-forward window 2010-01-01+ (grid cells are fixed configs; WF[...] rows re-select the cell each Jan 1 on the expanding window by that objective)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| baseline | +10.2% | 8.8% | 1.00 | -11.7% | 0.88 | 0.58 | 0.33 | 59.8% | 30 |
| tv 10% binary | +10.5% | 8.9% | 1.02 | -12.9% | 0.81 | 0.63 | 0.42 | 64.3% | 18 |
| tv 10% scaled | +10.6% | 8.9% | 1.03 | -13.8% | 0.77 | 0.62 | 0.39 | 64.0% | 32 |
| tv 12% binary | +11.6% | 9.9% | 1.03 | -13.3% | 0.88 | 0.70 | 0.46 | 70.8% | 15 |
| tv 12% scaled | +11.6% | 9.9% | 1.02 | -14.2% | 0.82 | 0.68 | 0.42 | 70.3% | 30 |
| tv 15% binary | +12.3% | 10.6% | 1.02 | -14.3% | 0.86 | 0.74 | 0.48 | 75.0% | 13 |
| tv 15% scaled | +12.3% | 10.6% | 1.02 | -14.2% | 0.87 | 0.72 | 0.45 | 74.4% | 29 |
| tv 12% binary, IBIT .3 GLDM .8 | +11.9% | 10.0% | 1.04 | -13.4% | 0.89 | 0.71 | 0.45 | 70.9% | 16 |
| tv 12% binary, IBIT .4 GLDM 1 | +12.0% | 10.0% | 1.05 | -13.4% | 0.89 | 0.71 | 0.45 | 71.0% | 16 |
| tv 12% binary, no regime | +11.5% | 10.7% | 0.94 | -19.2% | 0.60 | 0.74 | 0.54 | 78.2% | 16 |
| static 80/15/5 | +11.8% | 15.0% | 0.73 | -29.6% | 0.40 | 1.00 | 1.00 |  |  |
| WF[sharpe] | +10.8% | 10.2% | 0.93 | -15.1% | 0.72 | 0.68 | 0.48 |  |  |
| WF[calmar] | +10.0% | 9.1% | 0.94 | -13.8% | 0.72 | 0.61 | 0.41 |  |  |
| WF[cagr_dd20] | +11.1% | 10.6% | 0.92 | -19.2% | 0.58 | 0.70 | 0.50 |  |  |

### Success criteria (walk-forward window, vs baseline)

|  | UpCap+ | CAGR>=11% | DD>=-20% | Sharpe>=base-0.1 | ALL |
|---|---|---|---|---|---|
| baseline | ✗ | ✗ | ✓ | ✓ | ✗ |
| tv 10% binary | ✓ | ✗ | ✓ | ✓ | ✗ |
| tv 10% scaled | ✗ | ✗ | ✓ | ✓ | ✗ |
| tv 12% binary | ✓ | ✓ | ✓ | ✓ | ✓ |
| tv 12% scaled | ✓ | ✓ | ✓ | ✓ | ✓ |
| tv 15% binary | ✓ | ✓ | ✓ | ✓ | ✓ |
| tv 15% scaled | ✓ | ✓ | ✓ | ✓ | ✓ |
| tv 12% binary, IBIT .3 GLDM .8 | ✓ | ✓ | ✓ | ✓ | ✓ |
| tv 12% binary, IBIT .4 GLDM 1 | ✓ | ✓ | ✓ | ✓ | ✓ |
| tv 12% binary, no regime | ✓ | ✓ | ✓ | ✓ | ✓ |
| WF[sharpe] | ✓ | ✗ | ✓ | ✓ | ✗ |
| WF[calmar] | ✗ | ✗ | ✓ | ✓ | ✗ |
| WF[cagr_dd20] | ✓ | ✓ | ✓ | ✓ | ✓ |

### Walk-forward picks per year

|  | sharpe | calmar | cagr_dd20 |
|---|---|---|---|
| 2010 | tv 12% binary, no regime | tv 12% binary, no regime | tv 12% binary, no regime |
| 2011 | tv 12% binary, no regime | tv 12% binary, no regime | tv 12% binary, no regime |
| 2012 | tv 12% binary, no regime | tv 12% binary, no regime | tv 12% binary, no regime |
| 2013 | tv 12% binary, no regime | baseline | tv 12% binary, no regime |
| 2014 | tv 12% binary, no regime | tv 12% binary, no regime | tv 12% binary, no regime |
| 2015 | tv 12% binary, no regime | baseline | tv 15% binary |
| 2016 | baseline | baseline | tv 15% scaled |
| 2017 | tv 12% scaled | tv 10% scaled | tv 15% scaled |
| 2018 | tv 10% scaled | tv 10% scaled | tv 15% scaled |
| 2019 | tv 10% scaled | tv 10% scaled | tv 15% scaled |
| 2020 | tv 10% scaled | tv 10% scaled | tv 12% binary, no regime |
| 2021 | tv 15% binary | baseline | tv 15% scaled |
| 2022 | tv 15% binary | tv 15% scaled | tv 15% binary |
| 2023 | tv 15% binary | baseline | tv 15% binary |
| 2024 | tv 12% binary, IBIT .4 GLDM 1 | tv 12% binary, IBIT .4 GLDM 1 | tv 15% scaled |
| 2025 | tv 12% binary, IBIT .4 GLDM 1 | baseline | tv 15% scaled |
| 2026 | tv 12% binary, IBIT .4 GLDM 1 | baseline | tv 15% binary |

## Full period (in-sample)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| baseline | +9.7% | 8.7% | 0.96 | -11.7% | 0.83 | 0.56 | 0.29 | 58.8% | 30 |
| tv 10% binary | +9.8% | 8.8% | 0.97 | -12.9% | 0.76 | 0.61 | 0.36 | 63.8% | 16 |
| tv 10% scaled | +9.9% | 8.9% | 0.98 | -13.8% | 0.72 | 0.60 | 0.34 | 63.5% | 29 |
| tv 12% binary | +10.9% | 9.8% | 0.98 | -13.3% | 0.82 | 0.67 | 0.39 | 69.8% | 14 |
| tv 12% scaled | +10.9% | 9.8% | 0.98 | -14.2% | 0.77 | 0.66 | 0.37 | 69.4% | 28 |
| tv 15% binary | +11.6% | 10.5% | 0.99 | -14.3% | 0.81 | 0.71 | 0.41 | 73.7% | 12 |
| tv 15% scaled | +11.6% | 10.5% | 0.98 | -14.2% | 0.82 | 0.70 | 0.39 | 73.3% | 27 |
| tv 12% binary, IBIT .3 GLDM .8 | +11.1% | 9.9% | 0.99 | -13.4% | 0.83 | 0.68 | 0.39 | 69.9% | 14 |
| tv 12% binary, IBIT .4 GLDM 1 | +11.2% | 9.9% | 1.00 | -13.4% | 0.83 | 0.68 | 0.39 | 70.0% | 14 |
| tv 12% binary, no regime | +11.2% | 10.6% | 0.94 | -19.2% | 0.58 | 0.73 | 0.46 | 77.0% | 15 |
| static 80/15/5 | +10.0% | 16.4% | 0.59 | -47.8% | 0.21 | 1.00 | 1.00 |  |  |

## Lag years

|  | 2009 | 2012 | 2019 | 2023 | 2026 |
|---|---|---|---|---|---|
| baseline | +15.6% | +0.4% | +9.7% | +8.8% | +4.5% |
| tv 10% binary | +15.0% | +0.4% | +13.1% | +12.5% | +6.7% |
| tv 10% scaled | +14.5% | +0.4% | +12.3% | +14.6% | +6.7% |
| tv 12% binary | +18.5% | +0.2% | +13.6% | +12.3% | +6.5% |
| tv 12% scaled | +18.1% | -0.1% | +12.7% | +13.8% | +6.8% |
| tv 15% binary | +22.5% | -1.2% | +14.3% | +11.9% | +6.7% |
| tv 15% scaled | +21.8% | -1.1% | +13.4% | +13.1% | +6.7% |
| tv 12% binary, IBIT .3 GLDM .8 | +18.5% | +0.2% | +13.6% | +15.0% | +6.5% |
| tv 12% binary, IBIT .4 GLDM 1 | +18.5% | +0.2% | +13.6% | +16.4% | +6.5% |
| tv 12% binary, no regime | +19.1% | +0.5% | +19.8% | +13.3% | +5.3% |
| static 80/15/5 | +30.8% | +14.8% | +29.9% | +26.0% | +8.6% |
| WF[sharpe] |  | +0.5% | +12.3% | +11.9% | +6.5% |
| WF[calmar] |  | +0.5% | +12.3% | +8.8% | +4.5% |
| WF[cagr_dd20] |  | +0.5% | +13.4% | +11.9% | +6.7% |
