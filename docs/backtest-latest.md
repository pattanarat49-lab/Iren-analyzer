# IREN probability backtest (alpaca data)

Generated 2026-10-06T22:40:27+00:00 · data 2024-10-07T13:30:00+00:00 → 2026-10-06T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.518 | 0.516 | 0.2489 | 0.2498 | [-0.00120, -0.00058] | 0.517 | 250 | ✅ edge |
| 15m | lgbm | 0.502 | 0.515 | 0.2498 | 0.2498 | [-0.00038, +0.00032] | 0.501 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.500 | 0.516 | 0.2504 | 0.2499 | [-0.00020, +0.00117] | 0.496 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.523 | 0.485 | 0.2498 | 0.2513 | [-0.00525, +0.00229] | 0.547 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,966 over 250 days; share of "up": 0.484
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.518 | 0.2489 | 0.6908 | 0.517 | 0.0036 | 0.024 | 0.640 | 1.15 |
| lgbm | 0.515 | 0.2489 | 0.6908 | 0.516 | 0.0035 | 0.034 | 0.601 | 0.58 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.096 | 0.083 | 12 |
| 0.1–0.2 | 0.162 | 0.169 | 296 |
| 0.2–0.3 | 0.247 | 0.108 | 342 |
| 0.3–0.4 | 0.364 | 0.332 | 199 |
| 0.4–0.5 | 0.483 | 0.479 | 67,408 |
| 0.5–0.6 | 0.514 | 0.503 | 28,608 |
| 0.6–0.7 | 0.614 | 0.515 | 101 |

## 15m (15 นาที)

- Test rows: 96,956 over 250 days; share of "up": 0.485
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.515 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.508 | 0.2499 | 0.6929 | 0.504 | -0.0002 | 0.026 | 0.537 | 0.32 |
| lgbm | 0.502 | 0.2498 | 0.6927 | 0.501 | 0.0001 | 0.021 | 0.605 | -0.95 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.262 | 0.105 | 210 |
| 0.3–0.4 | 0.360 | 0.246 | 350 |
| 0.4–0.5 | 0.486 | 0.490 | 68,903 |
| 0.5–0.6 | 0.516 | 0.478 | 27,490 |
| 0.6–0.7 | 0.603 | 1.000 | 3 |

## 1h (1 ชั่วโมง)

- Test rows: 96,911 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.498 | 0.2505 | 0.6941 | 0.496 | -0.0022 | 0.057 | 0.494 | -0.11 |
| lgbm | 0.500 | 0.2504 | 0.6939 | 0.496 | -0.0019 | 0.025 | 0.502 | 0.18 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.394 | 0.519 | 890 |
| 0.4–0.5 | 0.489 | 0.489 | 72,760 |
| 0.5–0.6 | 0.517 | 0.468 | 23,261 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,970 over 250 days; share of "up": 0.466
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.485 | 0.2513 | 0.6958 | – | – | – | – | – |
| logreg | 0.523 | 0.2498 | 0.6930 | 0.547 | 0.0059 | 0.324 | 0.549 | 13.17 |
| lgbm | 0.463 | 0.2542 | 0.7016 | 0.467 | -0.0114 | 0.158 | 0.503 | -22.80 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.190 | 0.000 | 13 |
| 0.2–0.3 | 0.257 | 0.633 | 150 |
| 0.3–0.4 | 0.374 | 0.408 | 2,719 |
| 0.4–0.5 | 0.458 | 0.408 | 27,163 |
| 0.5–0.6 | 0.532 | 0.487 | 62,189 |
| 0.6–0.7 | 0.642 | 0.552 | 4,114 |
| 0.7–0.8 | 0.736 | 0.590 | 592 |
| 0.8–0.9 | 0.826 | 0.567 | 30 |
