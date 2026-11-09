export const MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024;
  export const ALLOWED_DOCUMENT_TYPES: Readonly<Record<string, readonly string[]>> = Object.freeze({
  ".jpg": ["image/jpeg"], ".jpeg": ["image/jpeg"], ".png": ["image/png"],
  ".webp": ["image/webp"], ".pdf": ["application/pdf"],
});

export function validateDocumentFile(file: File | null | undefined) {
    if (!file) return { valid: false, code: "missing", message: "اختاري ملفًا أولًا." };
  if (file.size <= 0) return { valid: false, code: "empty", message: "الملف فارغ." };
  if (file.size > MAX_DOCUMENT_SIZE_BYTES) return { valid: false, code: "too_large", message: "حجم الملف أكبر من 10 MB." };
  const dot = file.name.lastIndexOf(".");
  const extension = dot >= 0 ? file.name.slice(dot).toLowerCase() : "";
  const allowedMimeTypes = ALLOWED_DOCUMENT_TYPES[extension];
  if (!allowedMimeTypes) return { valid: false, code: "extension", message: "نوع الملف غير مدعوم. استخدمي JPG أو PNG أو WEBP أو PDF." };
  if (file.type && !allowedMimeTypes.includes(file.type)) return { valid: false, code: "mime", message: "امتداد الملف لا يتوافق مع نوعه." };
  return { valid: true, code: "ok", message: "الملف مقبول للفحص الشكلي التجريبي." };
}
