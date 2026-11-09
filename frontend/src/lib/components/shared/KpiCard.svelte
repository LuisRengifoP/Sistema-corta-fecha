<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    label,
    valor,
    acento = 'neutral',
    href = null,
    icon
  }: {
    label: string;
    valor: string | number;
    acento?: 'neutral' | 'normal' | 'preventiva' | 'prioritaria' | 'critica';
    href?: string | null;
    icon?: Snippet;
  } = $props();

  const ACENTO: Record<string, string> = {
    neutral: 'bg-line',
    normal: 'bg-estado-normal',
    preventiva: 'bg-estado-preventiva',
    prioritaria: 'bg-estado-prioritaria',
    critica: 'bg-estado-critica'
  };
</script>

<svelte:element
  this={href ? 'a' : 'div'}
  {href}
  class="block rounded-card border border-line bg-surface p-4 shadow-card transition {href
    ? 'hover:border-brand/40'
    : ''}"
>
  <div class="flex items-center gap-2">
    <span class="h-2.5 w-2.5 rounded-full {ACENTO[acento]}"></span>
    <span class="text-xs font-medium text-muted">{label}</span>
    {#if icon}
      <span class="ml-auto text-muted">{@render icon()}</span>
    {/if}
  </div>
  <p class="mt-2 text-kpi text-ink">{valor}</p>
</svelte:element>
