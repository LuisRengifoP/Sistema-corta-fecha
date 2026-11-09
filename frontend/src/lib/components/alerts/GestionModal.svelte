<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/ui';
  import type { Usuario } from '$lib/types';
  import XIcon from 'lucide-svelte/icons/x';

  let {
    url,
    titulo,
    subtitulo,
    onClose,
    onSaved
  }: {
    url: string;
    titulo: string;
    subtitulo: string;
    onClose: () => void;
    onSaved: () => void;
  } = $props();

  let usuarios = $state<Usuario[]>([]);
  let responsableId = $state<number | null>(null);
  let descripcion = $state('');
  let cerrar = $state(false);
  let resultado = $state('');
  let guardando = $state(false);

  const puedeGuardar = $derived(
    responsableId !== null && descripcion.trim() !== '' && (!cerrar || resultado.trim() !== '')
  );

  $effect(() => {
    api.get<Usuario[]>('/api/v1/usuarios').then((u) => (usuarios = u)).catch(() => {});
  });

  async function guardar() {
    if (!puedeGuardar || responsableId === null) return;
    guardando = true;
    try {
      await api.post(url, {
        responsable_id: responsableId,
        descripcion,
        cerrar,
        resultado: cerrar ? resultado : null
      });
      toast(cerrar ? 'Gestion cerrada' : 'Seguimiento registrado', 'ok');
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

<div class="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-card bg-surface shadow-elevated">
  <header class="flex items-center justify-between border-b border-line px-5 py-4">
    <h2 class="text-base font-semibold text-ink">{titulo}</h2>
    <button onclick={onClose} class="rounded-control p-1 text-muted hover:bg-canvas" aria-label="Cerrar">
      <XIcon size={18} />
    </button>
  </header>

  <div class="space-y-4 p-5 text-sm">
    <div class="rounded-control border border-line p-3">
      <p class="text-muted">{subtitulo}</p>
    </div>

    <div>
      <label for="resp" class="font-medium text-ink">Responsable</label>
      <select id="resp" bind:value={responsableId}
        class="mt-1 w-full rounded-control border border-line px-3 py-2 focus:border-brand focus:outline-none">
        <option value={null} disabled selected>Selecciona un responsable</option>
        {#each usuarios as u (u.id)}<option value={u.id}>{u.nombre}</option>{/each}
      </select>
    </div>

    <div>
      <label for="desc" class="font-medium text-ink">Accion / seguimiento</label>
      <textarea id="desc" rows="3" bind:value={descripcion}
        placeholder="Describe la accion a realizar o el seguimiento"
        class="mt-1 w-full rounded-control border border-line px-3 py-2 focus:border-brand focus:outline-none"></textarea>
    </div>

    <label class="flex items-center gap-2">
      <input type="checkbox" bind:checked={cerrar} />
      <span class="text-ink">Marcar gestion como completada</span>
    </label>

    {#if cerrar}
      <div>
        <label for="res" class="font-medium text-ink">Resultado (obligatorio)</label>
        <textarea id="res" rows="2" bind:value={resultado}
          placeholder="Resultado de la gestion"
          class="mt-1 w-full rounded-control border border-line px-3 py-2 focus:border-brand focus:outline-none"></textarea>
      </div>
    {/if}
  </div>

  <footer class="flex items-center justify-end gap-2 border-t border-line px-5 py-3">
    <button onclick={onClose} class="rounded-control px-3 py-2 text-sm font-medium text-ink hover:bg-canvas">
      Cancelar
    </button>
    <button onclick={guardar} disabled={!puedeGuardar || guardando}
      class="rounded-control bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
      {guardando ? 'Guardando...' : cerrar ? 'Cerrar gestion' : 'Registrar'}
    </button>
  </footer>
</div>
