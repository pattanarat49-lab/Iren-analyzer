# IREN probability backtest (alpaca data)

Generated 2026-11-13T02:46:02+00:00 · data 2024-11-12T14:46:00+00:00 → 2026-11-12T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.519 | 0.519 | 0.2488 | 0.2497 | [-0.00112, -0.00048] | 0.516 | 250 | ✅ edge |
| 15m | lgbm | 0.515 | 0.517 | 0.2494 | 0.2497 | [-0.00070, +0.00013] | 0.512 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.508 | 0.518 | 0.2499 | 0.2498 | [-0.00064, +0.00078] | 0.505 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.521 | 0.482 | 0.2489 | 0.2501 | [-0.00376, +0.00141] | 0.544 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,940 over 250 days; share of "up": 0.481
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.520 | 0.2489 | 0.6908 | 0.516 | 0.0031 | 0.034 | 0.608 | 1.09 |
| lgbm | 0.519 | 0.2488 | 0.6906 | 0.516 | 0.0033 | 0.042 | 0.580 | 1.08 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.185 | 0.076 | 158 |
| 0.2–0.3 | 0.240 | 0.134 | 567 |
| 0.3–0.4 | 0.367 | 0.386 | 114 |
| 0.4–0.5 | 0.480 | 0.478 | 70,885 |
| 0.5–0.6 | 0.514 | 0.500 | 25,214 |
| 0.6–0.7 | 0.606 | 1.000 | 2 |

## 15m (15 นาที)

- Test rows: 96,930 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.518 | 0.2495 | 0.6921 | 0.510 | 0.0010 | 0.028 | 0.564 | 1.49 |
| lgbm | 0.515 | 0.2494 | 0.6920 | 0.512 | 0.0013 | 0.039 | 0.564 | 0.79 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.288 | 0.140 | 200 |
| 0.3–0.4 | 0.343 | 0.336 | 889 |
| 0.4–0.5 | 0.484 | 0.481 | 70,109 |
| 0.5–0.6 | 0.515 | 0.495 | 25,729 |
| 0.6–0.7 | 0.603 | 1.000 | 3 |

## 1h (1 ชั่วโมง)

- Test rows: 96,886 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.514 | 0.2500 | 0.6932 | 0.491 | -0.0006 | 0.012 | 0.561 | 6.00 |
| lgbm | 0.508 | 0.2499 | 0.6929 | 0.505 | -0.0001 | 0.042 | 0.563 | 3.80 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.377 | 0.222 | 261 |
| 0.4–0.5 | 0.484 | 0.480 | 60,146 |
| 0.5–0.6 | 0.509 | 0.487 | 36,479 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,944 over 250 days; share of "up": 0.470
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.482 | 0.2501 | 0.6934 | – | – | – | – | – |
| logreg | 0.521 | 0.2489 | 0.6911 | 0.544 | 0.0048 | 0.199 | 0.575 | 16.77 |
| lgbm | 0.500 | 0.2506 | 0.6943 | 0.508 | -0.0017 | 0.111 | 0.521 | -3.73 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.183 | 0.000 | 13 |
| 0.2–0.3 | 0.273 | 0.414 | 58 |
| 0.3–0.4 | 0.372 | 0.528 | 1,200 |
| 0.4–0.5 | 0.473 | 0.439 | 40,238 |
| 0.5–0.6 | 0.525 | 0.489 | 53,567 |
| 0.6–0.7 | 0.627 | 0.596 | 1,626 |
| 0.7–0.8 | 0.734 | 0.456 | 237 |
| 0.8–0.9 | 0.806 | 0.000 | 5 |
