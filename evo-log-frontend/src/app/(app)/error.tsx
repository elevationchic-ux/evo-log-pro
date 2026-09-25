'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { AlertTriangle, RotateCcw, LayoutDashboard, LifeBuoy } from 'lucide-react';

/**
 * Ecran de secours du workspace : capture toute erreur de rendu survenue
 * dans une page du groupe (app). Jamais d'ecran blanc pour l'utilisateur.
 */
export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Journalise la trace pour le diagnostic technique
    console.error('[EVO-LOG] Erreur de page:', error);
  }, [error]);

  return (
    <div className="flex items-center justify-center min-h-[60vh] px-4 py-12">
      <div className="max-w-md w-full text-center space-y-5">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-red-500/10 border border-red-500/30">
          <AlertTriangle className="w-7 h-7 text-red-400" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-slate-100">Cette page a rencontré un problème</h2>
          <p className="mt-2 text-sm text-slate-400 leading-relaxed">
            Vos données n&apos;ont pas été affectées. Relancez la page&nbsp;; si le problème
            persiste, prévenez votre administrateur en précisant le module concerné.
          </p>
        </div>
        {error.digest && (
          <p className="text-[11px] font-mono text-slate-400">Référence technique : {error.digest}</p>
        )}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            onClick={reset}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-amber-500 text-slate-950 text-sm font-bold hover:bg-amber-400 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            Réessayer
          </button>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-sm font-semibold text-slate-200 hover:bg-slate-700 transition-colors"
          >
            <LayoutDashboard className="w-4 h-4" />
            Retour au tableau de bord
          </Link>
        </div>
        <p className="inline-flex items-center gap-1.5 text-xs text-slate-500">
          <LifeBuoy className="w-3.5 h-3.5" />
          Besoin d&apos;aide ? Le support interne EVO-LOG est disponible via le menu assistance.
        </p>
      </div>
    </div>
  );
}
