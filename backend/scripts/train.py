"""Train the up/down probability models for every horizon and save them.

Usage (from backend/):
    python -m scripts.train              # uses HISTORY_YEARS of bars in the database
    python -m scripts.train --years 1 --horizons 15m,1h

Models are written to models/<source>/ (source = "alpaca" or "demo"), together with report.json.
The running server picks up new model files automatically within a minute.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from app import db
from app.config import get_settings
from app.model.data import load_frames
from app.model.features import HORIZONS
from app.model.predictor import model_dir
from app.model.train import train_all


def main() -> int:
    s = get_settings()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--years", type=float, default=s.history_years)
    ap.add_argument("--horizons", default=",".join(HORIZONS))
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    engine = db.make_engine(s.effective_database_url)
    t0 = time.time()
    frames = load_frames(engine, s.all_symbols, args.years)
    n = len(frames[s.primary_symbol.upper()])
    print(f"Loaded {n:,d} {s.primary_symbol} bars ({s.resolved_source} data) in {time.time() - t0:.1f}s")
    if n < 5000:
        print("Not enough history. Run `python -m scripts.backfill` first.", file=sys.stderr)
        return 1
    out = model_dir(s.models_dir, s.resolved_source)
    peers = [x for x in s.all_symbols if x != s.primary_symbol.upper()]
    report = train_all(frames, s.primary_symbol.upper(), peers, out, s.resolved_source, args.horizons.split(","))
    for h, r in report["horizons"].items():
        m = r["metrics"]
        if "error" in m:
            print(f"  {h:4s}: {m['error']}")
            continue
        b = m["models"][m["best_model"]]
        verdict = "EDGE" if m["edge"] else "NO PROVEN EDGE"
        print(
            f"  {h:4s}: {m['best_model']:6s} acc {b['accuracy']:.3f} vs base {m['baseline']['accuracy']:.3f} | "
            f"Brier {b['brier']:.4f} vs base {m['baseline']['brier']:.4f} | {m['n_days']} test days | {verdict}"
        )
    print(f"Saved to {out} in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
