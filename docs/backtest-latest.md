# IREN probability backtest (alpaca data)

Generated 2026-11-05T02:40:36+00:00 · data 2024-11-04T14:41:00+00:00 → 2026-11-04T21:49:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.514 | 0.519 | 0.2490 | 0.2497 | [-0.00096, -0.00032] | 0.514 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.503 | 0.518 | 0.2497 | 0.2498 | [-0.00041, +0.00034] | 0.504 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.499 | 0.518 | 0.2503 | 0.2499 | [-0.00013, +0.00100] | 0.488 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.504 | 0.482 | 0.2504 | 0.2510 | [-0.00348, +0.00235] | 0.530 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,914 over 250 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.516 | 0.2491 | 0.6912 | 0.513 | 0.0023 | 0.028 | 0.612 | 0.81 |
| lgbm | 0.514 | 0.2490 | 0.6910 | 0.514 | 0.0026 | 0.033 | 0.588 | 0.57 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.192 | 0.035 | 85 |
| 0.2–0.3 | 0.243 | 0.152 | 652 |
| 0.3–0.4 | 0.374 | 0.483 | 149 |
| 0.4–0.5 | 0.479 | 0.479 | 64,196 |
| 0.5–0.6 | 0.516 | 0.493 | 31,825 |
| 0.6–0.7 | 0.602 | 0.286 | 7 |

## 15m (15 นาที)

- Test rows: 96,914 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.506 | 0.2498 | 0.6928 | 0.506 | -0.0002 | 0.047 | 0.536 | -0.60 |
| lgbm | 0.503 | 0.2497 | 0.6926 | 0.504 | 0.0002 | 0.042 | 0.560 | -1.15 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.252 | 0.164 | 110 |
| 0.3–0.4 | 0.357 | 0.316 | 883 |
| 0.4–0.5 | 0.485 | 0.488 | 65,648 |
| 0.5–0.6 | 0.516 | 0.477 | 30,271 |
| 0.6–0.7 | 0.606 | 1.000 | 2 |

## 1h (1 ชั่วโมง)

- Test rows: 96,902 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.499 | 0.2503 | 0.6939 | 0.488 | -0.0017 | 0.030 | 0.504 | 0.58 |
| lgbm | 0.501 | 0.2504 | 0.6939 | 0.493 | -0.0018 | 0.044 | 0.531 | -1.19 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.127 | 0.429 | 28 |
| 0.2–0.3 | 0.225 | 0.300 | 50 |
| 0.3–0.4 | 0.364 | 0.380 | 229 |
| 0.4–0.5 | 0.490 | 0.489 | 73,534 |
| 0.5–0.6 | 0.514 | 0.462 | 22,866 |
| 0.6–0.7 | 0.616 | 0.297 | 195 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,911 over 250 days; share of "up": 0.468
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.482 | 0.2510 | 0.6952 | – | – | – | – | – |
| logreg | 0.504 | 0.2504 | 0.6940 | 0.530 | 0.0024 | 0.242 | 0.537 | 4.71 |
| lgbm | 0.493 | 0.2516 | 0.6963 | 0.497 | -0.0023 | 0.117 | 0.504 | -4.72 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.189 | 0.000 | 11 |
| 0.2–0.3 | 0.275 | 0.396 | 48 |
| 0.3–0.4 | 0.376 | 0.487 | 1,546 |
| 0.4–0.5 | 0.473 | 0.452 | 35,328 |
| 0.5–0.6 | 0.524 | 0.472 | 56,597 |
| 0.6–0.7 | 0.633 | 0.571 | 2,988 |
| 0.7–0.8 | 0.728 | 0.448 | 393 |
