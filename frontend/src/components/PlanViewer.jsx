import { useState } from "react";

const CATEGORIES = [
  "Education",
  "Environment",
  "Healthcare",
  "Income Generation",
  "Women's Empowerment",
  "Admin Cost",
];

const ABBR = {
  "Education": "Edu.",
  "Environment": "Env.",
  "Healthcare": "Health",
  "Income Generation": "Inc. Gen.",
  "Women's Empowerment": "W. Emp.",
  "Admin Cost": "Admin",
};

function emptyRow(category) {
  return { category, details: "", amount: null, comment: "" };
}

function defaultRows() {
  return CATEGORIES.map((cat) => emptyRow(cat));
}

function PlanTable({ year, rows, readonly, onChange, currency, rate, grandTotal }) {
  const data = (rows && rows.length > 0) ? rows : defaultRows();
  const [openComments, setOpenComments] = useState({});

  function displayAmount(amount) {
    if (amount == null) return null;
    if (currency === "USD") return (amount / rate).toFixed(2);
    return Number(amount).toLocaleString("en-IN");
  }

  const symbol = currency === "INR" ? "₹" : "$";

  const groups = CATEGORIES.map((cat) => ({
    cat,
    indices: data.reduce((acc, r, i) => r.category === cat ? [...acc, i] : acc, []),
  }));

  function update(i, field, value) {
    onChange?.(data.map((r, idx) => idx === i ? { ...r, [field]: value } : r));
  }

  function addRow(cat) {
    const lastIdx = data.map((r, i) => r.category === cat ? i : -1).filter(i => i >= 0).pop() ?? data.length - 1;
    const next = [...data];
    next.splice(lastIdx + 1, 0, emptyRow(cat));
    onChange?.(next);
  }

  function removeRow(i) {
    onChange?.(data.filter((_, idx) => idx !== i));
  }

  function toggleComment(i) {
    setOpenComments((prev) => ({ ...prev, [i]: !prev[i] }));
  }

  const total = data.reduce((sum, r) => sum + (parseFloat(r.amount) || 0), 0);

  return (
    <div className="mb-6">
      <h3 className="text-sm font-semibold text-gray-600 mb-2">Year {year}</h3>
      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm border-collapse">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-1.5 py-1 font-medium text-gray-600 w-14 border-r">Cat.</th>
              <th className="text-left px-1.5 py-1 font-medium text-gray-600">Details</th>
              <th className="text-right px-1.5 py-1 font-medium text-gray-600 w-28">Amt ({symbol})</th>
              <th className="text-right px-1 py-1 font-medium text-gray-600 w-10">%</th>
              <th className="w-6" />
              {!readonly && <th className="w-5" />}
            </tr>
          </thead>
          <tbody>
            {groups.map(({ cat, indices }) => {
              if (indices.length === 0) return null;
              return indices.map((rowIdx, posInGroup) => {
                const hasComment = !!data[rowIdx].comment;
                const commentOpen = !!openComments[rowIdx];
                return (
                  <>
                    <tr key={rowIdx} className="border-b last:border-0 hover:bg-gray-50">
                      {posInGroup === 0 && (
                        <td
                          rowSpan={indices.length + (readonly ? 0 : 1)}
                          className="px-1.5 py-1 font-medium text-gray-700 align-top border-r bg-gray-50 w-14 leading-tight"
                          title={cat}
                        >
                          {ABBR[cat] ?? cat}
                        </td>
                      )}
                      <td className="px-1.5 py-0.5 align-top">
                        {readonly ? (
                          <span className="text-gray-700 whitespace-pre-wrap break-words block">
                            {data[rowIdx].details || <span className="text-gray-300">—</span>}
                          </span>
                        ) : (
                          <textarea
                            rows={2}
                            className="w-full bg-transparent focus:bg-white focus:outline focus:outline-1 focus:outline-primary-300 rounded px-1 py-0.5 text-sm resize-none"
                            value={data[rowIdx].details || ""}
                            onChange={(e) => update(rowIdx, "details", e.target.value)}
                            placeholder="Describe activity…"
                          />
                        )}
                      </td>
                      <td className="px-1.5 py-0.5 text-right align-top">
                        {readonly ? (
                          <span className="text-gray-700">
                            {data[rowIdx].amount != null
                              ? `${symbol}${displayAmount(data[rowIdx].amount)}`
                              : <span className="text-gray-300">—</span>}
                          </span>
                        ) : (
                          <input
                            type="number"
                            className="w-full bg-transparent focus:bg-white focus:outline focus:outline-1 focus:outline-primary-300 rounded px-1 py-0.5 text-sm text-right"
                            value={
                              currency === "USD"
                                ? (data[rowIdx].amount != null ? (data[rowIdx].amount / rate).toFixed(2) : "")
                                : (data[rowIdx].amount ?? "")
                            }
                            onChange={(e) => {
                              const val = e.target.value ? parseFloat(e.target.value) : null;
                              update(rowIdx, "amount", currency === "USD" && val != null ? val * rate : val);
                            }}
                            placeholder="0"
                          />
                        )}
                      </td>
                      <td className="px-1 py-0.5 text-right align-top text-xs text-gray-400">
                        {grandTotal > 0 && data[rowIdx].amount != null
                          ? `${((parseFloat(data[rowIdx].amount) || 0) / grandTotal * 100).toFixed(1)}%`
                          : <span className="text-gray-200">—</span>}
                      </td>
                      <td className="px-0.5 text-center align-top pt-1">
                        <button
                          onClick={() => toggleComment(rowIdx)}
                          title={commentOpen ? "Hide comment" : "Add comment"}
                          className={`text-xs leading-none ${hasComment || commentOpen ? "text-primary-600" : "text-gray-300 hover:text-gray-500"}`}
                        >
                          💬
                        </button>
                      </td>
                      {!readonly && (
                        <td className="px-0.5 text-center align-top pt-1">
                          {indices.length > 1 && (
                            <button
                              onClick={() => removeRow(rowIdx)}
                              className="text-gray-300 hover:text-red-400 text-xs leading-none"
                              title="Remove row"
                            >✕</button>
                          )}
                        </td>
                      )}
                    </tr>
                    {commentOpen && (
                      <tr key={`comment-${rowIdx}`} className="border-b bg-yellow-50">
                        <td />
                        <td colSpan={4} className="px-2 py-1">
                          {readonly && data[rowIdx].comment ? (
                            <p className="text-xs text-gray-600 whitespace-pre-wrap">{data[rowIdx].comment}</p>
                          ) : readonly ? null : (
                            <textarea
                              rows={2}
                              autoFocus
                              className="w-full border border-yellow-200 rounded px-1.5 py-0.5 text-xs bg-white resize-none focus:outline-none focus:border-yellow-400"
                              value={data[rowIdx].comment || ""}
                              onChange={(e) => update(rowIdx, "comment", e.target.value)}
                              placeholder="Add a comment…"
                            />
                          )}
                        </td>
                        {!readonly && <td />}
                      </tr>
                    )}
                  </>
                );
              }).concat(
                !readonly ? [(
                  <tr key={`add-${cat}`} className="border-b last:border-0">
                    <td colSpan={5} className="px-1.5 py-0.5">
                      <button
                        onClick={() => addRow(cat)}
                        className="text-xs text-primary-600 hover:text-primary-800 hover:underline"
                      >
                        + Add row
                      </button>
                    </td>
                    <td />
                  </tr>
                )] : []
              );
            })}
          </tbody>
          <tfoot className="bg-gray-50 border-t">
            <tr>
              <td colSpan={readonly ? 2 : 3} className="px-1.5 py-1 text-sm font-semibold text-gray-600 text-right">Total</td>
              <td className="px-1.5 py-1 text-sm font-semibold text-gray-800 text-right">
                {symbol}{currency === "INR" ? total.toLocaleString("en-IN") : (total / rate).toFixed(2)}
              </td>
              <td className="px-1 py-1 text-xs text-gray-400 text-right">
                {grandTotal > 0 ? `${(total / grandTotal * 100).toFixed(1)}%` : "—"}
              </td>
              <td />{!readonly && <td />}
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}

export function PlanViewer({ plan, readonly = true, onChange }) {
  const [currency, setCurrency] = useState("INR");
  const [rate, setRate] = useState(84);

  if (!plan) return <p className="text-sm text-gray-400">Not available yet.</p>;

  const grandTotalINR = [1, 2, 3].reduce((sum, yr) => {
    const rows = plan.plan_data?.[String(yr)] ?? [];
    return sum + rows.reduce((s, r) => s + (parseFloat(r.amount) || 0), 0);
  }, 0);
  const symbol = currency === "INR" ? "₹" : "$";
  const grandTotalDisplay = currency === "INR"
    ? grandTotalINR.toLocaleString("en-IN")
    : (grandTotalINR / rate).toFixed(2);

  function handleYearChange(year, rows) {
    onChange?.({ ...(plan.plan_data || {}), [String(year)]: rows });
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div className="bg-primary-50 border border-primary-200 rounded-lg px-4 py-2 flex items-center gap-3">
          <span className="text-sm text-primary-700 font-medium">3-Year Grand Total</span>
          <span className="text-lg font-bold text-primary-800">{symbol}{grandTotalDisplay}</span>
        </div>
        <div className="flex items-center gap-3">
        <span className="text-sm font-medium text-gray-600">Amount in</span>
        <span className="inline-flex rounded border border-gray-200 overflow-hidden text-sm">
          <button
            onClick={() => setCurrency("INR")}
            className={`px-2.5 py-1 ${currency === "INR" ? "bg-primary-700 text-white" : "text-gray-500 hover:bg-gray-100"}`}
          >₹</button>
          <button
            onClick={() => setCurrency("USD")}
            className={`px-2.5 py-1 ${currency === "USD" ? "bg-primary-700 text-white" : "text-gray-500 hover:bg-gray-100"}`}
          >$</button>
        </span>
        {currency === "USD" && (
          <span className="inline-flex items-center gap-1.5 text-sm text-gray-500">
            $1&nbsp;=&nbsp;₹
            <input
              type="number"
              min="1"
              value={rate}
              onChange={(e) => setRate(parseFloat(e.target.value) || 1)}
              className="w-16 border border-gray-200 rounded px-2 py-0.5 text-right text-gray-700 focus:outline-none focus:border-primary-400"
            />
          </span>
        )}
        </div>
      </div>

      {[1, 2, 3].map((yr) => (
        <PlanTable
          key={yr}
          year={yr}
          rows={plan.plan_data?.[String(yr)]}
          readonly={readonly}
          onChange={(rows) => handleYearChange(yr, rows)}
          currency={currency}
          rate={rate}
          grandTotal={grandTotalINR}
        />
      ))}
    </div>
  );
}
