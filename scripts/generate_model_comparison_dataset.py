"""Generate the reproducible synthetic retrieval model-comparison dataset."""

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
OUT = ROOT / "data" / "evaluation" / "model_comparison"

CATEGORIES = [
    ("permit", "تصريح خدمة", "service permit"),
    ("appointment", "موعد خدمة", "service appointment"),
    ("document", "مستند مطلوب", "required document"),
    ("payment", "دفع الرسوم", "fee payment"),
    ("complaint", "شكوى خدمة", "service complaint"),
    ("renewal", "تجديد الخدمة", "service renewal"),
    ("status", "حالة الطلب", "application status"),
    ("accessibility", "دعم الإتاحة", "accessibility support"),
    ("address", "عنوان المركز", "center address"),
    ("notification", "إشعار الخدمة", "service notification"),
]


def rows() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    chunks: list[dict[str, object]] = []
    queries: list[dict[str, object]] = []
    judgments: list[dict[str, object]] = []
    for index, (category, ar, en) in enumerate(CATEGORIES, start=1):
        primary = f"syn-{index:02d}-1"
        partial = f"syn-{index:02d}-2"
        for variant in range(1, 6):
            chunk_id = f"syn-{index:02d}-{variant}"
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": f"syn-doc-{index:02d}",
                    "text": (
                        f"SYNTHETIC SERVICE RECORD {index}. "
                        f"الفئة: {ar}. هذا النص خيالي للاختبار فقط. "
                        f"Category: {en}. Variant {variant} describes a fictional service."
                    ),
                    "language": "ar_msa" if variant < 3 else "en",
                    "source_identifier": f"synthetic://service/{index}/section/{variant}",
                    "metadata": {"category": category, "review_status": "pending_human_review"},
                }
            )
        variants = [
            ("msa", f"ما هي معلومات {ar} في الخدمة التجريبية؟"),
            ("egy", f"عايز أعرف تفاصيل {ar} في الخدمة التجريبية"),
            ("en", f"How do I use the fictional {en} service?"),
            ("spelling", f"{en} information and service details"),
        ]
        for suffix, (language, text) in enumerate(variants, start=1):
            query_id = f"q-{index:02d}-{suffix}"
            queries.append(
                {
                    "query_id": query_id,
                    "query": text,
                    "language": {"msa": "ar_msa", "egy": "ar_egy", "en": "en", "spelling": "en"}[
                        language
                    ],
                    "category": category,
                    "review_status": "pending_human_review",
                }
            )
            judgments.append(
                {
                    "query_id": query_id,
                    "relevant_chunk_ids": [primary, partial],
                    "relevance": {primary: 2, partial: 1},
                    "review_status": "pending_human_review",
                }
            )
    return chunks, queries, judgments


def write_jsonl(path: Path, values: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(value, ensure_ascii=False) + "\n" for value in values),
        encoding="utf-8",
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    chunks, queries, judgments = rows()
    write_jsonl(OUT / "synthetic_chunks.jsonl", chunks)
    write_jsonl(OUT / "synthetic_queries.jsonl", queries)
    write_jsonl(OUT / "relevance_judgments.jsonl", judgments)
    print(f"Generated {len(chunks)} chunks, {len(queries)} queries, and {len(judgments)} judgments.")


if __name__ == "__main__":
    main()
