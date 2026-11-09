def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
) -> list[str]:


    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size و overlap")

    words = text.split()
    chunks = []

    current_chunk = []
    current_length = 0

    for word in words:
        added_length = len(word) + 1

        if current_chunk and current_length + added_length > chunk_size:
            chunks.append(" ".join(current_chunk))

            overlap_words = []
            overlap_length = 0

            for old_word in reversed(current_chunk):
                if overlap_length + len(old_word) + 1 > overlap:
                    break

                overlap_words.insert(0, old_word)
                overlap_length += len(old_word) + 1

            current_chunk = overlap_words
            current_length = overlap_length

        current_chunk.append(word)
        current_length += added_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks