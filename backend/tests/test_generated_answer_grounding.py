import pytest

from app.services.evidence_validator import evidence_validator


@pytest.fixture
def source_chunk():
    return {
        "service_name_ar": "تجديد بطاقة الرقم القومي",
        "chunk_text": "تجديد بطاقة الرقم القومي يتطلب تقديم البطاقة السابقة.",
        "authority": "قطاع الأحوال المدنية",
        "fees_text": "الرسوم 50 جنيه",
        "processing_time": "مدة الإجراء 7 أيام",
        "steps": ["تقديم الطلب"],
        "required_documents": ["البطاقة السابقة"],
    }


def test_accepts_answer_supported_by_source(source_chunk):
    answer = "تجديد بطاقة الرقم القومي يتطلب البطاقة السابقة، والرسوم 50 جنيه."

    assert evidence_validator.validate_generated_answer(
        source_chunk, answer
    ) is True


def test_rejects_unsupported_fee_and_duration(source_chunk):
    answer = (
        "تجديد بطاقة الرقم القومي يتطلب البطاقة السابقة، "
        "والرسوم 999 جنيه، ومدة الإجراء 30 يوم."
    )

    assert evidence_validator.validate_generated_answer(
        source_chunk, answer
    ) is False


def test_rejects_empty_answer(source_chunk):
    assert evidence_validator.validate_generated_answer(
        source_chunk, ""
    ) is False


def test_ignores_evidence_reference_marker(source_chunk):
    answer = "تجديد بطاقة الرقم القومي يتطلب البطاقة السابقة [E1]."

    assert evidence_validator.validate_generated_answer(
        source_chunk, answer
    ) is True


def test_rejects_unsupported_fee_alone(source_chunk):
    answer = (
        "تجديد بطاقة الرقم القومي يتطلب البطاقة السابقة، "
        "والرسوم 999 جنيه."
    )

    assert evidence_validator.validate_generated_answer(
        source_chunk, answer
    ) is False


def test_rejects_unsupported_duration_alone(source_chunk):
    answer = (
        "تجديد بطاقة الرقم القومي يتطلب البطاقة السابقة، "
        "ومدة الإجراء 30 يوم."
    )

    assert evidence_validator.validate_generated_answer(
        source_chunk, answer
    ) is False


def test_accepts_fee_with_unrelated_number_after_comma(source_chunk):
    fee = "\u0627\u0644\u0631\u0633\u0648\u0645"
    steps = "\u0639\u062f\u062f \u0627\u0644\u062e\u0637\u0648\u0627\u062a"
    comma = "\u060c"
    answer = (
        source_chunk["service_name_ar"] + " "
        + fee + " 50 \u062c\u0646\u064a\u0647"
        + comma + steps + " 5"
    )

    assert evidence_validator.validate_generated_answer(
        source_chunk, answer
    ) is True


def test_accepts_duration_with_unrelated_number_after_comma(source_chunk):
    duration = "\u0645\u062f\u0629 \u0627\u0644\u0625\u062c\u0631\u0627\u0621"
    service_number = "\u0631\u0642\u0645 \u0627\u0644\u062e\u062f\u0645\u0629"
    comma = "\u060c"
    answer = (
        source_chunk["service_name_ar"] + " "
        + duration + " 7 \u0623\u064a\u0627\u0645"
        + comma + service_number + " 123"
    )

    assert evidence_validator.validate_generated_answer(
        source_chunk, answer
    ) is True
