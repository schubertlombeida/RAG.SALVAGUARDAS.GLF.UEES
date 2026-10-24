import pytest
from src.evaluate import retrieval_metrics, validate_gold, wilson

def test_hit_recall_mrr_differ():
    result = retrieval_metrics(["wrong", "A", "A"], ["A", "B"])
    assert result == {"hit_at_5": 1, "recall_at_5": .5, "precision_at_5": .2, "mrr_at_5": .5}
    assert retrieval_metrics([], [])["recall_at_5"] is None

def test_wilson_boundaries():
    assert wilson(0, 10)[1] > 0
    assert wilson(10, 10)[0] < 1
    with pytest.raises(ValueError): wilson(1, 0)

def test_reject_unreviewed_or_wrong_version():
    with pytest.raises(ValueError): validate_gold([{"query_id": "1"}], {"A"}, "hash", "test")

def test_valid_unanswerable():
    q = {"query_id": "q1", "query": "Consulta", "theme": "Tema", "reviewer": "Especialista B",
         "question_author": "Autor A", "review_date": "2026-10-26", "review_status": "approved",
         "split": "test", "corpus_sha256": "hash", "relevant_chunk_ids": [],
         "answerable": False, "annotation_note": "No existe el dato en el corpus sintético"}
    validate_gold([q], {"A"}, "hash", "test")
    q["reviewer"] = q["question_author"]
    with pytest.raises(ValueError): validate_gold([q], {"A"}, "hash", "test")
