'use client';

import React, { useState } from 'react';
import { Wallet, Search } from 'lucide-react';
import { apiClient, apiUrl } from '@/lib/api-client';
import { toast } from 'sonner';

interface LignePaie {
  employe_id: number;
  mois_payes: number;
  salaire_brut: number;
  salaire_net: number;
  cnps_salarial: number;
  irgm: number;
  cnps_patronal: number;
  cout_total_employeur: number;
}

const fmt = (v: number | undefined) => Number(v || 0).toLocaleString('fr-FR');

export default function PaieRecapitulatifPage() {
  const [annee, setAnnee] = useState(new Date().getFullYear());
  const [lignes, setLignes] = useState<LignePaie[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const chercher = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(apiUrl('/rh-avance/paie-recapitulatif-annuel'), { params: { annee } });
      setLignes(Array.isArray(res.data) ? res.data : []);
      setSearched(true);
    } catch { toast.error('Récapitulatif indisponible'); }
    finally { setLoading(false); }
  };

  const totaux = lignes.reduce((acc, l) => ({
    brut: acc.brut + l.salaire_brut, net: acc.net + l.salaire_net,
    sal: acc.sal + l.cnps_salarial, pat: acc.pat + l.cnps_patronal,
    cout: acc.cout + l.cout_total_employeur,
  }), { brut: 0, net: 0, sal: 0, pat: 0, cout: 0 });

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 md:p-6">
      <header>
        <h1 className="flex items-center gap-2 text-xl font-semibold text-slate-100">
          <Wallet className="h-6 w-6 text-emerald-400" /> Récapitulatif annuel de paie
        </h1>
        <p className="text-sm text-slate-400">Cumuls par employé : brut, net, CNPS salarial, part patronale et coût employeur.</p>
      </header>

      <div className="flex items-center gap-2">
        <input type="number" min={2000} max={2100} value={annee} onChange={e => setAnnee(Number(e.target.value))}
          className="w-28 rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 min-h-[44px]" />
        <button onClick={chercher} disabled={loading}
          className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-emerald-600 px-5 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50">
          <Search className="h-4 w-4" /> {loading ? 'Chargement…' : `Exercice ${annee}`}
        </button>
      </div>

      {searched && (
        <section className="overflow-x-auto rounded-xl border border-slate-700">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
              <tr>
                <th className="px-4 py-3">Employé</th><th className="px-4 py-3 text-center">Mois</th>
                <th className="px-4 py-3 text-right">Brut</th><th className="px-4 py-3 text-right">Net</th>
                <th className="px-4 py-3 text-right">CNPS salar.</th><th className="px-4 py-3 text-right">IRGM</th>
                <th className="px-4 py-3 text-right">CNPS patron.</th><th className="px-4 py-3 text-right">Coût employeur</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {lignes.length === 0 ? (
                <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-500">Aucune fiche de paie pour {annee}.</td></tr>
              ) : lignes.map(l => (
                <tr key={l.employe_id} className="hover:bg-slate-900/50">
                  <td className="px-4 py-3 text-slate-200">Employé #{l.employe_id}</td>
                  <td className="px-4 py-3 text-center">{l.mois_payes}</td>
                  <td className="px-4 py-3 text-right">{fmt(l.salaire_brut)}</td>
                  <td className="px-4 py-3 text-right text-emerald-400">{fmt(l.salaire_net)}</td>
                  <td className="px-4 py-3 text-right">{fmt(l.cnps_salarial)}</td>
                  <td className="px-4 py-3 text-right">{fmt(l.irgm)}</td>
                  <td className="px-4 py-3 text-right">{fmt(l.cnps_patronal)}</td>
                  <td className="px-4 py-3 text-right font-bold text-slate-100">{fmt(l.cout_total_employeur)}</td>
                </tr>
              ))}
            </tbody>
            {lignes.length > 0 && (
              <tfoot className="bg-slate-900/80 font-bold">
                <tr className="text-slate-200">
                  <td className="px-4 py-3" colSpan={2}>TOTAL {annee}</td>
                  <td className="px-4 py-3 text-right">{fmt(totaux.brut)}</td>
                  <td className="px-4 py-3 text-right text-emerald-400">{fmt(totaux.net)}</td>
                  <td className="px-4 py-3 text-right">{fmt(totaux.sal)}</td>
                  <td className="px-4 py-3 text-right">—</td>
                  <td className="px-4 py-3 text-right">{fmt(totaux.pat)}</td>
                  <td className="px-4 py-3 text-right text-cyan-300">{fmt(totaux.cout)}</td>
                </tr>
              </tfoot>
            )}
          </table>
        </section>
      )}
    </div>
  );
}
