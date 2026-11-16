
import pytest

from app.modules.ingestion.chunkers.document_chunker import chunk_text


def test_chunk_text_splits_text_with_overlap():
    result = chunk_text(
        "one two three four five six",
        chunk_size=12,
        overlap=4,
    )

    assert result == [
        "one two",
        "two three",
        "four five",
        "five six",
    ]


def test_chunk_text_returns_empty_list_for_empty_input():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_handles_single_word():
    assert chunk_text("hello", chunk_size=12, overlap=0) == ["hello"]


def test_chunk_text_handles_zero_overlap():
    result = chunk_text(
        "one two three four",
        chunk_size=8,
        overlap=0,
    )

    assert result == ["one two", "three", "four"]


def test_chunk_text_supports_arabic():
    result = chunk_text(
        "مرحبا بك في نظام حقي للمساعدات الحكومية",
        chunk_size=15,
        overlap=5,
    )

    assert result == [
        "مرحبا بك في",
        "بك في نظام حقي",
        "حقي للمساعدات",
        "الحكومية",
    ]


def test_chunk_text_keeps_words_longer_than_chunk_size():
    result = chunk_text(
        "abcdefghijklmno test",
        chunk_size=10,
        overlap=2,
    )

    assert result == ["abcdefghijklmno", "test"]


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [
        (0, 0),
        (-1, 0),
        (10, -1),
        (10, 10),
        (10, 11),
    ],
)
def test_chunk_text_rejects_invalid_configuration(chunk_size, overlap):
    with pytest.raises(ValueError):
        chunk_text("some sample text", chunk_size, overlap)


def test_chunk_text_respects_chunk_size_for_normal_words():
    result = chunk_text(
        "one two three four five six seven eight",
        chunk_size=12,
        overlap=3,
    )

    assert all(len(chunk) <= 12 for chunk in result)
