import { useState } from "react";
import Shell from "../components/layout/Shell";
import Badge from "../components/common/Badge";
import ServiceCard from "../components/services/ServiceCard";
import { services, categories } from "../data/services";
import { normalizeArabicText } from "../utils/arabicText.js";
function Services(){const [search,setSearch]=useState("");const [cat,setCat]=useState("الكل");const normalizedSearch=normalizeArabicText(search);const filtered=services.filter(s=>(cat==="الكل"||s.cat===cat)&&normalizeArabicText(s.name+" "+s.desc).includes(normalizedSearch));return <Shell><main className="page wrap"><div className="page-intro"><Badge>دليل الخدمات</Badge><h1>الخدمات العامة بخطوات واضحة</h1><p>أدلة إرشادية عامة مبنية على بيانات عيّنة. نبدأ بخدمات الأحوال المدنية، وباقي الفئات قريبًا.</p><Badge kind="muted">بيانات تجريبية</Badge></div><div className="filter-box"><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="ابحث عن خدمة… مثلًا: ميلاد"/><div className="chips">{categories.map(c=><button className={cat===c?"active":""} onClick={()=>setCat(c)} key={c}>{c}</button>)}</div></div><p className="result-count">{filtered.length} خدمة</p><div className="service-grid">{filtered.map((s,i)=><ServiceCard key={s.id} service={s} icon={["▤","▣","▧","♡","✒","⌁","▣","✚"][services.indexOf(s)]}/>)}</div></main></Shell>}
export default Services;
