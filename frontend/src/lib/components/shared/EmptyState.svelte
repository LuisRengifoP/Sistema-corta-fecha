<script lang="ts">
  let {
    titulo = 'Sin registros',
    descripcion = ''
  }: { titulo?: string; descripcion?: string } = $props();
</script>

<div class="rounded-card border border-dashed border-line bg-surface p-8 text-center">
  <p class="text-sm font-medium text-ink">{titulo}</p>
  {#if descripcion}
    <p class="mt-1 text-sm text-muted">{descripcion}</p>
  {/if}
</div>
