# IREN probability backtest (alpaca data)

Generated 2026-10-07T22:39:43+00:00 · data 2024-10-07T13:30:00+00:00 → 2026-10-07T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.516 | 0.517 | 0.2488 | 0.2498 | [-0.00126, -0.00059] | 0.519 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.504 | 0.515 | 0.2498 | 0.2498 | [-0.00038, +0.00036] | 0.501 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.501 | 0.516 | 0.2504 | 0.2499 | [-0.00034, +0.00147] | 0.496 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.519 | 0.485 | 0.2501 | 0.2514 | [-0.00535, +0.00268] | 0.545 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,966 over 250 days; share of "up": 0.483
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.518 | 0.2489 | 0.6908 | 0.517 | 0.0035 | 0.026 | 0.633 | 1.21 |
| lgbm | 0.516 | 0.2488 | 0.6907 | 0.519 | 0.0037 | 0.035 | 0.604 | 0.70 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.192 | 0.074 | 149 |
| 0.2–0.3 | 0.219 | 0.129 | 365 |
| 0.3–0.4 | 0.326 | 0.206 | 267 |
| 0.4–0.5 | 0.480 | 0.480 | 66,326 |
| 0.5–0.6 | 0.516 | 0.499 | 29,852 |
| 0.6–0.7 | 0.609 | 0.714 | 7 |

## 15m (15 นาที)

- Test rows: 96,956 over 250 days; share of "up": 0.485
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.515 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.507 | 0.2499 | 0.6930 | 0.503 | -0.0004 | 0.025 | 0.541 | 0.23 |
| lgbm | 0.504 | 0.2498 | 0.6927 | 0.501 | 0.0000 | 0.020 | 0.603 | -0.81 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.271 | 0.110 | 172 |
| 0.3–0.4 | 0.358 | 0.272 | 540 |
| 0.4–0.5 | 0.483 | 0.487 | 58,968 |
| 0.5–0.6 | 0.513 | 0.486 | 37,241 |
| 0.6–0.7 | 0.614 | 0.457 | 35 |

## 1h (1 ชั่วโมง)

- Test rows: 96,911 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.501 | 0.2504 | 0.6940 | 0.496 | -0.0021 | 0.088 | 0.511 | 1.03 |
| lgbm | 0.498 | 0.2504 | 0.6940 | 0.495 | -0.0022 | 0.029 | 0.529 | -0.58 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.173 | 0.435 | 23 |
| 0.2–0.3 | 0.285 | 0.330 | 103 |
| 0.3–0.4 | 0.365 | 0.427 | 281 |
| 0.4–0.5 | 0.484 | 0.488 | 66,722 |
| 0.5–0.6 | 0.521 | 0.474 | 29,739 |
| 0.6–0.7 | 0.638 | 0.279 | 43 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,970 over 250 days; share of "up": 0.465
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.485 | 0.2514 | 0.6959 | – | – | – | – | – |
| logreg | 0.519 | 0.2501 | 0.6936 | 0.545 | 0.0052 | 0.326 | 0.550 | 12.36 |
| lgbm | 0.466 | 0.2541 | 0.7015 | 0.467 | -0.0109 | 0.184 | 0.535 | -20.12 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.183 | 0.000 | 16 |
| 0.2–0.3 | 0.237 | 0.581 | 167 |
| 0.3–0.4 | 0.376 | 0.414 | 2,666 |
| 0.4–0.5 | 0.456 | 0.415 | 28,179 |
| 0.5–0.6 | 0.533 | 0.482 | 61,054 |
| 0.6–0.7 | 0.652 | 0.562 | 3,689 |
| 0.7–0.8 | 0.726 | 0.567 | 1,167 |
| 0.8–0.9 | 0.825 | 0.594 | 32 |
