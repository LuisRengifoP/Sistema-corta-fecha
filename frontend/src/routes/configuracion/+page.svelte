<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/ui';
  import type { Bodega, Rol, Sucursal } from '$lib/types';
  import PageHeader from '$lib/components/shared/PageHeader.svelte';
  import LoadingState from '$lib/components/shared/LoadingState.svelte';
  import ErrorState from '$lib/components/shared/ErrorState.svelte';
  import EmptyState from '$lib/components/shared/EmptyState.svelte';
  import RegistroModal, { type Campo } from '$lib/components/config/RegistroModal.svelte';
  import PlusIcon from 'lucide-svelte/icons/plus';

  type Tab = 'sucursales' | 'bodegas' | 'roles';
  let tab = $state<Tab>('sucursales');

  let sucursales = $state<Sucursal[]>([]);
  let bodegas = $state<Bodega[]>([]);
  let roles = $state<Rol[]>([]);
  let error = $state('');
  let cargando = $state(true);

  const sucNombre = $derived(new Map(sucursales.map((s) => [s.id, s.nombre])));

  let modalAbierto = $state(false);
  let editando = $state<Record<string, unknown> | null>(null);

  async function cargar() {
    cargando = true;
    error = '';
    try {
      [sucursales, bodegas, roles] = await Promise.all([
        api.get<Sucursal[]>('/api/v1/sucursales'),
        api.get<Bodega[]>('/api/v1/bodegas'),
        api.get<Rol[]>('/api/v1/roles')
      ]);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error';
    } finally {
      cargando = false;
    }
  }

  const config = $derived({
    sucursales: {
      titulo: 'sucursal',
      endpoint: '/api/v1/sucursales',
      campos: [
        { key: 'codigo', label: 'Codigo', tipo: 'text', requerido: true },
        { key: 'nombre', label: 'Nombre', tipo: 'text', requerido: true },
        { key: 'direccion', label: 'Direccion', tipo: 'textarea' },
        { key: 'activa', label: 'Activa', tipo: 'checkbox' }
      ] as Campo[]
    },
    bodegas: {
      titulo: 'bodega',
      endpoint: '/api/v1/bodegas',
      campos: [
        {
          key: 'sucursal_id',
          label: 'Sucursal',
          tipo: 'select',
          requerido: true,
          opciones: sucursales.map((s) => ({ value: s.id, label: s.nombre }))
        },
        { key: 'codigo', label: 'Codigo', tipo: 'text', requerido: true },
        { key: 'nombre', label: 'Nombre', tipo: 'text', requerido: true },
        { key: 'activa', label: 'Activa', tipo: 'checkbox' }
      ] as Campo[]
    },
    roles: {
      titulo: 'rol',
      endpoint: '/api/v1/roles',
      campos: [
        { key: 'nombre', label: 'Nombre', tipo: 'text', requerido: true },
        { key: 'descripcion', label: 'Descripcion', tipo: 'textarea' }
      ] as Campo[]
    }
  });

  const actual = $derived(config[tab]);

  function nuevo() {
    editando = null;
    modalAbierto = true;
  }

  function editar(reg: Record<string, unknown>) {
    editando = reg;
    modalAbierto = true;
  }

  async function eliminar(endpoint: string, id: number, etiqueta: string) {
    if (!confirm(`Eliminar "${etiqueta}"? Esta accion no se puede deshacer.`)) return;
    try {
      await api.del(`${endpoint}/${id}`);
      toast('Registro eliminado', 'ok');
      await cargar();
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Error', 'error');
    }
  }

  const TABS: { id: Tab; label: string }[] = [
    { id: 'sucursales', label: 'Sucursales' },
    { id: 'bodegas', label: 'Bodegas' },
    { id: 'roles', label: 'Roles' }
  ];

  $effect(() => {
    cargar();
  });
</script>

<PageHeader titulo="Configuracion" descripcion="Datos maestros: sucursales, bodegas y roles del sistema.">
  {#snippet acciones()}
    <button onclick={nuevo}
      class="inline-flex items-center gap-2 rounded-control bg-brand px-3 py-2 text-sm font-medium text-white hover:bg-brand-700">
      <PlusIcon size={15} /> Nuevo {actual.titulo}
    </button>
  {/snippet}
</PageHeader>

<div class="mb-4 flex gap-1 border-b border-line">
  {#each TABS as t (t.id)}
    <button onclick={() => (tab = t.id)}
      class="border-b-2 px-4 py-2 text-sm font-medium transition {tab === t.id
        ? 'border-brand text-brand'
        : 'border-transparent text-muted hover:text-ink'}">
      {t.label}
    </button>
  {/each}
</div>

{#if cargando}
  <LoadingState />
{:else if error}
  <ErrorState mensaje={error} onReintentar={cargar} />
{:else}
  <div class="overflow-x-auto rounded-card border border-line bg-surface shadow-card">
    {#if tab === 'sucursales'}
      {#if sucursales.length === 0}
        <EmptyState titulo="Sin sucursales" descripcion="Agrega la primera sucursal." />
      {:else}
        <table class="w-full min-w-[640px] text-sm">
          <thead>
            <tr class="border-b border-line text-left text-xs font-semibold uppercase tracking-wide text-muted">
              <th class="px-4 py-3">Codigo</th>
              <th class="px-4 py-3">Nombre</th>
              <th class="px-4 py-3">Direccion</th>
              <th class="px-4 py-3">Estado</th>
              <th class="px-4 py-3 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {#each sucursales as s (s.id)}
              <tr class="border-b border-line last:border-0 hover:bg-canvas">
                <td class="px-4 py-3 font-medium text-ink">{s.codigo}</td>
                <td class="px-4 py-3 text-ink">{s.nombre}</td>
                <td class="px-4 py-3 text-muted">{s.direccion ?? '—'}</td>
                <td class="px-4 py-3 text-ink">{s.activa ? 'Activa' : 'Inactiva'}</td>
                <td class="px-4 py-3">
                  <div class="flex justify-end gap-2">
                    <button onclick={() => editar(s as unknown as Record<string, unknown>)}
                      class="rounded-control border border-line px-2.5 py-1 text-xs font-medium text-ink hover:bg-canvas">Editar</button>
                    <button onclick={() => eliminar('/api/v1/sucursales', s.id, s.nombre)}
                      class="rounded-control border border-line px-2.5 py-1 text-xs font-medium text-estado-critica hover:bg-estado-critica/10">Eliminar</button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    {:else if tab === 'bodegas'}
      {#if bodegas.length === 0}
        <EmptyState titulo="Sin bodegas" descripcion="Agrega la primera bodega." />
      {:else}
        <table class="w-full min-w-[640px] text-sm">
          <thead>
            <tr class="border-b border-line text-left text-xs font-semibold uppercase tracking-wide text-muted">
              <th class="px-4 py-3">Codigo</th>
              <th class="px-4 py-3">Nombre</th>
              <th class="px-4 py-3">Sucursal</th>
              <th class="px-4 py-3">Estado</th>
              <th class="px-4 py-3 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {#each bodegas as b (b.id)}
              <tr class="border-b border-line last:border-0 hover:bg-canvas">
                <td class="px-4 py-3 font-medium text-ink">{b.codigo}</td>
                <td class="px-4 py-3 text-ink">{b.nombre}</td>
                <td class="px-4 py-3 text-ink">{sucNombre.get(b.sucursal_id) ?? '—'}</td>
                <td class="px-4 py-3 text-ink">{b.activa ? 'Activa' : 'Inactiva'}</td>
                <td class="px-4 py-3">
                  <div class="flex justify-end gap-2">
                    <button onclick={() => editar(b as unknown as Record<string, unknown>)}
                      class="rounded-control border border-line px-2.5 py-1 text-xs font-medium text-ink hover:bg-canvas">Editar</button>
                    <button onclick={() => eliminar('/api/v1/bodegas', b.id, b.nombre)}
                      class="rounded-control border border-line px-2.5 py-1 text-xs font-medium text-estado-critica hover:bg-estado-critica/10">Eliminar</button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    {:else}
      {#if roles.length === 0}
        <EmptyState titulo="Sin roles" descripcion="Agrega el primer rol." />
      {:else}
        <table class="w-full min-w-[520px] text-sm">
          <thead>
            <tr class="border-b border-line text-left text-xs font-semibold uppercase tracking-wide text-muted">
              <th class="px-4 py-3">Nombre</th>
              <th class="px-4 py-3">Descripcion</th>
              <th class="px-4 py-3 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {#each roles as r (r.id)}
              <tr class="border-b border-line last:border-0 hover:bg-canvas">
                <td class="px-4 py-3 font-medium text-ink">{r.nombre}</td>
                <td class="px-4 py-3 text-muted">{r.descripcion ?? '—'}</td>
                <td class="px-4 py-3">
                  <div class="flex justify-end gap-2">
                    <button onclick={() => editar(r as unknown as Record<string, unknown>)}
                      class="rounded-control border border-line px-2.5 py-1 text-xs font-medium text-ink hover:bg-canvas">Editar</button>
                    <button onclick={() => eliminar('/api/v1/roles', r.id, r.nombre)}
                      class="rounded-control border border-line px-2.5 py-1 text-xs font-medium text-estado-critica hover:bg-estado-critica/10">Eliminar</button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    {/if}
  </div>
{/if}

{#if modalAbierto}
  <RegistroModal
    titulo={actual.titulo}
    endpoint={actual.endpoint}
    campos={actual.campos}
    registro={editando}
    onClose={() => (modalAbierto = false)}
    onSaved={cargar}
  />
{/if}
