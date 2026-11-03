# IREN probability backtest (alpaca data)

Generated 2026-11-03T03:33:40+00:00 · data 2024-11-04T14:30:00+00:00 → 2026-11-02T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.514 | 0.519 | 0.2489 | 0.2497 | [-0.00106, -0.00045] | 0.515 | 249 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.503 | 0.517 | 0.2499 | 0.2498 | [-0.00032, +0.00049] | 0.500 | 249 | ⚠️ **no proven edge** |
| 1h | logreg | 0.498 | 0.517 | 0.2505 | 0.2499 | [-0.00001, +0.00117] | 0.483 | 249 | ⚠️ **no proven edge** |
| eod | logreg | 0.516 | 0.481 | 0.2504 | 0.2509 | [-0.00359, +0.00249] | 0.532 | 249 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,516 over 249 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.517 | 0.2491 | 0.6912 | 0.514 | 0.0024 | 0.023 | 0.635 | 0.85 |
| lgbm | 0.514 | 0.2489 | 0.6908 | 0.515 | 0.0030 | 0.030 | 0.600 | 0.67 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.195 | 0.000 | 60 |
| 0.2–0.3 | 0.244 | 0.146 | 591 |
| 0.3–0.4 | 0.331 | 0.242 | 132 |
| 0.4–0.5 | 0.481 | 0.480 | 66,810 |
| 0.5–0.6 | 0.514 | 0.492 | 28,922 |
| 0.6–0.7 | 0.602 | 1.000 | 1 |

## 15m (15 นาที)

- Test rows: 96,506 over 249 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.506 | 0.2499 | 0.6930 | 0.502 | -0.0007 | 0.035 | 0.522 | -0.14 |
| lgbm | 0.503 | 0.2499 | 0.6928 | 0.500 | -0.0004 | 0.032 | 0.570 | -1.45 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.270 | 0.215 | 386 |
| 0.3–0.4 | 0.359 | 0.442 | 453 |
| 0.4–0.5 | 0.485 | 0.488 | 69,691 |
| 0.5–0.6 | 0.518 | 0.473 | 25,968 |
| 0.6–0.7 | 0.603 | 0.000 | 8 |

## 1h (1 ชั่วโมง)

- Test rows: 96,461 over 249 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.498 | 0.2505 | 0.6941 | 0.483 | -0.0022 | 0.034 | 0.510 | -0.14 |
| lgbm | 0.512 | 0.2505 | 0.6941 | 0.496 | -0.0022 | 0.042 | 0.548 | 2.47 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.148 | 0.356 | 45 |
| 0.2–0.3 | 0.233 | 0.342 | 38 |
| 0.3–0.4 | 0.372 | 0.428 | 299 |
| 0.4–0.5 | 0.491 | 0.490 | 73,330 |
| 0.5–0.6 | 0.512 | 0.461 | 22,563 |
| 0.6–0.7 | 0.616 | 0.382 | 186 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,520 over 249 days; share of "up": 0.469
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.481 | 0.2509 | 0.6950 | – | – | – | – | – |
| logreg | 0.516 | 0.2504 | 0.6940 | 0.532 | 0.0021 | 0.244 | 0.537 | 11.00 |
| lgbm | 0.486 | 0.2524 | 0.6979 | 0.494 | -0.0058 | 0.153 | 0.476 | -8.79 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.199 | 0.000 | 3 |
| 0.2–0.3 | 0.261 | 0.243 | 37 |
| 0.3–0.4 | 0.378 | 0.509 | 1,245 |
| 0.4–0.5 | 0.478 | 0.448 | 44,405 |
| 0.5–0.6 | 0.528 | 0.480 | 46,537 |
| 0.6–0.7 | 0.627 | 0.562 | 4,046 |
| 0.7–0.8 | 0.723 | 0.328 | 247 |
