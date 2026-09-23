import pytest

from app import db
from app.config import Settings


@pytest.fixture
def settings(tmp_path):
    return Settings(
        _env_file=None,
        alpaca_api_key_id="key",
        alpaca_api_secret_key="secret",
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
    )


@pytest.fixture
def engine(settings):
    e = db.make_engine(settings.database_url)
    yield e
    e.dispose()
