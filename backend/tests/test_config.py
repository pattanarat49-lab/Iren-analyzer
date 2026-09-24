from app.config import Settings


_KEY_VARS = (
    "ALPACA_API_KEY_ID", "APCA_API_KEY_ID", "ALPACA_APIKEY",
    "ALPACA_API_SECRET_KEY", "APCA_API_SECRET_KEY", "ALPACA_SECRETKEY",
)


def test_demo_mode_without_keys_uses_separate_db(tmp_path, monkeypatch):
    for name in _KEY_VARS:  # real keys in the shell must not leak into this test
        monkeypatch.delenv(name, raising=False)
    s = Settings(_env_file=None, database_url=f"sqlite:///{tmp_path}/iren.db")
    assert s.resolved_source == "demo"
    assert s.effective_database_url.endswith("iren-demo.db")


def test_alpaca_mode_with_keys(tmp_path):
    s = Settings(_env_file=None, alpaca_api_key_id="k", alpaca_api_secret_key="s", database_url="", alpaca_history_feed="")
    assert s.resolved_source == "alpaca"
    assert s.database_url.endswith("iren.db") and s.effective_database_url == s.database_url
    assert s.history_feed == "iex"


def test_symbols_and_public_has_no_secrets():
    s = Settings(_env_file=None, alpaca_api_key_id="k", alpaca_api_secret_key="supersecret")
    assert s.stock_symbols == ["IREN", "CIFR", "NBIS", "CRWV", "NVDA", "QQQ"]
    assert s.crypto_symbol_list == ["BTC/USD"]
    assert "supersecret" not in str(s.public())


def test_postgres_urls_use_psycopg3(tmp_path):
    s = Settings(_env_file=None, database_url="postgres://u:p@host:5432/db")
    assert s.database_url == "postgresql+psycopg://u:p@host:5432/db"
    s = Settings(_env_file=None, database_url="postgresql://u:p@host/db")
    assert s.database_url.startswith("postgresql+psycopg://")


def test_postgres_schema_and_upserts_compile():
    """The upsert statements must compile for PostgreSQL (no live server needed)."""
    from sqlalchemy.dialects import postgresql
    from sqlalchemy.dialects.postgresql import insert
    from sqlalchemy.schema import CreateTable

    from app import db

    for t in (db.bars, db.predictions, db.stream_events):
        str(CreateTable(t).compile(dialect=postgresql.dialect()))
    stmt = insert(db.predictions).values([{"horizon": "5m"}]).on_conflict_do_nothing(index_elements=["made_at", "horizon", "source"])
    assert "ON CONFLICT" in str(stmt.compile(dialect=postgresql.dialect()))


def test_models_dir_env(tmp_path):
    s = Settings(_env_file=None, models_dir=str(tmp_path / "m"))
    assert s.models_dir == tmp_path / "m"


def test_apca_env_names_are_accepted(monkeypatch):
    monkeypatch.setenv("APCA_API_KEY_ID", "id-from-apca")
    monkeypatch.setenv("APCA_API_SECRET_KEY", "secret-from-apca")
    s = Settings(_env_file=None)
    assert s.alpaca_api_key_id == "id-from-apca" and s.has_alpaca_keys


def test_short_env_names_are_accepted(monkeypatch):
    monkeypatch.setenv("ALPACA_APIKEY", "short-id")
    monkeypatch.setenv("ALPACA_SECRETKEY", "short-secret")
    s = Settings(_env_file=None)
    assert (s.alpaca_api_key_id, s.alpaca_api_secret_key) == ("short-id", "short-secret")
    assert s.resolved_source == "alpaca"


def test_keys_are_stripped():
    s = Settings(_env_file=None, alpaca_api_key_id=" k\n", alpaca_api_secret_key="s \n")
    assert (s.alpaca_api_key_id, s.alpaca_api_secret_key) == ("k", "s")
    s = Settings(_env_file=None, alpaca_api_key_id='"k"', alpaca_api_secret_key="'s'\n")
    assert (s.alpaca_api_key_id, s.alpaca_api_secret_key) == ("k", "s")
