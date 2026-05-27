import { getToken, clearAuth } from "../auth";

const BASE = import.meta.env.VITE_API_URL || "/api";

export async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  Object.assign(headers, options.headers); // caller headers win (e.g. preview token)

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearAuth();
    window.location.hash = "#/login";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }

  if (res.status === 204) return null;
  return res.json();
}

export const get = (path) => apiFetch(path);
export const post = (path, body) => apiFetch(path, { method: "POST", body: JSON.stringify(body) });
export const patch = (path, body) => apiFetch(path, { method: "PATCH", body: JSON.stringify(body) });
export const del = (path) => apiFetch(path, { method: "DELETE" });

export async function postForm(path, formData) {
  const token = getToken();
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  // No Content-Type — browser sets it with the multipart boundary automatically
  const res = await fetch(`${BASE}${path}`, { method: "POST", body: formData, headers });
  if (res.status === 401) { clearAuth(); window.location.hash = "#/login"; throw new Error("Unauthorized"); }
  if (!res.ok) { const err = await res.json().catch(() => ({ detail: res.statusText })); throw new Error(err.detail || "Request failed"); }
  return res.json();
}
