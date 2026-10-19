# IREN probability backtest (alpaca data)

Generated 2026-10-19T22:55:35+00:00 · data 2024-10-21T12:56:00+00:00 → 2026-10-19T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.513 | 0.518 | 0.2491 | 0.2497 | [-0.00095, -0.00031] | 0.513 | 249 | ⚠️ **no proven edge** |
| 15m | logreg | 0.501 | 0.516 | 0.2501 | 0.2498 | [-0.00010, +0.00066] | 0.499 | 249 | ⚠️ **no proven edge** |
| 1h | logreg | 0.492 | 0.517 | 0.2501 | 0.2499 | [-0.00028, +0.00079] | 0.492 | 249 | ⚠️ **no proven edge** |
| eod | logreg | 0.514 | 0.483 | 0.2508 | 0.2510 | [-0.00368, +0.00365] | 0.532 | 249 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,502 over 249 days; share of "up": 0.482
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.513 | 0.2491 | 0.6911 | 0.513 | 0.0026 | 0.017 | 0.667 | 0.62 |
| lgbm | 0.515 | 0.2491 | 0.6911 | 0.513 | 0.0025 | 0.040 | 0.569 | 0.51 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.097 | 0.000 | 2 |
| 0.1–0.2 | 0.167 | 0.079 | 140 |
| 0.2–0.3 | 0.247 | 0.220 | 464 |
| 0.3–0.4 | 0.347 | 0.251 | 287 |
| 0.4–0.5 | 0.481 | 0.480 | 60,428 |
| 0.5–0.6 | 0.512 | 0.493 | 35,180 |
| 0.6–0.7 | 0.622 | 1.000 | 1 |

## 15m (15 นาที)

- Test rows: 96,492 over 249 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.501 | 0.2501 | 0.6933 | 0.499 | -0.0011 | 0.018 | 0.535 | -0.24 |
| lgbm | 0.499 | 0.2501 | 0.6933 | 0.494 | -0.0011 | 0.031 | 0.555 | -1.42 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.185 | 0.233 | 30 |
| 0.2–0.3 | 0.260 | 0.386 | 259 |
| 0.3–0.4 | 0.356 | 0.271 | 266 |
| 0.4–0.5 | 0.484 | 0.488 | 58,708 |
| 0.5–0.6 | 0.509 | 0.482 | 37,229 |

## 1h (1 ชั่วโมง)

- Test rows: 96,447 over 249 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.492 | 0.2501 | 0.6934 | 0.492 | -0.0009 | 0.012 | 0.539 | -0.26 |
| lgbm | 0.500 | 0.2503 | 0.6937 | 0.494 | -0.0015 | 0.026 | 0.583 | -0.46 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.273 | 0.440 | 25 |
| 0.3–0.4 | 0.375 | 0.346 | 156 |
| 0.4–0.5 | 0.487 | 0.493 | 61,305 |
| 0.5–0.6 | 0.509 | 0.466 | 34,961 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,506 over 249 days; share of "up": 0.468
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.483 | 0.2510 | 0.6951 | – | – | – | – | – |
| logreg | 0.514 | 0.2508 | 0.6951 | 0.532 | 0.0006 | 0.277 | 0.548 | 11.12 |
| lgbm | 0.470 | 0.2548 | 0.7030 | 0.462 | -0.0153 | 0.188 | 0.455 | -20.54 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.184 | 0.000 | 16 |
| 0.2–0.3 | 0.273 | 0.375 | 216 |
| 0.3–0.4 | 0.370 | 0.417 | 4,996 |
| 0.4–0.5 | 0.466 | 0.433 | 26,389 |
| 0.5–0.6 | 0.526 | 0.483 | 60,720 |
| 0.6–0.7 | 0.639 | 0.542 | 3,208 |
| 0.7–0.8 | 0.730 | 0.512 | 882 |
| 0.8–0.9 | 0.825 | 0.304 | 79 |
