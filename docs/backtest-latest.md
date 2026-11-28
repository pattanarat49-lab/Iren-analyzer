# IREN probability backtest (alpaca data)

Generated 2026-11-28T04:04:47+00:00 · data 2024-11-27T16:05:00+00:00 → 2026-11-27T18:16:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.521 | 0.520 | 0.2488 | 0.2496 | [-0.00106, -0.00055] | 0.517 | 250 | ✅ edge |
| 15m | lgbm | 0.518 | 0.518 | 0.2495 | 0.2497 | [-0.00059, +0.00030] | 0.513 | 250 | ⚠️ **no proven edge** |
| 1h | logreg | 0.513 | 0.518 | 0.2499 | 0.2498 | [-0.00018, +0.00041] | 0.502 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.519 | 0.463 | 0.2506 | 0.2502 | [-0.00257, +0.00362] | 0.537 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,965 over 250 days; share of "up": 0.480
- Verdict: โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.520 | 0.2496 | 0.6924 | – | – | – | – | – |
| logreg | 0.521 | 0.2488 | 0.6906 | 0.517 | 0.0032 | 0.021 | 0.639 | 1.07 |
| lgbm | 0.517 | 0.2489 | 0.6907 | 0.515 | 0.0030 | 0.040 | 0.584 | 0.59 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.096 | 0.182 | 22 |
| 0.1–0.2 | 0.174 | 0.052 | 174 |
| 0.2–0.3 | 0.243 | 0.175 | 417 |
| 0.3–0.4 | 0.354 | 0.341 | 299 |
| 0.4–0.5 | 0.483 | 0.477 | 76,277 |
| 0.5–0.6 | 0.513 | 0.502 | 19,671 |
| 0.6–0.7 | 0.609 | 0.514 | 105 |

## 15m (15 นาที)

- Test rows: 96,964 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6926 | – | – | – | – | – |
| logreg | 0.515 | 0.2497 | 0.6924 | 0.509 | 0.0003 | 0.017 | 0.582 | 0.84 |
| lgbm | 0.518 | 0.2495 | 0.6922 | 0.513 | 0.0007 | 0.024 | 0.567 | 1.60 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.289 | 0.081 | 74 |
| 0.3–0.4 | 0.359 | 0.399 | 1,262 |
| 0.4–0.5 | 0.483 | 0.477 | 67,280 |
| 0.5–0.6 | 0.510 | 0.501 | 28,348 |

## 1h (1 ชั่วโมง)

- Test rows: 96,921 over 250 days; share of "up": 0.482
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.513 | 0.2499 | 0.6929 | 0.502 | -0.0004 | 0.004 | 0.583 | 3.17 |
| lgbm | 0.508 | 0.2501 | 0.6934 | 0.497 | -0.0013 | 0.027 | 0.519 | 0.95 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.374 | 0.556 | 153 |
| 0.4–0.5 | 0.493 | 0.483 | 90,815 |
| 0.5–0.6 | 0.506 | 0.461 | 5,953 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,963 over 250 days; share of "up": 0.474
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.463 | 0.2502 | 0.6935 | – | – | – | – | – |
| logreg | 0.519 | 0.2506 | 0.6946 | 0.537 | -0.0019 | 0.219 | 0.546 | 10.27 |
| lgbm | 0.499 | 0.2519 | 0.6972 | 0.499 | -0.0070 | 0.131 | 0.535 | -5.53 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.165 | 0.256 | 39 |
| 0.2–0.3 | 0.271 | 0.436 | 257 |
| 0.3–0.4 | 0.368 | 0.474 | 3,179 |
| 0.4–0.5 | 0.472 | 0.444 | 36,758 |
| 0.5–0.6 | 0.525 | 0.496 | 52,708 |
| 0.6–0.7 | 0.626 | 0.484 | 3,808 |
| 0.7–0.8 | 0.729 | 0.196 | 214 |
