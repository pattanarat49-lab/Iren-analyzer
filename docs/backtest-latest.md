# IREN probability backtest (alpaca data)

Generated 2026-10-20T22:55:52+00:00 · data 2024-10-21T12:56:00+00:00 → 2026-10-20T20:00:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.513 | 0.518 | 0.2491 | 0.2497 | [-0.00095, -0.00030] | 0.513 | 250 | ⚠️ **no proven edge** |
| 15m | logreg | 0.501 | 0.516 | 0.2501 | 0.2498 | [-0.00009, +0.00068] | 0.499 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.492 | 0.518 | 0.2501 | 0.2499 | [-0.00029, +0.00078] | 0.492 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.513 | 0.483 | 0.2509 | 0.2510 | [-0.00377, +0.00365] | 0.531 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,893 over 250 days; share of "up": 0.482
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.513 | 0.2491 | 0.6911 | 0.513 | 0.0026 | 0.017 | 0.666 | 0.61 |
| lgbm | 0.515 | 0.2491 | 0.6911 | 0.513 | 0.0026 | 0.040 | 0.569 | 0.50 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.097 | 0.000 | 2 |
| 0.1–0.2 | 0.167 | 0.079 | 140 |
| 0.2–0.3 | 0.247 | 0.219 | 465 |
| 0.3–0.4 | 0.347 | 0.251 | 287 |
| 0.4–0.5 | 0.481 | 0.480 | 60,776 |
| 0.5–0.6 | 0.512 | 0.493 | 35,222 |
| 0.6–0.7 | 0.622 | 1.000 | 1 |

## 15m (15 นาที)

- Test rows: 96,883 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.501 | 0.2501 | 0.6933 | 0.499 | -0.0010 | 0.018 | 0.536 | -0.31 |
| lgbm | 0.499 | 0.2501 | 0.6933 | 0.494 | -0.0011 | 0.031 | 0.556 | -1.41 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.185 | 0.233 | 30 |
| 0.2–0.3 | 0.260 | 0.385 | 260 |
| 0.3–0.4 | 0.356 | 0.271 | 266 |
| 0.4–0.5 | 0.484 | 0.488 | 59,035 |
| 0.5–0.6 | 0.510 | 0.481 | 37,292 |

## 1h (1 ชั่วโมง)

- Test rows: 96,838 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.492 | 0.2501 | 0.6934 | 0.492 | -0.0010 | 0.012 | 0.539 | -0.33 |
| lgbm | 0.501 | 0.2503 | 0.6937 | 0.493 | -0.0016 | 0.026 | 0.583 | -0.11 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.273 | 0.440 | 25 |
| 0.3–0.4 | 0.375 | 0.346 | 156 |
| 0.4–0.5 | 0.487 | 0.493 | 61,316 |
| 0.5–0.6 | 0.509 | 0.465 | 35,341 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,896 over 250 days; share of "up": 0.467
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.483 | 0.2510 | 0.6951 | – | – | – | – | – |
| logreg | 0.513 | 0.2509 | 0.6952 | 0.531 | 0.0005 | 0.276 | 0.548 | 10.89 |
| lgbm | 0.470 | 0.2548 | 0.7029 | 0.462 | -0.0153 | 0.187 | 0.455 | -20.46 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.184 | 0.000 | 16 |
| 0.2–0.3 | 0.273 | 0.375 | 216 |
| 0.3–0.4 | 0.370 | 0.417 | 4,996 |
| 0.4–0.5 | 0.466 | 0.433 | 26,389 |
| 0.5–0.6 | 0.526 | 0.482 | 61,110 |
| 0.6–0.7 | 0.639 | 0.542 | 3,208 |
| 0.7–0.8 | 0.730 | 0.512 | 882 |
| 0.8–0.9 | 0.825 | 0.304 | 79 |
