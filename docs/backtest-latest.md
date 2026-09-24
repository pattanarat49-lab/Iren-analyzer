# IREN probability backtest (alpaca data)

Generated 2026-09-24T22:36:23+00:00 · data 2024-09-24T13:15:00+00:00 → 2026-09-24T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.514 | 0.514 | 0.2490 | 0.2500 | [-0.00127, -0.00063] | 0.515 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.511 | 0.511 | 0.2497 | 0.2499 | [-0.00055, +0.00018] | 0.508 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.507 | 0.512 | 0.2499 | 0.2499 | [-0.00053, +0.00063] | 0.511 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.531 | 0.443 | 0.2496 | 0.2506 | [-0.00461, +0.00290] | 0.558 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,955 over 250 days; share of "up": 0.486
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2500 | 0.6931 | – | – | – | – | – |
| logreg | 0.517 | 0.2491 | 0.6912 | 0.516 | 0.0035 | 0.021 | 0.656 | 1.01 |
| lgbm | 0.514 | 0.2490 | 0.6910 | 0.515 | 0.0039 | 0.030 | 0.612 | 0.52 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.192 | 0.031 | 127 |
| 0.2–0.3 | 0.249 | 0.160 | 561 |
| 0.3–0.4 | 0.368 | 0.346 | 211 |
| 0.4–0.5 | 0.481 | 0.484 | 66,409 |
| 0.5–0.6 | 0.512 | 0.500 | 29,647 |

## 15m (15 นาที)

- Test rows: 96,945 over 250 days; share of "up": 0.489
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.511 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.513 | 0.2497 | 0.6926 | 0.511 | 0.0007 | 0.021 | 0.570 | 1.58 |
| lgbm | 0.511 | 0.2497 | 0.6924 | 0.508 | 0.0009 | 0.026 | 0.574 | 0.44 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.270 | 0.152 | 231 |
| 0.3–0.4 | 0.354 | 0.257 | 525 |
| 0.4–0.5 | 0.486 | 0.486 | 61,147 |
| 0.5–0.6 | 0.512 | 0.499 | 35,021 |
| 0.6–0.7 | 0.603 | 0.857 | 21 |

## 1h (1 ชั่วโมง)

- Test rows: 96,900 over 250 days; share of "up": 0.488
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.512 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.507 | 0.2499 | 0.6930 | 0.511 | -0.0002 | 0.045 | 0.540 | 4.66 |
| lgbm | 0.502 | 0.2502 | 0.6935 | 0.496 | -0.0010 | 0.026 | 0.535 | 0.26 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.289 | 0.273 | 11 |
| 0.3–0.4 | 0.375 | 0.350 | 297 |
| 0.4–0.5 | 0.487 | 0.488 | 73,974 |
| 0.5–0.6 | 0.515 | 0.489 | 22,618 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,959 over 250 days; share of "up": 0.474
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.443 | 0.2506 | 0.6944 | – | – | – | – | – |
| logreg | 0.531 | 0.2496 | 0.6926 | 0.558 | 0.0039 | 0.274 | 0.573 | 14.42 |
| lgbm | 0.503 | 0.2503 | 0.6937 | 0.521 | 0.0014 | 0.143 | 0.554 | -2.91 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.164 | 0.000 | 25 |
| 0.2–0.3 | 0.274 | 0.460 | 322 |
| 0.3–0.4 | 0.370 | 0.413 | 4,450 |
| 0.4–0.5 | 0.468 | 0.402 | 23,858 |
| 0.5–0.6 | 0.527 | 0.500 | 60,979 |
| 0.6–0.7 | 0.631 | 0.532 | 6,960 |
| 0.7–0.8 | 0.725 | 0.464 | 364 |
| 0.8–0.9 | 0.813 | 1.000 | 1 |
