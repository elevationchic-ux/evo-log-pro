'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { ClipboardCheck, ArrowLeft, Search } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api-client';

interface Inventaire {
  id: number;
  numero_inventaire: string;
  entrepot_id: number;
  type_inventaire: string;
  date_debut?: string;
  date_fin?: string;
  operateur?: string;
  inspecteur_douane?: string;
  resultat?: string;
  ecart_tonnage?: number;
  ecart_valeur?: number;
  statut: string;
  lignes: number;
}

const STATUT_STYLES: Record<string, string> = {
  en_cours: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
  complet: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  valide: 'bg-sky-500/10 text-sky-400 border border-sky-500/20',
};

export default function InventairePhysiquePage() {
  const [items, setItems] = useState<Inventaire[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchData = useCallback(async () => {
    try {
      const res: any = await apiClient.get('/api/v1/magasin-douane/inventaires', { params: { limit: 200 } });
      const body = res.data ?? res;
      setItems(body.items || []);
      setTotal(body.total || 0);
    } catch (err: any) {
      if (err?.response?.status === 404 || err?.response?.status === 501) {
        toast.warning('Module inventaires non configuré');
      } else {
        toast.error('Erreur chargement inventaires');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const filtered = search
    ? items.filter(i => i.numero_inventaire.toLowerCase().includes(search.toLowerCase()) || (i.operateur || '').toLowerCase().includes(search.toLowerCase()))
    : items;

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-white animate-in fade-in duration-300">
      <Link href="/magasin/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-4">
        <ArrowLeft className="w-4 h-4" /> Retour au Dashboard
      </Link>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-black flex items-center gap-3">
            <ClipboardCheck className="w-7 h-7 text-emerald-400" />
            Inventaires Physiques
          </h1>
          <p className="text-sm text-slate-400 mt-1">{total} inventaire(s) enregistré(s)</p>
        </div>
      </div>

      <div className="relative mb-4 max-w-md">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="N° inventaire, opérateur..."
          className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
        />
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Chargement...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 bg-slate-900 border border-slate-800 rounded-2xl">
          <ClipboardCheck className="w-12 h-12 mx-auto text-slate-600 mb-3" />
          <p className="text-slate-400">Aucun inventaire physique enregistré</p>
        </div>
      ) : (
        <div className="overflow-x-auto bg-slate-900 border border-slate-800 rounded-2xl">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-xs tracking-wider">
                <th className="py-3 px-4">N° Inventaire</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Période</th>
                <th className="py-3 px-4">Opérateur</th>
                <th className="py-3 px-4 text-center">Lignes</th>
                <th className="py-3 px-4">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((inv) => (
                <tr key={inv.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-4 font-mono font-bold text-emerald-400">{inv.numero_inventaire}</td>
                  <td className="py-2.5 px-4 text-slate-400">{inv.type_inventaire || '-'}</td>
                  <td className="py-2.5 px-4 text-slate-400 text-xs">
                    {inv.date_debut ? new Date(inv.date_debut).toLocaleDateString('fr-FR') : '?'} → {inv.date_fin ? new Date(inv.date_fin).toLocaleDateString('fr-FR') : '?'}
                  </td>
                  <td className="py-2.5 px-4">{inv.operateur || '-'}</td>
                  <td className="py-2.5 px-4 text-center font-mono">{inv.lignes}</td>
                  <td className="py-2.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${STATUT_STYLES[inv.statut] || 'bg-slate-500/10 text-slate-400 border border-slate-500/20'}`}>
                      {inv.statut?.replace('_', ' ')}
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
