# IREN probability backtest (alpaca data)

Generated 2026-10-15T22:53:17+00:00 · data 2024-10-15T13:30:00+00:00 → 2026-10-15T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.513 | 0.518 | 0.2490 | 0.2497 | [-0.00102, -0.00039] | 0.513 | 250 | ⚠️ **no proven edge** |
| 15m | logreg | 0.503 | 0.515 | 0.2500 | 0.2498 | [-0.00020, +0.00054] | 0.500 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.495 | 0.516 | 0.2502 | 0.2499 | [-0.00042, +0.00094] | 0.500 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.514 | 0.484 | 0.2510 | 0.2509 | [-0.00398, +0.00410] | 0.534 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,890 over 250 days; share of "up": 0.482
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.513 | 0.2490 | 0.6910 | 0.513 | 0.0029 | 0.023 | 0.638 | 0.46 |
| lgbm | 0.515 | 0.2491 | 0.6911 | 0.514 | 0.0026 | 0.045 | 0.557 | 0.58 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.099 | 0.000 | 2 |
| 0.1–0.2 | 0.164 | 0.095 | 158 |
| 0.2–0.3 | 0.230 | 0.150 | 380 |
| 0.3–0.4 | 0.347 | 0.275 | 302 |
| 0.4–0.5 | 0.482 | 0.480 | 62,259 |
| 0.5–0.6 | 0.512 | 0.493 | 33,787 |
| 0.6–0.7 | 0.616 | 0.500 | 2 |

## 15m (15 นาที)

- Test rows: 96,880 over 250 days; share of "up": 0.485
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.515 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.503 | 0.2500 | 0.6931 | 0.500 | -0.0007 | 0.026 | 0.549 | -0.88 |
| lgbm | 0.508 | 0.2501 | 0.6933 | 0.497 | -0.0012 | 0.058 | 0.520 | -0.57 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.177 | 0.179 | 39 |
| 0.2–0.3 | 0.246 | 0.258 | 198 |
| 0.3–0.4 | 0.360 | 0.372 | 513 |
| 0.4–0.5 | 0.483 | 0.487 | 57,436 |
| 0.5–0.6 | 0.509 | 0.485 | 38,438 |
| 0.6–0.7 | 0.609 | 0.457 | 256 |

## 1h (1 ชั่วโมง)

- Test rows: 96,835 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.495 | 0.2502 | 0.6935 | 0.500 | -0.0010 | 0.065 | 0.525 | 0.79 |
| lgbm | 0.506 | 0.2503 | 0.6937 | 0.505 | -0.0015 | 0.042 | 0.486 | 1.90 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.263 | 0.339 | 56 |
| 0.3–0.4 | 0.369 | 0.326 | 377 |
| 0.4–0.5 | 0.485 | 0.493 | 59,331 |
| 0.5–0.6 | 0.515 | 0.473 | 37,054 |
| 0.6–0.7 | 0.609 | 0.706 | 17 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,894 over 250 days; share of "up": 0.471
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.484 | 0.2509 | 0.6950 | – | – | – | – | – |
| logreg | 0.514 | 0.2510 | 0.6953 | 0.534 | -0.0001 | 0.352 | 0.534 | 9.67 |
| lgbm | 0.481 | 0.2532 | 0.6996 | 0.482 | -0.0089 | 0.128 | 0.489 | -16.62 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.185 | 0.000 | 14 |
| 0.2–0.3 | 0.271 | 0.291 | 251 |
| 0.3–0.4 | 0.366 | 0.392 | 4,862 |
| 0.4–0.5 | 0.461 | 0.445 | 27,159 |
| 0.5–0.6 | 0.531 | 0.484 | 58,137 |
| 0.6–0.7 | 0.638 | 0.533 | 5,815 |
| 0.7–0.8 | 0.732 | 0.532 | 624 |
| 0.8–0.9 | 0.827 | 0.531 | 32 |
