from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_not_found_returns_json_error():
    r = client.get("/no-existe")
    assert r.status_code == 404
    data = r.json()
    assert "error" in data
    assert data["error"]["type"] == "HTTPException"


def test_internal_error_returns_500_json(monkeypatch):
    import app.main as main_module

    async def boom_middleware(request, call_next):
        raise RuntimeError("boom")

    # Parchea el símbolo que realmente usa create_app()
    monkeypatch.setattr(main_module, "request_logging_middleware", boom_middleware)

    patched_app = main_module.create_app()

    # IMPORTANTE: que no propague la excepción al test
    patched_client = TestClient(patched_app, raise_server_exceptions=False)

    r = patched_client.get("/health")
    assert r.status_code == 500
    data = r.json()
    assert data["error"]["type"] == "InternalServerError"
