from app.core.base import Base
from app.models.user import User


def test_user_model_registered_in_metadata():
    assert User.__table__ is not None
    assert "users" in Base.metadata.tables
