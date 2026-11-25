"""Adapter for converting legacy HAQI retrieval records to RAG contracts."""

import json
from collections.abc import Mapping
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from app.contracts.retrieval import RetrievalMethod, RetrievedChunk


_CHUNK_NAMESPACE = uuid5(NAMESPACE_URL, "haqi/legacy/chunk")
_DOCUMENT_NAMESPACE = uuid5(NAMESPACE_URL, "haqi/legacy/document")


def _stable_id(namespace: UUID, value: Any, field: str) -> UUID:
    if value is None or not str(value).strip():
        raise ValueError(f"Legacy retrieval record is missing {field}")
    return uuid5(namespace, str(value).strip())


def _metadata_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return str(value)


class LegacyRetrievalAdapter:
    """Convert legacy retrieval dictionaries without changing their source."""

    @staticmethod
    def convert(record: Mapping[str, Any], rank: int) -> RetrievedChunk:
        if rank < 1:
            raise ValueError("rank must be greater than or equal to 1")

        legacy_chunk_id = record.get("chunk_id")
        legacy_document_id = record.get("document_id")
        text = record.get("chunk_text")

        if text is None or not str(text).strip():
            raise ValueError("Legacy retrieval record is missing chunk_text")

        metadata = {
            key: _metadata_value(value)
            for key, value in record.items()
            if key not in {"chunk_text", "original_url"}
        }

        metadata["legacy_chunk_id"] = str(legacy_chunk_id)
        metadata["legacy_document_id"] = str(legacy_document_id)

        return RetrievedChunk(
            chunk_id=_stable_id(_CHUNK_NAMESPACE, legacy_chunk_id, "chunk_id"),
            document_id=_stable_id(
                _DOCUMENT_NAMESPACE, legacy_document_id, "document_id"
            ),
            score=record.get("rerank_score"),
            retrieval_method=RetrievalMethod.RERANKED,
            text=str(text),
            source_url=record.get("original_url") or None,
            rank=rank,
            metadata=metadata,
        )

    @classmethod
    def convert_many(
        cls, records: list[Mapping[str, Any]]
    ) -> list[RetrievedChunk]:
        return [
            cls.convert(record, rank=index)
            for index, record in enumerate(records, start=1)
        ]
