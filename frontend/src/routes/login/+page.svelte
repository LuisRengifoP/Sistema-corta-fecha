<script lang="ts">
  import { goto } from '$app/navigation';
  import { login } from '$lib/services/api';
  import EyeIcon from 'lucide-svelte/icons/eye';
  import EyeOffIcon from 'lucide-svelte/icons/eye-off';

  let email = $state('admin@corta-fecha.com');
  let password = $state('');
  let error = $state('');
  let cargando = $state(false);
  let verPassword = $state(false);

  async function onSubmit(e: Event) {
    e.preventDefault();
    error = '';
    cargando = true;
    try {
      await login(email, password);
      goto('/');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error';
    } finally {
      cargando = false;
    }
  }
</script>

<div class="flex min-h-screen items-center justify-center bg-canvas p-4">
  <form
    onsubmit={onSubmit}
    class="w-full max-w-sm space-y-5 rounded-card border border-line bg-surface p-8 shadow-card"
  >
    <div class="text-center">
      <img
        src="/logo.png"
        alt="Corta Fecha"
        width="96"
        height="96"
        class="mx-auto mb-3 h-24 w-24 rounded-card"
      />
      <h1 class="text-xl font-bold text-ink">Sistema Corta Fecha</h1>
      <p class="text-sm text-muted">Inicia sesion para continuar</p>
    </div>

    {#if error}
      <div class="rounded-control bg-estado-critica/5 px-3 py-2 text-sm text-estado-critica">
        {error}
      </div>
    {/if}

    <div class="space-y-1.5">
      <label for="email" class="text-sm font-medium text-ink">Email</label>
      <input
        id="email"
        type="email"
        bind:value={email}
        required
        class="w-full rounded-control border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-brand focus:outline-none"
      />
    </div>

    <div class="space-y-1.5">
      <label for="password" class="text-sm font-medium text-ink">Contrasena</label>
      <div class="relative">
        <input
          id="password"
          type={verPassword ? 'text' : 'password'}
          bind:value={password}
          required
          autocomplete="current-password"
          class="w-full rounded-control border border-line bg-surface px-3 py-2 pr-10 text-sm text-ink focus:border-brand focus:outline-none"
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

    <button
      type="submit"
      disabled={cargando}
      class="w-full rounded-control bg-brand px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:opacity-50"
    >
      {cargando ? 'Entrando...' : 'Entrar'}
    </button>
  </form>
</div>
