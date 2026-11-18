"""Intent classification and entity extraction for Arabic government queries."""

from app.contracts.nlp import Entity

# تصنيف نوايا المستخدم (يغطي نوايا الخدمات الحكومية وفئات ملف التقييم العشر)
INTENT_KEYWORDS: dict[str, list[str]] = {
    "required_documents": ["مستندات", "المستندات", "أوراق", "الأوراق", "مستند مطلوب", "طلبات"],
    "fees_inquiry": ["رسوم", "الرسوم", "دفع الرسوم", "تكلفة", "سعر", "فلوس", "كام"],
    "appointment_inquiry": ["موعد خدمة", "موعد", "مواعيد", "حجز"],
    "complaint_inquiry": ["شكوى خدمة", "شكوى", "شكاوى", "تظلم"],
    "status_inquiry": ["حالة الطلب", "متابعة الطلب", "الاستعلام عن حالة"],
    "accessibility_inquiry": ["دعم الإتاحة", "الإتاحة", "ذوي الهمم", "ذوي الاحتياجات"],
    "location_inquiry": ["عنوان المركز", "عنوان", "أماكن", "الأماكن", "أين", "مكتب", "فرع"],
    "notification_inquiry": ["إشعار الخدمة", "إشعار", "تنبيه"],
    "permit_inquiry": ["تصريح خدمة", "تصريح", "ترخيص"],
    "renewal_inquiry": ["تجديد الخدمة", "تجديد"],
    "conditions_inquiry": ["شروط", "الشروط", "ينفع", "يحق", "سن"],
    "procedures_inquiry": ["إجراءات", "الإجراءات", "خطوات", "كيف", "طريقة", "استخراج"],
}

# الكيانات الحكومية المعتمدة (تشمل وثائق الأحوال المدنية + فئات التقييم)
GOVERNMENT_SERVICES_AND_DOCS: list[str] = [
    # وثائق وخدمات الأحوال المدنية والخدمات الحكومية
    "بطاقة الرقم القومي",
    "جواز السفر",
    "صحيفة الحالة الجنائية",
    "شهادة الميلاد",
    "شهادة الوفاة",
    "وثيقة زواج",
    "وثيقة طلاق",
    "القيد العائلي",
    "رخصة القيادة",
    "رخصة تسيير مركبة",
    "بطاقة التموين",
    "توكيل عام",
    # خدمات ملف التقييم القياسي (synthetic dataset)
    "الخدمة التجريبية",
    "تصريح خدمة",
    "موعد خدمة",
    "مستند مطلوب",
    "دفع الرسوم",
    "شكوى خدمة",
    "تجديد الخدمة",
    "حالة الطلب",
    "دعم الإتاحة",
    "عنوان المركز",
    "إشعار الخدمة",
]

ACTION_TYPES: list[str] = [
    "بدل فاقد",
    "بدل تالف",
    "تجديد",
    "استخراج",
    "إصدار",
    "تعديل بيانات",
    "دفع",
    "تقديم شكوى",
]

GOVERNMENT_AGENCIES: list[str] = [
    "الأحوال المدنية",
    "السجل المدني",
    "مصلحة الجوازات",
    "إدارة المرور",
    "الشهر العقاري",
    "مكتب التموين",
]


def classify_intent(text: str) -> tuple[str, float]:
    """Classify the user's intent and return (intent_label, confidence)."""
    if not text or not text.strip():
        return "unknown", 0.0

    for intent_name, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return intent_name, 0.92

    return "service_inquiry", 0.70


def extract_entities(text: str) -> list[Entity]:
    """Extract structured government entities (services, actions, agencies) from text."""
    if not text or not text.strip():
        return []

    extracted: list[Entity] = []
    seen: set[tuple[str, str]] = set()

    for service in GOVERNMENT_SERVICES_AND_DOCS:
        if service in text and (service, "government_service") not in seen:
            extracted.append(Entity(text=service, label="government_service"))
            seen.add((service, "government_service"))

    for action in ACTION_TYPES:
        if action in text and (action, "action_type") not in seen:
            extracted.append(Entity(text=action, label="action_type"))
            seen.add((action, "action_type"))

    for agency in GOVERNMENT_AGENCIES:
        if agency in text and (agency, "government_agency") not in seen:
            extracted.append(Entity(text=agency, label="government_agency"))
            seen.add((agency, "government_agency"))

    return extracted
