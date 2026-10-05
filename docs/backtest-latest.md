# IREN probability backtest (alpaca data)

Generated 2026-10-05T22:39:16+00:00 · data 2024-10-07T13:30:00+00:00 → 2026-10-05T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.518 | 0.516 | 0.2489 | 0.2498 | [-0.00120, -0.00057] | 0.517 | 249 | ✅ edge |
| 15m | lgbm | 0.503 | 0.515 | 0.2498 | 0.2498 | [-0.00037, +0.00032] | 0.501 | 249 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.500 | 0.516 | 0.2504 | 0.2499 | [-0.00015, +0.00123] | 0.497 | 249 | ⚠️ **no proven edge** |
| eod | logreg | 0.524 | 0.484 | 0.2497 | 0.2513 | [-0.00542, +0.00226] | 0.549 | 249 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,578 over 249 days; share of "up": 0.484
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.518 | 0.2489 | 0.6908 | 0.517 | 0.0036 | 0.024 | 0.640 | 1.15 |
| lgbm | 0.515 | 0.2489 | 0.6909 | 0.516 | 0.0035 | 0.034 | 0.600 | 0.56 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.096 | 0.083 | 12 |
| 0.1–0.2 | 0.162 | 0.169 | 296 |
| 0.2–0.3 | 0.248 | 0.109 | 341 |
| 0.3–0.4 | 0.364 | 0.332 | 199 |
| 0.4–0.5 | 0.483 | 0.479 | 67,050 |
| 0.5–0.6 | 0.514 | 0.503 | 28,579 |
| 0.6–0.7 | 0.614 | 0.515 | 101 |

## 15m (15 นาที)

- Test rows: 96,568 over 249 days; share of "up": 0.485
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.515 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.508 | 0.2499 | 0.6929 | 0.504 | -0.0002 | 0.026 | 0.537 | 0.28 |
| lgbm | 0.503 | 0.2498 | 0.6926 | 0.501 | 0.0002 | 0.021 | 0.607 | -0.88 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.262 | 0.105 | 209 |
| 0.3–0.4 | 0.360 | 0.246 | 350 |
| 0.4–0.5 | 0.486 | 0.490 | 68,666 |
| 0.5–0.6 | 0.516 | 0.479 | 27,340 |
| 0.6–0.7 | 0.603 | 1.000 | 3 |

## 1h (1 ชั่วโมง)

- Test rows: 96,523 over 249 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.498 | 0.2505 | 0.6941 | 0.496 | -0.0022 | 0.057 | 0.494 | -0.21 |
| lgbm | 0.500 | 0.2504 | 0.6939 | 0.497 | -0.0019 | 0.025 | 0.502 | 0.31 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.394 | 0.520 | 889 |
| 0.4–0.5 | 0.489 | 0.489 | 72,409 |
| 0.5–0.6 | 0.517 | 0.469 | 23,225 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,582 over 249 days; share of "up": 0.467
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.484 | 0.2513 | 0.6958 | – | – | – | – | – |
| logreg | 0.524 | 0.2497 | 0.6927 | 0.549 | 0.0064 | 0.322 | 0.552 | 13.47 |
| lgbm | 0.464 | 0.2541 | 0.7014 | 0.469 | -0.0109 | 0.158 | 0.506 | -22.60 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.190 | 0.000 | 13 |
| 0.2–0.3 | 0.257 | 0.633 | 150 |
| 0.3–0.4 | 0.374 | 0.408 | 2,719 |
| 0.4–0.5 | 0.458 | 0.408 | 27,163 |
| 0.5–0.6 | 0.532 | 0.489 | 61,802 |
| 0.6–0.7 | 0.643 | 0.552 | 4,113 |
| 0.7–0.8 | 0.736 | 0.590 | 592 |
| 0.8–0.9 | 0.826 | 0.567 | 30 |
