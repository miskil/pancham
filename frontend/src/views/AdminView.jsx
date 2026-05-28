import { useState, useEffect } from "react";
import * as api from "../api/admin";
import { VillageStageTracker } from "../components/VillageStageTracker";
import { VillageChannel } from "../components/VillageChannel";
import { Thread } from "../components/Thread";
import { PlanViewer } from "../components/PlanViewer";
import { RichText } from "../components/RichText";
import { VillageView } from "./VillageView";

const TABS = ["Dashboard", "Onboard", "Proposals", "Plans", "Status", "Org"];
const VILLAGE_VIEW_ENABLED = import.meta.env.VITE_ADMIN_VILLAGE_VIEW === "true";
const STAGE_PROGRESS = {
  PROPOSAL: 25,
  PLAN: 50,
  ACTIVE: 75,
  COMPLETED: 100,
};

function stageProgress(stage) {
  return STAGE_PROGRESS[stage] ?? 0;
}

function ExportDriveButton({ onExport }) {
  const [state, setState] = useState("idle"); // idle | loading | done | error

  async function handleClick() {
    setState("loading");
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
      setState("done");
    } catch (err) {
      setState("error");
      alert("Export failed: " + err.message);
    }
  }

  return (
    <button onClick={handleClick} disabled={state === "loading"}
      className="btn-sm bg-gray-700 disabled:opacity-50">
      {state === "loading" ? "Exporting…" : "Export DOCX"}
    </button>
  );
}

export function AdminView() {
  const [tab, setTab] = useState("Dashboard");
  const [preview, setPreview] = useState(null); // { token, village_name }

  if (preview) {
    return (
      <div>
        <div className="bg-yellow-400 text-yellow-900 px-4 py-2 flex items-center justify-between text-sm font-medium">
          <span>Previewing as village: <strong>{preview.village_name}</strong></span>
          <button onClick={() => setPreview(null)} className="underline">Back to Admin</button>
        </div>
        <VillageView previewToken={preview.token} />
      </div>
    );
  }

  return (
    <div className="app-shell">
      <div className="app-frame">
      <header className="topbar">
        <div>
          <p className="topbar-kicker">Operations Console</p>
          <span className="topbar-title">Pancham Admin</span>
          <p className="topbar-subtitle">Manage village onboarding, keep review cycles moving, and curate donor-facing reporting from one production workspace.</p>
        </div>
        <div className="hero-panel max-w-sm">
          <p className="eyebrow text-primary-50/70">Control Surface</p>
          <p className="mt-2 text-sm text-primary-50/85">Every village record, stage, contact, and publishing action stays visible without losing the field context.</p>
        </div>
      </header>
      <div className="tabbar">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`tab-pill ${tab === t ? "tab-pill-active" : "tab-pill-idle"}
            `}
          >
            {t}
          </button>
        ))}
      </div>
      <div className="content-shell max-w-6xl mx-auto">
        {tab === "Dashboard" && <DashboardTab />}
        {tab === "Onboard" && <OnboardTab villageViewEnabled={VILLAGE_VIEW_ENABLED} onPreview={setPreview} />}
        {tab === "Proposals" && <ProposalsTab />}
        {tab === "Plans" && <PlansTab />}
        {tab === "Status" && <StatusTab />}
        {tab === "Org" && <OrgTab />}
      </div>
      </div>
    </div>
  );
}

function DashboardTab() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({ villages: [], proposals: [], plans: [], updates: [] });

  useEffect(() => {
    let mounted = true;
    Promise.all([
      api.listVillages().catch(() => []),
      api.listProposals().catch(() => []),
      api.listPlans().catch(() => []),
      api.listStatusUpdates().catch(() => []),
    ]).then(([villages, proposals, plans, updates]) => {
      if (!mounted) return;
      setData({ villages, proposals, plans, updates });
      setLoading(false);
    });
    return () => { mounted = false; };
  }, []);

  if (loading) {
    return <div className="surface-card p-5 text-sm text-ink-400">Loading dashboard...</div>;
  }

  const { villages, proposals, plans, updates } = data;
  const total = villages.length;
  const active = villages.filter((v) => v.is_active).length;
  const completed = villages.filter((v) => v.stage === "COMPLETED").length;
  const avgProgress = total ? Math.round(villages.reduce((sum, v) => sum + stageProgress(v.stage), 0) / total) : 0;
  const proposalReviewQueue = proposals.filter((p) => ["SUBMITTED", "AMENDED", "UNDER_REVIEW"].includes(p.status)).length;
  const planReviewQueue = plans.filter((p) => p.status === "SUBMITTED").length;
  const publishedUpdates = updates.filter((u) => u.is_published).length;
  const stageCounts = {
    PROPOSAL: villages.filter((v) => v.stage === "PROPOSAL").length,
    PLAN: villages.filter((v) => v.stage === "PLAN").length,
    ACTIVE: villages.filter((v) => v.stage === "ACTIVE").length,
    COMPLETED: villages.filter((v) => v.stage === "COMPLETED").length,
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Villages" value={String(total)} />
        <StatCard label="Active Accounts" value={String(active)} />
        <StatCard label="Avg Progress" value={`${avgProgress}%`} />
        <StatCard label="Completed" value={String(completed)} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <StatCard label="Proposal Review Queue" value={String(proposalReviewQueue)} />
        <StatCard label="Plan Review Queue" value={String(planReviewQueue)} />
        <StatCard label="Published Updates" value={`${publishedUpdates}/${updates.length}`} />
      </div>

      <div className="bg-white rounded-xl border p-5">
        <h2 className="font-semibold text-gray-700 mb-3">Village Stage Distribution</h2>
        <div className="space-y-2">
          {Object.entries(stageCounts).map(([stage, count]) => (
            <div key={stage}>
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>{stage}</span>
                <span>{count}</span>
              </div>
              <div className="h-2 rounded bg-gray-100 overflow-hidden">
                <div
                  className="h-full bg-primary-600"
                  style={{ width: `${total ? Math.round((count / total) * 100) : 0}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border p-5">
        <h2 className="font-semibold text-gray-700 mb-3">Progress by Village</h2>
        {villages.length === 0 ? (
          <p className="text-sm text-gray-400">No villages available.</p>
        ) : (
          <div className="space-y-2">
            {villages.map((v) => {
              const pct = stageProgress(v.stage);
              return (
                <div key={v.id} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-gray-700">{v.name}</span>
                    <span className="text-gray-500">{v.stage} • {pct}%</span>
                  </div>
                  <div className="h-2 rounded bg-gray-100 mt-2 overflow-hidden">
                    <div className="h-full bg-primary-600" style={{ width: `${pct}%` }} />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{v.sub_status || "No sub-status"}</p>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-xl border p-4">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-2xl font-semibold text-gray-800 mt-1">{value}</p>
    </div>
  );
}

function OnboardTab({ villageViewEnabled, onPreview }) {
  const [villages, setVillages] = useState([]);
  const [form, setForm] = useState({
    name: "",
    district: "",
    taluka: "",
    population: "",
    ngo_name: "",
    ngo_contact_name: "",
    ngo_contact_phone: "",
    village_lead_name: "",
    village_lead_phone: "",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { api.listVillages().then(setVillages).catch(() => {}); }, []);

  async function previewVillage(id, name) {
    try {
      const data = await api.getPreviewToken(id);
      onPreview({ token: data.access_token, village_name: name });
    } catch (err) { alert(err.message); }
  }

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const v = await api.onboardVillage({ ...form, population: form.population ? +form.population : null });
      setResult(v);
      setVillages((prev) => [v, ...prev]);
      setForm({
        name: "",
        district: "",
        taluka: "",
        population: "",
        ngo_name: "",
        ngo_contact_name: "",
        ngo_contact_phone: "",
        village_lead_name: "",
        village_lead_phone: "",
      });
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border p-5">
        <h2 className="font-semibold text-gray-700 mb-4">Onboard a Village</h2>
        <form onSubmit={submit} className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {["name", "district", "taluka"].map((f) => (
            <div key={f}>
              <label className="block text-xs font-medium text-gray-600 mb-1 capitalize">{f}</label>
              <input
                required
                className="w-full border rounded px-3 py-2 text-sm"
                value={form[f]}
                onChange={(e) => setForm((p) => ({ ...p, [f]: e.target.value }))}
              />
            </div>
          ))}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Population</label>
            <input
              type="number"
              className="w-full border rounded px-3 py-2 text-sm"
              value={form.population}
              onChange={(e) => setForm((p) => ({ ...p, population: e.target.value }))}
            />
          </div>
          <div className="sm:col-span-2 grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Village Lead Name</label>
              <input
                className="w-full border rounded px-3 py-2 text-sm"
                value={form.village_lead_name}
                onChange={(e) => setForm((p) => ({ ...p, village_lead_name: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Village Lead Contact</label>
              <input
                className="w-full border rounded px-3 py-2 text-sm"
                value={form.village_lead_phone}
                onChange={(e) => setForm((p) => ({ ...p, village_lead_phone: e.target.value }))}
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">NGO Name</label>
            <input
              className="w-full border rounded px-3 py-2 text-sm"
              value={form.ngo_name}
              onChange={(e) => setForm((p) => ({ ...p, ngo_name: e.target.value }))}
            />
          </div>
          <div className="sm:col-span-2 grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Contact Person</label>
              <input
                className="w-full border rounded px-3 py-2 text-sm"
                value={form.ngo_contact_name}
                onChange={(e) => setForm((p) => ({ ...p, ngo_contact_name: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Contact Phone</label>
              <input
                className="w-full border rounded px-3 py-2 text-sm"
                value={form.ngo_contact_phone}
                onChange={(e) => setForm((p) => ({ ...p, ngo_contact_phone: e.target.value }))}
              />
            </div>
          </div>
          <div className="sm:col-span-2">
            <button type="submit" disabled={loading} className="bg-primary-700 text-white rounded px-4 py-2 text-sm disabled:opacity-60">
              {loading ? "Creating…" : "Create Village"}
            </button>
          </div>
        </form>
        {result && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded text-sm">
            <p className="font-medium text-green-800">Village created</p>
            <p>Username: <strong>{result.login_username}</strong></p>
            <p>Temp password: <strong>{result.temp_password}</strong></p>
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl border p-5">
        <h2 className="font-semibold text-gray-700 mb-3">All Villages</h2>
        {villages.length === 0 ? (
          <p className="text-sm text-gray-400">No villages yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead><tr className="text-left text-gray-500 border-b">
              <th className="pb-2">Name</th><th className="pb-2">District</th>
              <th className="pb-2">NGO</th><th className="pb-2">NGO Contact</th>
              <th className="pb-2">Village Lead</th>
              <th className="pb-2">Stage</th><th className="pb-2">Active</th>
              {villageViewEnabled && <th className="pb-2"></th>}
            </tr></thead>
            <tbody>
              {villages.map((v) => (
                <tr key={v.id} className="border-b last:border-0">
                  <td className="py-2">{v.name}</td>
                  <td className="py-2 text-gray-500">{v.district}</td>
                  <td className="py-2 text-gray-600">{v.ngo_name || "-"}</td>
                  <td className="py-2 text-gray-600">{v.ngo_contact_name || v.ngo_contact_phone || "-"}</td>
                  <td className="py-2 text-gray-600">{v.village_lead_name || v.village_lead_phone || "-"}</td>
                  <td className="py-2"><span className="bg-primary-100 text-primary-800 text-xs rounded px-2 py-0.5">{v.stage}</span></td>
                  <td className="py-2">{v.is_active ? "✓" : <button onClick={() => api.deactivateVillage(v.id).then(() => setVillages((p) => p.map((x) => x.id === v.id ? { ...x, is_active: false } : x)))} className="text-red-500 text-xs">Deactivate</button>}</td>
                  {villageViewEnabled && <td className="py-2"><button onClick={() => previewVillage(v.id, v.name)} className="text-xs text-primary-600 hover:underline">View as Village</button></td>}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function ProposalsTab() {
  const [proposals, setProposals] = useState([]);
  const [villageMeta, setVillageMeta] = useState({});
  const [selected, setSelected] = useState(null);
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setLoadError(null);
    api.listVillages()
      .then((items) => setVillageMeta(Object.fromEntries(items.map((v) => [v.id, v]))))
      .catch(() => {});
    api.listProposals()
      .then(setProposals)
      .catch((err) => setLoadError(err.message || "Failed to load proposals"))
      .finally(() => setLoading(false));
  }, []);

  const selectedVillage = selected ? villageMeta[selected.village_id] : null;

  async function act(action) {
    try {
      await action(selected.id, notes);
      const updated = await api.listProposals();
      setProposals(updated);
      setSelected(updated.find((p) => p.id === selected.id) || null);
    } catch (err) { alert(err.message); }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="md:col-span-1 space-y-2">
        {loading && <p className="text-sm text-gray-400">Loading proposals...</p>}
        {loadError && <p className="text-sm text-red-600">Could not load proposals: {loadError}</p>}
        {proposals.map((p) => (
          <button
            key={p.id}
            onClick={() => { setSelected(p); setNotes(""); }}
            className={`w-full text-left p-3 rounded-lg border text-sm
              ${selected?.id === p.id ? "border-primary-600 bg-primary-50" : "bg-white hover:bg-gray-50"}
            `}
          >
            <p className="font-medium">{p.village_name}</p>
            <p className="text-xs text-gray-500">{p.status}</p>
          </button>
        ))}
        {!loading && !loadError && proposals.length === 0 && <p className="text-sm text-gray-400">No proposals yet.</p>}
      </div>
      <div className="md:col-span-2">
        {selected ? (
          <div className="bg-white rounded-xl border p-5 space-y-4">
            <VillageStageTracker stage={selected.stage || "PROPOSAL"} subStatus={selected.sub_status} />
            <h2 className="font-semibold">{selected.village_name}</h2>
            <VillageOrgReadOnly village={selectedVillage} />
            <div className="space-y-2 text-sm">
              {["focus_area", "description", "community_context", "key_activities"].map((f) => selected[f] && (
                <div key={f}>
                  <span className="text-xs text-gray-500 uppercase">{f.replace("_", " ")}</span>
                  <p className="text-gray-800">{selected[f]}</p>
                </div>
              ))}
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Notes</label>
              <textarea className="w-full border rounded px-3 py-2 text-sm h-20" value={notes} onChange={(e) => setNotes(e.target.value)} />
            </div>
            <div className="flex flex-wrap gap-2">
              {selected.status === "SUBMITTED" && <button onClick={() => act(api.reviewProposal)} className="btn-sm bg-blue-600">Mark Under Review</button>}
              {["UNDER_REVIEW", "AMENDED"].includes(selected.status) && (
                <>
                  <button onClick={() => act(api.acceptProposal)} className="btn-sm bg-green-600">Accept</button>
                  <button onClick={() => act(api.requestAmendment)} className="btn-sm bg-yellow-500">Request Amendment</button>
                  <button onClick={() => act(api.declineProposal)} className="btn-sm bg-red-500">Decline</button>
                </>
              )}
              <ExportDriveButton onExport={() => api.exportProposal(selected.id)} />
            </div>
            <VillageChannel villageId={selected.village_id} />
            <EvidencePanel villageId={selected.village_id} />
          </div>
        ) : (
          <div className="bg-white rounded-xl border p-5 text-sm text-gray-400">Select a proposal.</div>
        )}
      </div>
    </div>
  );
}

const DOC_TYPE_LABELS = {
  GRAMSABHA: "Gramsabha Letter",
  PANCHAYAT: "Panchayat Letter",
  OTHER: "Other Document",
};

function EvidencePanel({ villageId }) {
  const [docs, setDocs] = useState([]);

  useEffect(() => {
    api.getVillageEvidence(villageId).then(setDocs).catch(() => {});
  }, [villageId]);

  if (docs.length === 0) return (
    <div className="border-t pt-4">
      <h3 className="text-sm font-semibold text-gray-600 mb-1">Support Evidence</h3>
      <p className="text-xs text-gray-400">No documents uploaded by village.</p>
    </div>
  );

  return (
    <div className="border-t pt-4">
      <h3 className="text-sm font-semibold text-gray-600 mb-3">Support Evidence</h3>
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
            <a
              href={d.file_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-primary-600 hover:underline shrink-0"
            >
              View
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

function PlansTab() {
  const [plans, setPlans] = useState([]);
  const [villageMeta, setVillageMeta] = useState({});
  const [selected, setSelected] = useState(null);
  const [draftData, setDraftData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.listVillages()
      .then((items) => setVillageMeta(Object.fromEntries(items.map((v) => [v.id, v]))))
      .catch(() => {});
    api.listPlans().then(setPlans).catch(() => {});
  }, []);

  function selectPlan(p) {
    setSelected(p);
    setDraftData(null);
    setError(null);
  }

  const frozen = selected?.status === "FROZEN";
  const canEdit = selected && !frozen;

  async function save() {
    if (!draftData) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await api.updatePlan(selected.id, draftData);
      setSelected(updated);
      setPlans((prev) => prev.map((p) => p.id === updated.id ? updated : p));
      setDraftData(null);
    } catch (err) { setError(err.message); } finally { setSaving(false); }
  }

  async function accept() {
    setSaving(true);
    setError(null);
    try {
      await api.acceptPlan(selected.id);
      const updated = await api.listPlans();
      setPlans(updated);
      setSelected(updated.find((x) => x.id === selected.id) || null);
      setDraftData(null);
    } catch (err) { setError(err.message); } finally { setSaving(false); }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="md:col-span-1 space-y-2">
        {plans.map((p) => (
          <button key={p.id} onClick={() => selectPlan(p)}
            className={`w-full text-left p-3 rounded-lg border text-sm ${selected?.id === p.id ? "border-primary-600 bg-primary-50" : "bg-white hover:bg-gray-50"}`}>
            <p className="font-medium">{p.village_name}</p>
            <p className="text-xs text-gray-500">{p.status}</p>
          </button>
        ))}
        {plans.length === 0 && <p className="text-sm text-gray-400">No plans submitted.</p>}
      </div>

      <div className="md:col-span-2">
        {selected ? (
          <div className="bg-white rounded-xl border p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="font-semibold">{selected.village_name}</h2>
                <span className={`text-xs rounded px-2 py-0.5 ${frozen ? "bg-gray-100 text-gray-500" : "bg-blue-100 text-blue-700"}`}>
                  {selected.status}
                </span>
              </div>
              <div className="flex gap-2">
                {canEdit && draftData && (
                  <button onClick={save} disabled={saving} className="btn-sm bg-primary-700">
                    {saving ? "Saving…" : "Save"}
                  </button>
                )}
                {selected.status === "SUBMITTED" && (
                  <button onClick={accept} disabled={saving} className="btn-sm bg-green-600">
                    {saving ? "…" : "Accept & Freeze"}
                  </button>
                )}
                <ExportDriveButton onExport={() => api.exportPlan(selected.id)} />
              </div>
            </div>
            <VillageOrgReadOnly village={selected ? villageMeta[selected.village_id] : null} />
            {error && <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded p-2">{error}</div>}
            <PlanViewer
              plan={{ plan_data: draftData ?? selected.plan_data }}
              readonly={frozen}
              onChange={setDraftData}
            />
          </div>
        ) : <div className="bg-white rounded-xl border p-5 text-sm text-gray-400">Select a plan.</div>}
      </div>
    </div>
  );
}

function OrgTab() {
  const [villages, setVillages] = useState([]);
  const [villageId, setVillageId] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    ngo_name: "",
    ngo_contact_name: "",
    ngo_contact_phone: "",
    village_lead_name: "",
    village_lead_phone: "",
    ngo_whatsapp_phone: "",
    vdc_members: Array.from({ length: 5 }, () => ({ name: "", role: "", phone: "" })),
  });

  useEffect(() => {
    api.listVillages().then((data) => {
      setVillages(data);
      if (data.length) setVillageId(data[0].id);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!villageId) return;
    setLoading(true);
    api.getVillageOrg(villageId).then((data) => {
      const members = [...(data.vdc_members || [])]
        .slice(0, 5)
        .map((m) => ({ name: m.name || "", role: m.role || "", phone: m.phone || "" }));
      while (members.length < 5) members.push({ name: "", role: "", phone: "" });
      setForm({
        ngo_name: data.ngo_name || "",
        ngo_contact_name: data.ngo_contact_name || "",
        ngo_contact_phone: data.ngo_contact_phone || "",
        village_lead_name: data.village_lead_name || "",
        village_lead_phone: data.village_lead_phone || "",
        ngo_whatsapp_phone: data.ngo_whatsapp_phone || "",
        vdc_members: members,
      });
    }).catch(() => {}).finally(() => setLoading(false));
  }, [villageId]);

  function updateMember(i, key, value) {
    setForm((prev) => {
      const next = [...prev.vdc_members];
      next[i] = { ...next[i], [key]: value };
      return { ...prev, vdc_members: next };
    });
  }

  async function save() {
    if (!villageId) return;
    setSaving(true);
    try {
      await api.updateVillageOrg(villageId, {
        ngo_name: form.ngo_name,
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

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border p-4 flex items-center gap-3">
        <label className="text-sm font-medium text-gray-600 whitespace-nowrap">Village</label>
        <select
          className="flex-1 border rounded px-3 py-2 text-sm"
          value={villageId}
          onChange={(e) => setVillageId(e.target.value)}
        >
          {villages.map((v) => (
            <option key={v.id} value={v.id}>{v.name} ({v.district})</option>
          ))}
        </select>
      </div>

      {!villageId && (
        <div className="bg-white rounded-xl border p-8 text-sm text-gray-400">No villages available.</div>
      )}

      {villageId && (
        <div className="bg-white rounded-xl border p-5 space-y-5">
          {loading && <p className="text-sm text-gray-400">Loading org details...</p>}
          {!loading && (
            <>
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
                  <label className="block text-xs font-medium text-gray-600 mb-1">NGO</label>
                  <input
                    className="w-full border rounded px-3 py-2 text-sm"
                    value={form.ngo_name}
                    onChange={(e) => setForm((p) => ({ ...p, ngo_name: e.target.value }))}
                  />
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
            </>
          )}
        </div>
      )}
    </div>
  );
}

function StatusTab() {
  const [villages, setVillages] = useState([]);
  const [villageId, setVillageId] = useState("");
  const [updates, setUpdates] = useState([]);
  const [openThread, setOpenThread] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { api.listVillages().then(setVillages).catch(() => {}); }, []);

  useEffect(() => {
    if (!villageId) { setUpdates([]); return; }
    setLoading(true);
    api.listStatusUpdates(villageId).then(setUpdates).catch(() => {}).finally(() => setLoading(false));
  }, [villageId]);

  async function togglePublish(u) {
    try {
      if (u.is_published) await api.unpublishUpdate(u.id);
      else await api.publishUpdate(u.id);
      setUpdates((prev) => prev.map((x) => x.id === u.id ? { ...x, is_published: !x.is_published } : x));
    } catch (err) { alert(err.message); }
  }

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border p-4 flex items-center gap-3">
        <label className="text-sm font-medium text-gray-600 whitespace-nowrap">Village</label>
        <select
          className="flex-1 border rounded px-3 py-2 text-sm"
          value={villageId}
          onChange={(e) => { setVillageId(e.target.value); setOpenThread(null); }}
        >
          <option value="">— select a village —</option>
          {villages.map((v) => (
            <option key={v.id} value={v.id}>{v.name} ({v.district})</option>
          ))}
        </select>
      </div>

      {villageId && (
        <div className="overflow-y-auto max-h-[calc(100vh-220px)] space-y-4 pr-1">
          <VillageOrgReadOnly village={villages.find((v) => v.id === villageId)} />
          {loading && <p className="text-sm text-gray-400 text-center py-6">Loading…</p>}
          {!loading && updates.length === 0 && (
            <p className="text-sm text-gray-400 text-center py-6">No status posts from this village yet.</p>
          )}
          {updates.map((u) => (
            <div key={u.id} className="bg-white rounded-xl border p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400">
                  {new Date(u.submitted_at).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" })}
                </span>
                <div className="flex items-center gap-2">
                  {u.is_published && (
                    <span className="text-xs text-green-600 font-medium bg-green-50 px-2 py-0.5 rounded">Published</span>
                  )}
                  <button
                    onClick={() => togglePublish(u)}
                    className={`btn-sm ${u.is_published ? "bg-gray-400" : "bg-green-600"}`}
                  >
                    {u.is_published ? "Unpublish" : "Publish to Donor"}
                  </button>
                </div>
              </div>

              {(u.media_files || []).map((m) => (
                m.media_type === "PHOTO"
                  ? <img key={m.id} src={m.file_url} alt="" className="w-full rounded" />
                  : <video key={m.id} src={m.file_url} controls className="w-full rounded" />
              ))}

              <RichText text={u.description} />

              <button
                onClick={() => setOpenThread(openThread === u.id ? null : u.id)}
                className="text-xs text-primary-600 hover:underline"
              >
                {openThread === u.id ? "Hide thread" : "View thread"}
              </button>
              {openThread === u.id && <Thread updateId={u.id} />}
            </div>
          ))}
        </div>
      )}

      {!villageId && (
        <div className="bg-white rounded-xl border p-8 text-center text-sm text-gray-400">
          Select a village to view status updates.
        </div>
      )}
    </div>
  );
}

function VillageOrgReadOnly({ village }) {
  if (!village) return null;
  const hasOrg = village.ngo_name || village.ngo_contact_name || village.ngo_contact_phone || village.village_lead_name || village.village_lead_phone;
  if (!hasOrg) return null;
  return (
    <div className="rounded-lg border bg-gray-50 p-3 text-sm text-gray-700">
      <p><span className="font-medium">NGO:</span> {village.ngo_name || "-"}</p>
      <p><span className="font-medium">Contact:</span> {village.ngo_contact_name || "-"}{village.ngo_contact_phone ? ` (${village.ngo_contact_phone})` : ""}</p>
      <p><span className="font-medium">Village Lead:</span> {village.village_lead_name || "-"}{village.village_lead_phone ? ` (${village.village_lead_phone})` : ""}</p>
    </div>
  );
}
