'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { BarChart3, ArrowLeft, Search } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api-client';

interface Rapport {
  id: number;
  numero_rapport: string;
  titre: string;
  type_rapport: string;
  frequence: string;
  statut: string;
  description?: string;
}

export default function RapportsPage() {
  const [rapports, setRapports] = useState<Rapport[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchData = useCallback(async () => {
    try {
      const res: any = await apiClient.get('/api/v1/reporting/rapports', { params: { limit: 200 } });
      const body = res.data ?? res;
      const list: Rapport[] = Array.isArray(body) ? body : (body.items || []);
      setRapports(list);
    } catch (err: any) {
      if (err?.response?.status === 404 || err?.response?.status === 501) {
        toast.warning('Module reporting non configuré');
      } else {
        toast.error('Erreur chargement rapports');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const filtered = search
    ? rapports.filter(r => r.titre.toLowerCase().includes(search.toLowerCase()) || r.numero_rapport.toLowerCase().includes(search.toLowerCase()))
    : rapports;

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-white animate-in fade-in duration-300">
      <Link href="/magasin/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-4">
        <ArrowLeft className="w-4 h-4" /> Retour au Dashboard
      </Link>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-black flex items-center gap-3">
            <BarChart3 className="w-7 h-7 text-violet-400" />
            Rapports & Analyses
          </h1>
          <p className="text-sm text-slate-400 mt-1">{rapports.length} rapport(s) disponible(s)</p>
        </div>
      </div>

      <div className="relative mb-4 max-w-md">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Rechercher par titre ou numéro..."
          className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500"
        />
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Chargement...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 bg-slate-900 border border-slate-800 rounded-2xl">
          <BarChart3 className="w-12 h-12 mx-auto text-slate-600 mb-3" />
          <p className="text-slate-400">Aucun rapport enregistré</p>
        </div>
      ) : (
        <div className="overflow-x-auto bg-slate-900 border border-slate-800 rounded-2xl">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-xs tracking-wider">
                <th className="py-3 px-4">N° Rapport</th>
                <th className="py-3 px-4">Titre</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Fréquence</th>
                <th className="py-3 px-4">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-4 font-mono text-xs text-violet-400">{r.numero_rapport}</td>
                  <td className="py-2.5 px-4 font-medium">{r.titre}</td>
                  <td className="py-2.5 px-4 text-slate-400">{r.type_rapport}</td>
                  <td className="py-2.5 px-4 text-slate-400">{r.frequence}</td>
                  <td className="py-2.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                      r.statut === 'actif'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                    }`}>
                      {r.statut}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
