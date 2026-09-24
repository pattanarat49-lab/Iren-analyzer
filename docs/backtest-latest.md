# IREN probability backtest (alpaca data)

Generated 2026-09-24T08:07:49+00:00 · data 2024-09-24T13:15:00+00:00 → 2026-09-23T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.513 | 0.514 | 0.2490 | 0.2500 | [-0.00129, -0.00054] | 0.514 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.506 | 0.511 | 0.2498 | 0.2499 | [-0.00054, +0.00028] | 0.510 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.502 | 0.512 | 0.2503 | 0.2499 | [-0.00038, +0.00122] | 0.499 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.526 | 0.435 | 0.2521 | 0.2508 | [-0.00295, +0.00581] | 0.528 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,962 over 250 days; share of "up": 0.486
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2500 | 0.6931 | – | – | – | – | – |
| logreg | 0.515 | 0.2493 | 0.6921 | 0.515 | 0.0026 | 0.023 | 0.645 | 0.85 |
| lgbm | 0.513 | 0.2490 | 0.6914 | 0.514 | 0.0037 | 0.030 | 0.620 | 0.86 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.067 | 0.178 | 275 |
| 0.1–0.2 | 0.117 | 0.123 | 308 |
| 0.2–0.3 | 0.227 | 0.123 | 179 |
| 0.3–0.4 | 0.328 | 0.467 | 364 |
| 0.4–0.5 | 0.479 | 0.482 | 57,317 |
| 0.5–0.6 | 0.508 | 0.499 | 38,091 |
| 0.6–0.7 | 0.635 | 0.547 | 382 |
| 0.7–0.8 | 0.746 | 0.333 | 6 |
| 0.8–0.9 | 0.838 | 0.750 | 8 |
| 0.9–1.0 | 0.984 | 0.688 | 32 |

## 15m (15 นาที)

- Test rows: 96,952 over 250 days; share of "up": 0.489
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.511 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.511 | 0.2500 | 0.6940 | 0.508 | -0.0004 | 0.022 | 0.583 | 1.30 |
| lgbm | 0.506 | 0.2498 | 0.6929 | 0.510 | 0.0006 | 0.029 | 0.569 | 0.14 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.049 | 0.252 | 103 |
| 0.1–0.2 | 0.144 | 0.157 | 274 |
| 0.2–0.3 | 0.258 | 0.268 | 287 |
| 0.3–0.4 | 0.367 | 0.433 | 194 |
| 0.4–0.5 | 0.490 | 0.492 | 81,931 |
| 0.5–0.6 | 0.523 | 0.483 | 13,017 |
| 0.6–0.7 | 0.612 | 0.497 | 1,092 |
| 0.7–0.8 | 0.747 | 0.440 | 25 |
| 0.8–0.9 | 0.883 | 0.870 | 23 |
| 0.9–1.0 | 0.942 | 0.167 | 6 |

## 1h (1 ชั่วโมง)

- Test rows: 96,907 over 250 days; share of "up": 0.488
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.512 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.503 | 0.2504 | 0.6951 | 0.503 | -0.0022 | 0.037 | 0.521 | 2.62 |
| lgbm | 0.502 | 0.2503 | 0.6938 | 0.499 | -0.0015 | 0.067 | 0.489 | -1.70 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.010 | 0.286 | 21 |
| 0.1–0.2 | 0.181 | 0.199 | 181 |
| 0.2–0.3 | 0.252 | 0.275 | 305 |
| 0.3–0.4 | 0.334 | 0.272 | 151 |
| 0.4–0.5 | 0.486 | 0.490 | 52,860 |
| 0.5–0.6 | 0.513 | 0.488 | 42,823 |
| 0.6–0.7 | 0.642 | 0.521 | 549 |
| 0.7–0.8 | 0.745 | 0.800 | 5 |
| 0.8–0.9 | 0.821 | 1.000 | 1 |
| 0.9–1.0 | 0.985 | 0.818 | 11 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,966 over 250 days; share of "up": 0.473
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.435 | 0.2508 | 0.6948 | – | – | – | – | – |
| logreg | 0.526 | 0.2521 | 0.6977 | 0.528 | -0.0051 | 0.345 | 0.539 | 5.83 |
| lgbm | 0.487 | 0.2545 | 0.7046 | 0.493 | -0.0147 | 0.293 | 0.534 | -14.46 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.021 | 0.000 | 6 |
| 0.1–0.2 | 0.123 | 0.000 | 1 |
| 0.2–0.3 | 0.295 | 0.389 | 198 |
| 0.3–0.4 | 0.368 | 0.432 | 8,420 |
| 0.4–0.5 | 0.463 | 0.434 | 29,475 |
| 0.5–0.6 | 0.540 | 0.494 | 50,107 |
| 0.6–0.7 | 0.642 | 0.535 | 8,419 |
| 0.7–0.8 | 0.721 | 0.335 | 334 |
| 0.8–0.9 | 0.876 | 1.000 | 2 |
| 0.9–1.0 | 0.990 | 1.000 | 4 |
