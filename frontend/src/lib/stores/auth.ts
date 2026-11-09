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

export function logout() {
  setToken(null);
}
