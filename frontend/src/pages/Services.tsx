import { useEffect, useMemo, useState } from "react";
import Shell from "../components/layout/Shell";
import Badge from "../components/common/Badge";
import ServiceCard from "../components/services/ServiceCard";
import { getServices } from "../services/api";
import type { ApiService } from "../types/api";
import type { GovernmentService } from "../types/domain";
import { normalizeArabicText } from "../utils/arabicText.js";

const serviceNames: Record<string, string> = {
  "birth-certificate": "استخراج شهادة ميلاد مميكنة",
  "national-id": "بطاقة الرقم القومي",
  "family-record": "استخراج قيد عائلي",
  "egyptian-passport": "استخراج جواز سفر مصري",
  "notary-power-of-attorney": "عمل توكيل رسمي",
  "takaful-and-karama": "برنامج تكافل وكرامة",
};

function createServiceCards(apiServices: ApiService[]): GovernmentService[] {
  const grouped = new Map<string, ApiService[]>();

  apiServices.forEach((service) => {
    const current = grouped.get(service.service_slug) ?? [];
    current.push(service);
    grouped.set(service.service_slug, current);
  });

  return Array.from(grouped.entries()).map(([slug, records]) => {
    const first = records[0];

    const description =
      slug === "national-id"
        ? "إصدار بطاقة الرقم القومي أو تجديدها أو استخراج بدل فاقد أو تالف."
        : "اعرف الخطوات والمستندات المطلوبة والجهة المسؤولة عن الخدمة.";

    return {
      id: slug,
      name: serviceNames[slug] ?? first.service_name_ar,
      cat: first.service_category,
      desc: description,
      status: "متاح",
    };
  });
}

function Services() {
  const [search, setSearch] = useState("");
  const [cat, setCat] = useState("الكل");
  const [services, setServices] = useState<GovernmentService[]>([]);
  const [categories, setCategories] = useState<string[]>(["الكل"]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
        setCategories(["الكل", ...uniqueCategories]);
      } catch {
        if (active) {
          setError("حصلت مشكلة أثناء تحميل الخدمات. تأكد إن الاتصال بالـAPI شغال وحاول تاني.");
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

  const filtered = useMemo(() => {
    const normalizedSearch = normalizeArabicText(search);

    return services.filter(
      (service) =>
        (cat === "الكل" || service.cat === cat) &&
        normalizeArabicText(service.name + " " + service.desc).includes(
          normalizedSearch
        )
    );
  }, [services, search, cat]);

  return (
    <Shell>
      <main className="page wrap">
        <div className="page-intro">
          <Badge>دليل الخدمات</Badge>
          <h1>الخدمات العامة بخطوات واضحة</h1>
          <p>
            تصفّح الخدمات الحكومية واعرف الإجراءات والمستندات المطلوبة من
            بيانات الخدمات المتاحة.
          </p>
          <Badge kind="muted">بيانات متصلة بالخدمات</Badge>
        </div>

        <div className="filter-box">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="ابحث عن خدمة… مثلًا: ميلاد"
          />

          <div className="chips">
            {categories.map((category) => (
              <button
                className={cat === category ? "active" : ""}
                onClick={() => setCat(category)}
                key={category}
              >
                {category}
              </button>
            ))}
          </div>
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
          <>
            <p className="result-count">{filtered.length} خدمة</p>

            {filtered.length > 0 ? (
              <div className="service-grid">
                {filtered.map((service, index) => (
                  <ServiceCard
                    key={service.id}
                    service={service}
                    icon={["▤", "▣", "▧", "♡", "✒", "⌁", "▣", "✚"][index % 8]}
                  />
                ))}
              </div>
            ) : (
              <div className="panel">
                <p>مفيش خدمات مطابقة لبحثك.</p>
              </div>
            )}
          </>
        )}
      </main>
    </Shell>
  );
}

export default Services;
