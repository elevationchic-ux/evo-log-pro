'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { ClipboardList, Plus, RefreshCw, Calculator, Landmark } from 'lucide-react';
import { apiClient, apiUrl } from '@/lib/api-client';
import { toast } from 'sonner';

interface Inventaire {
  id: number;
  numero_inventaire: string;
  entrepot_id: number;
  date_debut: string;
  date_fin?: string;
  type_inventaire?: string;
  statut: string;
}

interface Valorisation {
  inventaire_id: number;
  numero_inventaire: string;
  lignes_avec_ecart: number;
  impact_total_xaf: number;
  details: {
    ligne_id: number; stock_id: number; code_article: string; designation: string;
    ecart: number; prix_unitaire: number; impact_xaf: number;
  }[];
}

const fmt = (v: number | undefined) => Number(v || 0).toLocaleString('fr-FR');

export default function InventairesPage() {
  const [items, setItems] = useState<Inventaire[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ entrepot_id: '', type_inventaire: 'cyclique', date_debut: new Date().toISOString().slice(0, 10), date_fin: '', notes: '' });
  const [valorisation, setValorisation] = useState<Valorisation | null>(null);

  const charger = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(apiUrl('/magasin-avance/inventaires'));
      setItems(Array.isArray(res.data) ? res.data : []);
    } catch { toast.error('Impossible de charger les inventaires'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  const creer = async (ev: React.FormEvent) => {
    ev.preventDefault();
    try {
      await apiClient.post(apiUrl('/magasin-avance/inventaires'), {
        ...form, entrepot_id: Number(form.entrepot_id),
        date_fin: form.date_fin || null, notes: form.notes || null,
      });
      toast.success('Inventaire ouvert');
      setShowForm(false);
      charger();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur création');
    }
  };

  const voirValorisation = async (id: number) => {
    try {
      const res = await apiClient.get(apiUrl(`/magasin-avance/inventaires/${id}/valorisation-ecarts`));
      setValorisation(res.data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Valorisation indisponible');
    }
  };

  const ecrireComptable = async (inv: Inventaire) => {
    const dateEcriture = window.prompt('Date d\'écriture (AAAA-MM-JJ) :', new Date().toISOString().slice(0, 10));
    if (!dateEcriture) return;
    const stocks = window.prompt('Compte de stocks (ex. 371) :', '371');
    if (!stocks) return;
    const variation = window.prompt('Compte de variation de stocks (ex. 6031) :', '6031');
    if (!variation) return;
    try {
      const res = await apiClient.post(apiUrl(`/magasin-avance/inventaires/${inv.id}/ecriture-ecarts`), null, {
        params: { date_ecriture: dateEcriture, compte_stocks: stocks, compte_variation: variation },
      });
      toast.success(`Écriture ${res.data.montant.toLocaleString('fr-FR')} XAF comptabilisée (${res.data.sens}).`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur écriture');
    }
  };

  const input = 'w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-amber-500 focus:outline-none min-h-[44px]';
  const label = 'block text-xs font-medium text-slate-400 mb-1';

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 md:p-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-xl font-semibold text-slate-100">
            <ClipboardList className="h-6 w-6 text-amber-400" /> Inventaires tournants
          </h1>
          <p className="text-sm text-slate-400">Comptage cyclique, écarts valorisés et ajustement comptable.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={charger} className="inline-flex min-h-[44px] items-center gap-2 rounded-lg border border-slate-700 px-4 text-sm text-slate-300 hover:bg-slate-800">
            <RefreshCw className="h-4 w-4" /> Actualiser
          </button>
          <button onClick={() => setShowForm(!showForm)} className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-amber-500 px-4 text-sm font-medium text-slate-950 hover:bg-amber-400">
            <Plus className="h-4 w-4" /> Nouvel inventaire
          </button>
        </div>
      </header>

      {showForm && (
        <form onSubmit={creer} className="rounded-xl border border-slate-700 bg-slate-900/50 p-4">
          <div className="grid gap-4 md:grid-cols-4">
            <div><label className={label}>Entrepôt ID *</label><input required type="number" className={input} value={form.entrepot_id} onChange={e => setForm({ ...form, entrepot_id: e.target.value })} /></div>
            <div><label className={label}>Type</label>
              <select className={input} value={form.type_inventaire} onChange={e => setForm({ ...form, type_inventaire: e.target.value })}>
                <option value="cyclique">Cyclique</option><option value="partiel">Partiel</option><option value="complet">Complet</option>
              </select>
            </div>
            <div><label className={label}>Début *</label><input required type="date" className={input} value={form.date_debut} onChange={e => setForm({ ...form, date_debut: e.target.value })} /></div>
            <div><label className={label}>Fin prévue</label><input type="date" className={input} value={form.date_fin} onChange={e => setForm({ ...form, date_fin: e.target.value })} /></div>
          </div>
          <div className="mt-4 flex justify-end gap-2">
            <button type="button" onClick={() => setShowForm(false)} className="min-h-[44px] rounded-lg px-4 text-sm text-slate-400 hover:bg-slate-800">Annuler</button>
            <button type="submit" className="min-h-[44px] rounded-lg bg-amber-500 px-5 text-sm font-medium text-slate-950 hover:bg-amber-400">Ouvrir</button>
          </div>
        </form>
      )}

      <section className="overflow-x-auto rounded-xl border border-slate-700">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
            <tr>
              <th className="px-4 py-3">N°</th><th className="px-4 py-3">Type</th><th className="px-4 py-3">Entrepôt</th>
              <th className="px-4 py-3">Début</th><th className="px-4 py-3">Fin</th><th className="px-4 py-3">Statut</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {loading ? (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-500">Chargement…</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-500">Aucun inventaire.</td></tr>
            ) : items.map(inv => (
              <tr key={inv.id} className="hover:bg-slate-900/50">
                <td className="px-4 py-3 font-mono text-xs text-amber-300">{inv.numero_inventaire}</td>
                <td className="px-4 py-3 capitalize text-slate-300">{inv.type_inventaire || '—'}</td>
                <td className="px-4 py-3 text-slate-400">#{inv.entrepot_id}</td>
                <td className="px-4 py-3 text-slate-400">{inv.date_debut}</td>
                <td className="px-4 py-3 text-slate-400">{inv.date_fin || '—'}</td>
                <td className="px-4 py-3"><span className="rounded-full border border-slate-600 px-2 py-0.5 text-xs text-slate-300">{inv.statut}</span></td>
                <td className="px-4 py-3">
                  <div className="flex gap-1">
                    <button onClick={() => voirValorisation(inv.id)} className="inline-flex min-h-[44px] items-center gap-1 rounded-lg px-2 text-xs text-cyan-400 hover:bg-cyan-500/10" title="Valorisation écarts">
                      <Calculator className="h-4 w-4" /> Écarts
                    </button>
                    {inv.statut === 'termine' && (
                      <button onClick={() => ecrireComptable(inv)} className="inline-flex min-h-[44px] items-center gap-1 rounded-lg px-2 text-xs text-emerald-400 hover:bg-emerald-500/10" title="Écriture comptable">
                        <Landmark className="h-4 w-4" /> Comptabiliser
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {valorisation && (
        <section className="rounded-xl border border-cyan-500/30 bg-cyan-500/5 p-4">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-cyan-300">
              Écarts valorisés — {valorisation.numero_inventaire} · impact {fmt(valorisation.impact_total_xaf)} XAF
            </h2>
            <button onClick={() => setValorisation(null)} className="text-xs text-slate-400 hover:text-white">Fermer</button>
          </div>
          <div className="max-h-72 overflow-y-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-500"><tr><th className="px-2 py-1">Article</th><th className="px-2 py-1 text-right">Écart</th><th className="px-2 py-1 text-right">P.U.</th><th className="px-2 py-1 text-right">Impact</th></tr></thead>
              <tbody className="divide-y divide-slate-800 font-mono">
                {valorisation.details.filter(d => d.ecart !== 0).map(d => (
                  <tr key={d.ligne_id}>
                    <td className="px-2 py-1">{d.code_article} — {d.designation}</td>
                    <td className={`px-2 py-1 text-right ${d.ecart > 0 ? 'text-emerald-400' : 'text-red-400'}`}>{d.ecart}</td>
                    <td className="px-2 py-1 text-right">{fmt(d.prix_unitaire)}</td>
                    <td className="px-2 py-1 text-right font-bold">{fmt(d.impact_xaf)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
