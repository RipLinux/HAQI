import { useState } from "react";
import Shell from "../components/layout/Shell";
import Badge from "../components/common/Badge";
import { disclaimer } from "../data/services";
import { validateDocumentFile } from "../utils/fileValidation";
function DocumentCheck() {
  const [type, setType] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<boolean>(false);
const [error, setError] = useState<string>("");
const chooseFile = (candidate: File | null) => {    setResult(false); setError("");
    if (!candidate) { setFile(null); return; }
    const validation = validateDocumentFile(candidate);
    if (!validation.valid) { setFile(null); setError(validation.message); return; }
    setFile(candidate);
  };
  const reset = () => { setType(""); setFile(null); setResult(false); setError(""); };
  return <Shell><main className="page wrap narrow"><div className="page-intro centered"><Badge>أداة تجريبية</Badge><h1>فحص المستندات</h1><p>فحص شكلي محاكى لمساعدتك تراجع مستندك قبل التقديم. الملف يفضل على جهازك: لا يتم رفعه أو حفظه، ولا توجد قراءة آلية للنص (OCR).</p></div><div className="panel upload-panel"><label className="field-label" htmlFor="document-type">نوع المستند</label><select id="document-type" value={type} onChange={e=>{setType(e.target.value);setResult(false);}}><option value="">اختار نوع المستند</option><option>بطاقة الرقم القومي</option><option>شهادة الميلاد</option><option>القيد العائلي</option><option>مستند آخر</option></select><label className="dropzone"><span>⇧</span><b>اختاري ملفًا من جهازك</b><small>JPG / PNG / WEBP / PDF — حتى 10 MB</small><input key={file ? file.name : "empty-file-input"} type="file" accept=".jpg,.jpeg,.png,.webp,.pdf,application/pdf,image/jpeg,image/png,image/webp" onChange={e=>chooseFile(e.target.files?.[0] || null)}/></label>{file&&<p className="file-name">📎 {file.name} · {(file.size/1024/1024).toFixed(2)} MB</p>}{error&&<p role="alert" className="notice">{error}</p>}<div className="button-row"><button type="button" className="primary-btn" disabled={!type||!file} onClick={()=>setResult(true)}>افحص المستند</button><button type="button" className="outline-btn" onClick={reset}>إعادة</button></div><div className="result-box" aria-live="polite"><h3>النتيجة (محاكاة)</h3>{result?<><Badge kind="warning">فحص شكلي فقط</Badge><p>تم قبول الملف المختار لنوع «{type}». هذه النسخة لا تقرأ محتوى الملف ولا تتحقق من صحته رسميًا.</p><ul><li>تأكدي أن الصورة واضحة وكاملة.</li><li>تأكدي من عدم وجود أجزاء مقطوعة أو انعكاس ضوء.</li><li>راجعي تطابق البيانات مع متطلبات الجهة المختصة.</li></ul></>:<p>اختاري نوع المستند وملفًا صالحًا، ثم اضغطي «افحص المستند».</p>}</div></div><p className="disclaimer">{disclaimer}</p></main></Shell>;
}
export default DocumentCheck;
