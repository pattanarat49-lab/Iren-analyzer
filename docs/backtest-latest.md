# IREN probability backtest (alpaca data)

Generated 2026-11-25T05:00:06+00:00 · data 2024-11-25T14:30:00+00:00 → 2026-11-24T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.520 | 0.521 | 0.2488 | 0.2496 | [-0.00113, -0.00053] | 0.517 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.517 | 0.518 | 0.2495 | 0.2497 | [-0.00060, +0.00016] | 0.512 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.507 | 0.519 | 0.2497 | 0.2498 | [-0.00028, +0.00028] | 0.508 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.539 | 0.498 | 0.2498 | 0.2501 | [-0.00334, +0.00297] | 0.548 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,931 over 250 days; share of "up": 0.479
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.521 | 0.2496 | 0.6924 | – | – | – | – | – |
| logreg | 0.522 | 0.2488 | 0.6906 | 0.518 | 0.0033 | 0.024 | 0.623 | 1.29 |
| lgbm | 0.520 | 0.2488 | 0.6905 | 0.517 | 0.0034 | 0.040 | 0.581 | 1.02 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.181 | 0.056 | 143 |
| 0.2–0.3 | 0.232 | 0.148 | 575 |
| 0.3–0.4 | 0.367 | 0.396 | 91 |
| 0.4–0.5 | 0.480 | 0.477 | 73,499 |
| 0.5–0.6 | 0.515 | 0.498 | 22,616 |
| 0.6–0.7 | 0.604 | 0.429 | 7 |

## 15m (15 นาที)

- Test rows: 96,921 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.517 | 0.2495 | 0.6922 | 0.510 | 0.0007 | 0.023 | 0.585 | 1.14 |
| lgbm | 0.517 | 0.2495 | 0.6921 | 0.512 | 0.0009 | 0.027 | 0.577 | 1.43 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.292 | 0.122 | 90 |
| 0.3–0.4 | 0.354 | 0.301 | 933 |
| 0.4–0.5 | 0.481 | 0.477 | 63,426 |
| 0.5–0.6 | 0.513 | 0.497 | 32,472 |

## 1h (1 ชั่วโมง)

- Test rows: 96,877 over 250 days; share of "up": 0.481
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.507 | 0.2497 | 0.6926 | 0.508 | 0.0000 | 0.008 | 0.597 | 4.49 |
| lgbm | 0.512 | 0.2500 | 0.6932 | 0.497 | -0.0010 | 0.039 | 0.531 | 2.45 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.285 | 0.417 | 12 |
| 0.3–0.4 | 0.353 | 0.408 | 152 |
| 0.4–0.5 | 0.491 | 0.484 | 78,686 |
| 0.5–0.6 | 0.504 | 0.467 | 18,027 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,935 over 250 days; share of "up": 0.471
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.498 | 0.2501 | 0.6934 | – | – | – | – | – |
| logreg | 0.539 | 0.2498 | 0.6929 | 0.548 | 0.0013 | 0.250 | 0.565 | 24.49 |
| lgbm | 0.506 | 0.2514 | 0.6960 | 0.504 | -0.0050 | 0.179 | 0.545 | 1.68 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.168 | 0.000 | 26 |
| 0.2–0.3 | 0.268 | 0.323 | 158 |
| 0.3–0.4 | 0.375 | 0.439 | 4,809 |
| 0.4–0.5 | 0.478 | 0.428 | 40,694 |
| 0.5–0.6 | 0.528 | 0.512 | 46,549 |
| 0.6–0.7 | 0.629 | 0.499 | 4,417 |
| 0.7–0.8 | 0.730 | 0.248 | 282 |
