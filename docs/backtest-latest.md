# IREN probability backtest (alpaca data)

Generated 2026-10-08T22:41:58+00:00 · data 2024-10-08T13:30:00+00:00 → 2026-10-08T20:00:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.517 | 0.517 | 0.2489 | 0.2497 | [-0.00120, -0.00050] | 0.517 | 250 | ✅ edge |
| 15m | lgbm | 0.505 | 0.516 | 0.2498 | 0.2498 | [-0.00034, +0.00045] | 0.500 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.501 | 0.517 | 0.2506 | 0.2499 | [-0.00021, +0.00173] | 0.494 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.517 | 0.481 | 0.2507 | 0.2514 | [-0.00441, +0.00332] | 0.539 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,967 over 250 days; share of "up": 0.483
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.517 | 0.2489 | 0.6908 | 0.517 | 0.0034 | 0.026 | 0.633 | 1.01 |
| lgbm | 0.514 | 0.2489 | 0.6908 | 0.517 | 0.0033 | 0.048 | 0.584 | 0.53 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.096 | 0.091 | 11 |
| 0.1–0.2 | 0.165 | 0.152 | 315 |
| 0.2–0.3 | 0.249 | 0.116 | 329 |
| 0.3–0.4 | 0.358 | 0.348 | 201 |
| 0.4–0.5 | 0.483 | 0.479 | 67,066 |
| 0.5–0.6 | 0.516 | 0.500 | 28,952 |
| 0.6–0.7 | 0.622 | 0.516 | 93 |

## 15m (15 นาที)

- Test rows: 96,957 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.507 | 0.2499 | 0.6930 | 0.505 | -0.0005 | 0.025 | 0.543 | 0.20 |
| lgbm | 0.505 | 0.2498 | 0.6928 | 0.500 | -0.0002 | 0.028 | 0.582 | -0.92 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.274 | 0.128 | 179 |
| 0.3–0.4 | 0.360 | 0.288 | 708 |
| 0.4–0.5 | 0.485 | 0.488 | 65,024 |
| 0.5–0.6 | 0.516 | 0.483 | 31,040 |
| 0.6–0.7 | 0.608 | 0.333 | 6 |

## 1h (1 ชั่วโมง)

- Test rows: 96,912 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.501 | 0.2506 | 0.6944 | 0.494 | -0.0030 | 0.077 | 0.494 | 1.44 |
| lgbm | 0.496 | 0.2507 | 0.6946 | 0.492 | -0.0033 | 0.037 | 0.525 | -1.48 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.166 | 0.423 | 26 |
| 0.2–0.3 | 0.268 | 0.336 | 119 |
| 0.3–0.4 | 0.368 | 0.361 | 327 |
| 0.4–0.5 | 0.484 | 0.488 | 66,684 |
| 0.5–0.6 | 0.521 | 0.474 | 29,606 |
| 0.6–0.7 | 0.625 | 0.525 | 139 |
| 0.7–0.8 | 0.712 | 0.000 | 11 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,970 over 250 days; share of "up": 0.463
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.481 | 0.2514 | 0.6960 | – | – | – | – | – |
| logreg | 0.517 | 0.2507 | 0.6948 | 0.539 | 0.0029 | 0.310 | 0.548 | 10.08 |
| lgbm | 0.467 | 0.2543 | 0.7018 | 0.468 | -0.0112 | 0.197 | 0.476 | -19.97 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.187 | 0.000 | 13 |
| 0.2–0.3 | 0.254 | 0.576 | 172 |
| 0.3–0.4 | 0.377 | 0.387 | 4,698 |
| 0.4–0.5 | 0.460 | 0.414 | 24,473 |
| 0.5–0.6 | 0.533 | 0.482 | 62,292 |
| 0.6–0.7 | 0.649 | 0.527 | 4,251 |
| 0.7–0.8 | 0.728 | 0.563 | 1,045 |
| 0.8–0.9 | 0.824 | 0.577 | 26 |
