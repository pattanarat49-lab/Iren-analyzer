# IREN probability backtest (alpaca data)

Generated 2026-10-23T22:55:27+00:00 · data 2024-10-23T13:30:00+00:00 → 2026-10-23T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.513 | 0.519 | 0.2490 | 0.2497 | [-0.00104, -0.00033] | 0.515 | 250 | ⚠️ **no proven edge** |
| 15m | logreg | 0.504 | 0.517 | 0.2499 | 0.2498 | [-0.00028, +0.00040] | 0.502 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.507 | 0.519 | 0.2500 | 0.2499 | [-0.00045, +0.00070] | 0.497 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.507 | 0.478 | 0.2503 | 0.2511 | [-0.00416, +0.00262] | 0.535 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,894 over 250 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.514 | 0.2490 | 0.6911 | 0.514 | 0.0026 | 0.019 | 0.658 | 0.59 |
| lgbm | 0.513 | 0.2490 | 0.6910 | 0.515 | 0.0027 | 0.038 | 0.590 | 0.63 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.197 | 0.031 | 32 |
| 0.2–0.3 | 0.229 | 0.121 | 505 |
| 0.3–0.4 | 0.331 | 0.264 | 269 |
| 0.4–0.5 | 0.478 | 0.479 | 60,001 |
| 0.5–0.6 | 0.514 | 0.493 | 36,087 |

## 15m (15 นาที)

- Test rows: 96,884 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.504 | 0.2499 | 0.6928 | 0.502 | -0.0003 | 0.026 | 0.549 | -0.22 |
| lgbm | 0.504 | 0.2499 | 0.6930 | 0.499 | -0.0006 | 0.027 | 0.565 | -0.90 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.177 | 0.172 | 29 |
| 0.2–0.3 | 0.251 | 0.261 | 203 |
| 0.3–0.4 | 0.356 | 0.261 | 341 |
| 0.4–0.5 | 0.484 | 0.486 | 60,642 |
| 0.5–0.6 | 0.510 | 0.482 | 35,556 |
| 0.6–0.7 | 0.616 | 0.646 | 113 |

## 1h (1 ชั่วโมง)

- Test rows: 96,840 over 250 days; share of "up": 0.481
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.507 | 0.2500 | 0.6931 | 0.497 | -0.0004 | 0.033 | 0.549 | 1.62 |
| lgbm | 0.506 | 0.2501 | 0.6933 | 0.496 | -0.0008 | 0.045 | 0.540 | 0.22 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.156 | 0.480 | 25 |
| 0.2–0.3 | 0.272 | 0.340 | 147 |
| 0.3–0.4 | 0.367 | 0.343 | 268 |
| 0.4–0.5 | 0.489 | 0.484 | 74,827 |
| 0.5–0.6 | 0.512 | 0.474 | 21,561 |
| 0.6–0.7 | 0.611 | 0.000 | 12 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,898 over 250 days; share of "up": 0.463
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.478 | 0.2511 | 0.6954 | – | – | – | – | – |
| logreg | 0.507 | 0.2503 | 0.6940 | 0.535 | 0.0031 | 0.222 | 0.558 | 6.32 |
| lgbm | 0.470 | 0.2546 | 0.7025 | 0.464 | -0.0140 | 0.230 | 0.459 | -18.61 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.191 | 0.000 | 11 |
| 0.2–0.3 | 0.269 | 0.415 | 53 |
| 0.3–0.4 | 0.379 | 0.465 | 1,888 |
| 0.4–0.5 | 0.458 | 0.423 | 26,493 |
| 0.5–0.6 | 0.525 | 0.475 | 65,310 |
| 0.6–0.7 | 0.639 | 0.573 | 2,464 |
| 0.7–0.8 | 0.740 | 0.477 | 650 |
| 0.8–0.9 | 0.824 | 0.345 | 29 |
