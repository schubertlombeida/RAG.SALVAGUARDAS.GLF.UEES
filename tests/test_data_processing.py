import pytest
from src.data_processing import chunk_page, validate_records

def test_chunk_preserves_pages_and_limits():
    rows = chunk_page("manglar " * 500, "GLF_TEST", 7, "Prueba", "https://galapagoslifefund.org.ec/test.pdf")
    assert len(rows) > 1 and all(len(row["text"]) <= 1200 and row["page"] == 7 for row in rows)
    assert len({r["chunk_id"] for r in rows}) == len(rows)

def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_page("x", "D", 1, "x", "https://galapagoslifefund.org.ec/test.pdf", 100, 100)

def test_duplicate_and_untrusted_source(records):
    with pytest.raises(ValueError):
        validate_records(records + [records[0]])
    records[0]["source_url"] = "https://example.com/private.pdf"
    with pytest.raises(ValueError):
        validate_records(records)
