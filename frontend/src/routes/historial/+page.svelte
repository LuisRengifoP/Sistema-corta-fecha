<script lang="ts">
  import { api } from '$lib/services/api';
  import type { AccionAuditoria, HistorialCambio, Pagina } from '$lib/types';
  import { fechaHora } from '$lib/utils/format';
  import PageHeader from '$lib/components/shared/PageHeader.svelte';
  import LoadingState from '$lib/components/shared/LoadingState.svelte';
  import ErrorState from '$lib/components/shared/ErrorState.svelte';
  import EmptyState from '$lib/components/shared/EmptyState.svelte';
  import Pagination from '$lib/components/shared/Pagination.svelte';

  const ACCIONES: { value: AccionAuditoria | ''; label: string }[] = [
    { value: '', label: 'Todas las acciones' },
    { value: 'insert', label: 'Creacion' },
    { value: 'update', label: 'Actualizacion' },
    { value: 'delete', label: 'Eliminacion' }
  ];
  const ACCION_BADGE: Record<AccionAuditoria, string> = {
    insert: 'bg-estado-normal/10 text-estado-normal',
    update: 'bg-brand/10 text-brand',
    delete: 'bg-estado-critica/10 text-estado-critica'
  };
  const ACCION_LABEL: Record<AccionAuditoria, string> = {
    insert: 'Creacion',
    update: 'Actualizacion',
    delete: 'Eliminacion'
  };

  const LIMIT = 50;

  let pagina = $state<Pagina<HistorialCambio> | null>(null);
  let tablas = $state<string[]>([]);
  let error = $state('');
  let cargando = $state(true);

  let filtroTabla = $state('');
  let filtroAccion = $state<AccionAuditoria | ''>('');
  let desde = $state('');
  let hasta = $state('');
  let skip = $state(0);
  let expandida = $state<number | null>(null);

  function qs(): string {
    const p = new URLSearchParams();
    if (filtroTabla) p.set('tabla', filtroTabla);
    if (filtroAccion) p.set('accion', filtroAccion);
    if (desde) p.set('desde', new Date(desde).toISOString());
    if (hasta) p.set('hasta', new Date(hasta).toISOString());
    p.set('skip', String(skip));
    p.set('limit', String(LIMIT));
    return p.toString();
  }

  async function cargar() {
    cargando = true;
    error = '';
    try {
      pagina = await api.get<Pagina<HistorialCambio>>(`/api/v1/historial?${qs()}`);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error';
    } finally {
      cargando = false;
    }
  }

  async function cargarTablas() {
    try {
      tablas = await api.get<string[]>('/api/v1/historial/tablas');
    } catch {
      tablas = [];
    }
  }

  function aplicarFiltros() {
    skip = 0;
    cargar();
  }

  function limpiar() {
    filtroTabla = '';
    filtroAccion = '';
    desde = '';
    hasta = '';
    skip = 0;
    cargar();
  }

  function irPagina(nuevoSkip: number) {
    skip = nuevoSkip;
    expandida = null;
    cargar();
  }

  $effect(() => {
    cargarTablas();
    cargar();
  });
</script>

<PageHeader titulo="Historial de cambios" descripcion="Auditoria de las operaciones realizadas en el sistema." />

<div class="mb-4 flex flex-wrap items-end gap-3">
  <div>
    <label for="tabla" class="mb-1 block text-xs font-medium text-muted">Tabla</label>
    <select id="tabla" bind:value={filtroTabla}
      class="rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none">
      <option value="">Todas las tablas</option>
      {#each tablas as t (t)}<option value={t}>{t}</option>{/each}
    </select>
  </div>
  <div>
    <label for="accion" class="mb-1 block text-xs font-medium text-muted">Accion</label>
    <select id="accion" bind:value={filtroAccion}
      class="rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none">
      {#each ACCIONES as a (a.value)}<option value={a.value}>{a.label}</option>{/each}
    </select>
  </div>
  <div>
    <label for="desde" class="mb-1 block text-xs font-medium text-muted">Desde</label>
    <input id="desde" type="date" bind:value={desde}
      class="rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none" />
  </div>
  <div>
    <label for="hasta" class="mb-1 block text-xs font-medium text-muted">Hasta</label>
    <input id="hasta" type="date" bind:value={hasta}
      class="rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none" />
  </div>
  <button onclick={aplicarFiltros}
    class="rounded-control bg-brand px-3 py-2 text-sm font-medium text-white hover:bg-brand-700">Filtrar</button>
  <button onclick={limpiar}
    class="rounded-control border border-line px-3 py-2 text-sm font-medium text-ink hover:bg-canvas">Limpiar</button>
</div>

{#if cargando}
  <LoadingState />
{:else if error}
  <ErrorState mensaje={error} onReintentar={cargar} />
{:else if !pagina || pagina.items.length === 0}
  <EmptyState titulo="Sin registros" descripcion="No hay cambios que coincidan con los filtros." />
{:else}
  <div class="overflow-hidden rounded-card border border-line bg-surface shadow-card">
    <div class="overflow-x-auto">
      <table class="w-full min-w-[820px] text-sm">
        <thead>
          <tr class="border-b border-line text-left text-xs font-semibold uppercase tracking-wide text-muted">
            <th class="px-4 py-3">Fecha</th>
            <th class="px-4 py-3">Tabla</th>
            <th class="px-4 py-3">Registro</th>
            <th class="px-4 py-3">Accion</th>
            <th class="px-4 py-3">Usuario</th>
            <th class="px-4 py-3 text-right">Datos</th>
          </tr>
        </thead>
        <tbody>
          {#each pagina.items as h (h.id)}
            <tr class="border-b border-line last:border-0 hover:bg-canvas">
              <td class="px-4 py-3 text-ink">{fechaHora(h.created_at)}</td>
              <td class="px-4 py-3 font-medium text-ink">{h.tabla}</td>
              <td class="px-4 py-3 text-ink">#{h.registro_id}</td>
              <td class="px-4 py-3">
                <span class="inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium {ACCION_BADGE[h.accion]}">
                  {ACCION_LABEL[h.accion]}
                </span>
              </td>
              <td class="px-4 py-3 text-ink">{h.usuario_nombre ?? '—'}</td>
              <td class="px-4 py-3 text-right">
                <button onclick={() => (expandida = expandida === h.id ? null : h.id)}
                  class="rounded-control border border-line px-2.5 py-1 text-xs font-medium text-ink hover:bg-canvas">
                  {expandida === h.id ? 'Ocultar' : 'Ver'}
                </button>
              </td>
            </tr>
            {#if expandida === h.id}
              <tr class="border-b border-line bg-canvas last:border-0">
                <td colspan="6" class="px-4 py-3">
                  <div class="grid gap-3 md:grid-cols-2">
                    <div>
                      <p class="mb-1 text-xs font-semibold uppercase tracking-wide text-muted">Antes</p>
                      <pre class="overflow-x-auto rounded-control border border-line bg-surface p-3 text-xs text-ink">{h.datos_antes ? JSON.stringify(h.datos_antes, null, 2) : '—'}</pre>
                    </div>
                    <div>
                      <p class="mb-1 text-xs font-semibold uppercase tracking-wide text-muted">Despues</p>
                      <pre class="overflow-x-auto rounded-control border border-line bg-surface p-3 text-xs text-ink">{h.datos_despues ? JSON.stringify(h.datos_despues, null, 2) : '—'}</pre>
                    </div>
                  </div>
                </td>
              </tr>
            {/if}
          {/each}
        </tbody>
      </table>
    </div>
    <Pagination total={pagina.total} skip={pagina.skip} limit={pagina.limit} onPage={irPagina} />
  </div>
{/if}
