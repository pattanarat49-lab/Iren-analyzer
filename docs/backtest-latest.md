# IREN probability backtest (alpaca data)

Generated 2026-11-17T04:41:46+00:00 · data 2024-11-18T14:31:00+00:00 → 2026-11-16T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.520 | 0.519 | 0.2488 | 0.2497 | [-0.00120, -0.00053] | 0.519 | 249 | ✅ edge |
| 15m | logreg | 0.517 | 0.517 | 0.2495 | 0.2497 | [-0.00055, +0.00014] | 0.513 | 249 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.513 | 0.516 | 0.2500 | 0.2498 | [-0.00058, +0.00083] | 0.503 | 249 | ⚠️ **no proven edge** |
| eod | logreg | 0.529 | 0.475 | 0.2500 | 0.2501 | [-0.00340, +0.00325] | 0.539 | 249 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,540 over 249 days; share of "up": 0.481
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.520 | 0.2488 | 0.6906 | 0.518 | 0.0034 | 0.029 | 0.619 | 0.95 |
| lgbm | 0.520 | 0.2488 | 0.6905 | 0.519 | 0.0036 | 0.034 | 0.595 | 1.08 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.184 | 0.056 | 177 |
| 0.2–0.3 | 0.234 | 0.139 | 533 |
| 0.3–0.4 | 0.373 | 0.478 | 247 |
| 0.4–0.5 | 0.479 | 0.476 | 67,127 |
| 0.5–0.6 | 0.513 | 0.502 | 28,418 |
| 0.6–0.7 | 0.605 | 0.526 | 38 |

## 15m (15 นาที)

- Test rows: 96,530 over 249 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.517 | 0.2495 | 0.6922 | 0.513 | 0.0009 | 0.027 | 0.569 | 1.16 |
| lgbm | 0.514 | 0.2496 | 0.6923 | 0.511 | 0.0005 | 0.041 | 0.549 | 0.37 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.168 | 0.159 | 44 |
| 0.2–0.3 | 0.266 | 0.195 | 169 |
| 0.3–0.4 | 0.354 | 0.325 | 409 |
| 0.4–0.5 | 0.486 | 0.480 | 74,688 |
| 0.5–0.6 | 0.514 | 0.500 | 21,053 |
| 0.6–0.7 | 0.624 | 0.455 | 167 |

## 1h (1 ชั่วโมง)

- Test rows: 96,485 over 249 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.512 | 0.2500 | 0.6932 | 0.504 | -0.0008 | 0.012 | 0.576 | 4.91 |
| lgbm | 0.513 | 0.2500 | 0.6931 | 0.503 | -0.0005 | 0.037 | 0.537 | 3.72 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.291 | 0.189 | 37 |
| 0.3–0.4 | 0.355 | 0.381 | 544 |
| 0.4–0.5 | 0.488 | 0.480 | 66,765 |
| 0.5–0.6 | 0.510 | 0.495 | 28,983 |
| 0.6–0.7 | 0.609 | 0.442 | 156 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,544 over 249 days; share of "up": 0.475
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.475 | 0.2501 | 0.6933 | – | – | – | – | – |
| logreg | 0.529 | 0.2500 | 0.6934 | 0.539 | 0.0002 | 0.271 | 0.557 | 20.93 |
| lgbm | 0.501 | 0.2514 | 0.6962 | 0.508 | -0.0054 | 0.167 | 0.530 | -7.56 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.173 | 0.000 | 20 |
| 0.2–0.3 | 0.268 | 0.292 | 168 |
| 0.3–0.4 | 0.371 | 0.473 | 3,358 |
| 0.4–0.5 | 0.473 | 0.441 | 42,338 |
| 0.5–0.6 | 0.527 | 0.499 | 45,805 |
| 0.6–0.7 | 0.631 | 0.552 | 4,627 |
| 0.7–0.8 | 0.749 | 0.369 | 206 |
| 0.8–0.9 | 0.816 | 0.318 | 22 |
