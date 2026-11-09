from uuid import uuid4

from app.contracts.retrieval import RetrievalMethod, RetrievedChunk
from app.modules.retrieval.hybrid_search.fusion import reciprocal_rank_fusion


def result() -> RetrievedChunk:
    identifier = uuid4()
    return RetrievedChunk(
        chunk_id=identifier,
        document_id=uuid4(),
        text="text",
        retrieval_method=RetrievalMethod.VECTOR,
    )


def test_rrf_deduplicates_and_preserves_the_best_metadata() -> None:
    shared = result()
    other = result()
    fused = reciprocal_rank_fusion([[shared, other], [other, shared]], top_k=2)
    assert len(fused) == 2
    assert {item.chunk_id for item in fused} == {shared.chunk_id, other.chunk_id}
    assert all(item.retrieval_method == RetrievalMethod.HYBRID for item in fused)
    assert [item.rank for item in fused] == [1, 2]


def test_rrf_accepts_empty_sources() -> None:
    assert reciprocal_rank_fusion([[], []]) == []
