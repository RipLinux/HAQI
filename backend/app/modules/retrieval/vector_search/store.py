"""Database integration boundary for pgvector.

The table and column names are provisional until Maha's canonical ORM mapping is
available. The adapter accepts an existing SQLAlchemy session and does not create
an engine or ORM model.
"""

import re
from collections.abc import Mapping, Sequence
from typing import Any, Protocol
from uuid import UUID

from sqlalchemy import text

from app.contracts.retrieval import RetrievalMethod, RetrievedChunk

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class VectorStore(Protocol):
    async def add_embeddings(self, rows: Sequence[Mapping[str, Any]]) -> None: ...

    async def search(
        self, vector: Sequence[float], top_k: int, filters: Mapping[str, str] | None = None
    ) -> list[RetrievedChunk]: ...


def validate_vector(vector: Sequence[float], expected_dimension: int) -> list[float]:
    values = list(vector)
    if len(values) != expected_dimension:
        raise ValueError(
            f"Vector dimension mismatch: expected {expected_dimension}, got {len(values)}"
        )
    if not values or any(not isinstance(value, (int, float)) for value in values):
        raise ValueError("Vector must contain numeric values")
    return [float(value) for value in values]


def _vector_literal(vector: Sequence[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in vector) + "]"


class PgVectorStore:
    """Minimal parameterized adapter for a future shared Chunk table."""

    def __init__(
        self,
        session: Any,
        *,
        table: str = "chunks",
        dimension: int,
        chunk_id_column: str = "id",
        document_id_column: str = "document_id",
        text_column: str = "text",
        embedding_column: str = "embedding",
        source_url_column: str = "source_url",
    ) -> None:
        identifiers = (
            table,
            chunk_id_column,
            document_id_column,
            text_column,
            embedding_column,
            source_url_column,
        )
        if any(not _IDENTIFIER.fullmatch(identifier) for identifier in identifiers):
            raise ValueError("Table and column names must be simple SQL identifiers")
        self.session = session
        self.table = table
        self.dimension = dimension
        self.chunk_id_column = chunk_id_column
        self.document_id_column = document_id_column
        self.text_column = text_column
        self.embedding_column = embedding_column
        self.source_url_column = source_url_column

    async def add_embeddings(self, rows: Sequence[Mapping[str, Any]]) -> None:
        for row in rows:
            vector = validate_vector(row["embedding"], self.dimension)
            await self.session.execute(
                text(
                    f"INSERT INTO {self.table} "
                    f"({self.chunk_id_column}, {self.document_id_column}, "
                    f"{self.text_column}, {self.embedding_column}, {self.source_url_column}) "
                    "VALUES (:chunk_id, :document_id, :chunk_text, CAST(:embedding AS vector), :source_url)"
                ),
                {
                    "chunk_id": row["chunk_id"],
                    "document_id": row["document_id"],
                    "chunk_text": row["text"],
                    "embedding": _vector_literal(vector),
                    "source_url": row.get("source_url"),
                },
            )
        await self.session.commit()

    async def search(
        self, vector: Sequence[float], top_k: int, filters: Mapping[str, str] | None = None
    ) -> list[RetrievedChunk]:
        if top_k < 1:
            raise ValueError("top_k must be positive")
        vector = validate_vector(vector, self.dimension)
        # Metadata filters are intentionally deferred until Maha confirms columns.
        if filters:
            raise NotImplementedError("Metadata filters require the canonical Chunk mapping")
        result = await self.session.execute(
            text(
                f"SELECT {self.chunk_id_column}, {self.document_id_column}, "
                f"{self.text_column}, {self.source_url_column}, "
                f"1 - ({self.embedding_column} <=> CAST(:embedding AS vector)) AS score "
                f"FROM {self.table} ORDER BY {self.embedding_column} <=> CAST(:embedding AS vector) "
                "LIMIT :top_k"
            ),
            {"embedding": _vector_literal(vector), "top_k": top_k},
        )
        return [
            RetrievedChunk(
                chunk_id=UUID(str(row[0])),
                document_id=UUID(str(row[1])),
                text=row[2],
                source_url=row[3],
                score=float(row[4]),
                rank=index,
                retrieval_method=RetrievalMethod.VECTOR,
            )
            for index, row in enumerate(result.all(), start=1)
        ]
