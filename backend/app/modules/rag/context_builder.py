
"""Build a deterministic, source-aware context from retrieved chunks."""

from collections.abc import Sequence
from dataclasses import dataclass

from app.contracts.retrieval import RetrievedChunk


@dataclass(frozen=True, slots=True)
class ContextBuildResult:
    """Context text and the exact evidence chunks used to build it."""

    context_text: str
    chunks: tuple[RetrievedChunk, ...]


class ContextBuilder:
    """Prepare ranked retrieval results for grounded answer generation."""

    def __init__(self, max_chunks: int = 8) -> None:
        if max_chunks < 1:
            raise ValueError("max_chunks must be positive")

        self.max_chunks = max_chunks

    def build(self, chunks: Sequence[RetrievedChunk]) -> ContextBuildResult:
        """Filter invalid chunks, remove duplicates, and format evidence."""

        selected: list[RetrievedChunk] = []
        seen_chunk_ids: set[str] = set()

        for chunk in chunks:
            chunk_id = str(chunk.chunk_id)

            if chunk_id in seen_chunk_ids:
                continue

            if not chunk.text or not chunk.text.strip():
                continue

            selected.append(chunk)
            seen_chunk_ids.add(chunk_id)

            if len(selected) >= self.max_chunks:
                break

        context_parts: list[str] = []

        for index, chunk in enumerate(selected, start=1):
            source = chunk.source_url or "Not provided"

            context_parts.append(
                f"[E{index}]\n"
                f"chunk_id: {chunk.chunk_id}\n"
                f"source_url: {source}\n"
                f"content:\n{chunk.text.strip()}"
            )

        return ContextBuildResult(
            context_text="\n\n".join(context_parts),
            chunks=tuple(selected),
        )
