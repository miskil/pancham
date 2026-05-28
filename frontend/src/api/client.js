import { getToken, clearAuth } from "../auth";

const PRIMARY_BASE = import.meta.env.VITE_API_URL || "/api";
const RAILWAY_BACKEND_FALLBACK = "https://pancham-server.up.railway.app";
const BASES = [...new Set([PRIMARY_BASE, RAILWAY_BACKEND_FALLBACK])];

async function fetchWithFallback(path, options) {
  let lastError = null;
  for (const base of BASES) {
    try {
      return await fetch(`${base}${path}`, options);
    } catch (err) {
      lastError = err;
    }
  }
  const origin = typeof window !== "undefined" ? window.location.origin : "unknown-origin";
  const attempted = BASES.join(", ");
  const reason = lastError?.message || "Failed to fetch";
  throw new Error(`Network/CORS error from ${origin} to [${attempted}]: ${reason}`);
}

export async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  Object.assign(headers, options.headers); // caller headers win (e.g. preview token)

  const res = await fetchWithFallback(path, { ...options, headers });

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

export async function download(path, method = "POST") {
  const token = getToken();
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetchWithFallback(path, { method, headers });

  if (res.status === 401) {
    clearAuth();
    window.location.hash = "#/login";
    throw new Error("Unauthorized");
  }

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
}

export async function postForm(path, formData) {
  const token = getToken();
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  // No Content-Type — browser sets it with the multipart boundary automatically
  const res = await fetchWithFallback(path, { method: "POST", body: formData, headers });
  if (res.status === 401) { clearAuth(); window.location.hash = "#/login"; throw new Error("Unauthorized"); }
  if (!res.ok) { const err = await res.json().catch(() => ({ detail: res.statusText })); throw new Error(err.detail || "Request failed"); }
  return res.json();
}
