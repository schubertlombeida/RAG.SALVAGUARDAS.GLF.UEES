"""Synthetic fixtures test software, not the measured quality of GLF answers."""
from copy import deepcopy
import pytest
from app.app import validate_remote, create_app
from src.model import BM25, HeadingBM25, HybridRRF
from src.optimize import optimize, save_report
from src.answer_evaluation import summarize_answers


def label(records, split, query_id, query):
    return dict(query_id=query_id,query=query,theme="test",reviewer="specialist",review_date="2026-10-24",question_author="author",review_status="approved",split=split,corpus_sha256="test-hash",relevant_chunk_ids=[records[0]["chunk_id"]],answerable=True,annotation_note="Synthetic fixture only")


def test_hybrid_requires_same_content_and_preserves_sources(records):
    lexical=BM25(records);semantic=BM25(records)
    rows=HybridRRF(lexical,semantic).search("manglar")
    assert rows[0]["chunk_id"]==records[0]["chunk_id"]
    changed=deepcopy(records);changed[0]["text"]+=" otro contenido"
    with pytest.raises(ValueError): HybridRRF(lexical,BM25(changed))
    assert HeadingBM25(records,heading_weight=0).search("manglar")[0]["text"]==rows[0]["text"]


def test_optimization_is_reproducible_validated_and_never_touches_test(records,tmp_path):
    dev=[label(records,"development","d1","manglar")]
    val=[label(records,"validation","v1","ecosistema manglar")]
    result=optimize(records,dev,val,"test-hash")
    assert len(result["runs"])==12 and not result["test_used"]
    assert result==optimize(records,dev,val,"test-hash")
    output=tmp_path/"run";save_report(result,output)
    assert (output/"interaction.png").stat().st_size>1000
    with pytest.raises(ValueError): save_report(result,output)
    val[0]["split"]="test"
    with pytest.raises(ValueError): optimize(records,dev,val,"test-hash")
    val[0]["split"]="validation";val[0]["query"]="manglar"
    with pytest.raises(ValueError): optimize(records,dev,val,"test-hash")


def test_answer_metrics_need_human_review_and_separate_abstention(records):
    labels=[label(records,"test","q1","manglar"),dict(label(records,"test","q2","no contestable"),answerable=False,relevant_chunk_ids=[])]
    runs=[dict(configuration="brief",query_id=q["query_id"],corpus_sha256="test-hash",generated=q["answerable"]) for q in labels]
    reviews=[dict(configuration="brief",query_id=q["query_id"],reviewer="specialist",review_date="2026-10-24",review_status="approved",claims_total=2 if q["answerable"] else 0,claims_supported=1 if q["answerable"] else 0,answer_adequate=True,review_note="synthetic",manual_seconds=20,assisted_seconds=12) for q in labels]
    report=summarize_answers(labels,runs,reviews,"test-hash",{r["chunk_id"] for r in records})
    summary=report["configurations"]["brief"]
    assert summary["claim_support_fraction"]==.5 and summary["correct_abstentions"]==1
    assert summary["wrong_abstentions"]==0 and summary["median_paired_saving_seconds"]==8
    reviews[0]["manual_seconds"]=float("nan")
    with pytest.raises(ValueError): summarize_answers(labels,runs,reviews,"test-hash",{r["chunk_id"] for r in records})
    reviews[0]["manual_seconds"]=20
    reviews[0]["reviewer"]="author"
    with pytest.raises(ValueError): summarize_answers(labels,runs,reviews,"test-hash",{r["chunk_id"] for r in records})


def test_remote_accepts_actual_service_citations_without_duplicated_text(records):
    source={k:v for k,v in records[0].items() if k!="text"}
    payload=dict(generated=True,answer=f"Evidencia [{source['chunk_id']}]",sources=[source],results=records)
    assert validate_remote(payload)["generated"]
    payload["results"][0]=dict(records[0],text=None)
    with pytest.raises(ValueError): validate_remote(payload)


def test_answer_mode_is_validated_before_provider_call(records):
    client=create_app(BM25(records),lambda *args,**kwargs: pytest.fail("Must not call provider")).test_client()
    for endpoint in ("/api/query","/api/query-stream"):
        assert client.post(endpoint,json={"mode":"rag","query":"manglar","answer_mode":"unlimited"}).status_code==400
