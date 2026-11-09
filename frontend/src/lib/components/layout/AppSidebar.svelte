<script lang="ts">
  import { page } from '$app/stores';
  import { sidebarCollapsed, toggleSidebar } from '$lib/stores/ui';
  import LayoutDashboard from 'lucide-svelte/icons/layout-dashboard';
  import Package from 'lucide-svelte/icons/package';
  import CalendarClock from 'lucide-svelte/icons/calendar-clock';
  import ClipboardCheck from 'lucide-svelte/icons/clipboard-check';
  import PackageX from 'lucide-svelte/icons/package-x';
  import BellRing from 'lucide-svelte/icons/bell-ring';
  import FileText from 'lucide-svelte/icons/file-text';
  import History from 'lucide-svelte/icons/history';
  import Users from 'lucide-svelte/icons/users';
  import Settings from 'lucide-svelte/icons/settings';
  import PanelLeftClose from 'lucide-svelte/icons/panel-left-close';
  import PanelLeftOpen from 'lucide-svelte/icons/panel-left-open';
  import type { ComponentType } from 'svelte';

  type Item = { label: string; href: string; icon: ComponentType; disponible: boolean };
  type Grupo = { titulo: string; items: Item[] };

  const grupos: Grupo[] = [
    {
      titulo: 'General',
      items: [{ label: 'Dashboard', href: '/', icon: LayoutDashboard, disponible: true }]
    },
    {
      titulo: 'Inventario',
      items: [
        { label: 'Productos', href: '/inventario', icon: Package, disponible: false },
        { label: 'Lotes y vencimientos', href: '/lotes', icon: CalendarClock, disponible: true }
      ]
    },
    {
      titulo: 'Operacion',
      items: [
        { label: 'Corta fecha', href: '/corta-fecha', icon: CalendarClock, disponible: true },
        { label: 'Inspecciones', href: '/inspecciones', icon: ClipboardCheck, disponible: true },
        { label: 'Productos averiados', href: '/averiados', icon: PackageX, disponible: true }
      ]
    },
    {
      titulo: 'Seguimiento',
      items: [{ label: 'Alertas y tareas', href: '/alertas', icon: BellRing, disponible: true }]
    },
    {
      titulo: 'Informacion',
      items: [
        { label: 'Reportes', href: '/reportes', icon: FileText, disponible: true },
        { label: 'Historial', href: '/historial', icon: History, disponible: true }
      ]
    },
    {
      titulo: 'Administracion',
      items: [
        { label: 'Usuarios y permisos', href: '/usuarios', icon: Users, disponible: true },
        { label: 'Configuracion', href: '/configuracion', icon: Settings, disponible: true }
      ]
    }
  ];

  let colapsado = $derived($sidebarCollapsed);
  let ruta = $derived($page.url.pathname);

  function activo(href: string): boolean {
    return href === '/' ? ruta === '/' : ruta.startsWith(href);
  }
</script>

<aside
  class="flex shrink-0 flex-col bg-navy text-white transition-all duration-200 {colapsado
    ? 'w-[72px]'
    : 'w-[248px]'}"
>
  <div class="flex h-16 items-center gap-2 px-4">
    <img
      src="/icons/marca-192.png"
      alt="Corta Fecha"
      width="32"
      height="32"
      class="h-8 w-8 shrink-0 rounded-control"
    />
    {#if !colapsado}
      <div class="min-w-0">
        <p class="truncate text-sm font-semibold">Corta Fecha</p>
        <p class="truncate text-xs text-white/50">Control de inventario</p>
      </div>
    {/if}
  </div>

  <nav class="flex-1 overflow-y-auto px-2 py-2">
    {#each grupos as grupo (grupo.titulo)}
      {#if !colapsado}
        <p class="px-3 pb-1 pt-3 text-[11px] font-semibold uppercase tracking-wider text-white/40">
          {grupo.titulo}
        </p>
      {/if}
      {#each grupo.items as item (item.href)}
        <a
          href={item.disponible ? item.href : undefined}
          aria-disabled={!item.disponible}
          title={item.disponible ? item.label : `${item.label} (proximamente)`}
          class="mb-0.5 flex items-center gap-3 rounded-control px-3 py-2 text-sm transition
            {activo(item.href) && item.disponible
            ? 'bg-brand text-white'
            : 'text-white/70 hover:bg-white/10'}
            {!item.disponible ? 'cursor-not-allowed opacity-40 hover:bg-transparent' : ''}"
        >
          <item.icon size={18} class="shrink-0" />
          {#if !colapsado}
            <span class="truncate">{item.label}</span>
          {/if}
        </a>
      {/each}
    {/each}
  </nav>

  <button
    onclick={toggleSidebar}
    class="flex items-center gap-3 border-t border-white/10 px-4 py-3 text-sm text-white/60 hover:text-white"
  >
    {#if colapsado}
      <PanelLeftOpen size={18} />
    {:else}
      <PanelLeftClose size={18} />
      <span>Contraer</span>
    {/if}
  </button>
</aside>
