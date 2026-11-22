"""Arabic text normalization and common spelling correction."""

import re

# علامات التشكيل العربية (فتحة، ضمة، كسرة، سكون، شدة، تنوين)
ARABIC_DIACRITICS = re.compile(r"[\u064B-\u065F\u0670]")

# قاموس تصحيح الأخطاء الإملائية الشائعة في الكلمات الحكومية والعامية
COMMON_SPELLING_FIXES: dict[str, str] = {
    "بطاقه": "بطاقة",
    "البطاقه": "البطاقة",
    "رخصه": "رخصة",
    "الرخصه": "الرخصة",
    "شهاده": "شهادة",
    "الشهاده": "الشهادة",
    "وثيقه": "وثيقة",
    "الوثيقه": "الوثيقة",
    "صحيفه": "صحيفة",
    "الصحيفه": "الصحيفة",
    "خدمه": "خدمة",
    "الخدمه": "الخدمة",
    "تجريبيه": "تجريبية",
    "التجريبيه": "التجريبية",
    "مدنيه": "مدنية",
    "المدنيه": "المدنية",
    "جنائيه": "جنائية",
    "الجنائيه": "الجنائية",
    "حكوميه": "حكومية",
    "الحكوميه": "الحكومية",
    "مطلوبه": "مطلوبة",
    "المطلوبه": "المطلوبة",
    "شكوي": "شكوى",
    "الشكوي": "الشكوى",
    "مستشفي": "مستشفى",
    "المستشفي": "المستشفى",
    "اجراءات": "إجراءات",
    "الاجراءات": "الإجراءات",
    "اوراق": "أوراق",
    "الاوراق": "الأوراق",
    "اماكن": "أماكن",
    "الاماكن": "الأماكن",
    "اشعار": "إشعار",
    "الاشعار": "الإشعار",
    "اتاحه": "إتاحة",
    "الاتاحه": "الإتاحة",
    "إستخراج": "استخراج",
    "اعرف": "أعرف",
    "اعمل": "أعمل",
    "ازاي": "إزاي",
    "ايه": "إيه",
    "اجدد": "أجدد",
    "اجددها": "أجددها",
    "اطلع": "أطلع",
    "اطلعها": "أطلعها",
}


def normalize_arabic_text(text: str) -> str:
    """Normalize Arabic text and fix common spelling variations."""
    if not text or not text.strip():
        return ""

    # 1. إزالة التشكيل والتطويل (الكشيدة)
    cleaned = ARABIC_DIACRITICS.sub("", text)
    cleaned = cleaned.replace("ـ", "")

    # 2. تقليل الحروف المكررة 3 مرات فأكثر إلى حرف واحد (مثل: عاااايز -> عايز)
    cleaned = re.sub(r"(.)\1{2,}", r"\1", cleaned)

    # 3. توحيد علامة الاستفهام وإزالة علامات الترقيم العربية والإنجليزية غير الضرورية
    cleaned = cleaned.replace("?", "؟")
    cleaned = re.sub(r"[،؛,!.:;\"'()\[\]{}\-_/\\]+", " ", cleaned)
    cleaned = re.sub(r"[^\w\s\u0621-\u064A؟]", " ", cleaned)

    # 4. توحيد المسافات وضبط علامة الاستفهام
    cleaned = re.sub(r"\s*؟+\s*", "؟ ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # 5. تصحيح الكلمات الشائعة مع الحفاظ على علامة الاستفهام في آخر الكلمة
    words = cleaned.split()
    corrected_words: list[str] = []
    for word in words:
        has_question_mark = word.endswith("؟")
        bare_word = word[:-1] if has_question_mark else word
        fixed_word = COMMON_SPELLING_FIXES.get(bare_word, bare_word)
        corrected_words.append(f"{fixed_word}؟" if has_question_mark else fixed_word)

    return " ".join(corrected_words)
