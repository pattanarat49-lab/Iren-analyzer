# IREN probability backtest (alpaca data)

Generated 2026-10-14T22:52:49+00:00 · data 2024-10-14T13:30:00+00:00 → 2026-10-14T20:01:00+00:00

> For education only. Not financial advice. Past out-of-sample results do not guarantee
> future performance. No trading costs or slippage are modelled.

Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training
purged by label end time, calibration on the most recent 20 % of each training window,
baseline = the training window's base rate of "up". Edge requires the model's Brier score
to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.

## Summary

| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5m | logreg | 0.512 | 0.518 | 0.2490 | 0.2497 | [-0.00100, -0.00038] | 0.513 | 250 | ⚠️ **no proven edge** |
| 15m | lgbm | 0.500 | 0.516 | 0.2500 | 0.2498 | [-0.00015, +0.00066] | 0.497 | 250 | ⚠️ **no proven edge** |
| 1h | lgbm | 0.503 | 0.517 | 0.2502 | 0.2499 | [-0.00021, +0.00083] | 0.498 | 250 | ⚠️ **no proven edge** |
| eod | logreg | 0.516 | 0.488 | 0.2508 | 0.2511 | [-0.00420, +0.00376] | 0.538 | 250 | ⚠️ **no proven edge** |

## 5m (5 นาที)

- Test rows: 96,962 over 250 days; share of "up": 0.482
- Verdict: ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.518 | 0.2497 | 0.6925 | – | – | – | – | – |
| logreg | 0.512 | 0.2490 | 0.6910 | 0.513 | 0.0028 | 0.021 | 0.645 | 0.36 |
| lgbm | 0.515 | 0.2490 | 0.6911 | 0.515 | 0.0027 | 0.037 | 0.587 | 0.60 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.0–0.1 | 0.093 | 0.091 | 11 |
| 0.1–0.2 | 0.169 | 0.082 | 184 |
| 0.2–0.3 | 0.232 | 0.157 | 350 |
| 0.3–0.4 | 0.344 | 0.256 | 308 |
| 0.4–0.5 | 0.481 | 0.480 | 58,928 |
| 0.5–0.6 | 0.513 | 0.491 | 37,171 |
| 0.6–0.7 | 0.605 | 0.500 | 10 |

## 15m (15 นาที)

- Test rows: 96,952 over 250 days; share of "up": 0.484
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.516 | 0.2498 | 0.6927 | – | – | – | – | – |
| logreg | 0.501 | 0.2501 | 0.6933 | 0.499 | -0.0011 | 0.032 | 0.539 | -1.30 |
| lgbm | 0.500 | 0.2500 | 0.6932 | 0.497 | -0.0010 | 0.036 | 0.546 | -1.60 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.2–0.3 | 0.287 | 0.110 | 155 |
| 0.3–0.4 | 0.351 | 0.280 | 592 |
| 0.4–0.5 | 0.484 | 0.490 | 60,034 |
| 0.5–0.6 | 0.516 | 0.478 | 36,086 |
| 0.6–0.7 | 0.606 | 0.518 | 85 |

## 1h (1 ชั่วโมง)

- Test rows: 96,907 over 250 days; share of "up": 0.483
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.517 | 0.2499 | 0.6930 | – | – | – | – | – |
| logreg | 0.496 | 0.2503 | 0.6937 | 0.494 | -0.0015 | 0.062 | 0.519 | 0.64 |
| lgbm | 0.503 | 0.2502 | 0.6936 | 0.498 | -0.0012 | 0.021 | 0.535 | 0.78 |

Calibration (lgbm): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.3–0.4 | 0.395 | 0.503 | 644 |
| 0.4–0.5 | 0.490 | 0.487 | 70,977 |
| 0.5–0.6 | 0.513 | 0.473 | 25,281 |
| 0.6–0.7 | 0.601 | 0.800 | 5 |

## eod (จบวัน (ราคาปิด))

- Test rows: 96,964 over 250 days; share of "up": 0.468
- Verdict: Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ

| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.488 | 0.2511 | 0.6954 | – | – | – | – | – |
| logreg | 0.516 | 0.2508 | 0.6950 | 0.538 | 0.0012 | 0.355 | 0.537 | 11.61 |
| lgbm | 0.479 | 0.2531 | 0.6995 | 0.483 | -0.0080 | 0.220 | 0.493 | -16.96 |

Calibration (logreg): predicted vs observed frequency of "up"

| Predicted bin | Mean predicted | Observed | Rows |
|---|---|---|---|
| 0.1–0.2 | 0.187 | 0.000 | 13 |
| 0.2–0.3 | 0.274 | 0.342 | 301 |
| 0.3–0.4 | 0.377 | 0.379 | 6,090 |
| 0.4–0.5 | 0.464 | 0.442 | 27,143 |
| 0.5–0.6 | 0.534 | 0.481 | 57,362 |
| 0.6–0.7 | 0.643 | 0.548 | 5,294 |
| 0.7–0.8 | 0.743 | 0.542 | 664 |
| 0.8–0.9 | 0.814 | 0.588 | 97 |
