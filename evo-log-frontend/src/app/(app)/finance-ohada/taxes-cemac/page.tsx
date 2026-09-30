'use client';

import React, { useEffect, useState } from 'react';
import {
  ShieldCheck, Download, CheckCircle2, AlertTriangle, RefreshCw,
} from 'lucide-react';
import { goodsDeclarationAPI } from '@/lib/api-client';
import { exportToCSV } from '@/lib/export';
import { toast } from 'sonner';

interface DumItem {
  id: number;
  numero_dum: string;
  marchandise?: string | null;
  nomenclature?: string | null;
  regime_douanier?: string | null;
  date_depot?: string | null;
  date_validation?: string | null;
  valeur_douane_xaf?: number | null;
  droits_douane?: number | null;
  tva?: number | null;
  montant_total?: number | null;
  statut?: string | null;
  reference_sydonia?: string | null;
}

const xaf = (n?: number | null) => `${Math.round(n || 0).toLocaleString()} XAF`;

const isCurrentMonth = (iso?: string | null) => {
  if (!iso) return false;
  const d = new Date(iso);
  const now = new Date();
  if (Number.isNaN(d.getTime())) return false;
  return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
};

const statutBadge = (statut?: string | null) => {
  switch (statut) {
    case 'liquidé':
      return { label: 'Liquidée', cls: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' };
    case 'valide':
      return { label: 'Validée', cls: 'bg-blue-500/10 text-blue-400 border-blue-500/20' };
    default:
      return { label: 'En attente', cls: 'bg-amber-500/10 text-amber-400 border-amber-500/20' };
  }
};

export default function FinanceOhadaTaxesCemac() {
  const [dums, setDums] = useState<DumItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await goodsDeclarationAPI.getAll({ limit: 500 });
      const items = res.data?.items;
      setDums(Array.isArray(items) ? items : []);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Données douanières indisponibles.');
      setDums([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  // Indicateurs derives UNIQUEMENT des DUM reellement enregistrees.
  const pending = dums.filter(d => d.statut !== 'liquidé');
  const totalEnAttente = pending.reduce((acc, d) => acc + (d.montant_total || 0), 0);

  const moisCourant = new Date().toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
  const liquidesMois = dums.filter(d => d.statut === 'liquidé' && isCurrentMonth(d.date_validation || d.date_depot));
  const droitsLiquidesMois = liquidesMois.reduce((acc, d) => acc + (d.droits_douane || 0), 0);

  const sydoniaReelles = dums.filter(d => d.reference_sydonia).length;

  const exporterBordereau = () => {
    if (!dums.length) { toast.error('Aucune déclaration à exporter.'); return; }
    exportToCSV(dums.map(d => ({
      numero_dum: d.numero_dum,
      marchandise: d.marchandise || '',
      code_sh: d.nomenclature || '',
      regime: d.regime_douanier || '',
      valeur_douane_xaf: Math.round(d.valeur_douane_xaf || 0),
      droits_douane_xaf: Math.round(d.droits_douane || 0),
      tva_xaf: Math.round(d.tva || 0),
      total_xaf: Math.round(d.montant_total || 0),
      statut: d.statut || '',
      reference_sydonia: d.reference_sydonia || 'non transmise',
    })), 'bordereau-declarations-douanieres');
    toast.success('Bordereau exporté depuis les DUM enregistrées.');
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-emerald-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Réglementation Fiscale &amp; Douanière
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KFIN_TAX
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <ShieldCheck className="w-8 h-8 text-emerald-400" />
            Fiscalité CEMAC &amp; Douanes
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Droits &amp; taxes consolidés depuis les déclarations (DUM) réellement enregistrées dans EVO-LOG.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={load}
            className="px-3 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-xl flex items-center gap-2 border border-slate-700 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button
            onClick={exporterBordereau}
            className="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-emerald-500/25 transition-all cursor-pointer"
          >
            <Download className="w-4 h-4" /> Bordereau Fiscal
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Droits &amp; Taxes en attente</div>
          <div className="text-2xl font-black text-amber-400 font-mono">
            {loading ? '' : xaf(totalEnAttente)}
          </div>
          <div className="text-[11px] text-slate-400 mt-2">
            {pending.length} déclaration{pending.length > 1 ? 's' : ''} non liquidée{pending.length > 1 ? 's' : ''} (estimation EVO-LOG)
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Droits douaniers liquidés ({moisCourant})</div>
          <div className="text-2xl font-black text-slate-100 font-mono">
            {loading ? '' : xaf(droitsLiquidesMois)}
          </div>
          <div className="text-[11px] text-slate-400 mt-2">
            {liquidesMois.length} DUM liquidée{liquidesMois.length > 1 ? 's' : ''} ce mois
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Télétransmission SYDONIA</div>
          <div className="text-2xl font-black text-slate-100 font-mono">
            {loading ? '' : `${sydoniaReelles} / ${dums.length}`}
          </div>
          <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            DUM disposant d&apos;une référence SYDONIA réelle
          </div>
        </div>
      </div>

      {/* Table Fiscalite */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">N° DUM</th>
                <th className="py-3.5 px-4">Marchandise / Code SH</th>
                <th className="py-3.5 px-4 text-right">Base en douane</th>
                <th className="py-3.5 px-4 text-right">Total droits &amp; taxes</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
                <th className="py-3.5 px-4">Réf. SYDONIA</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-12 text-center text-slate-500">Chargement des déclarations…</td>
                </tr>
              ) : error ? (
                <tr>
                  <td colSpan={6} className="p-12 text-center">
                    <AlertTriangle className="w-12 h-12 text-amber-500/40 mx-auto mb-3" />
                    <h3 className="font-semibold text-slate-100 text-base">Données indisponibles</h3>
                    <p className="text-xs text-slate-400 mt-1">{error}</p>
                    <button onClick={load} className="mt-4 px-4 py-2 text-xs font-bold rounded-xl border border-slate-700 text-slate-200 hover:bg-slate-800 transition-colors">
                      Réessayer
                    </button>
                  </td>
                </tr>
              ) : dums.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-12 text-center">
                    <CheckCircle2 className="w-12 h-12 text-slate-500/40 mx-auto mb-3" />
                    <h3 className="font-semibold text-slate-100 text-base">Aucune déclaration en douane enregistrée</h3>
                    <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                      Les droits et taxes apparaîtront ici dès que des DUM auront été saisies dans EVO-LOG.
                    </p>
                  </td>
                </tr>
              ) : (
                dums.map(d => {
                  const badge = statutBadge(d.statut);
                  return (
                    <tr key={d.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3.5 px-4 font-bold text-emerald-400">{d.numero_dum}</td>
                      <td className="py-3.5 px-4 font-sans">
                        <div className="text-slate-100 font-semibold">{d.marchandise || ''}</div>
                        <div className="text-[11px] text-slate-500">{d.nomenclature || 'code SH non renseigné'}</div>
                      </td>
                      <td className="py-3.5 px-4 text-right text-slate-400">{xaf(d.valeur_douane_xaf)}</td>
                      <td className="py-3.5 px-4 text-right font-bold text-slate-100">{xaf(d.montant_total)}</td>
                      <td className="py-3.5 px-4 text-center">
                        <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${badge.cls}`}>{badge.label}</span>
                      </td>
                      <td className="py-3.5 px-4 text-[11px]">
                        {d.reference_sydonia
                          ? <span className="text-emerald-400">{d.reference_sydonia}</span>
                          : <span className="text-slate-500">non transmise</span>}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-[11px] text-slate-500 flex items-start gap-2">
        <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5 text-amber-400" />
        Les montants affichés sont des estimations calculées dans EVO-LOG. Ils ne constituent pas un acte
        réglementaire : seuls les visuels DGI / SYDONIA (référence réelle indiquée ci-dessus) font foi. Une DUM
        sans référence SYDONIA n&apos;a pas été télétransmise ni acquittée.
      </p>
    </div>
  );
}
