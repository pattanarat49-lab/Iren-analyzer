# IREN probability backtest (alpaca data)

Generated 2026-11-11T02:02:33+00:00 · data 2024-11-11T14:30:00+00:00 → 2026-11-10T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.519 | 0.519 | 0.2489 | 0.2497 | [-0.00106, -0.00049] | 0.513 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.513 | 0.517 | 0.2495 | 0.2497 | [-0.00057, +0.00021] | 0.507 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.507 | 0.518 | 0.2498 | 0.2499 | [-0.00084, +0.00065] | 0.503 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.516 | 0.469 | 0.2501 | 0.2505 | [-0.00331, +0.00260] | 0.531 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,930 over 250 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.519 | 0.2489 | 0.6908 | 0.513 | 0.0031 | 0.026 | 0.623 | 0.99 |
| lgbm | 0.516 | 0.2489 | 0.6908 | 0.515 | 0.0030 | 0.044 | 0.566 | 0.71 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.095 | 0.182 | 11 |
| 0.1–0.2 | 0.163 | 0.080 | 163 |
| 0.2–0.3 | 0.242 | 0.125 | 393 |
| 0.3–0.4 | 0.362 | 0.363 | 342 |
| 0.4–0.5 | 0.482 | 0.478 | 73,646 |
| 0.5–0.6 | 0.515 | 0.500 | 22,362 |
| 0.6–0.7 | 0.612 | 0.462 | 13 |

## 15m (15 นาที)

- Test rows: 96,920 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.513 | 0.2496 | 0.6923 | 0.507 | 0.0006 | 0.034 | 0.539 | 0.52 |
| lgbm | 0.513 | 0.2495 | 0.6922 | 0.507 | 0.0008 | 0.040 | 0.562 | 0.85 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.268 | 0.141 | 128 |
| 0.3–0.4 | 0.346 | 0.347 | 995 |
| 0.4–0.5 | 0.483 | 0.481 | 68,474 |
| 0.5–0.6 | 0.514 | 0.493 | 27,321 |
| 0.6–0.7 | 0.603 | 1.000 | 2 |

## 1h (1 ชั่วโมง)

- Test rows: 96,875 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.510 | 0.2501 | 0.6933 | 0.488 | -0.0007 | 0.015 | 0.544 | 4.32 |
| lgbm | 0.507 | 0.2498 | 0.6927 | 0.503 | 0.0004 | 0.053 | 0.555 | 1.49 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.369 | 0.338 | 616 |
| 0.4–0.5 | 0.486 | 0.483 | 63,500 |
| 0.5–0.6 | 0.509 | 0.483 | 32,539 |
| 0.6–0.7 | 0.614 | 0.495 | 220 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,934 over 250 days; share of "up": 0.471
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.469 | 0.2505 | 0.6941 | – | – | – | – | – |
| logreg | 0.516 | 0.2501 | 0.6936 | 0.531 | 0.0015 | 0.249 | 0.562 | 14.72 |
| lgbm | 0.507 | 0.2507 | 0.6945 | 0.511 | -0.0008 | 0.103 | 0.465 | 3.40 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.181 | 0.000 | 14 |
| 0.2–0.3 | 0.258 | 0.392 | 74 |
| 0.3–0.4 | 0.376 | 0.494 | 2,129 |
| 0.4–0.5 | 0.470 | 0.445 | 38,837 |
| 0.5–0.6 | 0.527 | 0.486 | 52,930 |
| 0.6–0.7 | 0.626 | 0.557 | 2,564 |
| 0.7–0.8 | 0.734 | 0.458 | 330 |
| 0.8–0.9 | 0.818 | 0.286 | 56 |
