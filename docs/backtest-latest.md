# IREN probability backtest (alpaca data)

Generated 2026-10-12T22:42:11+00:00 · data 2024-10-14T13:30:00+00:00 → 2026-10-12T20:14:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.512 | 0.518 | 0.2490 | 0.2497 | [-0.00101, -0.00034] | 0.514 | 249 | ⚠️ **no proven edge** |
| 15m | logreg | 0.505 | 0.517 | 0.2501 | 0.2498 | [-0.00008, +0.00069] | 0.500 | 249 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.504 | 0.518 | 0.2503 | 0.2499 | [-0.00015, +0.00103] | 0.500 | 249 | ⚠️ **no proven edge** |
| eod | logreg | 0.510 | 0.490 | 0.2513 | 0.2512 | [-0.00360, +0.00408] | 0.535 | 249 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,575 over 249 days; share of "up": 0.482
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.512 | 0.2490 | 0.6910 | 0.514 | 0.0027 | 0.023 | 0.642 | 0.32 |
| lgbm | 0.516 | 0.2491 | 0.6911 | 0.514 | 0.0026 | 0.051 | 0.567 | 0.57 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.091 | 0.077 | 13 |
| 0.1–0.2 | 0.170 | 0.106 | 207 |
| 0.2–0.3 | 0.233 | 0.152 | 328 |
| 0.3–0.4 | 0.343 | 0.255 | 294 |
| 0.4–0.5 | 0.481 | 0.480 | 57,868 |
| 0.5–0.6 | 0.514 | 0.492 | 37,828 |
| 0.6–0.7 | 0.604 | 0.622 | 37 |

## 15m (15 นาที)

- Test rows: 96,575 over 249 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.505 | 0.2501 | 0.6933 | 0.500 | -0.0012 | 0.028 | 0.531 | -0.75 |
| lgbm | 0.501 | 0.2501 | 0.6933 | 0.498 | -0.0013 | 0.051 | 0.534 | -1.71 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.179 | 0.184 | 38 |
| 0.2–0.3 | 0.256 | 0.264 | 193 |
| 0.3–0.4 | 0.355 | 0.230 | 291 |
| 0.4–0.5 | 0.485 | 0.484 | 57,988 |
| 0.5–0.6 | 0.513 | 0.485 | 37,779 |
| 0.6–0.7 | 0.622 | 0.441 | 286 |

## 1h (1 ชั่วโมง)

- Test rows: 96,530 over 249 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.497 | 0.2503 | 0.6938 | 0.494 | -0.0018 | 0.056 | 0.525 | 1.17 |
| lgbm | 0.504 | 0.2503 | 0.6938 | 0.500 | -0.0017 | 0.033 | 0.509 | 2.34 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.383 | 0.471 | 807 |
| 0.4–0.5 | 0.489 | 0.484 | 66,561 |
| 0.5–0.6 | 0.513 | 0.477 | 28,828 |
| 0.6–0.7 | 0.608 | 0.542 | 334 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,574 over 249 days; share of "up": 0.465
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.490 | 0.2512 | 0.6955 | – | – | – | – | – |
| logreg | 0.510 | 0.2513 | 0.6960 | 0.535 | -0.0005 | 0.339 | 0.535 | 6.64 |
| lgbm | 0.482 | 0.2532 | 0.6997 | 0.486 | -0.0082 | 0.253 | 0.483 | -14.52 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.196 | 0.000 | 11 |
| 0.2–0.3 | 0.277 | 0.319 | 216 |
| 0.3–0.4 | 0.369 | 0.381 | 5,952 |
| 0.4–0.5 | 0.461 | 0.440 | 23,616 |
| 0.5–0.6 | 0.531 | 0.478 | 60,742 |
| 0.6–0.7 | 0.640 | 0.525 | 5,317 |
| 0.7–0.8 | 0.739 | 0.511 | 618 |
| 0.8–0.9 | 0.819 | 0.755 | 102 |
