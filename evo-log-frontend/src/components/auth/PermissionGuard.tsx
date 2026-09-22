'use client';

import React from 'react';
import { useSession } from 'next-auth/react';
import { canAccessTCode } from '@/utils/tcodeLookup';
import { AlertTriangle, Lock } from 'lucide-react';

interface PermissionGuardProps {
  permission?: string;
  requiredRoles?: string[];
  tcode?: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showCADCWarning?: boolean;
}

export function PermissionGuard({
  permission,
  requiredRoles,
  tcode,
  children,
  fallback,
  showCADCWarning = true
}: PermissionGuardProps) {
  const { data: session } = useSession();
  const user = session?.user as any;
  const userRoles: string[] = (user?.roles || []).map((r: string) => r.toUpperCase());
  const userPermissions: string[] = user?.permissions || [];

  // Super Admin a accès absolu
  if (userRoles.includes('SUPER_ADMIN')) {
    return <>{children}</>;
  }

  // 1. Vérification T-Code si spécifié
  if (tcode) {
    const hasTCodeAccess = userRoles.some(r => canAccessTCode(r, tcode));
    if (!hasTCodeAccess) {
      if (fallback) return <>{fallback}</>;
      if (showCADCWarning) {
        return (
          <div className="p-6 my-4 bg-slate-900/90 border border-amber-500/30 rounded-2xl text-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-amber-500/10 text-amber-400 rounded-xl">
                <Lock className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-100">Accès Restreint CADC ERP</h4>
                <p className="text-xs text-slate-400 font-mono">T-Code : {tcode.toUpperCase()}</p>
              </div>
            </div>
            <p className="text-xs text-slate-300 bg-slate-950 p-3 rounded-xl border border-slate-800">
              Votre profil <b className="text-amber-400">[{userRoles.join(', ') || 'INVITÉ'}]</b> ne dispose pas des droits requis pour exécuter cette opération.
            </p>
          </div>
        );
      }
      return null;
    }
  }

  // 2. Vérification Rôles requis
  if (requiredRoles && requiredRoles.length > 0) {
    const normalizedRequired = requiredRoles.map(r => r.toUpperCase());
    const hasRoleAccess = userRoles.some(r => normalizedRequired.includes(r) || r === 'ADMIN');
    if (!hasRoleAccess) {
      if (fallback) return <>{fallback}</>;
      return null;
    }
  }

  // 3. Vérification Permission spécifique
  if (permission) {
    const hasPerm = userPermissions.includes(permission) || userRoles.includes('ADMIN');
    if (!hasPerm) {
      if (fallback) return <>{fallback}</>;
      return null;
    }
  }

  return <>{children}</>;
}

export default PermissionGuard;