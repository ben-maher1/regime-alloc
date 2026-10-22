# Diagnosis: where the upside is lost vs static 80/15/5

## Waterfall, full period

Annualized log-return gap added by each step, split by benchmark phase (falling = peak→trough of a >10% benchmark drawdown, recovery = trough→new high). The recovery column is (c) slow re-risking.

| step | layer | falling | recovery | normal | total |
|---|---|---|---|---|---|
| friction (band, costs) | 80/15/5 w/ band+costs | +0.1% | -0.2% | +0.4% | +0.3% |
| (e) inverse-vol mix vs 80/15/5 | inv-vol mix, always in | +3.4% | -0.8% | +0.0% | +2.7% |
| (d) per-sleeve caps | + sleeve caps | -0.1% | -0.1% | -0.0% | -0.2% |
| trend on/off filter | + binary trend filter | +3.3% | -3.7% | -0.8% | -1.2% |
| (a) signal-strength cash drag | + partial scaling | +0.0% | -1.1% | -0.5% | -1.6% |
| (b) regime caps | + regime caps (= full) | +1.0% | -0.8% | -0.5% | -0.3% |
| TOTAL | full system - benchmark | +7.8% | -6.7% | -1.4% | -0.3% |

### Layer stats, full period

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| static 80/15/5 (frictionless) | +10.0% | 16.4% | 0.59 | -47.8% | 0.21 | 1.00 | 1.00 |  |  |
| 80/15/5 w/ band+costs | +10.3% | 16.4% | 0.60 | -47.9% | 0.22 | 1.01 | 0.99 | 97.2% | 1 |
| inv-vol mix, always in | +13.3% | 14.2% | 0.87 | -34.8% | 0.38 | 0.95 | 0.70 | 98.3% | 6 |
| + sleeve caps | +13.2% | 14.1% | 0.86 | -34.8% | 0.38 | 0.95 | 0.71 | 98.1% | 6 |
| + binary trend filter | +11.8% | 10.8% | 0.98 | -22.5% | 0.52 | 0.73 | 0.43 | 73.0% | 11 |
| + partial scaling | +10.0% | 10.0% | 0.88 | -18.7% | 0.54 | 0.63 | 0.38 | 67.4% | 36 |
| + regime caps (= full) | +9.7% | 8.7% | 0.96 | -11.7% | 0.83 | 0.56 | 0.29 | 58.8% | 30 |

## Waterfall, 2010+ (walk-forward window)

Annualized log-return gap added by each step, split by benchmark phase (falling = peak→trough of a >10% benchmark drawdown, recovery = trough→new high). The recovery column is (c) slow re-risking.

| step | layer | falling | recovery | normal | total |
|---|---|---|---|---|---|
| friction (band, costs) | 80/15/5 w/ band+costs | +0.1% | -0.3% | +0.4% | +0.3% |
| (e) inverse-vol mix vs 80/15/5 | inv-vol mix, always in | +2.8% | -0.5% | -0.6% | +1.7% |
| (d) per-sleeve caps | + sleeve caps | -0.1% | -0.0% | -0.0% | -0.1% |
| trend on/off filter | + binary trend filter | +2.7% | -4.2% | -0.3% | -1.8% |
| (a) signal-strength cash drag | + partial scaling | +0.4% | -1.0% | -0.6% | -1.2% |
| (b) regime caps | + regime caps (= full) | +1.0% | -0.9% | -0.3% | -0.2% |
| TOTAL | full system - benchmark | +7.0% | -7.0% | -1.4% | -1.4% |

### Layer stats, 2010+ (walk-forward window)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| static 80/15/5 (frictionless) | +11.8% | 15.0% | 0.73 | -29.6% | 0.40 | 1.00 | 1.00 |  |  |
| 80/15/5 w/ band+costs | +12.1% | 15.0% | 0.75 | -28.8% | 0.42 | 1.01 | 0.99 | 98.5% | 1 |
| inv-vol mix, always in | +14.0% | 13.4% | 0.95 | -24.9% | 0.56 | 0.95 | 0.76 | 99.6% | 6 |
| + sleeve caps | +13.8% | 13.4% | 0.94 | -24.9% | 0.56 | 0.95 | 0.77 | 99.5% | 6 |
| + binary trend filter | +11.8% | 10.7% | 0.97 | -22.5% | 0.52 | 0.73 | 0.51 | 73.2% | 11 |
| + partial scaling | +10.4% | 10.0% | 0.91 | -18.7% | 0.56 | 0.64 | 0.43 | 67.9% | 36 |
| + regime caps (= full) | +10.2% | 8.8% | 1.00 | -11.7% | 0.88 | 0.58 | 0.33 | 59.8% | 30 |

## One-at-a-time removals from the full system (full period)

|  | CAGR | Vol | Sharpe | MaxDD | Calmar | UpCap | DownCap | AvgExp | Rebal/yr |
|---|---|---|---|---|---|---|---|---|---|
| full system | +9.7% | 8.7% | 0.96 | -11.7% | 0.83 | 0.56 | 0.29 | 58.8% | 30 |
| - regime caps | +10.0% | 10.0% | 0.88 | -18.7% | 0.54 | 0.63 | 0.38 | 67.4% | 36 |
| - partial scaling (binary) | +11.0% | 9.2% | 1.06 | -11.6% | 0.95 | 0.64 | 0.32 | 62.9% | 11 |
| - sleeve caps | +9.7% | 8.7% | 0.97 | -11.7% | 0.83 | 0.57 | 0.29 | 58.9% | 30 |
| 80/15/5 base instead of inv-vol | +7.5% | 9.0% | 0.72 | -15.6% | 0.48 | 0.57 | 0.46 | 61.2% | 22 |
| static 80/15/5 | +10.0% | 16.4% | 0.59 | -47.8% | 0.21 | 1.00 | 1.00 |  |  |

## Per-year returns in the lag years

|  | 2009 | 2012 | 2019 | 2023 | 2026 |
|---|---|---|---|---|---|
| full system | +15.6% | +0.4% | +9.7% | +8.8% | +4.5% |
| - regime caps | +15.8% | +1.9% | +13.4% | +11.7% | +2.3% |
| - partial scaling (binary) | +23.0% | -0.1% | +11.0% | +9.0% | +6.1% |
| - sleeve caps | +16.2% | +0.4% | +9.7% | +8.8% | +4.5% |
| 80/15/5 base instead of inv-vol | +22.1% | +3.3% | +7.2% | +6.0% | +4.4% |
| static 80/15/5 | +30.8% | +14.8% | +29.9% | +26.0% | +8.6% |

## Benchmark drawdown episodes (>10%): how fast does the system re-risk?

| trough | peak | recovered | bench DD | strat DD | bench recov | strat recov | exp @trough | avg exp 0-63d | days to 80% exp |
|---|---|---|---|---|---|---|---|---|---|
| 2009-03-09 | 2007-10-15 | 2011-01-17 | -47.8% | +0.8% | +91.0% | +26.5% | 29.1% | 34.2% | 53.00 |
| 2011-10-03 | 2011-05-02 | 2012-09-12 | -18.4% | -0.4% | +21.4% | +0.0% | 26.8% | 21.2% | 88.00 |
| 2016-01-20 | 2014-07-07 | 2016-06-02 | -13.5% | -3.6% | +14.7% | +6.6% | 5.3% | 43.8% | 49.00 |
| 2018-12-25 | 2018-01-29 | 2019-06-21 | -20.4% | -8.3% | +25.5% | +6.2% | 30.8% | 37.7% | 75.00 |
| 2020-03-23 | 2020-02-13 | 2020-07-20 | -29.6% | -9.1% | +41.4% | +8.2% | 34.1% | 36.3% | 51.00 |
| 2022-10-14 | 2021-11-09 | 2023-12-20 | -26.9% | -4.9% | +35.3% | +9.3% | 4.4% | 21.7% | 50.00 |
| 2025-04-08 | 2025-02-21 | 2025-05-09 | -14.0% | -4.5% | +15.6% | +3.4% | 23.7% | 26.6% |  |
| 2026-03-30 | 2026-01-29 | 2026-04-16 | -10.2% | -5.5% | +10.3% | +1.2% | 12.1% | 19.3% |  |
