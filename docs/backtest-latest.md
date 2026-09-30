# IREN probability backtest (alpaca data)

Generated 2026-09-30T22:39:44+00:00 · data 2024-09-30T13:30:00+00:00 → 2026-09-30T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.515 | 0.515 | 0.2489 | 0.2499 | [-0.00134, -0.00065] | 0.518 | 250 | ✅ edge |
| 15m | lgbm | 0.505 | 0.514 | 0.2497 | 0.2498 | [-0.00048, +0.00023] | 0.505 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.502 | 0.514 | 0.2499 | 0.2499 | [-0.00050, +0.00044] | 0.498 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.517 | 0.467 | 0.2497 | 0.2510 | [-0.00485, +0.00249] | 0.555 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,949 over 250 days; share of "up": 0.485
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.515 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.519 | 0.2489 | 0.6908 | 0.519 | 0.0039 | 0.024 | 0.633 | 1.37 |
| lgbm | 0.515 | 0.2489 | 0.6907 | 0.518 | 0.0041 | 0.038 | 0.598 | 0.85 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.193 | 0.087 | 218 |
| 0.2–0.3 | 0.246 | 0.164 | 519 |
| 0.3–0.4 | 0.362 | 0.310 | 58 |
| 0.4–0.5 | 0.481 | 0.482 | 64,739 |
| 0.5–0.6 | 0.516 | 0.501 | 31,406 |
| 0.6–0.7 | 0.606 | 0.333 | 9 |

## 15m (15 นาที)

- Test rows: 96,939 over 250 days; share of "up": 0.486
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.507 | 0.2497 | 0.6926 | 0.511 | 0.0004 | 0.026 | 0.556 | 0.35 |
| lgbm | 0.505 | 0.2497 | 0.6925 | 0.505 | 0.0005 | 0.021 | 0.614 | -0.41 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.266 | 0.136 | 213 |
| 0.3–0.4 | 0.367 | 0.272 | 536 |
| 0.4–0.5 | 0.488 | 0.488 | 57,153 |
| 0.5–0.6 | 0.513 | 0.489 | 39,025 |
| 0.6–0.7 | 0.609 | 1.000 | 12 |

## 1h (1 ชั่วโมง)

- Test rows: 96,894 over 250 days; share of "up": 0.486
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.501 | 0.2504 | 0.6940 | 0.495 | -0.0022 | 0.083 | 0.500 | 1.86 |
| lgbm | 0.502 | 0.2499 | 0.6929 | 0.498 | 0.0000 | 0.015 | 0.619 | 2.02 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.294 | 0.286 | 7 |
| 0.3–0.4 | 0.357 | 0.235 | 213 |
| 0.4–0.5 | 0.489 | 0.489 | 63,241 |
| 0.5–0.6 | 0.510 | 0.482 | 33,433 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,953 over 250 days; share of "up": 0.466
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.467 | 0.2510 | 0.6951 | – | – | – | – | – |
| logreg | 0.517 | 0.2497 | 0.6927 | 0.555 | 0.0050 | 0.311 | 0.550 | 6.63 |
| lgbm | 0.482 | 0.2512 | 0.6956 | 0.509 | -0.0010 | 0.122 | 0.524 | -18.81 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.179 | 0.000 | 15 |
| 0.2–0.3 | 0.275 | 0.444 | 288 |
| 0.3–0.4 | 0.373 | 0.424 | 3,975 |
| 0.4–0.5 | 0.461 | 0.406 | 22,916 |
| 0.5–0.6 | 0.531 | 0.483 | 64,755 |
| 0.6–0.7 | 0.637 | 0.556 | 4,712 |
| 0.7–0.8 | 0.725 | 0.589 | 292 |
