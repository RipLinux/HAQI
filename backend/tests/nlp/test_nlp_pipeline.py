"""Unit and contract integration tests for the Arabic NLP module."""

from app.contracts.query import UserQuery
from app.contracts.retrieval import RetrievalRequest
from app.modules.nlp import process_user_query
from app.modules.nlp.dialect import convert_dialect_to_msa
from app.modules.nlp.normalizer import normalize_arabic_text


def test_normalize_arabic_text_fixes_spelling_and_noise() -> None:
    """Test diacritics removal, elongation cleanup, and common spelling fixes."""
    raw = "ازاي   اطلع بطاقه؟؟؟"
    assert normalize_arabic_text(raw) == "إزاي أطلع بطاقة؟"

    elongated = "عااااايز اجدد البطاقه"
    assert normalize_arabic_text(elongated) == "عايز أجدد البطاقة"


def test_convert_dialect_to_msa_maps_egyptian_terms() -> None:
    """Test Egyptian dialect phrases conversion to formal Arabic."""
    normalized = normalize_arabic_text("ازاي اطلع بطاقه بدل فايد؟")
    msa = convert_dialect_to_msa(normalized)
    assert "بطاقة الرقم القومي" in msa
    assert "بدل فاقد" in msa


def test_process_user_query_complete_question() -> None:
    """Test full NLP pipeline on a clear Egyptian Arabic query."""
    query = UserQuery(text="ازاي اطلع بطاقه؟", language="ar")
    output = process_user_query(query)

    assert output.clarification_needed is False
    assert output.clarification_question is None
    assert output.normalized_query == "إزاي أطلع بطاقة؟"
    assert output.rewritten_query == "ما إجراءات استخراج بطاقة الرقم القومي؟"
    assert output.retrieval_query == "ما إجراءات استخراج بطاقة الرقم القومي؟"
    assert output.intent == "procedures_inquiry"
    assert any(e.text == "بطاقة الرقم القومي" for e in output.entities)


def test_process_user_query_synthetic_benchmark_alignment() -> None:
    """Ensure Egyptian synthetic benchmark queries rewrite to canonical MSA form."""
    query = UserQuery(
        text="عايز أعرف تفاصيل تصريح خدمة في الخدمة التجريبية",
        language="ar_egy",
    )
    output = process_user_query(query)

    assert output.clarification_needed is False
    assert output.retrieval_query == "ما هي معلومات تصريح خدمة في الخدمة التجريبية؟"


def test_process_user_query_ambiguous_requires_clarification() -> None:
    """Ensure incomplete queries trigger clarification and block retrieval_query."""
    query = UserQuery(text="عايز اجددها، اعمل ايه؟", language="ar")
    output = process_user_query(query)

    assert output.clarification_needed is True
    assert output.clarification_question is not None
    assert "تجديد" in output.clarification_question
    assert output.retrieval_query is None


def test_nlp_output_integrates_with_retrieval_request() -> None:
    """Verify that NlpOutput.retrieval_query feeds cleanly into RetrievalRequest.query."""
    user_query = UserQuery(text="ايه الورق المطلوب لاستخراج شهاده الميلاد؟")
    nlp_output = process_user_query(user_query)

    assert not nlp_output.clarification_needed
    assert nlp_output.retrieval_query is not None

    retrieval_req = RetrievalRequest(
        query=nlp_output.retrieval_query,
        original_query=user_query.text,
        retrieval_query=nlp_output.retrieval_query,
        language=user_query.language,
    )
    assert retrieval_req.query == "ما هي المستندات المطلوبة لاستخراج شهادة الميلاد؟"
