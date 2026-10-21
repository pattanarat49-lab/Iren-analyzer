# IREN probability backtest (alpaca data)

Generated 2026-10-21T22:56:22+00:00 · data 2024-10-21T12:56:00+00:00 → 2026-10-21T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.514 | 0.518 | 0.2490 | 0.2497 | [-0.00106, -0.00036] | 0.514 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.502 | 0.515 | 0.2500 | 0.2498 | [-0.00019, +0.00059] | 0.496 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.501 | 0.516 | 0.2502 | 0.2499 | [-0.00027, +0.00090] | 0.494 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.511 | 0.480 | 0.2505 | 0.2511 | [-0.00388, +0.00283] | 0.538 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,893 over 250 days; share of "up": 0.482
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.512 | 0.2490 | 0.6911 | 0.514 | 0.0027 | 0.019 | 0.655 | 0.54 |
| lgbm | 0.514 | 0.2490 | 0.6910 | 0.514 | 0.0029 | 0.031 | 0.612 | 0.73 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.197 | 0.068 | 44 |
| 0.2–0.3 | 0.220 | 0.116 | 464 |
| 0.3–0.4 | 0.350 | 0.192 | 265 |
| 0.4–0.5 | 0.480 | 0.480 | 63,339 |
| 0.5–0.6 | 0.515 | 0.494 | 32,781 |

## 15m (15 นาที)

- Test rows: 96,883 over 250 days; share of "up": 0.485
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.515 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.504 | 0.2500 | 0.6931 | 0.501 | -0.0007 | 0.019 | 0.545 | 0.11 |
| lgbm | 0.502 | 0.2500 | 0.6931 | 0.496 | -0.0007 | 0.037 | 0.534 | -0.95 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.265 | 0.117 | 180 |
| 0.3–0.4 | 0.357 | 0.286 | 605 |
| 0.4–0.5 | 0.485 | 0.490 | 65,750 |
| 0.5–0.6 | 0.516 | 0.479 | 30,338 |
| 0.6–0.7 | 0.606 | 0.900 | 10 |

## 1h (1 ชั่วโมง)

- Test rows: 96,838 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.501 | 0.2502 | 0.6935 | 0.494 | -0.0011 | 0.016 | 0.565 | 0.36 |
| lgbm | 0.502 | 0.2502 | 0.6936 | 0.497 | -0.0013 | 0.037 | 0.553 | 0.50 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.179 | 0.440 | 25 |
| 0.2–0.3 | 0.287 | 0.308 | 104 |
| 0.3–0.4 | 0.357 | 0.460 | 174 |
| 0.4–0.5 | 0.487 | 0.488 | 66,489 |
| 0.5–0.6 | 0.512 | 0.476 | 30,045 |
| 0.6–0.7 | 0.602 | 0.000 | 1 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,897 over 250 days; share of "up": 0.467
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.480 | 0.2511 | 0.6954 | – | – | – | – | – |
| logreg | 0.511 | 0.2505 | 0.6944 | 0.538 | 0.0024 | 0.273 | 0.548 | 9.72 |
| lgbm | 0.465 | 0.2557 | 0.7046 | 0.454 | -0.0181 | 0.200 | 0.427 | -18.56 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.185 | 0.000 | 15 |
| 0.2–0.3 | 0.269 | 0.345 | 290 |
| 0.3–0.4 | 0.376 | 0.415 | 3,890 |
| 0.4–0.5 | 0.462 | 0.434 | 26,458 |
| 0.5–0.6 | 0.526 | 0.481 | 62,459 |
| 0.6–0.7 | 0.640 | 0.540 | 2,873 |
| 0.7–0.8 | 0.737 | 0.488 | 841 |
| 0.8–0.9 | 0.823 | 0.310 | 71 |
