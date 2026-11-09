<script lang="ts">
  let {
    mensaje = 'Ocurrio un error.',
    onReintentar = null
  }: { mensaje?: string; onReintentar?: (() => void) | null } = $props();
</script>

<div class="rounded-card border border-estado-critica/30 bg-estado-critica/5 p-4">
  <p class="text-sm text-estado-critica">{mensaje}</p>
  {#if onReintentar}
    <button
      onclick={onReintentar}
      class="mt-2 rounded-control border border-estado-critica/40 px-3 py-1 text-xs font-medium text-estado-critica hover:bg-estado-critica/10"
    >
      Reintentar
    </button>
  {/if}
</div>
