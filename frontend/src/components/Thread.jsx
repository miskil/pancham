import { useState, useEffect } from "react";
import { getToken } from "../auth";
import { apiFetch } from "../api/client";

export function Thread({ updateId }) {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiFetch(`/threads/${updateId}/messages`).then(setMessages).catch(() => {});
  }, [updateId]);

  async function send() {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const msg = await apiFetch(`/threads/${updateId}/messages`, {
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
    <div className="border rounded-lg p-3 bg-gray-50 mt-3">
      <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Thread</h4>
      <div className="space-y-2 max-h-48 overflow-y-auto mb-2">
        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.author_role === "ADMIN" ? "justify-start" : "justify-end"}`}>
            <div
              className={`rounded-lg px-3 py-1.5 text-sm max-w-xs
                ${m.author_role === "ADMIN" ? "bg-white border text-gray-800" : "bg-primary-600 text-white"}
              `}
            >
              {m.message}
            </div>
          </div>
        ))}
        {messages.length === 0 && <p className="text-xs text-gray-400">No messages yet.</p>}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded px-2 py-1 text-sm"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Reply…"
        />
        <button
          onClick={send}
          disabled={loading || !text.trim()}
          className="px-3 py-1 bg-primary-600 text-white rounded text-sm disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
