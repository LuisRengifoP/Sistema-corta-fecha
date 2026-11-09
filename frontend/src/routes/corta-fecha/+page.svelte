<script lang="ts">
  import { api } from '$lib/services/api';
  import type { RegistroCortaFechaRow } from '$lib/types';
  import { fechaLocal, fechaHora, num } from '$lib/utils/format';
  import PageHeader from '$lib/components/shared/PageHeader.svelte';
  import LoadingState from '$lib/components/shared/LoadingState.svelte';
  import ErrorState from '$lib/components/shared/ErrorState.svelte';
  import EmptyState from '$lib/components/shared/EmptyState.svelte';
  import RegistroCortaFechaForm from '$lib/components/cortafecha/RegistroCortaFechaForm.svelte';
  import PlusIcon from 'lucide-svelte/icons/plus';

  let filas = $state<RegistroCortaFechaRow[]>([]);
  let error = $state('');
  let cargando = $state(true);
  let formAbierto = $state(false);

  async function cargar() {
    cargando = true;
    error = '';
    try {
      filas = await api.get<RegistroCortaFechaRow[]>('/api/v1/registros-corta-fecha/vista');
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

<PageHeader
  titulo="Corta fecha"
  descripcion="Registro de productos proximos a vencer detectados en el recorrido de pasillos."
>
  {#snippet acciones()}
    <button
      onclick={() => (formAbierto = true)}
      class="inline-flex items-center gap-2 rounded-control bg-brand px-3 py-2 text-sm font-medium text-white hover:bg-brand-700"
    >
      <PlusIcon size={15} /> Nuevo registro
    </button>
  {/snippet}
</PageHeader>

{#if cargando}
  <LoadingState />
{:else if error}
  <ErrorState mensaje={error} onReintentar={cargar} />
{:else if filas.length === 0}
  <EmptyState titulo="Sin registros" descripcion="Registra el primer producto de corta fecha." />
{:else}
  <div class="overflow-x-auto rounded-card border border-line bg-surface shadow-card">
    <table class="w-full min-w-[820px] text-sm">
      <thead>
        <tr class="border-b border-line text-left text-xs font-semibold uppercase tracking-wide text-muted">
          <th class="px-4 py-3">Proveedor</th>
          <th class="px-4 py-3">Codigo</th>
          <th class="px-4 py-3">Producto</th>
          <th class="px-4 py-3 text-right">Unidades</th>
          <th class="px-4 py-3">Vencimiento</th>
          <th class="px-4 py-3">Lote</th>
          <th class="px-4 py-3">Registrado</th>
        </tr>
      </thead>
      <tbody>
        {#each filas as f (f.id)}
          <tr class="border-b border-line last:border-0 hover:bg-canvas">
            <td class="px-4 py-3 text-ink">{f.proveedor ?? '—'}</td>
            <td class="px-4 py-3 font-medium text-ink">{f.producto_sku}</td>
            <td class="px-4 py-3 text-ink">{f.producto_descripcion}</td>
            <td class="px-4 py-3 text-right text-ink">
              {f.unidades !== null ? num(f.unidades) : '—'}
              {#if f.cajas !== null || f.unidades_sueltas !== null}
                <span class="block text-xs text-muted">
                  {num(f.cajas ?? 0)} cajas + {num(f.unidades_sueltas ?? 0)} und.
                </span>
              {/if}
            </td>
            <td class="px-4 py-3 text-ink">{fechaLocal(f.fecha_vencimiento)}</td>
            <td class="px-4 py-3 text-ink">{f.numero_lote}</td>
            <td class="px-4 py-3">
              <p class="text-ink">{fechaHora(f.registrado_en)}</p>
              <p class="text-xs text-muted">{f.responsable} · {f.bodega_nombre}</p>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

{#if formAbierto}
  <RegistroCortaFechaForm onClose={() => (formAbierto = false)} onSaved={cargar} />
{/if}
