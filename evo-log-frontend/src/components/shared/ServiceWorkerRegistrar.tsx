'use client';

import { useEffect } from 'react';

/**
 * Enregistre le service worker (public/sw.js) pour le mode hors connexion.
 *
 * Seulement en production : en dev, le sw casserait le hot-reload de Next.
 * L'enregistrement echoue silencieusement si le navigateur ne le supporte
 * pas (le reste de l'app fonctionne, simplement sans cache offline).
 */
export default function ServiceWorkerRegistrar() {
  useEffect(() => {
    if (process.env.NODE_ENV !== 'production') return;
    if (typeof navigator === 'undefined' || !('serviceWorker' in navigator)) return;

    navigator.serviceWorker
      .register('/sw.js')
      .catch((err) => console.warn('[PWA] Service worker non enregistré :', err));
  }, []);

  return null;
}
