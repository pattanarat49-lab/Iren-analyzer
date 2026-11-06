# IREN probability backtest (alpaca data)

Generated 2026-11-06T02:40:10+00:00 · data 2024-11-05T14:40:00+00:00 → 2026-11-05T21:56:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.514 | 0.519 | 0.2489 | 0.2497 | [-0.00109, -0.00042] | 0.514 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.508 | 0.518 | 0.2497 | 0.2498 | [-0.00038, +0.00036] | 0.504 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.503 | 0.517 | 0.2503 | 0.2499 | [-0.00049, +0.00134] | 0.495 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.499 | 0.482 | 0.2503 | 0.2508 | [-0.00319, +0.00203] | 0.528 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,907 over 250 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.518 | 0.2490 | 0.6910 | 0.513 | 0.0026 | 0.023 | 0.642 | 0.91 |
| lgbm | 0.514 | 0.2489 | 0.6909 | 0.514 | 0.0029 | 0.030 | 0.605 | 0.66 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.192 | 0.049 | 144 |
| 0.2–0.3 | 0.248 | 0.144 | 457 |
| 0.3–0.4 | 0.340 | 0.292 | 236 |
| 0.4–0.5 | 0.481 | 0.480 | 67,923 |
| 0.5–0.6 | 0.514 | 0.492 | 28,127 |
| 0.6–0.7 | 0.604 | 0.750 | 20 |

## 15m (15 นาที)

- Test rows: 96,904 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2498 | 0.6926 | – | – | – | – | – |
| logreg | 0.510 | 0.2497 | 0.6926 | 0.508 | 0.0001 | 0.034 | 0.542 | 0.14 |
| lgbm | 0.508 | 0.2497 | 0.6926 | 0.504 | 0.0001 | 0.032 | 0.569 | -0.76 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.266 | 0.143 | 105 |
| 0.3–0.4 | 0.358 | 0.343 | 893 |
| 0.4–0.5 | 0.486 | 0.485 | 69,114 |
| 0.5–0.6 | 0.516 | 0.482 | 26,790 |
| 0.6–0.7 | 0.605 | 1.000 | 2 |

## 1h (1 ชั่วโมง)

- Test rows: 96,896 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.508 | 0.2503 | 0.6938 | 0.484 | -0.0015 | 0.017 | 0.488 | 1.54 |
| lgbm | 0.503 | 0.2503 | 0.6937 | 0.495 | -0.0015 | 0.042 | 0.526 | 1.35 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.293 | 0.152 | 112 |
| 0.3–0.4 | 0.337 | 0.436 | 908 |
| 0.4–0.5 | 0.487 | 0.487 | 67,624 |
| 0.5–0.6 | 0.516 | 0.475 | 28,230 |
| 0.6–0.7 | 0.602 | 0.591 | 22 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,898 over 250 days; share of "up": 0.468
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.482 | 0.2508 | 0.6947 | – | – | – | – | – |
| logreg | 0.499 | 0.2503 | 0.6939 | 0.528 | 0.0020 | 0.230 | 0.537 | 1.58 |
| lgbm | 0.492 | 0.2515 | 0.6962 | 0.503 | -0.0028 | 0.123 | 0.503 | -5.30 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.191 | 0.000 | 11 |
| 0.2–0.3 | 0.276 | 0.419 | 43 |
| 0.3–0.4 | 0.378 | 0.511 | 1,208 |
| 0.4–0.5 | 0.473 | 0.457 | 34,225 |
| 0.5–0.6 | 0.523 | 0.470 | 59,189 |
| 0.6–0.7 | 0.641 | 0.616 | 1,973 |
| 0.7–0.8 | 0.728 | 0.319 | 248 |
| 0.8–0.9 | 0.801 | 0.000 | 1 |
