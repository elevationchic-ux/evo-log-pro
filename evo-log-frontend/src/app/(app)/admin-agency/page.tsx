'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { RefreshCw } from 'lucide-react';

// Module historique fusionné dans /agences (réseau territorial + périmètre
// agence backend). Redirection conservée pour les liens profonds existants.
export default function AdminAgencyRedirect() {
  const router = useRouter();
  useEffect(() => { router.replace('/agences'); }, [router]);
  return (
    <div className="flex items-center justify-center py-24 text-slate-400">
      <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
    </div>
  );
}
