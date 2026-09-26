'use client';

// Console Super-Admin CADC — Paliers d'abonnement (SubscriptionPlan).
// max_modules verrouille, une fois le plan créé, le nombre de modules allouables
// aux entreprises qui y sont rattachées. Le sélecteur de modules inclus désactive
// les cases au-delà du compteur.

import React, { useState, useEffect, useCallback } from 'react';
import { Tag, Plus, RefreshCw, Pencil, Trash2, X, CheckCircle2, Lock } from 'lucide-react';
import { toast } from 'sonner';
import { saasConsoleAPI } from '@/lib/api-client';

interface CadcModule { key: string; label: string; domain: string }
interface CadcPlan {
  id: number; code: string; nom: string; type_plan: string; description?: string | null;
  prix_mensuel?: number; prix_annuel?: number; devise?: string;
  modules_inclus: string[]; max_modules: number | null; max_users?: number;
  is_active: boolean; company_count?: number;
}

interface PlanForm {
  code: string; nom: string; type_plan: string; description: string;
  prix_mensuel: string; prix_annuel: string; max_users: string;
  max_modules: string; unlimited: boolean; modules_inclus: string[]; is_active: boolean;
}

const PLAN_TYPES = ['starter', 'pro', 'enterprise', 'custom'];
const emptyForm = (): PlanForm => ({
  code: '', nom: '', type_plan: 'pro', description: '', prix_mensuel: '0', prix_annuel: '0',
  max_users: '20', max_modules: '5', unlimited: false, modules_inclus: [], is_active: true,
});

export default function CadcPlansPage() {
  const [plans, setPlans] = useState<CadcPlan[]>([]);
  const [modules, setModules] = useState<CadcModule[]>([]);
  const [loading, setLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState<CadcPlan | null>(null);
  const [form, setForm] = useState<PlanForm>(emptyForm());
  const [saving, setSaving] = useState(false);

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [pRes, mRes] = await Promise.all([saasConsoleAPI.listPlans(), saasConsoleAPI.getModulesCatalog()]);
      setPlans(Array.isArray(pRes.data) ? pRes.data : []);
      setModules(mRes.data?.modules || []);
    } catch (err) {
      console.error(err);
      toast.error('Impossible de charger les paliers');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadAll(); }, [loadAll]);

  const openCreate = () => { setEditing(null); setForm(emptyForm()); setDrawerOpen(true); };

  const openEdit = (p: CadcPlan) => {
    setEditing(p);
    setForm({
      code: p.code, nom: p.nom, type_plan: p.type_plan || 'pro', description: p.description || '',
      prix_mensuel: String(p.prix_mensuel ?? 0), prix_annuel: String(p.prix_annuel ?? 0),
      max_users: String(p.max_users ?? 20),
      max_modules: p.max_modules == null ? '' : String(p.max_modules),
      unlimited: p.max_modules == null,
      modules_inclus: Array.isArray(p.modules_inclus) ? [...p.modules_inclus] : [],
      is_active: p.is_active,
    });
    setDrawerOpen(true);
  };

  const cap: number | null = form.unlimited ? null : (form.max_modules === '' ? null : Number(form.max_modules));

  const toggleModule = (key: string) => {
    setForm(prev => {
      if (prev.modules_inclus.includes(key)) return { ...prev, modules_inclus: prev.modules_inclus.filter(m => m !== key) };
      if (cap !== null && prev.modules_inclus.length >= cap) {
        toast.warning(`Verrou : ${cap} module(s) maximum pour ce palier`);
        return prev;
      }
      return { ...prev, modules_inclus: [...prev.modules_inclus, key] };
    });
  };

  const handleSave = async () => {
    if (!form.code.trim() || !form.nom.trim()) { toast.error('Code et nom obligatoires'); return; }
    setSaving(true);
    const payload: Record<string, unknown> = {
      nom: form.nom.trim(), type_plan: form.type_plan, description: form.description || null,
      prix_mensuel: Number(form.prix_mensuel) || 0, prix_annuel: Number(form.prix_annuel) || 0,
      max_users: Number(form.max_users) || 10, max_modules: cap,
      modules_inclus: form.modules_inclus, is_active: form.is_active,
    };
    try {
      if (!editing) {
        await saasConsoleAPI.createPlan({ ...payload, code: form.code.trim() });
        toast.success('Palier créé');
      } else {
        await saasConsoleAPI.updatePlan(editing.id, payload);
        toast.success('Palier mis à jour');
      }
      setDrawerOpen(false);
      loadAll();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Échec de l\'enregistrement');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (p: CadcPlan) => {
    if (!confirm(`Supprimer le palier « ${p.nom} » ?`)) return;
    try {
      await saasConsoleAPI.deletePlan(p.id);
      toast.success('Palier supprimé');
      loadAll();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Suppression impossible');
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">Console Super-Admin CADC</span>
          <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">T-Code : KCADC_PLN</span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3"><Tag className="w-8 h-8 text-amber-400" /> Paliers d&apos;abonnement</h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">Le verrou <span className="font-mono text-amber-300">max_modules</span> borne le nombre de modules allouables aux entreprises du palier.</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={loadAll} className="p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-slate-300 transition-all"><RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-amber-400' : ''}`} /></button>
            <button onClick={openCreate} className="px-4 py-2.5 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs rounded-xl flex items-center gap-1.5 transition-colors shadow-lg shadow-amber-600/20"><Plus className="w-4 h-4" /> Nouveau palier</button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {plans.map(p => (
          <div key={p.id} className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg flex flex-col">
            <div className="flex items-start justify-between">
              <div>
                <div className="text-[11px] font-black uppercase tracking-wider text-amber-400">{p.type_plan}</div>
                <h3 className="text-lg font-black text-slate-100">{p.nom}</h3>
                <div className="font-mono text-[11px] text-slate-500">{p.code}</div>
              </div>
              <div className="flex items-center gap-1">
                <button onClick={() => openEdit(p)} className="p-1.5 text-slate-400 hover:text-amber-300 hover:bg-slate-800 rounded-lg"><Pencil className="w-4 h-4" /></button>
                <button onClick={() => handleDelete(p)} className="p-1.5 text-red-400 hover:bg-red-500/10 rounded-lg"><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
            <div className="mt-3 flex items-center gap-2 text-xs">
              <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 flex items-center gap-1">
                <Lock className="w-3 h-3" /> {p.max_modules == null ? 'Illimité' : `${p.max_modules} modules`}
              </span>
              <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">{p.company_count ?? 0} entreprise(s)</span>
            </div>
            <div className="mt-2 text-[11px] text-slate-400 font-mono">{(p.modules_inclus?.length || 0)} module(s) inclus</div>
            <div className="mt-3 pt-3 border-t border-slate-800 flex items-center justify-between text-[11px]">
              <span className={p.is_active ? 'text-emerald-400 font-bold' : 'text-red-400 font-bold'}>{p.is_active ? 'ACTIF' : 'ARCHIVÉ'}</span>
              <span className="text-slate-400 font-mono">{Number(p.prix_mensuel || 0).toLocaleString('fr-FR')} {p.devise}/mois</span>
            </div>
          </div>
        ))}
        {!loading && plans.length === 0 && <div className="text-slate-500 font-sans text-sm col-span-full py-10 text-center">Aucun palier.</div>}
      </div>

      {drawerOpen && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm" onClick={() => setDrawerOpen(false)} />
          <div className="relative h-full w-full max-w-lg bg-slate-900 border-l border-slate-800 shadow-2xl overflow-y-auto">
            <div className="sticky top-0 bg-slate-900/95 backdrop-blur border-b border-slate-800 px-6 py-4 flex items-center justify-between z-10">
              <h2 className="text-lg font-black text-slate-100">{editing ? `Éditer — ${editing.nom}` : 'Nouveau palier'}</h2>
              <button onClick={() => setDrawerOpen(false)} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Field label="Code" disabled={!!editing}><input value={form.code} onChange={e => setForm({ ...form, code: e.target.value })} disabled={!!editing} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100 disabled:opacity-50" /></Field>
                <Field label="Type">
                  <select value={form.type_plan} onChange={e => setForm({ ...form, type_plan: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100">
                    {PLAN_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </Field>
              </div>
              <Field label="Nom"><input value={form.nom} onChange={e => setForm({ ...form, nom: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
              <Field label="Description"><textarea value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} rows={2} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
              <div className="grid grid-cols-2 gap-4">
                <Field label="Prix mensuel"><input type="number" value={form.prix_mensuel} onChange={e => setForm({ ...form, prix_mensuel: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Prix annuel"><input type="number" value={form.prix_annuel} onChange={e => setForm({ ...form, prix_annuel: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Max utilisateurs"><input type="number" value={form.max_users} onChange={e => setForm({ ...form, max_users: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Verrou max_modules">
                  <div className="flex items-center gap-2">
                    <input type="number" min={0} value={form.unlimited ? '' : form.max_modules} disabled={form.unlimited} onChange={e => setForm({ ...form, max_modules: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100 disabled:opacity-40" />
                    <label className="flex items-center gap-1 text-[11px] text-slate-400 whitespace-nowrap"><input type="checkbox" checked={form.unlimited} onChange={e => setForm({ ...form, unlimited: e.target.checked })} className="rounded bg-slate-950 border-slate-700" />Illimité</label>
                  </div>
                </Field>
              </div>
              <label className="flex items-center gap-2 text-sm text-slate-300"><input type="checkbox" checked={form.is_active} onChange={e => setForm({ ...form, is_active: e.target.checked })} className="rounded bg-slate-950 border-slate-700" />Palier actif</label>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-bold text-slate-200">Modules inclus</span>
                  <span className="text-[11px] font-mono text-slate-400">{form.modules_inclus.length}{cap !== null ? ` / ${cap}` : ''}</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-64 overflow-y-auto p-1">
                  {modules.map(m => {
                    const checked = form.modules_inclus.includes(m.key);
                    const blocked = !checked && cap !== null && form.modules_inclus.length >= cap;
                    return (
                      <label key={m.key} className={`flex items-center gap-2 px-2.5 py-2 rounded-lg border text-xs font-sans cursor-pointer transition-all ${checked ? 'bg-amber-500/10 border-amber-500/40 text-amber-200' : blocked ? 'bg-slate-950 border-slate-800 text-slate-600 cursor-not-allowed' : 'bg-slate-950 border-slate-700 text-slate-300 hover:border-slate-600'}`}>
                        <input type="checkbox" checked={checked} disabled={blocked} onChange={() => toggleModule(m.key)} className="rounded bg-slate-950 border-slate-700" />
                        <span className="truncate" title={m.label}>{m.label}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
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
  return <div><label className="block text-xs font-semibold text-slate-400 mb-1">{label}{disabled && ' (verrouillé)'}</label>{children}</div>;
}
