<script lang="ts">
  import { api } from '$lib/services/api';
  import type { LoteDetalle } from '$lib/types';
  import { fechaLocal, fechaHora, num } from '$lib/utils/format';
  import EstadoLoteBadge from '$lib/components/shared/EstadoLoteBadge.svelte';
  import LoadingState from '$lib/components/shared/LoadingState.svelte';
  import ErrorState from '$lib/components/shared/ErrorState.svelte';
  import XIcon from 'lucide-svelte/icons/x';

  let { loteId, onClose }: { loteId: number; onClose: () => void } = $props();

  let detalle = $state<LoteDetalle | null>(null);
  let error = $state('');
  let cargando = $state(true);

  async function cargar() {
    cargando = true;
    error = '';
    try {
      detalle = await api.get<LoteDetalle>(`/api/v1/lotes/${loteId}/detalle`);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error';
    } finally {
      cargando = false;
    }
  }

  $effect(() => {
    loteId;
    cargar();
  });
</script>

<!-- Overlay -->
<button
  class="fixed inset-0 z-40 bg-black/30"
  onclick={onClose}
  aria-label="Cerrar panel"
></button>

<!-- Panel lateral -->
<aside
  class="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-line bg-surface shadow-elevated"
>
  <header class="flex items-center justify-between border-b border-line px-5 py-4">
    <h2 class="text-base font-semibold text-ink">Detalle del lote</h2>
    <button onclick={onClose} class="rounded-control p-1 text-muted hover:bg-canvas" aria-label="Cerrar">
      <XIcon size={18} />
    </button>
  </header>

  <div class="flex-1 overflow-y-auto p-5">
    {#if cargando}
      <LoadingState />
    {:else if error}
      <ErrorState mensaje={error} onReintentar={cargar} />
    {:else if detalle}
      <div class="space-y-5 text-sm">
        <!-- Producto + lote -->
        <section>
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold uppercase tracking-wide text-muted">Lote</span>
            <EstadoLoteBadge estado={detalle.estado} />
          </div>
          <p class="mt-1 text-base font-semibold text-ink">{detalle.producto_descripcion}</p>
          <p class="text-muted">SKU {detalle.producto_sku} · Lote {detalle.numero_lote}</p>
        </section>

        <!-- Datos -->
        <section class="grid grid-cols-2 gap-3">
          <div>
            <p class="text-xs text-muted">Vence</p>
            <p class="font-medium text-ink">{fechaLocal(detalle.fecha_vencimiento)}</p>
          </div>
          <div>
            <p class="text-xs text-muted">Dias restantes</p>
            <p class="font-medium text-ink">{detalle.dias_restantes ?? '—'}</p>
          </div>
          <div>
            <p class="text-xs text-muted">Categoria</p>
            <p class="font-medium text-ink">{detalle.categoria ?? '—'}</p>
          </div>
          <div>
            <p class="text-xs text-muted">Proveedor</p>
            <p class="font-medium text-ink">{detalle.proveedor ?? '—'}</p>
          </div>
          <div>
            <p class="text-xs text-muted">Existencia total</p>
            <p class="font-medium text-ink">
              {num(detalle.existencia_total)} {detalle.unidad_base}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted">Factor empaque</p>
            <p class="font-medium text-ink">{num(detalle.factor_empaque)}</p>
          </div>
        </section>

        <!-- Existencias por bodega -->
        <section>
          <h3 class="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
            Existencias por bodega
          </h3>
          {#if detalle.existencias.length === 0}
            <p class="text-muted">Sin existencias registradas.</p>
          {:else}
            <ul class="divide-y divide-line rounded-control border border-line">
              {#each detalle.existencias as e (e.bodega_id)}
                <li class="flex items-center justify-between px-3 py-2">
                  <span class="text-ink">{e.sucursal_nombre} · {e.bodega_nombre}</span>
                  <span class="font-medium text-ink">{num(e.cantidad)}</span>
                </li>
              {/each}
            </ul>
          {/if}
        </section>

        <!-- Inspecciones -->
        <section>
          <h3 class="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
            Inspecciones recientes
          </h3>
          {#if detalle.inspecciones.length === 0}
            <p class="text-muted">Sin inspecciones. Una alerta no equivale a inspeccion fisica.</p>
          {:else}
            <ul class="space-y-2">
              {#each detalle.inspecciones as i (i.id)}
                <li class="rounded-control border border-line p-3">
                  <div class="flex items-center justify-between">
                    <span class="font-medium text-ink">{i.responsable}</span>
                    <span class="text-xs text-muted">{fechaHora(i.fecha_inspeccion)}</span>
                  </div>
                  {#if i.cantidad_contada !== null}
                    <p class="text-muted">Contado: {num(i.cantidad_contada)}</p>
                  {/if}
                  {#if i.observaciones}
                    <p class="mt-1 text-ink">{i.observaciones}</p>
                  {/if}
                </li>
              {/each}
            </ul>
          {/if}
        </section>
      </div>
    {/if}
  </div>
</aside>
