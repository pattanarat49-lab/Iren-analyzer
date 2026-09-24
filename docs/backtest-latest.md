# IREN probability backtest (alpaca data)

Generated 2026-09-24T05:04:10+00:00 · data 2024-09-23T17:04:00+00:00 → 2026-09-23T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.512 | 0.514 | 0.2489 | 0.2500 | [-0.00139, -0.00065] | 0.514 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.505 | 0.511 | 0.2498 | 0.2499 | [-0.00051, +0.00043] | 0.505 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.503 | 0.512 | 0.2504 | 0.2499 | [-0.00034, +0.00143] | 0.507 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.526 | 0.435 | 0.2516 | 0.2508 | [-0.00374, +0.00570] | 0.539 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,962 over 250 days; share of "up": 0.486
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2500 | 0.6931 | – | – | – | – | – |
| logreg | 0.514 | 0.2492 | 0.6916 | 0.516 | 0.0031 | 0.024 | 0.643 | 0.81 |
| lgbm | 0.512 | 0.2489 | 0.6910 | 0.514 | 0.0041 | 0.025 | 0.643 | 0.46 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.057 | 0.148 | 311 |
| 0.1–0.2 | 0.139 | 0.126 | 334 |
| 0.2–0.3 | 0.228 | 0.155 | 116 |
| 0.3–0.4 | 0.371 | 0.091 | 11 |
| 0.4–0.5 | 0.480 | 0.484 | 63,351 |
| 0.5–0.6 | 0.510 | 0.497 | 32,441 |
| 0.6–0.7 | 0.622 | 0.537 | 328 |
| 0.7–0.8 | 0.738 | 0.357 | 28 |
| 0.8–0.9 | 0.839 | 0.882 | 17 |
| 0.9–1.0 | 0.990 | 0.840 | 25 |

## 15m (15 นาที)

- Test rows: 96,952 over 250 days; share of "up": 0.489
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.511 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.512 | 0.2499 | 0.6940 | 0.508 | 0.0001 | 0.021 | 0.603 | 1.39 |
| lgbm | 0.505 | 0.2498 | 0.6932 | 0.505 | 0.0002 | 0.035 | 0.555 | -0.48 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.026 | 0.234 | 77 |
| 0.1–0.2 | 0.151 | 0.162 | 346 |
| 0.2–0.3 | 0.245 | 0.353 | 266 |
| 0.3–0.4 | 0.347 | 0.419 | 136 |
| 0.4–0.5 | 0.491 | 0.492 | 79,734 |
| 0.5–0.6 | 0.517 | 0.482 | 15,633 |
| 0.6–0.7 | 0.617 | 0.469 | 695 |
| 0.7–0.8 | 0.744 | 0.857 | 7 |
| 0.8–0.9 | 0.810 | 0.895 | 19 |
| 0.9–1.0 | 0.939 | 0.718 | 39 |

## 1h (1 ชั่วโมง)

- Test rows: 96,907 over 250 days; share of "up": 0.488
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.512 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.503 | 0.2504 | 0.6950 | 0.507 | -0.0020 | 0.073 | 0.522 | 1.90 |
| lgbm | 0.499 | 0.2507 | 0.6948 | 0.498 | -0.0030 | 0.059 | 0.494 | 1.67 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.023 | 0.287 | 80 |
| 0.1–0.2 | 0.138 | 0.460 | 87 |
| 0.2–0.3 | 0.258 | 0.288 | 184 |
| 0.3–0.4 | 0.337 | 0.361 | 352 |
| 0.4–0.5 | 0.480 | 0.486 | 45,161 |
| 0.5–0.6 | 0.516 | 0.491 | 50,884 |
| 0.6–0.7 | 0.644 | 0.629 | 35 |
| 0.7–0.8 | 0.756 | 0.500 | 2 |
| 0.8–0.9 | 0.832 | 0.357 | 28 |
| 0.9–1.0 | 0.990 | 0.681 | 94 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,966 over 250 days; share of "up": 0.473
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.435 | 0.2508 | 0.6948 | – | – | – | – | – |
| logreg | 0.526 | 0.2516 | 0.6970 | 0.539 | -0.0032 | 0.337 | 0.545 | 8.04 |
| lgbm | 0.493 | 0.2546 | 0.7054 | 0.494 | -0.0149 | 0.425 | 0.501 | -8.20 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.010 | 0.000 | 7 |
| 0.2–0.3 | 0.268 | 0.263 | 57 |
| 0.3–0.4 | 0.367 | 0.414 | 9,547 |
| 0.4–0.5 | 0.464 | 0.440 | 28,681 |
| 0.5–0.6 | 0.539 | 0.495 | 48,861 |
| 0.6–0.7 | 0.644 | 0.527 | 9,322 |
| 0.7–0.8 | 0.728 | 0.349 | 410 |
| 0.9–1.0 | 0.990 | 0.802 | 81 |
