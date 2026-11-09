<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/ui';
  import { fechaLocal, fechaHora, num } from '$lib/utils/format';
  import PageHeader from '$lib/components/shared/PageHeader.svelte';
  import LoadingState from '$lib/components/shared/LoadingState.svelte';
  import ErrorState from '$lib/components/shared/ErrorState.svelte';
  import EmptyState from '$lib/components/shared/EmptyState.svelte';
  import FileDown from 'lucide-svelte/icons/file-down';

  type Columna = { clave: string; etiqueta: string };
  type Preview = {
    tipo: string;
    titulo: string;
    columnas: Columna[];
    filas: Record<string, unknown>[];
    resumen: Record<string, number | string>;
  };

  const TIPOS = [
    { tipo: 'lotes', titulo: 'Lotes por vencimiento' },
    { tipo: 'inspecciones', titulo: 'Inspecciones realizadas' },
    { tipo: 'averiados', titulo: 'Productos averiados' }
  ];
  const ESTADOS = ['', 'vencido', 'critica', 'prioritaria', 'preventiva', 'normal', 'sin_fecha'];

  let tipo = $state('lotes');
  let estado = $state('');
  let data = $state<Preview | null>(null);
  let error = $state('');
  let cargando = $state(true);
  let descargando = $state(false);

  function queryString(): string {
    const p = new URLSearchParams();
    if (tipo === 'lotes' && estado) p.set('estado', estado);
    const s = p.toString();
    return s ? `?${s}` : '';
  }

  function celda(clave: string, valor: unknown): string {
    if (valor === null || valor === undefined || valor === '') return '—';
    if (clave === 'fecha_inspeccion' || clave === 'created_at') return fechaHora(String(valor));
    if (clave === 'fecha_vencimiento') return fechaLocal(String(valor));
    if (['existencia_total', 'cantidad_contada', 'cantidad_afectada'].includes(clave))
      return num(valor as string);
    return String(valor);
  }

  async function cargar() {
    cargando = true;
    error = '';
    try {
      data = await api.get<Preview>(`/api/v1/reportes/${tipo}/preview${queryString()}`);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error';
    } finally {
      cargando = false;
    }
  }

  async function exportar() {
    descargando = true;
    try {
      await api.download(`/api/v1/reportes/${tipo}/excel${queryString()}`, `reporte_${tipo}.xlsx`);
      toast('Excel generado', 'ok');
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Error', 'error');
    } finally {
      descargando = false;
    }
  }

  $effect(() => {
    tipo;
    estado;
    cargar();
  });
</script>

<PageHeader titulo="Reportes" descripcion="Filtra y exporta a Excel. La exportacion respeta los filtros activos.">
  {#snippet acciones()}
    <button onclick={exportar} disabled={descargando || !data || data.filas.length === 0}
      class="inline-flex items-center gap-2 rounded-control bg-estado-normal px-3 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50">
      <FileDown size={15} />
      {descargando ? 'Generando...' : 'Exportar a Excel'}
    </button>
  {/snippet}
</PageHeader>

<!-- Filtros -->
<div class="mb-4 flex flex-wrap items-center gap-3">
  <select bind:value={tipo}
    class="rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none">
    {#each TIPOS as t (t.tipo)}<option value={t.tipo}>{t.titulo}</option>{/each}
  </select>
  {#if tipo === 'lotes'}
    <select bind:value={estado}
      class="rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none">
      {#each ESTADOS as e (e)}<option value={e}>{e === '' ? 'Todos los estados' : e}</option>{/each}
    </select>
  {/if}
</div>

{#if cargando}
  <LoadingState />
{:else if error}
  <ErrorState mensaje={error} onReintentar={cargar} />
{:else if data}
  <!-- Resumen -->
  <div class="mb-4 flex flex-wrap gap-2">
    {#each Object.entries(data.resumen) as [k, v] (k)}
      <span class="rounded-full border border-line bg-surface px-3 py-1 text-xs text-muted">
        {k}: <span class="font-semibold text-ink">{v}</span>
      </span>
    {/each}
  </div>

  {#if data.filas.length === 0}
    <EmptyState titulo="Sin datos" descripcion="No hay registros para los filtros seleccionados." />
  {:else}
    <div class="overflow-x-auto rounded-card border border-line bg-surface shadow-card">
      <table class="w-full min-w-[720px] text-sm">
        <thead>
          <tr class="border-b border-line text-left text-xs font-semibold uppercase tracking-wide text-muted">
            {#each data.columnas as c (c.clave)}<th class="px-4 py-3">{c.etiqueta}</th>{/each}
          </tr>
        </thead>
        <tbody>
          {#each data.filas as f, i (i)}
            <tr class="border-b border-line last:border-0">
              {#each data.columnas as c (c.clave)}
                <td class="px-4 py-3 text-ink">{celda(c.clave, f[c.clave])}</td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
{/if}
