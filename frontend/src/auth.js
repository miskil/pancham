const TOKEN_KEY = "pancham_token";
const USER_KEY = "pancham_user";

export function saveAuth(token, role, villageId = null, mustChangePassword = false) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify({ role, villageId, mustChangePassword }));
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function isLoggedIn() {
  return !!getToken();
}

export function mustChangePassword() {
  const user = getUser();
  return user?.mustChangePassword === true;
}

export function clearMustChangePassword() {
  const user = getUser();
  if (user) {
    user.mustChangePassword = false;
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}
