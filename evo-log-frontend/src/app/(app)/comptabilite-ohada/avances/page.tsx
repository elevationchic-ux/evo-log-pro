'use client';

import React, { useEffect, useState } from 'react';
import { deepAPI } from '@/lib/api-client';
import { RefreshCw } from 'lucide-react';
import Link from 'next/link';

type Row = Record<string, unknown>;
type Field = { name: string; label: string; type?: 'text' | 'number' | 'date'; required?: boolean; placeholder?: string };

interface Config {
  key: string;
  label: string;
  fetcher: () => Promise<{ data: Row[] | { items?: Row[] } }>;
  creator: (d: Row) => Promise<unknown>;
  columns: { key: string; label: string }[];
  fields: Field[];
}

const num = (v: unknown) => {
  if (v === null || v === undefined) return '—';
  const n = Number(v);
  return Number.isFinite(n) ? n.toLocaleString('fr-FR') : String(v);
};
const txt = (v: unknown) => (v === null || v === undefined || v === '' ? '—' : String(v));

function ResourceTab({ cfg }: { cfg: Config }) {
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);
  const [vals, setVals] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const res = await cfg.fetcher();
      const d = res.data ?? res;
      setRows(Array.isArray(d) ? d : ((d as { items?: Row[] }).items ?? []));
    } catch { setRows([]); }
    setLoading(false);
  };
  useEffect(() => { load(); }, [cfg.key]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true); setMsg(null);
    const body: Row = {};
    cfg.fields.forEach((f) => {
      const v = vals[f.name];
      if (v === undefined || v === '') return;
      body[f.name] = f.type === 'number' ? Number(v) : v;
    });
    try {
      await cfg.creator(body);
      setMsg('Enregistré.');
      setVals({});
      load();
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : 'Erreur');
    } finally { setSaving(false); }
  };

  return (
    <div className="space-y-4">
      <form onSubmit={submit} className="bg-white border rounded-xl p-4 shadow-sm">
        <div className="grid grid-cols-4 gap-3 items-end">
          {cfg.fields.map((f) => (
            <label key={f.name} className="text-sm">
              <span className="block text-xs text-gray-500 mb-1">{f.label}{f.required ? ' *' : ''}</span>
              <input
                type={f.type ?? 'text'}
                required={f.required}
                value={vals[f.name] ?? ''}
                onChange={(e) => setVals({ ...vals, [f.name]: e.target.value })}
                placeholder={f.placeholder}
                className="w-full border rounded px-2 py-1.5 text-sm"
              />
            </label>
          ))}
          <button disabled={saving} className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
            {saving ? '…' : 'Créer'}
          </button>
        </div>
        {msg && <p className="text-sm text-blue-700 mt-2">{msg}</p>}
      </form>

      <div className="bg-white border rounded-xl shadow-sm overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs text-gray-500">
            <tr>{cfg.columns.map((c) => <th key={c.key} className="px-4 py-3">{c.label}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={Number(r.id ?? i)} className="border-t">
                {cfg.columns.map((c) => <td key={c.key} className="px-4 py-2">{num(r[c.key]) === '—' ? txt(r[c.key]) : num(r[c.key])}</td>)}
              </tr>
            ))}
            {!loading && rows.length === 0 && (
              <tr><td colSpan={cfg.columns.length} className="px-4 py-8 text-center text-gray-400">Aucune donnée</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const TABS: Config[] = [
  {
    key: 'immobilisations', label: 'Immobilisations',
    fetcher: () => deepAPI.getAssetRegistrations(), creator: deepAPI.createAssetRegistration,
    columns: [
      { key: 'numero_inventaire', label: 'N° inventaire' }, { key: 'designation', label: 'Désignation' },
      { key: 'categorie', label: 'Catégorie' }, { key: 'valeur_acquisition_xaf', label: 'Valeur XAF' },
      { key: 'duree_amortissement_an', label: 'Durée (an)' }, { key: 'statut', label: 'Statut' },
    ],
    fields: [
      { name: 'numero_inventaire', label: 'N° inventaire', required: true },
      { name: 'designation', label: 'Désignation' }, { name: 'categorie', label: 'Catégorie' },
      { name: 'valeur_acquisition_xaf', label: 'Valeur XAF', type: 'number' },
      { name: 'duree_amortissement_an', label: 'Durée (an)', type: 'number' },
      { name: 'mode_amortissement', label: 'Mode amortissement' }, { name: 'statut', label: 'Statut' },
    ],
  },
  {
    key: 'amortissements', label: 'Plans d’amortissement',
    fetcher: () => deepAPI.getDepreciationSchedules(), creator: deepAPI.createDepreciationSchedule,
    columns: [
      { key: 'reference', label: 'Référence' }, { key: 'asset_id', label: 'Immo' },
      { key: 'exercice', label: 'Exercice' }, { key: 'dotation_xaf', label: 'Dotation' },
      { key: 'cumul_xaf', label: 'Cumul' }, { key: 'statut', label: 'Statut' },
    ],
    fields: [
      { name: 'reference', label: 'Référence', required: true }, { name: 'asset_id', label: 'Immo ID', type: 'number', required: true },
      { name: 'exercice', label: 'Exercice', type: 'number' }, { name: 'dotation_xaf', label: 'Dotation XAF', type: 'number' },
      { name: 'date_ecriture', label: 'Date écriture', type: 'date' }, { name: 'statut', label: 'Statut' },
    ],
  },
  {
    key: 'provisions', label: 'Provisions',
    fetcher: () => deepAPI.getProvisions(), creator: deepAPI.createProvision,
    columns: [
      { key: 'reference', label: 'Référence' }, { key: 'type_provision', label: 'Type' },
      { key: 'exercice', label: 'Exercice' }, { key: 'montant_xaf', label: 'Montant XAF' },
      { key: 'statut', label: 'Statut' }, { key: 'motivation', label: 'Motivation' },
    ],
    fields: [
      { name: 'reference', label: 'Référence', required: true }, { name: 'type_provision', label: 'Type', required: true },
      { name: 'exercice', label: 'Exercice', type: 'number' }, { name: 'montant_xaf', label: 'Montant XAF', type: 'number' },
      { name: 'compte_charge', label: 'Compte charge' }, { name: 'motivation', label: 'Motivation' },
    ],
  },
  {
    key: 'intercompany', label: 'Inter-sociétés',
    fetcher: () => deepAPI.getIntercompanyEntries(), creator: deepAPI.createIntercompanyEntry,
    columns: [
      { key: 'reference', label: 'Référence' }, { key: 'entite_emettrice', label: 'Émettrice' },
      { key: 'entite_destinatrice', label: 'Destinataire' }, { key: 'montant_xaf', label: 'Montant XAF' },
      { key: 'nature', label: 'Nature' }, { key: 'statut', label: 'Statut' },
    ],
    fields: [
      { name: 'reference', label: 'Référence', required: true },
      { name: 'entite_emettrice', label: 'Entité émettrice' }, { name: 'entite_destinatrice', label: 'Entité destinataire' },
      { name: 'montant_xaf', label: 'Montant XAF', type: 'number' }, { name: 'nature', label: 'Nature' },
      { name: 'date_ecriture', label: 'Date', type: 'date' }, { name: 'statut', label: 'Statut' },
    ],
  },
  {
    key: 'audit-pafs', label: 'Audits PAF',
    fetcher: () => deepAPI.getAuditPafs(), creator: deepAPI.createAuditPaf,
    columns: [
      { key: 'hash_ligne', label: 'Hash' }, { key: 'numero_piece', label: 'N° pièce' },
      { key: 'compte', label: 'Compte' }, { key: 'libelle', label: 'Libellé' },
      { key: 'debit_xaf', label: 'Débit' }, { key: 'credit_xaf', label: 'Crédit' },
    ],
    fields: [
      { name: 'hash_ligne', label: 'Hash ligne', required: true }, { name: 'hash_precedent', label: 'Hash précédent' },
      { name: 'numero_piece', label: 'N° pièce' }, { name: 'compte', label: 'Compte' },
      { name: 'libelle', label: 'Libellé' }, { name: 'debit_xaf', label: 'Débit XAF', type: 'number' },
      { name: 'credit_xaf', label: 'Crédit XAF', type: 'number' },
    ],
  },
  {
    key: 'taxes', label: 'Déclarations fiscales',
    fetcher: () => deepAPI.getTaxDeclarations(), creator: deepAPI.createTaxDeclaration,
    columns: [
      { key: 'reference', label: 'Référence' }, { key: 'type_declaration', label: 'Type' },
      { key: 'periode_debut', label: 'Début' }, { key: 'periode_fin', label: 'Fin' },
      { key: 'base_imposable_xaf', label: 'Base XAF' }, { key: 'droits_xaf', label: 'Droits XAF' },
      { key: 'statut', label: 'Statut' },
    ],
    fields: [
      { name: 'reference', label: 'Référence', required: true }, { name: 'type_declaration', label: 'Type', required: true },
      { name: 'periode_debut', label: 'Début', type: 'date' }, { name: 'periode_fin', label: 'Fin', type: 'date' },
      { name: 'base_imposable_xaf', label: 'Base XAF', type: 'number' }, { name: 'droits_xaf', label: 'Droits XAF', type: 'number' },
      { name: 'date_depot', label: 'Date dépôt', type: 'date' }, { name: 'statut', label: 'Statut' },
    ],
  },
  {
    key: 'paie', label: 'Écritures de paie',
    fetcher: () => deepAPI.getPayrollEntries(), creator: deepAPI.createPayrollEntry,
    columns: [
      { key: 'reference', label: 'Référence' }, { key: 'periode', label: 'Période' },
      { key: 'masse_salariale_xaf', label: 'Masse XAF' }, { key: 'charges_patronales_xaf', label: 'Charges' },
      { key: 'impot_retenu_xaf', label: 'IR retenu' }, { key: 'net_paye_xaf', label: 'Net payé' },
      { key: 'statut', label: 'Statut' },
    ],
    fields: [
      { name: 'reference', label: 'Référence', required: true }, { name: 'periode', label: 'Période', required: true, placeholder: '2025-11' },
      { name: 'masse_salariale_xaf', label: 'Masse salariale', type: 'number' },
      { name: 'charges_patronales_xaf', label: 'Charges patronales', type: 'number' },
      { name: 'impot_retenu_xaf', label: 'IR retenu', type: 'number' }, { name: 'net_paye_xaf', label: 'Net payé', type: 'number' },
      { name: 'date_passage', label: 'Date passage', type: 'date' }, { name: 'statut', label: 'Statut' },
    ],
  },
  {
    key: 'tresorerie', label: 'Comptes de trésorerie',
    fetcher: () => deepAPI.getTreasuryAccounts(), creator: deepAPI.createTreasuryAccount,
    columns: [
      { key: 'code_compte', label: 'Code' }, { key: 'intitule', label: 'Intitulé' },
      { key: 'type_compte', label: 'Type' }, { key: 'banque', label: 'Banque' },
      { key: 'solde_actuel_xaf', label: 'Solde XAF' }, { key: 'devise', label: 'Devise' }, { key: 'statut', label: 'Statut' },
    ],
    fields: [
      { name: 'code_compte', label: 'Code compte', required: true }, { name: 'intitule', label: 'Intitulé', required: true },
      { name: 'type_compte', label: 'Type (banque/caisse)' }, { name: 'banque', label: 'Banque' }, { name: 'rib', label: 'RIB' },
      { name: 'solde_actuel_xaf', label: 'Solde XAF', type: 'number' }, { name: 'devise', label: 'Devise' }, { name: 'statut', label: 'Statut' },
    ],
  },
  {
    key: 'analytique', label: 'Sections analytiques',
    fetcher: () => deepAPI.getAnalyticalSections(), creator: deepAPI.createAnalyticalSection,
    columns: [
      { key: 'code_section', label: 'Code' }, { key: 'intitule', label: 'Intitulé' },
      { key: 'type_section', label: 'Type' }, { key: 'cle_repartition', label: 'Clé repartition' },
      { key: 'cout_total_xaf', label: 'Coût XAF' }, { key: 'actif', label: 'Actif' },
    ],
    fields: [
      { name: 'code_section', label: 'Code section', required: true }, { name: 'intitule', label: 'Intitulé', required: true },
      { name: 'type_section', label: 'Type' }, { name: 'cle_repartition', label: 'Clé de répartition' },
      { name: 'unite_oeuvre', label: 'Unité d’œuvre' }, { name: 'cout_total_xaf', label: 'Coût XAF', type: 'number' },
    ],
  },
];

export default function ComptabiliteAvancesPage() {
  const [tab, setTab] = useState(TABS[0].key);
  const [nonce, setNonce] = useState(0);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/comptabilite-ohada/dashboard" className="text-sm text-gray-400 hover:text-gray-600">← Comptabilité OHADA</Link>
          <h1 className="text-2xl font-bold mt-1">Comptabilité avancée</h1>
          <p className="text-sm text-gray-500">Immobilisations, provisions, PAF, déclarations fiscales, paie, trésorerie, analytique.</p>
        </div>
        <button onClick={() => setNonce((n) => n + 1)} className="flex items-center gap-2 px-3 py-2 text-sm border rounded-lg hover:bg-gray-50">
          <RefreshCw className="w-4 h-4" /> Actualiser
        </button>
      </div>

      <div className="flex flex-wrap gap-2 border-b pb-2">
        {TABS.map((t) => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm rounded-t-lg ${tab === t.key ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {TABS.filter((t) => t.key === tab).map((t) => (
        <ResourceTab key={`${t.key}-${nonce}`} cfg={t} />
      ))}
    </div>
  );
}
