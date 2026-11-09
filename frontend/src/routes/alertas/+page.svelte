<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/ui';
  import type { AlertaVistaRow, EstadoSeguimiento } from '$lib/types';
  import { fechaLocal, num } from '$lib/utils/format';
  import PageHeader from '$lib/components/shared/PageHeader.svelte';
  import EstadoLoteBadge from '$lib/components/shared/EstadoLoteBadge.svelte';
  import LoadingState from '$lib/components/shared/LoadingState.svelte';
  import ErrorState from '$lib/components/shared/ErrorState.svelte';
  import EmptyState from '$lib/components/shared/EmptyState.svelte';
  import GestionModal from '$lib/components/alerts/GestionModal.svelte';
  import LotDetailDrawer from '$lib/components/lots/LotDetailDrawer.svelte';
  import RefreshCw from 'lucide-svelte/icons/refresh-cw';

  type Bandeja = { key: string; label: string; query: string };
  const BANDEJAS: Bandeja[] = [
    { key: 'todas', label: 'Todas', query: '' },
    { key: 'vencidas', label: 'Vencidas', query: 'estado=vencido' },
    { key: 'criticas', label: 'Criticas', query: 'estado=critica' },
    { key: 'prioritarias', label: 'Prioritarias', query: 'estado=prioritaria' },
    { key: 'preventivas', label: 'Preventivas', query: 'estado=preventiva' },
    { key: 'sin_resp', label: 'Sin responsable', query: 'sin_responsable=true' },
    { key: 'pend_gestion', label: 'Pendientes de gestion', query: 'seguimiento=pendiente' }
  ];

  const SEG_LABEL: Record<EstadoSeguimiento, string> = {
    pendiente: 'Pendiente',
    en_gestion: 'En gestion',
    gestionada: 'Gestionada',
    descartada: 'Descartada'
  };

  let bandeja = $state('todas');
  let filas = $state<AlertaVistaRow[]>([]);
  let error = $state('');
  let cargando = $state(true);
  let recalculando = $state(false);

  let alertaGestion = $state<AlertaVistaRow | null>(null);
  let loteVer = $state<number | null>(null);

  async function cargar() {
    cargando = true;
    error = '';
    try {
      const q = BANDEJAS.find((b) => b.key === bandeja)?.query ?? '';
      filas = await api.get<AlertaVistaRow[]>(`/api/v1/alertas/vista${q ? `?${q}` : ''}`);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error';
    } finally {
      cargando = false;
    }
  }

  async function recalcular() {
    recalculando = true;
    try {
      await api.post('/api/v1/alertas/recalcular', {});
      await cargar();
      toast('Alertas recalculadas', 'ok');
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Error', 'error');
    } finally {
      recalculando = false;
    }
  }

  $effect(() => {
    bandeja;
    cargar();
  });
</script>

<PageHeader titulo="Alertas y seguimiento" descripcion="Convierte vencimientos en tareas con responsable y resultado.">
  {#snippet acciones()}
    <button onclick={recalcular} disabled={recalculando}
      class="inline-flex items-center gap-2 rounded-control bg-brand px-3 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
      <RefreshCw size={15} class={recalculando ? 'animate-spin' : ''} />
      {recalculando ? 'Recalculando...' : 'Recalcular'}
    </button>
  {/snippet}
</PageHeader>

<!-- Bandejas -->
<div class="mb-4 flex flex-wrap gap-2">
  {#each BANDEJAS as b (b.key)}
    <button
      onclick={() => (bandeja = b.key)}
      class="rounded-full px-3 py-1.5 text-sm font-medium transition
        {bandeja === b.key ? 'bg-navy text-white' : 'border border-line bg-surface text-muted hover:text-ink'}"
    >
      {b.label}
    </button>
  {/each}
</div>

{#if cargando}
  <LoadingState />
{:else if error}
  <ErrorState mensaje={error} onReintentar={cargar} />
{:else if filas.length === 0}
  <EmptyState titulo="Sin alertas" descripcion="No hay alertas en esta bandeja." />
{:else}
  <div class="overflow-x-auto rounded-card border border-line bg-surface shadow-card">
    <table class="w-full min-w-[920px] text-sm">
      <thead>
        <tr class="border-b border-line text-left text-xs font-semibold uppercase tracking-wide text-muted">
          <th class="px-4 py-3">Estado</th>
          <th class="px-4 py-3">Producto</th>
          <th class="px-4 py-3">Lote</th>
          <th class="px-4 py-3 text-right">Dias</th>
          <th class="px-4 py-3 text-right">Cantidad</th>
          <th class="px-4 py-3">Seguimiento</th>
          <th class="px-4 py-3">Responsable</th>
          <th class="px-4 py-3">Insp.</th>
          <th class="px-4 py-3 text-right">Acciones</th>
        </tr>
      </thead>
      <tbody>
        {#each filas as f (f.id)}
          <tr class="border-b border-line last:border-0 hover:bg-canvas">
            <td class="px-4 py-3"><EstadoLoteBadge estado={f.estado} /></td>
            <td class="px-4 py-3">
              <p class="font-medium text-ink">{f.producto_descripcion}</p>
              <p class="text-xs text-muted">{f.producto_sku} · {f.sucursal_nombre}</p>
            </td>
            <td class="px-4 py-3 text-ink">{f.numero_lote}</td>
            <td class="px-4 py-3 text-right text-ink">{f.dias_restantes ?? '—'}</td>
            <td class="px-4 py-3 text-right text-ink">
              {f.cantidad_en_riesgo !== null ? num(f.cantidad_en_riesgo) : '—'}
            </td>
            <td class="px-4 py-3">
              <span class="rounded-full bg-canvas px-2 py-0.5 text-xs font-medium text-muted">
                {SEG_LABEL[f.seguimiento]}
              </span>
            </td>
            <td class="px-4 py-3 text-ink">{f.responsable ?? '—'}</td>
            <td class="px-4 py-3">
              {#if f.tiene_inspeccion}
                <span class="text-xs font-medium text-estado-normal">Si</span>
              {:else}
                <span class="text-xs text-muted">No</span>
              {/if}
            </td>
            <td class="px-4 py-3">
              <div class="flex justify-end gap-2">
                <button onclick={() => (loteVer = f.lote_id)}
                  class="rounded-control border border-line px-2.5 py-1 text-xs font-medium text-ink hover:bg-canvas">
                  Ver lote
                </button>
                <button onclick={() => (alertaGestion = f)}
                  class="rounded-control bg-brand px-2.5 py-1 text-xs font-medium text-white hover:bg-brand-700">
                  Gestionar
                </button>
              </div>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

{#if alertaGestion}
  <GestionModal
    url={`/api/v1/alertas/${alertaGestion.id}/gestion`}
    titulo="Gestionar alerta"
    subtitulo={`${alertaGestion.producto_descripcion} · ${alertaGestion.producto_sku} · Lote ${alertaGestion.numero_lote} · ${alertaGestion.sucursal_nombre}`}
    onClose={() => (alertaGestion = null)}
    onSaved={cargar}
  />
{/if}

{#if loteVer !== null}
  <LotDetailDrawer loteId={loteVer} onClose={() => (loteVer = null)} />
{/if}
