'use client';

import { useEffect, useState } from 'react';
import { RefreshCw, WalletCards } from 'lucide-react';
import { rhAPI } from '@/lib/api-client';

type Payroll = {
  id: number;
  periode_debut?: string;
  periode_fin?: string;
  salaire_base: number;
  salaire_net: number;
  primes: number;
  deductions: number;
  date_paiement?: string | null;
  statut?: string;
};

export default function RHPaiePage() {
  const [rows, setRows] = useState<Payroll[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await rhAPI.getPaie();
      const data = response.data;
      setRows(Array.isArray(data) ? data : data?.items || []);
    } catch (requestError: any) {
      setRows([]);
      setError(requestError?.response?.data?.detail || 'Impossible de charger la paie.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <WalletCards className="w-6 h-6 text-emerald-400" /> Paie
          </h1>
          <p className="text-xs text-slate-400">Bulletins persistés de l’employé authentifié</p>
        </div>
        <button onClick={load} disabled={loading} className="px-3 py-2 rounded-lg border border-slate-700 text-slate-300 text-xs">
          <RefreshCw className={`w-4 h-4 inline mr-2 ${loading ? 'animate-spin' : ''}`} /> Actualiser
        </button>
      </div>
      {error && <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm">{error}</div>}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 overflow-hidden">
        {loading ? <div className="p-6 text-slate-400">Chargement...</div> : rows.length === 0 ? (
          <div className="p-6 text-slate-400">Aucun bulletin de paie enregistré.</div>
        ) : (
          <div className="divide-y divide-slate-800">
            {rows.map(row => (
              <div key={row.id} className="p-4 grid grid-cols-1 md:grid-cols-6 gap-2 text-sm">
                <span className="text-slate-300">{row.periode_debut || 'Période indisponible'} → {row.periode_fin || ''}</span>
                <span className="text-slate-300">{row.salaire_base.toLocaleString('fr-FR')} XAF brut</span>
                <span className="text-white font-semibold">{row.salaire_net.toLocaleString('fr-FR')} XAF net</span>
                <span className="text-slate-400">Primes: {row.primes.toLocaleString('fr-FR')} XAF</span>
                <span className="text-slate-400">Retenues: {row.deductions.toLocaleString('fr-FR')} XAF</span>
                <span className="text-slate-300">{row.statut || 'Statut indisponible'}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
