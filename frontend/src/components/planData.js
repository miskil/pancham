export const PLAN_YEARS = ["1", "2", "3"];

export const PLAN_CATEGORY_OPTIONS = [
  { code: "H", label: "H", title: "Health" },
  { code: "E", label: "E", title: "Education" },
  { code: "En", label: "En", title: "Environment" },
  { code: "WE", label: "WE", title: "Women's Empowerment" },
  { code: "IG", label: "IG", title: "Income Generation" },
];

const CATEGORY_BY_CODE = Object.fromEntries(PLAN_CATEGORY_OPTIONS.map((item) => [item.code, item.title]));
const LEGACY_CATEGORY_BY_LABEL = {
  Health: "H",
  Healthcare: "H",
  Education: "E",
  Environment: "En",
  "Women's Empowerment": "WE",
  "Income Generation": "IG",
  "Admin Cost": "IG",
};

export function createEmptyActivity() {
  return {
    activity: "",
    poc: "",
    amount: null,
    notes: "",
  };
}

export function createEmptyMilestone(index = 1) {
  return {
    milestone: "",
    categories: [],
    impact: "",
    activities: [createEmptyActivity()],
    label: `Milestone ${index}`,
  };
}

export function categoryTitle(code) {
  return CATEGORY_BY_CODE[code] || code;
}

export function normalizeCategory(code) {
  if (typeof code !== "string") return null;
  const trimmed = code.trim();
  if (CATEGORY_BY_CODE[trimmed]) return trimmed;
  return LEGACY_CATEGORY_BY_LABEL[trimmed] || null;
}

export function normalizeCategories(categories) {
  const raw = Array.isArray(categories) ? categories : categories ? [categories] : [];
  const normalized = raw.map(normalizeCategory).filter(Boolean);
  return normalized.length ? [...new Set(normalized)] : ["H"];
}

export function normalizeActivity(activity) {
  const source = activity && typeof activity === "object" ? activity : {};
  return {
    activity: source.activity || source.details || "",
    poc: source.poc || "",
    amount: source.amount ?? null,
    notes: source.notes || source.comment || "",
  };
}

export function normalizeMilestone(milestone, index = 1) {
  const source = milestone && typeof milestone === "object" ? milestone : {};
  const activities = Array.isArray(source.activities) && source.activities.length > 0
    ? source.activities.map(normalizeActivity)
    : [normalizeActivity(source)];

  return {
    milestone: source.milestone || source.title || source.name || `Milestone ${index}`,
    categories: normalizeCategories(source.categories || source.category),
    impact: source.impact || source.impact_box || "",
    activities,
  };
}

export function normalizeYearData(yearData) {
  const source = Array.isArray(yearData) ? yearData : [];
  if (source.length === 0) {
    return [createEmptyMilestone()];
  }

  const alreadyNested = source.some((item) => item && typeof item === "object" && Array.isArray(item.activities));
  if (alreadyNested) {
    return source.map((milestone, index) => normalizeMilestone(milestone, index + 1));
  }

  return source.map((row, index) => ({
    milestone: row?.milestone || row?.title || row?.category || `Milestone ${index + 1}`,
    categories: normalizeCategories(row?.categories || row?.category),
    impact: row?.impact || row?.impact_box || "",
    activities: [normalizeActivity(row)],
  }));
}

export function normalizePlanData(planData) {
  const source = planData && typeof planData === "object" ? planData : {};
  const normalized = {};
  for (const year of PLAN_YEARS) {
    normalized[year] = normalizeYearData(source[year]);
  }
  return normalized;
}

export function flattenPlanActivities(planData) {
  const normalized = normalizePlanData(planData);
  return PLAN_YEARS.flatMap((year) =>
    normalized[year].flatMap((milestone) =>
      (milestone.activities || []).map((activity) => ({
        year,
        milestone: milestone.milestone,
        categories: milestone.categories || [],
        ...activity,
      })),
    ),
  );
}

export function sumPlanAmount(planData) {
  return flattenPlanActivities(planData).reduce((sum, item) => sum + (parseFloat(item.amount) || 0), 0);
}

export function countFilledPlanActivities(planData) {
  return flattenPlanActivities(planData).filter((item) => item.activity || item.poc || item.amount != null || item.notes).length;
}
