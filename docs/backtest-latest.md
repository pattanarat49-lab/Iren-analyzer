# IREN probability backtest (alpaca data)

Generated 2026-11-27T04:24:27+00:00 · data 2024-11-26T16:25:00+00:00 → 2026-11-25T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.519 | 0.520 | 0.2488 | 0.2496 | [-0.00109, -0.00049] | 0.516 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.518 | 0.518 | 0.2495 | 0.2497 | [-0.00064, +0.00015] | 0.514 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.512 | 0.519 | 0.2498 | 0.2498 | [-0.00026, +0.00022] | 0.508 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.517 | 0.487 | 0.2496 | 0.2503 | [-0.00323, +0.00198] | 0.544 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,955 over 250 days; share of "up": 0.480
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.520 | 0.2496 | 0.6924 | – | – | – | – | – |
| logreg | 0.522 | 0.2488 | 0.6907 | 0.518 | 0.0031 | 0.022 | 0.637 | 1.20 |
| lgbm | 0.519 | 0.2488 | 0.6906 | 0.516 | 0.0032 | 0.040 | 0.591 | 0.93 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.182 | 0.045 | 134 |
| 0.2–0.3 | 0.241 | 0.161 | 614 |
| 0.3–0.4 | 0.374 | 0.475 | 118 |
| 0.4–0.5 | 0.479 | 0.477 | 70,330 |
| 0.5–0.6 | 0.513 | 0.497 | 25,736 |
| 0.6–0.7 | 0.608 | 0.478 | 23 |

## 15m (15 นาที)

- Test rows: 96,945 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.518 | 0.2496 | 0.6922 | 0.513 | 0.0007 | 0.024 | 0.583 | 1.46 |
| lgbm | 0.518 | 0.2495 | 0.6920 | 0.514 | 0.0010 | 0.028 | 0.581 | 1.19 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.292 | 0.135 | 89 |
| 0.3–0.4 | 0.357 | 0.329 | 912 |
| 0.4–0.5 | 0.483 | 0.477 | 65,954 |
| 0.5–0.6 | 0.511 | 0.499 | 29,978 |
| 0.6–0.7 | 0.615 | 1.000 | 12 |

## 1h (1 ชั่วโมง)

- Test rows: 96,900 over 250 days; share of "up": 0.481
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.512 | 0.2498 | 0.6927 | 0.508 | 0.0001 | 0.004 | 0.596 | 4.65 |
| lgbm | 0.513 | 0.2500 | 0.6931 | 0.498 | -0.0009 | 0.028 | 0.525 | 3.70 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.358 | 0.430 | 142 |
| 0.4–0.5 | 0.492 | 0.482 | 82,469 |
| 0.5–0.6 | 0.505 | 0.477 | 14,289 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,959 over 250 days; share of "up": 0.472
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.487 | 0.2503 | 0.6938 | – | – | – | – | – |
| logreg | 0.517 | 0.2496 | 0.6925 | 0.544 | 0.0027 | 0.219 | 0.548 | 12.29 |
| lgbm | 0.493 | 0.2516 | 0.6966 | 0.493 | -0.0053 | 0.174 | 0.533 | -6.26 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.191 | 0.000 | 3 |
| 0.2–0.3 | 0.228 | 0.650 | 103 |
| 0.3–0.4 | 0.382 | 0.453 | 1,121 |
| 0.4–0.5 | 0.469 | 0.443 | 37,847 |
| 0.5–0.6 | 0.526 | 0.492 | 56,082 |
| 0.6–0.7 | 0.618 | 0.462 | 1,798 |
| 0.7–0.8 | 0.703 | 0.000 | 5 |
