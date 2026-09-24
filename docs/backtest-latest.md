# IREN probability backtest (alpaca data)

Generated 2026-09-24T02:36:52+00:00 · data 2024-09-23T14:37:00+00:00 → 2026-09-23T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.514 | 0.514 | 0.2489 | 0.2500 | [-0.00137, -0.00067] | 0.514 | 250 | ✅ edge |
| 15m | lgbm | 0.506 | 0.511 | 0.2499 | 0.2499 | [-0.00046, +0.00049] | 0.508 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.503 | 0.512 | 0.2504 | 0.2499 | [-0.00041, +0.00138] | 0.506 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.526 | 0.435 | 0.2518 | 0.2508 | [-0.00354, +0.00576] | 0.533 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,962 over 250 days; share of "up": 0.486
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2500 | 0.6931 | – | – | – | – | – |
| logreg | 0.515 | 0.2493 | 0.6921 | 0.515 | 0.0026 | 0.018 | 0.668 | 0.90 |
| lgbm | 0.514 | 0.2489 | 0.6909 | 0.514 | 0.0041 | 0.051 | 0.571 | 0.69 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.060 | 0.169 | 260 |
| 0.1–0.2 | 0.120 | 0.135 | 325 |
| 0.2–0.3 | 0.215 | 0.094 | 159 |
| 0.3–0.4 | 0.333 | 0.167 | 18 |
| 0.4–0.5 | 0.481 | 0.483 | 61,303 |
| 0.5–0.6 | 0.509 | 0.500 | 34,823 |
| 0.6–0.7 | 0.623 | 0.740 | 50 |
| 0.7–0.8 | 0.756 | 1.000 | 10 |
| 0.8–0.9 | 0.896 | 1.000 | 1 |
| 0.9–1.0 | 0.990 | 0.846 | 13 |

## 15m (15 นาที)

- Test rows: 96,952 over 250 days; share of "up": 0.489
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.511 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.513 | 0.2499 | 0.6941 | 0.509 | -0.0000 | 0.024 | 0.578 | 1.63 |
| lgbm | 0.506 | 0.2499 | 0.6932 | 0.508 | 0.0001 | 0.032 | 0.552 | -0.11 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.020 | 0.239 | 117 |
| 0.1–0.2 | 0.135 | 0.159 | 220 |
| 0.2–0.3 | 0.241 | 0.128 | 172 |
| 0.3–0.4 | 0.332 | 0.464 | 358 |
| 0.4–0.5 | 0.490 | 0.492 | 81,459 |
| 0.5–0.6 | 0.525 | 0.480 | 13,281 |
| 0.6–0.7 | 0.602 | 0.491 | 1,282 |
| 0.7–0.8 | 0.748 | 0.541 | 37 |
| 0.8–0.9 | 0.855 | 1.000 | 13 |
| 0.9–1.0 | 0.990 | 0.846 | 13 |

## 1h (1 ชั่วโมง)

- Test rows: 96,907 over 250 days; share of "up": 0.488
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.512 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.503 | 0.2504 | 0.6945 | 0.506 | -0.0019 | 0.077 | 0.516 | 1.81 |
| lgbm | 0.497 | 0.2505 | 0.6942 | 0.495 | -0.0025 | 0.066 | 0.494 | -3.06 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.020 | 0.288 | 73 |
| 0.1–0.2 | 0.173 | 0.444 | 90 |
| 0.2–0.3 | 0.260 | 0.282 | 216 |
| 0.3–0.4 | 0.337 | 0.382 | 325 |
| 0.4–0.5 | 0.480 | 0.487 | 44,924 |
| 0.5–0.6 | 0.516 | 0.491 | 51,201 |
| 0.6–0.7 | 0.649 | 0.750 | 28 |
| 0.7–0.8 | 0.756 | 1.000 | 1 |
| 0.8–0.9 | 0.832 | 0.357 | 28 |
| 0.9–1.0 | 0.990 | 0.619 | 21 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,966 over 250 days; share of "up": 0.473
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.435 | 0.2508 | 0.6948 | – | – | – | – | – |
| logreg | 0.526 | 0.2518 | 0.6974 | 0.533 | -0.0038 | 0.337 | 0.547 | 7.88 |
| lgbm | 0.491 | 0.2557 | 0.7093 | 0.491 | -0.0195 | 0.308 | 0.525 | -14.23 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.010 | 0.000 | 6 |
| 0.2–0.3 | 0.286 | 0.436 | 165 |
| 0.3–0.4 | 0.367 | 0.425 | 9,077 |
| 0.4–0.5 | 0.463 | 0.437 | 29,419 |
| 0.5–0.6 | 0.540 | 0.494 | 49,001 |
| 0.6–0.7 | 0.646 | 0.535 | 8,759 |
| 0.7–0.8 | 0.729 | 0.361 | 457 |
| 0.9–1.0 | 0.990 | 0.793 | 82 |
