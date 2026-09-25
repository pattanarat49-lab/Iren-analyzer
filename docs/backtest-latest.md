# IREN probability backtest (alpaca data)

Generated 2026-09-25T22:36:41+00:00 · data 2024-09-25T13:30:00+00:00 → 2026-09-25T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.519 | 0.514 | 0.2489 | 0.2500 | [-0.00137, -0.00071] | 0.519 | 250 | ✅ edge |
| 15m | logreg | 0.514 | 0.511 | 0.2497 | 0.2499 | [-0.00057, +0.00008] | 0.512 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.499 | 0.512 | 0.2501 | 0.2499 | [-0.00033, +0.00077] | 0.493 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.524 | 0.468 | 0.2492 | 0.2506 | [-0.00483, +0.00202] | 0.553 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,951 over 250 days; share of "up": 0.486
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2500 | 0.6931 | – | – | – | – | – |
| logreg | 0.519 | 0.2489 | 0.6908 | 0.519 | 0.0042 | 0.023 | 0.645 | 1.36 |
| lgbm | 0.514 | 0.2489 | 0.6908 | 0.517 | 0.0041 | 0.035 | 0.605 | 0.70 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.099 | 0.000 | 2 |
| 0.1–0.2 | 0.162 | 0.162 | 290 |
| 0.2–0.3 | 0.240 | 0.125 | 360 |
| 0.3–0.4 | 0.369 | 0.390 | 290 |
| 0.4–0.5 | 0.483 | 0.482 | 70,937 |
| 0.5–0.6 | 0.513 | 0.509 | 25,065 |
| 0.6–0.7 | 0.611 | 0.571 | 7 |

## 15m (15 นาที)

- Test rows: 96,941 over 250 days; share of "up": 0.489
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.511 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.514 | 0.2497 | 0.6924 | 0.512 | 0.0010 | 0.018 | 0.583 | 1.66 |
| lgbm | 0.506 | 0.2497 | 0.6926 | 0.507 | 0.0007 | 0.037 | 0.564 | -0.40 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.177 | 0.208 | 24 |
| 0.2–0.3 | 0.252 | 0.294 | 194 |
| 0.3–0.4 | 0.361 | 0.292 | 397 |
| 0.4–0.5 | 0.489 | 0.484 | 68,444 |
| 0.5–0.6 | 0.508 | 0.506 | 27,746 |
| 0.6–0.7 | 0.612 | 0.390 | 136 |

## 1h (1 ชั่วโมง)

- Test rows: 96,896 over 250 days; share of "up": 0.488
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.512 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.505 | 0.2502 | 0.6935 | 0.499 | -0.0012 | 0.031 | 0.531 | 3.57 |
| lgbm | 0.499 | 0.2501 | 0.6933 | 0.493 | -0.0008 | 0.018 | 0.604 | 0.05 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.382 | 0.208 | 197 |
| 0.4–0.5 | 0.488 | 0.494 | 71,661 |
| 0.5–0.6 | 0.510 | 0.473 | 24,747 |
| 0.6–0.7 | 0.669 | 0.612 | 291 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,955 over 250 days; share of "up": 0.474
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.468 | 0.2506 | 0.6944 | – | – | – | – | – |
| logreg | 0.524 | 0.2492 | 0.6917 | 0.553 | 0.0054 | 0.305 | 0.567 | 12.27 |
| lgbm | 0.499 | 0.2501 | 0.6934 | 0.520 | 0.0019 | 0.137 | 0.593 | -7.85 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.182 | 0.000 | 11 |
| 0.2–0.3 | 0.271 | 0.589 | 146 |
| 0.3–0.4 | 0.380 | 0.410 | 4,050 |
| 0.4–0.5 | 0.461 | 0.411 | 23,745 |
| 0.5–0.6 | 0.529 | 0.495 | 63,690 |
| 0.6–0.7 | 0.629 | 0.545 | 5,222 |
| 0.7–0.8 | 0.719 | 0.560 | 91 |
