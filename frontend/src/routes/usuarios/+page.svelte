<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/ui';
  import type { Rol, Sucursal, Usuario } from '$lib/types';
  import { fechaHora } from '$lib/utils/format';
  import PageHeader from '$lib/components/shared/PageHeader.svelte';
  import LoadingState from '$lib/components/shared/LoadingState.svelte';
  import ErrorState from '$lib/components/shared/ErrorState.svelte';
  import EmptyState from '$lib/components/shared/EmptyState.svelte';
  import UsuarioModal from '$lib/components/users/UsuarioModal.svelte';
  import PlusIcon from 'lucide-svelte/icons/plus';

  let usuarios = $state<Usuario[]>([]);
  let roles = $state<Rol[]>([]);
  let sucursales = $state<Sucursal[]>([]);
  let error = $state('');
  let cargando = $state(true);

  let modalAbierto = $state(false);
  let editando = $state<Usuario | null>(null);

  const rolNombre = $derived(new Map(roles.map((r) => [r.id, r.nombre])));

  // Solo se ofrecen las sucursales habilitadas. Si queda una sola (Distrimarcas),
  // deja de ser un dato que el encargado tenga que elegir o filtrar.
  const sucNombre = $derived(new Map(sucursales.map((s) => [s.id, s.nombre])));
  const sucursalesActivas = $derived(sucursales.filter((s) => s.activa));
  const sucursalUnica = $derived(sucursalesActivas.length === 1 ? sucursalesActivas[0] : null);

  // Filtro de roles: se muestran los roles que el sistema usa hoy (todos los
  // usuarios son Admin), mas el rol del usuario que se esta editando.
  const rolesAsignables = $derived.by(() => {
    const enUso = new Set(usuarios.map((u) => u.rol_id));
    if (editando) enUso.add(editando.rol_id);
    const lista = roles.filter((r) => enUso.has(r.id));
    return lista.length > 0 ? lista : roles;
  });

  async function cargar() {
    cargando = true;
    error = '';
    try {
      [usuarios, roles, sucursales] = await Promise.all([
        api.get<Usuario[]>('/api/v1/usuarios'),
        api.get<Rol[]>('/api/v1/roles'),
        api.get<Sucursal[]>('/api/v1/sucursales')
      ]);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error';
    } finally {
      cargando = false;
    }
  }

  function nuevo() {
    editando = null;
    modalAbierto = true;
  }

  function editar(u: Usuario) {
    editando = u;
    modalAbierto = true;
  }

  async function alternarActivo(u: Usuario) {
    try {
      await api.patch(`/api/v1/usuarios/${u.id}`, { activo: !u.activo });
      toast(u.activo ? 'Usuario desactivado' : 'Usuario activado', 'ok');
      await cargar();
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Error', 'error');
    }
  }

  async function eliminar(u: Usuario) {
    if (!confirm(`Eliminar al usuario "${u.nombre}"? Esta accion no se puede deshacer.`)) return;
    try {
      await api.del(`/api/v1/usuarios/${u.id}`);
      toast('Usuario eliminado', 'ok');
      await cargar();
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Error', 'error');
    }
  }

  $effect(() => {
    cargar();
  });
</script>

<PageHeader
  titulo="Usuarios y permisos"
  descripcion={sucursalUnica
    ? `Administra las cuentas de acceso y sus roles. Sucursal: ${sucursalUnica.nombre}.`
    : 'Administra las cuentas de acceso al sistema y sus roles.'}
>
  {#snippet acciones()}
    <button onclick={nuevo}
      class="inline-flex items-center gap-2 rounded-control bg-brand px-3 py-2 text-sm font-medium text-white hover:bg-brand-700">
      <PlusIcon size={15} /> Nuevo usuario
    </button>
  {/snippet}
</PageHeader>

{#if cargando}
  <LoadingState />
{:else if error}
  <ErrorState mensaje={error} onReintentar={cargar} />
{:else if usuarios.length === 0}
  <EmptyState titulo="Sin usuarios" descripcion="Crea el primer usuario del sistema." />
{:else}
  <div class="overflow-x-auto rounded-card border border-line bg-surface shadow-card">
    <table class="w-full min-w-[820px] text-sm">
      <thead>
        <tr class="border-b border-line text-left text-xs font-semibold uppercase tracking-wide text-muted">
          <th class="px-4 py-3">Nombre</th>
          <th class="px-4 py-3">Email</th>
          <th class="px-4 py-3">Rol</th>
          {#if !sucursalUnica}<th class="px-4 py-3">Sucursal</th>{/if}
          <th class="px-4 py-3">Estado</th>
          <th class="px-4 py-3">Ultimo acceso</th>
          <th class="px-4 py-3 text-right">Acciones</th>
        </tr>
      </thead>
      <tbody>
        {#each usuarios as u (u.id)}
          <tr class="border-b border-line last:border-0 hover:bg-canvas">
            <td class="px-4 py-3 font-medium text-ink">{u.nombre}</td>
            <td class="px-4 py-3 text-ink">{u.email}</td>
            <td class="px-4 py-3 text-ink">{rolNombre.get(u.rol_id) ?? '—'}</td>
            {#if !sucursalUnica}
              <td class="px-4 py-3 text-ink">
                {u.sucursal_id ? (sucNombre.get(u.sucursal_id) ?? '—') : '—'}
              </td>
            {/if}
            <td class="px-4 py-3">
              {#if u.activo}
                <span class="inline-flex items-center gap-1.5 rounded-full bg-estado-normal/10 px-2.5 py-0.5 text-xs font-medium text-estado-normal">
                  <span class="h-1.5 w-1.5 rounded-full bg-current"></span> Activo
                </span>
              {:else}
                <span class="inline-flex items-center gap-1.5 rounded-full bg-canvas px-2.5 py-0.5 text-xs font-medium text-muted">
                  <span class="h-1.5 w-1.5 rounded-full bg-current"></span> Inactivo
                </span>
              {/if}
            </td>
            <td class="px-4 py-3 text-ink">{fechaHora(u.ultimo_acceso)}</td>
            <td class="px-4 py-3">
              <div class="flex justify-end gap-2">
                <button onclick={() => alternarActivo(u)}
                  class="rounded-control border border-line px-2.5 py-1 text-xs font-medium text-ink hover:bg-canvas">
                  {u.activo ? 'Desactivar' : 'Activar'}
                </button>
                <button onclick={() => editar(u)}
                  class="rounded-control border border-line px-2.5 py-1 text-xs font-medium text-ink hover:bg-canvas">
                  Editar
                </button>
                <button onclick={() => eliminar(u)}
                  class="rounded-control border border-line px-2.5 py-1 text-xs font-medium text-estado-critica hover:bg-estado-critica/10">
                  Eliminar
                </button>
              </div>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

{#if modalAbierto}
  <UsuarioModal
    usuario={editando}
    roles={rolesAsignables}
    sucursales={sucursalesActivas}
    onClose={() => (modalAbierto = false)}
    onSaved={cargar}
  />
{/if}
