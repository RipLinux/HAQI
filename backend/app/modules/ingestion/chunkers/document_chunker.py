
"""Word-based text chunking with character overlap."""


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[str]:
    """Split text into chunks with a configurable character overlap."""

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap must be smaller")

    words = text.split()

    if not words:
        return []

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    for word in words:
        added_length = len(word) + (1 if current_chunk else 0)

        if current_chunk and current_length + added_length > chunk_size:
            chunks.append(" ".join(current_chunk))

            overlap_words: list[str] = []
            overlap_length = 0

            for old_word in reversed(current_chunk):
                word_length = len(old_word)

                separator_length = 1 if overlap_words else 0
                required_length = word_length + separator_length

                if overlap_length + required_length > overlap:
                    break

                overlap_words.insert(0, old_word)
                overlap_length += required_length

            current_chunk = overlap_words
            current_length = len(" ".join(current_chunk))

        separator_length = 1 if current_chunk else 0
        current_chunk.append(word)
        current_length += len(word) + separator_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
