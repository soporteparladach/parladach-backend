from sqlalchemy import text

from app.core.database import engine


def test_db_connection_select_1():
    with engine.connect() as conn:
        value = conn.execute(text("SELECT 1")).scalar_one()
        assert value == 1
