"""Contratos del progreso real y de los errores seguros, sin invocar modelos externos."""
import json
from uuid import UUID

import pytest
import requests

from app.app import create_app
from src.model import BM25


def events(response):
    return [json.loads(line) for line in response.data.splitlines() if line]


class Remote:
    def __init__(self, rows, status=200):
        self.rows, self.status_code, self.closed = rows, status, False

    def iter_lines(self):
        for row in self.rows:
            yield row if isinstance(row, bytes) else json.dumps(row).encode()

    def close(self):
        self.closed = True


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setenv("GLF_RAG_URL", "https://example.hf.space/api/ask")
    monkeypatch.setenv("GLF_RAG_KEY", "synthetic-test-key")


def test_local_progress_matches_result_and_validation(records):
    client = create_app(BM25(records)).test_client()
    for body in [None, {}, {"query": "   ", "mode": "local"}, {"query": "a"*601, "mode": "rag"}, {"query": "manglar", "mode": "unknown"}]:
        assert client.post("/api/query-stream", json=body).status_code == 400
    response = client.post("/api/query-stream", json={"query": " manglar ", "mode": "local"})
    rows = events(response)
    assert response.headers["Cache-Control"] == "no-store"
    assert [r["type"] for r in rows] == ["stage", "result"]
    result = rows[-1]["result"]
    assert result["query"] == "manglar" and result["generated"] is False
    assert result["results"][0]["chunk_id"] == "TEST::1"
    assert result["model"] == "BM25 local" and result["elapsed_seconds"] >= 0
    assert all(r["request_id"] == str(UUID(result["request_id"])) for r in rows)


def test_remote_stage_model_and_citations_are_preserved(records, configured):
    payload = dict(generated=True, answer="Evidencia [TEST::1]", results=records, sources=[records[0]], model="Qwen/test-provider")
    remote = Remote([
        {"type": "stage", "stage": "generation", "model": "Qwen/test-provider"},
        {"type": "heartbeat"}, {"type": "result", "result": payload},
    ])
    calls = []
    def post(url, **kwargs):
        calls.append((url, kwargs))
        return remote
    rows = events(create_app(BM25(records), post).test_client().post("/api/query-stream", json={"query": "manglar", "mode": "rag"}))
    assert [r.get("stage") for r in rows[:-1]] == ["connecting", "generation"]
    assert rows[-1]["result"]["model"] == "Qwen/test-provider"
    assert rows[-1]["result"]["sources"] == [records[0]]
    assert len(calls) == 1 and calls[0][0].endswith("/api/ask-stream")
    assert calls[0][1]["stream"] and calls[0][1]["allow_redirects"] is False
    assert remote.closed


@pytest.mark.parametrize("status,code", [(429,"quota"),(401,"configuration"),(403,"configuration"),(503,"unavailable")])
def test_remote_http_errors_are_safe(records, configured, status, code):
    remote = Remote([], status)
    response = create_app(BM25(records), lambda *a, **kw: remote).test_client().post("/api/query-stream", json={"query":"manglar","mode":"rag"})
    assert events(response)[-1]["code"] == code and remote.closed
    assert b"synthetic-test-key" not in response.data


@pytest.mark.parametrize("remote_rows", [[], [b"not-json"], [[]], [{"type":"stage","stage":"invented","model":"test"}], [b"x"*220001]])
def test_incomplete_or_malformed_progress_fails_closed(records, configured, remote_rows):
    remote = Remote(remote_rows)
    rows = events(create_app(BM25(records), lambda *a, **kw: remote).test_client().post("/api/query-stream", json={"query":"manglar","mode":"rag"}))
    assert rows[-1]["code"] == "invalid-response" and remote.closed
    assert not any(r["type"] == "result" for r in rows)


def test_configuration_and_timeout_are_distinct(records, configured, monkeypatch):
    def timeout(*args, **kwargs):
        raise requests.Timeout("Private provider detail")
    client = create_app(BM25(records), timeout).test_client()
    response = client.post("/api/query-stream", json={"query":"manglar","mode":"rag"})
    assert events(response)[-1]["code"] == "timeout"
    assert b"Private provider detail" not in response.data
    monkeypatch.setenv("GLF_RAG_URL", "https://untrusted.example/api/ask")
    rows = events(client.post("/api/query-stream", json={"query":"manglar","mode":"rag"}))
    assert len(rows) == 1 and rows[0]["code"] == "configuration"
