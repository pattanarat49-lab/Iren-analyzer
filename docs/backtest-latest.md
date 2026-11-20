# IREN probability backtest (alpaca data)

Generated 2026-11-20T03:38:34+00:00 · data 2024-11-19T15:39:00+00:00 → 2026-11-19T21:00:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.519 | 0.519 | 0.2488 | 0.2497 | [-0.00118, -0.00053] | 0.516 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.515 | 0.517 | 0.2495 | 0.2498 | [-0.00068, +0.00005] | 0.512 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.507 | 0.516 | 0.2499 | 0.2498 | [-0.00050, +0.00057] | 0.501 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.526 | 0.474 | 0.2497 | 0.2501 | [-0.00351, +0.00284] | 0.543 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,906 over 250 days; share of "up": 0.481
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.521 | 0.2488 | 0.6906 | 0.517 | 0.0034 | 0.026 | 0.622 | 1.03 |
| lgbm | 0.519 | 0.2488 | 0.6906 | 0.516 | 0.0034 | 0.045 | 0.584 | 0.92 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.183 | 0.106 | 329 |
| 0.2–0.3 | 0.234 | 0.119 | 369 |
| 0.3–0.4 | 0.374 | 0.473 | 165 |
| 0.4–0.5 | 0.479 | 0.478 | 71,084 |
| 0.5–0.6 | 0.515 | 0.499 | 24,846 |
| 0.6–0.7 | 0.609 | 0.531 | 113 |

## 15m (15 นาที)

- Test rows: 96,896 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.516 | 0.2495 | 0.6921 | 0.510 | 0.0011 | 0.023 | 0.579 | 1.05 |
| lgbm | 0.515 | 0.2495 | 0.6920 | 0.512 | 0.0012 | 0.027 | 0.580 | 1.17 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.269 | 0.102 | 137 |
| 0.3–0.4 | 0.349 | 0.319 | 849 |
| 0.4–0.5 | 0.483 | 0.482 | 72,873 |
| 0.5–0.6 | 0.514 | 0.496 | 23,026 |
| 0.6–0.7 | 0.605 | 0.091 | 11 |

## 1h (1 ชั่วโมง)

- Test rows: 96,851 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.516 | 0.2501 | 0.6933 | 0.504 | -0.0009 | 0.012 | 0.581 | 5.15 |
| lgbm | 0.507 | 0.2499 | 0.6929 | 0.501 | -0.0002 | 0.027 | 0.572 | 1.18 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.370 | 0.294 | 412 |
| 0.4–0.5 | 0.488 | 0.485 | 68,644 |
| 0.5–0.6 | 0.509 | 0.485 | 27,559 |
| 0.6–0.7 | 0.620 | 0.466 | 236 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,909 over 250 days; share of "up": 0.476
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.474 | 0.2501 | 0.6933 | – | – | – | – | – |
| logreg | 0.526 | 0.2497 | 0.6928 | 0.543 | 0.0014 | 0.245 | 0.568 | 17.12 |
| lgbm | 0.508 | 0.2510 | 0.6954 | 0.510 | -0.0039 | 0.147 | 0.539 | -0.32 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.176 | 0.219 | 32 |
| 0.2–0.3 | 0.264 | 0.478 | 255 |
| 0.3–0.4 | 0.369 | 0.439 | 3,783 |
| 0.4–0.5 | 0.475 | 0.448 | 41,900 |
| 0.5–0.6 | 0.527 | 0.499 | 46,043 |
| 0.6–0.7 | 0.632 | 0.534 | 4,623 |
| 0.7–0.8 | 0.738 | 0.383 | 264 |
| 0.8–0.9 | 0.811 | 0.111 | 9 |
