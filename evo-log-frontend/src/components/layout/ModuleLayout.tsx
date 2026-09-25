// src/components/layout/ModuleLayout.tsx - Primitive de page standardisée
// Châssi commun à toutes les pages de l'ERP : titre + description (pédagogique
// pour un novice) + aide contextuelle + zone d'actions. Rétro-compatible :
// sans `title`, le composant rend simplement ses enfants (comportement historique).
'use client';

import { ReactNode } from 'react';

interface ModuleLayoutProps {
  children: ReactNode;
  module?: string;
  /** Titre de la page, en français métier (ex. « Ordres de transfert magasin »). */
  title?: string;
  /** Description d'une phrase : ce que fait la page, pour un utilisateur novice. */
  description?: string;
  /** Aide contextuelle affichée dans un bandeau discret (astuce, rappel de processus). */
  help?: string;
  /** Zone d'actions (boutons principaux : créer, exporter, paramétrer…). */
  actions?: ReactNode;
}

export function ModuleLayout({ children, title, description, help, actions }: ModuleLayoutProps) {
  if (!title) return <>{children}</>;

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-xl sm:text-2xl font-bold text-slate-100 tracking-tight">{title}</h1>
          {description && (
            <p className="mt-1 text-sm text-slate-400 max-w-3xl leading-relaxed">{description}</p>
          )}
        </div>
        {actions && <div className="flex flex-wrap items-center gap-2 shrink-0">{actions}</div>}
      </header>

      {help && (
        <div
          role="note"
          className="flex items-start gap-2 rounded-xl border border-indigo-500/30 bg-indigo-500/10 px-3 py-2.5 text-xs text-indigo-200"
        >
          <span aria-hidden className="material-symbols-outlined text-[16px] mt-px shrink-0">
            info
          </span>
          <span className="leading-relaxed">{help}</span>
        </div>
      )}

      {children}
    </div>
  );
}

export default ModuleLayout;
