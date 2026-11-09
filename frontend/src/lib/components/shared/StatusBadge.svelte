<script lang="ts">
  import type { EstadoAlerta } from '$lib/types';

  let { estado }: { estado: EstadoAlerta } = $props();

  const MAP: Record<EstadoAlerta, { label: string; clases: string }> = {
    normal: { label: 'Normal', clases: 'bg-estado-normal/10 text-estado-normal' },
    preventiva: { label: 'Preventiva', clases: 'bg-estado-preventiva/15 text-yellow-700' },
    prioritaria: { label: 'Prioritaria', clases: 'bg-estado-prioritaria/15 text-orange-700' },
    critica: { label: 'Critica', clases: 'bg-estado-critica/10 text-estado-critica' },
    vencido: { label: 'Vencido', clases: 'bg-estado-critica text-white' }
  };

  let item = $derived(MAP[estado]);
</script>

<span
  class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium {item.clases}"
>
  <span class="h-1.5 w-1.5 rounded-full bg-current"></span>
  {item.label}
</span>
