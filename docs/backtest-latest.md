# IREN probability backtest (alpaca data)

Generated 2026-11-18T03:48:33+00:00 · data 2024-11-18T14:31:00+00:00 → 2026-11-17T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.521 | 0.519 | 0.2487 | 0.2497 | [-0.00123, -0.00056] | 0.519 | 250 | ✅ edge |
| 15m | logreg | 0.517 | 0.517 | 0.2495 | 0.2497 | [-0.00057, +0.00010] | 0.513 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.513 | 0.517 | 0.2500 | 0.2498 | [-0.00050, +0.00081] | 0.503 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.530 | 0.475 | 0.2500 | 0.2501 | [-0.00358, +0.00348] | 0.540 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,936 over 250 days; share of "up": 0.481
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.520 | 0.2488 | 0.6905 | 0.518 | 0.0035 | 0.029 | 0.621 | 0.98 |
| lgbm | 0.521 | 0.2487 | 0.6905 | 0.519 | 0.0036 | 0.034 | 0.595 | 1.10 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.184 | 0.056 | 177 |
| 0.2–0.3 | 0.234 | 0.136 | 544 |
| 0.3–0.4 | 0.373 | 0.478 | 247 |
| 0.4–0.5 | 0.479 | 0.476 | 67,483 |
| 0.5–0.6 | 0.513 | 0.502 | 28,447 |
| 0.6–0.7 | 0.605 | 0.526 | 38 |

## 15m (15 นาที)

- Test rows: 96,926 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.517 | 0.2495 | 0.6921 | 0.513 | 0.0009 | 0.027 | 0.570 | 1.22 |
| lgbm | 0.515 | 0.2496 | 0.6923 | 0.511 | 0.0006 | 0.041 | 0.549 | 0.38 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.166 | 0.167 | 42 |
| 0.2–0.3 | 0.266 | 0.190 | 179 |
| 0.3–0.4 | 0.354 | 0.327 | 410 |
| 0.4–0.5 | 0.486 | 0.480 | 75,223 |
| 0.5–0.6 | 0.514 | 0.500 | 20,905 |
| 0.6–0.7 | 0.624 | 0.455 | 167 |

## 1h (1 ชั่วโมง)

- Test rows: 96,881 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.512 | 0.2500 | 0.6932 | 0.505 | -0.0008 | 0.012 | 0.578 | 5.13 |
| lgbm | 0.513 | 0.2500 | 0.6931 | 0.503 | -0.0006 | 0.036 | 0.537 | 3.93 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.291 | 0.189 | 37 |
| 0.3–0.4 | 0.355 | 0.381 | 544 |
| 0.4–0.5 | 0.488 | 0.480 | 67,140 |
| 0.5–0.6 | 0.510 | 0.494 | 29,004 |
| 0.6–0.7 | 0.609 | 0.442 | 156 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,940 over 250 days; share of "up": 0.474
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.475 | 0.2501 | 0.6933 | – | – | – | – | – |
| logreg | 0.530 | 0.2500 | 0.6933 | 0.540 | 0.0003 | 0.270 | 0.557 | 21.12 |
| lgbm | 0.501 | 0.2514 | 0.6961 | 0.508 | -0.0054 | 0.166 | 0.530 | -7.47 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.173 | 0.000 | 20 |
| 0.2–0.3 | 0.268 | 0.292 | 168 |
| 0.3–0.4 | 0.371 | 0.473 | 3,358 |
| 0.4–0.5 | 0.473 | 0.440 | 42,628 |
| 0.5–0.6 | 0.527 | 0.500 | 45,911 |
| 0.6–0.7 | 0.631 | 0.552 | 4,627 |
| 0.7–0.8 | 0.749 | 0.369 | 206 |
| 0.8–0.9 | 0.816 | 0.318 | 22 |
