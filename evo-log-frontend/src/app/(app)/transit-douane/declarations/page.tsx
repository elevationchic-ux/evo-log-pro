'use client';

import React, { useEffect, useState } from 'react';
import {
  FileText, Search, AlertTriangle, RefreshCw, Database,
} from 'lucide-react';
import { goodsDeclarationAPI } from '@/lib/api-client';

interface DumItem {
  id: number;
  numero_dum: string;
  type_operation: string;
  regime_douanier: string;
  bureau_douane: string | null;
  date_depot: string | null;
  declarant: string | null;
  importateur: string | null;
  marchandise: string | null;
  nomenclature: string | null;
  valeur_douane_xaf: number | null;
  droits_douane: number | null;
  tva: number | null;
  montant_total: number | null;
  statut: string;
  reference_sydonia: string | null;
}

// Statut réel renvoyé par le backend : 'en_attente' | 'valide' | 'liquidé'.
const STATUT_STYLES: Record<string, string> = {
  en_attente: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
  valide: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
  'liquidé': 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
};
const STATUT_LABELS: Record<string, string> = {
  en_attente: 'En attente',
  valide: 'Validée',
  'liquidé': 'Liquidée',
};

function xaf(n: number | null | undefined): string {
  if (n === null || n === undefined) return '';
  return Math.round(n).toLocaleString('fr-FR');
}

function dateCourte(iso: string | null): string {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString('fr-FR');
}

export default function TransitDouaneDeclarations() {
  const [items, setItems] = useState<DumItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const charger = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await goodsDeclarationAPI.getAll({ limit: 500 });
      setItems(res.data.items ?? []);
    } catch {
      setItems([]);
      setError('Données indisponibles. Vérifiez votre connexion ou réessayez.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    charger();
  }, []);

  const filtered = items.filter(d => {
    const q = searchQuery.toLowerCase();
    return (
      d.numero_dum.toLowerCase().includes(q) ||
      (d.importateur ?? '').toLowerCase().includes(q) ||
      (d.marchandise ?? '').toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-cyan-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              Déclarations en Douane (DUM)
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wider uppercase bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1.5">
              <Database className="w-3 h-3" /> Source : déclarations enregistrées
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <FileText className="w-8 h-8 text-cyan-400" />
            Déclarations DUM Import / Export / Transit
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Déclarations uniques de marchandises réellement enregistrées. Liquidation estimative
            tant que la télétransmission SYDONIA/ASYCUDA n&apos;est pas connectée.
          </p>
        </div>
      </div>

      {/* Table DUM */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher n° DUM, importateur ou marchandise..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>
        </div>

        {loading ? (
          <div className="p-10 text-center text-slate-400 text-sm">Chargement des déclarations…</div>
        ) : error ? (
          <div className="p-10 text-center space-y-3">
            <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
            <p className="text-sm text-slate-300">{error}</p>
            <button
              onClick={charger}
              className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-bold"
            >
              <RefreshCw className="w-4 h-4" /> Réessayer
            </button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-10 text-center space-y-2">
            <FileText className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-400">
              {items.length === 0
                ? 'Aucune déclaration DUM enregistrée.'
                : 'Aucune déclaration ne correspond à cette recherche.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider bg-slate-950">
                  <th className="py-3.5 px-4">N° DUM & Régime</th>
                  <th className="py-3.5 px-4">Importateur</th>
                  <th className="py-3.5 px-4">Marchandise (SH)</th>
                  <th className="py-3.5 px-4 text-right">Valeur douane (XAF)</th>
                  <th className="py-3.5 px-4 text-right">Droits & taxes</th>
                  <th className="py-3.5 px-4">Dépôt</th>
                  <th className="py-3.5 px-4 text-center">Statut</th>
                  <th className="py-3.5 px-4">Réf. SYDONIA</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {filtered.map(d => (
                  <tr key={d.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-cyan-400">{d.numero_dum}</div>
                      <div className="text-[11px] text-slate-400 font-sans">{d.regime_douanier}</div>
                    </td>
                    <td className="py-3.5 px-4 font-sans text-slate-100 font-semibold">{d.importateur ?? ''}</td>
                    <td className="py-3.5 px-4 font-sans text-slate-300 max-w-[220px]">
                      <div className="truncate">{d.marchandise ?? ''}</div>
                      <div className="text-[11px] text-slate-500">{d.nomenclature ?? ''}</div>
                    </td>
                    <td className="py-3.5 px-4 text-right font-bold text-slate-200">{xaf(d.valeur_douane_xaf)}</td>
                    <td className="py-3.5 px-4 text-right font-bold text-red-400">{xaf(d.montant_total)}</td>
                    <td className="py-3.5 px-4 text-slate-400">{dateCourte(d.date_depot)}</td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${STATUT_STYLES[d.statut] ?? 'bg-slate-800 text-slate-400 border border-slate-700'}`}>
                        {STATUT_LABELS[d.statut] ?? d.statut}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {d.reference_sydonia ? (
                        <span className="text-emerald-400 font-mono">{d.reference_sydonia}</span>
                      ) : (
                        <span className="text-slate-500">non transmise</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
