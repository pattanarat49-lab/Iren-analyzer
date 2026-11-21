# IREN probability backtest (alpaca data)

Generated 2026-11-21T03:21:26+00:00 · data 2024-11-20T15:22:00+00:00 → 2026-11-20T21:01:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.522 | 0.520 | 0.2488 | 0.2497 | [-0.00113, -0.00059] | 0.518 | 250 | ✅ edge |
| 15m | lgbm | 0.514 | 0.517 | 0.2493 | 0.2498 | [-0.00083, -0.00004] | 0.515 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.510 | 0.517 | 0.2500 | 0.2498 | [-0.00050, +0.00084] | 0.506 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.526 | 0.471 | 0.2495 | 0.2501 | [-0.00370, +0.00246] | 0.547 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,904 over 250 days; share of "up": 0.480
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.520 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.522 | 0.2488 | 0.6906 | 0.518 | 0.0034 | 0.024 | 0.623 | 1.08 |
| lgbm | 0.517 | 0.2488 | 0.6906 | 0.515 | 0.0034 | 0.047 | 0.581 | 0.73 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.094 | 0.083 | 12 |
| 0.1–0.2 | 0.170 | 0.066 | 197 |
| 0.2–0.3 | 0.244 | 0.133 | 354 |
| 0.3–0.4 | 0.363 | 0.383 | 295 |
| 0.4–0.5 | 0.481 | 0.477 | 77,472 |
| 0.5–0.6 | 0.515 | 0.506 | 18,477 |
| 0.6–0.7 | 0.650 | 0.619 | 21 |
| 0.7–0.8 | 0.707 | 0.487 | 76 |

## 15m (15 นาที)

- Test rows: 96,894 over 250 days; share of "up": 0.483
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.517 | 0.2496 | 0.6923 | 0.509 | 0.0006 | 0.023 | 0.575 | 1.22 |
| lgbm | 0.514 | 0.2493 | 0.6918 | 0.515 | 0.0017 | 0.035 | 0.568 | 1.05 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.269 | 0.118 | 119 |
| 0.3–0.4 | 0.342 | 0.324 | 943 |
| 0.4–0.5 | 0.483 | 0.483 | 75,015 |
| 0.5–0.6 | 0.517 | 0.493 | 20,803 |
| 0.6–0.7 | 0.612 | 0.571 | 14 |

## 1h (1 ชั่วโมง)

- Test rows: 96,849 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.515 | 0.2500 | 0.6932 | 0.504 | -0.0008 | 0.010 | 0.556 | 5.12 |
| lgbm | 0.510 | 0.2500 | 0.6931 | 0.506 | -0.0007 | 0.034 | 0.533 | 3.60 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.377 | 0.251 | 351 |
| 0.4–0.5 | 0.487 | 0.482 | 69,049 |
| 0.5–0.6 | 0.511 | 0.486 | 27,182 |
| 0.6–0.7 | 0.634 | 0.506 | 267 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,906 over 250 days; share of "up": 0.474
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.471 | 0.2501 | 0.6934 | – | – | – | – | – |
| logreg | 0.526 | 0.2495 | 0.6923 | 0.547 | 0.0024 | 0.234 | 0.573 | 18.80 |
| lgbm | 0.501 | 0.2514 | 0.6959 | 0.494 | -0.0050 | 0.110 | 0.499 | -3.09 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.162 | 0.000 | 22 |
| 0.2–0.3 | 0.266 | 0.460 | 202 |
| 0.3–0.4 | 0.368 | 0.450 | 3,432 |
| 0.4–0.5 | 0.476 | 0.448 | 44,755 |
| 0.5–0.6 | 0.528 | 0.498 | 43,956 |
| 0.6–0.7 | 0.627 | 0.522 | 4,216 |
| 0.7–0.8 | 0.727 | 0.307 | 238 |
| 0.8–0.9 | 0.819 | 0.788 | 85 |
