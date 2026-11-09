from app.modules.retrieval.reranking.reranker import NoOpReranker


def test_noop_reranker_is_explicit_and_handles_empty_candidates() -> None:
    reranker = NoOpReranker()
    assert reranker.identifier == "none"
    assert reranker.rerank("query", []) == []
