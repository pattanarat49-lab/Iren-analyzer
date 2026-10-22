# IREN probability backtest (alpaca data)

Generated 2026-10-22T22:56:36+00:00 · data 2024-10-22T12:49:00+00:00 → 2026-10-22T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.513 | 0.518 | 0.2489 | 0.2497 | [-0.00112, -0.00046] | 0.515 | 250 | ⚠️ **no proven edge** |
| 15m | logreg | 0.508 | 0.516 | 0.2499 | 0.2498 | [-0.00028, +0.00038] | 0.502 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.501 | 0.518 | 0.2501 | 0.2499 | [-0.00037, +0.00074] | 0.496 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.501 | 0.480 | 0.2506 | 0.2510 | [-0.00351, +0.00271] | 0.535 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,899 over 250 days; share of "up": 0.482
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.514 | 0.2491 | 0.6911 | 0.513 | 0.0026 | 0.020 | 0.639 | 0.72 |
| lgbm | 0.513 | 0.2489 | 0.6909 | 0.515 | 0.0031 | 0.027 | 0.618 | 0.52 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.197 | 0.152 | 46 |
| 0.2–0.3 | 0.223 | 0.110 | 463 |
| 0.3–0.4 | 0.330 | 0.231 | 299 |
| 0.4–0.5 | 0.480 | 0.481 | 65,647 |
| 0.5–0.6 | 0.516 | 0.492 | 30,444 |

## 15m (15 นาที)

- Test rows: 96,889 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.508 | 0.2499 | 0.6929 | 0.502 | -0.0003 | 0.026 | 0.556 | 0.30 |
| lgbm | 0.505 | 0.2500 | 0.6931 | 0.499 | -0.0008 | 0.035 | 0.540 | -0.55 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.176 | 0.192 | 26 |
| 0.2–0.3 | 0.252 | 0.260 | 204 |
| 0.3–0.4 | 0.363 | 0.314 | 408 |
| 0.4–0.5 | 0.486 | 0.486 | 69,407 |
| 0.5–0.6 | 0.514 | 0.485 | 26,814 |
| 0.6–0.7 | 0.608 | 0.767 | 30 |

## 1h (1 ชั่วโมง)

- Test rows: 96,844 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.501 | 0.2501 | 0.6933 | 0.496 | -0.0007 | 0.026 | 0.534 | 0.66 |
| lgbm | 0.501 | 0.2506 | 0.6944 | 0.495 | -0.0029 | 0.048 | 0.506 | 0.27 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.169 | 0.440 | 25 |
| 0.2–0.3 | 0.281 | 0.333 | 138 |
| 0.3–0.4 | 0.370 | 0.344 | 183 |
| 0.4–0.5 | 0.489 | 0.488 | 72,113 |
| 0.5–0.6 | 0.513 | 0.467 | 24,384 |
| 0.6–0.7 | 0.603 | 0.000 | 1 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,903 over 250 days; share of "up": 0.467
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.480 | 0.2510 | 0.6951 | – | – | – | – | – |
| logreg | 0.501 | 0.2506 | 0.6946 | 0.535 | 0.0014 | 0.242 | 0.543 | 4.20 |
| lgbm | 0.469 | 0.2545 | 0.7022 | 0.463 | -0.0139 | 0.165 | 0.461 | -16.62 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.198 | 0.000 | 4 |
| 0.2–0.3 | 0.267 | 0.339 | 62 |
| 0.3–0.4 | 0.380 | 0.455 | 2,507 |
| 0.4–0.5 | 0.460 | 0.443 | 26,954 |
| 0.5–0.6 | 0.525 | 0.474 | 64,175 |
| 0.6–0.7 | 0.640 | 0.551 | 2,692 |
| 0.7–0.8 | 0.740 | 0.418 | 479 |
| 0.8–0.9 | 0.823 | 0.333 | 30 |
