import { sveltekit } from '@sveltejs/kit/vite';
import { SvelteKitPWA } from '@vite-pwa/sveltekit';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  // Origen del backend: decide que peticiones cachea el Service Worker.
  // Se lee igual que en el cliente (ver src/lib/services/api.ts), tomando
  // el valor del .env del frontend o del entorno del proceso.
  const env = loadEnv(mode, process.cwd(), 'VITE_');
  const API_URL = env.VITE_API_URL ?? 'http://localhost:8000';

  return {
    plugins: [
      sveltekit(),
      SvelteKitPWA({
        // Workbox genera el Service Worker a partir de esta configuracion.
        strategies: 'generateSW',
        // 'prompt': la app avisa y el usuario decide cuando actualizar, para no
        // recargar una pantalla a medio llenar durante el recorrido de pasillos.
        registerType: 'prompt',
        injectRegister: null,
        manifest: {
          id: '/',
          name: 'Sistema Corta Fecha',
          short_name: 'Corta Fecha',
          description:
            'Control de productos proximos a vencer y averiados: registro, inspecciones y alertas.',
          lang: 'es',
          dir: 'ltr',
          start_url: '/',
          scope: '/',
          display: 'standalone',
          orientation: 'portrait-primary',
          background_color: '#f8fafc',
          theme_color: '#2563eb',
          categories: ['business', 'productivity'],
          icons: [
            { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
            { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
            {
              src: '/icons/maskable-512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'maskable'
            }
          ],
          shortcuts: [
            { name: 'Corta fecha', short_name: 'Corta fecha', url: '/corta-fecha' },
            { name: 'Inspecciones', short_name: 'Inspecciones', url: '/inspecciones' },
            { name: 'Alertas', short_name: 'Alertas', url: '/alertas' }
          ]
        },
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg,webp,woff,woff2}'],
          // Sin conexion y sin la pagina en cache se muestra /offline.html.
          navigateFallback: '/offline.html',
          navigateFallbackDenylist: [/^\/api\//, /^\/auth\//],
          cleanupOutdatedCaches: true,
          clientsClaim: true,
          runtimeCaching: [
            {
              // Navegaciones: red primero para no mostrar pantallas viejas,
              // con la copia en cache como respaldo si la red no responde.
              urlPattern: ({ request }) => request.mode === 'navigate',
              handler: 'NetworkFirst',
              options: {
                cacheName: 'cf-paginas',
                networkTimeoutSeconds: 3,
                expiration: { maxEntries: 40, maxAgeSeconds: 60 * 60 * 24 * 30 }
              }
            },
            {
              // Lecturas de la API: red primero y copia local para poder
              // consultar los ultimos datos sin conexion. Solo GET.
              // Esta cache se borra al cerrar sesion (ver src/lib/stores/auth.ts).
              urlPattern: ({ url, request }) =>
                request.method === 'GET' &&
                url.origin === new URL(API_URL).origin &&
                (url.pathname.startsWith('/api/v1/') || url.pathname === '/auth/me'),
              handler: 'NetworkFirst',
              method: 'GET',
              options: {
                cacheName: 'cf-api',
                networkTimeoutSeconds: 5,
                expiration: { maxEntries: 120, maxAgeSeconds: 60 * 60 * 24 },
                cacheableResponse: { statuses: [200] }
              }
            },
            {
              urlPattern: ({ url }) => url.origin === 'https://fonts.googleapis.com',
              handler: 'StaleWhileRevalidate',
              options: { cacheName: 'cf-google-fonts-css' }
            },
            {
              urlPattern: ({ url }) => url.origin === 'https://fonts.gstatic.com',
              handler: 'CacheFirst',
              options: {
                cacheName: 'cf-google-fonts',
                expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 * 365 },
                cacheableResponse: { statuses: [0, 200] }
              }
            }
          ]
        },
        devOptions: {
          // El Service Worker queda desactivado en `vite dev` para no servir
          // codigo viejo mientras se desarrolla.
          enabled: false,
          type: 'module',
          navigateFallback: '/'
        }
      })
    ],
    server: {
      port: 5173
    }
  };
});
