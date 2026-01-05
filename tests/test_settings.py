import os
from app.config.settings import Settings


def test_settings_reads_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5432/db")
    monkeypatch.setenv("SECRET_KEY", "x")

    s = Settings(_env_file=None)  
    assert s.app_env == "test"
