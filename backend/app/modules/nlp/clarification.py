"""Clarification detection for incomplete or ambiguous Arabic queries."""

from app.contracts.nlp import Entity


def check_clarification_needed(
    intent: str,
    entities: list[Entity],
    normalized_text: str,
) -> tuple[bool, str | None]:
    """Determine if the user query requires clarification before retrieval."""
    words = normalized_text.replace("؟", "").split()
    if len(words) < 2:
        return (
            True,
            "من فضلك وضّح سؤالك أكثر؛ ما هي الخدمة أو الوثيقة الحكومية التي تستفسر عنها؟",
        )

    has_target_service = any(
        entity.label in ("government_service", "government_agency") for entity in entities
    )

    if not has_target_service:
        actions = [e.text for e in entities if e.label == "action_type"]
        if "تجديد" in actions:
            return (
                True,
                "ما هي الوثيقة أو الخدمة التي تريد تجديدها؟ (مثل: بطاقة الرقم القومي، جواز السفر، أو رخصة القيادة)",
            )
        if any(act in actions for act in ("استخراج", "بدل فاقد", "بدل تالف")):
            return (
                True,
                "ما هي الوثيقة التي تريد استخراجها؟ (مثل: بطاقة الرقم القومي، شهادة الميلاد، أو صحيفة الحالة الجنائية)",
            )
        if intent == "required_documents":
            return (
                True,
                "ما هي الخدمة أو الوثيقة التي تسأل عن مستنداتها المطلوبة؟",
            )
        if intent == "fees_inquiry":
            return (
                True,
                "ما هي الخدمة أو الوثيقة التي تسأل عن رسومها؟",
            )
        return (
            True,
            "من فضلك حدد اسم الوثيقة أو الخدمة الحكومية التي تستفسر عنها (مثل: بطاقة الرقم القومي أو جواز السفر).",
        )

    return False, None
