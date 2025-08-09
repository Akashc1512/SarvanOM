from fastapi.testclient import TestClient

from services.api_gateway.main import app


client = TestClient(app)


def test_gateway_index_forward(monkeypatch):
    # Mock retrieval service response
    class MockResponse:
        def __init__(self, status_code=200, json_data=None):
            self.status_code = status_code
            self._json = json_data or {"upserted": 2}

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception("HTTP error")

        def json(self):
            return self._json

    def mock_post(url, json):  # noqa: ARG001 - signature match for httpx
        return MockResponse(200, {"upserted": len(json.get("ids", []))})

    # Patch httpx.AsyncClient to synchronous shim for testing this route quickly
    import httpx

    class MockClient:
        def __init__(self, timeout):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json):
            return mock_post(url, json)

    monkeypatch.setattr(httpx, "AsyncClient", MockClient)

    payload = {
        "ids": ["x1", "x2"],
        "texts": ["A", "B"],
        "metadatas": [{}, {}],
    }
    r = client.post("/query/index", json=payload)
    assert r.status_code == 200, r.text
    assert r.json()["upserted"] == 2
