import { useState } from "react";
import {
  PLAN_CATEGORY_OPTIONS,
  PLAN_YEARS,
  categoryTitle,
  createEmptyActivity,
  createEmptyMilestone,
  normalizePlanData,
  sumPlanAmount,
} from "./planData";

function formatDisplayAmount(amount, currency, rate) {
  if (amount == null || amount === "") return null;
  const value = parseFloat(amount) || 0;
  if (currency === "USD") return (value / rate).toFixed(2);
  return Number(value).toLocaleString("en-IN");
}

function formatCurrency(amount, currency, rate) {
  const symbol = currency === "INR" ? "₹" : "$";
  const display = formatDisplayAmount(amount, currency, rate);
  return display == null ? null : `${symbol}${display}`;
}

function MilestoneCard({
  milestone,
  milestoneIndex,
  readonly,
  currency,
  rate,
  onChange,
  onRemove,
  onAddActivity,
  onRemoveActivity,
}) {
  const milestoneTotal = (milestone.activities || []).reduce((sum, activity) => sum + (parseFloat(activity.amount) || 0), 0);

  function toggleCategory(code) {
    const current = milestone.categories || [];
    const next = current.includes(code)
      ? current.filter((item) => item !== code)
      : [...current, code];
    onChange({ ...milestone, categories: next.length ? next : current });
  }

  return (
    <div className="rounded-2xl border border-primary-100/80 bg-white/90 p-4 space-y-4 shadow-soft">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div className="flex-1 min-w-0">
          {readonly ? (
            <h4 className="font-semibold text-ink-900 break-words">{milestone.milestone || `Milestone ${milestoneIndex}`}</h4>
          ) : (
            <input
              className="w-full border border-primary-100 rounded-xl px-3 py-2 text-sm bg-white"
              value={milestone.milestone || ""}
              onChange={(e) => onChange({ ...milestone, milestone: e.target.value })}
              placeholder={`Milestone ${milestoneIndex}`}
            />
          )}
          <div className="mt-3 flex flex-wrap gap-2">
            {(milestone.categories || []).map((code) => (
              <span
                key={code}
                className="inline-flex items-center rounded-full border border-primary-200 bg-primary-50 px-2.5 py-1 text-xs font-medium text-primary-700"
                title={categoryTitle(code)}
              >
                {code}
              </span>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 md:justify-end">
          <span className="rounded-full bg-sand-100 px-3 py-1 text-xs font-semibold text-ink-700">
            Total {currency === "INR" ? "₹" : "$"}{currency === "INR" ? milestoneTotal.toLocaleString("en-IN") : (milestoneTotal / rate).toFixed(2)}
          </span>
          {!readonly && onRemove && (
            <button onClick={onRemove} className="btn-secondary text-xs px-3 py-1.5">
              Remove milestone
            </button>
          )}
        </div>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-ink-500 mb-2">Categories</p>
        <div className="flex flex-wrap gap-2">
          {PLAN_CATEGORY_OPTIONS.map((item) => {
            const active = (milestone.categories || []).includes(item.code);
            return (
              <button
                key={item.code}
                type="button"
                onClick={() => !readonly && toggleCategory(item.code)}
                disabled={readonly}
                className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition-all ${
                  active
                    ? "border-primary-600 bg-primary-600 text-white"
                    : "border-primary-100 bg-white text-ink-600 hover:border-primary-300"
                } ${readonly ? "cursor-default" : ""}`}
                title={item.title}
              >
                {item.code}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-ink-500 mb-2">Impact</p>
        {readonly ? (
          <p className="rounded-xl border border-primary-100 bg-primary-50/50 px-3 py-2 text-sm text-ink-700 whitespace-pre-wrap break-words">
            {milestone.impact || <span className="text-ink-300">—</span>}
          </p>
        ) : (
          <textarea
            rows={3}
            className="w-full border border-primary-100 rounded-xl px-3 py-2 text-sm bg-white resize-none"
            value={milestone.impact || ""}
            onChange={(e) => onChange({ ...milestone, impact: e.target.value })}
            placeholder="Describe the expected impact of this milestone…"
          />
        )}
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-ink-500">Activities</p>
          {!readonly && (
            <button onClick={onAddActivity} className="text-xs font-semibold text-primary-700 hover:text-primary-800">
              + Add activity
            </button>
          )}
        </div>

        {(milestone.activities || []).map((activity, activityIndex) => {
          const amountLabel = formatCurrency(activity.amount, currency, rate);
          return (
            <div key={activityIndex} className="rounded-xl border border-primary-100 bg-ink-50/60 p-3 space-y-3">
              {readonly ? (
                <>
                  <div className="flex flex-col gap-1">
                    <p className="text-sm font-medium text-ink-900 break-words">
                      {activity.activity || <span className="text-ink-300">—</span>}
                    </p>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-500">
                      <span>POC: {activity.poc || "—"}</span>
                      <span>Amount: {amountLabel || "—"}</span>
                    </div>
                  </div>
                  {activity.notes && <p className="text-xs text-ink-600 whitespace-pre-wrap">{activity.notes}</p>}
                </>
              ) : (
                <>
                  <div className="grid grid-cols-1 gap-3 md:grid-cols-[1.5fr_1fr_0.7fr_auto]">
                    <input
                      className="w-full border border-primary-100 rounded-xl px-3 py-2 text-sm bg-white"
                      value={activity.activity || ""}
                      onChange={(e) => onChange({
                        ...milestone,
                        activities: milestone.activities.map((item, idx) => idx === activityIndex ? { ...item, activity: e.target.value } : item),
                      })}
                      placeholder="Activity"
                    />
                    <input
                      className="w-full border border-primary-100 rounded-xl px-3 py-2 text-sm bg-white"
                      value={activity.poc || ""}
                      onChange={(e) => onChange({
                        ...milestone,
                        activities: milestone.activities.map((item, idx) => idx === activityIndex ? { ...item, poc: e.target.value } : item),
                      })}
                      placeholder="POC"
                    />
                    <input
                      type="number"
                      className="w-full border border-primary-100 rounded-xl px-3 py-2 text-sm bg-white text-right"
                      value={currency === "USD"
                        ? (activity.amount != null ? (activity.amount / rate).toFixed(2) : "")
                        : (activity.amount ?? "")}
                      onChange={(e) => {
                        const value = e.target.value ? parseFloat(e.target.value) : null;
                        onChange({
                          ...milestone,
                          activities: milestone.activities.map((item, idx) => idx === activityIndex
                            ? { ...item, amount: currency === "USD" && value != null ? value * rate : value }
                            : item),
                        });
                      }}
                      placeholder="Amount"
                    />
                      {onRemoveActivity && (
                        <button onClick={() => onRemoveActivity(activityIndex)} className="btn-secondary text-xs px-3 py-2">
                        Remove
                      </button>
                    )}
                  </div>
                  <textarea
                    rows={2}
                    className="w-full border border-primary-100 rounded-xl px-3 py-2 text-sm bg-white resize-none"
                    value={activity.notes || ""}
                    onChange={(e) => onChange({
                      ...milestone,
                      activities: milestone.activities.map((item, idx) => idx === activityIndex ? { ...item, notes: e.target.value } : item),
                    })}
                    placeholder="Activity notes"
                  />
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function YearPanel({ year, rows, readonly, currency, rate, grandTotal, onChange }) {
  const data = rows && rows.length > 0 ? rows : [createEmptyMilestone()];
  const yearTotal = data.reduce((sum, milestone) => {
    return sum + (milestone.activities || []).reduce((activitySum, activity) => activitySum + (parseFloat(activity.amount) || 0), 0);
  }, 0);

  function updateMilestone(index, nextMilestone) {
    onChange(data.map((item, itemIndex) => (itemIndex === index ? nextMilestone : item)));
  }

  function addMilestone() {
    onChange([...data, createEmptyMilestone(data.length + 1)]);
  }

  function removeMilestone(index) {
    if (data.length === 1) return;
    onChange(data.filter((_, itemIndex) => itemIndex !== index));
  }

  function addActivity(index) {
    onChange(data.map((item, itemIndex) => (
      itemIndex === index
        ? { ...item, activities: [...(item.activities || []), createEmptyActivity()] }
        : item
    )));
  }

  function removeActivity(milestoneIndex, activityIndex) {
    onChange(data.map((item, itemIdx) => {
      if (itemIdx !== milestoneIndex) return item;
      const nextActivities = (item.activities || []).filter((_, idx) => idx !== activityIndex);
      return { ...item, activities: nextActivities.length ? nextActivities : [createEmptyActivity()] };
    }));
  }

  return (
    <div className="mb-6">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-ink-700">Year {year}</h3>
        <div className="flex items-center gap-2 text-xs text-ink-500">
          <span>Total:</span>
          <span className="font-semibold text-ink-800">{currency === "INR" ? "₹" : "$"}{currency === "INR" ? yearTotal.toLocaleString("en-IN") : (yearTotal / rate).toFixed(2)}</span>
          {grandTotal > 0 && <span>({((yearTotal / grandTotal) * 100).toFixed(1)}%)</span>}
        </div>
      </div>

      <div className="space-y-4">
        {data.map((milestone, milestoneIndex) => (
          <MilestoneCard
            key={`${year}-${milestoneIndex}`}
            milestone={milestone}
            milestoneIndex={milestoneIndex + 1}
            readonly={readonly}
            currency={currency}
            rate={rate}
            onChange={(next) => updateMilestone(milestoneIndex, next)}
            onRemove={readonly ? null : () => removeMilestone(milestoneIndex)}
            onAddActivity={readonly ? null : () => addActivity(milestoneIndex)}
            onRemoveActivity={readonly ? null : (activityIndex) => removeActivity(milestoneIndex, activityIndex)}
          />
        ))}
      </div>

      {!readonly && (
        <div className="mt-3">
          <button onClick={addMilestone} className="text-xs font-semibold text-primary-700 hover:text-primary-800">
            + Add milestone
          </button>
        </div>
      )}
    </div>
  );
}

export function PlanMilestonesViewer({ plan, readonly = true, onChange }) {
  const [currency, setCurrency] = useState("INR");
  const [rate, setRate] = useState(84);

  if (!plan) return <p className="text-sm text-gray-400">Not available yet.</p>;

  const normalizedPlan = normalizePlanData(plan.plan_data);
  const grandTotalINR = sumPlanAmount(normalizedPlan);
  const symbol = currency === "INR" ? "₹" : "$";
  const grandTotalDisplay = currency === "INR"
    ? grandTotalINR.toLocaleString("en-IN")
    : (grandTotalINR / rate).toFixed(2);

  function handleYearChange(year, rows) {
    onChange?.({ ...normalizedPlan, [String(year)]: rows });
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="bg-primary-50 border border-primary-200 rounded-xl px-4 py-3 flex items-center gap-3">
          <span className="text-sm text-primary-700 font-medium">3-Year Grand Total</span>
          <span className="text-lg font-bold text-primary-800">{symbol}{grandTotalDisplay}</span>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-sm font-medium text-ink-600">Amount in</span>
          <span className="inline-flex rounded-xl border border-primary-100 overflow-hidden text-sm bg-white">
            <button
              onClick={() => setCurrency("INR")}
              className={`px-3 py-2 ${currency === "INR" ? "bg-primary-700 text-white" : "text-ink-500 hover:bg-ink-50"}`}
            >
              ₹
            </button>
            <button
              onClick={() => setCurrency("USD")}
              className={`px-3 py-2 ${currency === "USD" ? "bg-primary-700 text-white" : "text-ink-500 hover:bg-ink-50"}`}
            >
              $
            </button>
          </span>
          {currency === "USD" && (
            <span className="inline-flex items-center gap-1.5 text-sm text-ink-500">
              $1 = ₹
              <input
                type="number"
                min="1"
                value={rate}
                onChange={(e) => setRate(parseFloat(e.target.value) || 1)}
                className="w-20 border border-primary-100 rounded-xl px-2 py-1 text-right text-ink-700 bg-white"
              />
            </span>
          )}
        </div>
      </div>

      {PLAN_YEARS.map((year) => (
        <YearPanel
          key={year}
          year={year}
          rows={normalizedPlan[year]}
          readonly={readonly}
          currency={currency}
          rate={rate}
          grandTotal={grandTotalINR}
          onChange={(rows) => handleYearChange(year, rows)}
        />
      ))}
    </div>
  );
}
