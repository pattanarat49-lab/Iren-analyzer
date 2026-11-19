# IREN probability backtest (alpaca data)

Generated 2026-11-19T03:44:22+00:00 · data 2024-11-18T15:45:00+00:00 → 2026-11-18T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.520 | 0.519 | 0.2488 | 0.2497 | [-0.00120, -0.00058] | 0.517 | 250 | ✅ edge |
| 15m | lgbm | 0.516 | 0.517 | 0.2493 | 0.2497 | [-0.00084, -0.00002] | 0.515 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.513 | 0.516 | 0.2500 | 0.2498 | [-0.00027, +0.00068] | 0.506 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.532 | 0.474 | 0.2493 | 0.2500 | [-0.00381, +0.00192] | 0.545 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,921 over 250 days; share of "up": 0.481
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.520 | 0.2489 | 0.6907 | 0.518 | 0.0032 | 0.030 | 0.611 | 0.97 |
| lgbm | 0.520 | 0.2488 | 0.6905 | 0.517 | 0.0036 | 0.056 | 0.578 | 1.21 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.184 | 0.090 | 255 |
| 0.2–0.3 | 0.239 | 0.116 | 439 |
| 0.3–0.4 | 0.372 | 0.441 | 222 |
| 0.4–0.5 | 0.479 | 0.478 | 71,134 |
| 0.5–0.6 | 0.516 | 0.500 | 24,757 |
| 0.6–0.7 | 0.607 | 0.579 | 114 |

## 15m (15 นาที)

- Test rows: 96,911 over 250 days; share of "up": 0.483
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.516 | 0.2495 | 0.6921 | 0.512 | 0.0009 | 0.024 | 0.561 | 0.84 |
| lgbm | 0.516 | 0.2493 | 0.6918 | 0.515 | 0.0017 | 0.028 | 0.596 | 1.09 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.272 | 0.140 | 164 |
| 0.3–0.4 | 0.340 | 0.307 | 783 |
| 0.4–0.5 | 0.483 | 0.480 | 69,601 |
| 0.5–0.6 | 0.516 | 0.498 | 26,324 |
| 0.6–0.7 | 0.610 | 0.359 | 39 |

## 1h (1 ชั่วโมง)

- Test rows: 96,866 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.513 | 0.2500 | 0.6932 | 0.506 | -0.0008 | 0.014 | 0.516 | 4.27 |
| lgbm | 0.507 | 0.2500 | 0.6932 | 0.504 | -0.0008 | 0.036 | 0.549 | 1.37 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.187 | 0.500 | 2 |
| 0.2–0.3 | 0.259 | 0.326 | 46 |
| 0.3–0.4 | 0.374 | 0.549 | 468 |
| 0.4–0.5 | 0.492 | 0.480 | 71,490 |
| 0.5–0.6 | 0.507 | 0.494 | 24,860 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,925 over 250 days; share of "up": 0.475
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.474 | 0.2500 | 0.6932 | – | – | – | – | – |
| logreg | 0.532 | 0.2493 | 0.6918 | 0.545 | 0.0031 | 0.258 | 0.566 | 21.85 |
| lgbm | 0.508 | 0.2513 | 0.6959 | 0.513 | -0.0050 | 0.159 | 0.523 | -3.65 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.185 | 0.731 | 78 |
| 0.2–0.3 | 0.266 | 0.437 | 87 |
| 0.3–0.4 | 0.382 | 0.453 | 2,091 |
| 0.4–0.5 | 0.474 | 0.441 | 45,050 |
| 0.5–0.6 | 0.528 | 0.505 | 45,383 |
| 0.6–0.7 | 0.619 | 0.534 | 4,115 |
| 0.7–0.8 | 0.716 | 0.322 | 121 |
