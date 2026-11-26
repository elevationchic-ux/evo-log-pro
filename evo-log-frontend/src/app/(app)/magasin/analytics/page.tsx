'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { TrendingUp, ArrowLeft, AlertTriangle, Package, BarChart2 } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import { magasinAPI } from '@/lib/api-client';

interface StockStatusBucket {
  statut: string;
  libelle: string;
  nb_articles: number;
  valeur: number;
}

interface Kpis {
  total_articles?: number;
  valeur_totale?: number;
  mouvements_jour?: number;
  [key: string]: unknown;
}

export default function AnalyticsPage() {
  const [statuses, setStatuses] = useState<StockStatusBucket[]>([]);
  const [totalArticles, setTotalArticles] = useState(0);
  const [kpis, setKpis] = useState<Kpis | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [statusRes, kpiRes] = await Promise.allSettled([
        magasinAPI.getStockStatuses(),
        magasinAPI.getKpis(),
      ]);
      if (statusRes.status === 'fulfilled') {
        const body = statusRes.value?.data ?? statusRes.value;
        setStatuses(body.statuses || []);
        setTotalArticles(body.total_articles || 0);
      }
      if (kpiRes.status === 'fulfilled') {
        const body = kpiRes.value?.data ?? kpiRes.value;
        setKpis(body);
      }
    } catch (err: any) {
      toast.error('Erreur chargement analytics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-white animate-in fade-in duration-300">
      <Link href="/magasin/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-4">
        <ArrowLeft className="w-4 h-4" /> Retour au Dashboard
      </Link>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-black flex items-center gap-3">
            <TrendingUp className="w-7 h-7 text-emerald-400" />
            Analytics Stock
          </h1>
          <p className="text-sm text-slate-400 mt-1">{totalArticles} article(s) actif(s) en stock</p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Chargement...</div>
      ) : (
        <>
          {/* KPI Cards */}
          {kpis && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                <p className="text-xs uppercase text-slate-400 mb-1">Total articles</p>
                <p className="text-3xl font-black text-white">{kpis.total_articles?.toLocaleString() || totalArticles}</p>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                <p className="text-xs uppercase text-slate-400 mb-1">Valeur stock</p>
                <p className="text-3xl font-black text-emerald-400">{kpis.valeur_totale ? `${(kpis.valeur_totale as number).toLocaleString()} FCFA` : '-'}</p>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                <p className="text-xs uppercase text-slate-400 mb-1">Mouvements / jour</p>
                <p className="text-3xl font-black text-sky-400">{kpis.mouvements_jour?.toLocaleString() || '-'}</p>
              </div>
            </div>
          )}

          {/* Stock Status Distribution */}
          <section>
            <h2 className="text-lg font-bold mb-3 flex items-center gap-2">
              <BarChart2 className="w-5 h-5 text-amber-400" />
              Répartition par statut de stock
            </h2>
            {statuses.length === 0 ? (
              <div className="text-center py-8 bg-slate-900 border border-slate-800 rounded-2xl">
                <Package className="w-10 h-10 mx-auto text-slate-600 mb-2" />
                <p className="text-slate-400 text-sm">Aucune donnée de stock disponible</p>
              </div>
            ) : (
              <div className="space-y-3">
                {statuses.map((s) => {
                  const pct = totalArticles > 0 ? Math.round((s.nb_articles / totalArticles) * 100) : 0;
                  const isAlerte = s.statut === 'rupture' || s.statut === 'bas';
                  return (
                    <div key={s.statut} className="flex items-center gap-4 bg-slate-900 border border-slate-800 rounded-xl p-4">
                      <div className={`w-24 text-sm font-bold ${isAlerte ? 'text-red-400' : 'text-slate-200'}`}>
                        {isAlerte && <AlertTriangle className="w-3.5 h-3.5 inline mr-1" />}
                        {s.libelle}
                      </div>
                      <div className="flex-1">
                        <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all ${
                              s.statut === 'rupture' ? 'bg-red-500' :
                              s.statut === 'bas' ? 'bg-amber-500' :
                              s.statut === 'excess' ? 'bg-purple-500' : 'bg-emerald-500'
                            }`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                      <div className="w-20 text-right font-mono text-sm text-slate-300">{s.nb_articles} art.</div>
                      <div className="w-28 text-right font-mono text-xs text-slate-400">{s.valeur.toLocaleString()} F</div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
