'use client';

import React, { useEffect, useState } from 'react';
import { deepAPI } from '@/lib/api-client';
import { RefreshCw } from 'lucide-react';
import Link from 'next/link';

type Rapprochement = {
  id: number;
  reference: string;
  compte_banque?: string | null;
  periode_debut?: string | null;
  periode_fin?: string | null;
  solde_banque_xaf?: number | null;
  solde_compta_xaf?: number | null;
  ecart_xaf?: number | null;
  nb_lignes_pointees?: number | null;
  statut?: string | null;
};

type Budget = {
  id: number;
  reference: string;
  centre_cout?: string | null;
  exercice?: number | null;
  budget_prevu_xaf?: number | null;
  consomme_xaf?: number | null;
  engagement_xaf?: number | null;
  ecart_pct?: number | null;
  statut?: string | null;
};

const fmt = (n?: number | null) => (n === null || n === undefined ? '—' : n.toLocaleString('fr-FR'));

export default function RapprochementsPage() {
  const [rappro, setRappro] = useState<Rapprochement[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(true);
  const [formR, setFormR] = useState({ reference: '', compte_banque: '', solde_banque_xaf: '', solde_compta_xaf: '', ecart_xaf: '' });
  const [formB, setFormB] = useState({ reference: '', centre_cout: '', exercice: new Date().getFullYear().toString(), budget_prevu_xaf: '', consomme_xaf: '' });
  const [msg, setMsg] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const [r, b] = await Promise.all([deepAPI.getBankReconciliations(), deepAPI.getBudgetControls()]);
      const rd = (r.data ?? r) as Rapprochement[] | { items?: Rapprochement[] };
      const bd = (b.data ?? b) as Budget[] | { items?: Budget[] };
      setRappro(Array.isArray(rd) ? rd : (rd.items ?? []));
      setBudgets(Array.isArray(bd) ? bd : (bd.items ?? []));
    } catch { /* endpoints peuvent être vides */ }
    setLoading(false);
  };
  useEffect(() => { load(); }, []);

  const submitR = async (e: React.FormEvent) => {
    e.preventDefault(); setMsg(null);
    try {
      await deepAPI.createBankReconciliation({
        reference: formR.reference,
        compte_banque: formR.compte_banque || undefined,
        solde_banque_xaf: formR.solde_banque_xaf ? Number(formR.solde_banque_xaf) : undefined,
        solde_compta_xaf: formR.solde_compta_xaf ? Number(formR.solde_compta_xaf) : undefined,
        ecart_xaf: formR.ecart_xaf ? Number(formR.ecart_xaf) : undefined,
      });
      setMsg('Rapprochement enregistré.'); setFormR({ reference: '', compte_banque: '', solde_banque_xaf: '', solde_compta_xaf: '', ecart_xaf: '' }); load();
    } catch (err: unknown) { setMsg(err instanceof Error ? err.message : 'Erreur'); }
  };

  const submitB = async (e: React.FormEvent) => {
    e.preventDefault(); setMsg(null);
    try {
      await deepAPI.createBudgetControl({
        reference: formB.reference,
        centre_cout: formB.centre_cout || undefined,
        exercice: Number(formB.exercice) || undefined,
        budget_prevu_xaf: formB.budget_prevu_xaf ? Number(formB.budget_prevu_xaf) : undefined,
        consomme_xaf: formB.consomme_xaf ? Number(formB.consomme_xaf) : undefined,
      });
      setMsg('Contrôle budgétaire enregistré.'); setFormB({ reference: '', centre_cout: '', exercice: new Date().getFullYear().toString(), budget_prevu_xaf: '', consomme_xaf: '' }); load();
    } catch (err: unknown) { setMsg(err instanceof Error ? err.message : 'Erreur'); }
  };

  return (
    <div className="p-6 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/comptabilite-ohada/dashboard" className="text-sm text-gray-400 hover:text-gray-600">← Comptabilité OHADA</Link>
          <h1 className="text-2xl font-bold mt-1">Rapprochements & contrôle budgétaire</h1>
        </div>
        <button onClick={load} className="flex items-center gap-2 px-3 py-2 text-sm border rounded-lg hover:bg-gray-50">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Actualiser
        </button>
      </div>
      {msg && <p className="text-sm text-blue-700">{msg}</p>}

      <section>
        <h2 className="text-lg font-semibold mb-3">Rapprochements bancaires</h2>
        <form onSubmit={submitR} className="bg-white border rounded-xl p-5 shadow-sm grid grid-cols-6 gap-3 items-end mb-4">
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Référence *</span>
            <input required value={formR.reference} onChange={(e) => setFormR({ ...formR, reference: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Compte banque</span>
            <input value={formR.compte_banque} onChange={(e) => setFormR({ ...formR, compte_banque: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Solde banque XAF</span>
            <input type="number" value={formR.solde_banque_xaf} onChange={(e) => setFormR({ ...formR, solde_banque_xaf: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Solde compta XAF</span>
            <input type="number" value={formR.solde_compta_xaf} onChange={(e) => setFormR({ ...formR, solde_compta_xaf: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Écart XAF</span>
            <input type="number" value={formR.ecart_xaf} onChange={(e) => setFormR({ ...formR, ecart_xaf: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">Créer</button>
        </form>
        <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs text-gray-500">
              <tr><th className="px-4 py-3">Référence</th><th className="px-4 py-3">Compte</th><th className="px-4 py-3">Solde banque</th><th className="px-4 py-3">Solde compta</th><th className="px-4 py-3">Écart</th><th className="px-4 py-3">Statut</th></tr>
            </thead>
            <tbody>
              {rappro.map((r) => (
                <tr key={r.id} className="border-t">
                  <td className="px-4 py-2 font-medium">{r.reference}</td>
                  <td className="px-4 py-2">{r.compte_banque ?? '—'}</td>
                  <td className="px-4 py-2">{fmt(r.solde_banque_xaf)}</td>
                  <td className="px-4 py-2">{fmt(r.solde_compta_xaf)}</td>
                  <td className={`px-4 py-2 font-medium ${r.ecart_xaf ? 'text-red-600' : 'text-green-700'}`}>{fmt(r.ecart_xaf)}</td>
                  <td className="px-4 py-2">{r.statut ?? '—'}</td>
                </tr>
              ))}
              {!loading && rappro.length === 0 && <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">Aucun rapprochement</td></tr>}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Contrôle budgétaire</h2>
        <form onSubmit={submitB} className="bg-white border rounded-xl p-5 shadow-sm grid grid-cols-6 gap-3 items-end mb-4">
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Référence *</span>
            <input required value={formB.reference} onChange={(e) => setFormB({ ...formB, reference: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Centre de coût</span>
            <input value={formB.centre_cout} onChange={(e) => setFormB({ ...formB, centre_cout: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Exercice</span>
            <input type="number" value={formB.exercice} onChange={(e) => setFormB({ ...formB, exercice: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Budget prévu XAF</span>
            <input type="number" value={formB.budget_prevu_xaf} onChange={(e) => setFormB({ ...formB, budget_prevu_xaf: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Consommé XAF</span>
            <input type="number" value={formB.consomme_xaf} onChange={(e) => setFormB({ ...formB, consomme_xaf: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">Créer</button>
        </form>
        <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs text-gray-500">
              <tr><th className="px-4 py-3">Référence</th><th className="px-4 py-3">Centre de coût</th><th className="px-4 py-3">Exercice</th><th className="px-4 py-3">Prévu</th><th className="px-4 py-3">Consommé</th><th className="px-4 py-3">Écart %</th><th className="px-4 py-3">Statut</th></tr>
            </thead>
            <tbody>
              {budgets.map((b) => (
                <tr key={b.id} className="border-t">
                  <td className="px-4 py-2 font-medium">{b.reference}</td>
                  <td className="px-4 py-2">{b.centre_cout ?? '—'}</td>
                  <td className="px-4 py-2">{b.exercice ?? '—'}</td>
                  <td className="px-4 py-2">{fmt(b.budget_prevu_xaf)}</td>
                  <td className="px-4 py-2">{fmt(b.consomme_xaf)}</td>
                  <td className={`px-4 py-2 font-medium ${b.ecart_pct && b.ecart_pct > 0 ? 'text-red-600' : 'text-green-700'}`}>{b.ecart_pct ?? '—'} %</td>
                  <td className="px-4 py-2">{b.statut ?? '—'}</td>
                </tr>
              ))}
              {!loading && budgets.length === 0 && <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">Aucun contrôle budgétaire</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
