import pytest

from app.contracts.retrieval import RetrievalMethod
from app.modules.retrieval.legacy_adapter import LegacyRetrievalAdapter


@pytest.fixture
def legacy_record():
    return {
        "id": 12,
        "chunk_id": "legacy-chunk-12",
        "document_id": 4,
        "chunk_text": "خطوات استخراج الخدمة",
        "original_url": "https://example.gov.eg/service",
        "doc_code": "DOC-01",
        "doc_title": "دليل الخدمات",
        "authority": "Government",
        "service_slug": "service-a",
        "intent_tag": "inquiry",
        "rerank_score": 0.91,
        "steps": ["الخطوة الأولى", "الخطوة الثانية"],
    }


def test_converts_legacy_record_and_preserves_metadata(legacy_record):
    result = LegacyRetrievalAdapter.convert(legacy_record, rank=1)

    assert result.text == legacy_record["chunk_text"]
    assert result.source_url == legacy_record["original_url"]
    assert result.score == pytest.approx(0.91)
    assert result.rank == 1
    assert result.retrieval_method == RetrievalMethod.RERANKED
    assert result.metadata["legacy_chunk_id"] == "legacy-chunk-12"
    assert result.metadata["legacy_document_id"] == "4"
    assert result.metadata["doc_code"] == "DOC-01"
    assert "الخطوة الأولى" in result.metadata["steps"]


def test_ids_are_stable(legacy_record):
    first = LegacyRetrievalAdapter.convert(legacy_record, rank=1)
    second = LegacyRetrievalAdapter.convert(legacy_record, rank=2)

    assert first.chunk_id == second.chunk_id
    assert first.document_id == second.document_id


def test_different_documents_have_different_ids(legacy_record):
    first = LegacyRetrievalAdapter.convert(legacy_record, rank=1)
    legacy_record["document_id"] = 5
    second = LegacyRetrievalAdapter.convert(legacy_record, rank=1)

    assert first.document_id != second.document_id


@pytest.mark.parametrize(
    ("field", "value"),
    [("chunk_id", None), ("document_id", None), ("chunk_text", "")],
)
def test_rejects_missing_required_values(legacy_record, field, value):
    legacy_record[field] = value

    with pytest.raises(ValueError):
        LegacyRetrievalAdapter.convert(legacy_record, rank=1)


def test_convert_many_preserves_order_and_assigns_rank(legacy_record):
    second = {**legacy_record, "chunk_id": "legacy-chunk-13"}

    results = LegacyRetrievalAdapter.convert_many([legacy_record, second])

    assert [item.rank for item in results] == [1, 2]
    assert results[0].chunk_id != results[1].chunk_id
