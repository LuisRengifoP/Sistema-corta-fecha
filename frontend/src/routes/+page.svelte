<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/ui';
  import type { EstadoAlerta, ResumenDashboard } from '$lib/types';
  import PageHeader from '$lib/components/shared/PageHeader.svelte';
  import KpiCard from '$lib/components/shared/KpiCard.svelte';
  import LoadingState from '$lib/components/shared/LoadingState.svelte';
  import ErrorState from '$lib/components/shared/ErrorState.svelte';
  import RefreshCw from 'lucide-svelte/icons/refresh-cw';

  let resumen = $state<ResumenDashboard | null>(null);
  let error = $state('');
  let cargando = $state(true);
  let recalculando = $state(false);

  const ESTADOS: { key: EstadoAlerta; label: string; acento: 'normal' | 'preventiva' | 'prioritaria' | 'critica' }[] = [
    { key: 'vencido', label: 'Vencidos', acento: 'critica' },
    { key: 'critica', label: 'Criticos', acento: 'critica' },
    { key: 'prioritaria', label: 'Prioritarios', acento: 'prioritaria' },
    { key: 'preventiva', label: 'Preventivos', acento: 'preventiva' },
    { key: 'normal', label: 'Normales', acento: 'normal' }
  ];

  async function cargar() {
    cargando = true;
    error = '';
    try {
      resumen = await api.get<ResumenDashboard>('/api/v1/dashboard/resumen');
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
    cargar();
  });
</script>

<PageHeader
  titulo="Dashboard"
  descripcion="Vision operativa de vencimientos, inspecciones y novedades."
>
  {#snippet acciones()}
    <button
      onclick={recalcular}
      disabled={recalculando}
      class="inline-flex items-center gap-2 rounded-control bg-brand px-3 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:opacity-50"
    >
      <RefreshCw size={15} class={recalculando ? 'animate-spin' : ''} />
      {recalculando ? 'Recalculando...' : 'Recalcular alertas'}
    </button>
  {/snippet}
</PageHeader>

{#if cargando}
  <LoadingState />
{:else if error}
  <ErrorState mensaje={error} onReintentar={cargar} />
{:else if resumen}
  <div class="space-y-6">
    <section>
      <h3 class="mb-2 text-sm font-semibold text-muted">Alertas por estado</h3>
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        {#each ESTADOS as e (e.key)}
          <KpiCard label={e.label} valor={resumen.alertas_por_estado[e.key]} acento={e.acento} />
        {/each}
      </div>
    </section>

    <section>
      <h3 class="mb-2 text-sm font-semibold text-muted">Inventario</h3>
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <KpiCard label="Productos" valor={resumen.total_productos} />
        <KpiCard label="Lotes" valor={resumen.total_lotes} />
        <KpiCard label="Alertas activas" valor={resumen.total_alertas} />
        <KpiCard
          label="Lotes sin fecha"
          valor={resumen.lotes_sin_fecha}
          acento={resumen.lotes_sin_fecha > 0 ? 'prioritaria' : 'neutral'}
        />
      </div>
    </section>
  </div>
{/if}
