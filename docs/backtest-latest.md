# IREN probability backtest (alpaca data)

Generated 2026-09-28T22:37:43+00:00 · data 2024-09-30T13:30:00+00:00 → 2026-09-28T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.515 | 0.515 | 0.2489 | 0.2499 | [-0.00134, -0.00062] | 0.517 | 249 | ✅ edge |
| 15m | lgbm | 0.507 | 0.512 | 0.2497 | 0.2499 | [-0.00054, +0.00022] | 0.506 | 249 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.498 | 0.514 | 0.2502 | 0.2499 | [-0.00018, +0.00088] | 0.495 | 249 | ⚠️ **no proven edge** |
| eod | logreg | 0.516 | 0.469 | 0.2501 | 0.2509 | [-0.00468, +0.00310] | 0.551 | 249 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,566 over 249 days; share of "up": 0.485
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.515 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.519 | 0.2489 | 0.6908 | 0.519 | 0.0040 | 0.024 | 0.634 | 1.32 |
| lgbm | 0.515 | 0.2489 | 0.6908 | 0.517 | 0.0040 | 0.049 | 0.581 | 0.94 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.189 | 0.069 | 144 |
| 0.2–0.3 | 0.239 | 0.157 | 574 |
| 0.3–0.4 | 0.347 | 0.284 | 67 |
| 0.4–0.5 | 0.482 | 0.483 | 68,050 |
| 0.5–0.6 | 0.518 | 0.501 | 27,695 |
| 0.6–0.7 | 0.609 | 0.500 | 36 |

## 15m (15 นาที)

- Test rows: 96,556 over 249 days; share of "up": 0.488
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.512 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.508 | 0.2497 | 0.6925 | 0.511 | 0.0006 | 0.023 | 0.573 | 0.31 |
| lgbm | 0.507 | 0.2497 | 0.6925 | 0.506 | 0.0007 | 0.028 | 0.579 | 0.20 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.265 | 0.165 | 243 |
| 0.3–0.4 | 0.363 | 0.280 | 447 |
| 0.4–0.5 | 0.488 | 0.487 | 57,336 |
| 0.5–0.6 | 0.513 | 0.493 | 38,508 |
| 0.6–0.7 | 0.606 | 0.545 | 22 |

## 1h (1 ชั่วโมง)

- Test rows: 96,511 over 249 days; share of "up": 0.486
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.502 | 0.2504 | 0.6939 | 0.498 | -0.0018 | 0.067 | 0.490 | 1.76 |
| lgbm | 0.498 | 0.2502 | 0.6936 | 0.495 | -0.0014 | 0.024 | 0.530 | -0.89 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.378 | 0.255 | 204 |
| 0.4–0.5 | 0.486 | 0.492 | 58,090 |
| 0.5–0.6 | 0.510 | 0.480 | 38,157 |
| 0.6–0.7 | 0.604 | 0.583 | 60 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,570 over 249 days; share of "up": 0.469
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.469 | 0.2509 | 0.6950 | – | – | – | – | – |
| logreg | 0.516 | 0.2501 | 0.6934 | 0.551 | 0.0034 | 0.330 | 0.554 | 6.37 |
| lgbm | 0.479 | 0.2519 | 0.6970 | 0.500 | -0.0038 | 0.109 | 0.534 | -21.10 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.153 | 0.000 | 21 |
| 0.2–0.3 | 0.274 | 0.457 | 324 |
| 0.3–0.4 | 0.374 | 0.411 | 4,571 |
| 0.4–0.5 | 0.459 | 0.410 | 20,477 |
| 0.5–0.6 | 0.530 | 0.482 | 64,353 |
| 0.6–0.7 | 0.636 | 0.559 | 6,483 |
| 0.7–0.8 | 0.730 | 0.548 | 341 |
