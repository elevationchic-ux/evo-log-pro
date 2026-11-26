'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { AlertTriangle, Compass, FileText, Package, RefreshCw } from 'lucide-react';
import { b2bPortalAPI } from '@/lib/api-client';

export default function B2BClientDashboard() {
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);

  const loadDashboard = async () => {
    setLoading(true);
    setMessage(null);
    try {
      await b2bPortalAPI.getDossiers();
    } catch {
      setMessage('Les dossiers B2B persistés ne sont pas encore disponibles pour cette société.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadDashboard();
  }, []);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        <h1 className="flex items-center gap-2 text-2xl font-black text-white">
          <Compass className="h-6 w-6 text-amber-400" /> Tableau de bord B2B
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Les opérations affichées doivent provenir des dossiers persistés de votre société.
        </p>
      </div>

      {loading && <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 text-sm text-slate-400">Chargement des dossiers...</div>}
      {!loading && message && (
        <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-5 text-sm text-amber-200">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
            <div>
              <p>{message}</p>
              <p className="mt-1 text-xs text-amber-300/80">Aucune donnée de démonstration n’est affichée.</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        <Link href="/b2b/tracking" className="rounded-2xl border border-slate-800 bg-slate-900 p-5 text-slate-200 hover:border-amber-500/50">
          <Package className="mb-3 h-5 w-5 text-amber-400" />
          <span className="font-bold">Suivi cargaison</span>
        </Link>
        <Link href="/b2b/documents" className="rounded-2xl border border-slate-800 bg-slate-900 p-5 text-slate-200 hover:border-amber-500/50">
          <FileText className="mb-3 h-5 w-5 text-amber-400" />
          <span className="font-bold">Documents</span>
        </Link>
        <button onClick={() => void loadDashboard()} className="rounded-2xl border border-slate-800 bg-slate-900 p-5 text-left text-slate-200 hover:border-amber-500/50">
          <RefreshCw className="mb-3 h-5 w-5 text-amber-400" />
          <span className="font-bold">Actualiser</span>
        </button>
      </div>
    </div>
  );
}
