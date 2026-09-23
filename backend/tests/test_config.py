from app.config import Settings


def test_demo_mode_without_keys_uses_separate_db(tmp_path):
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
    assert s.stock_symbols == ["IREN", "CRWV", "NBIS", "NVDA", "QQQ"]
    assert s.crypto_symbol_list == ["BTC/USD"]
    assert "supersecret" not in str(s.public())
