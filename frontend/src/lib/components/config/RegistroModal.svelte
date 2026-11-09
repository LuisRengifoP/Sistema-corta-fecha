<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/ui';
  import XIcon from 'lucide-svelte/icons/x';

  export type Campo = {
    key: string;
    label: string;
    tipo: 'text' | 'textarea' | 'checkbox' | 'select';
    opciones?: { value: number | string; label: string }[];
    requerido?: boolean;
  };

  let {
    titulo,
    endpoint,
    campos,
    registro = null,
    onClose,
    onSaved
  }: {
    titulo: string;
    endpoint: string;
    campos: Campo[];
    registro?: Record<string, unknown> | null;
    onClose: () => void;
    onSaved: () => void;
  } = $props();

  const edicion = registro !== null;

  function inicial(): Record<string, unknown> {
    const v: Record<string, unknown> = {};
    for (const c of campos) {
      if (registro && c.key in registro) v[c.key] = registro[c.key];
      else v[c.key] = c.tipo === 'checkbox' ? true : c.tipo === 'select' ? (c.opciones?.[0]?.value ?? null) : '';
    }
    return v;
  }

  let valores = $state<Record<string, unknown>>(inicial());
  let guardando = $state(false);

  const puedeGuardar = $derived(
    campos.every((c) => {
      if (!c.requerido) return true;
      const v = valores[c.key];
      return v !== null && v !== undefined && String(v).trim() !== '';
    })
  );

  async function guardar() {
    if (!puedeGuardar) return;
    guardando = true;
    try {
      if (edicion && registro) {
        await api.patch(`${endpoint}/${registro.id}`, valores);
        toast('Registro actualizado', 'ok');
      } else {
        await api.post(endpoint, valores);
        toast('Registro creado', 'ok');
      }
      onSaved();
      onClose();
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Error', 'error');
    } finally {
      guardando = false;
    }
  }
</script>

<button class="fixed inset-0 z-40 bg-black/40" onclick={onClose} aria-label="Cerrar"></button>

<div
  class="fixed left-1/2 top-1/2 z-50 max-h-[90vh] w-full max-w-md -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-card bg-surface shadow-elevated"
>
  <header class="flex items-center justify-between border-b border-line px-5 py-4">
    <h2 class="text-base font-semibold text-ink">{edicion ? `Editar ${titulo}` : `Nuevo ${titulo}`}</h2>
    <button onclick={onClose} class="rounded-control p-1 text-muted hover:bg-canvas" aria-label="Cerrar">
      <XIcon size={18} />
    </button>
  </header>

  <div class="space-y-4 p-5 text-sm">
    {#each campos as c (c.key)}
      {#if c.tipo === 'checkbox'}
        <label class="flex cursor-pointer items-center gap-2">
          <input type="checkbox" bind:checked={valores[c.key] as boolean} />
          <span class="text-ink">{c.label}</span>
        </label>
      {:else if c.tipo === 'textarea'}
        <div>
          <label for={c.key} class="font-medium text-ink">{c.label}</label>
          <textarea id={c.key} rows="2" bind:value={valores[c.key] as string}
            class="mt-1 w-full rounded-control border border-line px-3 py-2 focus:border-brand focus:outline-none"></textarea>
        </div>
      {:else if c.tipo === 'select'}
        <div>
          <label for={c.key} class="font-medium text-ink">{c.label}</label>
          <select id={c.key} bind:value={valores[c.key]}
            class="mt-1 w-full rounded-control border border-line px-3 py-2 focus:border-brand focus:outline-none">
            {#each c.opciones ?? [] as o (o.value)}<option value={o.value}>{o.label}</option>{/each}
          </select>
        </div>
      {:else}
        <div>
          <label for={c.key} class="font-medium text-ink">{c.label}</label>
          <input id={c.key} bind:value={valores[c.key] as string}
            class="mt-1 w-full rounded-control border border-line px-3 py-2 focus:border-brand focus:outline-none" />
        </div>
      {/if}
    {/each}
  </div>

  <footer class="flex items-center justify-end gap-2 border-t border-line px-5 py-3">
    <button onclick={onClose} class="rounded-control px-3 py-2 text-sm font-medium text-ink hover:bg-canvas">Cancelar</button>
    <button onclick={guardar} disabled={!puedeGuardar || guardando}
      class="rounded-control bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
      {guardando ? 'Guardando...' : edicion ? 'Guardar cambios' : 'Crear'}
    </button>
  </footer>
</div>
