<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/ui';
  import type { LoteDetalle, LoteVistaRow, TipoNovedad, Usuario } from '$lib/types';
  import { fechaLocal, num } from '$lib/utils/format';
  import EstadoLoteBadge from '$lib/components/shared/EstadoLoteBadge.svelte';
  import XIcon from 'lucide-svelte/icons/x';
  import SearchIcon from 'lucide-svelte/icons/search';
  import CheckIcon from 'lucide-svelte/icons/check';

  let { onClose, onSaved }: { onClose: () => void; onSaved: () => void } = $props();

  const PASOS = ['Identificacion', 'Verificacion fisica', 'Estado y evidencia', 'Confirmacion'];
  let paso = $state(1);

  // Usuario actual (responsable).
  let me = $state<Usuario | null>(null);

  // Paso 1
  let q = $state('');
  let resultados = $state<LoteVistaRow[]>([]);
  let loteSel = $state<LoteVistaRow | null>(null);
  let detalle = $state<LoteDetalle | null>(null);
  let bodegaId = $state<number | null>(null);

  // Paso 2
  let fechaVenc = $state('');
  let cajas = $state(0);
  let unidades = $state(0);

  // Paso 3
  const ESTADOS = [
    { value: 'correcto', label: 'Correcto' },
    { value: 'proximo', label: 'Proximo a vencer' },
    { value: 'averiado', label: 'Averiado' },
    { value: 'vencido', label: 'Vencido' },
    { value: 'otra', label: 'Otra novedad' }
  ];
  let estado = $state('correcto');
  let tipoNovedad = $state<TipoNovedad>('averia');
  let cantidadAfectada = $state(0);
  let observaciones = $state('');

  let guardando = $state(false);

  const factor = $derived(detalle ? Number(detalle.factor_empaque) : 1);

  /** Parte del desglose que ya declaro el encargado para esa bodega. */
  function prefijarDesglose() {
    const e = detalle?.existencias.find((x) => x.bodega_id === bodegaId);
    if (!e) return;
    if (e.cajas !== null || e.unidades_sueltas !== null) {
      cajas = Number(e.cajas ?? 0);
      unidades = Number(e.unidades_sueltas ?? 0);
    }
  }
  const cantidadContada = $derived(cajas * factor + Number(unidades));
  const existenciaBodega = $derived(
    detalle && bodegaId
      ? Number(detalle.existencias.find((e) => e.bodega_id === bodegaId)?.cantidad ?? 0)
      : 0
  );
  const difiere = $derived(detalle !== null && bodegaId !== null && cantidadContada !== existenciaBodega);

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
      fechaVenc = detalle.fecha_vencimiento ?? '';
      if (detalle.existencias.length === 1) bodegaId = detalle.existencias[0].bodega_id;
      prefijarDesglose();
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Error', 'error');
    }
  }

  const puedeAvanzar = $derived.by(() => {
    if (paso === 1) return loteSel !== null && bodegaId !== null;
    if (paso === 2) return fechaVenc !== '' && cajas >= 0 && unidades >= 0;
    if (paso === 3) return estado !== 'averiado' || cantidadAfectada > 0;
    return true;
  });

  async function guardar() {
    if (!loteSel || !bodegaId || !me) return;
    guardando = true;
    try {
      const insp = await api.post<{ id: number }>('/api/v1/inspecciones', {
        lote_id: loteSel.id,
        bodega_id: bodegaId,
        responsable_id: me.id,
        cantidad_contada: cantidadContada,
        fecha_vencimiento_verificada: fechaVenc || null,
        observaciones: observaciones || null
      });
      if (estado === 'averiado') {
        await api.post('/api/v1/novedades', {
          lote_id: loteSel.id,
          bodega_id: bodegaId,
          inspeccion_id: insp.id,
          tipo: tipoNovedad,
          cantidad_afectada: cantidadAfectada,
          reportado_por_id: me.id,
          observaciones: observaciones || null
        });
      }
      toast('Inspeccion guardada', 'ok');
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

<div class="fixed inset-x-0 bottom-0 top-0 z-50 mx-auto flex max-w-xl flex-col bg-surface shadow-elevated sm:inset-y-6 sm:rounded-card">
  <!-- Header + stepper -->
  <header class="border-b border-line px-5 py-4">
    <div class="flex items-center justify-between">
      <h2 class="text-base font-semibold text-ink">Nueva inspeccion</h2>
      <button onclick={onClose} class="rounded-control p-1 text-muted hover:bg-canvas" aria-label="Cerrar">
        <XIcon size={18} />
      </button>
    </div>
    <ol class="mt-3 flex items-center gap-1">
      {#each PASOS as p, i (p)}
        <li class="flex flex-1 items-center gap-1.5">
          <span
            class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold
              {paso > i + 1 ? 'bg-estado-normal text-white' : paso === i + 1 ? 'bg-brand text-white' : 'bg-line text-muted'}"
          >
            {#if paso > i + 1}<CheckIcon size={13} />{:else}{i + 1}{/if}
          </span>
          <span class="hidden truncate text-xs text-muted sm:block">{p}</span>
          {#if i < PASOS.length - 1}<span class="h-px flex-1 bg-line"></span>{/if}
        </li>
      {/each}
    </ol>
  </header>

  <div class="flex-1 overflow-y-auto p-5">
    {#if paso === 1}
      <!-- Paso 1: Identificacion -->
      <div class="space-y-4">
        <div>
          <label for="buscar-lote" class="text-sm font-medium text-ink">Buscar producto o lote</label>
          <div class="relative mt-1">
            <SearchIcon size={16} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
            <input
              id="buscar-lote"
              bind:value={q}
              oninput={buscar}
              placeholder="SKU, nombre o numero de lote"
              class="w-full rounded-control border border-line py-2 pl-9 pr-3 text-sm focus:border-brand focus:outline-none"
            />
          </div>
        </div>

        {#if resultados.length > 0}
          <ul class="divide-y divide-line rounded-control border border-line">
            {#each resultados as r (r.id)}
              <li>
                <button
                  onclick={() => elegirLote(r)}
                  class="flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-canvas
                    {loteSel?.id === r.id ? 'bg-brand/5' : ''}"
                >
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

        {#if detalle}
          <div>
            <span class="text-sm font-medium text-ink">Bodega</span>
            {#if detalle.existencias.length === 0}
              <p class="mt-1 text-sm text-muted">Este lote no tiene existencias registradas.</p>
            {:else}
              <div class="mt-1 space-y-2">
                {#each detalle.existencias as e (e.bodega_id)}
                  <label class="flex cursor-pointer items-center gap-2 rounded-control border border-line px-3 py-2 text-sm">
                    <input
                      type="radio"
                      name="bodega"
                      value={e.bodega_id}
                      bind:group={bodegaId}
                      onchange={prefijarDesglose}
                    />
                    <span class="text-ink">{e.sucursal_nombre} · {e.bodega_nombre}</span>
                    <span class="ml-auto text-muted">
                      {num(e.cantidad)}
                      {#if e.cajas !== null || e.unidades_sueltas !== null}
                        <span class="text-xs">
                          ({num(e.cajas ?? 0)} cajas + {num(e.unidades_sueltas ?? 0)} und.)
                        </span>
                      {/if}
                    </span>
                  </label>
                {/each}
              </div>
            {/if}
          </div>
        {/if}
      </div>
    {:else if paso === 2}
      <!-- Paso 2: Verificacion fisica -->
      <div class="space-y-4">
        <div>
          <label for="fventa" class="text-sm font-medium text-ink">Fecha de vencimiento observada</label>
          <input
            id="fventa"
            type="date"
            bind:value={fechaVenc}
            class="mt-1 w-full rounded-control border border-line px-3 py-2 text-sm focus:border-brand focus:outline-none"
          />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="cajas" class="text-sm font-medium text-ink">Cajas completas</label>
            <input id="cajas" type="number" min="0" bind:value={cajas}
              class="mt-1 w-full rounded-control border border-line px-3 py-2 text-sm focus:border-brand focus:outline-none" />
          </div>
          <div>
            <label for="unid" class="text-sm font-medium text-ink">Unidades sueltas</label>
            <input id="unid" type="number" min="0" bind:value={unidades}
              class="mt-1 w-full rounded-control border border-line px-3 py-2 text-sm focus:border-brand focus:outline-none" />
          </div>
        </div>
        <div class="rounded-control bg-canvas px-3 py-2 text-sm">
          <p class="text-muted">
            Factor de empaque: <span class="font-medium text-ink">{num(factor)}</span>
          </p>
          <p class="text-muted">
            Equivalencia: <span class="font-medium text-ink">{num(cantidadContada)} {detalle?.unidad_base ?? ''}</span>
          </p>
          <p class="text-muted">
            En sistema: <span class="font-medium text-ink">{num(existenciaBodega)}</span>
          </p>
          {#if difiere}
            <p class="mt-1 text-estado-prioritaria">
              La cantidad fisica no coincide con el inventario. Se registrara una diferencia para revision.
            </p>
          {/if}
        </div>
      </div>
    {:else if paso === 3}
      <!-- Paso 3: Estado y evidencia -->
      <div class="space-y-4">
        <div>
          <label for="estado" class="text-sm font-medium text-ink">Estado observado</label>
          <select id="estado" bind:value={estado}
            class="mt-1 w-full rounded-control border border-line px-3 py-2 text-sm focus:border-brand focus:outline-none">
            {#each ESTADOS as e (e.value)}<option value={e.value}>{e.label}</option>{/each}
          </select>
        </div>
        {#if estado === 'averiado'}
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label for="tnov" class="text-sm font-medium text-ink">Tipo de averia</label>
              <select id="tnov" bind:value={tipoNovedad}
                class="mt-1 w-full rounded-control border border-line px-3 py-2 text-sm focus:border-brand focus:outline-none">
                <option value="averia">Averia</option>
                <option value="rotura">Rotura</option>
                <option value="contaminacion">Contaminacion</option>
                <option value="empaque_danado">Empaque danado</option>
                <option value="otro">Otro</option>
              </select>
            </div>
            <div>
              <label for="cafec" class="text-sm font-medium text-ink">Cantidad afectada</label>
              <input id="cafec" type="number" min="0" bind:value={cantidadAfectada}
                class="mt-1 w-full rounded-control border border-line px-3 py-2 text-sm focus:border-brand focus:outline-none" />
            </div>
          </div>
        {/if}
        <div>
          <label for="obs" class="text-sm font-medium text-ink">Observaciones</label>
          <textarea id="obs" rows="3" bind:value={observaciones}
            class="mt-1 w-full rounded-control border border-line px-3 py-2 text-sm focus:border-brand focus:outline-none"></textarea>
        </div>
        <p class="text-xs text-muted">Fotografias: disponibles en una etapa posterior.</p>
      </div>
    {:else}
      <!-- Paso 4: Confirmacion -->
      <div class="space-y-3 text-sm">
        <div class="rounded-control border border-line p-3">
          <p class="font-medium text-ink">{loteSel?.producto_descripcion}</p>
          <p class="text-muted">{loteSel?.producto_sku} · Lote {loteSel?.numero_lote}</p>
        </div>
        <dl class="grid grid-cols-2 gap-2">
          <div><dt class="text-muted">Vencimiento</dt><dd class="text-ink">{fechaLocal(fechaVenc)}</dd></div>
          <div><dt class="text-muted">Contado</dt><dd class="text-ink">{num(cantidadContada)} ({cajas} cajas + {num(unidades)} und.)</dd></div>
          <div><dt class="text-muted">Estado</dt><dd class="text-ink">{ESTADOS.find((e) => e.value === estado)?.label}</dd></div>
          <div><dt class="text-muted">Responsable</dt><dd class="text-ink">{me?.nombre ?? '—'}</dd></div>
        </dl>
        {#if estado === 'averiado'}
          <p class="rounded-control bg-estado-critica/5 px-3 py-2 text-estado-critica">
            Se registrara una novedad: {tipoNovedad}, {num(cantidadAfectada)} afectadas.
          </p>
        {/if}
        {#if difiere}
          <p class="rounded-control bg-estado-prioritaria/10 px-3 py-2 text-orange-700">
            Diferencia con el inventario registrada para revision (no modifica existencias).
          </p>
        {/if}
      </div>
    {/if}
  </div>

  <!-- Footer nav -->
  <footer class="flex items-center justify-between border-t border-line px-5 py-3">
    <button
      onclick={() => (paso = Math.max(1, paso - 1))}
      disabled={paso === 1}
      class="rounded-control px-3 py-2 text-sm font-medium text-ink hover:bg-canvas disabled:opacity-40"
    >
      Atras
    </button>
    {#if paso < 4}
      <button
        onclick={() => (paso += 1)}
        disabled={!puedeAvanzar}
        class="rounded-control bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
      >
        Siguiente
      </button>
    {:else}
      <button
        onclick={guardar}
        disabled={guardando}
        class="rounded-control bg-estado-normal px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
      >
        {guardando ? 'Guardando...' : 'Guardar inspeccion'}
      </button>
    {/if}
  </footer>
</div>
