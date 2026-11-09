<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/ui';
  import type { Rol, Sucursal, Usuario } from '$lib/types';
  import XIcon from 'lucide-svelte/icons/x';
  import EyeIcon from 'lucide-svelte/icons/eye';
  import EyeOffIcon from 'lucide-svelte/icons/eye-off';

  let {
    usuario = null,
    roles,
    sucursales,
    onClose,
    onSaved
  }: {
    usuario?: Usuario | null;
    /** Solo los roles que el sistema usa hoy (ver filtro en la pagina de usuarios). */
    roles: Rol[];
    sucursales: Sucursal[];
    onClose: () => void;
    onSaved: () => void;
  } = $props();

  const edicion = usuario !== null;

  // Con una sola sucursal habilitada no hay nada que elegir: se asigna sola.
  const sucursalUnica = $derived(sucursales.length === 1 ? sucursales[0] : null);

  let nombre = $state(usuario?.nombre ?? '');
  let email = $state(usuario?.email ?? '');
  let password = $state('');
  let verPassword = $state(false);
  let rolId = $state<number | null>(usuario?.rol_id ?? roles[0]?.id ?? null);
  let sucursalId = $state<number | null>(
    usuario?.sucursal_id ?? (sucursales.length === 1 ? sucursales[0].id : null)
  );
  let activo = $state(usuario?.activo ?? true);
  let guardando = $state(false);

  // Si solo hay una sucursal, el usuario queda siempre asignado a ella.
  $effect(() => {
    if (sucursalUnica !== null) sucursalId = sucursalUnica.id;
  });

  const puedeGuardar = $derived(
    nombre.trim() !== '' &&
      email.trim() !== '' &&
      rolId !== null &&
      (edicion || password.length >= 6)
  );

  async function guardar() {
    if (!puedeGuardar) return;
    guardando = true;
    try {
      if (edicion && usuario) {
        const body: Record<string, unknown> = {
          nombre: nombre.trim(),
          rol_id: rolId,
          sucursal_id: sucursalId,
          activo
        };
        if (password) body.password = password;
        await api.patch(`/api/v1/usuarios/${usuario.id}`, body);
        toast('Usuario actualizado', 'ok');
      } else {
        await api.post('/api/v1/usuarios', {
          nombre: nombre.trim(),
          email: email.trim(),
          password,
          rol_id: rolId,
          sucursal_id: sucursalId,
          activo
        });
        toast('Usuario creado', 'ok');
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
    <h2 class="text-base font-semibold text-ink">
      {edicion ? 'Editar usuario' : 'Nuevo usuario'}
    </h2>
    <button onclick={onClose} class="rounded-control p-1 text-muted hover:bg-canvas" aria-label="Cerrar">
      <XIcon size={18} />
    </button>
  </header>

  <div class="space-y-4 p-5 text-sm">
    <div>
      <label for="nombre" class="font-medium text-ink">Nombre</label>
      <input id="nombre" bind:value={nombre}
        class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none" />
    </div>

    <div>
      <label for="email" class="font-medium text-ink">Email</label>
      <input id="email" type="email" bind:value={email} disabled={edicion}
        class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none disabled:bg-canvas disabled:text-muted" />
      {#if edicion}
        <p class="mt-1 text-xs text-muted">El email no se puede cambiar.</p>
      {/if}
    </div>

    <div>
      <label for="password" class="font-medium text-ink">
        {edicion ? 'Nueva contrasena (opcional)' : 'Contrasena'}
      </label>
      <div class="relative mt-1">
        <input
          id="password"
          type={verPassword ? 'text' : 'password'}
          bind:value={password}
          autocomplete="new-password"
          placeholder={edicion ? 'Dejar vacio para mantener' : 'Minimo 6 caracteres'}
          class="w-full rounded-control border border-line bg-surface px-3 py-2 pr-10 text-ink focus:border-brand focus:outline-none"
        />
        <button
          type="button"
          onclick={() => (verPassword = !verPassword)}
          class="absolute inset-y-0 right-0 flex items-center px-3 text-muted hover:text-ink"
          aria-label={verPassword ? 'Ocultar contrasena' : 'Mostrar contrasena'}
          title={verPassword ? 'Ocultar contrasena' : 'Mostrar contrasena'}
        >
          {#if verPassword}<EyeOffIcon size={16} />{:else}<EyeIcon size={16} />{/if}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label for="rol" class="font-medium text-ink">Rol</label>
        <select id="rol" bind:value={rolId}
          class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none">
          {#each roles as r (r.id)}<option value={r.id}>{r.nombre}</option>{/each}
        </select>
      </div>
      <div>
        <span class="font-medium text-ink">Sucursal</span>
        {#if sucursalUnica}
          <p
            class="mt-1 w-full rounded-control border border-line bg-canvas px-3 py-2 text-ink"
            title="Unica sucursal habilitada"
          >
            {sucursalUnica.nombre}
          </p>
        {:else}
          <select bind:value={sucursalId} aria-label="Sucursal"
            class="mt-1 w-full rounded-control border border-line bg-surface px-3 py-2 text-ink focus:border-brand focus:outline-none">
            <option value={null}>Sin asignar</option>
            {#each sucursales as s (s.id)}<option value={s.id}>{s.nombre}</option>{/each}
          </select>
        {/if}
      </div>
    </div>

    <label class="flex cursor-pointer items-center gap-2">
      <input type="checkbox" bind:checked={activo} />
      <span class="text-ink">Usuario activo</span>
    </label>
  </div>

  <footer class="flex items-center justify-end gap-2 border-t border-line px-5 py-3">
    <button onclick={onClose} class="rounded-control px-3 py-2 text-sm font-medium text-ink hover:bg-canvas">Cancelar</button>
    <button onclick={guardar} disabled={!puedeGuardar || guardando}
      class="rounded-control bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
      {guardando ? 'Guardando...' : edicion ? 'Guardar cambios' : 'Crear usuario'}
    </button>
  </footer>
</div>
