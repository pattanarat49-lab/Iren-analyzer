import os

import pytest

from app import db
from app.config import Settings

# Set TEST_DATABASE_URL (e.g. postgresql+psycopg://postgres:pw@localhost:5432/iren) to run every
# database test against PostgreSQL instead of a temporary SQLite file.
TEST_DB = os.environ.get("TEST_DATABASE_URL")


@pytest.fixture
def settings(tmp_path):
    return Settings(
        _env_file=None,
        alpaca_api_key_id="key",
        alpaca_api_secret_key="secret",
        database_url=TEST_DB or f"sqlite:///{tmp_path / 'test.db'}",
    )


@pytest.fixture
def engine(settings):
    e = db.make_engine(settings.database_url)
    if TEST_DB:
        db.metadata.drop_all(e)
        db.metadata.create_all(e)
    yield e
    e.dispose()
