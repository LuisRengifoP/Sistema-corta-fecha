import { browser } from '$app/environment';
import { writable } from 'svelte/store';

const KEY = 'cf_token';

function leerToken(): string | null {
  if (!browser) return null;
  try {
    return localStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export const token = writable<string | null>(leerToken());

export function setToken(value: string | null) {
  token.set(value);
  if (!browser) return;
  try {
    if (value) localStorage.setItem(KEY, value);
    else localStorage.removeItem(KEY);
  } catch {
    /* ignore */
  }
}

/**
 * Borra la cache de respuestas de la API del Service Worker.
 *
 * Esas respuestas se guardan por URL, sin el usuario que las pidio, asi
 * que hay que eliminarlas al cerrar sesion para que la siguiente persona
 * que entre en el mismo dispositivo no vea datos de la anterior.
 */
async function limpiarCacheApi() {
  if (!browser || !('caches' in window)) return;
  try {
    const nombres = await caches.keys();
    await Promise.all(
      nombres.filter((n) => n.includes('cf-api')).map((n) => caches.delete(n))
    );
  } catch {
    /* ignore */
  }
}

export function logout() {
  setToken(null);
  void limpiarCacheApi();
}
