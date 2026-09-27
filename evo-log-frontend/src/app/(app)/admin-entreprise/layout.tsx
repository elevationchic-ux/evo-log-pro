'use client';

// Garde de périmètre pour l'arborescence /admin-entreprise (Phase 2 — niveau 1).
//
// La sidebar ne publie ce groupe qu'aux rôles ADMIN / SUPER_ADMIN ; ce garde
// route-level ferme le trou « saisie directe de l'URL » pour que l'écran
// "Administration Entreprise" reste inaccessible à tout niveau > 1.
//
// Règle d'invisibilité (plan Phase 2) : visible uniquement par le CADC (niveau 0)
// et l'admin entreprise (niveau 1). Le backend applique indépendamment
// require_company_admin + resolve_scope_company_id (403 / 403 cross-tenant).

import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { useAuth } from '@/components/shared/AuthProvider';

export default function AdminEntrepriseLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  const level = Number((user as any)?.roleLevel ?? 9);
  const isSuper = Boolean((user as any)?.isSuperuser) || level === 0;
  const canAccess = isSuper || level <= 1;

  if (loading) return null;

  if (!canAccess) {
    return (
      <div className="max-w-md mx-auto my-16 text-center space-y-3">
        <div className="w-14 h-14 rounded-2xl bg-slate-800/60 border border-slate-700 text-slate-500 flex items-center justify-center mx-auto">
          <ShieldAlert className="w-7 h-7" />
        </div>
        <p className="text-sm font-bold text-slate-400">Accès réservé</p>
        <p className="text-xs text-slate-500">
          Cette zone est réservée à l'administrateur de votre entreprise.
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
