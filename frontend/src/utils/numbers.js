const DIGIT_MAP = {
  "०": "0",
  "१": "1",
  "२": "2",
  "३": "3",
  "४": "4",
  "५": "5",
  "६": "6",
  "७": "7",
  "८": "8",
  "९": "9",
};

export function normalizeLocalizedDigits(value) {
  if (value == null) return "";
  return String(value)
    .replace(/[०-९]/g, (ch) => DIGIT_MAP[ch] || ch)
    .replace(/,/g, "")
    .trim();
}

export function parseLocaleNumber(value) {
  if (typeof value === "number") return Number.isFinite(value) ? value : null;
  const normalized = normalizeLocalizedDigits(value);
  if (!normalized) return null;
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

export function formatEnglishNumber(value, options = {}) {
  const parsed = parseLocaleNumber(value);
  if (parsed == null) return "";
  return new Intl.NumberFormat("en-IN-u-nu-latn", options).format(parsed);
}
