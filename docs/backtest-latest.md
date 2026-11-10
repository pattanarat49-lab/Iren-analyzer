# IREN probability backtest (alpaca data)

Generated 2026-11-10T04:15:38+00:00 · data 2024-11-11T14:30:00+00:00 → 2026-11-09T21:00:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.519 | 0.519 | 0.2489 | 0.2497 | [-0.00105, -0.00049] | 0.513 | 249 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.513 | 0.517 | 0.2496 | 0.2497 | [-0.00060, +0.00023] | 0.507 | 249 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.506 | 0.517 | 0.2498 | 0.2499 | [-0.00085, +0.00058] | 0.502 | 249 | ⚠️ **no proven edge** |
| eod | logreg | 0.516 | 0.469 | 0.2501 | 0.2505 | [-0.00340, +0.00270] | 0.531 | 249 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,537 over 249 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.519 | 0.2489 | 0.6908 | 0.513 | 0.0031 | 0.026 | 0.623 | 0.96 |
| lgbm | 0.515 | 0.2489 | 0.6908 | 0.515 | 0.0030 | 0.044 | 0.565 | 0.70 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.095 | 0.182 | 11 |
| 0.1–0.2 | 0.163 | 0.080 | 163 |
| 0.2–0.3 | 0.242 | 0.126 | 389 |
| 0.3–0.4 | 0.362 | 0.364 | 341 |
| 0.4–0.5 | 0.482 | 0.479 | 73,270 |
| 0.5–0.6 | 0.515 | 0.500 | 22,350 |
| 0.6–0.7 | 0.612 | 0.462 | 13 |

## 15m (15 นาที)

- Test rows: 96,527 over 249 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.513 | 0.2496 | 0.6923 | 0.507 | 0.0006 | 0.034 | 0.538 | 0.43 |
| lgbm | 0.513 | 0.2496 | 0.6922 | 0.507 | 0.0008 | 0.040 | 0.561 | 0.76 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.268 | 0.142 | 127 |
| 0.3–0.4 | 0.346 | 0.348 | 992 |
| 0.4–0.5 | 0.483 | 0.481 | 68,151 |
| 0.5–0.6 | 0.514 | 0.493 | 27,255 |
| 0.6–0.7 | 0.603 | 1.000 | 2 |

## 1h (1 ชั่วโมง)

- Test rows: 96,482 over 249 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.509 | 0.2501 | 0.6933 | 0.488 | -0.0007 | 0.015 | 0.544 | 4.05 |
| lgbm | 0.506 | 0.2498 | 0.6927 | 0.502 | 0.0004 | 0.053 | 0.555 | 0.97 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.369 | 0.338 | 616 |
| 0.4–0.5 | 0.486 | 0.484 | 63,107 |
| 0.5–0.6 | 0.509 | 0.483 | 32,539 |
| 0.6–0.7 | 0.614 | 0.495 | 220 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,540 over 249 days; share of "up": 0.470
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.469 | 0.2505 | 0.6941 | – | – | – | – | – |
| logreg | 0.516 | 0.2501 | 0.6936 | 0.531 | 0.0013 | 0.250 | 0.562 | 14.25 |
| lgbm | 0.507 | 0.2507 | 0.6945 | 0.511 | -0.0009 | 0.103 | 0.466 | 3.32 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.181 | 0.000 | 14 |
| 0.2–0.3 | 0.258 | 0.392 | 74 |
| 0.3–0.4 | 0.376 | 0.494 | 2,129 |
| 0.4–0.5 | 0.470 | 0.444 | 38,539 |
| 0.5–0.6 | 0.527 | 0.485 | 52,834 |
| 0.6–0.7 | 0.626 | 0.557 | 2,564 |
| 0.7–0.8 | 0.734 | 0.458 | 330 |
| 0.8–0.9 | 0.818 | 0.286 | 56 |
