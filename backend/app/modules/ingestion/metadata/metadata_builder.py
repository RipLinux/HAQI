from pathlib import Path
from uuid import uuid4


def build_chunk_metadata(
    file_path: str,
    title: str,
    source_type: str,
    chunk_index: int,
    category: str,
    page_number: int | None = None,
    source_url: str | None = None,
) -> dict:

    path = Path(file_path)

    return {
        "document_id": path.stem,
        "chunk_id": str(uuid4()),
        "title": title,
        "file_name": path.name,
        "source_type": source_type,
        "category": category,
        "source_url": source_url,
        "chunk_index": chunk_index,
        "page_number": page_number,
    }