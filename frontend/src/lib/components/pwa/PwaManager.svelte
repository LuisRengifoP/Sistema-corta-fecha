<script lang="ts">
  /**
   * Registro del Service Worker (Workbox) y avisos de la PWA:
   * - instalar la app en el dispositivo (WebAPK en Android, acceso directo en escritorio);
   * - avisar cuando hay una version nueva, sin recargar por su cuenta;
   * - mostrar que la app quedo lista para funcionar sin conexion;
   * - indicar cuando el dispositivo pierde la conexion.
   */
  import { onMount } from 'svelte';
  import DownloadIcon from 'lucide-svelte/icons/download';
  import RefreshIcon from 'lucide-svelte/icons/refresh-cw';
  import WifiOffIcon from 'lucide-svelte/icons/wifi-off';
  import XIcon from 'lucide-svelte/icons/x';

  let necesitaActualizar = $state(false);
  let listoSinConexion = $state(false);
  let sinConexion = $state(false);
  let instalable = $state<BeforeInstallPromptEvent | null>(null);

  let actualizar: ((recargar?: boolean) => Promise<void>) | null = null;

  onMount(() => {
    sinConexion = !navigator.onLine;
    const online = () => (sinConexion = false);
    const offline = () => (sinConexion = true);
    window.addEventListener('online', online);
    window.addEventListener('offline', offline);

    const alInstalar = (e: BeforeInstallPromptEvent) => {
      // Se difiere el dialogo del navegador para ofrecerlo desde la propia app.
      e.preventDefault();
      instalable = e;
    };
    const instalada = () => (instalable = null);
    window.addEventListener('beforeinstallprompt', alInstalar);
    window.addEventListener('appinstalled', instalada);

    // Import dinamico: el modulo virtual solo existe en el build.
    import('virtual:pwa-register')
      .then(({ registerSW }) => {
        actualizar = registerSW({
          immediate: true,
          onNeedRefresh: () => (necesitaActualizar = true),
          onOfflineReady: () => {
            listoSinConexion = true;
            setTimeout(() => (listoSinConexion = false), 6000);
          }
        });
      })
      .catch(() => {
        /* sin Service Worker (dev o navegador sin soporte) */
      });

    return () => {
      window.removeEventListener('online', online);
      window.removeEventListener('offline', offline);
      window.removeEventListener('beforeinstallprompt', alInstalar);
      window.removeEventListener('appinstalled', instalada);
    };
  });

  async function instalar() {
    const evento = instalable;
    if (!evento) return;
    instalable = null;
    await evento.prompt();
    await evento.userChoice;
  }

  async function aplicarActualizacion() {
    necesitaActualizar = false;
    await actualizar?.(true);
  }
</script>

<div class="pointer-events-none fixed bottom-4 left-1/2 z-[60] flex w-full max-w-sm -translate-x-1/2 flex-col gap-2 px-4">
  {#if sinConexion}
    <div
      class="pointer-events-auto flex items-center gap-2 rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink shadow-elevated"
      role="status"
    >
      <WifiOffIcon size={16} class="text-estado-prioritaria" />
      <span>Sin conexion. Se muestran los ultimos datos guardados.</span>
    </div>
  {/if}

  {#if listoSinConexion}
    <div
      class="pointer-events-auto flex items-center gap-2 rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink shadow-elevated"
      role="status"
    >
      <span>App lista para usarse sin conexion.</span>
    </div>
  {/if}

  {#if necesitaActualizar}
    <div
      class="pointer-events-auto flex items-center gap-2 rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink shadow-elevated"
      role="alert"
    >
      <RefreshIcon size={16} class="text-brand" />
      <span class="flex-1">Hay una version nueva.</span>
      <button
        onclick={aplicarActualizacion}
        class="rounded-control bg-brand px-2.5 py-1 text-xs font-medium text-white hover:bg-brand-700"
      >
        Actualizar
      </button>
      <button
        onclick={() => (necesitaActualizar = false)}
        class="rounded-control p-1 text-muted hover:bg-canvas"
        aria-label="Cerrar aviso"
      >
        <XIcon size={14} />
      </button>
    </div>
  {/if}

  {#if instalable}
    <div
      class="pointer-events-auto flex items-center gap-2 rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink shadow-elevated"
    >
      <DownloadIcon size={16} class="text-brand" />
      <span class="flex-1">Instala Corta Fecha en este dispositivo.</span>
      <button
        onclick={instalar}
        class="rounded-control bg-brand px-2.5 py-1 text-xs font-medium text-white hover:bg-brand-700"
      >
        Instalar
      </button>
      <button
        onclick={() => (instalable = null)}
        class="rounded-control p-1 text-muted hover:bg-canvas"
        aria-label="Cerrar aviso"
      >
        <XIcon size={14} />
      </button>
    </div>
  {/if}
</div>
