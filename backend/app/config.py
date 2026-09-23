"""Application settings, loaded from environment variables / backend/.env.

API keys are only ever read here, on the server. Nothing in this module is sent to the browser
except the non-secret fields exposed by `Settings.public()`.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_DIR / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    alpaca_api_key_id: str = ""
    alpaca_api_secret_key: str = ""
    # "iex" = free Basic plan (IEX exchange only); "sip" = Algo Trader Plus (consolidated tape).
    alpaca_stock_feed: Literal["iex", "sip"] = "iex"
    # Feed used for historical backfill. Defaults to the live feed so that volume-based features
    # are computed from the same source in training and live inference.
    alpaca_history_feed: Literal["iex", "sip"] | None = None
    alpaca_data_url: str = "https://data.alpaca.markets"
    alpaca_stream_url: str = "wss://stream.data.alpaca.markets"
    # Free plan allows 200 requests/min; keep a safety margin.
    alpaca_rest_rpm: int = 180

    finnhub_api_key: str = ""

    database_url: str = f"sqlite:///{REPO_DIR / 'data' / 'iren.db'}"

    primary_symbol: str = "IREN"
    context_symbols: str = "CIFR,NBIS,CRWV,NVDA,QQQ"
    crypto_symbols: str = "BTC/USD"

    # "auto" = Alpaca when keys are present, otherwise the simulated demo feed.
    data_source: Literal["auto", "alpaca", "demo"] = "auto"
    # Seconds between REST polls when the WebSocket is down.
    poll_interval_s: float = 10.0
    # Seconds without any stream message before we consider the socket dead.
    stream_stale_s: float = 90.0
    # Minutes without a trade in the regular session before flagging a possible halt.
    halt_suspect_min: int = 5

    cors_origins: str = "http://localhost:3000"

    history_years: float = Field(default=2.0, gt=0)

    # Nightly retrain after the extended session ends (20:00 ET) + this many minutes.
    retrain_enabled: bool = True
    retrain_delay_min: int = 30

    # Where trained models are stored (a persistent volume in deployments).
    models_dir: Path = REPO_DIR / "models"

    @field_validator("database_url", mode="before")
    @classmethod
    def _default_db(cls, v: str | None) -> str:
        v = (v or "").strip()
        if not v:
            return f"sqlite:///{REPO_DIR / 'data' / 'iren.db'}"
        # Hosting providers hand out postgres:// or postgresql:// URLs; use the psycopg 3 driver.
        for prefix in ("postgres://", "postgresql://"):
            if v.startswith(prefix):
                return "postgresql+psycopg://" + v[len(prefix):]
        return v

    @field_validator("models_dir", mode="before")
    @classmethod
    def _default_models(cls, v: str | Path | None) -> Path:
        return Path(v) if v else REPO_DIR / "models"

    @field_validator("alpaca_history_feed", mode="before")
    @classmethod
    def _empty_is_none(cls, v: str | None) -> str | None:
        return v or None

    @property
    def has_alpaca_keys(self) -> bool:
        return bool(self.alpaca_api_key_id and self.alpaca_api_secret_key)

    @property
    def resolved_source(self) -> Literal["alpaca", "demo"]:
        if self.data_source == "auto":
            return "alpaca" if self.has_alpaca_keys else "demo"
        return self.data_source

    @property
    def effective_database_url(self) -> str:
        """Demo mode writes to a separate SQLite file so simulated bars never mix with real ones."""
        if self.resolved_source == "demo" and self.database_url.startswith("sqlite:///"):
            path = Path(self.database_url.removeprefix("sqlite:///"))
            return f"sqlite:///{path.with_name(path.stem + '-demo' + path.suffix)}"
        return self.database_url

    @property
    def stock_symbols(self) -> list[str]:
        ctx = [s.strip().upper() for s in self.context_symbols.split(",") if s.strip()]
        return [self.primary_symbol.upper(), *[s for s in ctx if s != self.primary_symbol.upper()]]

    @property
    def crypto_symbol_list(self) -> list[str]:
        return [s.strip().upper() for s in self.crypto_symbols.split(",") if s.strip()]

    @property
    def all_symbols(self) -> list[str]:
        return [*self.stock_symbols, *self.crypto_symbol_list]

    @property
    def history_feed(self) -> str:
        return self.alpaca_history_feed or self.alpaca_stock_feed

    def public(self) -> dict:
        """Non-secret settings that are safe to show in the UI."""
        return {
            "source": self.resolved_source,
            "stock_feed": self.alpaca_stock_feed if self.resolved_source == "alpaca" else "demo",
            "primary_symbol": self.primary_symbol.upper(),
            "stock_symbols": self.stock_symbols,
            "crypto_symbols": self.crypto_symbol_list,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
