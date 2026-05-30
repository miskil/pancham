import { useState, useEffect, useMemo } from "react";
import * as baseApi from "../api/village";
import { apiFetch, postForm } from "../api/client";
import { VillageStageTracker } from "../components/VillageStageTracker";
import { Thread } from "../components/Thread";
import { VillageChannel } from "../components/VillageChannel";
import { PlanMilestonesViewer } from "../components/PlanMilestonesViewer";
import { RichText } from "../components/RichText";
import { PLAN_CATEGORY_OPTIONS, countFilledPlanActivities, flattenPlanActivities, normalizePlanData, sumPlanAmount } from "../components/planData";

const TABS = ["Dashboard", "Proposal", "Evidence", "Org", "Funding", "Plan", "Status"];
const STAGE_PROGRESS = {
  PROPOSAL: 25,
  PLAN: 50,
  ACTIVE: 75,
  COMPLETED: 100,
};

function stageProgress(stage) {
  return STAGE_PROGRESS[stage] ?? 0;
}

function normalizeName(value) {
  if (!value) return "";
  return value.trim().toLowerCase().replace(/\s+/g, " ");
}

function makeApi(token) {
  if (!token) return baseApi;
  const f = (path, opts = {}) => apiFetch(path, { ...opts, headers: { Authorization: `Bearer ${token}`, ...opts.headers } });
  const dl = async (path, method = "POST") => {
    const res = await fetch(`${import.meta.env.VITE_API_URL || "/api"}${path}`, {
      method,
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Request failed");
    }
    const blob = await res.blob();
    const cd = res.headers.get("content-disposition") || "";
    const utf8Match = cd.match(/filename\*=UTF-8''([^;]+)/i);
    const plainMatch = cd.match(/filename="?([^";]+)"?/i);
    const filename = decodeURIComponent((utf8Match && utf8Match[1]) || (plainMatch && plainMatch[1]) || "export.docx");
    return { blob, filename };
  };
  return {
    getMe: () => f("/village/me"),
    getOrg: () => f("/village/org"),
    updateOrg: (b) => f("/village/org", { method: "PATCH", body: JSON.stringify(b) }),
    listFundingRounds: () => f("/village/funding-rounds"),
    updateFundingRound: (roundId, b) => f(`/village/funding-rounds/${roundId}`, { method: "PATCH", body: JSON.stringify(b) }),
    getProposal: () => f("/village/proposal"),
    createProposal: (b) => f("/village/proposal", { method: "POST", body: JSON.stringify(b) }),
    updateProposal: (b) => f("/village/proposal", { method: "PATCH", body: JSON.stringify(b) }),
    createPlan: (b) => f("/village/plan", { method: "POST", body: JSON.stringify(b) }),
    getBaseline: () => f("/village/plan/baseline"),
    updateBaseline: (b) => f("/village/plan/baseline", { method: "PATCH", body: JSON.stringify(b) }),
    getWip: () => f("/village/plan/wip"),
    updateWip: (b) => f("/village/plan/wip", { method: "PATCH", body: JSON.stringify(b) }),
    listUpdates: () => f("/village/status"),
    createUpdate: (b) => f("/village/status", { method: "POST", body: JSON.stringify(b) }),
    getThreadMessages: (uid) => f(`/threads/${uid}/messages`),
    postThreadMessage: (uid, message) => f(`/threads/${uid}/messages`, { method: "POST", body: JSON.stringify({ message }) }),
    getChannelMessages: (vid) => f(`/channels/${vid}/messages`),
    postChannelMessage: (vid, message) => f(`/channels/${vid}/messages`, { method: "POST", body: JSON.stringify({ message }) }),
    uploadMedia: (updateId, formData) => {
      const headers = { Authorization: `Bearer ${token}` };
      return fetch(`${import.meta.env.VITE_API_URL || "/api"}/village/status/${updateId}/media`, { method: "POST", body: formData, headers })
        .then((r) => r.ok ? r.json() : r.json().then((e) => Promise.reject(new Error(e.detail))));
    },
    listEvidence: () => f("/village/evidence"),
    uploadEvidence: (formData) => {
      const headers = { Authorization: `Bearer ${token}` };
      return fetch(`${import.meta.env.VITE_API_URL || "/api"}/village/evidence`, { method: "POST", body: formData, headers })
        .then((r) => r.ok ? r.json() : r.json().then((e) => Promise.reject(new Error(e.detail))));
    },
    deleteEvidence: (id) => f(`/village/evidence/${id}`, { method: "DELETE" }),
    exportProposal: (id) => dl(`/admin/export/proposals/${id}`, "POST"),
    exportPlan: (id) => dl(`/admin/export/plans/${id}`, "POST"),
  };
}

function ExportDocxButton({ onExport }) {
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    try {
      const { blob, filename } = await onExport();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert("Export failed: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <button onClick={run} disabled={loading} className="btn-sm bg-gray-700 disabled:opacity-60">
      {loading ? "Exporting..." : "Export DOCX"}
    </button>
  );
}

export function VillageView({ previewToken } = {}) {
  const api = useMemo(() => makeApi(previewToken), [previewToken]);
  const [tab, setTab] = useState("Dashboard");
  const [me, setMe] = useState(null);

  useEffect(() => { api.getMe().then(setMe).catch(() => {}); }, [api]);

  const proposalAccepted = me && !["CREATED", "PROPOSAL_SUBMITTED", "UNDER_REVIEW", "AMENDMENT_REQUESTED", "AMENDED"].includes(me.internal_status);

  return (
    <div className="app-shell">
      <div className="app-frame">
      <header className="topbar">
        <div className="flex gap-8 items-start w-full">
          <div>
            <span className="topbar-title">Pancham</span>
          </div>
          {me && (
            <div className="flex-1">
              <p className="topbar-subtitle">{me.name} • {me.district}, {me.taluka}</p>
              {(me.village_lead_name || me.fcra_number || me.ngo_name) && (
                <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-primary-50/75">
                  {me.village_lead_name && <span><span className="text-primary-50/50">Lead</span> {me.village_lead_name}{me.village_lead_phone ? ` · ${me.village_lead_phone}` : ""}</span>}
                  {(me.fcra_number || me.ngo_name) && (
                    <span>
                      <span className="text-primary-50/50">FCRA</span> {me.fcra_number || me.ngo_name}
                      {me.fcra_expiry_date ? ` · Expires ${me.fcra_expiry_date}` : ""}
                    </span>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </header>

      {me && (
        <div className="bg-white/55 border-b border-primary-100/60 px-4 pt-4 pb-2 md:px-6">
          <VillageStageTracker stage={me.stage} subStatus={me.sub_status} />
        </div>
      )}

      <div className="tabbar">
        {TABS.map((t) => {
          const locked = t === "Plan" && !proposalAccepted;
          return (
            <button
              key={t}
              onClick={() => !locked && setTab(t)}
              className={`tab-pill ${tab === t ? "tab-pill-active" : "tab-pill-idle"}
                ${locked ? "opacity-40 cursor-not-allowed" : ""}
              `}
            >
              {t} {locked && "🔒"}
            </button>
          );
        })}
      </div>

      <div className="content-shell max-w-4xl mx-auto">
        {tab === "Dashboard" && <DashboardTab me={me} api={api} />}
        {tab === "Proposal" && <ProposalTab me={me} onUpdate={setMe} api={api} />}
        {tab === "Evidence" && <EvidenceTab api={api} />}
        {tab === "Org" && <OrgTab api={api} />}
        {tab === "Funding" && <FundingTab api={api} me={me} />}
        {tab === "Plan" && proposalAccepted && <ProjectTab me={me} api={api} />}
        {tab === "Status" && <StatusTab me={me} api={api} />}
      </div>
      </div>
    </div>
  );
}

function DashboardTab({ me, api }) {
  const [loading, setLoading] = useState(true);
  const [proposal, setProposal] = useState(null);
  const [proposalLoadError, setProposalLoadError] = useState(null);
  const [baseline, setBaseline] = useState(null);
  const [wip, setWip] = useState(null);
  const [updates, setUpdates] = useState([]);

  useEffect(() => {
    let mounted = true;
    Promise.all([
      api.getProposal().catch((err) => {
        if (mounted) setProposalLoadError(err.message || "Failed to load proposal");
        return null;
      }),
      api.getBaseline().catch(() => null),
      api.getWip().catch(() => null),
      api.listUpdates().catch(() => []),
    ]).then(([proposalData, baselineData, wipData, updatesData]) => {
      if (!mounted) return;
      setProposal(proposalData);
      setBaseline(baselineData);
      setWip(wipData);
      setUpdates(updatesData);
      setLoading(false);
    });
    return () => { mounted = false; };
  }, [api]);

  if (!me || loading) {
    return <div className="bg-white rounded-xl border p-5 text-sm text-gray-400">Loading dashboard...</div>;
  }

  const progress = stageProgress(me.stage);
  const publishedCount = updates.filter((u) => u.is_published).length;
  const currentPlan = wip || baseline;
  const normalizedPlan = currentPlan ? normalizePlanData(currentPlan.plan_data || {}) : null;
  const planRows = currentPlan ? flattenPlanActivities(currentPlan.plan_data || {}) : [];
  const filledRows = currentPlan ? countFilledPlanActivities(currentPlan.plan_data || {}) : 0;
  const planFillPercent = planRows.length ? Math.round((filledRows / planRows.length) * 100) : 0;
  const milestoneCount = normalizedPlan
    ? Object.values(normalizedPlan).reduce((sum, milestones) => sum + milestones.length, 0)
    : 0;
  const totalSpent = currentPlan ? sumPlanAmount(currentPlan.plan_data || {}) : 0;
  const impactMilestones = normalizedPlan
    ? Object.values(normalizedPlan).flat().filter((milestone) => (milestone.impact || "").trim()).length
    : 0;
  const impactPreview = normalizedPlan
    ? Object.values(normalizedPlan)
        .flat()
        .map((milestone) => (milestone.impact || "").trim())
        .find(Boolean)
    : "";

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border p-5">
        <div className="flex items-center justify-between mb-2">
          <h2 className="font-semibold text-gray-700">Village Progress</h2>
          <span className="text-sm text-primary-700 font-semibold">{progress}%</span>
        </div>
        <div className="h-3 rounded bg-gray-100 overflow-hidden">
          <div className="h-full bg-primary-600" style={{ width: `${progress}%` }} />
        </div>
        <p className="text-xs text-gray-500 mt-2">{me.stage} • {me.sub_status}</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
        <StatCard label="Milestones" value={currentPlan ? `${milestoneCount}` : "—"} note={currentPlan ? "across 3 years" : "Submit a plan to start"} />
        <StatCard label="% Complete" value={currentPlan ? `${planFillPercent}%` : "—"} note={currentPlan ? `${filledRows}/${planRows.length} activities filled` : "Activities and notes will drive progress"} />
        <StatCard label="$ Spent" value={currentPlan ? `$${totalSpent.toLocaleString("en-IN")}` : "—"} note={currentPlan ? "Total planned amount" : "Plan totals appear here"} />
        <StatCard
          label="Impact"
          value={currentPlan ? `${impactMilestones} milestone${impactMilestones === 1 ? "" : "s"}` : "—"}
          note={currentPlan ? (impactPreview || "Add an impact statement inside each milestone") : "Impact statements appear here"}
        />
      </div>

      {proposalLoadError && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
          Proposal could not be loaded: {proposalLoadError}
        </div>
      )}

      <div className="bg-white rounded-xl border p-5">
        <h3 className="font-medium text-gray-700 mb-3">Plan Highlights</h3>
        {currentPlan ? (
          <ul className="space-y-2 text-sm text-gray-700">
            <li>{milestoneCount > 0 ? "✓" : "○"} {milestoneCount} milestones across the 3-year plan</li>
            <li>{planFillPercent > 0 ? "✓" : "○"} {planFillPercent}% of activities filled out</li>
            <li>{totalSpent > 0 ? "✓" : "○"} Planned spend totals $ {totalSpent.toLocaleString("en-IN")}</li>
            <li>{impactMilestones > 0 ? "✓" : "○"} Impact defined for {impactMilestones} milestones</li>
          </ul>
        ) : (
          <p className="text-sm text-gray-400">Submit a plan to see milestone, spending, and impact summaries.</p>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, note }) {
  return (
    <div className="bg-white rounded-xl border p-4 space-y-1.5">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-base font-semibold text-gray-800 mt-1">{value}</p>
      {note && <p className="text-xs text-gray-500 leading-snug">{note}</p>}
    </div>
  );
}

function ProposalTab({ me, onUpdate, api }) {
  const [proposal, setProposal] = useState(null);
  const [form, setForm] = useState({ focus_areas: [], per_capita_income: "", description: "", community_context: "", key_activities: "" });
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState(null);
  const [noProposal, setNoProposal] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const readonly = proposal?.status === "ACCEPTED";

  useEffect(() => {
    api.getProposal().then((p) => {
      setNoProposal(false);
      setLoadError(null);
      setProposal(p);
      setForm({
        focus_areas: p.focus_areas || (p.focus_area ? p.focus_area.split(",").map((item) => item.trim()).filter(Boolean) : []),
        per_capita_income: p.per_capita_income || "",
        description: p.description || "",
        community_context: p.community_context || "",
        key_activities: p.key_activities || "",
      });
    }).catch((err) => {
      if ((err.message || "").toLowerCase().includes("no proposal yet")) {
        setLoadError(null);
        setNoProposal(true);
        return;
      }
      setNoProposal(false);
      setLoadError(err.message || "Failed to load proposal");
    });
  }, [api]);

  async function save(submit) {
    console.log("save called, submit=", submit);
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      const body = { ...form, submit };
      const p = proposal
        ? await api.updateProposal(body)
        : await api.createProposal(body);
      setProposal(p);
      setSuccess(submit ? "Proposal submitted!" : "Draft saved.");
      if (submit) {
        const fresh = await api.getMe();
        onUpdate(fresh);
      }
    } catch (err) {
      console.error("save error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const STATUS_LABELS = {
    DRAFT: { label: "Draft", color: "bg-gray-100 text-gray-600" },
    SUBMITTED: { label: "Submitted — awaiting review", color: "bg-blue-100 text-blue-700" },
    UNDER_REVIEW: { label: "Under review", color: "bg-yellow-100 text-yellow-700" },
    AMENDMENT_REQUESTED: { label: "Amendment requested", color: "bg-orange-100 text-orange-700" },
    AMENDED: { label: "Amendment submitted", color: "bg-blue-100 text-blue-700" },
    ACCEPTED: { label: "Accepted", color: "bg-green-100 text-green-700" },
    DECLINED: { label: "Declined", color: "bg-red-100 text-red-700" },
  };
  const canEdit = !proposal || ["DRAFT", "AMENDMENT_REQUESTED"].includes(proposal?.status);

  function toggleFocusArea(code) {
    setForm((prev) => {
      const current = prev.focus_areas || [];
      const next = current.includes(code)
        ? current.filter((item) => item !== code)
        : [...current, code];
      return { ...prev, focus_areas: next };
    });
  }

  return (
    <div className="bg-white rounded-xl border p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-gray-700">Village Proposal</h2>
        <div className="flex items-center gap-2">
          {proposal && <ExportDocxButton onExport={() => api.exportProposal(proposal.id)} />}
          {proposal && (
            <span className={`text-xs font-medium rounded-full px-3 py-1 ${STATUS_LABELS[proposal.status]?.color}`}>
              {STATUS_LABELS[proposal.status]?.label ?? proposal.status}
            </span>
          )}
        </div>
      </div>
      <p className="text-xs text-gray-500">Current Village ID: {me?.id || "unknown"}</p>

      {proposal?.reviewer_notes && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
          <strong>Admin notes:</strong> {proposal.reviewer_notes}
        </div>
      )}
      {noProposal && !proposal && (
        <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-blue-800">
          No proposal record found for this village ID on the current server.
        </div>
      )}
      {loadError && <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">Proposal could not be loaded: {loadError}</div>}

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Focus Areas</label>
        {canEdit ? (
          <div className="flex flex-wrap gap-1.5">
            {PLAN_CATEGORY_OPTIONS.map((item) => {
              const active = (form.focus_areas || []).includes(item.code);
              return (
                <button
                  key={item.code}
                  type="button"
                  onClick={() => toggleFocusArea(item.code)}
                  className={`rounded-full px-2.5 py-1 text-xs font-medium border transition-colors ${
                    active
                      ? "bg-primary-600 text-white border-primary-600"
                      : "bg-white text-gray-600 border-gray-300 hover:border-primary-300"
                  }`}
                  title={item.title}
                >
                  {item.code}
                </button>
              );
            })}
          </div>
        ) : (
          <p className="text-sm text-gray-800 bg-gray-50 rounded px-3 py-2 min-h-8">
            {(form.focus_areas || []).length > 0 ? (form.focus_areas || []).join(", ") : <span className="text-gray-400 italic">Not filled in</span>}
          </p>
        )}
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">गावाच दर डोई उत्पन्न</label>
        {canEdit ? (
          <input
            className="w-full border rounded px-3 py-2 text-sm"
            value={form.per_capita_income}
            onChange={(e) => setForm((p) => ({ ...p, per_capita_income: e.target.value }))}
          />
        ) : (
          <p className="text-sm text-gray-800 bg-gray-50 rounded px-3 py-2 min-h-8">
            {form.per_capita_income || <span className="text-gray-400 italic">Not filled in</span>}
          </p>
        )}
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">गावाची भौगोलीक आणि सामाजीक माहिती</label>
        {canEdit ? (
          <textarea
            className="w-full border rounded px-3 py-2 text-sm h-24"
            value={form.description}
            onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
          />
        ) : (
          <p className="text-sm text-gray-800 bg-gray-50 rounded px-3 py-2 min-h-8 whitespace-pre-wrap">
            {form.description || <span className="text-gray-400 italic">Not filled in</span>}
          </p>
        )}
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">गावाची गरज</label>
        {canEdit ? (
          <textarea
            className="w-full border rounded px-3 py-2 text-sm h-24"
            value={form.community_context}
            onChange={(e) => setForm((p) => ({ ...p, community_context: e.target.value }))}
          />
        ) : (
          <p className="text-sm text-gray-800 bg-gray-50 rounded px-3 py-2 min-h-8 whitespace-pre-wrap">
            {form.community_context || <span className="text-gray-400 italic">Not filled in</span>}
          </p>
        )}
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">गावा साठी काय करता येईल</label>
        {canEdit ? (
          <textarea
            className="w-full border rounded px-3 py-2 text-sm h-24"
            value={form.key_activities}
            onChange={(e) => setForm((p) => ({ ...p, key_activities: e.target.value }))}
          />
        ) : (
          <p className="text-sm text-gray-800 bg-gray-50 rounded px-3 py-2 min-h-8 whitespace-pre-wrap">
            {form.key_activities || <span className="text-gray-400 italic">Not filled in</span>}
          </p>
        )}
      </div>
      {error && <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-700">{error}</div>}
      {success && <div className="bg-green-50 border border-green-200 rounded p-3 text-sm text-green-700">{success}</div>}

      {canEdit && (
        <div className="flex gap-3">
          <button onClick={() => save(false)} disabled={loading} className="btn-sm bg-gray-400">
            {loading ? "Saving…" : "Save Draft"}
          </button>
          <button onClick={() => save(true)} disabled={loading} className="btn-sm bg-primary-700">
            {loading ? "Submitting…" : proposal?.status === "AMENDMENT_REQUESTED" ? "Resubmit" : "Submit"}
          </button>
        </div>
      )}
    </div>
  );
}

function OrgTab({ api }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    fcra_number: "",
    fcra_expiry_date: "",
    ngo_contact_name: "",
    ngo_contact_phone: "",
    village_lead_name: "",
    village_lead_phone: "",
    ngo_whatsapp_phone: "",
    vdc_members: Array.from({ length: 5 }, () => ({ name: "", role: "", phone: "" })),
  });

  useEffect(() => {
    api.getOrg().then((data) => {
      const members = [...(data.vdc_members || [])]
        .slice(0, 5)
        .map((m) => ({ name: m.name || "", role: m.role || "", phone: m.phone || "" }));
      while (members.length < 5) members.push({ name: "", role: "", phone: "" });
      setForm({
        fcra_number: data.fcra_number || data.ngo_name || "",
        fcra_expiry_date: data.fcra_expiry_date || "",
        ngo_contact_name: data.ngo_contact_name || "",
        ngo_contact_phone: data.ngo_contact_phone || "",
        village_lead_name: data.village_lead_name || "",
        village_lead_phone: data.village_lead_phone || "",
        ngo_whatsapp_phone: data.ngo_whatsapp_phone || "",
        vdc_members: members,
      });
    }).catch(() => {}).finally(() => setLoading(false));
  }, [api]);

  function updateMember(i, key, value) {
    setForm((prev) => {
      const next = [...prev.vdc_members];
      next[i] = { ...next[i], [key]: value };
      return { ...prev, vdc_members: next };
    });
  }

  async function save() {
    setSaving(true);
    try {
      await api.updateOrg({
        fcra_number: form.fcra_number,
        fcra_expiry_date: form.fcra_expiry_date || null,
        ngo_contact_name: form.ngo_contact_name,
        ngo_contact_phone: form.ngo_contact_phone,
        village_lead_name: form.village_lead_name,
        village_lead_phone: form.village_lead_phone,
        ngo_whatsapp_phone: form.ngo_whatsapp_phone,
        vdc_members: form.vdc_members.filter((m) => m.name.trim()),
      });
      alert("Org details saved");
    } catch (err) {
      alert(err.message);
    } finally {
      setSaving(false);
    }
  }

  const waNumber = (form.ngo_whatsapp_phone || "").replace(/[^\d]/g, "");
  const waLink = waNumber ? `https://wa.me/${waNumber}` : "";

  if (loading) {
    return <div className="bg-white rounded-xl border p-5 text-sm text-gray-400">Loading org details…</div>;
  }

  return (
    <div className="bg-white rounded-xl border p-5 space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-gray-700">Organization</h2>
        <div className="flex items-center gap-2">
          {waLink && (
            <a href={waLink} target="_blank" rel="noopener noreferrer" className="btn-sm bg-green-600">
              WhatsApp NGO
            </a>
          )}
          <button onClick={save} disabled={saving} className="btn-sm bg-primary-700 disabled:opacity-60">
            {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </div>

      <div className="rounded-lg border bg-gray-50 p-3 text-sm text-gray-700 space-y-3">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Village Lead</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <input
              className="border rounded px-3 py-2 text-sm"
              placeholder="Lead name"
              value={form.village_lead_name}
              onChange={(e) => setForm((p) => ({ ...p, village_lead_name: e.target.value }))}
            />
            <input
              className="border rounded px-3 py-2 text-sm"
              placeholder="Lead contact"
              value={form.village_lead_phone}
              onChange={(e) => setForm((p) => ({ ...p, village_lead_phone: e.target.value }))}
            />
          </div>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">FCRA Number</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <input
              className="border rounded px-3 py-2 text-sm"
              value={form.fcra_number}
              onChange={(e) => setForm((p) => ({ ...p, fcra_number: e.target.value }))}
              placeholder="FCRA number"
            />
            <input
              type="date"
              className="border rounded px-3 py-2 text-sm"
              value={form.fcra_expiry_date}
              onChange={(e) => setForm((p) => ({ ...p, fcra_expiry_date: e.target.value }))}
            />
          </div>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Contact</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <input
              className="border rounded px-3 py-2 text-sm"
              placeholder="Contact person"
              value={form.ngo_contact_name}
              onChange={(e) => setForm((p) => ({ ...p, ngo_contact_name: e.target.value }))}
            />
            <input
              className="border rounded px-3 py-2 text-sm"
              placeholder="Contact phone"
              value={form.ngo_contact_phone}
              onChange={(e) => setForm((p) => ({ ...p, ngo_contact_phone: e.target.value }))}
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="sm:col-span-2">
          <label className="block text-xs font-medium text-gray-600 mb-1">WhatsApp Phone</label>
          <input className="w-full border rounded px-3 py-2 text-sm" value={form.ngo_whatsapp_phone}
            onChange={(e) => setForm((p) => ({ ...p, ngo_whatsapp_phone: e.target.value }))}
            placeholder="e.g. 919876543210"
          />
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">VDC Members (up to 5)</h3>
        <div className="space-y-2">
          {form.vdc_members.map((m, i) => (
            <div key={i} className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <input
                className="border rounded px-3 py-2 text-sm"
                placeholder={`Member ${i + 1} Name`}
                value={m.name}
                onChange={(e) => updateMember(i, "name", e.target.value)}
              />
              <input
                className="border rounded px-3 py-2 text-sm"
                placeholder="Role"
                value={m.role}
                onChange={(e) => updateMember(i, "role", e.target.value)}
              />
              <input
                className="border rounded px-3 py-2 text-sm"
                placeholder="Phone"
                value={m.phone}
                onChange={(e) => updateMember(i, "phone", e.target.value)}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function FundingTab({ api, me }) {
  const [loading, setLoading] = useState(true);
  const [savingRoundId, setSavingRoundId] = useState(null);
  const [rounds, setRounds] = useState([]);
  const canEditFunding = (me?.current_user_type || "").toUpperCase() === "NGO";

  useEffect(() => {
    api.listFundingRounds().then((data) => {
      setRounds(data.map((item) => ({
        ...item,
        funding_sent_date: item.funding_sent_date || "",
        funding_received_date: item.funding_received_date || "",
        funding_amount: item.funding_amount != null ? String(item.funding_amount) : "",
        admin_funding_note: item.admin_funding_note || item.funding_status_note || "",
        village_funding_note: item.village_funding_note || item.funding_status_note || "",
        funding_received_message: item.funding_received_message || "",
      })));
    }).catch(() => {}).finally(() => setLoading(false));
  }, [api]);

  function updateRound(roundId, key, value) {
    setRounds((prev) => prev.map((item) => item.id === roundId ? { ...item, [key]: value } : item));
  }

  async function saveRound(roundId) {
    const current = rounds.find((item) => item.id === roundId);
    if (!current) return;
    setSavingRoundId(roundId);
    try {
      const updated = await api.updateFundingRound(roundId, {
        funding_received_date: current.funding_received_date || null,
        admin_funding_note: current.admin_funding_note,
        village_funding_note: current.village_funding_note,
        funding_received_message: current.funding_received_message || null,
      });
      setRounds((prev) => prev.map((item) => item.id === roundId ? {
        ...updated,
        funding_sent_date: updated.funding_sent_date || "",
        funding_received_date: updated.funding_received_date || "",
        funding_amount: updated.funding_amount != null ? String(updated.funding_amount) : "",
        admin_funding_note: updated.admin_funding_note || updated.funding_status_note || "",
        village_funding_note: updated.village_funding_note || updated.funding_status_note || "",
        funding_received_message: updated.funding_received_message || "",
      } : item));
    } catch (err) {
      alert(err.message);
    } finally {
      setSavingRoundId(null);
    }
  }

  const totalFunding = rounds.reduce((sum, item) => sum + (Number(item.funding_amount) || 0), 0);

  if (loading) {
    return <div className="bg-white rounded-xl border p-5 text-sm text-gray-400">Loading funding rounds...</div>;
  }

  return (
    <div className="bg-white rounded-xl border p-5 space-y-4">
      {!canEditFunding && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          Funding is read-only. Only NGO lead can update received details.
        </div>
      )}
      <div>
        <p className="text-xs text-gray-500">Total Funding</p>
        <p className="text-2xl font-semibold text-gray-800">₹ {totalFunding.toLocaleString("en-IN")}</p>
      </div>

      {rounds.length === 0 && <p className="text-sm text-gray-400">No funding rounds yet.</p>}

      {rounds.map((round) => (
        <div key={round.id} className="rounded-xl border p-4 space-y-4 bg-gray-50">
          <div className="flex items-center justify-between gap-3">
            <h3 className="font-semibold text-gray-700">Round {round.round_number}</h3>
            <button onClick={() => saveRound(round.id)} disabled={savingRoundId === round.id || !canEditFunding} className="btn-sm bg-primary-700 disabled:opacity-60">
              {savingRoundId === round.id ? "Saving..." : "Save Round"}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="rounded-lg border bg-white p-3 space-y-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Sender (Admin)</p>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Funding Sent Date</label>
                <input type="date" className="w-full border rounded px-3 py-2 text-sm bg-gray-50" value={round.funding_sent_date} readOnly />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Funding Amount</label>
                <input type="number" className="w-full border rounded px-3 py-2 text-sm bg-gray-50" value={round.funding_amount} readOnly />
              </div>
            </div>

            <div className="rounded-lg border bg-white p-3 space-y-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Receiver (Village)</p>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Funding Received Date</label>
                <input type="date" className="w-full border rounded px-3 py-2 text-sm" value={round.funding_received_date} onChange={(e) => updateRound(round.id, "funding_received_date", e.target.value)} readOnly={!canEditFunding} />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Received Message for Audit</label>
                <textarea className="w-full border rounded px-3 py-2 text-sm h-24" value={round.funding_received_message} onChange={(e) => updateRound(round.id, "funding_received_message", e.target.value)} placeholder="Village audit message" readOnly={!canEditFunding} />
              </div>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Admin Funding Note</label>
            <textarea className="w-full border rounded px-3 py-2 text-sm h-24 bg-gray-50" value={round.admin_funding_note} readOnly placeholder="Admin note will appear here" />
            <label className="block text-xs font-medium text-gray-600 mb-1">Village Funding Note</label>
            <textarea className="w-full border rounded px-3 py-2 text-sm h-24 bg-white" value={round.village_funding_note} onChange={(e) => updateRound(round.id, "village_funding_note", e.target.value)} placeholder="Village-only note" readOnly={!canEditFunding} />
          </div>
        </div>
      ))}
    </div>
  );
}

const DOC_TYPE_LABELS = {
  GRAMSABHA: "Gramsabha Letter",
  PANCHAYAT: "Panchayat Letter",
  OTHER: "Other Document",
};

function EvidenceTab({ api }) {
  const [docs, setDocs] = useState([]);
  const [docType, setDocType] = useState("GRAMSABHA");
  const [notes, setNotes] = useState("");
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => { api.listEvidence().then(setDocs).catch(() => {}); }, [api]);

  async function upload(e) {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const fd = new FormData();
      fd.append("doc_type", docType);
      fd.append("notes", notes);
      fd.append("file", file);
      const doc = await api.uploadEvidence(fd);
      setDocs((prev) => [doc, ...prev]);
      setFile(null);
      setNotes("");
      e.target.reset();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function remove(id) {
    try {
      await api.deleteEvidence(id);
      setDocs((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      alert(err.message);
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border p-5">
        <h2 className="font-semibold text-gray-700 mb-1">Support Evidence</h2>
        <p className="text-xs text-gray-500 mb-4">
          Upload scanned copies of letters from Gramsabha and Panchayat supporting Pancham in your village.
        </p>

        <form onSubmit={upload} className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Document Type</label>
            <select
              className="w-full border rounded px-3 py-2 text-sm"
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
            >
              {Object.entries(DOC_TYPE_LABELS).map(([val, label]) => (
                <option key={val} value={val}>{label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">File</label>
            <input
              type="file"
              required
              accept=".pdf,.jpg,.jpeg,.png"
              className="w-full text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <p className="text-xs text-gray-400 mt-0.5">PDF, JPG or PNG accepted</p>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Notes (optional)</label>
            <input
              type="text"
              className="w-full border rounded px-3 py-2 text-sm"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Resolution dated 12 Jan 2026"
            />
          </div>

          {error && <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded p-2">{error}</div>}

          <button type="submit" disabled={uploading || !file} className="btn-sm bg-primary-700 disabled:opacity-60">
            {uploading ? "Uploading…" : "Upload Document"}
          </button>
        </form>
      </div>

      {docs.length > 0 && (
        <div className="bg-white rounded-xl border p-5">
          <h3 className="font-medium text-gray-700 mb-3">Uploaded Documents</h3>
          <div className="space-y-2">
            {docs.map((d) => (
              <div key={d.id} className="flex items-start justify-between gap-3 p-3 border rounded-lg bg-gray-50">
                <div className="min-w-0">
                  <span className="inline-block text-xs font-medium bg-primary-100 text-primary-700 rounded px-2 py-0.5 mb-1">
                    {DOC_TYPE_LABELS[d.doc_type] ?? d.doc_type}
                  </span>
                  <p className="text-sm text-gray-700 truncate">{d.filename}</p>
                  {d.notes && <p className="text-xs text-gray-500 mt-0.5">{d.notes}</p>}
                  <p className="text-xs text-gray-400 mt-0.5">{new Date(d.uploaded_at).toLocaleDateString()}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <a
                    href={d.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-primary-600 hover:underline"
                  >
                    View
                  </a>
                  <button
                    onClick={() => remove(d.id)}
                    className="text-xs text-red-400 hover:text-red-600"
                    title="Delete"
                  >✕</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {docs.length === 0 && (
        <p className="text-sm text-gray-400 text-center py-4">No documents uploaded yet.</p>
      )}
    </div>
  );
}

function VillageOrgReadOnly({ village }) {
  if (!village) return null;
  const hasOrg = village.fcra_number || village.ngo_name || village.ngo_contact_name || village.ngo_contact_phone || village.village_lead_name || village.village_lead_phone;
  if (!hasOrg) return null;
  return (
    <div className="mt-3 rounded-lg border bg-gray-50 p-3 text-sm text-gray-700">
      <p><span className="font-medium">FCRA Number:</span> {village.fcra_number || village.ngo_name || "-"}</p>
      <p><span className="font-medium">FCRA Expiry:</span> {village.fcra_expiry_date || "-"}</p>
      <p><span className="font-medium">Contact:</span> {village.ngo_contact_name || "-"}{village.ngo_contact_phone ? ` (${village.ngo_contact_phone})` : ""}</p>
      <p><span className="font-medium">Village Lead:</span> {village.village_lead_name || "-"}{village.village_lead_phone ? ` (${village.village_lead_phone})` : ""}</p>
    </div>
  );
}

function ProjectTab({ me, api }) {
  const [baseline, setBaseline] = useState(null);
  const [wip, setWip] = useState(null);
  const [draftData, setDraftData] = useState(null);
  const [lastDraftSavedAt, setLastDraftSavedAt] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState("wip"); // "baseline" | "wip"

  useEffect(() => {
    api.getBaseline().then((data) => {
      setBaseline(data);
      if (data?.updated_at) {
        setLastDraftSavedAt(new Date(data.updated_at));
      }
    }).catch(() => {});
    api.getWip().then((data) => {
      setWip(data);
      if (data?.updated_at) {
        setLastDraftSavedAt((prev) => {
          if (!prev) return new Date(data.updated_at);
          const next = new Date(data.updated_at);
          return next > prev ? next : prev;
        });
      }
    }).catch(() => {});
  }, [api]);

  async function saveBaselineDraft() {
    setSaving(true);
    setError(null);
    try {
      const currentBaseline = baseline
        ? await api.updateBaseline({ plan_data: draftData ?? baseline.plan_data, submit: false })
        : await api.createPlan({ plan_data: draftData, submit: false });
      setBaseline(currentBaseline);
      setDraftData(null);
      setLastDraftSavedAt(currentBaseline?.updated_at ? new Date(currentBaseline.updated_at) : new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function submitPlan() {
    setSaving(true);
    setError(null);
    try {
      const submittedBaseline = baseline
        ? await api.updateBaseline({ plan_data: draftData ?? baseline.plan_data, submit: true })
        : await api.createPlan({ plan_data: draftData, submit: true });
      setBaseline(submittedBaseline);
      setDraftData(null);
    } catch (err) { setError(err.message); } finally { setSaving(false); }
  }

  async function saveWip() {
    if (!draftData) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await api.updateWip({ plan_data: draftData });
      setWip(updated);
      setDraftData(null);
      setLastDraftSavedAt(updated?.updated_at ? new Date(updated.updated_at) : new Date());
    } catch (err) { setError(err.message); } finally { setSaving(false); }
  }

  if (!baseline) {
    return (
      <div className="bg-white rounded-xl border p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-700">3-Year Activity Plan</h2>
          <div className="flex items-center gap-2">
            <button onClick={saveBaselineDraft} disabled={saving} className="btn-sm bg-gray-400">
              {saving ? "Saving..." : "Save Draft"}
            </button>
            <button onClick={submitPlan} disabled={saving} className="btn-sm bg-primary-700">
              {saving ? "Submitting…" : "Submit Plan"}
            </button>
          </div>
        </div>
        {error && <div className="mb-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded p-2">{error}</div>}
        <PlanMilestonesViewer
          plan={{ plan_data: draftData }}
          readonly={false}
          onChange={setDraftData}
        />
      </div>
    );
  }

  const frozen = baseline.status === "FROZEN";
  const baselineEditable = ["DRAFT", "AMENDMENT_REQUESTED"].includes(baseline.status);
  const baselineDataForView = draftData ?? baseline.plan_data;
  const currentWipData = draftData ?? wip?.plan_data;
  const exportPlanId = wip?.id || baseline?.id;

  return (
    <div className="space-y-4">
      <div className="flex gap-2 bg-white border rounded-lg p-1 w-fit">
        <button
          onClick={() => setActiveView("baseline")}
          className={`px-4 py-1.5 rounded text-sm font-medium transition-colors
            ${activeView === "baseline" ? "bg-primary-700 text-white" : "text-gray-500 hover:text-gray-700"}`}
        >
          Baseline
        </button>
        <button
          onClick={() => setActiveView("wip")}
          className={`px-4 py-1.5 rounded text-sm font-medium transition-colors
            ${activeView === "wip" ? "bg-primary-700 text-white" : "text-gray-500 hover:text-gray-700"}`}
        >
          WIP
        </button>
      </div>

      {exportPlanId && (
        <div>
          <ExportDocxButton onExport={() => api.exportPlan(exportPlanId)} />
        </div>
      )}

      {error && <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded p-2">{error}</div>}
      {lastDraftSavedAt && (
        <div className="text-xs text-green-700 bg-green-50 border border-green-200 rounded px-3 py-2">
          Draft saved at {lastDraftSavedAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </div>
      )}

      {activeView === "baseline" && (
        <div className="bg-white rounded-xl border p-5">
          <div className="flex items-center gap-2 mb-4">
            <h2 className="font-semibold text-gray-700">Baseline Plan</h2>
            <span className="text-xs bg-gray-100 text-gray-500 rounded px-2 py-0.5">
              {baseline.status === "FROZEN" ? "Frozen - read only" : baseline.status}
            </span>
            {baselineEditable && (
              <div className="ml-auto flex gap-2">
                <button onClick={saveBaselineDraft} disabled={saving} className="btn-sm bg-gray-400">
                  {saving ? "Saving..." : "Save Draft"}
                </button>
                <button onClick={submitPlan} disabled={saving} className="btn-sm bg-primary-700">
                  {saving ? "Submitting..." : baseline.status === "AMENDMENT_REQUESTED" ? "Resubmit Plan" : "Submit Plan"}
                </button>
              </div>
            )}
          </div>
          {baseline.reviewer_notes && (
            <div className="mb-3 bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
              <strong>Admin amendment notes:</strong> {baseline.reviewer_notes}
            </div>
          )}
          <PlanMilestonesViewer
            plan={{ ...baseline, plan_data: baselineDataForView }}
            readonly={!baselineEditable}
            onChange={baselineEditable ? setDraftData : undefined}
          />
        </div>
      )}

      {activeView === "wip" && (
        <div className="bg-white rounded-xl border p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-700">WIP Plan</h2>
            {wip && draftData && (
              <button onClick={saveWip} disabled={saving} className="btn-sm bg-primary-700">
                {saving ? "Saving…" : "Save Changes"}
              </button>
            )}
          </div>
          {wip ? (
            <PlanMilestonesViewer
              plan={{ plan_data: currentWipData }}
              readonly={false}
              onChange={setDraftData}
            />
          ) : (
            <p className="text-sm text-gray-400">WIP plan not yet created — admin must accept the baseline first.</p>
          )}
        </div>
      )}
    </div>
  );
}

function StatusTab({ me, api }) {
  const [updates, setUpdates] = useState([]);
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useState(null);

  useEffect(() => { api.listUpdates().then(setUpdates).catch(() => {}); }, [api]);

  async function post() {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const u = await api.createUpdate({ description: text });
      if (file) {
        const fd = new FormData();
        fd.append("file", file);
        const media = await api.uploadMedia(u.id, fd);
        u.media_files = [media];
      }
      setUpdates((prev) => [u, ...prev]);
      setText("");
      setFile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border p-4">
        <h2 className="font-semibold text-gray-700 mb-3">Post Update</h2>
        <textarea
          className="w-full border rounded px-3 py-2 text-sm h-24 mb-2"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="What's happening in the village…"
        />
        <div className="flex items-center gap-3">
          <label className="cursor-pointer flex items-center gap-1.5 text-sm text-gray-500 hover:text-primary-600">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828L18 9.828a4 4 0 00-5.656-5.656L5.757 10.757a6 6 0 108.486 8.486L20 13" />
            </svg>
            {file ? file.name : "Attach image or video"}
            <input
              type="file"
              accept="image/*,video/*"
              className="hidden"
              onChange={(e) => setFile(e.target.files[0] || null)}
            />
          </label>
          {file && (
            <button onClick={() => setFile(null)} className="text-xs text-red-400 hover:text-red-600">✕ Remove</button>
          )}
        </div>
        {file && file.type.startsWith("image/") && (
          <img src={URL.createObjectURL(file)} alt="preview" className="mt-2 rounded border" />
        )}
        {file && file.type.startsWith("video/") && (
          <video src={URL.createObjectURL(file)} className="mt-2 max-h-40 w-full rounded border" controls />
        )}
        {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
        <button
          onClick={post}
          disabled={loading || !text.trim()}
          className="mt-3 btn-sm bg-primary-700 disabled:opacity-60"
        >
          {loading ? "Posting…" : "Post"}
        </button>
      </div>

      {me && <VillageChannel villageId={me.id} />}

      <div className="space-y-3">
        {updates.map((u) => (
          <div key={u.id} className="bg-white rounded-xl border p-4">
            <p className="text-xs text-gray-400 mb-2">
              {new Date(u.submitted_at).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" })}
            </p>
            {(u.media_files || []).map((m) => (
              m.media_type === "PHOTO"
                ? <img key={m.id} src={m.file_url} alt="" className="w-full rounded mb-2" />
                : <video key={m.id} src={m.file_url} controls className="w-full rounded mb-2" />
            ))}
            <RichText text={u.description} />
            {u.is_published && <span className="text-xs text-green-600 font-medium mt-1 block">Published</span>}
            <button onClick={() => setSelected(selected?.id === u.id ? null : u)} className="text-xs text-primary-600 mt-1 block">
              {selected?.id === u.id ? "Hide thread" : "View thread"}
            </button>
            {selected?.id === u.id && <Thread updateId={u.id} />}
          </div>
        ))}
      </div>
    </div>
  );
}
