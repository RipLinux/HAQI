"""PostgreSQL full-text search boundary.

The query is passed as a parameter. PostgreSQL's default configuration is not
assumed to provide Arabic stemming; normalized text from the NLP module is accepted.
"""

import re
from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy import text

from app.contracts.retrieval import RetrievalMethod, RetrievedChunk


class PgFullTextSearcher:
    def __init__(
        self, session: Any, *, table: str = "chunks", configuration: str = "simple"
    ) -> None:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table):
            raise ValueError("table must be a simple SQL identifier")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", configuration):
            raise ValueError("configuration must be a simple SQL identifier")
        self.session = session
        self.table = table
        self.configuration = configuration

    async def search(
        self, query: str, top_k: int = 10, filters: Mapping[str, str] | None = None
    ) -> list[RetrievedChunk]:
        if not query.strip():
            return []
        if not 1 <= top_k <= 100:
            raise ValueError("top_k must be between 1 and 100")
        if filters:
            raise NotImplementedError("Metadata filters require the canonical Chunk mapping")
        result = await self.session.execute(
            text(
                f"SELECT id, document_id, text, source_url, "
                f"ts_rank_cd(to_tsvector('{self.configuration}', text), "
                f"plainto_tsquery('{self.configuration}', :query)) AS score "
                f"FROM {self.table} "
                f"WHERE to_tsvector('{self.configuration}', text) @@ "
                f"plainto_tsquery('{self.configuration}', :query) "
                "ORDER BY score DESC, id LIMIT :top_k"
            ),
            {"query": query, "top_k": top_k},
        )
        return [
            RetrievedChunk(
                chunk_id=UUID(str(row[0])),
                document_id=UUID(str(row[1])),
                text=row[2],
                source_url=row[3],
                score=float(row[4]),
                rank=index,
                retrieval_method=RetrievalMethod.KEYWORD,
            )
            for index, row in enumerate(result.all(), start=1)
        ]
