import { useState } from "react";
import { post } from "../api/client";
import { saveAuth, clearMustChangePassword } from "../auth";

function ChangePasswordScreen({ role, onDone }) {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const endpoint = role === "ADMIN" ? "/auth/admin/change-password" : "/auth/village/change-password";

  async function handleSubmit(e) {
    e.preventDefault();
    if (next !== confirm) { setError("Passwords do not match"); return; }
    if (next.length < 8) { setError("New password must be at least 8 characters"); return; }
    setError(null);
    setLoading(true);
    try {
      await post(endpoint, { current_password: current, new_password: next });
      clearMustChangePassword();
      onDone();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell flex items-center justify-center">
      <div className="surface-card w-full max-w-md p-6 md:p-8">
        <p className="eyebrow">Security</p>
        <h2 className="section-title mt-2">Change your password</h2>
        <p className="text-sm text-ink-500 mt-2 mb-6">You must set a new password before continuing. Choose something at least 8 characters long.</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-ink-700 mb-1.5">Temporary password</label>
            <input type="password" value={current} onChange={(e) => setCurrent(e.target.value)} className="w-full px-3.5 py-3 text-sm" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-ink-700 mb-1.5">New password</label>
            <input type="password" value={next} onChange={(e) => setNext(e.target.value)} className="w-full px-3.5 py-3 text-sm" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-ink-700 mb-1.5">Confirm new password</label>
            <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} className="w-full px-3.5 py-3 text-sm" required />
          </div>
          {error && <p className="rounded-2xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full py-3">
            {loading ? "Saving…" : "Set new password"}
          </button>
        </form>
      </div>
    </div>
  );
}

export function LoginView({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mustChange, setMustChange] = useState(false);
  const [loginRole, setLoginRole] = useState(null);
  const [loginVillageId, setLoginVillageId] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = await post("/auth/login", { username, password });
      saveAuth(data.access_token, data.role, data.village_id, data.must_change_password);
      if (data.must_change_password) {
        setLoginRole(data.role);
        setLoginVillageId(data.village_id);
        setMustChange(true);
      } else {
        onLogin(data.role, data.village_id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (mustChange) {
    return <ChangePasswordScreen role={loginRole} onDone={() => onLogin(loginRole, loginVillageId)} />;
  }

  return (
    <div className="app-shell flex items-center justify-center">
      <div className="app-frame w-full max-w-5xl">
        <div className="grid lg:grid-cols-[1.2fr_0.95fr]">
          <section className="topbar min-h-[320px] lg:min-h-[640px]">
            <div className="hero-grid w-full">
              <div>
                <p className="topbar-kicker">Pancham Platform</p>
                <h1 className="topbar-title mt-3">Village development with a field-first command center.</h1>
                <p className="topbar-subtitle">
                  Pancham connects programme teams, village leads, and donors through one shared operating surface for proposals, plans, reporting, and donor visibility.
                </p>
              </div>
              <div className="space-y-4">
                <div className="hero-panel">
                  <p className="eyebrow">For Admin</p>
                  <p className="mt-2 text-sm text-primary-50/85">Onboard villages, review submissions, and publish only the right updates to donors.</p>
                </div>
                <div className="hero-panel">
                  <p className="eyebrow">For Village</p>
                  <p className="mt-2 text-sm text-primary-50/85">Track programme stages, submit status evidence, and manage work against the frozen baseline.</p>
                </div>
              </div>
            </div>
          </section>

          <section className="content-shell flex items-center justify-center bg-white/55">
            <div className="surface-card w-full max-w-md p-6 md:p-8">
              <p className="eyebrow">Secure Sign In</p>
              <h2 className="section-title mt-2">पंचम</h2>
              <p className="text-sm text-ink-500 mt-2 mb-6">Access the right workspace for Admin, Village, or Donor operations.</p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-ink-700 mb-1.5">Username</label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-3.5 py-3 text-sm"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-ink-700 mb-1.5">Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-3.5 py-3 text-sm"
                    required
                  />
                </div>
                {error && <p className="rounded-2xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-sm w-full py-3"
                >
                  {loading ? "Signing in…" : "Sign in"}
                </button>
              </form>

              <div className="info-card mt-5">
                <p className="font-medium text-ink-700">Built for low-friction field operations</p>
                <p className="mt-1 text-ink-500">Fast login, clear programme state, and shared contact context across every role.</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
