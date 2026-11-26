'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Building2, Plus, RefreshCw, CalendarClock, Landmark } from 'lucide-react';
import { apiClient, apiUrl } from '@/lib/api-client';
import { toast } from 'sonner';

interface Immobilisation {
  id: number;
  numero_immobilisation: string;
  designation: string;
  date_acquisition: string;
  valeur_acquisition: number;
  valeur_residuelle: number;
  duree_mois: number;
  compte_immobilisation: string;
  compte_amortissement: string;
  compte_dotation: string;
  statut?: string;
}

interface Echeance {
  periode: string;
  dotation: number;
  cumul_amortissement: number;
  net_comptable: number;
}

export default function ImmobilisationsPage() {
  const [items, setItems] = useState<Immobilisation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [echeancier, setEcheancier] = useState<{ id: number; lignes: Echeance[] } | null>(null);
  const [form, setForm] = useState({
    numero_immobilisation: '', designation: '', date_acquisition: '',
    valeur_acquisition: '', valeur_residuelle: '0', duree_mois: 60,
    compte_immobilisation: '215', compte_amortissement: '281', compte_dotation: '681',
  });

  const charger = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(apiUrl('/comptabilite-avance/immobilisations'));
      setItems(Array.isArray(res.data) ? res.data : res.data?.items || []);
    } catch { toast.error('Impossible de charger les immobilisations'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  const creer = async (ev: React.FormEvent) => {
    ev.preventDefault();
    try {
      await apiClient.post(apiUrl('/comptabilite-avance/immobilisations'), {
        ...form,
        valeur_acquisition: Number(form.valeur_acquisition),
        valeur_residuelle: Number(form.valeur_residuelle),
        duree_mois: Number(form.duree_mois),
      });
      toast.success('Immobilisation créée');
      setShowForm(false);
      charger();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur création');
    }
  };

  const voirEcheancier = async (id: number) => {
    try {
      const res = await apiClient.get(apiUrl(`/comptabilite-avance/immobilisations/${id}/echeancier`));
      setEcheancier({ id, lignes: Array.isArray(res.data) ? res.data : res.data?.echeancier || [] });
    } catch { toast.error('Échéancier indisponible'); }
  };

  const genererDotation = async (imm: Immobilisation) => {
    const periode = window.prompt('Période (AAAA-MM) :', new Date().toISOString().slice(0, 7));
    if (!periode) return;
    try {
      await apiClient.post(apiUrl(`/comptabilite-avance/immobilisations/${imm.id}/amortissement`), {
        date_ecriture: new Date().toISOString().slice(0, 10), periode,
      });
      toast.success(`Dotation ${periode} comptabilisée (681/${imm.compte_amortissement}).`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur dotation');
    }
  };

  const input = 'w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-violet-500 focus:outline-none min-h-[44px]';
  const label = 'block text-xs font-medium text-slate-400 mb-1';
  const fmt = (v: number) => Number(v || 0).toLocaleString('fr-FR');

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 md:p-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-xl font-semibold text-slate-100">
            <Building2 className="h-6 w-6 text-violet-400" /> Immobilisations amortissables
          </h1>
          <p className="text-sm text-slate-400">Registre SYSCOHADA — dotations automatiques 681/28x depuis le grand livre.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={charger} className="inline-flex min-h-[44px] items-center gap-2 rounded-lg border border-slate-700 px-4 text-sm text-slate-300 hover:bg-slate-800">
            <RefreshCw className="h-4 w-4" /> Actualiser
          </button>
          <button onClick={() => setShowForm(!showForm)} className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-violet-600 px-4 text-sm font-medium text-white hover:bg-violet-500">
            <Plus className="h-4 w-4" /> Nouvelle immobilisation
          </button>
        </div>
      </header>

      {showForm && (
        <form onSubmit={creer} className="rounded-xl border border-slate-700 bg-slate-900/50 p-4">
          <div className="grid gap-4 md:grid-cols-4">
            <div><label className={label}>N° immobilisation *</label><input required className={input} value={form.numero_immobilisation} onChange={e => setForm({ ...form, numero_immobilisation: e.target.value })} placeholder="IMM-001" /></div>
            <div className="md:col-span-2"><label className={label}>Désignation *</label><input required className={input} value={form.designation} onChange={e => setForm({ ...form, designation: e.target.value })} /></div>
            <div><label className={label}>Date acquisition *</label><input required type="date" className={input} value={form.date_acquisition} onChange={e => setForm({ ...form, date_acquisition: e.target.value })} /></div>
            <div><label className={label}>Valeur acquisition *</label><input required type="number" className={input} value={form.valeur_acquisition} onChange={e => setForm({ ...form, valeur_acquisition: e.target.value })} /></div>
            <div><label className={label}>Valeur résiduelle</label><input type="number" className={input} value={form.valeur_residuelle} onChange={e => setForm({ ...form, valeur_residuelle: e.target.value })} /></div>
            <div><label className={label}>Durée (mois)</label><input type="number" min={1} className={input} value={form.duree_mois} onChange={e => setForm({ ...form, duree_mois: Number(e.target.value) })} /></div>
            <div><label className={label}>Compte actif</label><input className={input} value={form.compte_immobilisation} onChange={e => setForm({ ...form, compte_immobilisation: e.target.value })} /></div>
            <div><label className={label}>Compte amortissement</label><input className={input} value={form.compte_amortissement} onChange={e => setForm({ ...form, compte_amortissement: e.target.value })} /></div>
            <div><label className={label}>Compte dotation</label><input className={input} value={form.compte_dotation} onChange={e => setForm({ ...form, compte_dotation: e.target.value })} /></div>
          </div>
          <div className="mt-4 flex justify-end gap-2">
            <button type="button" onClick={() => setShowForm(false)} className="min-h-[44px] rounded-lg px-4 text-sm text-slate-400 hover:bg-slate-800">Annuler</button>
            <button type="submit" className="min-h-[44px] rounded-lg bg-violet-600 px-5 text-sm font-medium text-white hover:bg-violet-500">Enregistrer</button>
          </div>
        </form>
      )}

      <section className="overflow-x-auto rounded-xl border border-slate-700">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
            <tr>
              <th className="px-4 py-3">N°</th><th className="px-4 py-3">Désignation</th>
              <th className="px-4 py-3 text-right">Valeur acq.</th><th className="px-4 py-3 text-right">Durée</th>
              <th className="px-4 py-3">Comptes</th><th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {loading ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-500">Chargement…</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-500">Aucune immobilisation.</td></tr>
            ) : items.map(imm => (
              <tr key={imm.id} className="hover:bg-slate-900/50">
                <td className="px-4 py-3 font-mono text-xs text-violet-300">{imm.numero_immobilisation}</td>
                <td className="px-4 py-3 text-slate-200">{imm.designation}</td>
                <td className="px-4 py-3 text-right text-slate-300">{fmt(imm.valeur_acquisition)} XAF</td>
                <td className="px-4 py-3 text-right text-slate-400">{imm.duree_mois} mois</td>
                <td className="px-4 py-3 font-mono text-xs text-slate-400">{imm.compte_immobilisation}/{imm.compte_amortissement}/{imm.compte_dotation}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-1">
                    <button onClick={() => voirEcheancier(imm.id)} className="inline-flex min-h-[44px] items-center gap-1 rounded-lg px-2 text-xs text-slate-300 hover:bg-slate-800" title="Échéancier">
                      <CalendarClock className="h-4 w-4" /> Échéancier
                    </button>
                    <button onClick={() => genererDotation(imm)} className="inline-flex min-h-[44px] items-center gap-1 rounded-lg px-2 text-xs text-emerald-400 hover:bg-emerald-500/10" title="Générer dotation">
                      <Landmark className="h-4 w-4" /> Dotation
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {echeancier && (
        <section className="rounded-xl border border-violet-500/30 bg-violet-500/5 p-4">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-violet-300">Échéancier — immobilisation #{echeancier.id}</h2>
            <button onClick={() => setEcheancier(null)} className="text-xs text-slate-400 hover:text-white">Fermer</button>
          </div>
          <div className="max-h-72 overflow-y-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-500"><tr><th className="px-2 py-1">Période</th><th className="px-2 py-1 text-right">Dotation</th><th className="px-2 py-1 text-right">Cumul</th><th className="px-2 py-1 text-right">Net comptable</th></tr></thead>
              <tbody className="divide-y divide-slate-800 font-mono">
                {echeancier.lignes.slice(0, 24).map(l => (
                  <tr key={l.periode}><td className="px-2 py-1">{l.periode}</td><td className="px-2 py-1 text-right">{fmt(l.dotation)}</td><td className="px-2 py-1 text-right">{fmt(l.cumul_amortissement)}</td><td className="px-2 py-1 text-right">{fmt(l.net_comptable)}</td></tr>
                ))}
              </tbody>
            </table>
            {echeancier.lignes.length > 24 && <p className="mt-2 text-xs text-slate-500">… {echeancier.lignes.length - 24} périodes supplémentaires</p>}
          </div>
        </section>
      )}
    </div>
  );
}
