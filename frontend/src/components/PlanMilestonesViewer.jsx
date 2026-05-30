import { useEffect, useState } from "react";
import {
  DEFAULT_PLAN_META,
  PLAN_CATEGORY_OPTIONS,
  PLAN_YEARS,
  categoryTitle,
  createEmptyActivity,
  createEmptyMilestone,
  getPlanMeta,
  normalizePlanData,
  sumPlanAmount,
  withPlanMeta,
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

  const activities = milestone.activities || [];
  const filledActivities = activities.filter((a) => a.pct_complete !== "" && a.pct_complete != null);
  const milestonePct = filledActivities.length > 0
    ? Math.round(filledActivities.reduce((sum, a) => sum + (parseFloat(a.pct_complete) || 0), 0) / filledActivities.length)
    : null;

  function toggleCategory(code) {
    const current = milestone.categories || [];
    const next = current.includes(code)
      ? current.filter((item) => item !== code)
      : [...current, code];
    onChange({ ...milestone, categories: next });
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
          <div className="mt-2 flex flex-wrap gap-1">
            {PLAN_CATEGORY_OPTIONS.map((item) => {
              const active = (milestone.categories || []).includes(item.code);
              return (
                <button
                  key={item.code}
                  type="button"
                  onClick={() => !readonly && toggleCategory(item.code)}
                  disabled={readonly}
                  className={`rounded-full px-2 py-0.5 text-xs font-medium transition-all ${
                    active
                      ? "bg-primary-600 text-white border border-primary-600"
                      : "bg-ink-100 text-ink-400 border border-ink-200"
                  } ${readonly ? "cursor-default" : "cursor-pointer hover:opacity-80"}`}
                  title={item.title}
                >
                  {item.code}
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 md:justify-end">
          {milestonePct != null && (
            <span className="rounded-full bg-forest-50 border border-forest-200 px-2.5 py-0.5 text-xs font-semibold text-forest-700">
              {milestonePct}%
            </span>
          )}
          <span className="rounded-full bg-sand-100 px-3 py-1 text-xs font-semibold text-ink-700">
            {currency === "INR" ? "₹" : "$"}{currency === "INR" ? milestoneTotal.toLocaleString("en-IN") : (milestoneTotal / rate).toFixed(2)}
          </span>
          {!readonly && onRemove && (
            <button onClick={onRemove} title="Remove milestone" className="ml-1 text-ink-300 hover:text-red-500 transition-colors text-lg leading-none">
              &times;
            </button>
          )}
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
                      {activity.end_date && <span>Due: {activity.end_date}</span>}
                      {activity.pct_complete !== "" && activity.pct_complete != null && <span>{activity.pct_complete}% complete</span>}
                    </div>
                  </div>
                  {activity.notes && <p className="text-xs text-ink-600 whitespace-pre-wrap">{activity.notes}</p>}
                </>
              ) : (
                <>
                  <div className="flex items-start gap-2">
                    <div className="flex-1 grid grid-cols-1 gap-2 md:grid-cols-[1.5fr_1fr_0.7fr]">
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
                    </div>
                    {onRemoveActivity && (
                      <button onClick={() => onRemoveActivity(activityIndex)} title="Remove activity" className="mt-2 text-ink-300 hover:text-red-500 transition-colors text-lg leading-none flex-shrink-0">
                        &times;
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_0.6fr_2.2fr]">
                    <input
                      type="date"
                      className="w-full border border-primary-100 rounded-xl px-3 py-2 text-sm bg-white"
                      value={activity.end_date || ""}
                      onChange={(e) => onChange({
                        ...milestone,
                        activities: milestone.activities.map((item, idx) => idx === activityIndex ? { ...item, end_date: e.target.value } : item),
                      })}
                      placeholder="End date"
                    />
                    <input
                      type="number"
                      min="0"
                      max="100"
                      className="w-full border border-primary-100 rounded-xl px-3 py-2 text-sm bg-white text-right"
                      value={activity.pct_complete ?? ""}
                      onChange={(e) => onChange({
                        ...milestone,
                        activities: milestone.activities.map((item, idx) => idx === activityIndex ? { ...item, pct_complete: e.target.value } : item),
                      })}
                      placeholder="% complete"
                    />
                    <input
                      className="w-full min-w-0 border border-primary-100 rounded-xl px-3 py-2 text-sm bg-white"
                      value={activity.notes || ""}
                      onChange={(e) => onChange({
                        ...milestone,
                        activities: milestone.activities.map((item, idx) => idx === activityIndex ? { ...item, notes: e.target.value } : item),
                      })}
                      placeholder="Notes"
                    />
                  </div>
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
  const initialMeta = getPlanMeta(plan?.plan_data);
  const [currency, setCurrency] = useState(initialMeta.currency || DEFAULT_PLAN_META.currency);
  const [rate, setRate] = useState(initialMeta.rate || DEFAULT_PLAN_META.rate);
  const [liveRateLoading, setLiveRateLoading] = useState(false);
  const [liveRateUpdatedAt, setLiveRateUpdatedAt] = useState("");

  if (!plan) return <p className="text-sm text-gray-400">Not available yet.</p>;

  const normalizedPlan = normalizePlanData(plan.plan_data);

  useEffect(() => {
    const nextMeta = getPlanMeta(plan?.plan_data);
    setCurrency(nextMeta.currency);
    setRate(nextMeta.rate);
  }, [plan]);

  function emitPlanWithMeta(nextYears, nextMeta) {
    onChange?.(withPlanMeta(nextYears, nextMeta));
  }

  function handleCurrencyChange(nextCurrency) {
    setCurrency(nextCurrency);
    emitPlanWithMeta(normalizedPlan, { currency: nextCurrency, rate });
  }

  function handleRateChange(nextRate) {
    const safeRate = Number.isFinite(nextRate) && nextRate > 0 ? nextRate : 1;
    setRate(safeRate);
    emitPlanWithMeta(normalizedPlan, { currency, rate: safeRate });
  }

  async function refreshLiveRate() {
    setLiveRateLoading(true);
    try {
      const res = await fetch("https://open.er-api.com/v6/latest/USD");
      if (!res.ok) throw new Error("Failed to fetch live exchange rate");
      const data = await res.json();
      const inr = Number(data?.rates?.INR);
      if (!Number.isFinite(inr) || inr <= 0) throw new Error("Invalid live exchange rate");
      handleRateChange(inr);
      setLiveRateUpdatedAt(data?.time_last_update_utc || new Date().toUTCString());
    } catch {
      // Keep the current manually entered rate when live fetch fails.
    } finally {
      setLiveRateLoading(false);
    }
  }

  useEffect(() => {
    if (currency === "USD") refreshLiveRate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currency]);

  const grandTotalINR = sumPlanAmount(normalizedPlan);
  const symbol = currency === "INR" ? "₹" : "$";
  const grandTotalDisplay = currency === "INR"
    ? grandTotalINR.toLocaleString("en-IN")
    : (grandTotalINR / rate).toFixed(2);

  function handleYearChange(year, rows) {
    emitPlanWithMeta({ ...normalizedPlan, [String(year)]: rows }, { currency, rate });
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
              onClick={() => handleCurrencyChange("INR")}
              className={`px-3 py-2 ${currency === "INR" ? "bg-primary-700 text-white" : "text-ink-500 hover:bg-ink-50"}`}
            >
              ₹
            </button>
            <button
              onClick={() => handleCurrencyChange("USD")}
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
                onChange={(e) => handleRateChange(parseFloat(e.target.value) || 1)}
                className="w-20 border border-primary-100 rounded-xl px-2 py-1 text-right text-ink-700 bg-white"
              />
              <button
                type="button"
                onClick={refreshLiveRate}
                disabled={liveRateLoading}
                className="px-2 py-1 rounded border border-primary-100 text-xs text-ink-600 hover:bg-ink-50 disabled:opacity-60"
              >
                {liveRateLoading ? "Loading..." : "Use Live"}
              </button>
              {liveRateUpdatedAt && (
                <span className="text-xs text-ink-400">Updated: {liveRateUpdatedAt}</span>
              )}
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
