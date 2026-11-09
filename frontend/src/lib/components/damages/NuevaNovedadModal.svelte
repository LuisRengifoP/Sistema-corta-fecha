<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/ui';
  import type { LoteDetalle, LoteVistaRow, TipoNovedad, Usuario } from '$lib/types';
  import { num } from '$lib/utils/format';
  import EstadoLoteBadge from '$lib/components/shared/EstadoLoteBadge.svelte';
  import XIcon from 'lucide-svelte/icons/x';
  import SearchIcon from 'lucide-svelte/icons/search';

  let { onClose, onSaved }: { onClose: () => void; onSaved: () => void } = $props();

  let me = $state<Usuario | null>(null);
  let q = $state('');
  let resultados = $state<LoteVistaRow[]>([]);
  let loteSel = $state<LoteVistaRow | null>(null);
  let detalle = $state<LoteDetalle | null>(null);
  let bodegaId = $state<number | null>(null);

  let tipo = $state<TipoNovedad>('averia');
  let cantidad = $state(0);
  let observaciones = $state('');
  let guardando = $state(false);

  const puedeGuardar = $derived(
    loteSel !== null && bodegaId !== null && cantidad > 0 && me !== null
  );

  $effect(() => {
    api.get<Usuario>('/auth/me').then((u) => (me = u)).catch(() => {});
  });

  let debounce: ReturnType<typeof setTimeout>;
  function buscar() {
    clearTimeout(debounce);
    debounce = setTimeout(async () => {
      if (!q.trim()) {
        resultados = [];
        return;
      }
      try {
        resultados = await api.get<LoteVistaRow[]>(`/api/v1/lotes/vista?q=${encodeURIComponent(q)}`);
      } catch {
        resultados = [];
      }
    }, 250);
  }

  async function elegirLote(row: LoteVistaRow) {
    loteSel = row;
    bodegaId = null;
    detalle = null;
    try {
      detalle = await api.get<LoteDetalle>(`/api/v1/lotes/${row.id}/detalle`);
      if (detalle.existencias.length === 1) bodegaId = detalle.existencias[0].bodega_id;
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Error', 'error');
    }
  }

  async function guardar() {
    if (!loteSel || !bodegaId || !me) return;
    guardando = true;
    try {
      await api.post('/api/v1/novedades', {
        lote_id: loteSel.id,
        bodega_id: bodegaId,
        tipo,
        cantidad_afectada: cantidad,
        reportado_por_id: me.id,
        observaciones: observaciones || null
      });
      toast('Novedad registrada', 'ok');
      onSaved();
      onClose();
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Error', 'error');
    } finally {
      guardando = false;
    }
  }
</script>

<button class="fixed inset-0 z-40 bg-black/40" onclick={onClose} aria-label="Cerrar"></button>

<div class="fixed left-1/2 top-1/2 z-50 max-h-[90vh] w-full max-w-md -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-card bg-surface shadow-elevated">
  <header class="flex items-center justify-between border-b border-line px-5 py-4">
    <h2 class="text-base font-semibold text-ink">Registrar novedad</h2>
    <button onclick={onClose} class="rounded-control p-1 text-muted hover:bg-canvas" aria-label="Cerrar">
      <XIcon size={18} />
    </button>
  </header>

  <div class="space-y-4 p-5 text-sm">
    <div>
      <label for="buscar" class="font-medium text-ink">Lote</label>
      <div class="relative mt-1">
        <SearchIcon size={16} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
        <input id="buscar" bind:value={q} oninput={buscar} placeholder="SKU, nombre o lote"
          class="w-full rounded-control border border-line py-2 pl-9 pr-3 focus:border-brand focus:outline-none" />
      </div>
      {#if resultados.length > 0 && !loteSel}
        <ul class="mt-2 divide-y divide-line rounded-control border border-line">
          {#each resultados as r (r.id)}
            <li>
              <button onclick={() => elegirLote(r)}
                class="flex w-full items-center justify-between px-3 py-2 text-left hover:bg-canvas">
                <span>
                  <span class="font-medium text-ink">{r.producto_descripcion}</span>
                  <span class="block text-xs text-muted">{r.producto_sku} · Lote {r.numero_lote}</span>
                </span>
                <EstadoLoteBadge estado={r.estado} />
              </button>
            </li>
          {/each}
        </ul>
      {/if}
      {#if loteSel}
        <div class="mt-2 flex items-center justify-between rounded-control border border-line px-3 py-2">
          <span>
            <span class="font-medium text-ink">{loteSel.producto_descripcion}</span>
            <span class="block text-xs text-muted">{loteSel.producto_sku} · Lote {loteSel.numero_lote}</span>
          </span>
          <button onclick={() => { loteSel = null; detalle = null; bodegaId = null; }}
            class="text-xs text-brand hover:underline">Cambiar</button>
        </div>
      {/if}
    </div>

    {#if detalle}
      <div>
        <span class="font-medium text-ink">Bodega</span>
        <div class="mt-1 space-y-2">
          {#each detalle.existencias as e (e.bodega_id)}
            <label class="flex cursor-pointer items-center gap-2 rounded-control border border-line px-3 py-2">
              <input type="radio" name="bod" value={e.bodega_id} bind:group={bodegaId} />
              <span class="text-ink">{e.sucursal_nombre} · {e.bodega_nombre}</span>
              <span class="ml-auto text-muted">{num(e.cantidad)}</span>
            </label>
          {/each}
          {#if detalle.existencias.length === 0}
            <p class="text-muted">Sin existencias registradas para este lote.</p>
          {/if}
        </div>
      </div>
    {/if}

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label for="tipo" class="font-medium text-ink">Tipo</label>
        <select id="tipo" bind:value={tipo}
          class="mt-1 w-full rounded-control border border-line px-3 py-2 focus:border-brand focus:outline-none">
          <option value="averia">Averia</option>
          <option value="rotura">Rotura</option>
          <option value="contaminacion">Contaminacion</option>
          <option value="empaque_danado">Empaque danado</option>
          <option value="otro">Otro</option>
        </select>
      </div>
      <div>
        <label for="cant" class="font-medium text-ink">Cantidad afectada</label>
        <input id="cant" type="number" min="0" bind:value={cantidad}
          class="mt-1 w-full rounded-control border border-line px-3 py-2 focus:border-brand focus:outline-none" />
      </div>
    </div>

    <div>
      <label for="obs" class="font-medium text-ink">Observaciones</label>
      <textarea id="obs" rows="2" bind:value={observaciones}
        class="mt-1 w-full rounded-control border border-line px-3 py-2 focus:border-brand focus:outline-none"></textarea>
    </div>
  </div>

  <footer class="flex items-center justify-end gap-2 border-t border-line px-5 py-3">
    <button onclick={onClose} class="rounded-control px-3 py-2 text-sm font-medium text-ink hover:bg-canvas">Cancelar</button>
    <button onclick={guardar} disabled={!puedeGuardar || guardando}
      class="rounded-control bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
      {guardando ? 'Guardando...' : 'Registrar novedad'}
    </button>
  </footer>
</div>
