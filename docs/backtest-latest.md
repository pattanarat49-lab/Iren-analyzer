# IREN probability backtest (alpaca data)

Generated 2026-09-25T13:06:55+00:00 · data 2024-09-25T13:30:00+00:00 → 2026-09-24T19:59:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.518 | 0.514 | 0.2489 | 0.2500 | [-0.00135, -0.00071] | 0.519 | 250 | ✅ edge |
| 15m | lgbm | 0.511 | 0.511 | 0.2497 | 0.2499 | [-0.00057, +0.00017] | 0.508 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.506 | 0.512 | 0.2500 | 0.2499 | [-0.00047, +0.00069] | 0.506 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.523 | 0.473 | 0.2496 | 0.2505 | [-0.00439, +0.00261] | 0.555 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,955 over 250 days; share of "up": 0.486
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.514 | 0.2500 | 0.6931 | – | – | – | – | – |
| logreg | 0.518 | 0.2489 | 0.6908 | 0.519 | 0.0042 | 0.029 | 0.614 | 1.32 |
| lgbm | 0.516 | 0.2489 | 0.6909 | 0.517 | 0.0041 | 0.049 | 0.585 | 0.86 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.096 | 0.154 | 13 |
| 0.1–0.2 | 0.164 | 0.150 | 307 |
| 0.2–0.3 | 0.243 | 0.135 | 340 |
| 0.3–0.4 | 0.372 | 0.388 | 286 |
| 0.4–0.5 | 0.483 | 0.482 | 71,150 |
| 0.5–0.6 | 0.514 | 0.509 | 24,836 |
| 0.6–0.7 | 0.607 | 0.565 | 23 |

## 15m (15 นาที)

- Test rows: 96,945 over 250 days; share of "up": 0.489
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.511 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.512 | 0.2497 | 0.6926 | 0.511 | 0.0007 | 0.022 | 0.565 | 1.33 |
| lgbm | 0.511 | 0.2497 | 0.6925 | 0.508 | 0.0009 | 0.034 | 0.561 | 0.39 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.279 | 0.154 | 182 |
| 0.3–0.4 | 0.357 | 0.267 | 618 |
| 0.4–0.5 | 0.486 | 0.486 | 60,448 |
| 0.5–0.6 | 0.512 | 0.499 | 35,682 |
| 0.6–0.7 | 0.606 | 0.533 | 15 |

## 1h (1 ชั่วโมง)

- Test rows: 96,900 over 250 days; share of "up": 0.488
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.512 | 0.2499 | 0.6929 | – | – | – | – | – |
| logreg | 0.506 | 0.2500 | 0.6931 | 0.506 | -0.0004 | 0.033 | 0.541 | 4.61 |
| lgbm | 0.498 | 0.2502 | 0.6935 | 0.493 | -0.0011 | 0.019 | 0.568 | 0.49 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.272 | 0.000 | 1 |
| 0.3–0.4 | 0.373 | 0.425 | 266 |
| 0.4–0.5 | 0.487 | 0.489 | 75,735 |
| 0.5–0.6 | 0.515 | 0.485 | 20,898 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,959 over 250 days; share of "up": 0.474
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.473 | 0.2505 | 0.6942 | – | – | – | – | – |
| logreg | 0.523 | 0.2496 | 0.6924 | 0.555 | 0.0040 | 0.266 | 0.572 | 10.81 |
| lgbm | 0.507 | 0.2509 | 0.6951 | 0.517 | -0.0016 | 0.158 | 0.522 | -3.62 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.171 | 0.000 | 17 |
| 0.2–0.3 | 0.279 | 0.539 | 204 |
| 0.3–0.4 | 0.376 | 0.414 | 4,794 |
| 0.4–0.5 | 0.464 | 0.408 | 21,210 |
| 0.5–0.6 | 0.526 | 0.494 | 64,400 |
| 0.6–0.7 | 0.631 | 0.532 | 6,220 |
| 0.7–0.8 | 0.719 | 0.430 | 114 |
