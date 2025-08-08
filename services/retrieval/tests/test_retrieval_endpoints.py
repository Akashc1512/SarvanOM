import asyncio
from fastapi.testclient import TestClient

from services.retrieval.main import app


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "retrieval"


def test_index_and_search_roundtrip():
    # Index a couple docs
    payload = {
        "ids": ["d1", "d2"],
        "texts": [
            "Paris is the capital of France.",
            "Tokyo is the capital of Japan.",
        ],
        "metadatas": [{"lang": "en"}, {"lang": "en"}],
    }
    r = client.post("/index", json=payload)
    assert r.status_code == 200, r.text
    assert r.json().get("upserted") == 2

    # Search for related text
    s = client.post("/search", json={"query": "What is the capital of France?", "max_results": 5})
    assert s.status_code == 200, s.text
    data = s.json()
    assert data["total_results"] >= 1
    # Expect that one of the sources references "Paris"
    texts = " ".join([src.get("text", "") for src in data["sources"]]).lower()
    assert "paris" in texts


