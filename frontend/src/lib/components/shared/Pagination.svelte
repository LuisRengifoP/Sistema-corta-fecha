<script lang="ts">
  import ChevronLeft from 'lucide-svelte/icons/chevron-left';
  import ChevronRight from 'lucide-svelte/icons/chevron-right';

  let {
    total,
    skip,
    limit,
    onPage
  }: {
    total: number;
    skip: number;
    limit: number;
    /** Nuevo offset (skip) solicitado. */
    onPage: (skip: number) => void;
  } = $props();

  const paginaActual = $derived(Math.floor(skip / limit) + 1);
  const totalPaginas = $derived(Math.max(1, Math.ceil(total / limit)));
  const desde = $derived(total === 0 ? 0 : skip + 1);
  const hasta = $derived(Math.min(skip + limit, total));

  function ir(pagina: number) {
    const p = Math.min(Math.max(1, pagina), totalPaginas);
    onPage((p - 1) * limit);
  }
</script>

<div class="flex items-center justify-between gap-3 border-t border-line px-4 py-3 text-sm">
  <p class="text-muted">
    {desde}–{hasta} de {total}
  </p>
  <div class="flex items-center gap-1">
    <button
      onclick={() => ir(paginaActual - 1)}
      disabled={paginaActual <= 1}
      class="flex items-center gap-1 rounded-control border border-line px-2.5 py-1.5 font-medium text-ink hover:bg-canvas disabled:cursor-not-allowed disabled:opacity-40"
      aria-label="Pagina anterior"
    >
      <ChevronLeft size={15} /> Anterior
    </button>
    <span class="px-2 text-muted">Pagina {paginaActual} de {totalPaginas}</span>
    <button
      onclick={() => ir(paginaActual + 1)}
      disabled={paginaActual >= totalPaginas}
      class="flex items-center gap-1 rounded-control border border-line px-2.5 py-1.5 font-medium text-ink hover:bg-canvas disabled:cursor-not-allowed disabled:opacity-40"
      aria-label="Pagina siguiente"
    >
      Siguiente <ChevronRight size={15} />
    </button>
  </div>
</div>
