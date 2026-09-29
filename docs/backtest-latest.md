# IREN probability backtest (alpaca data)

Generated 2026-09-29T22:39:22+00:00 · data 2024-09-30T13:30:00+00:00 → 2026-09-29T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.519 | 0.515 | 0.2489 | 0.2499 | [-0.00131, -0.00066] | 0.519 | 250 | ✅ edge |
| 15m | lgbm | 0.507 | 0.513 | 0.2497 | 0.2498 | [-0.00054, +0.00022] | 0.506 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.498 | 0.514 | 0.2502 | 0.2499 | [-0.00022, +0.00091] | 0.494 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.515 | 0.469 | 0.2501 | 0.2509 | [-0.00459, +0.00304] | 0.550 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,955 over 250 days; share of "up": 0.485
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.515 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.519 | 0.2489 | 0.6908 | 0.519 | 0.0040 | 0.024 | 0.635 | 1.31 |
| lgbm | 0.515 | 0.2489 | 0.6908 | 0.517 | 0.0039 | 0.050 | 0.579 | 0.93 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.096 | 0.000 | 2 |
| 0.1–0.2 | 0.165 | 0.168 | 268 |
| 0.2–0.3 | 0.253 | 0.109 | 357 |
| 0.3–0.4 | 0.361 | 0.330 | 221 |
| 0.4–0.5 | 0.484 | 0.479 | 67,318 |
| 0.5–0.6 | 0.514 | 0.508 | 28,697 |
| 0.6–0.7 | 0.653 | 0.511 | 92 |

## 15m (15 นาที)

- Test rows: 96,945 over 250 days; share of "up": 0.487
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.513 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.508 | 0.2497 | 0.6926 | 0.511 | 0.0006 | 0.023 | 0.573 | 0.26 |
| lgbm | 0.507 | 0.2497 | 0.6925 | 0.506 | 0.0007 | 0.028 | 0.579 | 0.21 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.265 | 0.163 | 245 |
| 0.3–0.4 | 0.363 | 0.280 | 447 |
| 0.4–0.5 | 0.488 | 0.486 | 57,662 |
| 0.5–0.6 | 0.513 | 0.493 | 38,569 |
| 0.6–0.7 | 0.606 | 0.545 | 22 |

## 1h (1 ชั่วโมง)

- Test rows: 96,901 over 250 days; share of "up": 0.486
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.502 | 0.2504 | 0.6939 | 0.498 | -0.0019 | 0.067 | 0.490 | 1.60 |
| lgbm | 0.498 | 0.2502 | 0.6936 | 0.494 | -0.0014 | 0.023 | 0.530 | -0.86 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.378 | 0.252 | 206 |
| 0.4–0.5 | 0.486 | 0.491 | 58,422 |
| 0.5–0.6 | 0.510 | 0.479 | 38,213 |
| 0.6–0.7 | 0.604 | 0.583 | 60 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,959 over 250 days; share of "up": 0.469
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.469 | 0.2509 | 0.6950 | – | – | – | – | – |
| logreg | 0.515 | 0.2501 | 0.6935 | 0.550 | 0.0031 | 0.330 | 0.552 | 6.08 |
| lgbm | 0.478 | 0.2519 | 0.6970 | 0.499 | -0.0039 | 0.109 | 0.534 | -21.14 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.153 | 0.000 | 21 |
| 0.2–0.3 | 0.274 | 0.457 | 324 |
| 0.3–0.4 | 0.374 | 0.411 | 4,571 |
| 0.4–0.5 | 0.459 | 0.410 | 20,377 |
| 0.5–0.6 | 0.530 | 0.482 | 64,842 |
| 0.6–0.7 | 0.636 | 0.559 | 6,484 |
| 0.7–0.8 | 0.730 | 0.550 | 340 |
