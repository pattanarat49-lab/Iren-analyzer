# IREN probability backtest (alpaca data)

Generated 2026-10-09T22:42:00+00:00 · data 2024-10-09T13:30:00+00:00 → 2026-10-09T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.513 | 0.517 | 0.2490 | 0.2497 | [-0.00114, -0.00045] | 0.515 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.507 | 0.516 | 0.2497 | 0.2498 | [-0.00045, +0.00033] | 0.504 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.500 | 0.516 | 0.2504 | 0.2499 | [-0.00029, +0.00143] | 0.498 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.516 | 0.485 | 0.2508 | 0.2513 | [-0.00473, +0.00363] | 0.543 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,967 over 250 days; share of "up": 0.483
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.515 | 0.2490 | 0.6910 | 0.516 | 0.0030 | 0.029 | 0.615 | 0.77 |
| lgbm | 0.513 | 0.2490 | 0.6909 | 0.515 | 0.0031 | 0.031 | 0.603 | 0.27 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.192 | 0.133 | 158 |
| 0.2–0.3 | 0.226 | 0.107 | 345 |
| 0.3–0.4 | 0.328 | 0.192 | 276 |
| 0.4–0.5 | 0.480 | 0.482 | 67,069 |
| 0.5–0.6 | 0.516 | 0.493 | 29,119 |

## 15m (15 นาที)

- Test rows: 96,957 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.507 | 0.2499 | 0.6929 | 0.504 | -0.0004 | 0.026 | 0.549 | 0.26 |
| lgbm | 0.507 | 0.2497 | 0.6925 | 0.504 | 0.0003 | 0.024 | 0.581 | -0.42 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.281 | 0.123 | 171 |
| 0.3–0.4 | 0.355 | 0.261 | 568 |
| 0.4–0.5 | 0.484 | 0.486 | 65,759 |
| 0.5–0.6 | 0.517 | 0.486 | 30,458 |
| 0.6–0.7 | 0.602 | 1.000 | 1 |

## 1h (1 ชั่วโมง)

- Test rows: 96,912 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.498 | 0.2506 | 0.6943 | 0.495 | -0.0028 | 0.051 | 0.498 | 1.35 |
| lgbm | 0.500 | 0.2504 | 0.6940 | 0.498 | -0.0023 | 0.035 | 0.516 | 0.22 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.391 | 0.459 | 495 |
| 0.4–0.5 | 0.485 | 0.489 | 67,658 |
| 0.5–0.6 | 0.517 | 0.473 | 28,706 |
| 0.6–0.7 | 0.604 | 0.264 | 53 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,971 over 250 days; share of "up": 0.466
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.485 | 0.2513 | 0.6957 | – | – | – | – | – |
| logreg | 0.516 | 0.2508 | 0.6950 | 0.543 | 0.0019 | 0.355 | 0.537 | 9.96 |
| lgbm | 0.471 | 0.2533 | 0.6998 | 0.473 | -0.0080 | 0.152 | 0.525 | -15.59 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.197 | 0.000 | 11 |
| 0.2–0.3 | 0.251 | 0.565 | 177 |
| 0.3–0.4 | 0.380 | 0.379 | 6,085 |
| 0.4–0.5 | 0.461 | 0.428 | 23,035 |
| 0.5–0.6 | 0.533 | 0.482 | 62,210 |
| 0.6–0.7 | 0.647 | 0.528 | 4,082 |
| 0.7–0.8 | 0.724 | 0.590 | 1,339 |
| 0.8–0.9 | 0.827 | 0.562 | 32 |
