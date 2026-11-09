import { browser } from '$app/environment';
import { writable } from 'svelte/store';

// ---- Sidebar contraido (persistente) ----
const KEY = 'cf_sidebar_collapsed';

function leer(): boolean {
  if (!browser) return false;
  try {
    return localStorage.getItem(KEY) === '1';
  } catch {
    return false;
  }
}

export const sidebarCollapsed = writable<boolean>(leer());

export function toggleSidebar() {
  sidebarCollapsed.update((v) => {
    const nuevo = !v;
    if (browser) {
      try {
        localStorage.setItem(KEY, nuevo ? '1' : '0');
      } catch {
        /* ignore */
      }
    }
    return nuevo;
  });
}

// ---- Toasts ----
export type Toast = { id: number; tipo: 'ok' | 'error' | 'info'; texto: string };

export const toasts = writable<Toast[]>([]);
let seq = 0;

export function toast(texto: string, tipo: Toast['tipo'] = 'info') {
  const id = ++seq;
  toasts.update((t) => [...t, { id, tipo, texto }]);
  setTimeout(() => {
    toasts.update((t) => t.filter((x) => x.id !== id));
  }, 4000);
}
