import fitz
from pathlib import Path


def extract_pdf(file_path: str) -> list[dict]:
    path = Path(file_path)
    pages = []

    with fitz.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text", sort=True)

            if text.strip():
                pages.append({
                    "page_number": page_number,
                    "text": text.strip()
                })

    return pages