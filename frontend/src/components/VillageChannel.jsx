import { useState, useEffect } from "react";
import { apiFetch } from "../api/client";

export function VillageChannel({ villageId }) {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiFetch(`/channels/${villageId}/messages`).then(setMessages).catch(() => {});
  }, [villageId]);

  async function send() {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const msg = await apiFetch(`/channels/${villageId}/messages`, {
        method: "POST",
        body: JSON.stringify({ message: text }),
      });
      setMessages((prev) => [...prev, msg]);
      setText("");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="border rounded-lg p-4 bg-white">
      <h3 className="font-semibold text-gray-700 mb-3">Village Channel</h3>
      <div className="space-y-2 max-h-72 overflow-y-auto mb-3">
        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.author_role === "ADMIN" ? "justify-start" : "justify-end"}`}>
            <div
              className={`rounded-lg px-3 py-2 text-sm max-w-sm
                ${m.author_role === "ADMIN" ? "bg-gray-100 text-gray-800" : "bg-primary-600 text-white"}
              `}
            >
              <span className="block text-xs opacity-60 mb-0.5">{m.author_role}</span>
              {m.message}
            </div>
          </div>
        ))}
        {messages.length === 0 && <p className="text-sm text-gray-400">No messages yet.</p>}
      </div>
      <div className="flex flex-col sm:flex-row gap-2">
        <input
          className="flex-1 border rounded px-3 py-2 text-sm"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Type a message…"
        />
        <button
          onClick={send}
          disabled={loading || !text.trim()}
          className="px-4 py-2 bg-primary-600 text-white rounded text-sm disabled:opacity-50 w-full sm:w-auto"
        >
          Send
        </button>
      </div>
    </div>
  );
}
