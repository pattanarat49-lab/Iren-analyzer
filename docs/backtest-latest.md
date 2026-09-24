# IREN probability backtest (alpaca data)

Generated 2026-09-24T15:14:01+00:00 · data 2024-09-24T13:15:00+00:00 → 2026-09-24T15:10:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.514 | 0.514 | 0.2490 | 0.2500 | [-0.00127, -0.00064] | 0.515 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.511 | 0.511 | 0.2497 | 0.2499 | [-0.00055, +0.00018] | 0.508 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.503 | 0.512 | 0.2501 | 0.2499 | [-0.00044, +0.00089] | 0.507 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.522 | 0.435 | 0.2520 | 0.2508 | [-0.00284, +0.00555] | 0.528 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,667 over 250 days; share of "up": 0.486
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2500 | 0.6931 | – | – | – | – | – |
| logreg | 0.517 | 0.2491 | 0.6912 | 0.516 | 0.0035 | 0.021 | 0.656 | 1.02 |
| lgbm | 0.514 | 0.2490 | 0.6910 | 0.515 | 0.0039 | 0.031 | 0.613 | 0.53 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.192 | 0.031 | 127 |
| 0.2–0.3 | 0.249 | 0.160 | 561 |
| 0.3–0.4 | 0.368 | 0.346 | 211 |
| 0.4–0.5 | 0.481 | 0.484 | 66,154 |
| 0.5–0.6 | 0.512 | 0.500 | 29,614 |

## 15m (15 นาที)

- Test rows: 96,657 over 250 days; share of "up": 0.489
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.511 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.513 | 0.2497 | 0.6926 | 0.512 | 0.0007 | 0.021 | 0.570 | 1.63 |
| lgbm | 0.511 | 0.2497 | 0.6924 | 0.508 | 0.0009 | 0.026 | 0.574 | 0.46 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.270 | 0.152 | 231 |
| 0.3–0.4 | 0.354 | 0.257 | 525 |
| 0.4–0.5 | 0.486 | 0.486 | 60,876 |
| 0.5–0.6 | 0.512 | 0.499 | 35,004 |
| 0.6–0.7 | 0.603 | 0.857 | 21 |

## 1h (1 ชั่วโมง)

- Test rows: 96,612 over 250 days; share of "up": 0.488
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.512 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.503 | 0.2501 | 0.6933 | 0.507 | -0.0008 | 0.033 | 0.535 | 1.60 |
| lgbm | 0.498 | 0.2504 | 0.6939 | 0.495 | -0.0019 | 0.028 | 0.534 | -0.73 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.287 | 0.143 | 7 |
| 0.3–0.4 | 0.373 | 0.395 | 266 |
| 0.4–0.5 | 0.483 | 0.485 | 47,643 |
| 0.5–0.6 | 0.512 | 0.491 | 48,695 |
| 0.6–0.7 | 0.605 | 0.000 | 1 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,966 over 250 days; share of "up": 0.473
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.435 | 0.2508 | 0.6948 | – | – | – | – | – |
| logreg | 0.522 | 0.2520 | 0.6975 | 0.528 | -0.0047 | 0.310 | 0.535 | 2.80 |
| lgbm | 0.492 | 0.2537 | 0.7007 | 0.496 | -0.0115 | 0.295 | 0.476 | -15.14 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.183 | 0.000 | 15 |
| 0.2–0.3 | 0.274 | 0.258 | 124 |
| 0.3–0.4 | 0.371 | 0.462 | 3,800 |
| 0.4–0.5 | 0.462 | 0.442 | 37,100 |
| 0.5–0.6 | 0.540 | 0.497 | 49,680 |
| 0.6–0.7 | 0.643 | 0.494 | 5,626 |
| 0.7–0.8 | 0.732 | 0.396 | 601 |
| 0.8–0.9 | 0.816 | 0.150 | 20 |
