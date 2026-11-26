'use client';

import { usePathname } from 'next/navigation';
import DomainLoadingExperience from '@/components/shared/DomainLoadingExperience';

/**
 * Page de chargement dynamique globale de l'ERP EVO-LOG :
 * Détecte le module en cours de résolution et déploie l'ambiance, la couleur
 * et l'animation signature spécifique du domaine (Comptabilité, Port, Transport, Collaboratif...)
 */
export default function AppLoading() {
  const pathname = usePathname();
  const segment = pathname ? pathname.replace(/^\/+/, '').split('/')[0] : 'dashboard';

  return (
    <div className="relative min-h-[calc(100vh-var(--app-header-h,64px))] flex items-center justify-center p-2 sm:p-4">
      <DomainLoadingExperience
        targetDomain={segment}
        fullScreen={false}
        durationMs={2000}
      />
    </div>
  );
}
