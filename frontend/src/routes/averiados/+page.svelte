<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/ui';
  import type { DisposicionNovedad, NovedadResumen, NovedadVistaRow, TipoNovedad } from '$lib/types';
  import { fechaHora, num } from '$lib/utils/format';
  import PageHeader from '$lib/components/shared/PageHeader.svelte';
  import KpiCard from '$lib/components/shared/KpiCard.svelte';
  import LoadingState from '$lib/components/shared/LoadingState.svelte';
  import ErrorState from '$lib/components/shared/ErrorState.svelte';
  import EmptyState from '$lib/components/shared/EmptyState.svelte';
  import GestionModal from '$lib/components/alerts/GestionModal.svelte';
  import NuevaNovedadModal from '$lib/components/damages/NuevaNovedadModal.svelte';
  import LotDetailDrawer from '$lib/components/lots/LotDetailDrawer.svelte';
  import PlusIcon from 'lucide-svelte/icons/plus';

  const TIPO: Record<TipoNovedad, string> = {
    averia: 'Averia',
    rotura: 'Rotura',
    contaminacion: 'Contaminacion',
    empaque_danado: 'Empaque danado',
    otro: 'Otro'
  };
  const DISP: { value: DisposicionNovedad; label: string }[] = [
    { value: 'pendiente', label: 'Pendiente' },
    { value: 'devolucion_proveedor', label: 'Devolucion a proveedor' },
    { value: 'baja', label: 'Baja' },
    { value: 'donacion', label: 'Donacion' },
    { value: 'reproceso', label: 'Reproceso' },
    { value: 'venta_descuento', label: 'Venta con descuento' }
  ];
  const DISP_LABEL = Object.fromEntries(DISP.map((d) => [d.value, d.label]));

  let filas = $state<NovedadVistaRow[]>([]);
  let resumen = $state<NovedadResumen | null>(null);
  let error = $state('');
  let cargando = $state(true);
  let filtroDisp = $state<DisposicionNovedad | ''>('');

  let nuevaAbierta = $state(false);
  let novedadGestion = $state<NovedadVistaRow | null>(null);
  let loteVer = $state<number | null>(null);

  async function cargar() {
    cargando = true;
    error = '';
    try {
      const q = filtroDisp ? `?disposicion=${filtroDisp}` : '';
      [filas, resumen] = await Promise.all([
        api.get<NovedadVistaRow[]>(`/api/v1/novedades/vista${q}`),
        api.get<NovedadResumen>('/api/v1/novedades/resumen')
      ]);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error';
    } finally {
      cargando = false;
    }
  }

  async function cambiarDisposicion(nov: NovedadVistaRow, value: DisposicionNovedad) {
    try {
      await api.patch(`/api/v1/novedades/${nov.id}`, { disposicion: value });
      toast('Disposicion actualizada', 'ok');
      await cargar();
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Error', 'error');
    }
  }

  $effect(() => {
    filtroDisp;
    cargar();
  });
</script>

<PageHeader titulo="Productos averiados" descripcion="Gestion de mercancia danada, separada de las alertas de vencimiento.">
  {#snippet acciones()}
    <button onclick={() => (nuevaAbierta = true)}
      class="inline-flex items-center gap-2 rounded-control bg-brand px-3 py-2 text-sm font-medium text-white hover:bg-brand-700">
      <PlusIcon size={15} /> Registrar novedad
    </button>
  {/snippet}
</PageHeader>

{#if resumen}
  <div class="mb-5 grid grid-cols-2 gap-4 sm:grid-cols-4">
    <KpiCard label="Novedades abiertas" valor={resumen.abiertas} acento="prioritaria" />
    <KpiCard label="Cantidad afectada" valor={num(resumen.cantidad_afectada)} />
    <KpiCard label="Cerradas" valor={resumen.cerradas} acento="normal" />
    <KpiCard label="Total casos" valor={resumen.total} />
  </div>
{/if}

<div class="mb-4 flex items-center gap-3">
  <select bind:value={filtroDisp}
    class="rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none">
    <option value="">Todas las disposiciones</option>
    {#each DISP as d (d.value)}<option value={d.value}>{d.label}</option>{/each}
  </select>
</div>

{#if cargando}
  <LoadingState />
{:else if error}
  <ErrorState mensaje={error} onReintentar={cargar} />
{:else if filas.length === 0}
  <EmptyState titulo="Sin novedades" descripcion="No hay productos averiados registrados." />
{:else}
  <div class="overflow-x-auto rounded-card border border-line bg-surface shadow-card">
    <table class="w-full min-w-[920px] text-sm">
      <thead>
        <tr class="border-b border-line text-left text-xs font-semibold uppercase tracking-wide text-muted">
          <th class="px-4 py-3">Fecha</th>
          <th class="px-4 py-3">Producto</th>
          <th class="px-4 py-3">Lote</th>
          <th class="px-4 py-3">Tipo</th>
          <th class="px-4 py-3 text-right">Afectada</th>
          <th class="px-4 py-3">Bodega</th>
          <th class="px-4 py-3">Reporto</th>
          <th class="px-4 py-3">Disposicion</th>
          <th class="px-4 py-3 text-right">Acciones</th>
        </tr>
      </thead>
      <tbody>
        {#each filas as f (f.id)}
          <tr class="border-b border-line last:border-0 hover:bg-canvas">
            <td class="px-4 py-3 text-ink">{fechaHora(f.created_at)}</td>
            <td class="px-4 py-3">
              <p class="font-medium text-ink">{f.producto_descripcion}</p>
              <p class="text-xs text-muted">{f.producto_sku}</p>
            </td>
            <td class="px-4 py-3 text-ink">{f.numero_lote}</td>
            <td class="px-4 py-3 text-ink">{TIPO[f.tipo]}</td>
            <td class="px-4 py-3 text-right text-ink">{num(f.cantidad_afectada)}</td>
            <td class="px-4 py-3 text-ink">{f.bodega_nombre}</td>
            <td class="px-4 py-3 text-ink">{f.reportado_por}</td>
            <td class="px-4 py-3">
              <select
                value={f.disposicion}
                onchange={(e) => cambiarDisposicion(f, e.currentTarget.value as DisposicionNovedad)}
                class="rounded-control border border-line bg-surface px-2 py-1 text-xs text-ink focus:border-brand focus:outline-none"
              >
                {#each DISP as d (d.value)}<option value={d.value}>{d.label}</option>{/each}
              </select>
            </td>
            <td class="px-4 py-3">
              <div class="flex justify-end gap-2">
                <button onclick={() => (loteVer = f.lote_id)}
                  class="rounded-control border border-line px-2.5 py-1 text-xs font-medium text-ink hover:bg-canvas">
                  Ver lote
                </button>
                <button onclick={() => (novedadGestion = f)}
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

{#if nuevaAbierta}
  <NuevaNovedadModal onClose={() => (nuevaAbierta = false)} onSaved={cargar} />
{/if}

{#if novedadGestion}
  <GestionModal
    url={`/api/v1/novedades/${novedadGestion.id}/gestion`}
    titulo="Gestionar novedad"
    subtitulo={`${novedadGestion.producto_descripcion} · ${novedadGestion.producto_sku} · Lote ${novedadGestion.numero_lote}`}
    onClose={() => (novedadGestion = null)}
    onSaved={cargar}
  />
{/if}

{#if loteVer !== null}
  <LotDetailDrawer loteId={loteVer} onClose={() => (loteVer = null)} />
{/if}
