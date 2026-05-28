import { useState, useEffect } from "react";
import * as api from "../api/donor";
import { VillageStageTracker } from "../components/VillageStageTracker";

export function DonorView() {
  const [villages, setVillages] = useState([]);
  const [selected, setSelected] = useState(null);
  const [updates, setUpdates] = useState([]);

  useEffect(() => { api.listVillages().then(setVillages).catch(() => {}); }, []);

  async function selectVillage(v) {
    setSelected(v);
    setUpdates(await api.getVillageUpdates(v.id).catch(() => []));
  }

  return (
    <div className="app-shell">
      <div className="app-frame">
      <header className="topbar">
        <div>
          <p className="topbar-kicker">Curated Donor Feed</p>
          <span className="topbar-title">Pancham Donor View</span>
          <p className="topbar-subtitle">A clear, curated window into village progress, lead contacts, and published updates.</p>
        </div>
        <div className="hero-panel max-w-sm">
          <p className="eyebrow text-primary-50/70">Published Only</p>
          <p className="mt-2 text-sm text-primary-50/85">This view exposes only admin-approved villages and updates, preserving internal discussion channels.</p>
        </div>
      </header>
      <div className="content-shell max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1 space-y-2">
          <h2 className="section-title text-xl mb-2">Villages</h2>
          {villages.map((v) => (
            <button
              key={v.id}
              onClick={() => selectVillage(v)}
              className={`w-full text-left p-4 rounded-2xl border text-sm transition-all
                ${selected?.id === v.id ? "border-accent-500 bg-accent-50 shadow-soft" : "bg-white/80 border-white/80 hover:bg-white hover:shadow-soft"}
              `}
            >
              <p className="font-medium">{v.name}</p>
              <p className="text-xs text-ink-500">{v.district}</p>
              <span className="inline-flex mt-2 text-xs bg-primary-100 text-primary-800 rounded-full px-2 py-1">{v.stage}</span>
            </button>
          ))}
          {villages.length === 0 && <p className="surface-card p-5 text-sm text-ink-400">No published villages yet.</p>}
        </div>
        <div className="md:col-span-2">
          {selected ? (
            <div className="space-y-4">
              <div className="surface-card p-5 md:p-6">
                <h2 className="section-title text-3xl mb-1">{selected.name}</h2>
                <p className="text-sm text-ink-500 mb-4">{selected.district}</p>
                {(selected.ngo_name || selected.ngo_contact_name || selected.ngo_contact_phone || selected.village_lead_name || selected.village_lead_phone) && (
                  <div className="info-card mb-4">
                    <p><span className="font-medium">NGO:</span> {selected.ngo_name || "-"}</p>
                    <p><span className="font-medium">Contact:</span> {selected.ngo_contact_name || "-"}{selected.ngo_contact_phone ? ` (${selected.ngo_contact_phone})` : ""}</p>
                    <p><span className="font-medium">Village Lead:</span> {selected.village_lead_name || "-"}{selected.village_lead_phone ? ` (${selected.village_lead_phone})` : ""}</p>
                  </div>
                )}
                <VillageStageTracker stage={selected.stage} subStatus={selected.sub_status} />
              </div>
              {updates.map((u) => (
                <div key={u.id} className="surface-card p-4 md:p-5">
                  <p className="text-sm text-ink-700">{u.description}</p>
                  <p className="text-xs text-ink-400 mt-1">{new Date(u.submitted_at).toLocaleDateString()}</p>
                  {u.media_files?.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {u.media_files.map((m) => (
                        <img key={m.id} src={m.file_url} alt={m.caption || ""} className="w-24 h-24 object-cover rounded-xl border border-primary-100" />
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {updates.length === 0 && <p className="surface-card p-5 text-sm text-ink-400">No published updates for this village.</p>}
            </div>
          ) : (
            <div className="surface-card p-5 text-sm text-ink-400">Select a village to see updates.</div>
          )}
        </div>
      </div>
      </div>
    </div>
  );
}
