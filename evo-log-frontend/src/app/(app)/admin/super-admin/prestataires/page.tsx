'use client';

// Console Super-Admin CADC  Annuaire des prestataires. Écriture réservée au CADC
// (le backend exige require_superadmin) ; la consultation publique reste ailleurs.

import React, { useState, useEffect, useCallback } from 'react';
import { Users, Plus, Search, RefreshCw, Pencil, Trash2, X, CheckCircle2 } from 'lucide-react';
import { toast } from 'sonner';
import { saasConsoleAPI } from '@/lib/api-client';

interface CadcPrestataire {
  id: number; code: string; raison_sociale: string; specialite: string;
  sigle?: string | null; ville?: string | null; zone_portuaire?: string | null;
  contact_nom?: string | null; contact_telephone: string; contact_email?: string | null;
  agrement_portuaire?: string | null; statut_agrement?: string; est_actif: boolean;
}

interface PForm {
  code: string; raison_sociale: string; specialite: string; sigle: string;
  ville: string; zone_portuaire: string; contact_nom: string; contact_telephone: string;
  contact_email: string; agrement_portuaire: string; statut_agrement: string; est_actif: boolean;
}

const SPECIALITES = [
  'TRANSPORT_LOURD', 'MANUTENTION_PORTUAIRE', 'TRANSIT_DOUANE', 'ENTREPOSAGE',
  'CLEANING', 'SECURITE', 'MAINTENANCE', 'AUTRE',
];
const emptyForm = (): PForm => ({
  code: '', raison_sociale: '', specialite: 'TRANSPORT_LOURD', sigle: '', ville: 'Douala',
  zone_portuaire: '', contact_nom: '', contact_telephone: '', contact_email: '',
  agrement_portuaire: '', statut_agrement: 'VALIDE', est_actif: true,
});

export default function CadcPrestatairesPage() {
  const [rows, setRows] = useState<CadcPrestataire[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState<CadcPrestataire | null>(null);
  const [form, setForm] = useState<PForm>(emptyForm());
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await saasConsoleAPI.listPrestataires(search ? { search } : undefined);
      setRows(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error(err);
      toast.error('Impossible de charger l\'annuaire');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { load(); }, [load]);

  const openCreate = () => { setEditing(null); setForm(emptyForm()); setDrawerOpen(true); };
  const openEdit = (p: CadcPrestataire) => {
    setEditing(p);
    setForm({
      code: p.code, raison_sociale: p.raison_sociale, specialite: p.specialite || '',
      sigle: p.sigle || '', ville: p.ville || 'Douala', zone_portuaire: p.zone_portuaire || '',
      contact_nom: p.contact_nom || '', contact_telephone: p.contact_telephone || '',
      contact_email: p.contact_email || '', agrement_portuaire: p.agrement_portuaire || '',
      statut_agrement: p.statut_agrement || 'VALIDE', est_actif: p.est_actif,
    });
    setDrawerOpen(true);
  };

  const handleSave = async () => {
    if (!form.code.trim() || !form.raison_sociale.trim() || !form.contact_telephone.trim()) {
      toast.error('Code, raison sociale et téléphone sont obligatoires'); return;
    }
    setSaving(true);
    const payload: Record<string, unknown> = {
      raison_sociale: form.raison_sociale.trim(), specialite: form.specialite, sigle: form.sigle || null,
      ville: form.ville || null, zone_portuaire: form.zone_portuaire || null,
      contact_nom: form.contact_nom || null, contact_telephone: form.contact_telephone.trim(),
      contact_email: form.contact_email || null, agrement_portuaire: form.agrement_portuaire || null,
      statut_agrement: form.statut_agrement, est_actif: form.est_actif,
    };
    try {
      if (!editing) {
        await saasConsoleAPI.createPrestataire({ ...payload, code: form.code.trim() });
        toast.success('Prestataire ajouté');
      } else {
        await saasConsoleAPI.updatePrestataire(editing.id, payload);
        toast.success('Prestataire mis à jour');
      }
      setDrawerOpen(false); load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Échec de l\'enregistrement');
    } finally { setSaving(false); }
  };

  const handleDelete = async (p: CadcPrestataire) => {
    if (!confirm(`Retirer « ${p.raison_sociale} » de l'annuaire ?`)) return;
    try { await saasConsoleAPI.deletePrestataire(p.id); toast.success('Prestataire retiré'); load(); }
    catch (err: any) { toast.error(err?.response?.data?.detail || 'Suppression impossible'); }
  };

  const filtered = rows.filter(p =>
    p.raison_sociale.toLowerCase().includes(search.toLowerCase()) || p.code.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">Console Super-Admin CADC</span>
          <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">T-Code : KCADC_PRE</span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3"><Users className="w-8 h-8 text-amber-400" /> Annuaire des prestataires</h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">Référencement B2B  écriture strictement réservée au Super Administrateur CADC.</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={load} className="p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-slate-300 transition-all"><RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-amber-400' : ''}`} /></button>
            <button onClick={openCreate} className="px-4 py-2.5 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs rounded-xl flex items-center gap-1.5 transition-colors shadow-lg shadow-amber-600/20"><Plus className="w-4 h-4" /> Ajouter</button>
          </div>
        </div>
      </div>

      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher un prestataire..." className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500" />
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Prestataire</th>
                <th className="py-3.5 px-4">Spécialité</th>
                <th className="py-3.5 px-4">Contact</th>
                <th className="py-3.5 px-4 text-center">Agréement</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(p => (
                <tr key={p.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold font-sans text-slate-100">{p.raison_sociale}</div>
                    <div className="text-[11px] text-amber-400 font-mono">{p.code}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans">{p.specialite}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-sans">{p.contact_nom || ''}</div>
                    <div className="text-[11px] text-slate-500">{p.contact_telephone}</div>
                  </td>
                  <td className="py-3.5 px-4 text-center font-mono text-[11px]">{p.agrement_portuaire || ''}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${p.est_actif ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>{p.est_actif ? 'ACTIF' : 'INACTIF'}</span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button onClick={() => openEdit(p)} className="px-2.5 py-1 text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-bold border border-slate-700 flex items-center gap-1"><Pencil className="w-3 h-3" /> Éditer</button>
                      <button onClick={() => handleDelete(p)} className="p-1.5 text-red-400 hover:bg-red-500/10 rounded-lg border border-transparent hover:border-red-500/30"><Trash2 className="w-4 h-4" /></button>
                    </div>
                  </td>
                </tr>
              ))}
              {!loading && filtered.length === 0 && <tr><td colSpan={6} className="py-10 text-center text-slate-500 font-sans">Aucun prestataire.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      {drawerOpen && (
        <div className="fixed inset-0 z-[100] flex justify-end">
          <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm" onClick={() => setDrawerOpen(false)} />
          <div className="relative h-full w-full max-w-lg bg-slate-900 border-l border-slate-800 shadow-2xl overflow-y-auto">
            <div className="sticky top-0 bg-slate-900/95 backdrop-blur border-b border-slate-800 px-6 py-4 flex items-center justify-between z-10">
              <h2 className="text-lg font-black text-slate-100">{editing ? `Éditer  ${editing.raison_sociale}` : 'Nouveau prestataire'}</h2>
              <button onClick={() => setDrawerOpen(false)} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Field label="Code" disabled={!!editing}><input value={form.code} onChange={e => setForm({ ...form, code: e.target.value })} disabled={!!editing} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100 disabled:opacity-50" /></Field>
                <Field label="Spécialité">
                  <select value={form.specialite} onChange={e => setForm({ ...form, specialite: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100">
                    {SPECIALITES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </Field>
              </div>
              <Field label="Raison sociale"><input value={form.raison_sociale} onChange={e => setForm({ ...form, raison_sociale: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
              <div className="grid grid-cols-2 gap-4">
                <Field label="Sigle"><input value={form.sigle} onChange={e => setForm({ ...form, sigle: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Ville"><input value={form.ville} onChange={e => setForm({ ...form, ville: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Zone portuaire"><input value={form.zone_portuaire} onChange={e => setForm({ ...form, zone_portuaire: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Agréement portuaire"><input value={form.agrement_portuaire} onChange={e => setForm({ ...form, agrement_portuaire: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Contact (nom)"><input value={form.contact_nom} onChange={e => setForm({ ...form, contact_nom: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Téléphone *"><input value={form.contact_telephone} onChange={e => setForm({ ...form, contact_telephone: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Email"><input value={form.contact_email} onChange={e => setForm({ ...form, contact_email: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Statut agréement">
                  <select value={form.statut_agrement} onChange={e => setForm({ ...form, statut_agrement: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100">
                    {['VALIDE', 'EXPIRE', 'SUSPENDU', 'EN_ATTENTE'].map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </Field>
              </div>
              <label className="flex items-center gap-2 text-sm text-slate-300"><input type="checkbox" checked={form.est_actif} onChange={e => setForm({ ...form, est_actif: e.target.checked })} className="rounded bg-slate-950 border-slate-700" />Prestataire actif</label>
            </div>
            <div className="sticky bottom-0 bg-slate-900/95 backdrop-blur border-t border-slate-800 px-6 py-4 flex justify-end gap-3">
              <button onClick={() => setDrawerOpen(false)} className="px-4 py-2 text-sm rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700">Annuler</button>
              <button onClick={handleSave} disabled={saving} className="px-4 py-2 text-sm rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-bold disabled:opacity-50 flex items-center gap-2"><CheckCircle2 className="w-4 h-4" /> {saving ? 'Enregistrement...' : 'Enregistrer'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, children, disabled }: { label: string; children: React.ReactNode; disabled?: boolean }) {
  return <div><label className="block text-xs font-semibold text-slate-400 mb-1">{label}</label>{children}</div>;
}
