'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { ClipboardList, ArrowLeft, Search, CheckCircle } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import { receptionMag3API } from '@/lib/api-client';

interface Reception {
  id: number;
  numero_bon: string;
  fournisseur_id: number;
  entrepot_id: number;
  entrepot_nom?: string;
  date_reception?: string;
  statut: string;
  notes?: string;
  nombre_lignes?: number;
}

const STATUT_STYLES: Record<string, string> = {
  en_attente: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
  valide: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  refuse: 'bg-red-500/10 text-red-400 border border-red-500/20',
};

export default function ReceptionMag3Page() {
  const [items, setItems] = useState<Reception[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterStatut, setFilterStatut] = useState<string>('');

  const fetchData = useCallback(async () => {
    try {
      const params: Record<string, unknown> = { limit: 200 };
      if (search) params.search = search;
      if (filterStatut) params.statut = filterStatut;
      const res: any = await receptionMag3API.getAll(params);
      const body = res.data ?? res;
      setItems(body.items || []);
      setTotal(body.total || 0);
    } catch (err: any) {
      if (err?.response?.status === 501 || err?.response?.status === 404) {
        toast.warning('Module réceptions MAG3 non configuré');
      } else {
        toast.error('Erreur chargement réceptions');
      }
    } finally {
      setLoading(false);
    }
  }, [search, filterStatut]);

  useEffect(() => { fetchData(); }, [fetchData]);

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-white animate-in fade-in duration-300">
      <Link href="/magasin/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-4">
        <ArrowLeft className="w-4 h-4" /> Retour au Dashboard
      </Link>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-black flex items-center gap-3">
            <ClipboardList className="w-7 h-7 text-sky-400" />
            Réceptions Magasin 3
          </h1>
          <p className="text-sm text-slate-400 mt-1">{total} réception(s) enregistrée(s)</p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="N° bon, notes..."
            className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>
        <select
          value={filterStatut}
          onChange={(e) => setFilterStatut(e.target.value)}
          className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-sky-500"
        >
          <option value="">Tous statuts</option>
          <option value="en_attente">En attente</option>
          <option value="valide">Validé</option>
          <option value="refuse">Refusé</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Chargement...</div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 bg-slate-900 border border-slate-800 rounded-2xl">
          <ClipboardList className="w-12 h-12 mx-auto text-slate-600 mb-3" />
          <p className="text-slate-400">Aucune réception MAG3</p>
        </div>
      ) : (
        <div className="overflow-x-auto bg-slate-900 border border-slate-800 rounded-2xl">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-xs tracking-wider">
                <th className="py-3 px-4">N° Bon</th>
                <th className="py-3 px-4">Entrepôt</th>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Statut</th>
                <th className="py-3 px-4">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {items.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-4 font-mono font-bold text-sky-400">{r.numero_bon}</td>
                  <td className="py-2.5 px-4">{r.entrepot_nom || `ID ${r.entrepot_id}`}</td>
                  <td className="py-2.5 px-4 text-slate-400">{r.date_reception ? new Date(r.date_reception).toLocaleDateString('fr-FR') : '-'}</td>
                  <td className="py-2.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${STATUT_STYLES[r.statut] || 'bg-slate-500/10 text-slate-400 border border-slate-500/20'}`}>
                      {r.statut?.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-slate-400 max-w-[200px] truncate">{r.notes || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
