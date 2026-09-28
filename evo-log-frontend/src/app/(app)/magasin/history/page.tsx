'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { History, ArrowLeft, Search } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import { magasinAPI } from '@/lib/api-client';

interface MouvementLigne {
  id: number;
  reference: string;
  type_mouvement: string;
  quantite: number;
  quantite_avant?: number;
  quantite_apres?: number;
  valeur_totale?: number;
  raison?: string;
  document_reference?: string;
  destination?: string;
  operateur?: string;
  date_mouvement?: string;
}

export default function HistoriqueMouvementsPage() {
  const [items, setItems] = useState<MouvementLigne[]>([]);
  const [total, setTotal] = useState(0);
  const [entrees, setEntrees] = useState(0);
  const [sorties, setSorties] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchHistory = useCallback(async () => {
    try {
      const res: any = await magasinAPI.getHistory({ q: search || undefined, limit: 200 });
      const body = res.data ?? res;
      setItems(body.items || []);
      setTotal(body.total || 0);
      setEntrees(body.entrees || 0);
      setSorties(body.sorties || 0);
    } catch (err: any) {
      if (err?.response?.status === 501) {
        toast.warning('Module historique non configure');
      } else {
        toast.error('Erreur chargement historique');
      }
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-white animate-in fade-in duration-300">
      <Link href="/magasin/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-4">
        <ArrowLeft className="w-4 h-4" /> Retour au Dashboard
      </Link>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-black flex items-center gap-3">
            <History className="w-7 h-7 text-sky-400" />
            Historique des Mouvements
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            {total} mouvement(s) &#8212; Entr&#233;es: {entrees.toLocaleString()} &#8212; Sorties: {sorties.toLocaleString()}
          </p>
        </div>
      </div>

      <div className="relative mb-4 max-w-md">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filtrer par article, r&#233;f&#233;rence..."
          className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
        />
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Chargement...</div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 bg-slate-900 border border-slate-800 rounded-2xl">
          <History className="w-12 h-12 mx-auto text-slate-600 mb-3" />
          <p className="text-slate-400">Aucun mouvement enregistr&#233;</p>
        </div>
      ) : (
        <div className="overflow-x-auto bg-slate-900 border border-slate-800 rounded-2xl">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-xs tracking-wider">
                <th className="py-3 px-4">R&#233;f&#233;rence</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Article</th>
                <th className="py-3 px-4 text-right">Qt&#233;</th>
                <th className="py-3 px-4 text-right">Avant</th>
                <th className="py-3 px-4 text-right">Apr&#232;s</th>
                <th className="py-3 px-4">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {items.map((m) => (
                <tr key={m.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-4 font-mono text-xs">{m.reference}</td>
                  <td className="py-2.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                      m.type_mouvement === 'entree'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : m.type_mouvement === 'sortie'
                        ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {m.type_mouvement}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 max-w-[180px] truncate">{m.raison || m.document_reference || '-'}</td>
                  <td className="py-2.5 px-4 text-right font-mono">{m.quantite?.toLocaleString() || '-'}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-slate-400">{m.quantite_avant?.toLocaleString() || '-'}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-slate-400">{m.quantite_apres?.toLocaleString() || '-'}</td>
                  <td className="py-2.5 px-4 text-slate-400 text-xs">{m.date_mouvement ? new Date(m.date_mouvement).toLocaleDateString('fr-FR') : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
