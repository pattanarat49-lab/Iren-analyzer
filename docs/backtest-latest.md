# IREN probability backtest (alpaca data)

Generated 2026-10-02T22:39:56+00:00 · data 2024-10-02T13:30:00+00:00 → 2026-10-02T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.513 | 0.515 | 0.2489 | 0.2498 | [-0.00125, -0.00058] | 0.517 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.503 | 0.514 | 0.2497 | 0.2498 | [-0.00042, +0.00025] | 0.502 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.494 | 0.515 | 0.2500 | 0.2499 | [-0.00036, +0.00066] | 0.493 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.525 | 0.490 | 0.2494 | 0.2510 | [-0.00497, +0.00166] | 0.551 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,975 over 250 days; share of "up": 0.485
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.515 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.518 | 0.2490 | 0.6910 | 0.518 | 0.0034 | 0.024 | 0.635 | 1.21 |
| lgbm | 0.513 | 0.2489 | 0.6908 | 0.517 | 0.0037 | 0.035 | 0.606 | 0.42 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.182 | 0.082 | 194 |
| 0.2–0.3 | 0.242 | 0.155 | 452 |
| 0.3–0.4 | 0.336 | 0.259 | 174 |
| 0.4–0.5 | 0.481 | 0.483 | 66,416 |
| 0.5–0.6 | 0.515 | 0.497 | 29,714 |
| 0.6–0.7 | 0.607 | 0.600 | 25 |

## 15m (15 นาที)

- Test rows: 96,965 over 250 days; share of "up": 0.486
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.509 | 0.2498 | 0.6927 | 0.507 | 0.0002 | 0.023 | 0.579 | 0.32 |
| lgbm | 0.503 | 0.2497 | 0.6926 | 0.502 | 0.0004 | 0.024 | 0.587 | -0.87 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.272 | 0.111 | 207 |
| 0.3–0.4 | 0.363 | 0.309 | 569 |
| 0.4–0.5 | 0.487 | 0.490 | 64,844 |
| 0.5–0.6 | 0.512 | 0.482 | 31,341 |
| 0.6–0.7 | 0.606 | 1.000 | 4 |

## 1h (1 ชั่วโมง)

- Test rows: 96,921 over 250 days; share of "up": 0.485
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.515 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.498 | 0.2504 | 0.6939 | 0.494 | -0.0020 | 0.043 | 0.513 | -0.31 |
| lgbm | 0.494 | 0.2500 | 0.6932 | 0.493 | -0.0006 | 0.015 | 0.584 | -2.45 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.374 | 0.226 | 340 |
| 0.4–0.5 | 0.489 | 0.495 | 67,027 |
| 0.5–0.6 | 0.509 | 0.465 | 29,293 |
| 0.6–0.7 | 0.627 | 0.444 | 261 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,979 over 250 days; share of "up": 0.469
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.490 | 0.2510 | 0.6951 | – | – | – | – | – |
| logreg | 0.525 | 0.2494 | 0.6920 | 0.551 | 0.0063 | 0.284 | 0.554 | 15.66 |
| lgbm | 0.473 | 0.2524 | 0.6980 | 0.478 | -0.0056 | 0.102 | 0.525 | -24.16 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.197 | 0.000 | 5 |
| 0.2–0.3 | 0.274 | 0.341 | 91 |
| 0.3–0.4 | 0.366 | 0.443 | 2,414 |
| 0.4–0.5 | 0.464 | 0.415 | 30,035 |
| 0.5–0.6 | 0.532 | 0.490 | 59,398 |
| 0.6–0.7 | 0.634 | 0.554 | 4,781 |
| 0.7–0.8 | 0.726 | 0.596 | 255 |
