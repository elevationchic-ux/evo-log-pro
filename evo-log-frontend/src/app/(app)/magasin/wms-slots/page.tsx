'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { LayoutGrid, ArrowLeft, Package, Search } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api-client';

interface SlotEntry {
  emplacement: string;
  articles: { code: string; designation: string; quantite: number; unite: string }[];
  total_weight: number;
}

export default function WmsSlotsPage() {
  const [slots, setSlots] = useState<SlotEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchSlots = useCallback(async () => {
    try {
      const params: Record<string, unknown> = { limit: 500 };
      if (search) params.q = search;
      const res: any = await apiClient.get('/api/v1/magasin/stocks/search', { params });
      const body = res.data ?? res;
      const items: any[] = body.items || [];

      // Group by emplacement
      const map = new Map<string, SlotEntry>();
      for (const item of items) {
        const loc = item.emplacement || 'NON ASSIGNÉ';
        if (!map.has(loc)) {
          map.set(loc, { emplacement: loc, articles: [], total_weight: 0 });
        }
        const entry = map.get(loc)!;
        entry.articles.push({
          code: item.code_article,
          designation: item.designation,
          quantite: item.quantite_disponible,
          unite: item.unite_mesure || 'U',
        });
        entry.total_weight += item.valeur || 0;
      }

      const sorted = [...map.values()].sort((a, b) => a.emplacement.localeCompare(b.emplacement));
      setSlots(sorted);
    } catch (err: any) {
      if (err?.response?.status === 501 || err?.response?.status === 404) {
        toast.warning('Module stocks/emplacements non configuré');
      } else {
        toast.error('Erreur chargement emplacements');
      }
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { fetchSlots(); }, [fetchSlots]);

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-white animate-in fade-in duration-300">
      <Link href="/magasin/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-4">
        <ArrowLeft className="w-4 h-4" /> Retour au Dashboard
      </Link>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-black flex items-center gap-3">
            <LayoutGrid className="w-7 h-7 text-purple-400" />
            Slots & Emplacements WMS
          </h1>
          <p className="text-sm text-slate-400 mt-1">{slots.length} emplacement(s) occupé(s)</p>
        </div>
      </div>

      <div className="relative mb-4 max-w-md">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Rechercher un emplacement ou article…"
          className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500"
        />
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Chargement…</div>
      ) : slots.length === 0 ? (
        <div className="text-center py-12 bg-slate-900 border border-slate-800 rounded-2xl">
          <LayoutGrid className="w-12 h-12 mx-auto text-slate-600 mb-3" />
          <p className="text-slate-400">Aucun emplacement avec du stock</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {slots.map((slot) => (
            <div key={slot.emplacement} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-purple-500/40 transition-colors">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-mono font-bold text-purple-400">{slot.emplacement}</h3>
                <span className="text-xs text-slate-500">{slot.articles.length} article(s)</span>
              </div>
              <div className="space-y-1.5">
                {slot.articles.slice(0, 5).map((a, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2 truncate">
                      <Package className="w-3 h-3 text-slate-500 shrink-0" />
                      <span className="truncate">{a.designation}</span>
                    </div>
                    <span className="font-mono text-slate-400 shrink-0 ml-2">{a.quantite} {a.unite}</span>
                  </div>
                ))}
                {slot.articles.length > 5 && (
                  <p className="text-xs text-slate-500 italic">+ {slot.articles.length - 5} autre(s)</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
