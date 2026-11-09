<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/ui';
  import type { Bodega, Proveedor } from '$lib/types';
  import { num } from '$lib/utils/format';
  import XIcon from 'lucide-svelte/icons/x';

  let { onClose, onSaved }: { onClose: () => void; onSaved: () => void } = $props();

  let proveedores = $state<Proveedor[]>([]);
  let bodegas = $state<Bodega[]>([]);

  // Campos de la hoja fisica de corta fecha.
  let proveedorId = $state<number | null>(null);
  let sku = $state('');
  let descripcion = $state('');
  let numeroLote = $state('');
  let fechaVenc = $state('');
  // Desglose: el encargado decide cuanto va en cajas y cuanto en unidades.
  // Los tres campos son independientes; el sistema no reparte el total solo.
  let cajas = $state<number>(0);
  let unidadesSueltas = $state<number>(0);
  let unidadesPorCaja = $state<number>(1);
  let bodegaId = $state<number | null>(null);
  let observaciones = $state('');

  let guardando = $state(false);

  $effect(() => {
    api
      .get<Proveedor[]>('/api/v1/proveedores')
      .then((p) => (proveedores = p))
      .catch(() => {});
    api
      .get<Bodega[]>('/api/v1/bodegas')
      .then((b) => {
        bodegas = b.filter((x) => x.activa);
        if (bodegas.length === 1) bodegaId = bodegas[0].id;
      })
      .catch(() => {});
  });

  const nCajas = $derived(Math.max(0, Number(cajas) || 0));
  const nPorCaja = $derived(Math.max(1, Number(unidadesPorCaja) || 1));
  const nSueltas = $derived(Math.max(0, Number(unidadesSueltas) || 0));
  const totalUnidades = $derived(nCajas * nPorCaja + nSueltas);

  const puedeGuardar = $derived(
    sku.trim() !== '' &&
      descripcion.trim() !== '' &&
      numeroLote.trim() !== '' &&
      fechaVenc !== '' &&
      Number(unidadesPorCaja) > 0 &&
      Number(cajas) >= 0 &&
      Number(unidadesSueltas) >= 0 &&
      totalUnidades > 0 &&
      bodegaId !== null
  );

  async function guardar() {
    if (!puedeGuardar) return;
    guardando = true;
    try {
      await api.post('/api/v1/registros-corta-fecha', {
        sku: sku.trim(),
        descripcion: descripcion.trim(),
        numero_lote: numeroLote.trim(),
        fecha_vencimiento: fechaVenc,
        cajas: nCajas,
        unidades_sueltas: nSueltas,
        unidades_por_caja: nPorCaja,
        bodega_id: bodegaId,
        proveedor_id: proveedorId,
        observaciones: observaciones.trim() || null
      });
      toast('Registro de corta fecha guardado', 'ok');
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

<div
  class="fixed left-1/2 top-1/2 z-50 max-h-[90vh] w-full max-w-lg -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-card bg-surface shadow-elevated"
>
  <header class="flex items-center justify-between border-b border-line px-5 py-4">
    <div>
      <h2 class="text-base font-semibold text-ink">Nuevo registro de corta fecha</h2>
      <p class="text-xs text-muted">Producto proximo a vencer detectado en el recorrido.</p>
    </div>
    <button onclick={onClose} class="rounded-control p-1 text-muted hover:bg-canvas" aria-label="Cerrar">
      <XIcon size={18} />
    </button>
  </header>

  <div class="space-y-4 p-5 text-sm">
    <div>
      <label for="cf-prov" class="font-medium text-ink">Proveedor</label>
      <select id="cf-prov" bind:value={proveedorId}
        class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none">
        <option value={null}>Sin proveedor</option>
        {#each proveedores as p (p.id)}<option value={p.id}>{p.nombre}</option>{/each}
      </select>
    </div>

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div>
        <label for="cf-sku" class="font-medium text-ink">Codigo (SKU)</label>
        <input id="cf-sku" bind:value={sku} placeholder="N27684"
          class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none" />
      </div>
      <div class="sm:col-span-2">
        <label for="cf-desc" class="font-medium text-ink">Nombre del producto</label>
        <input id="cf-desc" bind:value={descripcion} placeholder="MUUU WAFER LECHE PAG 14 LLEVE 15"
          class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none" />
      </div>
    </div>

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <div>
        <label for="cf-lote" class="font-medium text-ink">Lote</label>
        <input id="cf-lote" bind:value={numeroLote} placeholder="2164609"
          class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none" />
      </div>
      <div>
        <label for="cf-venc" class="font-medium text-ink">Fecha de vencimiento</label>
        <input id="cf-venc" type="date" bind:value={fechaVenc}
          class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none" />
      </div>
    </div>

    <fieldset class="rounded-card border border-line p-3">
      <legend class="px-1 text-xs font-semibold uppercase tracking-wide text-muted">
        Cantidad encontrada
      </legend>
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div>
          <label for="cf-cajas" class="font-medium text-ink">Cajas</label>
          <input id="cf-cajas" type="number" min="0" step="1" bind:value={cajas}
            class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none" />
        </div>
        <div>
          <label for="cf-upc" class="font-medium text-ink">Unidades por caja</label>
          <input id="cf-upc" type="number" min="1" step="1" bind:value={unidadesPorCaja}
            class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none" />
        </div>
        <div>
          <label for="cf-und" class="font-medium text-ink">Unidades sueltas</label>
          <input id="cf-und" type="number" min="0" step="any" bind:value={unidadesSueltas}
            class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none" />
        </div>
      </div>
      <p class="mt-2 text-xs text-muted">
        Total: <span class="font-medium text-ink">{num(totalUnidades)}</span> unidades
        ({num(nCajas)} cajas x {num(nPorCaja)} + {num(nSueltas)} sueltas). Cada campo se guarda tal
        como lo escribas.
      </p>
    </fieldset>

    <div>
      <label for="cf-bod" class="font-medium text-ink">Bodega</label>
      <select id="cf-bod" bind:value={bodegaId}
        class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none">
        <option value={null} disabled>Selecciona una bodega</option>
        {#each bodegas as b (b.id)}<option value={b.id}>{b.nombre}</option>{/each}
      </select>
      {#if bodegas.length === 0}
        <p class="mt-1 text-xs text-estado-prioritaria">
          No hay bodegas activas. Crea una en Configuracion antes de registrar.
        </p>
      {/if}
    </div>

    <div>
      <label for="cf-obs" class="font-medium text-ink">Observaciones</label>
      <textarea id="cf-obs" rows="2" bind:value={observaciones}
        class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none"></textarea>
    </div>
  </div>

  <footer class="flex items-center justify-end gap-2 border-t border-line px-5 py-3">
    <button onclick={onClose} class="rounded-control px-3 py-2 text-sm font-medium text-ink hover:bg-canvas">Cancelar</button>
    <button onclick={guardar} disabled={!puedeGuardar || guardando}
      class="rounded-control bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
      {guardando ? 'Guardando...' : 'Guardar registro'}
    </button>
  </footer>
</div>
