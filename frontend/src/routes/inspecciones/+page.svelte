<script lang="ts">
  import { api } from '$lib/services/api';
  import type { InspeccionVistaRow } from '$lib/types';
  import { fechaHora, num } from '$lib/utils/format';
  import PageHeader from '$lib/components/shared/PageHeader.svelte';
  import LoadingState from '$lib/components/shared/LoadingState.svelte';
  import ErrorState from '$lib/components/shared/ErrorState.svelte';
  import EmptyState from '$lib/components/shared/EmptyState.svelte';
  import InspectionForm from '$lib/components/inspections/InspectionForm.svelte';
  import PlusIcon from 'lucide-svelte/icons/plus';

  let filas = $state<InspeccionVistaRow[]>([]);
  let error = $state('');
  let cargando = $state(true);
  let formAbierto = $state(false);

  async function cargar() {
    cargando = true;
    error = '';
    try {
      filas = await api.get<InspeccionVistaRow[]>('/api/v1/inspecciones/vista');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error';
    } finally {
      cargando = false;
    }
  }

  $effect(() => {
    cargar();
  });
</script>

<PageHeader titulo="Inspecciones" descripcion="Captura fisica confirmada por un responsable.">
  {#snippet acciones()}
    <button
      onclick={() => (formAbierto = true)}
      class="inline-flex items-center gap-2 rounded-control bg-brand px-3 py-2 text-sm font-medium text-white hover:bg-brand-700"
    >
      <PlusIcon size={15} /> Nueva inspeccion
    </button>
  {/snippet}
</PageHeader>

{#if cargando}
  <LoadingState />
{:else if error}
  <ErrorState mensaje={error} onReintentar={cargar} />
{:else if filas.length === 0}
  <EmptyState titulo="Sin inspecciones" descripcion="Registra la primera inspeccion fisica." />
{:else}
  <div class="overflow-x-auto rounded-card border border-line bg-surface shadow-card">
    <table class="w-full min-w-[720px] text-sm">
      <thead>
        <tr class="border-b border-line text-left text-xs font-semibold uppercase tracking-wide text-muted">
          <th class="px-4 py-3">Fecha</th>
          <th class="px-4 py-3">Producto</th>
          <th class="px-4 py-3">Lote</th>
          <th class="px-4 py-3">Bodega</th>
          <th class="px-4 py-3">Responsable</th>
          <th class="px-4 py-3 text-right">Contado</th>
        </tr>
      </thead>
      <tbody>
        {#each filas as f (f.id)}
          <tr class="border-b border-line last:border-0">
            <td class="px-4 py-3 text-ink">{fechaHora(f.fecha_inspeccion)}</td>
            <td class="px-4 py-3">
              <p class="font-medium text-ink">{f.producto_descripcion}</p>
              <p class="text-xs text-muted">{f.producto_sku}</p>
            </td>
            <td class="px-4 py-3 text-ink">{f.numero_lote}</td>
            <td class="px-4 py-3 text-ink">{f.bodega_nombre}</td>
            <td class="px-4 py-3 text-ink">{f.responsable}</td>
            <td class="px-4 py-3 text-right text-ink">
              {f.cantidad_contada !== null ? num(f.cantidad_contada) : '—'}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

{#if formAbierto}
  <InspectionForm onClose={() => (formAbierto = false)} onSaved={cargar} />
{/if}
