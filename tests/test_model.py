import numpy as np
import pytest
from src.model import BM25, E5Endpoint

def test_retrieval_and_unmatched_query(records):
    index = BM25(records)
    assert index.search("restauracion manglar")[0]["chunk_id"] == "TEST::1"
    assert index.search("zxqvfrt") == []

def test_bad_parameters(records):
    with pytest.raises(ValueError):
        BM25(records, b=2)

def test_e5_rejects_dimensions_and_model(records):
    class Response:
        def raise_for_status(self): pass
        def json(self): return {"model": "intfloat/multilingual-e5-small", "embeddings": [[1, 2]] * 2}
    with pytest.raises(ValueError, match="Embeddings"):
        E5Endpoint(records, "https://example.hf.space/embed", transport=lambda *a, **k: Response())

def test_e5_contract_normalization(records):
    class Response:
        def __init__(self, n): self.n = n
        def raise_for_status(self): pass
        def json(self): return {"model": "intfloat/multilingual-e5-small", "embeddings": [[2.] * 384 for _ in range(self.n)]}
    index = E5Endpoint(records, "https://example.hf.space/embed",
                       transport=lambda *a, **k: Response(len(k["json"]["inputs"])))
    assert np.allclose(np.linalg.norm(index.vectors, axis=1), 1)
    assert len(index.search("manglar")) == 2

def test_e5_obeys_server_batch_limit(records):
    calls = []
    class Response:
        def __init__(self, n): self.n = n
        def raise_for_status(self): pass
        def json(self): return {"model": "intfloat/multilingual-e5-small", "embeddings": [[1.] * 384 for _ in range(self.n)]}
    def transport(*args, **kwargs):
        count = len(kwargs["json"]["inputs"])
        assert count <= 8
        calls.append(count)
        return Response(count)
    many = [dict(records[0], chunk_id=f"TEST::{i}") for i in range(17)]
    E5Endpoint(many, "https://example.hf.space/embed", transport=transport)
    assert calls == [8, 8, 1]
