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
    <div className="min-h-screen bg-gray-50">
      <header className="bg-primary-800 text-white px-4 py-3">
        <span className="font-bold text-lg">Pancham</span>
        <span className="ml-2 text-primary-200 text-sm">Donor View</span>
      </header>
      <div className="p-4 max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1 space-y-2">
          <h2 className="font-semibold text-gray-700 text-sm mb-2">Villages</h2>
          {villages.map((v) => (
            <button
              key={v.id}
              onClick={() => selectVillage(v)}
              className={`w-full text-left p-3 rounded-lg border text-sm
                ${selected?.id === v.id ? "border-primary-600 bg-primary-50" : "bg-white hover:bg-gray-50"}
              `}
            >
              <p className="font-medium">{v.name}</p>
              <p className="text-xs text-gray-500">{v.district}</p>
              <span className="text-xs bg-primary-100 text-primary-800 rounded px-1.5 py-0.5">{v.stage}</span>
            </button>
          ))}
          {villages.length === 0 && <p className="text-sm text-gray-400">No published villages yet.</p>}
        </div>
        <div className="md:col-span-2">
          {selected ? (
            <div className="space-y-4">
              <div className="bg-white rounded-xl border p-5">
                <h2 className="font-semibold text-lg text-gray-800 mb-1">{selected.name}</h2>
                <p className="text-sm text-gray-500 mb-4">{selected.district}</p>
                {(selected.ngo_name || selected.ngo_contact_name || selected.ngo_contact_phone || selected.village_lead_name || selected.village_lead_phone) && (
                  <div className="mb-4 rounded-lg border bg-gray-50 p-3 text-sm text-gray-700">
                    <p><span className="font-medium">NGO:</span> {selected.ngo_name || "-"}</p>
                    <p><span className="font-medium">Contact:</span> {selected.ngo_contact_name || "-"}{selected.ngo_contact_phone ? ` (${selected.ngo_contact_phone})` : ""}</p>
                    <p><span className="font-medium">Village Lead:</span> {selected.village_lead_name || "-"}{selected.village_lead_phone ? ` (${selected.village_lead_phone})` : ""}</p>
                  </div>
                )}
                <VillageStageTracker stage={selected.stage} subStatus={selected.sub_status} />
              </div>
              {updates.map((u) => (
                <div key={u.id} className="bg-white rounded-xl border p-4">
                  <p className="text-sm text-gray-700">{u.description}</p>
                  <p className="text-xs text-gray-400 mt-1">{new Date(u.submitted_at).toLocaleDateString()}</p>
                  {u.media_files?.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {u.media_files.map((m) => (
                        <img key={m.id} src={m.file_url} alt={m.caption || ""} className="w-24 h-24 object-cover rounded-lg border" />
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {updates.length === 0 && <p className="text-sm text-gray-400">No published updates for this village.</p>}
            </div>
          ) : (
            <div className="bg-white rounded-xl border p-5 text-sm text-gray-400">Select a village to see updates.</div>
          )}
        </div>
      </div>
    </div>
  );
}
