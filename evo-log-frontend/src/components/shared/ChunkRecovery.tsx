'use client';

import { useEffect } from 'react';

/**
 * Rétection automatique d'une build périmée (ChunkLoadError).
 *
 * Quand Vercel redéploie, les anciens fichiers `/_next/static/.../page-<hash>.js`
 * cessent d'exister. Un onglet resté ouvert sur la build précédente, ou un
 * service worker qui a gardé l'ancien HTML en mémoire, va alors tenter de charger
 * un chunk disparu -> `ChunkLoadError` -> erreur React #423 (Suspense), et la
 * page (ex. /login) ne s'affiche plus DU TOUT.
 *
 * Ce composant écoute les erreurs de chargement de chunk et provoque UN seul
 * rechargement de page, qui retélécharge le HTML courant et ses hashes à jour.
 * Un garde-fou temporel (sessionStorage) evite toute boucle de reload si le
 * problème persiste (on laisse alors l'utilisateur voir l'erreur plutôt que
 * de recharger indéfiniment).
 */
const KEY = 'evo_chunk_recovery_ts';
const COOLDOWN_MS = 60_000;

function looksLikeChunkFailure(message: string, name?: string): boolean {
  return (
    name === 'ChunkLoadError' ||
    /Loading (CSS )?chunk|dynamically imported module|Importing a module script failed|error loading dynamically|Failed to load (module|script|chunk)/i.test(
      message || '',
    )
  );
}

export default function ChunkRecovery() {
  useEffect(() => {
    let alreadyHandling = false;

    const reloadOnce = () => {
      if (alreadyHandling) return;
      const last = Number(sessionStorage.getItem(KEY) || 0);
      if (Date.now() - last < COOLDOWN_MS) {
        // Un reload vient deja d'etre tente : on ne relance pas en boucle.
        return;
      }
      alreadyHandling = true;
      sessionStorage.setItem(KEY, String(Date.now()));
      window.location.reload();
    };

    // Phase capture : capte les erreurs de ressources <script>/<link> (chunk 404).
    const onError = (event: ErrorEvent) => {
      const target = event?.target as unknown as { tagName?: string } | null;
      if (target && (target.tagName === 'SCRIPT' || target.tagName === 'LINK')) {
        reloadOnce();
        return;
      }
      if (looksLikeChunkFailure(event?.message || '', event?.error?.name)) reloadOnce();
    };

    // Les echecs d'import dynamique (App Router / webpack) remontent en promesse
    // rejetee non geree.
    const onRejection = (event: PromiseRejectionEvent) => {
      const reason = event?.reason as { message?: string; name?: string } | undefined;
      if (looksLikeChunkFailure(reason?.message || String(reason || ''), reason?.name)) {
        reloadOnce();
      }
    };

    window.addEventListener('error', onError, true);
    window.addEventListener('unhandledrejection', onRejection);
    return () => {
      window.removeEventListener('error', onError, true);
      window.removeEventListener('unhandledrejection', onRejection);
    };
  }, []);

  return null;
}
