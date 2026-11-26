'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Scale, Plus, RefreshCw, AlertTriangle, FileText, Ban, CheckCircle2 } from 'lucide-react';
import { apiClient, apiUrl } from '@/lib/api-client';
import { toast } from 'sonner';

interface Contrat {
  id: number;
  reference: string;
  type_contrat: string;
  objet: string;
  partie_adverse?: string;
  montant?: number;
  devise: string;
  date_debut: string;
  date_fin?: string;
  reconduction: string;
  preavis_jours: number;
  statut: string;
}

interface Echeance {
  contrat_id: number;
  reference: string;
  objet: string;
  date_fin?: string;
  jours_restants?: number;
  preavis_a_notifier_avant_le?: string;
  motif: string;
}

const STATUTS: Record<string, string> = {
  actif: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  resilie: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
  expire: 'bg-slate-500/15 text-slate-400 border-slate-500/30',
  contentieux: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  brouillon: 'bg-sky-500/15 text-sky-400 border-sky-500/30',
};

const TYPES = ['bail', 'prestation', 'partenariat', 'concession', 'fourniture', 'autre'];
const TYPES_CONTENTIEUX = ['recouvrement', 'litige_fournisseur', 'litige_client', 'sanction', 'autre'];
const STATUTS_CONTENTIEUX: Record<string, string> = {
  ouvert: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
  en_cours: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  transaction: 'bg-sky-500/15 text-sky-400 border-sky-500/30',
  gagne: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  perdu: 'bg-slate-500/15 text-slate-400 border-slate-500/30',
  abandonne: 'bg-slate-600/20 text-slate-500 border-slate-600/30',
};

interface Contentieux {
  id: number;
  reference: string;
  contrat_id?: number;
  type_contentieux: string;
  description: string;
  montant_reclame?: number;
  montant_obtenu?: number;
  date_declaration: string;
  date_echeance?: string;
  juridiction?: string;
  statut: string;
}

export default function JuridiquePage() {
  const [contrats, setContrats] = useState<Contrat[]>([]);
  const [echeances, setEcheances] = useState<Echeance[]>([]);
  const [contentieux, setContentieux] = useState<Contentieux[]>([]);
  const [onglet, setOnglet] = useState<'contrats' | 'contentieux'>('contrats');
  const [showFormContentieux, setShowFormContentieux] = useState(false);
  const [formContentieux, setFormContentieux] = useState({
    reference: '', type_contentieux: 'litige_fournisseur', description: '',
    montant_reclame: '', contrat_id: '', date_declaration: new Date().toISOString().slice(0, 10),
    date_echeance: '', juridiction: '',
  });
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    reference: '', type_contrat: 'bail', objet: '', partie_adverse: '',
    montant: '', date_debut: '', date_fin: '', reconduction: 'non', preavis_jours: 0,
  });

  const charger = useCallback(async () => {
    setLoading(true);
    try {
      const [c, e, ct] = await Promise.all([
        apiClient.get(apiUrl('/juridique/contrats')),
        apiClient.get(apiUrl('/juridique/echeances'), { params: { jours: 120 } }),
        apiClient.get(apiUrl('/juridique/contentieux')),
      ]);
      setContrats(Array.isArray(c.data) ? c.data : []);
      setEcheances(Array.isArray(e.data) ? e.data : []);
      setContentieux(Array.isArray(ct.data) ? ct.data : []);
    } catch (err) {
      console.error('Erreur chargement juridique', err);
      toast.error('Impossible de charger les données juridiques');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  const creerContentieux = async (ev: React.FormEvent) => {
    ev.preventDefault();
    try {
      await apiClient.post(apiUrl('/juridique/contentieux'), {
        ...formContentieux,
        contrat_id: formContentieux.contrat_id ? Number(formContentieux.contrat_id) : null,
        montant_reclame: formContentieux.montant_reclame ? Number(formContentieux.montant_reclame) : null,
        date_echeance: formContentieux.date_echeance || null,
        juridiction: formContentieux.juridiction || null,
      });
      toast.success('Contentieux enregistré');
      setShowFormContentieux(false);
      setFormContentieux({ reference: '', type_contentieux: 'litige_fournisseur', description: '', montant_reclame: '', contrat_id: '', date_declaration: new Date().toISOString().slice(0, 10), date_echeance: '', juridiction: '' });
      charger();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur création contentieux');
    }
  };

  const cloturer = async (id: number) => {
    const statut = window.prompt('Statut de clôture (transaction / gagne / perdu / abandonne) :');
    if (!statut) return;
    const montant = window.prompt('Montant obtenu (XAF, optionnel) :');
    try {
      await apiClient.post(apiUrl(`/juridique/contentieux/${id}/cloturer`), null, {
        params: { statut, montant_obtenu: montant ? Number(montant) : undefined },
      });
      toast.success('Contentieux clôturé');
      charger();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur clôture');
    }
  };

  const creer = async (ev: React.FormEvent) => {
    ev.preventDefault();
    try {
      await apiClient.post(apiUrl('/juridique/contrats'), {
        ...form,
        montant: form.montant ? Number(form.montant) : null,
        date_fin: form.date_fin || null,
        company_id: null,
      });
      toast.success('Contrat enregistré');
      setShowForm(false);
      setForm({ reference: '', type_contrat: 'bail', objet: '', partie_adverse: '', montant: '', date_debut: '', date_fin: '', reconduction: 'non', preavis_jours: 0 });
      charger();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  const resilier = async (id: number) => {
    const motif = window.prompt('Motif de résiliation :');
    if (!motif || motif.length < 3) return;
    try {
      await apiClient.post(apiUrl(`/juridique/contrats/${id}/resilier`), null, { params: { motif } });
      toast.success('Contrat résilié');
      charger();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur');
    }
  };

  const input = 'w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-amber-500 focus:outline-none min-h-[44px]';
  const label = 'block text-xs font-medium text-slate-400 mb-1';

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 md:p-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-xl font-semibold text-slate-100">
            <Scale className="h-6 w-6 text-amber-400" /> Juridique &amp; Contrats
          </h1>
          <p className="text-sm text-slate-400">Registre des contrats à valeur documentaire, contentieux et échéances.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={charger} className="inline-flex min-h-[44px] items-center gap-2 rounded-lg border border-slate-700 px-4 text-sm text-slate-300 hover:bg-slate-800">
            <RefreshCw className="h-4 w-4" /> Actualiser
          </button>
          <button onClick={() => setShowForm(!showForm)} className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-amber-500 px-4 text-sm font-medium text-slate-950 hover:bg-amber-400">
            <Plus className="h-4 w-4" /> Nouveau contrat
          </button>
        </div>
      </header>

      {showForm && (
        <form onSubmit={creer} className="rounded-xl border border-slate-700 bg-slate-900/50 p-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div><label className={label}>Référence *</label><input required className={input} value={form.reference} onChange={e => setForm({ ...form, reference: e.target.value })} placeholder="CTR-2026-001" /></div>
            <div><label className={label}>Type</label>
              <select className={input} value={form.type_contrat} onChange={e => setForm({ ...form, type_contrat: e.target.value })}>
                {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div><label className={label}>Partie adverse</label><input className={input} value={form.partie_adverse} onChange={e => setForm({ ...form, partie_adverse: e.target.value })} /></div>
            <div className="md:col-span-2"><label className={label}>Objet *</label><input required className={input} value={form.objet} onChange={e => setForm({ ...form, objet: e.target.value })} placeholder="Objet du contrat" /></div>
            <div><label className={label}>Montant (XAF)</label><input type="number" className={input} value={form.montant} onChange={e => setForm({ ...form, montant: e.target.value })} /></div>
            <div><label className={label}>Début *</label><input required type="date" className={input} value={form.date_debut} onChange={e => setForm({ ...form, date_debut: e.target.value })} /></div>
            <div><label className={label}>Fin</label><input type="date" className={input} value={form.date_fin} onChange={e => setForm({ ...form, date_fin: e.target.value })} /></div>
            <div><label className={label}>Reconduction</label>
              <select className={input} value={form.reconduction} onChange={e => setForm({ ...form, reconduction: e.target.value })}>
                <option value="non">Aucune</option><option value="tacite">Tacite</option><option value="automatique">Automatique</option>
              </select>
            </div>
            <div><label className={label}>Préavis (jours)</label><input type="number" min={0} className={input} value={form.preavis_jours} onChange={e => setForm({ ...form, preavis_jours: Number(e.target.value) })} /></div>
          </div>
          <div className="mt-4 flex justify-end gap-2">
            <button type="button" onClick={() => setShowForm(false)} className="min-h-[44px] rounded-lg px-4 text-sm text-slate-400 hover:bg-slate-800">Annuler</button>
            <button type="submit" className="min-h-[44px] rounded-lg bg-amber-500 px-5 text-sm font-medium text-slate-950 hover:bg-amber-400">Enregistrer</button>
          </div>
        </form>
      )}

      {/* Onglets Contrats / Contentieux */}
      <div className="flex items-center gap-2">
        {(['contrats', 'contentieux'] as const).map(o => (
          <button key={o} onClick={() => setOnglet(o)}
            className={`rounded-lg px-4 py-2 text-sm font-medium min-h-[44px] ${onglet === o ? 'bg-amber-500 text-slate-950' : 'border border-slate-700 text-slate-300 hover:bg-slate-800'}`}>
            {o === 'contrats' ? `Contrats (${contrats.length})` : `Contentieux (${contentieux.length})`}
          </button>
        ))}
        {onglet === 'contentieux' && (
          <button onClick={() => setShowFormContentieux(!showFormContentieux)}
            className="ml-auto inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-amber-500 px-4 text-sm font-medium text-slate-950 hover:bg-amber-400">
            <Plus className="h-4 w-4" /> Nouveau contentieux
          </button>
        )}
      </div>

      {onglet === 'contrats' && echeances.length > 0 && (
        <section className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4">
          <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-amber-300">
            <AlertTriangle className="h-4 w-4" /> Échéances &amp; préavis ({echeances.length})
          </h2>
          <ul className="space-y-2">
            {echeances.map(e => (
              <li key={e.contrat_id} className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-slate-900/60 px-3 py-2 text-sm">
                <span className="font-medium text-slate-200">{e.reference} — {e.objet}</span>
                <span className="text-slate-400">{e.jours_restants !== undefined ? `${e.jours_restants} j restants` : ''}</span>
                <span className="text-amber-300/90">{e.motif}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {onglet === 'contrats' && (
      <section className="overflow-x-auto rounded-xl border border-slate-700">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
            <tr>
              <th className="px-4 py-3">Référence</th><th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Objet</th><th className="px-4 py-3">Partie adverse</th>
              <th className="px-4 py-3 text-right">Montant</th><th className="px-4 py-3">Fin</th>
              <th className="px-4 py-3">Statut</th><th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {loading ? (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-500">Chargement…</td></tr>
            ) : contrats.length === 0 ? (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-500">
                <FileText className="mx-auto mb-2 h-8 w-8 text-slate-600" />
                Aucun contrat enregistré.
              </td></tr>
            ) : contrats.map(c => (
              <tr key={c.id} className="hover:bg-slate-900/50">
                <td className="px-4 py-3 font-mono text-xs text-amber-300">{c.reference}</td>
                <td className="px-4 py-3 capitalize text-slate-300">{c.type_contrat}</td>
                <td className="max-w-[240px] truncate px-4 py-3 text-slate-200">{c.objet}</td>
                <td className="px-4 py-3 text-slate-400">{c.partie_adverse || '—'}</td>
                <td className="px-4 py-3 text-right text-slate-300">{c.montant != null ? `${Number(c.montant).toLocaleString('fr-FR')} ${c.devise}` : '—'}</td>
                <td className="px-4 py-3 text-slate-400">{c.date_fin || '—'}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full border px-2 py-0.5 text-xs ${STATUTS[c.statut] || 'border-slate-600 text-slate-400'}`}>{c.statut}</span>
                </td>
                <td className="px-4 py-3 text-right">
                  {c.statut === 'actif' && (
                    <button onClick={() => resilier(c.id)} title="Résilier" className="inline-flex min-h-[44px] items-center gap-1 rounded-lg px-2 text-xs text-rose-400 hover:bg-rose-500/10">
                      <Ban className="h-4 w-4" /> Résilier
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      )}

      {onglet === 'contentieux' && (
        <>
          {showFormContentieux && (
            <form onSubmit={creerContentieux} className="rounded-xl border border-slate-700 bg-slate-900/50 p-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div><label className={label}>Référence *</label><input required className={input} value={formContentieux.reference} onChange={e => setFormContentieux({ ...formContentieux, reference: e.target.value })} placeholder="CTJ-2026-001" /></div>
                <div><label className={label}>Type</label>
                  <select className={input} value={formContentieux.type_contentieux} onChange={e => setFormContentieux({ ...formContentieux, type_contentieux: e.target.value })}>
                    {TYPES_CONTENTIEUX.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
                  </select>
                </div>
                <div><label className={label}>Contrat lié (ID, optionnel)</label>
                  <select className={input} value={formContentieux.contrat_id} onChange={e => setFormContentieux({ ...formContentieux, contrat_id: e.target.value })}>
                    <option value="">— Aucun —</option>
                    {contrats.map(c => <option key={c.id} value={c.id}>{c.reference} — {c.objet}</option>)}
                  </select>
                </div>
                <div className="md:col-span-2"><label className={label}>Description *</label><input required className={input} value={formContentieux.description} onChange={e => setFormContentieux({ ...formContentieux, description: e.target.value })} /></div>
                <div><label className={label}>Montant réclamé (XAF)</label><input type="number" className={input} value={formContentieux.montant_reclame} onChange={e => setFormContentieux({ ...formContentieux, montant_reclame: e.target.value })} /></div>
                <div><label className={label}>Déclaration *</label><input required type="date" className={input} value={formContentieux.date_declaration} onChange={e => setFormContentieux({ ...formContentieux, date_declaration: e.target.value })} /></div>
                <div><label className={label}>Échéance</label><input type="date" className={input} value={formContentieux.date_echeance} onChange={e => setFormContentieux({ ...formContentieux, date_echeance: e.target.value })} /></div>
                <div><label className={label}>Juridiction</label><input className={input} value={formContentieux.juridiction} onChange={e => setFormContentieux({ ...formContentieux, juridiction: e.target.value })} placeholder="Tribunal de première instance de…" /></div>
              </div>
              <div className="mt-4 flex justify-end gap-2">
                <button type="button" onClick={() => setShowFormContentieux(false)} className="min-h-[44px] rounded-lg px-4 text-sm text-slate-400 hover:bg-slate-800">Annuler</button>
                <button type="submit" className="min-h-[44px] rounded-lg bg-amber-500 px-5 text-sm font-medium text-slate-950 hover:bg-amber-400">Enregistrer</button>
              </div>
            </form>
          )}

          <section className="overflow-x-auto rounded-xl border border-slate-700">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
                <tr>
                  <th className="px-4 py-3">Référence</th><th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Description</th><th className="px-4 py-3 text-right">Réclamé</th>
                  <th className="px-4 py-3 text-right">Obtenu</th><th className="px-4 py-3">Déclaré le</th>
                  <th className="px-4 py-3">Statut</th><th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {loading ? (
                  <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-500">Chargement…</td></tr>
                ) : contentieux.length === 0 ? (
                  <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-500">Aucun contentieux.</td></tr>
                ) : contentieux.map(c => (
                  <tr key={c.id} className="hover:bg-slate-900/50">
                    <td className="px-4 py-3 font-mono text-xs text-amber-300">{c.reference}</td>
                    <td className="px-4 py-3 capitalize text-slate-300">{c.type_contentieux.replace(/_/g, ' ')}</td>
                    <td className="max-w-[220px] truncate px-4 py-3 text-slate-200">{c.description}</td>
                    <td className="px-4 py-3 text-right text-slate-300">{c.montant_reclame != null ? `${Number(c.montant_reclame).toLocaleString('fr-FR')} XAF` : '—'}</td>
                    <td className="px-4 py-3 text-right text-emerald-400">{c.montant_obtenu != null ? `${Number(c.montant_obtenu).toLocaleString('fr-FR')} XAF` : '—'}</td>
                    <td className="px-4 py-3 text-slate-400">{c.date_declaration}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full border px-2 py-0.5 text-xs ${STATUTS_CONTENTIEUX[c.statut] || 'border-slate-600 text-slate-400'}`}>{c.statut.replace(/_/g, ' ')}</span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      {(c.statut === 'ouvert' || c.statut === 'en_cours') && (
                        <button onClick={() => cloturer(c.id)} className="inline-flex min-h-[44px] items-center gap-1 rounded-lg px-2 text-xs text-emerald-400 hover:bg-emerald-500/10">
                          <CheckCircle2 className="h-4 w-4" /> Clôturer
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      )}
    </div>
  );
}
