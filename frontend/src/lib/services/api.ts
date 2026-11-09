import { get } from 'svelte/store';
import { logout, setToken, token } from '$lib/stores/auth';

export const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const t = get(token);
  if (t) headers.set('Authorization', `Bearer ${t}`);

  const res = await fetch(`${apiUrl}${path}`, { ...init, headers });

  if (res.status === 401) {
    logout();
    throw new ApiError(401, 'Sesion expirada');
  }
  if (!res.ok) {
    let detail = `${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

/** Descarga un archivo (con Authorization) y dispara el guardado en el navegador. */
async function download(path: string, fallbackName = 'archivo'): Promise<void> {
  const headers = new Headers();
  const t = get(token);
  if (t) headers.set('Authorization', `Bearer ${t}`);
  const res = await fetch(`${apiUrl}${path}`, { headers });
  if (res.status === 401) {
    logout();
    throw new ApiError(401, 'Sesion expirada');
  }
  if (!res.ok) throw new ApiError(res.status, `Error ${res.status}`);

  // Nombre desde Content-Disposition si existe.
  let nombre = fallbackName;
  const cd = res.headers.get('Content-Disposition');
  const m = cd?.match(/filename="?([^"]+)"?/);
  if (m) nombre = m[1];

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = nombre;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  download,
  post: <T>(path: string, body: unknown) =>
    request<T>(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    }),
  del: (path: string) => request<void>(path, { method: 'DELETE' })
};

/** Login OAuth2: usa form-urlencoded con 'username' (=email) y 'password'. */
export async function login(email: string, password: string): Promise<void> {
  const form = new URLSearchParams({ username: email, password });
  const res = await fetch(`${apiUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form
  });
  if (!res.ok) {
    let detail = 'Error de autenticacion';
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail);
  }
  const data = (await res.json()) as { access_token: string };
  setToken(data.access_token);
}

export { ApiError };
