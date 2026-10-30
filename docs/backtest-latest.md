# IREN probability backtest (alpaca data)

Generated 2026-10-30T02:05:32+00:00 · data 2024-10-29T14:06:00+00:00 → 2026-10-29T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.516 | 0.519 | 0.2490 | 0.2497 | [-0.00104, -0.00037] | 0.515 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.506 | 0.517 | 0.2498 | 0.2498 | [-0.00037, +0.00042] | 0.503 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.509 | 0.517 | 0.2501 | 0.2499 | [-0.00046, +0.00098] | 0.498 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.506 | 0.445 | 0.2502 | 0.2510 | [-0.00359, +0.00192] | 0.530 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,909 over 250 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.519 | 0.2490 | 0.6910 | 0.514 | 0.0027 | 0.023 | 0.638 | 1.19 |
| lgbm | 0.516 | 0.2490 | 0.6909 | 0.515 | 0.0029 | 0.041 | 0.577 | 0.68 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.195 | 0.023 | 86 |
| 0.2–0.3 | 0.238 | 0.146 | 595 |
| 0.3–0.4 | 0.349 | 0.343 | 143 |
| 0.4–0.5 | 0.480 | 0.480 | 68,194 |
| 0.5–0.6 | 0.519 | 0.495 | 27,889 |
| 0.6–0.7 | 0.602 | 1.000 | 2 |

## 15m (15 นาที)

- Test rows: 96,899 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.508 | 0.2499 | 0.6929 | 0.503 | -0.0004 | 0.036 | 0.524 | 0.30 |
| lgbm | 0.506 | 0.2498 | 0.6927 | 0.503 | -0.0001 | 0.025 | 0.585 | -1.07 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.271 | 0.249 | 225 |
| 0.3–0.4 | 0.355 | 0.302 | 669 |
| 0.4–0.5 | 0.484 | 0.488 | 72,314 |
| 0.5–0.6 | 0.518 | 0.478 | 23,691 |

## 1h (1 ชั่วโมง)

- Test rows: 96,856 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.517 | 0.2502 | 0.6936 | 0.487 | -0.0013 | 0.020 | 0.482 | 5.06 |
| lgbm | 0.509 | 0.2501 | 0.6934 | 0.498 | -0.0010 | 0.028 | 0.548 | 1.19 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.293 | 0.158 | 19 |
| 0.3–0.4 | 0.354 | 0.473 | 763 |
| 0.4–0.5 | 0.489 | 0.484 | 78,379 |
| 0.5–0.6 | 0.517 | 0.479 | 17,517 |
| 0.6–0.7 | 0.626 | 0.393 | 178 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,913 over 250 days; share of "up": 0.468
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.445 | 0.2510 | 0.6951 | – | – | – | – | – |
| logreg | 0.506 | 0.2502 | 0.6937 | 0.530 | 0.0030 | 0.188 | 0.537 | 5.19 |
| lgbm | 0.473 | 0.2536 | 0.7004 | 0.468 | -0.0105 | 0.134 | 0.459 | -17.98 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.189 | 0.000 | 13 |
| 0.2–0.3 | 0.268 | 0.408 | 71 |
| 0.3–0.4 | 0.371 | 0.534 | 1,197 |
| 0.4–0.5 | 0.467 | 0.431 | 27,223 |
| 0.5–0.6 | 0.518 | 0.480 | 66,409 |
| 0.6–0.7 | 0.648 | 0.591 | 1,708 |
| 0.7–0.8 | 0.730 | 0.387 | 287 |
| 0.8–0.9 | 0.805 | 0.400 | 5 |
