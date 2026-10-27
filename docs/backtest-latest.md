# IREN probability backtest (alpaca data)

Generated 2026-10-27T01:35:30+00:00 · data 2024-10-28T13:30:00+00:00 → 2026-10-26T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.515 | 0.519 | 0.2490 | 0.2497 | [-0.00096, -0.00034] | 0.513 | 249 | ⚠️ **no proven edge** |
| 15m | logreg | 0.508 | 0.517 | 0.2498 | 0.2498 | [-0.00024, +0.00038] | 0.499 | 249 | ⚠️ **no proven edge** |
| 1h | logreg | 0.515 | 0.519 | 0.2501 | 0.2499 | [-0.00038, +0.00076] | 0.493 | 249 | ⚠️ **no proven edge** |
| eod | logreg | 0.499 | 0.468 | 0.2508 | 0.2511 | [-0.00312, +0.00291] | 0.514 | 249 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,516 over 249 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.515 | 0.2490 | 0.6911 | 0.513 | 0.0026 | 0.021 | 0.649 | 0.84 |
| lgbm | 0.513 | 0.2491 | 0.6911 | 0.513 | 0.0024 | 0.053 | 0.555 | 0.55 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.176 | 0.108 | 157 |
| 0.2–0.3 | 0.236 | 0.133 | 240 |
| 0.3–0.4 | 0.335 | 0.229 | 410 |
| 0.4–0.5 | 0.482 | 0.479 | 64,672 |
| 0.5–0.6 | 0.511 | 0.494 | 30,948 |
| 0.6–0.7 | 0.612 | 0.750 | 4 |
| 0.7–0.8 | 0.720 | 0.518 | 85 |

## 15m (15 นาที)

- Test rows: 96,506 over 249 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.508 | 0.2498 | 0.6928 | 0.499 | -0.0003 | 0.023 | 0.558 | 0.31 |
| lgbm | 0.499 | 0.2499 | 0.6928 | 0.498 | -0.0003 | 0.021 | 0.598 | -1.97 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.180 | 0.208 | 24 |
| 0.2–0.3 | 0.258 | 0.256 | 203 |
| 0.3–0.4 | 0.357 | 0.230 | 296 |
| 0.4–0.5 | 0.485 | 0.484 | 67,715 |
| 0.5–0.6 | 0.510 | 0.484 | 28,157 |
| 0.6–0.7 | 0.644 | 0.604 | 111 |

## 1h (1 ชั่วโมง)

- Test rows: 96,461 over 249 days; share of "up": 0.481
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.515 | 0.2501 | 0.6933 | 0.493 | -0.0007 | 0.033 | 0.518 | 2.85 |
| lgbm | 0.502 | 0.2505 | 0.6941 | 0.495 | -0.0023 | 0.038 | 0.477 | -1.36 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.161 | 0.429 | 28 |
| 0.2–0.3 | 0.269 | 0.316 | 98 |
| 0.3–0.4 | 0.364 | 0.321 | 461 |
| 0.4–0.5 | 0.490 | 0.480 | 77,292 |
| 0.5–0.6 | 0.516 | 0.491 | 18,542 |
| 0.6–0.7 | 0.624 | 0.175 | 40 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,520 over 249 days; share of "up": 0.462
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.468 | 0.2511 | 0.6954 | – | – | – | – | – |
| logreg | 0.499 | 0.2508 | 0.6950 | 0.514 | 0.0012 | 0.207 | 0.537 | 1.14 |
| lgbm | 0.469 | 0.2550 | 0.7033 | 0.457 | -0.0155 | 0.222 | 0.456 | -17.04 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.184 | 0.000 | 20 |
| 0.2–0.3 | 0.264 | 0.412 | 80 |
| 0.3–0.4 | 0.373 | 0.448 | 2,001 |
| 0.4–0.5 | 0.460 | 0.431 | 23,831 |
| 0.5–0.6 | 0.520 | 0.470 | 67,980 |
| 0.6–0.7 | 0.640 | 0.581 | 1,971 |
| 0.7–0.8 | 0.729 | 0.456 | 621 |
| 0.8–0.9 | 0.819 | 0.375 | 16 |
