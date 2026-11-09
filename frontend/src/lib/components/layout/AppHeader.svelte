<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { api } from '$lib/services/api';
  import { logout } from '$lib/stores/auth';
  import type { Usuario } from '$lib/types';
  import Search from 'lucide-svelte/icons/search';
  import LogOut from 'lucide-svelte/icons/log-out';
  import ChevronDown from 'lucide-svelte/icons/chevron-down';
  import Warehouse from 'lucide-svelte/icons/warehouse';

  type Sucursal = { id: number; nombre: string };

  let usuario = $state<Usuario | null>(null);
  let sucursales = $state<Sucursal[]>([]);
  let sucursalSel = $state<string>('todas');
  let menuAbierto = $state(false);

  const TITULOS: Record<string, string> = {
    '/': 'Dashboard',
    '/lotes': 'Lotes y vencimientos',
    '/inspecciones': 'Inspecciones',
    '/alertas': 'Alertas y seguimiento',
    '/averiados': 'Productos averiados',
    '/reportes': 'Reportes'
  };
  let titulo = $derived(TITULOS[$page.url.pathname] ?? 'Corta Fecha');

  async function cargar() {
    try {
      usuario = await api.get<Usuario>('/auth/me');
    } catch {
      /* ignore */
    }
    try {
      sucursales = await api.get<Sucursal[]>('/api/v1/sucursales');
    } catch {
      sucursales = [];
    }
  }

  function salir() {
    logout();
    goto('/login');
  }

  $effect(() => {
    cargar();
  });
</script>

<header class="flex h-16 shrink-0 items-center gap-4 border-b border-line bg-surface px-6">
  <div class="min-w-0">
    <p class="text-xs text-muted">Corta Fecha</p>
    <h2 class="truncate text-base font-semibold text-ink">{titulo}</h2>
  </div>

  <!-- Buscador global -->
  <div class="relative ml-auto hidden max-w-xs flex-1 md:block">
    <Search size={16} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
    <input
      type="search"
      placeholder="Buscar producto, SKU o lote"
      class="w-full rounded-control border border-line bg-canvas py-2 pl-9 pr-3 text-sm placeholder:text-muted focus:border-brand focus:outline-none"
    />
  </div>

  <!-- Selector de bodega -->
  <div class="flex items-center gap-2 rounded-control border border-line px-2.5 py-1.5">
    <Warehouse size={16} class="text-muted" />
    <select
      bind:value={sucursalSel}
      class="bg-transparent text-sm text-ink focus:outline-none"
      aria-label="Seleccionar bodega"
    >
      <option value="todas">Todas las bodegas</option>
      {#each sucursales as s (s.id)}
        <option value={String(s.id)}>{s.nombre}</option>
      {/each}
    </select>
  </div>

  <!-- Usuario -->
  <div class="relative">
    <button
      onclick={() => (menuAbierto = !menuAbierto)}
      class="flex items-center gap-2 rounded-control px-2 py-1.5 text-sm hover:bg-canvas"
    >
      <span class="flex h-7 w-7 items-center justify-center rounded-full bg-navy text-xs font-semibold text-white">
        {(usuario?.nombre ?? '?').slice(0, 1).toUpperCase()}
      </span>
      <span class="hidden text-ink sm:block">{usuario?.nombre ?? 'Usuario'}</span>
      <ChevronDown size={14} class="text-muted" />
    </button>
    {#if menuAbierto}
      <div class="absolute right-0 top-full z-20 mt-1 w-52 rounded-control border border-line bg-surface py-1 shadow-elevated">
        <div class="border-b border-line px-3 py-2">
          <p class="truncate text-sm font-medium text-ink">{usuario?.nombre}</p>
          <p class="truncate text-xs text-muted">{usuario?.email}</p>
        </div>
        <button
          onclick={salir}
          class="flex w-full items-center gap-2 px-3 py-2 text-sm text-ink hover:bg-canvas"
        >
          <LogOut size={15} /> Salir
        </button>
      </div>
    {/if}
  </div>
</header>
