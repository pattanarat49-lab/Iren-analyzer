"""Walk-forward backtest of the probability models; writes a Markdown + JSON report.

Usage (from backend/):
    python -m scripts.backtest                 # all horizons, HISTORY_YEARS of data
    python -m scripts.backtest --years 1 --horizons 15m

Output: reports/backtest-<source>-<YYYYMMDD-HHMM>.md and .json in the repository root.
Every number in the report is out-of-sample: each prediction was made by a model trained only on
data whose outcome was known before that prediction's day.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone

from app import db
from app.config import REPO_DIR, get_settings
from app.model.data import load_frames
from app.model.features import HORIZON_TH, HORIZONS, build_features
from app.model.train import _jsonable, train_horizon


def fmt(x, digits=3):  # noqa: ANN001, ANN201
    return "–" if x is None else f"{x:.{digits}f}"


def render(report: dict) -> str:
    lines = [
        f"# IREN probability backtest ({report['source']} data)",
        "",
        f"Generated {report['generated_at']} · data {report['data_start']} → {report['data_end']}",
        "",
        "> For education only. Not financial advice. Past out-of-sample results do not guarantee",
        "> future performance. No trading costs or slippage are modelled.",
        "",
        "Method: expanding-window walk-forward (5 test blocks over the last 50 % of days), training",
        "purged by label end time, calibration on the most recent 20 % of each training window,",
        "baseline = the training window's base rate of \"up\". Edge requires the model's Brier score",
        "to beat the baseline with 95 % confidence (day-block bootstrap) on at least 20 test days.",
        "",
        "## Summary",
        "",
        "| Horizon | Best model | Accuracy | Baseline acc. | Brier | Baseline Brier | Brier diff 95% CI | AUC | Test days | Verdict |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for h, r in report["horizons"].items():
        m = r["metrics"]
        if "error" in m:
            lines.append(f"| {h} | – | – | – | – | – | – | – | – | {m['error']} |")
            continue
        b = m["models"][m["best_model"]]
        ci = b["brier_diff_ci"]
        verdict = "✅ edge" if m["edge"] else "⚠️ **no proven edge**"
        lines.append(
            f"| {h} | {m['best_model']} | {fmt(b['accuracy'])} | {fmt(m['baseline']['accuracy'])} | {fmt(b['brier'], 4)} | "
            f"{fmt(m['baseline']['brier'], 4)} | [{ci[0]:+.5f}, {ci[1]:+.5f}] | {fmt(b['auc'])} | {m['n_days']} | {verdict} |"
        )
    for h, r in report["horizons"].items():
        m = r["metrics"]
        if "error" in m:
            continue
        lines += ["", f"## {h} ({HORIZON_TH[h]})", "", f"- Test rows: {m['n']:,d} over {m['n_days']} days; share of \"up\": {m['up_rate']:.3f}", f"- Verdict: {m['edge_reason']}", ""]
        lines += ["| Model | Accuracy | Brier | Log loss | AUC | Brier skill | Confident share (p≥0.55 or ≤0.45) | Confident accuracy | Mean signed fwd return (bp) |", "|---|---|---|---|---|---|---|---|---|"]
        lines.append(f"| baseline | {fmt(m['baseline']['accuracy'])} | {fmt(m['baseline']['brier'], 4)} | {fmt(m['baseline']['logloss'], 4)} | – | – | – | – | – |")
        for kind, b in m["models"].items():
            lines.append(
                f"| {kind} | {fmt(b['accuracy'])} | {fmt(b['brier'], 4)} | {fmt(b['logloss'], 4)} | {fmt(b['auc'])} | {fmt(b['brier_skill'], 4)} | "
                f"{fmt(b['confident_share'])} | {fmt(b['confident_accuracy'])} | {fmt(b['mean_signed_fwd_ret_bp'], 2)} |"
            )
        best = m["models"][m["best_model"]]
        lines += ["", f"Calibration ({m['best_model']}): predicted vs observed frequency of \"up\"", "", "| Predicted bin | Mean predicted | Observed | Rows |", "|---|---|---|---|"]
        for c in best["reliability"]:
            lines.append(f"| {c['bin_low']:.1f}–{c['bin_high']:.1f} | {c['mean_p']:.3f} | {c['observed']:.3f} | {c['n']:,d} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    s = get_settings()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--years", type=float, default=s.history_years)
    ap.add_argument("--horizons", default=",".join(HORIZONS))
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    engine = db.make_engine(s.effective_database_url)
    frames = load_frames(engine, s.all_symbols, args.years)
    primary = s.primary_symbol.upper()
    if len(frames[primary]) < 5000:
        print("Not enough history. Run `python -m scripts.backfill` first.", file=sys.stderr)
        return 1
    peers = [x for x in s.all_symbols if x != primary]
    feats = build_features(frames, primary, peers)
    now = datetime.now(timezone.utc)
    report = {
        "generated_at": now.isoformat(timespec="seconds"),
        "source": s.resolved_source,
        "data_start": frames[primary].index[0].isoformat(),
        "data_end": frames[primary].index[-1].isoformat(),
        "horizons": {},
    }
    for h in args.horizons.split(","):
        r = train_horizon(feats, frames[primary], h)
        report["horizons"][h] = {"metrics": r.metrics, "meta": {k: v for k, v in r.meta.items() if k != "features"}}
    out_dir = REPO_DIR / "reports"
    out_dir.mkdir(exist_ok=True)
    stem = f"backtest-{s.resolved_source}-{now:%Y%m%d-%H%M}"
    (out_dir / f"{stem}.md").write_text(render(report), encoding="utf-8")
    (out_dir / f"{stem}.json").write_text(json.dumps(_jsonable(report), ensure_ascii=False, indent=2), encoding="utf-8")
    print(render(report).split("## Summary")[1].split("\n## ")[0])
    print(f"Report: {out_dir / stem}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
