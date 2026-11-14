# IREN probability backtest (alpaca data)

Generated 2026-11-14T02:35:03+00:00 · data 2024-11-13T14:35:00+00:00 → 2026-11-13T20:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | lgbm | 0.520 | 0.519 | 0.2488 | 0.2497 | [-0.00116, -0.00055] | 0.516 | 250 | ✅ edge |
| 15m | lgbm | 0.513 | 0.517 | 0.2494 | 0.2497 | [-0.00069, +0.00006] | 0.510 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.508 | 0.517 | 0.2497 | 0.2498 | [-0.00079, +0.00063] | 0.500 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.516 | 0.483 | 0.2494 | 0.2500 | [-0.00296, +0.00180] | 0.534 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,931 over 250 days; share of "up": 0.481
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.519 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.521 | 0.2489 | 0.6908 | 0.517 | 0.0031 | 0.034 | 0.597 | 1.10 |
| lgbm | 0.520 | 0.2488 | 0.6906 | 0.516 | 0.0035 | 0.041 | 0.590 | 1.13 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.183 | 0.060 | 150 |
| 0.2–0.3 | 0.242 | 0.136 | 568 |
| 0.3–0.4 | 0.370 | 0.406 | 143 |
| 0.4–0.5 | 0.479 | 0.476 | 66,601 |
| 0.5–0.6 | 0.513 | 0.501 | 29,437 |
| 0.6–0.7 | 0.607 | 0.594 | 32 |

## 15m (15 นาที)

- Test rows: 96,921 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.517 | 0.2495 | 0.6921 | 0.511 | 0.0011 | 0.024 | 0.576 | 1.37 |
| lgbm | 0.513 | 0.2494 | 0.6920 | 0.510 | 0.0013 | 0.023 | 0.600 | 0.73 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.281 | 0.133 | 90 |
| 0.3–0.4 | 0.338 | 0.289 | 835 |
| 0.4–0.5 | 0.484 | 0.482 | 69,966 |
| 0.5–0.6 | 0.516 | 0.493 | 26,026 |
| 0.6–0.7 | 0.604 | 0.500 | 4 |

## 1h (1 ชั่วโมง)

- Test rows: 96,876 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2498 | 0.6928 | – | – | – | – | – |
| logreg | 0.512 | 0.2500 | 0.6932 | 0.495 | -0.0008 | 0.013 | 0.548 | 5.83 |
| lgbm | 0.508 | 0.2497 | 0.6926 | 0.500 | 0.0004 | 0.042 | 0.579 | 2.03 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.382 | 0.318 | 777 |
| 0.4–0.5 | 0.486 | 0.484 | 64,867 |
| 0.5–0.6 | 0.512 | 0.487 | 31,221 |
| 0.6–0.7 | 0.604 | 0.000 | 11 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,935 over 250 days; share of "up": 0.474
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.483 | 0.2500 | 0.6932 | – | – | – | – | – |
| logreg | 0.516 | 0.2494 | 0.6921 | 0.534 | 0.0024 | 0.181 | 0.571 | 15.04 |
| lgbm | 0.500 | 0.2513 | 0.6958 | 0.504 | -0.0052 | 0.151 | 0.486 | -5.17 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.235 | 0.624 | 109 |
| 0.3–0.4 | 0.382 | 0.444 | 1,064 |
| 0.4–0.5 | 0.474 | 0.451 | 40,872 |
| 0.5–0.6 | 0.525 | 0.489 | 53,765 |
| 0.6–0.7 | 0.632 | 0.621 | 995 |
| 0.7–0.8 | 0.718 | 0.292 | 130 |
