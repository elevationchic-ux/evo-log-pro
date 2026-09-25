'use client';

// Route-level guard for the entire Super-Admin SaaS governance subtree
// (/admin-saas, /admin-saas/tenants, /admin-saas/users, /admin-saas/roles-permissions).
//
// The sidebar menu already hides these entries for non-super-admins via
// navigationRegistry.getFilteredNavigationForUser(), but menu hiding alone is not
// enough: the routes stay reachable by typing the URL. This layout closes that gap
// so the console is genuinely INVISIBLE to everyone except the platform Super Admin.
//
// The backend independently enforces require_superadmin on every console endpoint
// (403 otherwise); this guard simply avoids rendering a shell that would only show
// empty/error states to an unauthorized visitor.

import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { useAuth } from '@/components/shared/AuthProvider';

export default function AdminSaasLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  const isSuperAdmin = Boolean(
    (user as any)?.is_superuser ||
    user?.roles?.some((r) => {
      const u = (r || '').toUpperCase();
      return u === 'SUPER_ADMIN' || u === 'SUPERADMIN';
    })
  );

  // While the session is resolving, render nothing (the (app) layout already shows
  // the global loading screen). Rendering a "denied" flash for a legitimate super
  // admin would be a visible tell, which is exactly what invisibility avoids.
  if (loading) return null;

  if (!isSuperAdmin) {
    // Neutral, non-descriptive denial: we do not advertise that a console exists here.
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
