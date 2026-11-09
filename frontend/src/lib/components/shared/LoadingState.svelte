<script lang="ts">
  let { mensaje = 'Cargando...' }: { mensaje?: string } = $props();
</script>

<div class="flex items-center justify-center gap-2 rounded-card border border-line bg-surface p-8 text-sm text-muted">
  <span class="h-4 w-4 animate-spin rounded-full border-2 border-line border-t-brand"></span>
  {mensaje}
</div>
