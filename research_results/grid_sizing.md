# Grid: sizing

Lever family (a): cash drag from signal-strength scaling.

Hypothesis: clip(score/0.5, 0, 1) leaves a lot of a positive-trend sleeve's
baseline in cash (a rolling Sharpe of 0.25 is a decent trend but gets only
half weight). Lowering SIGNAL_CAP, flooring strength for positive-trend
sleeves, or re-spreading unused weight across live sleeves instead of to
SGOV should lift upside capture. The regime caps stay on, so drawdown
protection should mostly survive.

Grid (all with regime caps 1/1/.5/.5):
  SIGNAL_CAP          0.5 (base) / 0.35 / 0.25 / 0.1 / binary (score > 0 -> full)
  strength floor      0.25 / 0.5 / 1.0 when close > 200d SMA, at cap 0.5
                      0.5 when score > 0 (alone; same as cap 0.25 on [0, .25])
  redistribute        "zero" (dead sleeves' baseline -> live sleeves) and
                      "normalize" (risky sums to 1 when anything is on), at cap 0.5 / 0.25

## Walk-forward window 2010-01-01+ (grid cells are fixed configs; WF[...] rows re-select the cell each Jan 1 on the expanding window by that objective)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| baseline | +10.2% | 8.8% | 1.00 | -11.7% | 0.88 | 0.58 | 0.33 | 59.8% | 30 |
| cap 0.35 | +10.5% | 8.9% | 1.01 | -11.3% | 0.93 | 0.59 | 0.33 | 60.9% | 27 |
| cap 0.25 | +10.7% | 9.0% | 1.03 | -11.4% | 0.94 | 0.61 | 0.35 | 61.7% | 24 |
| cap 0.1 | +11.0% | 9.1% | 1.05 | -11.6% | 0.95 | 0.62 | 0.35 | 62.8% | 17 |
| binary | +11.5% | 9.2% | 1.08 | -11.6% | 0.99 | 0.65 | 0.37 | 63.7% | 11 |
| floor 0.25 >200d | +10.4% | 8.8% | 1.02 | -11.7% | 0.89 | 0.59 | 0.33 | 60.6% | 33 |
| floor 0.5 >200d | +10.5% | 8.9% | 1.02 | -11.7% | 0.90 | 0.60 | 0.35 | 61.8% | 30 |
| floor 1.0 >200d | +11.1% | 9.2% | 1.04 | -12.1% | 0.92 | 0.64 | 0.39 | 65.6% | 24 |
| floor 0.5 score>0 | +10.6% | 8.9% | 1.03 | -11.9% | 0.89 | 0.59 | 0.33 | 60.5% | 24 |
| zero cap 0.5 | +11.9% | 10.6% | 0.99 | -13.5% | 0.88 | 0.70 | 0.43 | 72.0% | 37 |
| zero cap 0.25 | +12.4% | 10.8% | 1.01 | -12.9% | 0.96 | 0.73 | 0.46 | 74.5% | 28 |
| normalize cap 0.5 | +13.0% | 11.1% | 1.04 | -14.4% | 0.91 | 0.75 | 0.46 | 76.5% | 27 |
| normalize cap 0.25 | +13.0% | 11.0% | 1.04 | -14.3% | 0.91 | 0.76 | 0.47 | 76.8% | 22 |
| static 80/15/5 | +11.8% | 15.0% | 0.73 | -29.6% | 0.40 | 1.00 | 1.00 |  |  |
| WF[sharpe] | +11.3% | 9.2% | 1.07 | -11.6% | 0.97 | 0.63 | 0.35 |  |  |
| WF[calmar] | +11.4% | 9.2% | 1.08 | -11.6% | 0.98 | 0.64 | 0.36 |  |  |
| WF[cagr_dd20] | +12.6% | 10.7% | 1.03 | -13.3% | 0.94 | 0.73 | 0.44 |  |  |

### Success criteria (walk-forward window, vs baseline)

|  | UpCap+ | CAGR>=11% | DD>=-20% | Sharpe>=base-0.1 | ALL |
|---|---|---|---|---|---|
| baseline | ✗ | ✗ | ✓ | ✓ | ✗ |
| cap 0.35 | ✗ | ✗ | ✓ | ✓ | ✗ |
| cap 0.25 | ✗ | ✗ | ✓ | ✓ | ✗ |
| cap 0.1 | ✗ | ✓ | ✓ | ✓ | ✗ |
| binary | ✓ | ✓ | ✓ | ✓ | ✓ |
| floor 0.25 >200d | ✗ | ✗ | ✓ | ✓ | ✗ |
| floor 0.5 >200d | ✗ | ✗ | ✓ | ✓ | ✗ |
| floor 1.0 >200d | ✓ | ✓ | ✓ | ✓ | ✓ |
| floor 0.5 score>0 | ✗ | ✗ | ✓ | ✓ | ✗ |
| zero cap 0.5 | ✓ | ✓ | ✓ | ✓ | ✓ |
| zero cap 0.25 | ✓ | ✓ | ✓ | ✓ | ✓ |
| normalize cap 0.5 | ✓ | ✓ | ✓ | ✓ | ✓ |
| normalize cap 0.25 | ✓ | ✓ | ✓ | ✓ | ✓ |
| WF[sharpe] | ✓ | ✓ | ✓ | ✓ | ✓ |
| WF[calmar] | ✓ | ✓ | ✓ | ✓ | ✓ |
| WF[cagr_dd20] | ✓ | ✓ | ✓ | ✓ | ✓ |

### Walk-forward picks per year

|  | sharpe | calmar | cagr_dd20 |
|---|---|---|---|
| 2010 | binary | cap 0.1 | normalize cap 0.25 |
| 2011 | binary | binary | normalize cap 0.25 |
| 2012 | cap 0.1 | binary | binary |
| 2013 | cap 0.1 | cap 0.1 | cap 0.1 |
| 2014 | cap 0.1 | cap 0.1 | normalize cap 0.25 |
| 2015 | cap 0.1 | cap 0.1 | normalize cap 0.25 |
| 2016 | cap 0.1 | cap 0.1 | normalize cap 0.25 |
| 2017 | cap 0.1 | cap 0.1 | normalize cap 0.25 |
| 2018 | cap 0.1 | cap 0.1 | normalize cap 0.25 |
| 2019 | cap 0.1 | cap 0.1 | normalize cap 0.25 |
| 2020 | cap 0.1 | binary | normalize cap 0.25 |
| 2021 | cap 0.1 | binary | normalize cap 0.25 |
| 2022 | cap 0.1 | binary | normalize cap 0.25 |
| 2023 | cap 0.1 | binary | normalize cap 0.25 |
| 2024 | binary | binary | normalize cap 0.25 |
| 2025 | binary | binary | normalize cap 0.25 |
| 2026 | binary | binary | normalize cap 0.25 |

## Full period (in-sample)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| baseline | +9.7% | 8.7% | 0.96 | -11.7% | 0.83 | 0.56 | 0.29 | 58.8% | 30 |
| cap 0.35 | +10.1% | 8.8% | 0.99 | -11.3% | 0.90 | 0.58 | 0.29 | 60.0% | 27 |
| cap 0.25 | +10.3% | 8.9% | 1.01 | -11.4% | 0.90 | 0.59 | 0.30 | 60.8% | 23 |
| cap 0.1 | +10.7% | 9.0% | 1.03 | -11.6% | 0.92 | 0.61 | 0.30 | 62.0% | 17 |
| binary | +11.0% | 9.2% | 1.06 | -11.6% | 0.95 | 0.64 | 0.32 | 62.9% | 11 |
| floor 0.25 >200d | +9.8% | 8.7% | 0.97 | -11.7% | 0.84 | 0.57 | 0.30 | 59.7% | 32 |
| floor 0.5 >200d | +9.9% | 8.8% | 0.97 | -11.7% | 0.84 | 0.59 | 0.32 | 61.0% | 30 |
| floor 1.0 >200d | +10.5% | 9.2% | 1.00 | -12.1% | 0.87 | 0.63 | 0.36 | 64.9% | 22 |
| floor 0.5 score>0 | +10.1% | 8.8% | 1.00 | -11.9% | 0.85 | 0.58 | 0.30 | 59.6% | 24 |
| zero cap 0.5 | +10.9% | 10.5% | 0.93 | -15.4% | 0.71 | 0.66 | 0.38 | 70.6% | 37 |
| zero cap 0.25 | +11.6% | 10.7% | 0.97 | -14.9% | 0.78 | 0.70 | 0.39 | 73.2% | 27 |
| normalize cap 0.5 | +12.4% | 11.0% | 1.01 | -14.4% | 0.86 | 0.74 | 0.40 | 75.4% | 25 |
| normalize cap 0.25 | +12.4% | 11.0% | 1.01 | -14.3% | 0.87 | 0.74 | 0.40 | 75.7% | 21 |
| static 80/15/5 | +10.0% | 16.4% | 0.59 | -47.8% | 0.21 | 1.00 | 1.00 |  |  |

## Lag years

|  | 2009 | 2012 | 2019 | 2023 | 2026 |
|---|---|---|---|---|---|
| baseline | +15.6% | +0.4% | +9.7% | +8.8% | +4.5% |
| cap 0.35 | +18.4% | +0.9% | +9.5% | +8.5% | +4.0% |
| cap 0.25 | +20.0% | +1.2% | +10.0% | +8.0% | +3.4% |
| cap 0.1 | +21.7% | +1.0% | +10.8% | +6.8% | +3.2% |
| binary | +23.0% | -0.1% | +11.0% | +9.0% | +6.1% |
| floor 0.25 >200d | +16.1% | +0.3% | +10.4% | +10.5% | +4.7% |
| floor 0.5 >200d | +17.3% | -0.0% | +11.2% | +12.2% | +4.9% |
| floor 1.0 >200d | +21.4% | -0.7% | +13.3% | +14.5% | +5.3% |
| floor 0.5 score>0 | +16.9% | -0.0% | +10.1% | +9.0% | +6.0% |
| zero cap 0.5 | +15.1% | -0.6% | +12.9% | +12.4% | +4.9% |
| zero cap 0.25 | +21.6% | -0.4% | +14.1% | +10.5% | +4.5% |
| normalize cap 0.5 | +27.7% | -1.9% | +13.4% | +11.6% | +7.2% |
| normalize cap 0.25 | +27.4% | -1.3% | +13.3% | +11.4% | +5.7% |
| static 80/15/5 | +30.8% | +14.8% | +29.9% | +26.0% | +8.6% |
| WF[sharpe] |  | +1.0% | +10.8% | +6.8% | +6.1% |
| WF[calmar] |  | -0.1% | +10.8% | +9.0% | +6.1% |
| WF[cagr_dd20] |  | -0.1% | +13.3% | +11.4% | +5.7% |
