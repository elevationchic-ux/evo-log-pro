'use client';

// Phase 4 — UI adaptative.
//
// Le principe (cf. plan) : "le nombre de sous-modules affichés diminue avec le
// niveau d'accès ; en dessous de 6 modules, rendu alternatif en anneaux orbitant
// autour du module, sans changer les path."
//
// Ce composant est PUREMENT PRÉSENTATIONNEL : il reçoit une liste de modules
// DÉJÀ filtrés en accessibilité par l'appelant (qui connaît les rôles/niveau de
// l'utilisateur). Il ne décide aucune autorisation lui-même — la vérité d'accès
// reste côté backend/garde de session. Les href sont transmis tels quels : on ne
// réécrit jamais un chemin selon le mode d'affichage.
//
// - >= threshold modules visibles : grille de cartes (rendu classique) ;
// - <  threshold modules visibles : anneau orbital (les modules gravitent autour
//   d'un noyau), ce qui remplit mieux l'écran qu'une grille à 2 ou 3 cases.
//
// Sur très petit écran l'orbite peut devenir illisible ; on bascule alors sur la
// grille via les classes responsives (l'orbite est masquée < md).

import React from 'react';
import Link from 'next/link';
import { ArrowRight, Lock } from 'lucide-react';

export interface AdaptiveModule {
  id: string;
  title: string;
  subtitle?: string;
  /** Chemin réel, transmis inchangé au lien (règle "sans changer les path"). */
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  /** Classes dégradé Tailwind (ex. 'from-blue-600 to-indigo-600'). */
  gradient?: string;
  /** Libellé court affiché sur la carte (ex. badge de domaine). */
  badge?: string;
  /** false = module verrouillé pour ce profil : on le grise, on n'orbite pas dessus. */
  allowed?: boolean;
}

interface AdaptiveModuleGridProps {
  items: AdaptiveModule[];
  /** Bascule grille -> orbite en dessous de ce nombre de modules AUTORISÉS. Défaut 6. */
  threshold?: number;
  /** Titre au centre de l'orbite quand le mode orbital est actif. */
  centerTitle?: string;
  centerSubtitle?: string;
}

/** Grille classique de cartes (mode par défaut, >= threshold). */
function GridRender({ items }: { items: AdaptiveModule[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      {items.map((m) => {
        const Icon = m.icon;
        const allowed = m.allowed !== false;
        return (
          <Link
            key={m.id}
            href={m.href}
            aria-disabled={!allowed}
            className={`group relative flex flex-col justify-between rounded-2xl border p-5 transition-all duration-200 ${
              allowed
                ? 'bg-slate-900 border-slate-700 hover:-translate-y-1 hover:shadow-xl hover:border-indigo-500/50'
                : 'bg-slate-800/60 border-slate-700/70 opacity-60 cursor-not-allowed'
            }`}
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${m.gradient || 'from-slate-600 to-slate-700'} text-white flex items-center justify-center shadow-md`}>
                  <Icon className="w-5 h-5" />
                </div>
                {m.badge && (
                  <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full border bg-indigo-500/10 text-indigo-300 border-indigo-500/40">
                    {m.badge}
                  </span>
                )}
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-200 leading-snug">{m.title}</h3>
                {m.subtitle && <p className="text-xs text-indigo-500 font-medium">{m.subtitle}</p>}
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-700/70 flex items-center justify-between text-xs">
              {allowed ? (
                <>
                  <span className="text-slate-400">Ouvrir</span>
                  <ArrowRight className="w-4 h-4 text-indigo-500 group-hover:translate-x-0.5 transition" />
                </>
              ) : (
                <span className="inline-flex items-center gap-1.5 text-slate-400 font-semibold">
                  <Lock className="w-3.5 h-3.5" /> Accès restreint
                </span>
              )}
            </div>
          </Link>
        );
      })}
    </div>
  );
}

/**
 * Anneau orbital : les modules AUTORISÉS gravitent autour d'un noyau central.
 * Position calculée sur un cercle (angle = index/N), en pourcentages pour rester
 * responsive dans un conteneur `aspect-square`. Les verrouillés ne sont pas
 * orbités (sinon l'anneau perd son sens "ce que je peux atteindre").
 *
 * En-dessous de `md`, on masque l'orbite et on retombe sur la grille : un anneau
 * de tuiles sur 320px est illisible, et l'accès aux memes `href` est préservé.
 */
function OrbitRender({
  allowedItems,
  allItems,
  centerTitle,
  centerSubtitle,
}: {
  allowedItems: AdaptiveModule[];
  allItems: AdaptiveModule[];
  centerTitle?: string;
  centerSubtitle?: string;
}) {
  const N = allowedItems.length;
  // Rayon en % du demi-conteneur ; un peu de marge pour que les tuiles ne
  // débordent pas du carré.
  const radius = 38;

  return (
    <>
      {/* Orbite : visible md+ uniquement. */}
      <div className="relative hidden md:block w-full max-w-xl mx-auto aspect-square">
        {/* Cercle-guide (le "anneau"). */}
        <div
          className="absolute rounded-full border-2 border-dashed border-indigo-500/25"
          style={{
            width: `${radius * 2}%`,
            height: `${radius * 2}%`,
            left: `${50 - radius}%`,
            top: `${50 - radius}%`,
          }}
        />
        {/* Noyau central. */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 rounded-full bg-gradient-to-br from-indigo-600 to-indigo-800 text-white flex flex-col items-center justify-center text-center shadow-2xl shadow-indigo-900/40 border border-indigo-400/40 p-3">
          <span className="text-sm font-black leading-tight">{centerTitle || 'Hub'}</span>
          {centerSubtitle && (
            <span className="text-[11px] text-indigo-200 mt-1 leading-tight">{centerSubtitle}</span>
          )}
        </div>

        {allowedItems.map((m, i) => {
          const Icon = m.icon;
          // On part du sommet (-90deg) puis on tourne, pour un rendu équilibré.
          const angle = (-90 + (360 / N) * i) * (Math.PI / 180);
          const cx = 50 + radius * Math.cos(angle);
          const cy = 50 + radius * Math.sin(angle);
          return (
            <Link
              key={m.id}
              href={m.href}
              className="group absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-1 w-24 text-center transition-transform hover:scale-110"
              style={{ left: `${cx}%`, top: `${cy}%` }}
            >
              <span className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${m.gradient || 'from-slate-600 to-slate-700'} text-white flex items-center justify-center shadow-lg ring-2 ring-slate-900`}>
                <Icon className="w-6 h-6" />
              </span>
              <span className="text-[11px] font-bold text-slate-200 leading-tight line-clamp-2 group-hover:text-indigo-300 transition">
                {m.title}
              </span>
            </Link>
          );
        })}
      </div>

      {/* Repli grille sur mobile : memes cibles, lisibilité préservée. */}
      <div className="md:hidden">
        <GridRender items={allItems} />
      </div>
    </>
  );
}

export default function AdaptiveModuleGrid({
  items,
  threshold = 6,
  centerTitle,
  centerSubtitle,
}: AdaptiveModuleGridProps) {
  const allowedItems = items.filter((m) => m.allowed !== false);

  // Sous le seuil de modules ACCESSIBLES -> anneau orbital. On passe aussi
  // allItems au mode orbital pour que le repli mobile conserve les verrouillés.
  if (allowedItems.length < threshold) {
    return (
      <OrbitRender
        allowedItems={allowedItems}
        allItems={items}
        centerTitle={centerTitle}
        centerSubtitle={centerSubtitle}
      />
    );
  }

  return <GridRender items={items} />;
}
