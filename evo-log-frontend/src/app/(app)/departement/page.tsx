'use client';

// Phase 3 — Ecran "Mon Département" pour le chef de département (niveau 2).
//
// Périmètre strict : le chef ne voit que SA fiche de département (nom, modules
// autorisés, effectif, responsable) et le roster des collaborateurs rattachés à
// son département. Le backend épingle le niveau 2 à son department_id ; toute
// tentative de télécharger un autre département renvoie 403.
//
// Un admin entreprise (1) / CADC (0) qui atteindrait cet écran doit cibler un
// département explicite ; ce n'est pas l'usage prévu ici (ils pilotent via
// l'Administration Entreprise / la console CADC). On affiche alors l'invite
// renvoyée par le backend plutôt que des données inventées (zéro-mock).

import React, { useState, useEffect, useCallback } from 'react';
import { Users, Building2, Mail, Phone, BadgeCheck, UserCog, CircleSlash } from 'lucide-react';
import { toast } from 'sonner';
import { departmentAPI } from '@/lib/api-client';

interface DeptOverview {
  id: number;
  company_id: number;
  code: string;
  nom: string;
  description?: string | null;
  modules_allowed: string[];
  effectif: number;
  manager: { id: number; username: string; full_name?: string | null } | null;
  is_active: boolean;
  role_level_callant: number;
}

interface Member {
  id: number;
  username: string;
  email: string;
  full_name?: string | null;
  matricule?: string | null;
  job_title?: string | null;
  phone?: string | null;
  role_level: number;
  is_active: boolean;
  department_id?: number | null;
  roles: string[];
}

const LEVEL_LABEL: Record<number, string> = {
  0: 'Super Admin',
  1: 'Admin entreprise',
  2: 'Chef de département',
  3: 'Collaborateur',
};

export default function DepartementPage() {
  const [overview, setOverview] = useState<DeptOverview | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setNotice(null);
    try {
      const [ov, mb] = await Promise.all([
        departmentAPI.getOverview(),
        departmentAPI.listMembers(),
      ]);
      setOverview(ov.data);
      setMembers(mb.data);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      if (err?.response?.status === 400 && typeof detail === 'string') {
        // Admin / CADC sans département ciblé : usage non prévu ici.
        setNotice(detail);
      } else {
        toast.error(detail || 'Impossible de charger le département');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) {
    return <div className="p-6 text-slate-400 text-sm">Chargement du département…</div>;
  }

  if (notice || !overview) {
    return (
      <div className="p-6 space-y-2">
        <h1 className="text-xl font-black text-slate-100">Mon Département</h1>
        <p className="text-sm text-amber-300">
          {notice ?? "Aucun département rattaché à ce compte."}
        </p>
        <p className="text-xs text-slate-500">
          La gestion multi-départements se fait depuis l'Administration Entreprise
          ou la console CADC. Cet écran est dédié au chef de département.
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 space-y-6">
      <header className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-xl bg-sky-600 text-white flex items-center justify-center shrink-0">
          <Building2 className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <h1 className="text-xl font-black text-slate-100">{overview.nom}</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Code&nbsp;: {overview.code} · Effectif&nbsp;: {overview.effectif}
            {overview.manager ? ` · Responsable&nbsp: ${overview.manager.full_name || overview.manager.username}` : ''}
          </p>
        </div>
      </header>

      {/* Modules autorisés pour le département */}
      <section className="rounded-xl border border-slate-700 bg-slate-900/60 p-4 space-y-2">
        <h2 className="text-sm font-bold text-slate-200">Modules autorisés</h2>
        {overview.modules_allowed.length === 0 ? (
          <p className="text-xs text-slate-500">Aucun module restreint — hérite de l'allocation entreprise.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {overview.modules_allowed.map(m => (
              <span key={m} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-sky-500/15 text-sky-300 border border-sky-500/30">
                <BadgeCheck className="w-3 h-3" /> {m}
              </span>
            ))}
          </div>
        )}
      </section>

      {/* Roster des collaborateurs */}
      <section className="space-y-2">
        <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <Users className="w-4 h-4" /> Collaborateurs du département
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {members.map(m => (
            <div key={m.id}
              className={`rounded-xl border p-4 space-y-2 ${
                m.is_active ? 'border-slate-700 bg-slate-900/60' : 'border-slate-800 bg-slate-950/40 opacity-70'}`}>
              <div className="flex items-center justify-between gap-2">
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-100 truncate">{m.full_name || m.username}</p>
                  <p className="text-[11px] text-slate-400 truncate">@{m.username}</p>
                </div>
                <span className={`shrink-0 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                  m.is_active ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' : 'bg-slate-800 text-slate-500 border-slate-700'}`}>
                  {m.is_active ? <UserCog className="w-3 h-3" /> : <CircleSlash className="w-3 h-3" />}
                  {LEVEL_LABEL[m.role_level] ?? `Niv. ${m.role_level}`}
                </span>
              </div>
              {m.job_title && <p className="text-xs text-slate-400">{m.job_title}</p>}
              <div className="text-[11px] text-slate-400 space-y-1">
                {m.matricule && <p className="font-mono">Mat. {m.matricule}</p>}
                <p className="flex items-center gap-1 truncate"><Mail className="w-3 h-3 shrink-0" /> {m.email}</p>
                {m.phone && <p className="flex items-center gap-1"><Phone className="w-3 h-3 shrink-0" /> {m.phone}</p>}
              </div>
              {m.roles.length > 0 && (
                <div className="flex flex-wrap gap-1 pt-1">
                  {m.roles.map(r => (
                    <span key={r} className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">{r}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
