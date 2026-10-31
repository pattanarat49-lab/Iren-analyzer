# IREN probability backtest (alpaca data)

Generated 2026-10-31T01:42:51+00:00 · data 2024-10-30T13:43:00+00:00 → 2026-10-30T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.514 | 0.519 | 0.2489 | 0.2497 | [-0.00109, -0.00044] | 0.516 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.505 | 0.517 | 0.2498 | 0.2498 | [-0.00034, +0.00041] | 0.501 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.510 | 0.518 | 0.2504 | 0.2499 | [-0.00026, +0.00128] | 0.500 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.506 | 0.449 | 0.2498 | 0.2509 | [-0.00366, +0.00151] | 0.537 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,911 over 250 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.519 | 0.2491 | 0.6912 | 0.514 | 0.0025 | 0.023 | 0.630 | 1.09 |
| lgbm | 0.514 | 0.2489 | 0.6908 | 0.516 | 0.0031 | 0.028 | 0.610 | 0.51 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.194 | 0.029 | 70 |
| 0.2–0.3 | 0.250 | 0.145 | 619 |
| 0.3–0.4 | 0.344 | 0.293 | 116 |
| 0.4–0.5 | 0.479 | 0.480 | 66,322 |
| 0.5–0.6 | 0.516 | 0.492 | 29,780 |
| 0.6–0.7 | 0.601 | 1.000 | 4 |

## 15m (15 นาที)

- Test rows: 96,901 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.510 | 0.2498 | 0.6927 | 0.504 | -0.0001 | 0.035 | 0.533 | 0.51 |
| lgbm | 0.505 | 0.2498 | 0.6927 | 0.501 | -0.0001 | 0.029 | 0.583 | -0.87 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.271 | 0.113 | 150 |
| 0.3–0.4 | 0.360 | 0.321 | 704 |
| 0.4–0.5 | 0.483 | 0.488 | 70,226 |
| 0.5–0.6 | 0.515 | 0.477 | 25,821 |

## 1h (1 ชั่วโมง)

- Test rows: 96,856 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.511 | 0.2504 | 0.6940 | 0.485 | -0.0021 | 0.023 | 0.507 | 1.35 |
| lgbm | 0.510 | 0.2504 | 0.6939 | 0.500 | -0.0019 | 0.021 | 0.477 | 1.84 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.294 | 0.221 | 95 |
| 0.3–0.4 | 0.359 | 0.611 | 740 |
| 0.4–0.5 | 0.489 | 0.482 | 76,643 |
| 0.5–0.6 | 0.514 | 0.480 | 19,378 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,915 over 250 days; share of "up": 0.469
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.449 | 0.2509 | 0.6949 | – | – | – | – | – |
| logreg | 0.506 | 0.2498 | 0.6928 | 0.537 | 0.0042 | 0.203 | 0.550 | 8.25 |
| lgbm | 0.478 | 0.2536 | 0.7005 | 0.469 | -0.0109 | 0.149 | 0.457 | -16.44 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.196 | 0.000 | 10 |
| 0.2–0.3 | 0.269 | 0.432 | 44 |
| 0.3–0.4 | 0.376 | 0.499 | 1,172 |
| 0.4–0.5 | 0.475 | 0.453 | 36,999 |
| 0.5–0.6 | 0.521 | 0.476 | 56,518 |
| 0.6–0.7 | 0.640 | 0.606 | 1,892 |
| 0.7–0.8 | 0.727 | 0.387 | 279 |
| 0.8–0.9 | 0.803 | 1.000 | 1 |
