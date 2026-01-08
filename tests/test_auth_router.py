from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_auth_router_is_registered():
    r = client.get("/auth/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
