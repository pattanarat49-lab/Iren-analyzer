# IREN probability backtest (alpaca data)

Generated 2026-10-28T01:32:41+00:00 · data 2024-10-28T13:30:00+00:00 → 2026-10-27T20:02:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.515 | 0.519 | 0.2490 | 0.2497 | [-0.00093, -0.00034] | 0.513 | 250 | ⚠️ **no proven edge** |
| 15m | logreg | 0.508 | 0.517 | 0.2498 | 0.2498 | [-0.00023, +0.00037] | 0.500 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.515 | 0.519 | 0.2501 | 0.2499 | [-0.00038, +0.00081] | 0.493 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.501 | 0.466 | 0.2508 | 0.2512 | [-0.00345, +0.00283] | 0.516 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,909 over 250 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.515 | 0.2490 | 0.6911 | 0.513 | 0.0026 | 0.020 | 0.649 | 0.82 |
| lgbm | 0.513 | 0.2491 | 0.6911 | 0.513 | 0.0024 | 0.052 | 0.556 | 0.53 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.176 | 0.108 | 157 |
| 0.2–0.3 | 0.236 | 0.133 | 241 |
| 0.3–0.4 | 0.335 | 0.229 | 410 |
| 0.4–0.5 | 0.482 | 0.479 | 65,060 |
| 0.5–0.6 | 0.511 | 0.494 | 30,952 |
| 0.6–0.7 | 0.612 | 0.750 | 4 |
| 0.7–0.8 | 0.720 | 0.518 | 85 |

## 15m (15 นาที)

- Test rows: 96,899 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.508 | 0.2498 | 0.6928 | 0.500 | -0.0003 | 0.023 | 0.558 | 0.31 |
| lgbm | 0.499 | 0.2498 | 0.6928 | 0.498 | -0.0003 | 0.021 | 0.599 | -1.95 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.180 | 0.208 | 24 |
| 0.2–0.3 | 0.258 | 0.255 | 204 |
| 0.3–0.4 | 0.357 | 0.230 | 296 |
| 0.4–0.5 | 0.485 | 0.484 | 68,095 |
| 0.5–0.6 | 0.510 | 0.484 | 28,169 |
| 0.6–0.7 | 0.644 | 0.604 | 111 |

## 1h (1 ชั่วโมง)

- Test rows: 96,854 over 250 days; share of "up": 0.481
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.515 | 0.2501 | 0.6933 | 0.493 | -0.0008 | 0.032 | 0.518 | 2.91 |
| lgbm | 0.502 | 0.2505 | 0.6941 | 0.495 | -0.0023 | 0.038 | 0.478 | -1.31 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.161 | 0.429 | 28 |
| 0.2–0.3 | 0.269 | 0.316 | 98 |
| 0.3–0.4 | 0.364 | 0.321 | 461 |
| 0.4–0.5 | 0.490 | 0.480 | 77,665 |
| 0.5–0.6 | 0.516 | 0.492 | 18,562 |
| 0.6–0.7 | 0.624 | 0.175 | 40 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,910 over 250 days; share of "up": 0.464
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.466 | 0.2512 | 0.6955 | – | – | – | – | – |
| logreg | 0.501 | 0.2508 | 0.6949 | 0.516 | 0.0016 | 0.206 | 0.537 | 1.52 |
| lgbm | 0.471 | 0.2548 | 0.7029 | 0.461 | -0.0145 | 0.223 | 0.460 | -16.63 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.184 | 0.000 | 20 |
| 0.2–0.3 | 0.264 | 0.412 | 80 |
| 0.3–0.4 | 0.373 | 0.448 | 2,001 |
| 0.4–0.5 | 0.460 | 0.431 | 23,845 |
| 0.5–0.6 | 0.520 | 0.473 | 68,356 |
| 0.6–0.7 | 0.640 | 0.581 | 1,971 |
| 0.7–0.8 | 0.729 | 0.456 | 621 |
| 0.8–0.9 | 0.819 | 0.375 | 16 |
