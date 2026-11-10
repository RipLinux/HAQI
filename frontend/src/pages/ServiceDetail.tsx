import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Shell from "../components/layout/Shell";
import Badge from "../components/common/Badge";
import { getServiceDetails } from "../services/api";
import type { ApiProcedure } from "../types/api";

const subtypeNames: Record<string, string> = {
  first_time: "إصدار لأول مرة",
  renewal: "تجديد البطاقة",
  replacement: "بدل فاقد أو تالف",
  general: "الإجراء العام",
};

function ServiceDetail() {
  const { id } = useParams();

  const [procedures, setProcedures] = useState<ApiProcedure[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [checked, setChecked] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadDetails() {
      try {
        setLoading(true);
        setError("");

        if (!id) {
          throw new Error("معرّف الخدمة غير موجود.");
        }

        const response = await getServiceDetails(id);

        if (!active) return;

        setProcedures(response.procedures ?? []);
        setSelectedIndex(0);
        setChecked([]);
      } catch {
        if (active) {
          setError("حصلت مشكلة أثناء تحميل تفاصيل الخدمة. تأكد من الاتصال وحاول مرة تانية.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadDetails();

    return () => {
      active = false;
    };
  }, [id]);

  const procedure = procedures[selectedIndex];

  const toggleDocument = (index: number) => {
    setChecked((current) =>
      current.includes(index)
        ? current.filter((item) => item !== index)
        : [...current, index]
    );
  };

  if (loading) {
    return (
      <Shell>
        <main className="page wrap">
          <p className="result-count">جاري تحميل تفاصيل الخدمة...</p>
        </main>
      </Shell>
    );
  }

  if (error || !procedure) {
    return (
      <Shell>
        <main className="page wrap">
          <div className="panel">
            <h1>{error ? "تعذّر تحميل الخدمة" : "الخدمة غير موجودة"}</h1>
            <p>{error || "ملقيناش تفاصيل للخدمة المطلوبة."}</p>
            <Link className="outline-btn" to="/services">
              العودة لدليل الخدمات
            </Link>
          </div>
        </main>
      </Shell>
    );
  }

  const steps = procedure.steps ?? [];
  const docs = procedure.required_documents ?? [];
  const eligibility = procedure.eligibility_criteria ?? [];

  const serviceName = procedure.service_name_ar;
  const subtypeName =
    subtypeNames[procedure.sub_type] ?? procedure.sub_type;

  return (
    <Shell>
      <main className="page wrap">
        <div className="breadcrumbs">
          <Link to="/">الرئيسية</Link> /{" "}
          <Link to="/services">دليل الخدمات</Link> /{" "}
          {procedure.service_category}
        </div>

        <div className="detail-heading">
          <Badge>{procedure.service_category}</Badge>
          <h1>{serviceName}</h1>
          <p>{procedure.chunk_text}</p>

          {procedure.is_official_verified ? (
            <Badge kind="verified">تم التحقق من المصدر الرسمي</Badge>
          ) : (
            <Badge kind="warning">المعلومات تحتاج إلى مراجعة المصدر الرسمي</Badge>
          )}
        </div>

        {procedures.length > 1 && (
          <div className="panel">
            <h2>اختار نوع الإجراء</h2>
            <div className="chips">
              {procedures.map((item, index) => (
                <button
                  type="button"
                  className={selectedIndex === index ? "active" : ""}
                  key={item.id}
                  onClick={() => {
                    setSelectedIndex(index);
                    setChecked([]);
                  }}
                >
                  {subtypeNames[item.sub_type] ?? item.sub_type}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="detail-layout">
          <div className="main-column">
            <div className="panel">
              <h2>عن الخدمة</h2>
              <p>{serviceName}</p>
              {procedures.length > 1 && <p>{subtypeName}</p>}
            </div>

            <div className="panel">
              <h2>الخطوات</h2>

              {steps.length > 0 ? (
                <div className="steps">
                  {steps.map((step, index) => (
                    <div className="step" key={`${index}-${step}`}>
                      <span>{index + 1}</span>
                      <div>
                        <h3>الخطوة {index + 1}</h3>
                        <p>{step}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p>لا توجد خطوات مسجلة لهذه الخدمة حاليًا.</p>
              )}
            </div>

            <div className="panel">
              <div className="panel-title">
                <div>
                  <h2>المستندات المطلوبة</h2>
                  <small>
                    {checked.length}/{docs.length}
                  </small>
                </div>
                <Badge kind="muted">قائمة مراجعة</Badge>
              </div>

              {docs.length > 0 ? (
                <div className="checklist">
                  {docs.map((document, index) => (
                    <label
                      key={`${index}-${document}`}
                      className={checked.includes(index) ? "checked" : ""}
                    >
                      <input
                        type="checkbox"
                        checked={checked.includes(index)}
                        onChange={() => toggleDocument(index)}
                      />
                      <span>{document}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <p>لا توجد مستندات مسجلة لهذه الخدمة حاليًا.</p>
              )}

              <Link className="outline-btn" to="/document-check">
                افحص مستند (تجريبي) ←
              </Link>
            </div>

            {eligibility.length > 0 && (
              <div className="panel">
                <h2>شروط الاستحقاق</h2>
                <ul>
                  {eligibility.map((item, index) => (
                    <li key={`${index}-${item}`}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="panel">
              <h2>المصدر والمعلومات المرجعية</h2>
              <p>
                <b>عنوان المصدر: </b>
                {procedure.doc_title}
              </p>
              <p>
                <b>كود المستند: </b>
                {procedure.doc_code}
              </p>
              <p>
                <b>آخر تحديث: </b>
                {procedure.last_updated || "غير محدد"}
              </p>
              <p>
                <b>تاريخ التحقق: </b>
                {procedure.verification_date || "غير محدد"}
              </p>
              {procedure.original_url && (
                <a
                  className="outline-btn"
                  href={procedure.original_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  فتح المصدر الأصلي ←
                </a>
              )}
            </div>
          </div>

          <aside className="side-column">
            <div className="panel">
              <h3>الجهة المسؤولة</h3>
              <b>{procedure.authority || "غير محددة"}</b>
            </div>

            <div className="panel">
              <h3>المدة المتوقعة</h3>
              <b>{procedure.processing_time || "غير محددة"}</b>
            </div>

            <div className="panel">
              <h3>الرسوم</h3>
              <b>{procedure.fees_text || "غير محددة"}</b>
            </div>

            <div className="panel">
              <h3>حالة المستند</h3>
              <b>{procedure.doc_status || "غير محددة"}</b>
            </div>

            <Link
              className="primary-btn full"
              to={"/assistant?q=" + encodeURIComponent("اسأل حقي عن " + serviceName)}
            >
              اسأل حقي عن الخدمة
            </Link>
          </aside>
        </div>

        <p className="disclaimer">
          المعلومات المعروضة إرشادية. يُرجى مراجعة المصدر الرسمي قبل اتخاذ أي إجراء.
        </p>
      </main>
    </Shell>
  );
}

export default ServiceDetail;
