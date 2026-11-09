import json
from pathlib import Path

from .chunkers.document_chunker import chunk_text
from .cleaners.arabic_cleaner import clean_arabic_text
from .extractors.html_extractor import extract_html
from .extractors.pdf_extractor import extract_pdf
from .metadata.metadata_builder import build_chunk_metadata

# تحديد مكان المشروع
PROJECT_ROOT = Path(__file__).resolve().parents[4]

# مسارات البيانات
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PDF_DIR = RAW_DIR / "pdf"
HTML_DIR = RAW_DIR / "html"

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_category(file_path: Path, base_dir: Path) -> str:
    """
    تحديد نوع الملف حسب المجلد الموجود بداخله.
    """

    relative_parts = [
        part.lower()
        for part in file_path.relative_to(base_dir).parts
    ]

    if "legislation and civil status" in relative_parts:
        return "legislation_and_civil_status"

    if "services" in relative_parts:
        return "services"

    return "other"


def process_pdf_files(output):
    total_chunks = 0

    if not PDF_DIR.exists():
        print("PDF folder not found!")
        return total_chunks

    pdf_files = list(PDF_DIR.rglob("*.pdf"))

    print(f"\nFound {len(pdf_files)} PDF files.")

    for pdf_file in pdf_files:

        category = get_category(pdf_file, PDF_DIR)

        print(f"\nProcessing PDF: {pdf_file.name}")
        print(f"Category: {category}")

        try:
            pages = extract_pdf(str(pdf_file))

            if not pages:
                print("Warning: No text extracted from this PDF.")
                continue

            for page in pages:

                cleaned_text = clean_arabic_text(page["text"])

                if not cleaned_text:
                    continue

                chunks = chunk_text(cleaned_text)

                for index, chunk in enumerate(chunks):

                    metadata = build_chunk_metadata(
                        file_path=str(pdf_file),
                        title=pdf_file.stem,
                        source_type="pdf",
                        category=category,
                        chunk_index=index,
                        page_number=page["page_number"],
                    )

                    record = {
                        "text": chunk,
                        "metadata": metadata
                    }

                    output.write(
                        json.dumps(record, ensure_ascii=False) + "\n"
                    )

                    total_chunks += 1

        except Exception as error:
            print(f"Error processing {pdf_file.name}: {error}")

    return total_chunks


def process_html_files(output):
    total_chunks = 0

    if not HTML_DIR.exists():
        print("HTML folder not found!")
        return total_chunks

    html_files = list(HTML_DIR.rglob("*.html"))
    html_files += list(HTML_DIR.rglob("*.htm"))

    print(f"\nFound {len(html_files)} HTML files.")

    for html_file in html_files:

        category = get_category(html_file, HTML_DIR)

        print(f"\nProcessing HTML: {html_file.name}")
        print(f"Category: {category}")

        try:
            document = extract_html(str(html_file))

            cleaned_text = clean_arabic_text(document["text"])

            if not cleaned_text:
                print("Warning: No text extracted from this HTML.")
                continue

            chunks = chunk_text(cleaned_text)

            for index, chunk in enumerate(chunks):

                metadata = build_chunk_metadata(
                    file_path=str(html_file),
                    title=document["title"],
                    source_type="html",
                    category=category,
                    chunk_index=index,
                )

                record = {
                    "text": chunk,
                    "metadata": metadata
                }

                output.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

                total_chunks += 1

        except Exception as error:
            print(f"Error processing {html_file.name}: {error}")

    return total_chunks


def process_documents():

    output_file = OUTPUT_DIR / "chunks.jsonl"

    print("Starting document processing...")

    with output_file.open("w", encoding="utf-8") as output:

        pdf_chunks = process_pdf_files(output)
        html_chunks = process_html_files(output)

    total_chunks = pdf_chunks + html_chunks

    print("\nProcessing completed!")
    print(f"PDF chunks: {pdf_chunks}")
    print(f"HTML chunks: {html_chunks}")
    print(f"Total chunks: {total_chunks}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    process_documents()