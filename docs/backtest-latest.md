# IREN probability backtest (alpaca data)

Generated 2026-11-24T06:14:07+00:00 · data 2024-11-25T14:30:00+00:00 → 2026-11-23T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.520 | 0.520 | 0.2488 | 0.2496 | [-0.00117, -0.00056] | 0.517 | 249 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.517 | 0.518 | 0.2495 | 0.2497 | [-0.00060, +0.00014] | 0.512 | 249 | ⚠️ **no proven edge** |
| 1h | logreg | 0.508 | 0.520 | 0.2497 | 0.2497 | [-0.00028, +0.00028] | 0.507 | 249 | ⚠️ **no proven edge** |
| eod | logreg | 0.540 | 0.499 | 0.2497 | 0.2501 | [-0.00373, +0.00319] | 0.550 | 249 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,543 over 249 days; share of "up": 0.480
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.520 | 0.2496 | 0.6924 | – | – | – | – | – |
| logreg | 0.522 | 0.2488 | 0.6906 | 0.519 | 0.0033 | 0.024 | 0.624 | 1.29 |
| lgbm | 0.520 | 0.2488 | 0.6905 | 0.517 | 0.0034 | 0.039 | 0.583 | 1.02 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.181 | 0.056 | 143 |
| 0.2–0.3 | 0.232 | 0.148 | 574 |
| 0.3–0.4 | 0.366 | 0.375 | 88 |
| 0.4–0.5 | 0.480 | 0.477 | 73,175 |
| 0.5–0.6 | 0.515 | 0.498 | 22,556 |
| 0.6–0.7 | 0.604 | 0.429 | 7 |

## 15m (15 นาที)

- Test rows: 96,533 over 249 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.517 | 0.2495 | 0.6922 | 0.510 | 0.0007 | 0.022 | 0.588 | 1.13 |
| lgbm | 0.517 | 0.2495 | 0.6921 | 0.512 | 0.0009 | 0.027 | 0.579 | 1.44 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.292 | 0.122 | 90 |
| 0.3–0.4 | 0.354 | 0.302 | 932 |
| 0.4–0.5 | 0.481 | 0.477 | 63,102 |
| 0.5–0.6 | 0.513 | 0.498 | 32,409 |

## 1h (1 ชั่วโมง)

- Test rows: 96,488 over 249 days; share of "up": 0.480
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.520 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.508 | 0.2497 | 0.6926 | 0.507 | -0.0000 | 0.008 | 0.596 | 4.54 |
| lgbm | 0.512 | 0.2500 | 0.6931 | 0.498 | -0.0009 | 0.040 | 0.531 | 2.52 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.285 | 0.417 | 12 |
| 0.3–0.4 | 0.353 | 0.400 | 155 |
| 0.4–0.5 | 0.492 | 0.483 | 78,921 |
| 0.5–0.6 | 0.504 | 0.467 | 17,400 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,547 over 249 days; share of "up": 0.470
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.499 | 0.2501 | 0.6933 | – | – | – | – | – |
| logreg | 0.540 | 0.2497 | 0.6928 | 0.550 | 0.0013 | 0.251 | 0.565 | 25.13 |
| lgbm | 0.506 | 0.2513 | 0.6960 | 0.505 | -0.0051 | 0.180 | 0.545 | 2.09 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.168 | 0.000 | 26 |
| 0.2–0.3 | 0.268 | 0.323 | 158 |
| 0.3–0.4 | 0.375 | 0.439 | 4,809 |
| 0.4–0.5 | 0.477 | 0.424 | 40,306 |
| 0.5–0.6 | 0.528 | 0.512 | 46,549 |
| 0.6–0.7 | 0.629 | 0.499 | 4,417 |
| 0.7–0.8 | 0.730 | 0.248 | 282 |
