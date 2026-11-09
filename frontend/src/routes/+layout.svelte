<script lang="ts">
  import '../app.css';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { token } from '$lib/stores/auth';
  import AppSidebar from '$lib/components/layout/AppSidebar.svelte';
  import AppHeader from '$lib/components/layout/AppHeader.svelte';
  import Toaster from '$lib/components/shared/Toaster.svelte';

  let { children } = $props();

  let enLogin = $derived($page.url.pathname === '/login');

  // Guard: sin token y fuera de /login -> /login. Con token en /login -> /.
  $effect(() => {
    if ($token === null && !enLogin) goto('/login');
    if ($token !== null && enLogin) goto('/');
  });
</script>

{#if enLogin}
  {@render children()}
{:else}
  <div class="flex h-screen overflow-hidden">
    <AppSidebar />
    <div class="flex min-w-0 flex-1 flex-col">
      <AppHeader />
      <main class="flex-1 overflow-y-auto p-6">
        <div class="mx-auto max-w-6xl">
          {@render children()}
        </div>
      </main>
    </div>
  </div>
{/if}

<Toaster />
