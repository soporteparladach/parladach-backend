import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.config.settings import settings

client = TestClient(app)


def test_access_token_contains_exp_and_iat():
    email = "token_exp@test.com"
    password = "Student123*"

    client.post("/auth/register", json={"email": email, "password": password, "role": "STUDENT"})
    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200

    token = login.json()["access_token"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    assert "exp" in payload
    assert "iat" in payload
    assert payload["exp"] > payload["iat"]
