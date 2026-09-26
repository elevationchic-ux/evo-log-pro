'use client';

// Console Super-Admin CADC — Entreprises (CRUD total + logo + allocation modules).
// Source de vérité tenant : Company + SubscriptionPlan. Le verrou max_modules du
// plan borne le nombre de modules sélectionnables (désactive les cases au-delà).

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Building2, Plus, Search, RefreshCw, Pencil, Trash2, X, Upload,
  CheckCircle2, ShieldCheck, Users2,
} from 'lucide-react';
import { toast } from 'sonner';
import { saasConsoleAPI, getApiBaseUrl } from '@/lib/api-client';

interface CadcModule { key: string; label: string; domain: string }
interface CadcPlan { id: number; code: string; nom: string; max_modules: number | null }
interface CadcCompany {
  id: number; code: string; nom: string; sigle?: string | null; ville?: string | null;
  pays?: string | null; telephone?: string | null; email?: string | null;
  is_active: boolean; subscription_plan_id?: number | null; max_users?: number;
  logo_url?: string | null; modules_actives: string[]; user_count?: number;
}

interface FormState {
  code: string; nom: string; sigle: string; ville: string; pays: string;
  telephone: string; email: string; subscription_plan_id: string; max_users: string;
  is_active: boolean; modules: string[];
}

const emptyForm = (): FormState => ({
  code: '', nom: '', sigle: '', ville: 'Douala', pays: 'Cameroun', telephone: '',
  email: '', subscription_plan_id: '', max_users: '20', is_active: true, modules: [],
});

export default function CadcEntreprisesPage() {
  const [companies, setCompanies] = useState<CadcCompany[]>([]);
  const [plans, setPlans] = useState<CadcPlan[]>([]);
  const [modules, setModules] = useState<CadcModule[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState<CadcCompany | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm());
  const [saving, setSaving] = useState(false);

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [cRes, pRes, mRes] = await Promise.all([
        saasConsoleAPI.listCompanies(search || undefined),
        saasConsoleAPI.listPlans(),
        saasConsoleAPI.getModulesCatalog(),
      ]);
      setCompanies(Array.isArray(cRes.data) ? cRes.data : []);
      setPlans(Array.isArray(pRes.data) ? pRes.data : []);
      setModules(mRes.data?.modules || []);
    } catch (err) {
      console.error(err);
      toast.error('Impossible de charger la console CADC');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { loadAll(); }, [loadAll]);

  const planById = useMemo(() => {
    const map: Record<number, CadcPlan> = {};
    for (const p of plans) map[p.id] = p;
    return map;
  }, [plans]);

  const selectedPlanCap: number | null = form.subscription_plan_id
    ? (planById[Number(form.subscription_plan_id)]?.max_modules ?? null)
    : null;

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm());
    setDrawerOpen(true);
  };

  const openEdit = (c: CadcCompany) => {
    setEditing(c);
    setForm({
      code: c.code, nom: c.nom, sigle: c.sigle || '', ville: c.ville || '', pays: c.pays || 'Cameroun',
      telephone: c.telephone || '', email: c.email || '',
      subscription_plan_id: c.subscription_plan_id ? String(c.subscription_plan_id) : '',
      max_users: String(c.max_users ?? 20), is_active: c.is_active,
      modules: Array.isArray(c.modules_actives) ? [...c.modules_actives] : [],
    });
    setDrawerOpen(true);
  };

  const toggleModule = (key: string) => {
    setForm(prev => {
      if (prev.modules.includes(key)) {
        return { ...prev, modules: prev.modules.filter(m => m !== key) };
      }
      if (selectedPlanCap !== null && prev.modules.length >= selectedPlanCap) {
        toast.warning(`Ce plan limite à ${selectedPlanCap} module(s)`);
        return prev;
      }
      return { ...prev, modules: [...prev.modules, key] };
    });
  };

  const handleSave = async () => {
    if (!form.code.trim() || !form.nom.trim()) {
      toast.error('Le code et le nom sont obligatoires');
      return;
    }
    setSaving(true);
    try {
      if (!editing) {
        await saasConsoleAPI.createCompany({
          code: form.code.trim(), nom: form.nom.trim(), sigle: form.sigle || null,
          ville: form.ville || null, pays: form.pays || null, telephone: form.telephone || null,
          email: form.email || null,
          subscription_plan_id: form.subscription_plan_id ? Number(form.subscription_plan_id) : null,
          max_users: Number(form.max_users) || 10, is_active: form.is_active,
          modules_actives: form.modules,
        });
        toast.success('Entreprise créée');
      } else {
        await saasConsoleAPI.updateCompany(editing.id, {
          nom: form.nom.trim(), sigle: form.sigle || null, ville: form.ville || null,
          pays: form.pays || null, telephone: form.telephone || null, email: form.email || null,
          subscription_plan_id: form.subscription_plan_id ? Number(form.subscription_plan_id) : null,
          max_users: Number(form.max_users) || 10, is_active: form.is_active,
        });
        // Allocation modules distincte (PUT /modules, bornée par le plan).
        if (JSON.stringify([...form.modules].sort()) !== JSON.stringify([...(editing.modules_actives || [])].sort())) {
          await saasConsoleAPI.allocateModules(editing.id, form.modules);
        }
        toast.success('Entreprise mise à jour');
      }
      setDrawerOpen(false);
      loadAll();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Échec de l\'enregistrement');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (c: CadcCompany) => {
    if (!confirm(`Supprimer l'entreprise « ${c.nom} » ?`)) return;
    try {
      await saasConsoleAPI.deleteCompany(c.id);
      toast.success('Entreprise supprimée');
      loadAll();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Suppression impossible');
    }
  };

  const handleLogo = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !editing) return;
    try {
      await saasConsoleAPI.uploadLogo(editing.id, file);
      toast.success('Logo téléversé');
      loadAll();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Échec du téléversement');
    }
  };

  const filtered = companies.filter(c =>
    c.nom.toLowerCase().includes(search.toLowerCase()) || c.code.toLowerCase().includes(search.toLowerCase())
  );

  const logoSrc = (url?: string | null) =>
    url ? (url.startsWith('http') ? url : `${getApiBaseUrl()}${url}`) : null;

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
            Console Super-Admin CADC
          </span>
          <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">T-Code : KCADC_ENT</span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
              <Building2 className="w-8 h-8 text-amber-400" /> Entreprises clientes
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              CRUD total des tenants, logos et allocation de modules bornée par le palier d&apos;abonnement.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={loadAll} className="p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-slate-300 transition-all" title="Rafraîchir">
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-amber-400' : ''}`} />
            </button>
            <button onClick={openCreate} className="px-4 py-2.5 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs rounded-xl flex items-center gap-1.5 transition-colors shadow-lg shadow-amber-600/20">
              <Plus className="w-4 h-4" /> Nouvelle entreprise
            </button>
          </div>
        </div>
      </div>

      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher par nom ou code..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500" />
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Entreprise</th>
                <th className="py-3.5 px-4">Palier</th>
                <th className="py-3.5 px-4 text-center">Modules</th>
                <th className="py-3.5 px-4 text-center">Utilisateurs</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(c => {
                const plan = c.subscription_plan_id ? planById[c.subscription_plan_id] : null;
                return (
                  <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-3">
                        {logoSrc(c.logo_url)
                          ? <img src={logoSrc(c.logo_url) as string} alt="" className="w-8 h-8 rounded-lg object-contain bg-slate-950 border border-slate-800" />
                          : <span className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-500 text-[10px] font-black">{c.nom.slice(0, 2).toUpperCase()}</span>}
                        <div>
                          <div className="font-bold font-sans text-slate-100">{c.nom}</div>
                          <div className="text-[11px] text-amber-400 font-mono">{c.code}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-sans">{plan ? `${plan.nom}` : '—'}</td>
                    <td className="py-3.5 px-4 text-center">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 border border-slate-700 text-slate-300">
                        {c.modules_actives?.length || 0}{plan?.max_modules ? ` / ${plan.max_modules}` : ''}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center font-bold text-blue-400">{c.user_count ?? 0}</td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${c.is_active ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                        {c.is_active ? 'ACTIF' : 'INACTIF'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => openEdit(c)} className="px-2.5 py-1 text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-bold border border-slate-700 transition-all flex items-center gap-1">
                          <Pencil className="w-3 h-3" /> Éditer
                        </button>
                        <button onClick={() => handleDelete(c)} className="p-1.5 text-red-400 hover:bg-red-500/10 rounded-lg border border-transparent hover:border-red-500/30 transition-all" title="Supprimer">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
              {!loading && filtered.length === 0 && (
                <tr><td colSpan={6} className="py-10 text-center text-slate-500 font-sans">Aucune entreprise.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {drawerOpen && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm" onClick={() => setDrawerOpen(false)} />
          <div className="relative h-full w-full max-w-lg bg-slate-900 border-l border-slate-800 shadow-2xl overflow-y-auto">
            <div className="sticky top-0 bg-slate-900/95 backdrop-blur border-b border-slate-800 px-6 py-4 flex items-center justify-between z-10">
              <h2 className="text-lg font-black text-slate-100">{editing ? `Éditer — ${editing.nom}` : 'Nouvelle entreprise'}</h2>
              <button onClick={() => setDrawerOpen(false)} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Field label="Code" disabled={!!editing}>
                  <input value={form.code} onChange={e => setForm({ ...form, code: e.target.value })} disabled={!!editing}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100 disabled:opacity-50" />
                </Field>
                <Field label="Sigle">
                  <input value={form.sigle} onChange={e => setForm({ ...form, sigle: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" />
                </Field>
              </div>
              <Field label="Nom">
                <input value={form.nom} onChange={e => setForm({ ...form, nom: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" />
              </Field>
              <div className="grid grid-cols-2 gap-4">
                <Field label="Ville"><input value={form.ville} onChange={e => setForm({ ...form, ville: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Pays"><input value={form.pays} onChange={e => setForm({ ...form, pays: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Téléphone"><input value={form.telephone} onChange={e => setForm({ ...form, telephone: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Email"><input value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Palier d'abonnement">
                  <select value={form.subscription_plan_id} onChange={e => setForm({ ...form, subscription_plan_id: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100">
                    <option value="">Aucun</option>
                    {plans.map(p => <option key={p.id} value={p.id}>{p.nom}{p.max_modules ? ` (max ${p.max_modules} modules)` : ''}</option>)}
                  </select>
                </Field>
                <Field label="Max utilisateurs"><input type="number" value={form.max_users} onChange={e => setForm({ ...form, max_users: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
              </div>
              <label className="flex items-center gap-2 text-sm text-slate-300">
                <input type="checkbox" checked={form.is_active} onChange={e => setForm({ ...form, is_active: e.target.checked })} className="rounded bg-slate-950 border-slate-700" />
                Entreprise active
              </label>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-bold text-slate-200 flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-amber-400" /> Modules alloués</span>
                  <span className="text-[11px] font-mono text-slate-400">
                    {form.modules.length}{selectedPlanCap !== null ? ` / ${selectedPlanCap}` : ''}
                  </span>
                </div>
                {selectedPlanCap !== null && (
                  <p className="text-[11px] text-amber-400/80 mb-2">Verrou du palier : {selectedPlanCap} module(s) maximum.</p>
                )}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-64 overflow-y-auto p-1">
                  {modules.map(m => {
                    const checked = form.modules.includes(m.key);
                    const blocked = !checked && selectedPlanCap !== null && form.modules.length >= selectedPlanCap;
                    return (
                      <label key={m.key} className={`flex items-center gap-2 px-2.5 py-2 rounded-lg border text-xs font-sans cursor-pointer transition-all ${checked ? 'bg-amber-500/10 border-amber-500/40 text-amber-200' : blocked ? 'bg-slate-950 border-slate-800 text-slate-600 cursor-not-allowed' : 'bg-slate-950 border-slate-700 text-slate-300 hover:border-slate-600'}`}>
                        <input type="checkbox" checked={checked} disabled={blocked} onChange={() => toggleModule(m.key)} className="rounded bg-slate-950 border-slate-700" />
                        <span className="truncate" title={m.label}>{m.label}</span>
                      </label>
                    );
                  })}
                </div>
              </div>

              {editing && (
                <div className="pt-2 border-t border-slate-800">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold text-slate-200 flex items-center gap-2"><Upload className="w-4 h-4 text-amber-400" /> Logo</span>
                    {logoSrc(editing.logo_url) && <img src={logoSrc(editing.logo_url) as string} alt="logo" className="w-10 h-10 rounded-lg object-contain bg-slate-950 border border-slate-800" />}
                  </div>
                  <input type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml,image/gif" onChange={handleLogo}
                    className="block w-full text-xs text-slate-400 file:mr-3 file:px-3 file:py-2 file:rounded-lg file:border-0 file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700" />
                </div>
              )}
            </div>
            <div className="sticky bottom-0 bg-slate-900/95 backdrop-blur border-t border-slate-800 px-6 py-4 flex justify-end gap-3">
              <button onClick={() => setDrawerOpen(false)} className="px-4 py-2 text-sm rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700">Annuler</button>
              <button onClick={handleSave} disabled={saving} className="px-4 py-2 text-sm rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-bold disabled:opacity-50 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" /> {saving ? 'Enregistrement...' : 'Enregistrer'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, children, disabled }: { label: string; children: React.ReactNode; disabled?: boolean }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-slate-400 mb-1 flex items-center gap-1">
        {label}
        {disabled && <Users2 className="w-3 h-3 text-slate-500" />}
      </label>
      {children}
    </div>
  );
}
