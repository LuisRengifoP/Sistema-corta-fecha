<script lang="ts">
  import { toasts } from '$lib/stores/ui';

  const COLOR = {
    ok: 'border-estado-normal/30 bg-estado-normal/5 text-estado-normal',
    error: 'border-estado-critica/30 bg-estado-critica/5 text-estado-critica',
    info: 'border-line bg-surface text-ink'
  };
</script>

<div class="pointer-events-none fixed bottom-4 right-4 z-50 flex flex-col gap-2">
  {#each $toasts as t (t.id)}
    <div
      class="pointer-events-auto rounded-control border px-4 py-2 text-sm shadow-elevated {COLOR[
        t.tipo
      ]}"
    >
      {t.texto}
    </div>
  {/each}
</div>
