import { browser } from '$app/environment';
import { writable } from 'svelte/store';

export type Tema = 'light' | 'dark';

const KEY = 'cf_theme';

function inicial(): Tema {
  if (!browser) return 'light';
  try {
    const guardado = localStorage.getItem(KEY);
    if (guardado === 'light' || guardado === 'dark') return guardado;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  } catch {
    return 'light';
  }
}

export const tema = writable<Tema>(inicial());

function aplicar(valor: Tema) {
  if (!browser) return;
  document.documentElement.classList.toggle('dark', valor === 'dark');
  try {
    localStorage.setItem(KEY, valor);
  } catch {
    /* ignore */
  }
}

// Aplica la clase en cada cambio (y en el valor inicial).
tema.subscribe(aplicar);

export function alternarTema() {
  tema.update((v) => (v === 'dark' ? 'light' : 'dark'));
}
