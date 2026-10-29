# IREN probability backtest (alpaca data)

Generated 2026-10-29T01:56:09+00:00 · data 2024-10-28T13:56:00+00:00 → 2026-10-28T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.517 | 0.519 | 0.2490 | 0.2497 | [-0.00094, -0.00036] | 0.514 | 250 | ⚠️ **no proven edge** |
| 15m | logreg | 0.503 | 0.517 | 0.2499 | 0.2498 | [-0.00026, +0.00043] | 0.503 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.505 | 0.517 | 0.2501 | 0.2499 | [-0.00053, +0.00112] | 0.498 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.506 | 0.463 | 0.2505 | 0.2512 | [-0.00320, +0.00183] | 0.516 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,905 over 250 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.517 | 0.2490 | 0.6911 | 0.514 | 0.0026 | 0.023 | 0.633 | 0.98 |
| lgbm | 0.511 | 0.2490 | 0.6911 | 0.513 | 0.0025 | 0.036 | 0.584 | 0.23 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.172 | 0.083 | 120 |
| 0.2–0.3 | 0.259 | 0.087 | 286 |
| 0.3–0.4 | 0.348 | 0.273 | 355 |
| 0.4–0.5 | 0.483 | 0.478 | 68,367 |
| 0.5–0.6 | 0.512 | 0.497 | 27,689 |
| 0.6–0.7 | 0.648 | 0.667 | 12 |
| 0.7–0.8 | 0.718 | 0.487 | 76 |

## 15m (15 นาที)

- Test rows: 96,895 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.503 | 0.2499 | 0.6928 | 0.503 | -0.0003 | 0.036 | 0.532 | -0.41 |
| lgbm | 0.499 | 0.2499 | 0.6929 | 0.499 | -0.0005 | 0.031 | 0.552 | -1.98 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.183 | 0.147 | 34 |
| 0.2–0.3 | 0.267 | 0.194 | 134 |
| 0.3–0.4 | 0.355 | 0.265 | 306 |
| 0.4–0.5 | 0.483 | 0.487 | 63,447 |
| 0.5–0.6 | 0.511 | 0.480 | 32,941 |
| 0.6–0.7 | 0.608 | 0.697 | 33 |

## 1h (1 ชั่วโมง)

- Test rows: 96,850 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.515 | 0.2502 | 0.6935 | 0.492 | -0.0012 | 0.030 | 0.509 | 3.26 |
| lgbm | 0.505 | 0.2501 | 0.6934 | 0.498 | -0.0010 | 0.034 | 0.548 | 1.24 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.290 | 0.185 | 92 |
| 0.3–0.4 | 0.359 | 0.489 | 1,048 |
| 0.4–0.5 | 0.489 | 0.486 | 75,013 |
| 0.5–0.6 | 0.518 | 0.472 | 20,676 |
| 0.6–0.7 | 0.604 | 0.143 | 21 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,909 over 250 days; share of "up": 0.467
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.463 | 0.2512 | 0.6955 | – | – | – | – | – |
| logreg | 0.506 | 0.2505 | 0.6943 | 0.516 | 0.0027 | 0.182 | 0.548 | 4.53 |
| lgbm | 0.470 | 0.2549 | 0.7031 | 0.462 | -0.0148 | 0.187 | 0.435 | -19.81 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.189 | 0.000 | 13 |
| 0.2–0.3 | 0.269 | 0.412 | 51 |
| 0.3–0.4 | 0.373 | 0.521 | 1,070 |
| 0.4–0.5 | 0.468 | 0.432 | 28,092 |
| 0.5–0.6 | 0.519 | 0.479 | 65,590 |
| 0.6–0.7 | 0.641 | 0.593 | 1,782 |
| 0.7–0.8 | 0.731 | 0.366 | 306 |
| 0.8–0.9 | 0.804 | 0.400 | 5 |
