# HAQI API Contract — للواجهة (هبة)

- **Base URL (محليًا):** `http://localhost:8000`
- **Swagger:** `http://localhost:8000/docs` — **OpenAPI JSON:** `http://localhost:8000/openapi.json`
  (تقدري تولّدي TypeScript Types منه: `npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts`)
- **CORS:** مفتوح لكل الأصول في مرحلة التطوير.
- **الأخطاء:** `{"detail": "..."}` مع كود 400 (سؤال فاضي) أو 404 (مش موجود) أو 422 (Request غلط).
- كل الأمثلة تحت **توضيحية للشكل** والنصوص الحقيقية بتيجي من الـ Backend.

> ⚠️ أسماء الـ endpoints والـ status هنا هي **الحالية في الكود**. لو الفريق اتفق على أسماء تانية (مثلًا `/chat/ask`) هنحدّث الملف ده ونبلّغك.

## الـ Endpoints

| # | Method | Path | الاستخدام في الواجهة |
|---|---|---|---|
| 1 | GET | `/api/v1/health` | فحص إن الـ Backend شغال |
| 2 | POST | `/api/v1/chat` | **المساعد الذكي** |
| 3 | POST | `/api/v1/sessions` | إنشاء/استرجاع جلسة |
| 4 | GET | `/api/v1/sessions/{session_id}` | سجل المحادثة |
| 5 | DELETE | `/api/v1/sessions/{session_id}` | حذف المحادثة (الخصوصية) |
| 6 | GET | `/api/v1/services?category=` | **عرض الخدمات** |
| 7 | GET | `/api/v1/services/{service_slug}?sub_type=` | **تفاصيل خدمة** |
| 8 | POST | `/api/v1/services/{service_slug}/check-eligibility` | **فحص المستندات والأهلية** |
| 9 | GET | `/api/v1/documents?category=` | المصادر الرسمية |
| 10 | POST | `/api/v1/feedback` | تقييم المستخدم للإجابة |

(الباقي — `validate`, `contradictions`, `evaluation/*`, `POST /documents` — للإدارة والتقييم، مش للمواطن.)

---

## 2) POST `/api/v1/chat`

**Request**
```json
{
  "question": "عايز أعرف الأوراق المطلوبة عشان أطلع بطاقة رقم قومي",
  "user_id": "guest_user",
  "session_id": null,
  "service_category": null
}
```
- `question` إجباري. الباقي اختياري.
- **المحادثة متعددة الأدوار:** خدي `session_id` من الـ response وابعتيه في الرسالة اللي بعدها.
  لو الرد كان `clarification_needed` والمستخدم اختار (مثلًا "تجديد")، ابعتي اختياره كـ `question` جديد بنفس الـ `session_id`.

**Response** (الشكل)
```json
{
  "status": "success",
  "session_id": "…",
  "user_id": "guest_user",
  "received_question": "…",
  "decision_type": "answered",
  "answer": "نص الإجابة بالعربي",
  "structured_guidance": {
    "specific_service": "…",
    "procedural_steps": ["…", "…"],
    "required_documents": ["…"],
    "responsible_authority": "…",
    "fees_and_duration": "…",
    "reference_and_verification": "…",
    "methodological_note": "…"
  },
  "clarification_question": null,
  "clarification_options": [],
  "sources": ["…"],
  "citations": [
    {
      "doc_code": "…", "title": "…", "authority": "…",
      "original_url": "https://…", "last_updated": "…",
      "verification_date": "…", "version": "1.0",
      "verification_status": "موثق رسمياً (Verified Official Source)",
      "relevance_score": 0.87
    }
  ],
  "nlp_analysis": { "…": "للتصحيح فقط، مش لازم تعرضيه" },
  "evidence_validation": { "is_sufficient": true, "decision_path": "path_1_verified_context", "…": "…" },
  "metrics": {}
}
```

### قواعد العرض حسب `decision_type`
| القيمة | تعرضي إيه |
|---|---|
| `answered` | `answer` + `structured_guidance` (خطوات، مستندات، جهة، رسوم) + `citations` كبطاقات مصادر |
| `clarification_needed` | `clarification_question` + أزرار من `clarification_options` |
| `safe_abstention` | `answer` (رسالة الامتناع) بتصميم مختلف + بدون خطوات. وما تعرضيش مصادر لو `citations` فاضية |

- `structured_guidance` و`citations` ممكن يبقوا فاضيين/`null` → اتعاملي معاهم كاختياريين.
- `evidence_validation.abstention_reason` ممكن يتعرض كسبب الامتناع.

---

## 6) GET `/api/v1/services?category=`
```json
{
  "status": "success",
  "count": 8,
  "services": [
    {
      "chunk_id": "…", "service_slug": "national-id",
      "service_name_ar": "…", "sub_type": "first_time",
      "service_category": "…", "authority": "…",
      "steps": ["…"], "required_documents": ["…"],
      "eligibility_criteria": ["…"], "fees_text": "…",
      "processing_time": "…", "source_url": "https://…",
      "last_updated": "…", "verification_date": "…"
    }
  ]
}
```
كل عنصر = إجراء واحد (خدمة + نوع فرعي). لو عايزة تجمّعي حسب الخدمة استخدمي `service_slug`.

الـ slugs الموجودة حاليًا: `national-id`, `birth-certificate`, `family-record`, `notary-power-of-attorney`, `takaful-and-karama`, `egyptian-passport`.
القيم الممكنة لـ `sub_type`: `first_time | renewal | replacement | general`.

## 7) GET `/api/v1/services/{service_slug}?sub_type=`
```json
{ "status": "success", "service_slug": "national-id", "procedures": [ { "…": "نفس حقول عنصر الخدمات + doc_code و doc_title و version" } ] }
```
404 لو الـ slug مش موجود.

## 8) POST `/api/v1/services/{service_slug}/check-eligibility`  ← واجهة فحص المستندات
**Request**
```json
{ "sub_type": "first_time", "age": 20, "available_documents": ["شهادة ميلاد", "صورة شخصية"] }
```
**Response**
```json
{
  "service_slug": "national-id", "service_name_ar": "…", "sub_type": "first_time",
  "is_eligible": true,
  "eligibility_notes": ["…"],
  "required_documents": ["…"],
  "matched_documents": ["…"],
  "missing_documents": ["…"],
  "readiness_percentage": 66.7,
  "official_reference": { "doc_code": "…", "title": "…", "authority": "…", "original_url": "…", "last_updated": "…", "verification_date": "…", "version": "1.0", "verification_status": "…", "relevance_score": 1.0 }
}
```
اعرضي `missing_documents` كقائمة "ناقص" و`readiness_percentage` كشريط تقدم.
المطابقة الحالية بالكلمات (مش ذكاء اصطناعي) فممكن تتجاهل صياغات مختلفة. الأفضل تخلي المستخدم يختار من `required_documents` بدل ما يكتب حر.

## 3–5) الجلسات
- `POST /api/v1/sessions?user_id=guest_user&session_id=` ← `{"status":"success","session":{…}}`
- `GET /api/v1/sessions/{id}` ← `{"status":"success","session":[…الرسائل…]}`
- `DELETE /api/v1/sessions/{id}` ← `{"status":"deleted","session_id":"…","message":"…"}`

## 10) POST `/api/v1/feedback`
```json
{ "session_id": "…", "message_id": null, "rating": 4, "is_helpful": true, "comment": null }
```
`rating` من 1 إلى 5.

## 9) GET `/api/v1/documents?category=`
قائمة مصادر: `doc_code, title, authority, original_url, publication_date, last_updated, service_category, verification_date, version, is_official_verified, status`.

---
### مش موجود حاليًا (قولي لو محتاجاه)
- رفع ملف مستند من المواطن (Document Upload) — الـ endpoint الحالي بيفحص قائمة أسماء مستندات مش ملفات.
- Authentication / حسابات.
