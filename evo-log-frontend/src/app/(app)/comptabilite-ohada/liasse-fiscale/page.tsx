'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { FileSpreadsheet, Plus, RefreshCw, Eye } from 'lucide-react';
import { apiClient, apiUrl } from '@/lib/api-client';
import { toast } from 'sonner';

interface Liasse {
  id: number;
  annee: number;
  total_tva_collectee: number;
  total_tva_deductible: number;
  total_tva_a_payer: number;
  total_is: number;
  total_impots: number;
  nombre_declarations_tva: number;
  statut: string;
  detail_json?: string | null;
  created_at?: string;
}

interface DeclarationDetail {
  numero?: string;
  periode?: string;
  annee?: number;
  base_imposable?: number;
  tva_collectee?: number;
  tva_deductible?: number;
  tva_a_payer?: number;
  benefice_fiscal?: number;
  is_du?: number;
  is_a_payer?: number;
  statut?: string;
  [key: string]: unknown;
}

const fmt = (v: number | unknown) => Number(v || 0).toLocaleString('fr-FR');

export default function LiasseFiscalePage() {
  const [liasses, setLiasses] = useState<Liasse[]>([]);
  const [loading, setLoading] = useState(true);
  const [annee, setAnnee] = useState(new Date().getFullYear());
  const [detail, setDetail] = useState<{ liasse: Liasse; tva: DeclarationDetail[]; is: DeclarationDetail[] } | null>(null);

  const charger = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(apiUrl('/comptabilite-avance/liasse-fiscale'));
      setLiasses(Array.isArray(res.data) ? res.data : res.data?.items || []);
    } catch { toast.error('Impossible de charger les liasses'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  const generer = async () => {
    try {
      await apiClient.post(apiUrl('/comptabilite-avance/liasse-fiscale'), { annee });
      toast.success(`Liasse ${annee} générée depuis les déclarations réelles.`);
      charger();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur génération');
    }
  };

  const voirDetail = async (id: number) => {
    try {
      const res = await apiClient.get(apiUrl(`/comptabilite-avance/liasse-fiscale/${id}`));
      const l = res.data as Liasse;
      const parsed = l.detail_json ? JSON.parse(l.detail_json as unknown as string) : {};
      setDetail({ liasse: l, tva: parsed.declarations_tva || [], is: parsed.declarations_is || [] });
    } catch { toast.error('Détail indisponible'); }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 md:p-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-xl font-semibold text-slate-100">
            <FileSpreadsheet className="h-6 w-6 text-emerald-400" /> Liasse fiscale CEMAC
          </h1>
          <p className="text-sm text-slate-400">Consolidation TVA + IS depuis les déclarations réelles de l'exercice.</p>
        </div>
        <div className="flex items-center gap-2">
          <input type="number" min={2000} max={2100} value={annee} onChange={e => setAnnee(Number(e.target.value))}
            className="w-24 rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 min-h-[44px]" />
          <button onClick={generer} className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-emerald-600 px-4 text-sm font-medium text-white hover:bg-emerald-500">
            <Plus className="h-4 w-4" /> Générer {annee}
          </button>
          <button onClick={charger} className="inline-flex min-h-[44px] items-center gap-2 rounded-lg border border-slate-700 px-4 text-sm text-slate-300 hover:bg-slate-800">
            <RefreshCw className="h-4 w-4" /> Actualiser
          </button>
        </div>
      </header>

      <section className="overflow-x-auto rounded-xl border border-slate-700">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
            <tr>
              <th className="px-4 py-3">Exercice</th><th className="px-4 py-3 text-right">TVA collectée</th>
              <th className="px-4 py-3 text-right">TVA déductible</th><th className="px-4 py-3 text-right">TVA à payer</th>
              <th className="px-4 py-3 text-right">IS</th><th className="px-4 py-3 text-right">Total impôts</th>
              <th className="px-4 py-3">Statut</th><th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {loading ? (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-500">Chargement…</td></tr>
            ) : liasses.length === 0 ? (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-500">Aucune liasse — générez-la après avoir saisi les déclarations TVA/IS.</td></tr>
            ) : liasses.map(l => (
              <tr key={l.id} className="hover:bg-slate-900/50">
                <td className="px-4 py-3 font-bold text-slate-200">{l.annee}</td>
                <td className="px-4 py-3 text-right">{fmt(l.total_tva_collectee)}</td>
                <td className="px-4 py-3 text-right">{fmt(l.total_tva_deductible)}</td>
                <td className="px-4 py-3 text-right text-amber-300">{fmt(l.total_tva_a_payer)}</td>
                <td className="px-4 py-3 text-right">{fmt(l.total_is)}</td>
                <td className="px-4 py-3 text-right font-bold text-slate-100">{fmt(l.total_impots)}</td>
                <td className="px-4 py-3"><span className="rounded-full border border-slate-600 px-2 py-0.5 text-xs text-slate-300">{l.statut}</span></td>
                <td className="px-4 py-3 text-right">
                  <button onClick={() => voirDetail(l.id)} className="inline-flex min-h-[44px] items-center gap-1 rounded-lg px-2 text-xs text-slate-300 hover:bg-slate-800">
                    <Eye className="h-4 w-4" /> Détail
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {detail && (
        <section className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-emerald-300">Détail liasse {detail.liasse.annee}</h2>
            <button onClick={() => setDetail(null)} className="text-xs text-slate-400 hover:text-white">Fermer</button>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h3 className="mb-2 text-xs font-bold uppercase text-slate-400">Déclarations TVA ({detail.tva.length})</h3>
              <ul className="space-y-1 font-mono text-xs">
                {detail.tva.map((d, i) => (
                  <li key={i} className="flex justify-between rounded bg-slate-900/60 px-2 py-1">
                    <span>{d.numero || d.periode}</span>
                    <span>collectée {fmt(d.tva_collectee)} · à payer {fmt(d.tva_a_payer)} · {d.statut}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="mb-2 text-xs font-bold uppercase text-slate-400">Déclarations IS ({detail.is.length})</h3>
              <ul className="space-y-1 font-mono text-xs">
                {detail.is.map((d, i) => (
                  <li key={i} className="flex justify-between rounded bg-slate-900/60 px-2 py-1">
                    <span>{d.numero || `IS ${d.annee}`}</span>
                    <span>bénéfice {fmt(d.benefice_fiscal)} · IS {fmt(d.is_a_payer)} · {d.statut}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
