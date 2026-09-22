'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid, Search, Plus, Download, BookOpen,
  RefreshCw, X, Loader2
} from 'lucide-react';
import { toast } from 'sonner';

interface SYSCOHADAAccount {
  code: string;
  intitule: string;
  classe: number;
  type: 'ACTIF' | 'PASSIF' | 'CHARGE' | 'PRODUIT';
  nature: 'CENTRALISATEUR' | 'DETAIL' | 'AUXILIAIRE';
  sens: 'DEBITEUR' | 'CREDITEUR';
}

const SYSCOHADA_PLAN: SYSCOHADAAccount[] = [
  // Classe 1
  { code: '101100', intitule: 'Capital Social Souscrit non Amorti', classe: 1, type: 'PASSIF', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },
  { code: '111100', intitule: 'Réserve Légale', classe: 1, type: 'PASSIF', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },
  { code: '121100', intitule: 'Report à Nouveau Créditeur', classe: 1, type: 'PASSIF', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },
  { code: '131100', intitule: 'Résultat Net de l Exercice (Bénéfice)', classe: 1, type: 'PASSIF', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },
  { code: '161100', intitule: 'Emprunts auprès des Établissements de Crédit', classe: 1, type: 'PASSIF', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },

  // Classe 2
  { code: '211100', intitule: 'Frais de Développement & Logiciels Informatiques', classe: 2, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '241100', intitule: 'Matériel Automobile & Tracteurs Routiers', classe: 2, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '241200', intitule: 'Semi-Remorques & Plateaux Porte-Conteneurs', classe: 2, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '244100', intitule: 'Matériel de Manutention Quai (Reachstackers)', classe: 2, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '284100', intitule: 'Amortissement du Matériel de Transport', classe: 2, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },

  // Classe 3
  { code: '311100', intitule: 'Marchandises en Magasin Portuaire MAG3', classe: 3, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '321100', intitule: 'Matières Consommables & Pièces de Rechange Flotte', classe: 3, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },

  // Classe 4
  { code: '401100', intitule: 'Fournisseurs d Exploitation (Carburant, Pièces)', classe: 4, type: 'PASSIF', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },
  { code: '411100', intitule: 'Clients Nationaux & Transitaires CEMAC', classe: 4, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '422100', intitule: 'Personnel - Rémunérations Dues Net', classe: 4, type: 'PASSIF', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },
  { code: '431100', intitule: 'Sécurité Sociale (CNPS Cameroun)', classe: 4, type: 'PASSIF', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },
  { code: '443100', intitule: 'État - TVA Facturée sur Prestations (19.25%)', classe: 4, type: 'PASSIF', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },
  { code: '445200', intitule: 'État - TVA Récupérable sur Achats & Services', classe: 4, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },

  // Classe 5
  { code: '512100', intitule: 'Afriland First Bank Cameroun', classe: 5, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '512200', intitule: 'Société Générale Cameroun (SGC)', classe: 5, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '531100', intitule: 'Caisse Principale Siège Douala Port', classe: 5, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '571100', intitule: 'Comptes Mobile Money Entreprise (OM / MOMO)', classe: 5, type: 'ACTIF', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },

  // Classe 6
  { code: '601100', intitule: 'Achats de Carburants Flotte (Gasoil)', classe: 6, type: 'CHARGE', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '611100', intitule: 'Transports Consommés & Sous-traitance', classe: 6, type: 'CHARGE', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '624100', intitule: 'Entretien & Réparations Véhicules Atelier GMAO', classe: 6, type: 'CHARGE', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '661100', intitule: 'Salaires & Traitements du Personnel', classe: 6, type: 'CHARGE', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },
  { code: '681100', intitule: 'Dotations aux Amortissements d Exploitation', classe: 6, type: 'CHARGE', nature: 'CENTRALISATEUR', sens: 'DEBITEUR' },

  // Classe 7
  { code: '706100', intitule: 'Prestations de Fret Routier & Déplacements', classe: 7, type: 'PRODUIT', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },
  { code: '706200', intitule: 'Prestations de Manutention & Acconage Quai', classe: 7, type: 'PRODUIT', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },
  { code: '706300', intitule: 'Prestations de Dédouanement & Transit CEMAC', classe: 7, type: 'PRODUIT', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },
  { code: '706400', intitule: 'Magasinage & Entreposage WMS Sous Douane', classe: 7, type: 'PRODUIT', nature: 'CENTRALISATEUR', sens: 'CREDITEUR' },
];

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

export default function ComptabiliteOhadaChartAccounts() {
  const [accounts, setAccounts] = useState<SYSCOHADAAccount[]>(SYSCOHADA_PLAN);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedClasse, setSelectedClasse] = useState<number | 'ALL'>('ALL');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newAccount, setNewAccount] = useState({ code: '', intitule: '', classe: 1, type: 'ACTIF', nature: 'DETAIL', sens: 'DEBITEUR' });
  const [saving, setSaving] = useState(false);

  const loadAccounts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const token = getToken();
      const res = await fetch(`${API_BASE}/comptabilite-avance/plan-comptable`, {
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      });
      if (!res.ok) throw new Error(`${res.status}`);
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        setAccounts(data.map((c: Record<string, unknown>) => ({
          code: String(c.numero_compte ?? c.code ?? ''),
          intitule: String(c.intitule ?? c.libelle ?? ''),
          classe: Number(c.classe ?? String(c.numero_compte ?? '')[0] ?? 1),
          type: String(c.type_compte ?? c.type ?? 'ACTIF') as SYSCOHADAAccount['type'],
          nature: String(c.nature ?? 'CENTRALISATEUR') as SYSCOHADAAccount['nature'],
          sens: String(c.sens ?? 'DEBITEUR') as SYSCOHADAAccount['sens'],
        })));
      }
    } catch {
      setError('Chargement API échoué — affichage du référentiel SYSCOHADA standard.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadAccounts(); }, [loadAccounts]);

  const filtered = accounts.filter(a => {
    const matchClasse = selectedClasse === 'ALL' || a.classe === selectedClasse;
    const matchSearch = a.code.includes(searchQuery) || a.intitule.toLowerCase().includes(searchQuery.toLowerCase());
    return matchClasse && matchSearch;
  });

  const createAccount = async () => {
    setSaving(true);
    try {
      const token = getToken();
      const res = await fetch(`${API_BASE}/comptabilite-avance/plan-comptable`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          numero_compte: newAccount.code,
          intitule: newAccount.intitule,
          classe: newAccount.classe,
          type_compte: newAccount.type,
          nature: newAccount.nature,
          sens: newAccount.sens,
        }),
      });
      if (!res.ok) throw new Error();
      toast.success(`Compte ${newAccount.code} créé avec succès`);
      setShowCreateModal(false);
      setNewAccount({ code: '', intitule: '', classe: 1, type: 'ACTIF', nature: 'DETAIL', sens: 'DEBITEUR' });
      await loadAccounts();
    } catch {
      toast.error('Erreur lors de la création du compte');
    } finally {
      setSaving(false);
    }
  };

  const exportCSV = () => {
    const csv = ['Code;Intitulé;Classe;Type;Nature;Sens', ...filtered.map(a =>
      `${a.code};${a.intitule};${a.classe};${a.type};${a.nature};${a.sens}`
    )].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url; link.download = 'plan_comptable_syscohada.csv'; link.click();
    URL.revokeObjectURL(url);
    toast.success('Plan comptable exporté (CSV)');
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
              Nomenclature Officielle SYSCOHADA
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KOHA_COA
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Grid className="w-8 h-8 text-violet-400" />
            Plan Comptable SYSCOHADA
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Référentiel des comptes généraux et auxiliaires normalisés pour la logistique portuaire et le transport CEMAC.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button onClick={loadAccounts} disabled={loading}
            className="px-3 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs rounded-xl flex items-center gap-2 border border-slate-700 transition-all">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button onClick={exportCSV}
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-xl flex items-center gap-2 border border-slate-700 transition-all">
            <Download className="w-4 h-4 text-violet-400" /> Exporter CSV
          </button>
          <button onClick={() => setShowCreateModal(true)}
            className="px-4 py-2.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-violet-500/25 transition-all">
            <Plus className="w-4 h-4" /> Nouveau Sous-Compte
          </button>
        </div>
      </div>

      {/* Classes SYSCOHADA Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
        <button
          onClick={() => setSelectedClasse('ALL')}
          className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all border ${
            selectedClasse === 'ALL'
              ? 'bg-violet-600 text-white border-violet-500 shadow'
              : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'
          }`}
        >
          Toutes les Classes (1-8)
        </button>
        {[
          { num: 1, label: 'Cl. 1 : Ressources Durables' },
          { num: 2, label: 'Cl. 2 : Actif Immobilisé' },
          { num: 3, label: 'Cl. 3 : Stocks WMS' },
          { num: 4, label: 'Cl. 4 : Tiers (Clients/Fournisseurs)' },
          { num: 5, label: 'Cl. 5 : Trésorerie' },
          { num: 6, label: 'Cl. 6 : Charges' },
          { num: 7, label: 'Cl. 7 : Produits (Fret/Transit)' },
        ].map(cl => (
          <button
            key={cl.num}
            onClick={() => setSelectedClasse(cl.num)}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all border ${
              selectedClasse === cl.num
                ? 'bg-violet-600 text-white border-violet-500 shadow'
                : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'
            }`}
          >
            {cl.label}
          </button>
        ))}
      </div>

      {/* Barre de recherche */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher par numéro de compte ou intitulé..."
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500 font-mono"
          />
        </div>
        <div className="flex items-center gap-3">
          {error && <span className="text-[11px] text-amber-400 font-mono">{error}</span>}
          <span className="text-xs text-slate-400 font-mono">{loading ? 'Chargement…' : `${filtered.length} comptes listés`}</span>
        </div>
      </div>

      {/* Table du Plan Comptable */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Numéro de Compte</th>
                <th className="py-3.5 px-4">Intitulé Officiel SYSCOHADA</th>
                <th className="py-3.5 px-4">Classe</th>
                <th className="py-3.5 px-4">Type</th>
                <th className="py-3.5 px-4">Nature</th>
                <th className="py-3.5 px-4 text-center">Sens Normal</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(acc => (
                <tr key={acc.code} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-bold text-amber-400 text-sm">{acc.code}</td>
                  <td className="py-3 px-4 font-sans text-slate-100 font-semibold">{acc.intitule}</td>
                  <td className="py-3 px-4 text-slate-400">Classe {acc.classe}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      acc.type === 'ACTIF' ? 'bg-blue-500/20 text-blue-300' :
                      acc.type === 'PASSIF' ? 'bg-purple-500/20 text-purple-300' :
                      acc.type === 'CHARGE' ? 'bg-red-500/20 text-red-300' :
                      'bg-emerald-500/20 text-emerald-300'
                    }`}>
                      {acc.type}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-400">{acc.nature}</td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                      acc.sens === 'DEBITEUR' ? 'text-blue-400 bg-blue-500/10' : 'text-emerald-400 bg-emerald-500/10'
                    }`}>
                      {acc.sens}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-slate-900 border border-violet-500/40 rounded-3xl shadow-2xl w-full max-w-md p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-black text-slate-100">Créer un Sous-Compte SYSCOHADA</h3>
              <button onClick={() => setShowCreateModal(false)} className="p-2 hover:bg-slate-800 rounded-xl text-slate-400"><X className="w-5 h-5" /></button>
            </div>
            <div className="space-y-3">
              {[
                { label: 'Numéro de compte (6 chiffres)', key: 'code', type: 'text', placeholder: '411200' },
                { label: 'Intitulé officiel SYSCOHADA', key: 'intitule', type: 'text', placeholder: 'Clients Particuliers' },
              ].map(f => (
                <div key={f.key}>
                  <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1 block">{f.label}</label>
                  <input type={f.type} value={newAccount[f.key as keyof typeof newAccount] as string}
                    onChange={e => setNewAccount(prev => ({ ...prev, [f.key]: e.target.value }))}
                    placeholder={f.placeholder}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-violet-500 font-mono" />
                </div>
              ))}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1 block">Type</label>
                  <select value={newAccount.type} onChange={e => setNewAccount(p => ({ ...p, type: e.target.value }))}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-violet-500">
                    {['ACTIF', 'PASSIF', 'CHARGE', 'PRODUIT'].map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1 block">Sens Normal</label>
                  <select value={newAccount.sens} onChange={e => setNewAccount(p => ({ ...p, sens: e.target.value }))}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-violet-500">
                    {['DEBITEUR', 'CREDITEUR'].map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
              </div>
            </div>
            <div className="flex gap-3 pt-2">
              <button onClick={() => setShowCreateModal(false)} className="flex-1 px-4 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs rounded-xl border border-slate-700">Annuler</button>
              <button onClick={createAccount} disabled={saving || !newAccount.code || !newAccount.intitule}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2">
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <BookOpen className="w-4 h-4" />}
                {saving ? 'Création…' : 'Créer le Compte'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
