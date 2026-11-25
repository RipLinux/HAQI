import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Shell from "../components/layout/Shell";
import Badge from "../components/common/Badge";
import ServiceCard from "../components/services/ServiceCard";
import { getServices } from "../services/api";
import type { ApiService } from "../types/api";
import type { GovernmentService } from "../types/domain";
import { sampleQuestions } from "../data/services";

const serviceNames: Record<string, string> = {
  "birth-certificate": "استخراج شهادة ميلاد مميكنة",
  "national-id": "بطاقة الرقم القومي",
  "family-record": "استخراج قيد عائلي",
  "egyptian-passport": "استخراج جواز سفر مصري",
  "notary-power-of-attorney": "عمل توكيل رسمي",
  "takaful-and-karama": "برنامج تكافل وكرامة",
};

const categoryDescriptions: Record<string, string> = {
  "قطاع الأحوال المدنية": "شهادات الميلاد والبطاقة والقيد العائلي.",
  "الوثائق والسفر": "خدمات جوازات السفر والوثائق.",
  "المعاشات والدعم": "برامج الدعم والمعاشات.",
  "التوثيق والتراخيص": "خدمات التوثيق والتراخيص.",
};

const icons = ["▤", "♡", "✒", "⌁", "▣", "✚"];

function createServiceCards(apiServices: ApiService[]): GovernmentService[] {
  const grouped = new Map<string, ApiService[]>();

  apiServices.forEach((service) => {
    const current = grouped.get(service.service_slug) ?? [];
    current.push(service);
    grouped.set(service.service_slug, current);
  });

  return Array.from(grouped.entries()).map(([slug, records]) => {
    const first = records[0];

    return {
      id: slug,
      name: serviceNames[slug] ?? first.service_name_ar,
      cat: first.service_category,
      desc:
        slug === "national-id"
          ? "إصدار بطاقة الرقم القومي أو تجديدها أو استخراج بدل فاقد أو تالف."
          : "اعرف الخطوات والمستندات المطلوبة والجهة المسؤولة عن الخدمة.",
      status: "متاح",
    };
  });
}

function Home() {
  const [q, setQ] = useState("");
  const [services, setServices] = useState<GovernmentService[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const nav = useNavigate();

  useEffect(() => {
    let active = true;

    async function loadServices() {
      try {
        setLoading(true);
        setError("");

        const response = await getServices();

        if (!active) return;

        const cards = createServiceCards(response.services);
        const uniqueCategories = Array.from(
          new Set(cards.map((service) => service.cat))
        );

        setServices(cards);
        setCategories(uniqueCategories);
      } catch {
        if (active) {
          setError(
            "حصلت مشكلة أثناء تحميل الخدمات. تأكدي إن الاتصال بالخدمات شغال وحاولي تاني."
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadServices();

    return () => {
      active = false;
    };
  }, []);

  return (
    <Shell>
      <main>
        <section className="hero">
          <div className="wrap hero-grid">
            <div>
              <Badge>مساعد الخدمات العامة — نموذج تجريبي</Badge>

              <h1>
                افهم حقك…
                <br />
                <em>وخطوتك الجاية</em>
              </h1>

              <p className="hero-copy">
                حقي بيشرح لك الخدمات العامة في مصر بلغة بسيطة، ويقولك
                المستندات والجهة المسؤولة، ويوضّح المصدر اللي لازم ترجعله
                قبل أي خطوة.
              </p>

              <form
                className="askbar"
                onSubmit={(e) => {
                  e.preventDefault();
                  if (q.trim()) {
                    nav("/assistant?q=" + encodeURIComponent(q));
                  }
                }}
              >
                <span>⌕</span>
                <input
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder="مثلًا: عايز أجدد بطاقتي، محتاج إيه؟"
                />
                <button type="submit">
                  اسأل <span>←</span>
                </button>
              </form>

              <div className="quick-questions">
                {sampleQuestions.slice(0, 3).map((question) => (
                  <button
                    key={question}
                    onClick={() =>
                      nav("/assistant?q=" + encodeURIComponent(question))
                    }
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>

            <div className="hero-art">
              <div className="art-orbit orbit1"></div>
              <div className="art-orbit orbit2"></div>

              <div className="hero-card original-style-card">
                <div className="original-question">
                  عايز أجدد بطاقتي، محتاج إيه؟
                </div>

                <div className="original-answer">
                  <span className="answer-dot">ح</span>
                  <div>
                    <b>حقي</b>
                    <p>
                      لتجديد البطاقة، هتحتاج تراجع المستندات المطلوبة
                      وتعرف خطوات التقديم من الجهة المختصة.
                    </p>
                  </div>
                </div>

                <div className="original-card-footer">
                  <span>● نموذج تجريبي</span>
                  <span className="number-dot">1</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="section wrap">
          <div className="section-head">
            <div>
              <Badge>نبدأ بالخدمات المتاحة</Badge>
              <h2>الخدمات الأكثر طلبًا</h2>
              <p>أدلة إرشادية تساعدك تعرف تبدأ منين.</p>
            </div>

            <Link className="text-link" to="/services">
              كل الخدمات ←
            </Link>
          </div>

          {loading && (
            <p className="result-count">جاري تحميل الخدمات...</p>
          )}

          {error && (
            <div className="panel">
              <p role="alert">{error}</p>
              <button
                className="outline-btn"
                onClick={() => window.location.reload()}
              >
                إعادة المحاولة
              </button>
            </div>
          )}

          {!loading && !error && (
            <div className="service-grid">
              {services.slice(0, 3).map((service, index) => (
                <ServiceCard
                  key={service.id}
                  service={service}
                  icon={icons[index % icons.length]}
                />
              ))}
            </div>
          )}
        </section>

        <section className="section categories-section">
          <div className="wrap">
            <div className="section-head">
              <div>
                <Badge>استكشف بسهولة</Badge>
                <h2>تصفّح حسب الفئة</h2>
                <p>اختار المجال اللي بتدور فيه عن خدمة.</p>
              </div>
            </div>

            {loading && (
              <p className="result-count">جاري تحميل الفئات...</p>
            )}

            {!loading && !error && (
              <div className="category-grid">
                {categories.map((category, index) => (
                  <Link
                    to="/services"
                    className="category-card"
                    key={category}
                  >
                    <span>{icons[index % icons.length]}</span>
                    <b>{category}</b>
                    <small>
                      {categoryDescriptions[category] ??
                        "تصفح الخدمات المتاحة في هذه الفئة."}
                    </small>
                    <i>←</i>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>

        <section className="section wrap">
          <div className="section-head">
            <div>
              <Badge>ببساطة وشفافية</Badge>
              <h2>حقي بيشتغل إزاي؟</h2>
            </div>
          </div>

          <div className="how-grid">
            {[
              ["01", "اسأل بلغتك", "اكتب سؤالك بالعامية أو الفصحى."],
              [
                "02",
                "نبحث في المصادر",
                "في النموذج: بيانات عيّنة محلية فقط، مش مواقع حكومية حية.",
              ],
              [
                "03",
                "إجابة بمصدرها",
                "كل إجابة بتوضّح مصدرها ومستوى الدليل.",
              ],
              [
                "04",
                "أو امتناع آمن",
                "لو مفيش دليل كافي، حقي بيقول كده صراحة ومش بيخمّن.",
              ],
            ].map((item) => (
              <div className="how-card" key={item[0]}>
                <span>{item[0]}</span>
                <h3>{item[1]}</h3>
                <p>{item[2]}</p>
              </div>
            ))}
          </div>

          <div className="feature-banners">
            <Link to="/document-check">
              <span className="feature-icon">▧</span>
              <div>
                <b>فحص المستندات (تجريبي)</b>
                <p>
                  اختار مستند وشوف قائمة مراجعة مقترحة قبل ما تروح.
                  الفحص شكلي فقط ولا يتحقق من صحة المستند رسميًا.
                </p>
              </div>
              <strong>جرّب الفحص ←</strong>
            </Link>

            <Link to="/sources">
              <span className="feature-icon">◈</span>
              <div>
                <b>الثقة والمصادر</b>
                <p>
                  نفرّق بوضوح بين روابط رسمية للتحقق ومصادر عيّنة توضيحية.
                </p>
              </div>
              <strong>مركز الموثوقية ←</strong>
            </Link>
          </div>
        </section>
      </main>
    </Shell>
  );
}

export default Home;
