'use client';

/**
 * Panneaux d'état standard du projet (chargement / vide / erreur / service indisponible).
 * Cohérents avec la charte slate-amber, compréhensibles pour un novice,
 * toujours assortis d'une action possible (réessayer, créer, retour).
 */
import Link from 'next/link';
import { Inbox, RotateCcw, WifiOff, ShieldAlert, ServerCrash, FileQuestion, Plus } from 'lucide-react';
import type { ApiErrorInfo } from '@/hooks/useApi';

/* ------------------------------- Chargement ------------------------------- */
export function DataLoadingState({ rows = 4, label = 'Chargement des données…' }: { rows?: number; label?: string }) {
  return (
    <div className="space-y-3 animate-pulse" aria-busy="true" aria-live="polite">
      <p className="text-xs text-slate-500 font-mono">{label}</p>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-12 rounded-xl bg-slate-900 border border-slate-800" />
      ))}
    </div>
  );
}

/* --------------------------------- Vide ----------------------------------- */
export function DataEmptyState({
  title = 'Aucune donnée pour le moment',
  description,
  actionLabel,
  actionHref,
  onAction,
}: {
  title?: string;
  description?: string;
  actionLabel?: string;
  actionHref?: string;
  onAction?: () => void;
}) {
  const inner = (
    <>
      <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-slate-800/60 border border-slate-700">
        <Inbox className="w-6 h-6 text-slate-400" />
      </div>
      <p className="mt-3 text-sm font-semibold text-slate-200">{title}</p>
      {description && <p className="mt-1 text-xs text-slate-500 max-w-sm mx-auto leading-relaxed">{description}</p>}
      {actionLabel && (
        <span className="mt-4 inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-500 text-slate-950 text-xs font-bold group-hover:bg-amber-400 transition-colors">
          <Plus className="w-3.5 h-3.5" />
          {actionLabel}
        </span>
      )}
    </>
  );
  return (
    <div className="text-center py-12 px-4">
      {actionHref ? (
        <Link href={actionHref} className="inline-block group">{inner}</Link>
      ) : onAction ? (
        <button onClick={onAction} className="inline-block group">{inner}</button>
      ) : (
        inner
      )}
    </div>
  );
}

/* -------------------------------- Erreur ---------------------------------- */
const ERROR_ICONS = {
  not_found: FileQuestion,
  unauthorized: ShieldAlert,
  server: ServerCrash,
  network: WifiOff,
  empty: Inbox,
  none: Inbox,
  unknown: ServerCrash,
} as const;

export function DataErrorState({ error, onRetry }: { error: ApiErrorInfo; onRetry?: () => void }) {
  const Icon = ERROR_ICONS[error.kind] ?? ServerCrash;
  const isUnavailable = error.kind === 'not_found';
  return (
    <div className="text-center py-12 px-4">
      <div className={`inline-flex items-center justify-center w-12 h-12 rounded-2xl border ${
        isUnavailable ? 'bg-slate-800/60 border-slate-700' : 'bg-red-500/10 border-red-500/30'
      }`}>
        <Icon className={`w-6 h-6 ${isUnavailable ? 'text-slate-400' : 'text-red-400'}`} />
      </div>
      <p className="mt-3 text-sm font-semibold text-slate-200">
        {isUnavailable ? 'Fonction non disponible' : 'Le chargement a échoué'}
      </p>
      <p className="mt-1 text-xs text-slate-500 max-w-md mx-auto leading-relaxed">{error.message}</p>
      {error.detail && (
        <p className="mt-2 text-[10px] font-mono text-slate-400 break-all">{error.detail}</p>
      )}
      {onRetry && !isUnavailable && (
        <button
          onClick={onRetry}
          className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-200 hover:bg-slate-700 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Réessayer
        </button>
      )}
      {error.kind === 'unauthorized' && (
        <Link
          href="/login"
          className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-500 text-slate-950 text-xs font-bold hover:bg-amber-400 transition-colors"
        >
          Se reconnecter
        </Link>
      )}
    </div>
  );
}

/* -------------------- Pratique : rendu conditionnel unique ---------------- */
import type { ReactNode } from 'react';

export function DataStateGate({
  loading,
  error,
  isEmpty,
  onRetry,
  skeletonRows,
  empty,
  children,
}: {
  loading: boolean;
  error: ApiErrorInfo | null;
  isEmpty: boolean;
  onRetry?: () => void;
  skeletonRows?: number;
  empty?: ReactNode;
  children: ReactNode;
}) {
  if (loading) return <DataLoadingState rows={skeletonRows} />;
  if (error) return <DataErrorState error={error} onRetry={onRetry} />;
  if (isEmpty) return <>{empty ?? <DataEmptyState />}</>;
  return <>{children}</>;
}
