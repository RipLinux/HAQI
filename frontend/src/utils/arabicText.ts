const ARABIC_DIACRITICS = /[\u064B-\u065F\u0670\u06D6-\u06ED]/g;
export function normalizeArabicText(value: string = "") {
  return String(value)
    .normalize("NFKC")
    .replace(ARABIC_DIACRITICS, "")
    .replace(/[إأآٱ]/g, "ا")
    .replace(/ى/g, "ي")
    .replace(/ؤ/g, "و")
    .replace(/ئ/g, "ي")
    .replace(/ـ/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}
