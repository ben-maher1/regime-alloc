# Frontier (baseline, combined, reentry, regime, sizing, voltarget): walk-forward window 2010-01-01+

Pareto-efficient fixed configs on (CAGR, MaxDD), plus baseline, benchmark, and WF[...] rows that re-select among *all* configs each Jan 1 on the expanding window (the honest number: fixed cells are picked with hindsight).

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr | CAGR full | MaxDD full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| regime:off 0.25 / up 0.0 | +10.4% | 8.5% | 1.04 | -9.4% | 1.11 | 0.56 | 0.28 | 57.0% | 27 | +9.8% | -10.9% |
| sizing:cap 0.35 | +10.5% | 8.9% | 1.01 | -11.3% | 0.93 | 0.59 | 0.33 | 60.9% | 27 | +10.1% | -11.3% |
| combined:cap.25 off.5 | +10.7% | 9.0% | 1.03 | -11.4% | 0.94 | 0.61 | 0.35 | 61.7% | 24 | +10.3% | -11.4% |
| sizing:cap 0.25 | +10.7% | 9.0% | 1.03 | -11.4% | 0.94 | 0.61 | 0.35 | 61.7% | 24 | +10.3% | -11.4% |
| combined:cap.25 off.5+bo20 | +12.3% | 9.5% | 1.13 | -11.5% | 1.08 | 0.70 | 0.41 | 68.5% | 21 | +11.7% | -11.5% |
| baseline | +10.2% | 8.8% | 1.00 | -11.7% | 0.88 | 0.58 | 0.33 | 59.8% | 30 | +9.7% | -11.7% |
| WF[sharpe] | +11.3% | 9.4% | 1.04 | -12.3% | 0.91 | 0.66 | 0.40 |  |  |  |  |
| sizing:zero cap 0.25 | +12.4% | 10.8% | 1.01 | -12.9% | 0.96 | 0.73 | 0.46 | 74.5% | 28 | +11.6% | -14.9% |
| combined:norm.25 off.5 | +13.0% | 11.0% | 1.04 | -14.3% | 0.91 | 0.76 | 0.47 | 76.8% | 22 | +12.4% | -14.3% |
| sizing:normalize cap 0.25 | +13.0% | 11.0% | 1.04 | -14.3% | 0.91 | 0.76 | 0.47 | 76.8% | 22 | +12.4% | -14.3% |
| sizing:normalize cap 0.5 | +13.0% | 11.1% | 1.04 | -14.4% | 0.91 | 0.75 | 0.46 | 76.5% | 27 | +12.4% | -14.4% |
| WF[calmar] | +11.5% | 9.9% | 1.02 | -17.5% | 0.66 | 0.70 | 0.47 |  |  |  |  |
| combined:norm.25 off.75/up0 | +13.2% | 11.8% | 1.00 | -17.9% | 0.74 | 0.80 | 0.54 | 82.8% | 24 | +12.9% | -17.9% |
| combined:norm.25 off.5+bo20 | +13.8% | 11.1% | 1.11 | -18.1% | 0.76 | 0.82 | 0.52 | 79.7% | 21 | +13.0% | -18.1% |
| WF[cagr_dd20] | +12.2% | 11.7% | 0.93 | -19.0% | 0.64 | 0.80 | 0.61 |  |  |  |  |
| combined:norm.25 off.75/up0+bo20 | +14.1% | 12.0% | 1.05 | -19.1% | 0.74 | 0.88 | 0.62 | 87.4% | 22 | +13.6% | -19.1% |
| static 80/15/5 | +11.8% | 15.0% | 0.73 | -29.6% | 0.40 | 1.00 | 1.00 |  |  | +10.0% | -47.8% |

## Criteria

|  | UpCap+ | CAGR>=11% | DD>=-20% | Sharpe>=base-0.1 | ALL |
|---|---|---|---|---|---|
| regime:off 0.25 / up 0.0 | ✗ | ✗ | ✓ | ✓ | ✗ |
| sizing:cap 0.35 | ✗ | ✗ | ✓ | ✓ | ✗ |
| combined:cap.25 off.5 | ✗ | ✗ | ✓ | ✓ | ✗ |
| sizing:cap 0.25 | ✗ | ✗ | ✓ | ✓ | ✗ |
| combined:cap.25 off.5+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| baseline | ✗ | ✗ | ✓ | ✓ | ✗ |
| WF[sharpe] | ✓ | ✓ | ✓ | ✓ | ✓ |
| sizing:zero cap 0.25 | ✓ | ✓ | ✓ | ✓ | ✓ |
| combined:norm.25 off.5 | ✓ | ✓ | ✓ | ✓ | ✓ |
| sizing:normalize cap 0.25 | ✓ | ✓ | ✓ | ✓ | ✓ |
| sizing:normalize cap 0.5 | ✓ | ✓ | ✓ | ✓ | ✓ |
| WF[calmar] | ✓ | ✓ | ✓ | ✓ | ✓ |
| combined:norm.25 off.75/up0 | ✓ | ✓ | ✓ | ✓ | ✓ |
| combined:norm.25 off.5+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| WF[cagr_dd20] | ✓ | ✓ | ✓ | ✓ | ✓ |
| combined:norm.25 off.75/up0+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| static 80/15/5 | ✓ | ✓ | ✗ | ✗ | ✗ |

## Walk-forward picks per year

|  | sharpe | calmar | cagr_dd20 |
|---|---|---|---|
| 2010 | combined:binary off.75/up0 | baseline:200d-MA overlay | combined:norm.25 off.75/up0 |
| 2011 | combined:binary off.75/up0 | combined:binary off.75/up0+bo20 | combined:norm.25 off.75/up0+bo20 |
| 2012 | sizing:cap 0.1 | combined:binary off.75/up0 | combined:norm.25 off.75/up0 |
| 2013 | sizing:cap 0.1 | combined:binary off.75/up0 | combined:binary off.75/up0+bo20 |
| 2014 | sizing:cap 0.1 | combined:binary off.75/up0 | combined:norm.25 off.75/up0 |
| 2015 | sizing:cap 0.1 | combined:binary off.75/up0 | combined:norm.25 off.75/up0 |
| 2016 | sizing:cap 0.1 | combined:binary off.75/up0 | combined:norm.25 off.75/up0 |
| 2017 | sizing:cap 0.1 | combined:binary off.75/up0 | combined:norm.25 off.75/up0+bo20 |
| 2018 | sizing:cap 0.1 | combined:binary off.75/up0 | combined:norm.25 off.75/up0+bo20 |
| 2019 | sizing:cap 0.1 | combined:binary off.75/up0 | combined:norm.25 off.75/up0 |
| 2020 | combined:binary off.5+bo20 | combined:binary off.75/up0 | combined:norm.25 off.75/up0+bo20 |
| 2021 | combined:binary off.5+bo20 | combined:cap.25 off.5+bo20 | combined:norm.25 off.75/up0+bo20 |
| 2022 | combined:cap.25 off.5+bo20 | combined:cap.25 off.5+bo20 | combined:norm.25 off.75/up0+bo20 |
| 2023 | sizing:cap 0.1 | combined:cap.25 off.5+bo20 | combined:norm.25 off.75/up0 |
| 2024 | combined:cap.25 off.5+bo20 | combined:cap.25 off.5+bo20 | combined:norm.25 off.75/up0+bo20 |
| 2025 | combined:cap.25 off.5+bo20 | combined:cap.25 off.5+bo20 | combined:norm.25 off.75/up0+bo20 |
| 2026 | combined:cap.25 off.5+bo20 | combined:cap.25 off.5+bo20 | combined:norm.25 off.75/up0+bo20 |

## Lag years

|  | 2009 | 2012 | 2019 | 2023 | 2026 |
|---|---|---|---|---|---|
| regime:off 0.25 / up 0.0 | +18.2% | +1.5% | +8.2% | +7.9% | +4.3% |
| sizing:cap 0.35 | +18.4% | +0.9% | +9.5% | +8.5% | +4.0% |
| combined:cap.25 off.5 | +20.0% | +1.2% | +10.0% | +8.0% | +3.4% |
| sizing:cap 0.25 | +20.0% | +1.2% | +10.0% | +8.0% | +3.4% |
| combined:cap.25 off.5+bo20 | +22.0% | +4.8% | +13.6% | +16.7% | +6.8% |
| baseline | +15.6% | +0.4% | +9.7% | +8.8% | +4.5% |
| sizing:zero cap 0.25 | +21.6% | -0.4% | +14.1% | +10.5% | +4.5% |
| combined:norm.25 off.5 | +27.4% | -1.3% | +13.3% | +11.4% | +5.7% |
| sizing:normalize cap 0.25 | +27.4% | -1.3% | +13.3% | +11.4% | +5.7% |
| sizing:normalize cap 0.5 | +27.7% | -1.9% | +13.4% | +11.6% | +7.2% |
| combined:norm.25 off.75/up0 | +31.8% | +0.9% | +16.7% | +13.4% | +4.3% |
| combined:norm.25 off.5+bo20 | +31.0% | +2.1% | +17.1% | +19.0% | +8.7% |
| combined:norm.25 off.75/up0+bo20 | +35.6% | +4.0% | +24.2% | +22.8% | +7.6% |
| static 80/15/5 | +30.8% | +14.8% | +29.9% | +26.0% | +8.6% |
| WF[sharpe] |  | +1.0% | +10.8% | +6.8% | +6.8% |
| WF[calmar] |  | +1.8% | +15.8% | +16.7% | +6.8% |
| WF[cagr_dd20] |  | +0.9% | +16.7% | +13.4% | +7.6% |

## All configs (walk-forward window)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr | efficient |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline | +10.2% | 8.8% | 1.00 | -11.7% | 0.88 | 0.58 | 0.33 | 59.8% | 30 | ✗ |
| baseline:momentum only | +10.4% | 10.0% | 0.91 | -18.7% | 0.56 | 0.64 | 0.43 | 67.9% | 36 | ✗ |
| baseline:200d-MA overlay | +9.9% | 9.2% | 0.93 | -12.6% | 0.78 | 0.60 | 0.40 | 64.4% | 36 | ✗ |
| combined:cap.5 off.5+bo20 | +12.1% | 9.4% | 1.12 | -11.6% | 1.04 | 0.69 | 0.40 | 67.5% | 25 | ✗ |
| combined:cap.5 off.75/up0 | +10.3% | 9.4% | 0.96 | -14.5% | 0.71 | 0.61 | 0.38 | 64.3% | 35 | ✗ |
| combined:cap.5 off.75/up0+bo20 | +12.7% | 10.1% | 1.10 | -14.5% | 0.87 | 0.74 | 0.47 | 74.0% | 27 | ✗ |
| combined:cap.25 off.5 | +10.7% | 9.0% | 1.03 | -11.4% | 0.94 | 0.61 | 0.35 | 61.7% | 24 | ✓ |
| combined:cap.25 off.5+bo20 | +12.3% | 9.5% | 1.13 | -11.5% | 1.08 | 0.70 | 0.41 | 68.5% | 21 | ✓ |
| combined:cap.25 off.75/up0 | +11.0% | 9.6% | 0.99 | -15.4% | 0.71 | 0.65 | 0.41 | 66.8% | 26 | ✗ |
| combined:cap.25 off.75/up0+bo20 | +12.7% | 10.3% | 1.09 | -15.4% | 0.83 | 0.76 | 0.49 | 75.1% | 23 | ✗ |
| combined:binary off.5 | +11.5% | 9.2% | 1.08 | -11.6% | 0.99 | 0.65 | 0.37 | 63.7% | 11 | ✗ |
| combined:binary off.5+bo20 | +12.2% | 9.6% | 1.11 | -12.8% | 0.95 | 0.71 | 0.43 | 69.7% | 14 | ✗ |
| combined:binary off.75/up0 | +11.7% | 9.9% | 1.03 | -17.5% | 0.67 | 0.70 | 0.44 | 69.1% | 12 | ✗ |
| combined:binary off.75/up0+bo20 | +12.5% | 10.5% | 1.05 | -17.5% | 0.71 | 0.77 | 0.53 | 76.5% | 15 | ✗ |
| combined:norm.25 off.5 | +13.0% | 11.0% | 1.04 | -14.3% | 0.91 | 0.76 | 0.47 | 76.8% | 22 | ✓ |
| combined:norm.25 off.5+bo20 | +13.8% | 11.1% | 1.11 | -18.1% | 0.76 | 0.82 | 0.52 | 79.7% | 21 | ✓ |
| combined:norm.25 off.75/up0 | +13.2% | 11.8% | 1.00 | -17.9% | 0.74 | 0.80 | 0.54 | 82.8% | 24 | ✓ |
| combined:norm.25 off.75/up0+bo20 | +14.1% | 12.0% | 1.05 | -19.1% | 0.74 | 0.88 | 0.62 | 87.4% | 22 | ✓ |
| combined:tv12 off.5 | +11.6% | 9.9% | 1.03 | -13.3% | 0.88 | 0.70 | 0.46 | 70.8% | 15 | ✗ |
| combined:tv12 off.5+bo20 | +11.6% | 9.8% | 1.03 | -16.8% | 0.69 | 0.73 | 0.51 | 73.6% | 18 | ✗ |
| combined:tv12 off.75/up0 | +11.8% | 10.5% | 0.99 | -17.8% | 0.66 | 0.73 | 0.51 | 75.7% | 16 | ✗ |
| combined:tv12 off.75/up0+bo20 | +11.9% | 10.6% | 0.99 | -19.1% | 0.62 | 0.78 | 0.58 | 79.7% | 19 | ✗ |
| reentry:breakout 20d -> 0.5 | +10.9% | 8.9% | 1.06 | -11.6% | 0.94 | 0.62 | 0.36 | 63.0% | 29 | ✗ |
| reentry:breakout 20d -> 1.0 | +12.1% | 9.4% | 1.12 | -11.6% | 1.04 | 0.69 | 0.40 | 67.5% | 25 | ✗ |
| reentry:breakout 50d -> 0.5 | +10.5% | 8.9% | 1.02 | -11.7% | 0.90 | 0.60 | 0.35 | 61.6% | 26 | ✗ |
| reentry:breakout 50d -> 1.0 | +11.1% | 9.2% | 1.04 | -11.7% | 0.95 | 0.64 | 0.39 | 64.6% | 20 | ✗ |
| reentry:fast blend 0.25 | +9.8% | 8.3% | 1.00 | -12.6% | 0.77 | 0.56 | 0.34 | 56.8% | 44 | ✗ |
| reentry:fast blend 0.5 | +9.4% | 8.1% | 0.98 | -14.1% | 0.66 | 0.54 | 0.32 | 54.4% | 44 | ✗ |
| reentry:smoothing 5 | +10.3% | 8.6% | 1.03 | -10.4% | 0.99 | 0.56 | 0.29 | 57.8% | 38 | ✗ |
| reentry:smoothing 2 | +9.7% | 8.3% | 0.99 | -13.0% | 0.74 | 0.55 | 0.32 | 56.8% | 43 | ✗ |
| regime:off 0.25 / up 0.15 | +10.2% | 8.4% | 1.04 | -9.4% | 1.09 | 0.55 | 0.27 | 55.6% | 26 | ✗ |
| regime:off 0.25 / up 0.05 | +10.2% | 8.5% | 1.03 | -9.4% | 1.09 | 0.55 | 0.28 | 56.6% | 26 | ✗ |
| regime:off 0.25 / up 0.0 | +10.4% | 8.5% | 1.04 | -9.4% | 1.11 | 0.56 | 0.28 | 57.0% | 27 | ✓ |
| regime:off 0.5 / up 0.05 | +10.2% | 8.8% | 1.00 | -11.7% | 0.87 | 0.58 | 0.33 | 60.4% | 31 | ✗ |
| regime:off 0.5 / up 0.0 | +10.3% | 8.8% | 1.00 | -11.7% | 0.88 | 0.58 | 0.33 | 60.7% | 31 | ✗ |
| regime:off 0.75 / up 0.15 | +10.3% | 9.3% | 0.96 | -14.5% | 0.71 | 0.60 | 0.37 | 63.9% | 34 | ✗ |
| regime:off 0.75 / up 0.05 | +10.3% | 9.3% | 0.95 | -14.5% | 0.71 | 0.61 | 0.38 | 64.2% | 34 | ✗ |
| regime:off 0.75 / up 0.0 | +10.3% | 9.4% | 0.96 | -14.5% | 0.71 | 0.61 | 0.38 | 64.3% | 35 | ✗ |
| regime:off 1.0 / up 0.15 | +10.4% | 10.0% | 0.91 | -18.7% | 0.56 | 0.64 | 0.43 | 67.9% | 36 | ✗ |
| regime:hl 2 / up 0.15 | +9.5% | 8.6% | 0.95 | -10.6% | 0.90 | 0.55 | 0.32 | 59.4% | 31 | ✗ |
| regime:hl 2 / up 0.0 | +9.6% | 8.7% | 0.94 | -10.6% | 0.90 | 0.55 | 0.33 | 60.8% | 32 | ✗ |
| sizing:cap 0.35 | +10.5% | 8.9% | 1.01 | -11.3% | 0.93 | 0.59 | 0.33 | 60.9% | 27 | ✓ |
| sizing:cap 0.25 | +10.7% | 9.0% | 1.03 | -11.4% | 0.94 | 0.61 | 0.35 | 61.7% | 24 | ✓ |
| sizing:cap 0.1 | +11.0% | 9.1% | 1.05 | -11.6% | 0.95 | 0.62 | 0.35 | 62.8% | 17 | ✗ |
| sizing:binary | +11.5% | 9.2% | 1.08 | -11.6% | 0.99 | 0.65 | 0.37 | 63.7% | 11 | ✗ |
| sizing:floor 0.25 >200d | +10.4% | 8.8% | 1.02 | -11.7% | 0.89 | 0.59 | 0.33 | 60.6% | 33 | ✗ |
| sizing:floor 0.5 >200d | +10.5% | 8.9% | 1.02 | -11.7% | 0.90 | 0.60 | 0.35 | 61.8% | 30 | ✗ |
| sizing:floor 1.0 >200d | +11.1% | 9.2% | 1.04 | -12.1% | 0.92 | 0.64 | 0.39 | 65.6% | 24 | ✗ |
| sizing:floor 0.5 score>0 | +10.6% | 8.9% | 1.03 | -11.9% | 0.89 | 0.59 | 0.33 | 60.5% | 24 | ✗ |
| sizing:zero cap 0.5 | +11.9% | 10.6% | 0.99 | -13.5% | 0.88 | 0.70 | 0.43 | 72.0% | 37 | ✗ |
| sizing:zero cap 0.25 | +12.4% | 10.8% | 1.01 | -12.9% | 0.96 | 0.73 | 0.46 | 74.5% | 28 | ✓ |
| sizing:normalize cap 0.5 | +13.0% | 11.1% | 1.04 | -14.4% | 0.91 | 0.75 | 0.46 | 76.5% | 27 | ✓ |
| sizing:normalize cap 0.25 | +13.0% | 11.0% | 1.04 | -14.3% | 0.91 | 0.76 | 0.47 | 76.8% | 22 | ✓ |
| voltarget:tv 10% binary | +10.5% | 8.9% | 1.02 | -12.9% | 0.81 | 0.63 | 0.42 | 64.3% | 18 | ✗ |
| voltarget:tv 10% scaled | +10.6% | 8.9% | 1.03 | -13.8% | 0.77 | 0.62 | 0.39 | 64.0% | 32 | ✗ |
| voltarget:tv 12% binary | +11.6% | 9.9% | 1.03 | -13.3% | 0.88 | 0.70 | 0.46 | 70.8% | 15 | ✗ |
| voltarget:tv 12% scaled | +11.6% | 9.9% | 1.02 | -14.2% | 0.82 | 0.68 | 0.42 | 70.3% | 30 | ✗ |
| voltarget:tv 15% binary | +12.3% | 10.6% | 1.02 | -14.3% | 0.86 | 0.74 | 0.48 | 75.0% | 13 | ✗ |
| voltarget:tv 15% scaled | +12.3% | 10.6% | 1.02 | -14.2% | 0.87 | 0.72 | 0.45 | 74.4% | 29 | ✗ |
| voltarget:tv 12% binary, IBIT .3 GLDM .8 | +11.9% | 10.0% | 1.04 | -13.4% | 0.89 | 0.71 | 0.45 | 70.9% | 16 | ✗ |
| voltarget:tv 12% binary, IBIT .4 GLDM 1 | +12.0% | 10.0% | 1.05 | -13.4% | 0.89 | 0.71 | 0.45 | 71.0% | 16 | ✗ |
| voltarget:tv 12% binary, no regime | +11.5% | 10.7% | 0.94 | -19.2% | 0.60 | 0.74 | 0.54 | 78.2% | 16 | ✗ |
| static 80/15/5 | +11.8% | 15.0% | 0.73 | -29.6% | 0.40 | 1.00 | 1.00 |  |  | ✗ |
| WF[sharpe] | +11.3% | 9.4% | 1.04 | -12.3% | 0.91 | 0.66 | 0.40 |  |  | ✗ |
| WF[calmar] | +11.5% | 9.9% | 1.02 | -17.5% | 0.66 | 0.70 | 0.47 |  |  | ✗ |
| WF[cagr_dd20] | +12.2% | 11.7% | 0.93 | -19.0% | 0.64 | 0.80 | 0.61 |  |  | ✗ |
