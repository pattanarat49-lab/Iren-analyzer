"""Load bar history from the database into per-symbol DataFrames."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
from sqlalchemy.engine import Engine

from .. import db
from ..analysis.engine import bars_to_frame


def load_frames(engine: Engine, symbols: list[str], years: float) -> dict[str, pd.DataFrame]:
    start = datetime.now(timezone.utc) - timedelta(days=365.25 * years)
    return {s: bars_to_frame(db.load_bars(engine, s, start=start)) for s in symbols}
