import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import Shell from "../components/layout/Shell";
import Badge from "../components/common/Badge";
import SourceMini from "../components/services/SourceMini";
import { services, disclaimer } from "../data/services";

function ServiceDetail() {
  const { id } = useParams();
  const s = services.find((x) => x.id === id);
  const [checked, setChecked] = useState<number[]>([]);

  if (!s) {
    return (
      <Shell>
        <main className="page wrap">
          <h1>الخدمة غير موجودة</h1>
          <Link to="/services">العودة لدليل الخدمات</Link>
        </main>
      </Shell>
    );
  }

  if (s.status !== "متاح") {
    return (
      <Shell>
        <main className="page wrap">
          <Badge>قريبًا</Badge>
          <h1>{s.name}</h1>
          <p>{s.desc}</p>
          <Link to="/services">العودة للخدمات</Link>
        </main>
      </Shell>
    );
  }

  // حماية من عدم وجود بيانات اختيارية
  const steps = s.steps ?? [];
  const docs = s.docs ?? [];
  const notes = s.notes ?? [];

  return (
    <Shell>
      <main className="page wrap">
        <div className="breadcrumbs">
          <Link to="/">الرئيسية</Link> /{" "}
          <Link to="/services">دليل الخدمات</Link> / {s.cat}
        </div>

        <div className="detail-heading">
          <Badge>{s.cat}</Badge>
          <h1>{s.name}</h1>
          <p>{s.desc}</p>
          <Badge kind="warning">دليل تجريبي — غير مُتحقق منه</Badge>
        </div>

        <div className="detail-layout">
          <div className="main-column">
            <div className="panel">
              <h2>عن الخدمة</h2>
              <p>{s.intro}</p>
            </div>

            <div className="panel">
              <h2>الخطوات</h2>
              <div className="steps">
                {steps.map((st, i) => (
                  <div className="step" key={st[0]}>
                    <span>{i + 1}</span>
                    <div>
                      <h3>{st[0]}</h3>
                      <p>{st[1]}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="panel">
              <div className="panel-title">
                <div>
                  <h2>المستندات المطلوبة (عيّنة)</h2>
                  <small>
                    {checked.length}/{docs.length}
                  </small>
                </div>
                <Badge kind="muted">قائمة مراجعة</Badge>
              </div>

              <div className="checklist">
                {docs.map((d, i) => (
                  <label
                    key={d}
                    className={checked.includes(i) ? "checked" : ""}
                  >
                    <input
                      type="checkbox"
                      checked={checked.includes(i)}
                      onChange={() =>
                        setChecked((v) =>
                          v.includes(i)
                            ? v.filter((x) => x !== i)
                            : [...v, i]
                        )
                      }
                    />
                    <span>{d}</span>
                  </label>
                ))}
              </div>

              <Link className="outline-btn" to="/document-check">
                افحص مستند (تجريبي) ←
              </Link>
            </div>

            <div className="panel">
              <h2>المصادر</h2>
              <SourceMini />
            </div>
          </div>

          <aside className="side-column">
            <div className="panel">
              <h3>الجهة المسؤولة</h3>
              <b>قطاع الأحوال المدنية — وزارة الداخلية</b>
              <p>
                مكاتب السجل المدني · منافذ الخدمة المعتمدة · القنوات
                الإلكترونية الرسمية (عند إتاحتها)
              </p>
            </div>

            <div className="panel">
              <h3>المدة المتوقعة</h3>
              <b>{s.duration}</b>
              <small className="muted-text">
                توضيحي — غير مُتحقق منه
              </small>
            </div>

            <div className="panel">
              <h3>الرسوم</h3>
              <b>تحقّق من المصدر الرسمي</b>
              <p>لا نعرض رسومًا غير مُتحقق منها</p>
            </div>

            <div className="panel warning-panel">
              <p>
                {notes.map((n) => (
                  <span key={n}>
                    • {n}
                    <br />
                  </span>
                ))}
              </p>
            </div>

            <Link
              className="primary-btn full"
              to={"/assistant?q=" + encodeURIComponent("اسأل حقي عن " + s.name)}
            >
              اسأل حقي عن الخدمة
            </Link>
          </aside>
        </div>

        <p className="disclaimer">{disclaimer}</p>
      </main>
    </Shell>
  );
}

export default ServiceDetail;