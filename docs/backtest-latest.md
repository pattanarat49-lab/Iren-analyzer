# IREN probability backtest (alpaca data)

Generated 2026-10-01T22:38:48+00:00 · data 2024-10-01T13:30:00+00:00 → 2026-10-01T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.515 | 0.515 | 0.2489 | 0.2499 | [-0.00129, -0.00061] | 0.517 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.505 | 0.514 | 0.2497 | 0.2498 | [-0.00054, +0.00022] | 0.506 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.496 | 0.514 | 0.2501 | 0.2499 | [-0.00027, +0.00067] | 0.489 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.527 | 0.463 | 0.2496 | 0.2510 | [-0.00492, +0.00230] | 0.552 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,964 over 250 days; share of "up": 0.485
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.515 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.519 | 0.2490 | 0.6910 | 0.518 | 0.0037 | 0.024 | 0.634 | 1.31 |
| lgbm | 0.515 | 0.2489 | 0.6908 | 0.517 | 0.0039 | 0.040 | 0.595 | 0.68 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.192 | 0.071 | 141 |
| 0.2–0.3 | 0.238 | 0.156 | 598 |
| 0.3–0.4 | 0.372 | 0.345 | 119 |
| 0.4–0.5 | 0.481 | 0.482 | 66,183 |
| 0.5–0.6 | 0.515 | 0.500 | 29,916 |
| 0.6–0.7 | 0.602 | 1.000 | 7 |

## 15m (15 นาที)

- Test rows: 96,954 over 250 days; share of "up": 0.486
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.510 | 0.2499 | 0.6929 | 0.509 | -0.0001 | 0.023 | 0.553 | 0.59 |
| lgbm | 0.505 | 0.2497 | 0.6924 | 0.506 | 0.0007 | 0.026 | 0.575 | -0.64 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.274 | 0.116 | 207 |
| 0.3–0.4 | 0.360 | 0.331 | 580 |
| 0.4–0.5 | 0.487 | 0.487 | 55,411 |
| 0.5–0.6 | 0.511 | 0.489 | 40,756 |

## 1h (1 ชั่วโมง)

- Test rows: 96,909 over 250 days; share of "up": 0.486
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.499 | 0.2505 | 0.6941 | 0.494 | -0.0024 | 0.050 | 0.493 | 0.39 |
| lgbm | 0.496 | 0.2501 | 0.6933 | 0.489 | -0.0008 | 0.014 | 0.636 | -1.24 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.373 | 0.319 | 295 |
| 0.4–0.5 | 0.488 | 0.493 | 63,745 |
| 0.5–0.6 | 0.508 | 0.473 | 32,606 |
| 0.6–0.7 | 0.639 | 0.548 | 263 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,968 over 250 days; share of "up": 0.469
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.463 | 0.2510 | 0.6951 | – | – | – | – | – |
| logreg | 0.527 | 0.2496 | 0.6925 | 0.552 | 0.0054 | 0.296 | 0.553 | 17.20 |
| lgbm | 0.471 | 0.2523 | 0.6978 | 0.484 | -0.0053 | 0.095 | 0.532 | -26.03 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.195 | 0.000 | 9 |
| 0.2–0.3 | 0.254 | 0.618 | 157 |
| 0.3–0.4 | 0.369 | 0.437 | 2,346 |
| 0.4–0.5 | 0.466 | 0.416 | 31,979 |
| 0.5–0.6 | 0.535 | 0.492 | 57,852 |
| 0.6–0.7 | 0.642 | 0.551 | 4,383 |
| 0.7–0.8 | 0.719 | 0.611 | 239 |
| 0.8–0.9 | 0.805 | 1.000 | 3 |
