'use client';

// Route-level guard for the entire Super-Admin CADC console subtree
// (/admin/super-admin, /admin/super-admin/entreprises, /plans-abonnement,
// /prestataires, /accreditations-entreprises).
//
// La sidebar masque déjà ce groupe pour tout non-super-admin, mais le masquage
// du menu ne suffit pas : les routes resteraient atteignables en tapant l'URL.
// Cette layout ferme ce trou pour que la console soit réellement INVISIBLE à
// tous sauf au Super Administrateur plateforme (compte CADC, niveau hiérarchique 0).
//
// Le backend applique indépendamment require_superadmin sur chaque endpoint
// (403 sinon) ; ce garde évite simplement de rendre une coquille qui n'afficherait
// que des états vides/erreur à un visiteur non autorisé.

import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { useAuth } from '@/components/shared/AuthProvider';

export default function CadcConsoleLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  const isSuperAdmin = Boolean(
    (user as any)?.isSuperuser ||
    Number((user as any)?.roleLevel ?? 9) === 0 ||
    user?.roles?.some((r) => {
      const u = (r || '').toUpperCase();
      return u === 'SUPER_ADMIN' || u === 'SUPERADMIN' || u === 'CADC';
    })
  );

  // Pendant la résolution de la session, ne rien rendre : flasher un "accès
  // refusé" à un légitime super-admin serait une indication visible, exactement
  // ce que l'invisibilité cherche à éviter.
  if (loading) return null;

  if (!isSuperAdmin) {
    // Refus neutre et non descriptif : on n'annonce pas qu'une console existe ici.
    return (
      <div className="max-w-md mx-auto my-16 text-center space-y-3">
        <div className="w-14 h-14 rounded-2xl bg-slate-800/60 border border-slate-700 text-slate-500 flex items-center justify-center mx-auto">
          <ShieldAlert className="w-7 h-7" />
        </div>
        <p className="text-sm font-bold text-slate-400">Page introuvable</p>
        <p className="text-xs text-slate-500">
          Cette adresse ne correspond à aucune ressource accessible.
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
