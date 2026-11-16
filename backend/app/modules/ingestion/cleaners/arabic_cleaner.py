
import re


def clean_arabic_text(text: str) -> str:
    """Clean whitespace and punctuation in Arabic and English text."""

    if not text:
        return ""

    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"\s+([،؛:,.!?؟])", r"\1", text)

    return text.strip()
