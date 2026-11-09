// See https://svelte.dev/docs/kit/types#app
/// <reference types="vite-plugin-pwa/client" />

declare global {
  namespace App {
    // interface Error {}
    // interface Locals {}
    // interface PageData {}
    // interface Platform {}
  }

  interface WindowEventMap {
    /** Chrome/Edge: permite diferir el dialogo de instalacion de la PWA. */
    beforeinstallprompt: BeforeInstallPromptEvent;
  }

  interface BeforeInstallPromptEvent extends Event {
    readonly platforms: string[];
    prompt(): Promise<void>;
    readonly userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>;
  }
}

export {};
