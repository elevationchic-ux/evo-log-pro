'use client';

// Phase 2  Profil Entreprise (SaaS) pour l'admin entreprise (niveau 1).
//
// Contrats backend : /api/v1/company-admin/profil (GET/PATCH) et
// /api/v1/company-admin/utilisateurs (GET), gardés require_company_admin +
// resolve_scope_company_id. L'admin entreprise est épinglé à sa société ; le
// CADC (niveau 0 / superuser) n'a pas de company_id propre et choisit donc
// l'entreprise ciblée via le sélecteur (paramètre company_id explicite).
//
// Distinction volontaire avec /company (fiche légale OHADA : NIF, RCCM,
// agréments, RIB) : cet écran expose l'IDENTITÉ SAAS du tenant  plan
// d'abonnement, verrous max_modules / max_users, modules alloués par le CADC
// et admins désignés (niveau 1)  et n'édite que les champs de marque
// autorisés par CompanyProfileUpdate (nom, sigle, coordonnées, couleur).

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Building, CreditCard, Layers, Users, Crown, Save, Palette,
} from 'lucide-react';
import { toast } from 'sonner';
import { companyAdminAPI, saasConsoleAPI } from '@/lib/api-client';
import { useAuth } from '@/components/shared/AuthProvider';

interface PlanInfo { id: number; nom: string; code: string; max_modules: number | null; max_users: number | null }
interface Profile {
  id: number; code: string; nom: string; sigle?: string | null;
  ville?: string | null; pays?: string | null; telephone?: string | null;
  email?: string | null; website?: string | null; logo_url?: string | null;
  primary_color?: string | null; is_active: boolean;
  plan: PlanInfo | null; modules_actives: string[]; user_count: number;
  role_level: number;
}
interface Member {
  id: number; username: string; email?: string | null; full_name?: string | null;
  role_level: number; is_active: boolean; is_superuser: boolean;
  must_change_password: boolean; roles: string[];
}

const EDITABLE_FIELDS: Array<{ key: keyof Profile; label: string; type?: string }> = [
  { key: 'nom', label: 'Raison sociale *' },
  { key: 'sigle', label: 'Sigle' },
  { key: 'ville', label: 'Ville' },
  { key: 'telephone', label: 'Téléphone' },
  { key: 'email', label: 'Email', type: 'email' },
  { key: 'website', label: 'Site web' },
];

export default function AdminEntrepriseProfilPage() {
  const { user } = useAuth();
  const isCadc = Boolean((user as any)?.isSuperuser) || Number((user as any)?.roleLevel ?? 9) === 0;

  const [companies, setCompanies] = useState<Array<{ id: number; nom: string }>>([]);
  const [targetId, setTargetId] = useState<number | undefined>(undefined);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [form, setForm] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Le CADC doit cibler une entreprise (400 sinon côté backend) ; l'admin
  // entreprise est épinglé à la sienne  pas de sélecteur pour lui.
  useEffect(() => {
    if (!isCadc) return;
    saasConsoleAPI.listCompanies().then(res => {
      const list = (res.data || []).map((c: any) => ({ id: c.id, nom: c.nom || c.code }));
      setCompanies(list);
      if (list.length) setTargetId(list[0].id);
    }).catch(() => toast.error('Liste des entreprises illisible (accès CADC requis).'));
  }, [isCadc]);

  const load = useCallback(async () => {
    if (isCadc && targetId == null) { setLoading(false); return; }
    setLoading(true);
    try {
      const [p, m] = await Promise.all([
        companyAdminAPI.getProfile(targetId),
        companyAdminAPI.listMembers(undefined, targetId),
      ]);
      setProfile(p.data);
      setMembers(m.data || []);
      const f: Record<string, string> = {};
      for (const { key } of EDITABLE_FIELDS) f[key] = (p.data as any)[key] ?? '';
      f.primary_color = p.data.primary_color ?? '';
      setForm(f);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Impossible de charger le profil entreprise');
    } finally {
      setLoading(false);
    }
  }, [isCadc, targetId]);

  useEffect(() => { load(); }, [load]);

  const admins = useMemo(
    () => members.filter(m => m.role_level <= 1 || m.is_superuser),
    [members],
  );

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {};
      for (const { key } of EDITABLE_FIELDS) {
        const v = (form[key] || '').trim();
        if (key === 'nom' && !v) { toast.error('La raison sociale est obligatoire.'); setSaving(false); return; }
        if (v) payload[key] = v;
      }
      if (form.primary_color) payload.primary_color = form.primary_color;
      await companyAdminAPI.updateProfile(payload, isCadc ? profile.id : undefined);
      toast.success('Profil entreprise mis à jour');
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Enregistrement impossible');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-6 text-slate-400 text-sm">Chargement du profil…</div>;
  if (!profile) {
    return (
      <div className="p-6 text-slate-500 text-sm">
        {isCadc ? 'Sélectionnez une entreprise pour piloter son profil SaaS.' : "Aucune entreprise rattachée à votre compte."}
      </div>
    );
  }

  const quotaUsers = profile.plan?.max_users == null ? `${profile.user_count}` : `${profile.user_count}/${profile.plan.max_users}`;
  const quotaModules = profile.plan?.max_modules == null ? `${profile.modules_actives.length}` : `${profile.modules_actives.length}/${profile.plan.max_modules}`;

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-4xl mx-auto">
      <header className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0">
          <Building className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-black text-slate-100 truncate">Profil Entreprise (SaaS)</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Identité du tenant, abonnement CADC et admins désignés  distincte de la fiche légale (page « Fiche Entreprise »).
          </p>
        </div>
        {isCadc && companies.length > 0 && (
          <select
            value={targetId ?? ''}
            onChange={e => setTargetId(Number(e.target.value))}
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
            aria-label="Entreprise ciblée"
          >
            {companies.map(c => <option key={c.id} value={c.id}>{c.nom}</option>)}
          </select>
        )}
      </header>

      {/* Carte abonnement */}
      <section className="rounded-xl border border-slate-700 bg-slate-900/60 p-4 space-y-3">
        <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <CreditCard className="w-4 h-4 text-emerald-400" /> Abonnement &amp; quotas
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
          <div>
            <p className="text-[11px] text-slate-500">Plan</p>
            <p className="font-semibold text-slate-100">{profile.plan ? profile.plan.nom : 'Aucun plan (CADC non abonné)'}</p>
          </div>
          <div>
            <p className="text-[11px] text-slate-500">Statut</p>
            <p className={`font-semibold ${profile.is_active ? 'text-emerald-400' : 'text-red-400'}`}>
              {profile.is_active ? 'Active' : 'Suspendue'}
            </p>
          </div>
          <div>
            <p className="text-[11px] text-slate-500">Collaborateurs</p>
            <p className="font-semibold text-slate-100">{quotaUsers}</p>
          </div>
          <div>
            <p className="text-[11px] text-slate-500">Modules alloués</p>
            <p className="font-semibold text-slate-100">{quotaModules}</p>
          </div>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {profile.modules_actives.length === 0 ? (
            <span className="text-xs text-slate-500">Aucun module alloué par le CADC.</span>
          ) : profile.modules_actives.map(m => (
            <span key={m} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
              <Layers className="w-3 h-3" /> {m}
            </span>
          ))}
        </div>
      </section>

      {/* Admins désignés */}
      <section className="rounded-xl border border-slate-700 bg-slate-900/60 p-4 space-y-3">
        <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <Crown className="w-4 h-4 text-amber-400" /> Admins désignés (niveau 1)
        </h2>
        {admins.length === 0 ? (
          <p className="text-xs text-slate-500">
            Aucun admin entreprise  le CADC doit en désigner un (console SaaS) pour l&apos;administration interne.
          </p>
        ) : (
          <ul className="divide-y divide-slate-800">
            {admins.map(a => (
              <li key={a.id} className="py-2 flex items-center justify-between gap-3 text-sm">
                <div className="min-w-0">
                  <p className="font-semibold text-slate-100 truncate">
                    {a.full_name || a.username}
                    {a.is_superuser && <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-violet-500/15 text-violet-300 border border-violet-500/30">CADC</span>}
                  </p>
                  <p className="text-[11px] text-slate-500 truncate">{a.email}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {a.must_change_password && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30">Mot de passe temp.</span>
                  )}
                  <span className={`text-[11px] font-semibold ${a.is_active ? 'text-emerald-400' : 'text-red-400'}`}>
                    {a.is_active ? 'Actif' : 'Inactif'}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
        <p className="text-[11px] text-slate-500 flex items-center gap-1">
          <Users className="w-3 h-3" /> {members.length} collaborateur(s) rattaché(s) à l&apos;entreprise.
        </p>
      </section>

      {/* Edition champs de marque */}
      <form onSubmit={save} className="rounded-xl border border-slate-700 bg-slate-900/60 p-4 space-y-4">
        <h2 className="text-sm font-bold text-slate-200">Informations modifiables</h2>
        <p className="text-[11px] text-slate-500 -mt-2">
          Code tenant ({profile.code}) et plan verrouillés côté CADC. La fiche légale (NIF, RCCM, agréments, RIB)
          se gère dans « Fiche &amp; Identité de l&apos;Entreprise ».
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {EDITABLE_FIELDS.map(({ key, label, type }) => (
            <div key={key}>
              <label className="block text-xs font-semibold text-slate-400 mb-1">{label}</label>
              <input
                type={type || 'text'}
                value={form[key] || ''}
                onChange={e => setForm({ ...form, [key]: e.target.value })}
                className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100 focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          ))}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1 flex items-center gap-1">
              <Palette className="w-3.5 h-3.5" /> Couleur principale
            </label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                value={/^#[0-9a-fA-F]{6}$/.test(form.primary_color || '') ? form.primary_color : '#6366f1'}
                onChange={e => setForm({ ...form, primary_color: e.target.value })}
                className="w-10 h-10 rounded-lg bg-slate-800 border border-slate-700 cursor-pointer"
                aria-label="Couleur principale"
              />
              <input
                value={form.primary_color || ''}
                onChange={e => setForm({ ...form, primary_color: e.target.value })}
                placeholder="#6366f1"
                className="flex-1 px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm font-mono text-slate-100 focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>
        </div>
        <div className="flex justify-end">
          <button type="submit" disabled={saving}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50">
            <Save className="w-4 h-4" /> {saving ? 'Enregistrement…' : 'Enregistrer'}
          </button>
        </div>
      </form>
    </div>
  );
}
