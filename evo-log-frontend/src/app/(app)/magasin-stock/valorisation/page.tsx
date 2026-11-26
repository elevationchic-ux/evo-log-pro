'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Package, Search, CalendarClock } from 'lucide-react';
import { apiClient, apiUrl } from '@/lib/api-client';
import { toast } from 'sonner';

interface LigneValorisation {
  stock_id: number;
  code_article: string;
  designation: string;
  quantite: number;
  prix_unitaire: number;
  valorisation: number;
}

interface FefoResultat {
  stock_id: number;
  quantite_demandee: number;
  quantite_couverte: number;
  quantite_non_couverte: number;
  lots: { peremption_id: number; lot_numero: string; date_peremption?: string; quantite_allouee: number; cout_unitaire?: number }[];
}

const fmt = (v: number | undefined) => Number(v || 0).toLocaleString('fr-FR');

export default function ValorisationStockPage() {
  const [globale, setGlobale] = useState<{ nb_articles: number; valorisation_totale: number; lignes: LigneValorisation[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [stockId, setStockId] = useState('');
  const [quantite, setQuantite] = useState('');
  const [fefo, setFefo] = useState<FefoResultat | null>(null);

  const charger = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(apiUrl('/magasin-valuation/valorisation'));
      setGlobale(res.data);
    } catch { toast.error('Valorisation indisponible'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  const testerFefo = async () => {
    if (!stockId || !quantite) { toast.error('Stock et quantité requis'); return; }
    try {
      const res = await apiClient.get(apiUrl(`/magasin-valuation/fefo/${stockId}`), { params: { quantite: Number(quantite) } });
      setFefo(res.data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Allocation FEFO impossible');
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 md:p-6">
      <header>
        <h1 className="flex items-center gap-2 text-xl font-semibold text-slate-100">
          <Package className="h-6 w-6 text-amber-400" /> Valorisation &amp; FEFO
        </h1>
        <p className="text-sm text-slate-400">Valorisation des stocks sur prix réels et allocation des sorties par péremption croissante.</p>
      </header>

      <section className="grid grid-cols-2 gap-3 md:grid-cols-3">
        <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-4">
          <div className="text-[10px] uppercase text-slate-500">Articles en stock</div>
          <div className="text-xl font-bold text-slate-100">{globale?.nb_articles ?? '—'}</div>
        </div>
        <div className="col-span-2 rounded-xl border border-amber-500/30 bg-amber-500/5 p-4">
          <div className="text-[10px] uppercase text-amber-400/70">Valorisation totale</div>
          <div className="text-xl font-bold text-amber-300">{fmt(globale?.valorisation_totale)} XAF</div>
        </div>
      </section>

      <section className="rounded-xl border border-slate-700 p-4">
        <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-200"><CalendarClock className="h-4 w-4 text-cyan-400" /> Test d'allocation FEFO</h2>
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label className="mb-1 block text-xs text-slate-400">ID article de stock</label>
            <input value={stockId} onChange={e => setStockId(e.target.value)} placeholder="ex. 12"
              className="w-36 rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 min-h-[44px]" />
          </div>
          <div>
            <label className="mb-1 block text-xs text-slate-400">Quantité à sortir</label>
            <input type="number" min={0} step="any" value={quantite} onChange={e => setQuantite(e.target.value)} placeholder="ex. 50"
              className="w-36 rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 min-h-[44px]" />
          </div>
          <button onClick={testerFefo}
            className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-cyan-600 px-5 text-sm font-medium text-white hover:bg-cyan-500">
            <Search className="h-4 w-4" /> Allouer
          </button>
        </div>

        {fefo && (
          <div className="mt-4 space-y-2 font-mono text-xs">
            <p className="text-slate-300">Demandé {fefo.quantite_demandee} — couvert {fefo.quantite_couverte}
              {fefo.quantite_non_couverte > 0 && <span className="text-red-400"> — NON COUVERT {fefo.quantite_non_couverte}</span>}
            </p>
            <ul className="space-y-1">
              {fefo.lots.map(l => (
                <li key={l.peremption_id} className="flex justify-between rounded bg-slate-900/60 px-2 py-1">
                  <span className="text-cyan-300">lot {l.lot_numero} · péremption {l.date_peremption || '—'}</span>
                  <span>{l.quantite_allouee} {l.cout_unitaire != null ? `· ${fmt(l.cout_unitaire)} XAF/u` : ''}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section className="overflow-x-auto rounded-xl border border-slate-700">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
            <tr>
              <th className="px-4 py-3">Code</th><th className="px-4 py-3">Désignation</th>
              <th className="px-4 py-3 text-right">Quantité</th><th className="px-4 py-3 text-right">P.U.</th>
              <th className="px-4 py-3 text-right">Valorisation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 font-mono text-xs">
            {loading ? (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-500">Chargement…</td></tr>
            ) : !globale || globale.lignes.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-500">Aucun article en stock.</td></tr>
            ) : globale.lignes.map(l => (
              <tr key={l.stock_id} className="hover:bg-slate-900/50">
                <td className="px-4 py-3 text-amber-300">{l.code_article}</td>
                <td className="px-4 py-3 text-slate-200">{l.designation}</td>
                <td className="px-4 py-3 text-right">{fmt(l.quantite)}</td>
                <td className="px-4 py-3 text-right">{fmt(l.prix_unitaire)}</td>
                <td className="px-4 py-3 text-right font-bold text-slate-100">{fmt(l.valorisation)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
