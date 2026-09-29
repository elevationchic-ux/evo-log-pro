'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { ClipboardCheck, ArrowLeft, Save, Search } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import { magasinAPI, inventaireAPI } from '@/lib/api-client';

interface StockItem {
  id: number;
  code_article: string;
  designation: string;
  categorie?: string;
  unite_mesure?: string;
  quantite_disponible: number;
  emplacement?: string;
  entrepot_id?: number;
  entrepot_nom?: string;
}

interface CountLine {
  stock_id: number;
  code: string;
  description: string;
  location: string;
  uom: string;
  systemQty: number;
  realQty: number | null;
  variance: number | null;
  status: 'pending' | 'match' | 'shortage' | 'overage';
}

export default function SaisieInventairePhysiquePage() {
  const [items, setItems] = useState<StockItem[]>([]);
  const [counts, setCounts] = useState<Map<number, number | null>>(new Map());
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [saving, setSaving] = useState(false);

  const fetchStocks = useCallback(async () => {
    try {
      const params: Record<string, unknown> = { limit: 500 };
      if (search) params.q = search;
      const res: any = await magasinAPI.getStocks(params);
      const body = res.data ?? res;
      const list: StockItem[] = body.items || [];
      setItems(list);
      setCounts(new Map());
    } catch (err: any) {
      if (err?.response?.status === 501) {
        toast.warning('Module stocks non configuré');
      } else {
        toast.error('Erreur chargement stocks');
      }
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { fetchStocks(); }, [fetchStocks]);

  const setRealQty = (stockId: number, qty: number | null) => {
    setCounts(prev => {
      const next = new Map(prev);
      next.set(stockId, qty);
      return next;
    });
  };

  const computedLines: CountLine[] = items.map(item => {
    const realQty = counts.get(item.id) ?? null;
    const variance = realQty !== null ? realQty - item.quantite_disponible : null;
    let status: CountLine['status'] = 'pending';
    if (realQty !== null) {
      if (variance === 0) status = 'match';
      else if (variance! < 0) status = 'shortage';
      else status = 'overage';
    }
    return {
      stock_id: item.id,
      code: item.code_article,
      description: item.designation,
      location: item.emplacement || item.entrepot_nom || '-',
      uom: item.unite_mesure || 'U',
      systemQty: item.quantite_disponible,
      realQty,
      variance,
      status,
    };
  });

  const counted = computedLines.filter(l => l.realQty !== null);
  const pending = computedLines.length - counted.length;

  const handleSubmit = async () => {
    if (counted.length === 0) {
      toast.error('Aucune ligne comptée à soumettre');
      return;
    }
    // Le circuit réel (Batch 18) : inventaire tournant → comptages →
    // validation qui ajuste le stock et journalise chaque écart.
    // L'ancien code postait un payload d'inventaire sur /magasin-avance/
    // receptions (422 permanent) en croyant « enregistrer les écarts » :
    // rien n'était jamais enregistré.
    const entrepotIds = new Set(
      counted
        .map(l => items.find(i => i.id === l.stock_id)?.entrepot_id)
        .filter((e): e is number => typeof e === 'number')
    );
    if (entrepotIds.size !== 1) {
      toast.error(
        'Impossible de rattacher les comptages à un entrepôt unique : ' +
        'chaque stock doit porter un entrepôt et ils doivent être identiques.'
      );
      return;
    }
    setSaving(true);
    try {
      const today = new Date().toISOString().slice(0, 10);
      const creres = await inventaireAPI.create({
        entrepot_id: [...entrepotIds][0],
        date_debut: today,
        type_inventaire: 'complet',
        notes: 'Inventaire physique saisi depuis le terminal magasin',
      });
      const inventaireId = creres.data.id;
      let comptees = 0;
      for (const line of counted) {
        await inventaireAPI.ajouterLigne(inventaireId, {
          stock_id: line.stock_id,
          quantite_comptee: line.realQty as number,
          commentaires: `Saisie physique : ${line.status} (écart ${line.variance})`,
        });
        comptees += 1;
      }
      toast.success(
        `Inventaire ${creres.data.numero_inventaire} : ${comptees} comptage(s) enregistré(s). ` +
        'Validez l\'inventaire côté magasin avancé pour ajuster le stock et journaliser les écarts.'
      );
      setCounts(new Map());
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(
        typeof detail === 'string' ? detail : 'Erreur soumission inventaire'
      );
    } finally {
      setSaving(false);
    }
  };

  const STATUS_STYLES: Record<string, string> = {
    match: 'bg-emerald-500/10 text-emerald-400',
    shortage: 'bg-red-500/10 text-red-400',
    overage: 'bg-amber-500/10 text-amber-400',
    pending: 'bg-slate-500/10 text-slate-400',
  };

  return (
    <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-white animate-in fade-in duration-300">
      <Link href="/magasin/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-4">
        <ArrowLeft className="w-4 h-4" /> Retour au Dashboard
      </Link>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-black flex items-center gap-3">
            <ClipboardCheck className="w-7 h-7 text-emerald-400" />
            Saisie Inventaire Physique
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            {computedLines.length} article(s) &#8212; {counted.length} compté(s) &#8212; {pending} en attente
          </p>
        </div>
        <button
          onClick={handleSubmit}
          disabled={counted.length === 0 || saving}
          className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 rounded-xl text-sm font-bold disabled:opacity-50 transition-colors"
        >
          <Save className="w-4 h-4" />
          {saving ? 'Soumission…' : 'Soumettre'}
        </button>
      </div>

      <div className="relative mb-4 max-w-md">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Code, désignation, emplacement…"
          className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
        />
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Chargement…</div>
      ) : computedLines.length === 0 ? (
        <div className="text-center py-12 bg-slate-900 border border-slate-800 rounded-2xl">
          <ClipboardCheck className="w-12 h-12 mx-auto text-slate-600 mb-3" />
          <p className="text-slate-400">Aucun article en stock</p>
        </div>
      ) : (
        <div className="overflow-x-auto bg-slate-900 border border-slate-800 rounded-2xl">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-xs tracking-wider">
                <th className="py-3 px-3">Emplacement</th>
                <th className="py-3 px-3">Code</th>
                <th className="py-3 px-3">Désignation</th>
                <th className="py-3 px-3 text-right">Qté Sys.</th>
                <th className="py-3 px-3 text-center">Qté Réelle</th>
                <th className="py-3 px-3 text-right">Écart</th>
                <th className="py-3 px-3 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {computedLines.map((line, idx) => (
                <tr key={line.stock_id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2 px-3 text-slate-400 font-mono text-xs">{line.location}</td>
                  <td className="py-2 px-3 font-mono text-emerald-400 text-xs">{line.code}</td>
                  <td className="py-2 px-3 max-w-[200px] truncate">{line.description}</td>
                  <td className="py-2 px-3 text-right font-mono">{line.systemQty.toLocaleString()} {line.uom}</td>
                  <td className="py-2 px-3 text-center">
                    <input
                      type="number"
                      value={line.realQty ?? ''}
                      onChange={(e) => {
                        const v = e.target.value === '' ? null : parseFloat(e.target.value);
                        setRealQty(line.stock_id, v);
                      }}
                      className="w-20 px-2 py-1 bg-slate-800 border border-slate-600 rounded text-center text-sm font-mono focus:outline-none focus:border-emerald-500"
                      placeholder="—"
                    />
                  </td>
                  <td className="py-2 px-3 text-right font-mono">
                    {line.variance !== null ? (
                      <span className={line.variance > 0 ? 'text-amber-400' : line.variance < 0 ? 'text-red-400' : 'text-emerald-400'}>
                        {line.variance > 0 ? '+' : ''}{line.variance.toLocaleString()}
                      </span>
                    ) : '-'}
                  </td>
                  <td className="py-2 px-3 text-center">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${STATUS_STYLES[line.status]}`}>
                      {line.status === 'pending' ? '—' : line.status}
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
