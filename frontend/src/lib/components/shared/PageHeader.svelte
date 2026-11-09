<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    titulo,
    descripcion = '',
    acciones
  }: { titulo: string; descripcion?: string; acciones?: Snippet } = $props();
</script>

<div class="mb-5 flex items-start justify-between gap-4">
  <div>
    <h1 class="text-[22px] font-bold text-ink">{titulo}</h1>
    {#if descripcion}
      <p class="mt-0.5 text-sm text-muted">{descripcion}</p>
    {/if}
  </div>
  {#if acciones}
    <div class="flex items-center gap-2">{@render acciones()}</div>
  {/if}
</div>
