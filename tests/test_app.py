from app.app import create_app, validate_remote
from src.model import BM25
import pytest

def test_app_query_validation_and_output(records):
    client = create_app(BM25(records)).test_client()
    assert client.get("/").status_code == 200
    for body in [{}, {"query": "a"}, {"query": "a" * 601}, {"query": 100}]:
        assert client.post("/api/query", json=body).status_code == 400
    result = client.post("/api/query", json={"query": "manglar"})
    assert result.status_code == 200 and result.json["generated"] is False
    assert result.json["results"][0]["chunk_id"] == "TEST::1"

def test_remote_missing_configuration(records, monkeypatch):
    monkeypatch.delenv("GLF_RAG_URL", raising=False)
    client = create_app(BM25(records)).test_client()
    assert client.post("/api/query", json={"query": "manglar", "mode": "rag"}).status_code == 503

def test_remote_citation_inconsistency(records):
    with pytest.raises(ValueError): validate_remote({"generated": True, "answer": "Sin citas", "sources": [], "results": []})
    with pytest.raises(ValueError): validate_remote({"generated": False, "answer": "No sé", "sources": [records[0]], "results": records})

def test_remote_rejects_unlisted_citation(records):
    body = {"generated": True, "answer": "Evidencia [TEST::1] y otra [INVENTADA::9]",
            "sources": [records[0]], "results": records}
    with pytest.raises(ValueError, match="referencias no verificadas"):
        validate_remote(body)
    body["answer"] = "Evidencia [TEST::1]"
    assert validate_remote(body)["generated"] is True
