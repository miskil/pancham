import { useState, useEffect } from "react";
import { getUser, isLoggedIn, clearAuth } from "./auth";
import { LoginView } from "./views/LoginView";
import { AdminView } from "./views/AdminView";
import { VillageView } from "./views/VillageView";
import { DonorView } from "./views/DonorView";

export default function App() {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (isLoggedIn()) setUser(getUser());
    setReady(true);
  }, []);

  function handleLogin(role, villageId) {
    setUser({ role, villageId });
  }

  function handleLogout() {
    clearAuth();
    setUser(null);
  }

  if (!ready) return null;

  if (!user) return <LoginView onLogin={handleLogin} />;

  return (
    <div className="relative">
      <button
        onClick={handleLogout}
        className="fixed top-3 right-3 z-50 text-xs bg-white border rounded px-2 py-1 text-gray-500 shadow-sm hover:bg-gray-50"
      >
        Logout
      </button>
      {user.role === "ADMIN" && <AdminView />}
      {user.role === "VILLAGE" && <VillageView />}
      {user.role === "DONOR" && <DonorView />}
    </div>
  );
}
