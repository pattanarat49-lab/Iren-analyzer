# IREN probability backtest (alpaca data)

Generated 2026-11-12T03:12:13+00:00 · data 2024-11-11T15:12:00+00:00 → 2026-11-11T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.514 | 0.519 | 0.2488 | 0.2497 | [-0.00117, -0.00054] | 0.515 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.512 | 0.517 | 0.2495 | 0.2497 | [-0.00067, +0.00009] | 0.510 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.505 | 0.518 | 0.2499 | 0.2499 | [-0.00060, +0.00078] | 0.500 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.518 | 0.473 | 0.2496 | 0.2504 | [-0.00354, +0.00189] | 0.539 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,946 over 250 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.520 | 0.2489 | 0.6908 | 0.515 | 0.0031 | 0.026 | 0.632 | 1.05 |
| lgbm | 0.514 | 0.2488 | 0.6906 | 0.515 | 0.0034 | 0.034 | 0.604 | 0.65 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.171 | 0.073 | 110 |
| 0.2–0.3 | 0.238 | 0.130 | 632 |
| 0.3–0.4 | 0.371 | 0.354 | 82 |
| 0.4–0.5 | 0.479 | 0.480 | 66,536 |
| 0.5–0.6 | 0.513 | 0.492 | 29,583 |
| 0.6–0.7 | 0.603 | 0.000 | 3 |

## 15m (15 นาที)

- Test rows: 96,936 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.518 | 0.2495 | 0.6921 | 0.508 | 0.0009 | 0.030 | 0.563 | 1.37 |
| lgbm | 0.512 | 0.2495 | 0.6920 | 0.510 | 0.0011 | 0.028 | 0.574 | 0.42 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.276 | 0.142 | 155 |
| 0.3–0.4 | 0.349 | 0.329 | 924 |
| 0.4–0.5 | 0.483 | 0.481 | 65,006 |
| 0.5–0.6 | 0.512 | 0.491 | 30,851 |

## 1h (1 ชั่วโมง)

- Test rows: 96,891 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.513 | 0.2501 | 0.6935 | 0.484 | -0.0012 | 0.012 | 0.495 | 5.79 |
| lgbm | 0.505 | 0.2499 | 0.6930 | 0.500 | -0.0003 | 0.042 | 0.558 | 1.54 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.392 | 0.292 | 349 |
| 0.4–0.5 | 0.484 | 0.484 | 64,813 |
| 0.5–0.6 | 0.512 | 0.480 | 31,729 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,950 over 250 days; share of "up": 0.468
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.473 | 0.2504 | 0.6939 | – | – | – | – | – |
| logreg | 0.518 | 0.2496 | 0.6924 | 0.539 | 0.0032 | 0.238 | 0.573 | 15.17 |
| lgbm | 0.513 | 0.2506 | 0.6944 | 0.517 | -0.0009 | 0.097 | 0.476 | 1.91 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.177 | 0.000 | 14 |
| 0.2–0.3 | 0.263 | 0.419 | 74 |
| 0.3–0.4 | 0.371 | 0.481 | 1,972 |
| 0.4–0.5 | 0.471 | 0.439 | 38,620 |
| 0.5–0.6 | 0.528 | 0.482 | 53,068 |
| 0.6–0.7 | 0.620 | 0.600 | 2,856 |
| 0.7–0.8 | 0.728 | 0.532 | 316 |
| 0.8–0.9 | 0.819 | 0.233 | 30 |
