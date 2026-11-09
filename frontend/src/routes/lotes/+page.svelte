<script lang="ts">
  import { api } from '$lib/services/api';
  import type { EstadoLote, LoteVistaRow } from '$lib/types';
  import { fechaLocal, num } from '$lib/utils/format';
  import PageHeader from '$lib/components/shared/PageHeader.svelte';
  import EstadoLoteBadge from '$lib/components/shared/EstadoLoteBadge.svelte';
  import LoadingState from '$lib/components/shared/LoadingState.svelte';
  import ErrorState from '$lib/components/shared/ErrorState.svelte';
  import EmptyState from '$lib/components/shared/EmptyState.svelte';
  import LotDetailDrawer from '$lib/components/lots/LotDetailDrawer.svelte';
  import SearchIcon from 'lucide-svelte/icons/search';

  let filas = $state<LoteVistaRow[]>([]);
  let error = $state('');
  let cargando = $state(true);

  let q = $state('');
  let estado = $state<EstadoLote | ''>('');
  let loteSel = $state<number | null>(null);

  const ESTADOS: { value: EstadoLote | ''; label: string }[] = [
    { value: '', label: 'Todos los estados' },
    { value: 'vencido', label: 'Vencido' },
    { value: 'critica', label: 'Critica' },
    { value: 'prioritaria', label: 'Prioritaria' },
    { value: 'preventiva', label: 'Preventiva' },
    { value: 'normal', label: 'Normal' },
    { value: 'sin_fecha', label: 'Sin fecha' }
  ];

  async function cargar() {
    cargando = true;
    error = '';
    try {
      const params = new URLSearchParams();
      if (q) params.set('q', q);
      if (estado) params.set('estado', estado);
      const qs = params.toString();
      filas = await api.get<LoteVistaRow[]>(`/api/v1/lotes/vista${qs ? `?${qs}` : ''}`);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error';
    } finally {
      cargando = false;
    }
  }

  // Recarga al cambiar filtros (q con debounce simple).
  let debounce: ReturnType<typeof setTimeout>;
  $effect(() => {
    q;
    estado;
    clearTimeout(debounce);
    debounce = setTimeout(cargar, 250);
  });
</script>

<PageHeader
  titulo="Lotes y vencimientos"
  descripcion="Control de vencimiento por lote. La unidad de seguimiento es el lote."
/>

<!-- FilterBar -->
<div class="mb-4 flex flex-wrap items-center gap-3">
  <div class="relative min-w-[240px] flex-1">
    <SearchIcon size={16} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
    <input
      type="search"
      bind:value={q}
      placeholder="Buscar producto, SKU o lote"
      class="w-full rounded-control border border-line bg-surface py-2 pl-9 pr-3 text-sm placeholder:text-muted focus:border-brand focus:outline-none"
    />
  </div>
  <select
    bind:value={estado}
    class="rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none"
  >
    {#each ESTADOS as e (e.value)}
      <option value={e.value}>{e.label}</option>
    {/each}
  </select>
</div>

{#if cargando}
  <LoadingState />
{:else if error}
  <ErrorState mensaje={error} onReintentar={cargar} />
{:else if filas.length === 0}
  <EmptyState titulo="Sin lotes" descripcion="No hay lotes que coincidan con los filtros." />
{:else}
  <div class="overflow-x-auto rounded-card border border-line bg-surface shadow-card">
    <table class="w-full min-w-[820px] text-sm">
      <thead>
        <tr class="border-b border-line text-left text-xs font-semibold uppercase tracking-wide text-muted">
          <th class="px-4 py-3">Producto</th>
          <th class="px-4 py-3">Lote</th>
          <th class="px-4 py-3">Vence</th>
          <th class="px-4 py-3 text-right">Dias</th>
          <th class="px-4 py-3 text-right">Existencia</th>
          <th class="px-4 py-3">Bodegas</th>
          <th class="px-4 py-3">Estado</th>
        </tr>
      </thead>
      <tbody>
        {#each filas as f (f.id)}
          <tr
            class="cursor-pointer border-b border-line last:border-0 hover:bg-canvas"
            onclick={() => (loteSel = f.id)}
          >
            <td class="px-4 py-3">
              <p class="font-medium text-ink">{f.producto_descripcion}</p>
              <p class="text-xs text-muted">{f.producto_sku}</p>
            </td>
            <td class="px-4 py-3 text-ink">{f.numero_lote}</td>
            <td class="px-4 py-3 text-ink">{fechaLocal(f.fecha_vencimiento)}</td>
            <td class="px-4 py-3 text-right text-ink">{f.dias_restantes ?? '—'}</td>
            <td class="px-4 py-3 text-right text-ink">
              {num(f.existencia_total)}
              <span class="block text-xs text-muted">{f.cajas} cajas + {num(f.unidades)} und.</span>
            </td>
            <td class="px-4 py-3 text-ink">{f.n_bodegas}</td>
            <td class="px-4 py-3"><EstadoLoteBadge estado={f.estado} /></td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

{#if loteSel !== null}
  <LotDetailDrawer loteId={loteSel} onClose={() => (loteSel = null)} />
{/if}
