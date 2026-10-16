# IREN probability backtest (alpaca data)

Generated 2026-10-16T22:55:02+00:00 · data 2024-10-16T13:30:00+00:00 → 2026-10-16T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.513 | 0.518 | 0.2490 | 0.2497 | [-0.00100, -0.00035] | 0.512 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.499 | 0.516 | 0.2500 | 0.2498 | [-0.00015, +0.00065] | 0.494 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.498 | 0.517 | 0.2501 | 0.2499 | [-0.00043, +0.00086] | 0.497 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.509 | 0.480 | 0.2511 | 0.2512 | [-0.00418, +0.00374] | 0.530 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,888 over 250 days; share of "up": 0.482
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.513 | 0.2490 | 0.6911 | 0.512 | 0.0027 | 0.022 | 0.636 | 0.52 |
| lgbm | 0.515 | 0.2491 | 0.6911 | 0.514 | 0.0026 | 0.049 | 0.566 | 0.56 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.099 | 0.000 | 2 |
| 0.1–0.2 | 0.168 | 0.099 | 162 |
| 0.2–0.3 | 0.238 | 0.147 | 380 |
| 0.3–0.4 | 0.345 | 0.288 | 288 |
| 0.4–0.5 | 0.481 | 0.480 | 61,811 |
| 0.5–0.6 | 0.512 | 0.493 | 34,244 |
| 0.6–0.7 | 0.631 | 1.000 | 1 |

## 15m (15 นาที)

- Test rows: 96,878 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.499 | 0.2501 | 0.6934 | 0.498 | -0.0013 | 0.033 | 0.540 | -1.28 |
| lgbm | 0.499 | 0.2500 | 0.6932 | 0.494 | -0.0010 | 0.023 | 0.580 | -1.62 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.292 | 0.137 | 102 |
| 0.3–0.4 | 0.359 | 0.216 | 578 |
| 0.4–0.5 | 0.485 | 0.492 | 68,635 |
| 0.5–0.6 | 0.516 | 0.471 | 27,563 |

## 1h (1 ชั่วโมง)

- Test rows: 96,833 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.498 | 0.2501 | 0.6934 | 0.497 | -0.0008 | 0.031 | 0.537 | 1.44 |
| lgbm | 0.504 | 0.2504 | 0.6940 | 0.496 | -0.0020 | 0.025 | 0.478 | 1.24 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.276 | 0.429 | 28 |
| 0.3–0.4 | 0.377 | 0.297 | 347 |
| 0.4–0.5 | 0.487 | 0.490 | 63,367 |
| 0.5–0.6 | 0.513 | 0.472 | 33,091 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,892 over 250 days; share of "up": 0.468
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.480 | 0.2512 | 0.6956 | – | – | – | – | – |
| logreg | 0.509 | 0.2511 | 0.6954 | 0.530 | 0.0006 | 0.335 | 0.534 | 6.04 |
| lgbm | 0.483 | 0.2539 | 0.7011 | 0.478 | -0.0107 | 0.214 | 0.489 | -14.06 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.193 | 0.000 | 8 |
| 0.2–0.3 | 0.276 | 0.261 | 153 |
| 0.3–0.4 | 0.369 | 0.379 | 5,311 |
| 0.4–0.5 | 0.463 | 0.447 | 24,788 |
| 0.5–0.6 | 0.530 | 0.479 | 60,874 |
| 0.6–0.7 | 0.637 | 0.530 | 5,179 |
| 0.7–0.8 | 0.726 | 0.536 | 556 |
| 0.8–0.9 | 0.823 | 0.696 | 23 |
