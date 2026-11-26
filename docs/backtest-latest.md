# IREN probability backtest (alpaca data)

Generated 2026-11-26T04:16:55+00:00 · data 2024-11-25T16:17:00+00:00 → 2026-11-25T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.520 | 0.520 | 0.2487 | 0.2496 | [-0.00118, -0.00055] | 0.518 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.517 | 0.518 | 0.2494 | 0.2497 | [-0.00068, +0.00003] | 0.514 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.511 | 0.519 | 0.2498 | 0.2498 | [-0.00025, +0.00024] | 0.506 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.533 | 0.487 | 0.2496 | 0.2503 | [-0.00347, +0.00239] | 0.546 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,955 over 250 days; share of "up": 0.480
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.520 | 0.2496 | 0.6924 | – | – | – | – | – |
| logreg | 0.521 | 0.2488 | 0.6907 | 0.519 | 0.0031 | 0.024 | 0.627 | 1.19 |
| lgbm | 0.520 | 0.2487 | 0.6904 | 0.518 | 0.0035 | 0.042 | 0.589 | 1.01 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.188 | 0.041 | 146 |
| 0.2–0.3 | 0.231 | 0.164 | 599 |
| 0.3–0.4 | 0.366 | 0.532 | 111 |
| 0.4–0.5 | 0.479 | 0.475 | 69,032 |
| 0.5–0.6 | 0.514 | 0.499 | 27,065 |
| 0.6–0.7 | 0.602 | 1.000 | 2 |

## 15m (15 นาที)

- Test rows: 96,945 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.516 | 0.2496 | 0.6924 | 0.513 | 0.0004 | 0.024 | 0.568 | 1.14 |
| lgbm | 0.517 | 0.2494 | 0.6919 | 0.514 | 0.0014 | 0.027 | 0.576 | 1.25 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.294 | 0.143 | 105 |
| 0.3–0.4 | 0.347 | 0.274 | 758 |
| 0.4–0.5 | 0.483 | 0.478 | 66,213 |
| 0.5–0.6 | 0.512 | 0.498 | 29,869 |

## 1h (1 ชั่วโมง)

- Test rows: 96,900 over 250 days; share of "up": 0.481
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.511 | 0.2498 | 0.6927 | 0.506 | -0.0000 | 0.003 | 0.650 | 4.35 |
| lgbm | 0.514 | 0.2499 | 0.6930 | 0.499 | -0.0006 | 0.030 | 0.527 | 3.57 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.296 | 0.000 | 1 |
| 0.3–0.4 | 0.357 | 0.447 | 132 |
| 0.4–0.5 | 0.492 | 0.483 | 84,870 |
| 0.5–0.6 | 0.507 | 0.470 | 11,897 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,959 over 250 days; share of "up": 0.472
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.487 | 0.2503 | 0.6937 | – | – | – | – | – |
| logreg | 0.533 | 0.2496 | 0.6926 | 0.546 | 0.0026 | 0.217 | 0.554 | 20.24 |
| lgbm | 0.494 | 0.2512 | 0.6958 | 0.496 | -0.0038 | 0.154 | 0.556 | -6.93 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.176 | 0.000 | 11 |
| 0.2–0.3 | 0.236 | 0.587 | 126 |
| 0.3–0.4 | 0.382 | 0.474 | 2,374 |
| 0.4–0.5 | 0.474 | 0.433 | 42,986 |
| 0.5–0.6 | 0.527 | 0.506 | 48,247 |
| 0.6–0.7 | 0.624 | 0.492 | 3,090 |
| 0.7–0.8 | 0.717 | 0.264 | 125 |
