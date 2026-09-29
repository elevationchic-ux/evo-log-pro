'use client';

// Garde de périmètre pour l'arborescence /departement (Phase 3  niveau 2).
//
// La sidebar ne publie ce groupe qu'aux rôles CHEF_DEPARTEMENT et supérieurs ;
// ce garde route-level ferme le trou « saisie directe de l'URL » pour que
// l'écran "Mon Département" reste inaccessible à un simple utilisateur (niveau 3).
//
// Règle d'invisibilité (plan Phase 3) : visible par le chef de département (2),
// l'admin entreprise (1) et le CADC (0). Le backend applique indépendamment
// require_department_head + _scoped_department (403 niveau 3, 403 cross-département
// pour un chef, 403 cross-entreprise pour un admin).

import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { useAuth } from '@/components/shared/AuthProvider';

export default function DepartementLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  const level = Number((user as any)?.roleLevel ?? 9);
  const isSuper = Boolean((user as any)?.isSuperuser) || level === 0;
  const canAccess = isSuper || level <= 2;

  if (loading) return null;

  if (!canAccess) {
    return (
      <div className="max-w-md mx-auto my-16 text-center space-y-3">
        <div className="w-14 h-14 rounded-2xl bg-slate-800/60 border border-slate-700 text-slate-500 flex items-center justify-center mx-auto">
          <ShieldAlert className="w-7 h-7" />
        </div>
        <p className="text-sm font-bold text-slate-400">Accès réservé</p>
        <p className="text-xs text-slate-500">
          Cette zone est réservée aux chefs de département et à l'administration.
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
