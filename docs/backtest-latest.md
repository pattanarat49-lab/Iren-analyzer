# IREN probability backtest (alpaca data)

Generated 2026-11-07T02:05:57+00:00 · data 2024-11-06T14:30:00+00:00 → 2026-11-06T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.515 | 0.519 | 0.2489 | 0.2497 | [-0.00107, -0.00049] | 0.515 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.511 | 0.518 | 0.2496 | 0.2497 | [-0.00055, +0.00025] | 0.507 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.512 | 0.518 | 0.2501 | 0.2499 | [-0.00026, +0.00064] | 0.486 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.496 | 0.476 | 0.2506 | 0.2509 | [-0.00314, +0.00238] | 0.521 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,915 over 250 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.518 | 0.2490 | 0.6910 | 0.513 | 0.0027 | 0.026 | 0.629 | 0.93 |
| lgbm | 0.515 | 0.2489 | 0.6908 | 0.515 | 0.0031 | 0.032 | 0.605 | 0.61 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.197 | 0.048 | 42 |
| 0.2–0.3 | 0.242 | 0.131 | 658 |
| 0.3–0.4 | 0.347 | 0.241 | 79 |
| 0.4–0.5 | 0.479 | 0.480 | 67,926 |
| 0.5–0.6 | 0.514 | 0.492 | 28,210 |

## 15m (15 นาที)

- Test rows: 96,905 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.515 | 0.2496 | 0.6924 | 0.506 | 0.0005 | 0.032 | 0.539 | 0.77 |
| lgbm | 0.511 | 0.2496 | 0.6923 | 0.507 | 0.0006 | 0.027 | 0.576 | 0.13 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.275 | 0.176 | 176 |
| 0.3–0.4 | 0.344 | 0.365 | 926 |
| 0.4–0.5 | 0.484 | 0.482 | 67,544 |
| 0.5–0.6 | 0.514 | 0.489 | 28,259 |

## 1h (1 ชั่วโมง)

- Test rows: 96,860 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.512 | 0.2501 | 0.6934 | 0.486 | -0.0008 | 0.016 | 0.503 | 4.80 |
| lgbm | 0.506 | 0.2501 | 0.6934 | 0.496 | -0.0009 | 0.033 | 0.531 | 1.87 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.156 | 0.318 | 22 |
| 0.2–0.3 | 0.250 | 0.333 | 42 |
| 0.3–0.4 | 0.378 | 0.286 | 154 |
| 0.4–0.5 | 0.492 | 0.483 | 81,562 |
| 0.5–0.6 | 0.514 | 0.480 | 14,990 |
| 0.6–0.7 | 0.609 | 0.444 | 90 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,919 over 250 days; share of "up": 0.470
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.476 | 0.2509 | 0.6949 | – | – | – | – | – |
| logreg | 0.496 | 0.2506 | 0.6944 | 0.521 | 0.0012 | 0.221 | 0.547 | 1.68 |
| lgbm | 0.502 | 0.2518 | 0.6968 | 0.501 | -0.0037 | 0.126 | 0.483 | 0.07 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.192 | 0.000 | 11 |
| 0.2–0.3 | 0.271 | 0.375 | 64 |
| 0.3–0.4 | 0.377 | 0.503 | 1,513 |
| 0.4–0.5 | 0.472 | 0.463 | 35,100 |
| 0.5–0.6 | 0.524 | 0.469 | 57,686 |
| 0.6–0.7 | 0.639 | 0.579 | 2,228 |
| 0.7–0.8 | 0.731 | 0.373 | 303 |
| 0.8–0.9 | 0.814 | 0.286 | 14 |
