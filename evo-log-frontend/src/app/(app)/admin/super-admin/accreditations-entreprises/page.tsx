'use client';

// Console Super-Admin CADC — Accréditations d'entreprise (délai).
// Un accord module daté (permission_code "module.*.*", date_debut/date_fin) débloque
// un module pour un collaborateur ciblé au-delà de l'allocation de base de son entreprise.

import React, { useState, useEffect, useCallback } from 'react';
import { ShieldAlert, RefreshCw, Plus, Trash2, X, CheckCircle2, Building2 } from 'lucide-react';
import { toast } from 'sonner';
import { saasConsoleAPI, adminAPI } from '@/lib/api-client';

interface CadcModule { key: string; label: string; domain: string }
interface Option { id: number; code: string; nom: string }
interface SimpleUser { id: number; username: string; full_name: string; role_level?: number }
interface CadcAccred {
  id: number; user_id: number; code: string; libelle?: string; module?: string;
  permission_code?: string; date_debut?: string | null; date_fin?: string | null;
  statut?: string; valide: boolean;
}

const toISO = (d: Date) => d.toISOString().slice(0, 10);

export default function CadcAccreditationsPage() {
  const [companies, setCompanies] = useState<Option[]>([]);
  const [modules, setModules] = useState<CadcModule[]>([]);
  const [companyId, setCompanyId] = useState<string>('');
  const [accreds, setAccreds] = useState<CadcAccred[]>([]);
  const [users, setUsers] = useState<SimpleUser[]>([]);
  const [loading, setLoading] = useState(false);

  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ user_id: '', module: '', libelle: '', date_debut: '', date_fin: '', motif: '' });

  const loadMeta = useCallback(async () => {
    try {
      const [cRes, mRes] = await Promise.all([saasConsoleAPI.listCompanies(), saasConsoleAPI.getModulesCatalog()]);
      setCompanies((Array.isArray(cRes.data) ? cRes.data : []).map((c: any) => ({ id: c.id, code: c.code, nom: c.nom })));
      setModules(mRes.data?.modules || []);
    } catch {
      toast.error('Chargement des référentiels impossible');
    }
  }, []);

  useEffect(() => { loadMeta(); }, [loadMeta]);

  const loadAccreditations = useCallback(async (cid: string) => {
    if (!cid) { setAccreds([]); setUsers([]); return; }
    setLoading(true);
    try {
      const [aRes, uRes] = await Promise.all([
        saasConsoleAPI.listCompanyAccreditations(Number(cid)),
        adminAPI.getUsers({ company_id: Number(cid), limit: 500 }),
      ]);
      setAccreds(Array.isArray(aRes.data) ? aRes.data : []);
      setUsers(Array.isArray(uRes.data) ? uRes.data : []);
    } catch (err) {
      console.error(err);
      toast.error('Chargement des accréditations impossible');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadAccreditations(companyId); }, [companyId, loadAccreditations]);

  const openGrant = () => {
    setForm({ user_id: '', module: '', libelle: '', date_debut: toISO(new Date()), date_fin: '', motif: '' });
    setModalOpen(true);
  };

  const handleGrant = async () => {
    if (!companyId) { toast.error('Choisissez une entreprise'); return; }
    if (!form.user_id || !form.module) { toast.error('Collaborateur et module requis'); return; }
    setSaving(true);
    try {
      await saasConsoleAPI.grantCompanyAccreditation(Number(companyId), {
        user_id: Number(form.user_id), module: form.module,
        libelle: form.libelle || null, date_debut: form.date_debut || null,
        date_fin: form.date_fin || null, motif: form.motif || null,
      });
      toast.success('Accréditation accordée');
      setModalOpen(false);
      loadAccreditations(companyId);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Échec de l\'octroi');
    } finally { setSaving(false); }
  };

  const handleRevoke = async (a: CadcAccred) => {
    if (!confirm(`Révoquer l'accréditation ${a.code} ?`)) return;
    try {
      await saasConsoleAPI.revokeCompanyAccreditation(Number(companyId), a.id);
      toast.success('Accréditation révoquée');
      loadAccreditations(companyId);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Révocation impossible');
    }
  };

  const userName = (id: number) => users.find(u => u.id === id)?.full_name || `#${id}`;

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">Console Super-Admin CADC</span>
          <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">T-Code : KCADC_ACR</span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3"><ShieldAlert className="w-8 h-8 text-amber-400" /> Accréditations d&apos;entreprise</h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">Accords module datés débloquant un accès pour un collaborateur, au-delà de l&apos;allocation de base.</p>
          </div>
          <div className="flex items-center gap-2">
            <select value={companyId} onChange={e => setCompanyId(e.target.value)} className="px-3 py-2.5 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-100 flex-1 sm:w-64">
              <option value="">— Choisir une entreprise —</option>
              {companies.map(c => <option key={c.id} value={c.id}>{c.nom} ({c.code})</option>)}
            </select>
            <button onClick={() => loadAccreditations(companyId)} disabled={!companyId} className="p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-slate-300 disabled:opacity-40"><RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-amber-400' : ''}`} /></button>
            <button onClick={openGrant} disabled={!companyId} className="px-4 py-2.5 bg-amber-600 hover:bg-amber-500 disabled:opacity-40 text-white font-bold text-xs rounded-xl flex items-center gap-1.5"><Plus className="w-4 h-4" /> Accorder</button>
          </div>
        </div>
      </div>

      {!companyId ? (
        <div className="bg-slate-900/60 border border-dashed border-slate-800 rounded-3xl p-12 text-center">
          <Building2 className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <p className="text-sm text-slate-500 font-sans">Sélectionnez une entreprise pour gérer ses accréditations.</p>
        </div>
      ) : (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider bg-slate-950">
                  <th className="py-3.5 px-4">Collaborateur</th>
                  <th className="py-3.5 px-4">Module</th>
                  <th className="py-3.5 px-4">Code</th>
                  <th className="py-3.5 px-4 text-center">Période</th>
                  <th className="py-3.5 px-4 text-center">Validité</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {accreds.map(a => (
                  <tr key={a.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-sans">{userName(a.user_id)}</td>
                    <td className="py-3.5 px-4"><span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-amber-300 font-mono text-[11px]">{a.module}</span></td>
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-500">{a.code}</td>
                    <td className="py-3.5 px-4 text-center text-[11px]">{a.date_debut || '…'} → {a.date_fin || 'illimité'}</td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${a.valide ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>{a.valide ? 'VALIDE' : 'EXPIRÉE'}</span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button onClick={() => handleRevoke(a)} className="p-1.5 text-red-400 hover:bg-red-500/10 rounded-lg border border-transparent hover:border-red-500/30" title="Révoquer"><Trash2 className="w-4 h-4" /></button>
                    </td>
                  </tr>
                ))}
                {!loading && accreds.length === 0 && <tr><td colSpan={6} className="py-10 text-center text-slate-500 font-sans">Aucune accréditation pour cette entreprise.</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm" onClick={() => setModalOpen(false)} />
          <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl">
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <h2 className="text-lg font-black text-slate-100">Accorder une accréditation</h2>
              <button onClick={() => setModalOpen(false)} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6 space-y-4">
              <Field label="Collaborateur">
                <select value={form.user_id} onChange={e => setForm({ ...form, user_id: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100">
                  <option value="">— Choisir —</option>
                  {users.map(u => <option key={u.id} value={u.id}>{u.full_name} ({u.username})</option>)}
                </select>
              </Field>
              <Field label="Module débloqué">
                <select value={form.module} onChange={e => setForm({ ...form, module: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100">
                  <option value="">— Choisir —</option>
                  {modules.map(m => <option key={m.key} value={m.key}>{m.label}</option>)}
                </select>
              </Field>
              <Field label="Libellé"><input value={form.libelle} onChange={e => setForm({ ...form, libelle: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" placeholder="Ex: Mission portuaire Kribi" /></Field>
              <div className="grid grid-cols-2 gap-4">
                <Field label="Date de début"><input type="date" value={form.date_debut} onChange={e => setForm({ ...form, date_debut: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
                <Field label="Date de fin (délai)"><input type="date" value={form.date_fin} onChange={e => setForm({ ...form, date_fin: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
              </div>
              <Field label="Motif"><input value={form.motif} onChange={e => setForm({ ...form, motif: e.target.value })} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" /></Field>
            </div>
            <div className="px-6 py-4 border-t border-slate-800 flex justify-end gap-3">
              <button onClick={() => setModalOpen(false)} className="px-4 py-2 text-sm rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700">Annuler</button>
              <button onClick={handleGrant} disabled={saving} className="px-4 py-2 text-sm rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-bold disabled:opacity-50 flex items-center gap-2"><CheckCircle2 className="w-4 h-4" /> {saving ? 'Octroi...' : 'Accorder'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div><label className="block text-xs font-semibold text-slate-400 mb-1">{label}</label>{children}</div>;
}
