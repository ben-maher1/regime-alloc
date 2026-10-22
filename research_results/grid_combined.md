# Grid: combined

Cross-family factorial for the CAGR-vs-MaxDD frontier.

Each family's grid shows where its own lever is flat. This crosses the
plausible settings of each lever (round numbers, not best cells) so the
interactions show up: e.g. does a breakout floor still help once the cash drag
is gone, and do the regime caps still pay for themselves under a vol target?

  sizing   cap 0.5 (base) / cap 0.25 / binary / normalize cap 0.25 / vol target 12% binary
  regime   risk-off 0.5 symmetric (base) / risk-off 0.75 with risk-on flip at 0
  reentry  none / 20d breakout -> full strength

## Walk-forward window 2010-01-01+ (grid cells are fixed configs; WF[...] rows re-select the cell each Jan 1 on the expanding window by that objective)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| baseline | +10.2% | 8.8% | 1.00 | -11.7% | 0.88 | 0.58 | 0.33 | 59.8% | 30 |
| cap.5 off.5+bo20 | +12.1% | 9.4% | 1.12 | -11.6% | 1.04 | 0.69 | 0.40 | 67.5% | 25 |
| cap.5 off.75/up0 | +10.3% | 9.4% | 0.96 | -14.5% | 0.71 | 0.61 | 0.38 | 64.3% | 35 |
| cap.5 off.75/up0+bo20 | +12.7% | 10.1% | 1.10 | -14.5% | 0.87 | 0.74 | 0.47 | 74.0% | 27 |
| cap.25 off.5 | +10.7% | 9.0% | 1.03 | -11.4% | 0.94 | 0.61 | 0.35 | 61.7% | 24 |
| cap.25 off.5+bo20 | +12.3% | 9.5% | 1.13 | -11.5% | 1.08 | 0.70 | 0.41 | 68.5% | 21 |
| cap.25 off.75/up0 | +11.0% | 9.6% | 0.99 | -15.4% | 0.71 | 0.65 | 0.41 | 66.8% | 26 |
| cap.25 off.75/up0+bo20 | +12.7% | 10.3% | 1.09 | -15.4% | 0.83 | 0.76 | 0.49 | 75.1% | 23 |
| binary off.5 | +11.5% | 9.2% | 1.08 | -11.6% | 0.99 | 0.65 | 0.37 | 63.7% | 11 |
| binary off.5+bo20 | +12.2% | 9.6% | 1.11 | -12.8% | 0.95 | 0.71 | 0.43 | 69.7% | 14 |
| binary off.75/up0 | +11.7% | 9.9% | 1.03 | -17.5% | 0.67 | 0.70 | 0.44 | 69.1% | 12 |
| binary off.75/up0+bo20 | +12.5% | 10.5% | 1.05 | -17.5% | 0.71 | 0.77 | 0.53 | 76.5% | 15 |
| norm.25 off.5 | +13.0% | 11.0% | 1.04 | -14.3% | 0.91 | 0.76 | 0.47 | 76.8% | 22 |
| norm.25 off.5+bo20 | +13.8% | 11.1% | 1.11 | -18.1% | 0.76 | 0.82 | 0.52 | 79.7% | 21 |
| norm.25 off.75/up0 | +13.2% | 11.8% | 1.00 | -17.9% | 0.74 | 0.80 | 0.54 | 82.8% | 24 |
| norm.25 off.75/up0+bo20 | +14.1% | 12.0% | 1.05 | -19.1% | 0.74 | 0.88 | 0.62 | 87.4% | 22 |
| tv12 off.5 | +11.6% | 9.9% | 1.03 | -13.3% | 0.88 | 0.70 | 0.46 | 70.8% | 15 |
| tv12 off.5+bo20 | +11.6% | 9.8% | 1.03 | -16.8% | 0.69 | 0.73 | 0.51 | 73.6% | 18 |
| tv12 off.75/up0 | +11.8% | 10.5% | 0.99 | -17.8% | 0.66 | 0.73 | 0.51 | 75.7% | 16 |
| tv12 off.75/up0+bo20 | +11.9% | 10.6% | 0.99 | -19.1% | 0.62 | 0.78 | 0.58 | 79.7% | 19 |
| static 80/15/5 | +11.8% | 15.0% | 0.73 | -29.6% | 0.40 | 1.00 | 1.00 |  |  |
| WF[sharpe] | +11.4% | 9.5% | 1.03 | -12.9% | 0.88 | 0.67 | 0.42 |  |  |
| WF[calmar] | +11.9% | 10.0% | 1.04 | -17.5% | 0.68 | 0.71 | 0.46 |  |  |
| WF[cagr_dd20] | +12.2% | 11.7% | 0.93 | -19.0% | 0.64 | 0.80 | 0.61 |  |  |

### Success criteria (walk-forward window, vs baseline)

|  | UpCap+ | CAGR>=11% | DD>=-20% | Sharpe>=base-0.1 | ALL |
|---|---|---|---|---|---|
| baseline | ✗ | ✗ | ✓ | ✓ | ✗ |
| cap.5 off.5+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| cap.5 off.75/up0 | ✗ | ✗ | ✓ | ✓ | ✗ |
| cap.5 off.75/up0+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| cap.25 off.5 | ✗ | ✗ | ✓ | ✓ | ✗ |
| cap.25 off.5+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| cap.25 off.75/up0 | ✓ | ✗ | ✓ | ✓ | ✗ |
| cap.25 off.75/up0+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| binary off.5 | ✓ | ✓ | ✓ | ✓ | ✓ |
| binary off.5+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| binary off.75/up0 | ✓ | ✓ | ✓ | ✓ | ✓ |
| binary off.75/up0+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| norm.25 off.5 | ✓ | ✓ | ✓ | ✓ | ✓ |
| norm.25 off.5+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| norm.25 off.75/up0 | ✓ | ✓ | ✓ | ✓ | ✓ |
| norm.25 off.75/up0+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| tv12 off.5 | ✓ | ✓ | ✓ | ✓ | ✓ |
| tv12 off.5+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| tv12 off.75/up0 | ✓ | ✓ | ✓ | ✓ | ✓ |
| tv12 off.75/up0+bo20 | ✓ | ✓ | ✓ | ✓ | ✓ |
| WF[sharpe] | ✓ | ✓ | ✓ | ✓ | ✓ |
| WF[calmar] | ✓ | ✓ | ✓ | ✓ | ✓ |
| WF[cagr_dd20] | ✓ | ✓ | ✓ | ✓ | ✓ |

### Walk-forward picks per year

|  | sharpe | calmar | cagr_dd20 |
|---|---|---|---|
| 2010 | binary off.75/up0 | binary off.75/up0 | norm.25 off.75/up0 |
| 2011 | binary off.75/up0 | binary off.75/up0+bo20 | norm.25 off.75/up0+bo20 |
| 2012 | binary off.5 | binary off.75/up0 | norm.25 off.75/up0 |
| 2013 | binary off.5+bo20 | binary off.75/up0 | binary off.75/up0+bo20 |
| 2014 | binary off.5 | binary off.75/up0 | norm.25 off.75/up0 |
| 2015 | binary off.5 | binary off.75/up0 | norm.25 off.75/up0 |
| 2016 | cap.25 off.5+bo20 | binary off.75/up0 | norm.25 off.75/up0 |
| 2017 | cap.25 off.5+bo20 | binary off.75/up0 | norm.25 off.75/up0+bo20 |
| 2018 | binary off.5+bo20 | binary off.75/up0 | norm.25 off.75/up0+bo20 |
| 2019 | binary off.5+bo20 | binary off.75/up0 | norm.25 off.75/up0 |
| 2020 | binary off.5+bo20 | binary off.75/up0 | norm.25 off.75/up0+bo20 |
| 2021 | binary off.5+bo20 | cap.25 off.5+bo20 | norm.25 off.75/up0+bo20 |
| 2022 | cap.25 off.5+bo20 | cap.25 off.5+bo20 | norm.25 off.75/up0+bo20 |
| 2023 | binary off.5 | cap.25 off.5+bo20 | norm.25 off.75/up0 |
| 2024 | cap.25 off.5+bo20 | cap.25 off.5+bo20 | norm.25 off.75/up0+bo20 |
| 2025 | cap.25 off.5+bo20 | cap.25 off.5+bo20 | norm.25 off.75/up0+bo20 |
| 2026 | cap.25 off.5+bo20 | cap.25 off.5+bo20 | norm.25 off.75/up0+bo20 |

## Full period (in-sample)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| baseline | +9.7% | 8.7% | 0.96 | -11.7% | 0.83 | 0.56 | 0.29 | 58.8% | 30 |
| cap.5 off.5+bo20 | +11.4% | 9.3% | 1.08 | -11.6% | 0.98 | 0.66 | 0.35 | 65.9% | 25 |
| cap.5 off.75/up0 | +9.9% | 9.3% | 0.93 | -14.5% | 0.68 | 0.60 | 0.33 | 63.6% | 34 |
| cap.5 off.75/up0+bo20 | +12.1% | 10.2% | 1.05 | -14.5% | 0.83 | 0.72 | 0.40 | 72.6% | 27 |
| cap.25 off.5 | +10.3% | 8.9% | 1.01 | -11.4% | 0.90 | 0.59 | 0.30 | 60.8% | 23 |
| cap.25 off.5+bo20 | +11.7% | 9.4% | 1.09 | -11.5% | 1.02 | 0.68 | 0.35 | 66.9% | 20 |
| cap.25 off.75/up0 | +10.7% | 9.6% | 0.99 | -15.4% | 0.69 | 0.64 | 0.35 | 66.2% | 26 |
| cap.25 off.75/up0+bo20 | +12.3% | 10.3% | 1.06 | -15.4% | 0.80 | 0.74 | 0.41 | 73.8% | 22 |
| binary off.5 | +11.0% | 9.2% | 1.06 | -11.6% | 0.95 | 0.64 | 0.32 | 62.9% | 11 |
| binary off.5+bo20 | +11.7% | 9.5% | 1.08 | -12.8% | 0.91 | 0.69 | 0.37 | 68.2% | 13 |
| binary off.75/up0 | +11.6% | 9.9% | 1.03 | -17.5% | 0.66 | 0.69 | 0.38 | 68.5% | 11 |
| binary off.75/up0+bo20 | +12.3% | 10.5% | 1.04 | -17.5% | 0.70 | 0.76 | 0.45 | 75.2% | 14 |
| norm.25 off.5 | +12.4% | 11.0% | 1.01 | -14.3% | 0.87 | 0.74 | 0.40 | 75.7% | 21 |
| norm.25 off.5+bo20 | +13.0% | 11.1% | 1.04 | -18.1% | 0.72 | 0.79 | 0.45 | 78.3% | 19 |
| norm.25 off.75/up0 | +12.9% | 11.8% | 0.99 | -17.9% | 0.72 | 0.79 | 0.46 | 81.8% | 22 |
| norm.25 off.75/up0+bo20 | +13.6% | 12.2% | 1.01 | -19.1% | 0.71 | 0.86 | 0.53 | 86.0% | 21 |
| tv12 off.5 | +10.9% | 9.8% | 0.98 | -13.3% | 0.82 | 0.67 | 0.39 | 69.8% | 14 |
| tv12 off.5+bo20 | +10.9% | 9.8% | 0.99 | -16.8% | 0.65 | 0.70 | 0.44 | 72.3% | 16 |
| tv12 off.75/up0 | +11.3% | 10.3% | 0.97 | -17.8% | 0.63 | 0.71 | 0.43 | 74.6% | 14 |
| tv12 off.75/up0+bo20 | +11.4% | 10.5% | 0.97 | -19.1% | 0.60 | 0.75 | 0.50 | 78.2% | 17 |
| static 80/15/5 | +10.0% | 16.4% | 0.59 | -47.8% | 0.21 | 1.00 | 1.00 |  |  |

## Lag years

|  | 2009 | 2012 | 2019 | 2023 | 2026 |
|---|---|---|---|---|---|
| baseline | +15.6% | +0.4% | +9.7% | +8.8% | +4.5% |
| cap.5 off.5+bo20 | +19.8% | +4.5% | +13.9% | +18.2% | +7.5% |
| cap.5 off.75/up0 | +15.9% | +1.7% | +11.8% | +10.6% | +2.8% |
| cap.5 off.75/up0+bo20 | +22.1% | +6.2% | +18.8% | +21.6% | +6.6% |
| cap.25 off.5 | +20.0% | +1.2% | +10.0% | +8.0% | +3.4% |
| cap.25 off.5+bo20 | +22.0% | +4.8% | +13.6% | +16.7% | +6.8% |
| cap.25 off.75/up0 | +22.4% | +3.1% | +13.8% | +10.4% | +2.2% |
| cap.25 off.75/up0+bo20 | +25.5% | +6.6% | +19.4% | +19.9% | +5.5% |
| binary off.5 | +23.0% | -0.1% | +11.0% | +9.0% | +6.1% |
| binary off.5+bo20 | +24.6% | +2.2% | +13.5% | +15.8% | +8.4% |
| binary off.75/up0 | +26.0% | +1.8% | +15.8% | +11.4% | +5.2% |
| binary off.75/up0+bo20 | +28.5% | +3.9% | +19.4% | +19.2% | +7.6% |
| norm.25 off.5 | +27.4% | -1.3% | +13.3% | +11.4% | +5.7% |
| norm.25 off.5+bo20 | +31.0% | +2.1% | +17.1% | +19.0% | +8.7% |
| norm.25 off.75/up0 | +31.8% | +0.9% | +16.7% | +13.4% | +4.3% |
| norm.25 off.75/up0+bo20 | +35.6% | +4.0% | +24.2% | +22.8% | +7.6% |
| tv12 off.5 | +18.5% | +0.2% | +13.6% | +12.3% | +6.5% |
| tv12 off.5+bo20 | +22.0% | +2.4% | +15.7% | +16.2% | +7.4% |
| tv12 off.75/up0 | +19.1% | +0.5% | +18.5% | +13.3% | +6.0% |
| tv12 off.75/up0+bo20 | +22.6% | +2.8% | +22.3% | +19.0% | +7.5% |
| static 80/15/5 | +30.8% | +14.8% | +29.9% | +26.0% | +8.6% |
| WF[sharpe] |  | -0.1% | +13.5% | +9.0% | +6.8% |
| WF[calmar] |  | +1.8% | +15.8% | +16.7% | +6.8% |
| WF[cagr_dd20] |  | +0.9% | +16.7% | +13.4% | +7.6% |
