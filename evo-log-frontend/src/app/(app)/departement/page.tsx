'use client';

// Phase 3 — Ecran "Mon Département" pour le chef de département (niveau 2).
//
// Périmètre strict : le chef ne voit et ne pilote que SA fiche de département
// (nom, modules autorisés, effectif, responsable) et le roster des collaborateurs
// rattachés à son département. Le backend épingle le niveau 2 à son department_id ;
// toute tentative de télécharger un autre département renvoie 403.
//
// Tranche C (écritures) : le chef peut AFFECTER un collaborateur (niveau 3) de son
// entreprise à son département et en RETIRER un. Ces actions ne font qu'appeler le
// backend scope (require_department_head + _scoped_department + _guard_target) :
// si l'autorisation manque, le 403/400 backend s'affiche honnêtement (zéro-mock).
//
// L'allocation des MODULES d'un département relève de l'Admin Entreprise (1) / CADC
// (0) et reste en lecture ici (un chef ne se auto-grantit pas ; cf. PUT /modules 403).
//
// Un admin entreprise (1) / CADC (0) qui atteindrait cet écran doit cibler un
// département explicite ; ce n'est pas l'usage prévu ici. On affiche alors l'invite
// renvoyée par le backend plutôt que des données inventées.

import React, { useState, useEffect, useCallback } from 'react';
import { Users, Building2, Mail, Phone, BadgeCheck, UserCog, CircleSlash, UserPlus, UserMinus, Search, CalendarDays, Clock, Plus, Trash2, CheckCircle2 } from 'lucide-react';
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

interface PlanningLine {
  id: number;
  employe_id: number;
  employe_username: string;
  employe_nom: string;
  date_jour: string | null;
  quart: string;
  poste_assigne: string;
  statut: string;
  observations?: string | null;
}

interface PlanningData {
  departement_id: number;
  departement_nom: string;
  semaine: string;
  du: string;
  au: string;
  lignes: PlanningLine[];
}

interface PresenceRow {
  employe_id: number;
  username: string;
  full_name: string;
  planifie: boolean;
  quart: string | null;
  poste_assigne: string | null;
  pointe: boolean;
  heure_arrivee: string | null;
  heure_depart: string | null;
  heures_effectives: number | null;
  est_valide: boolean | null;
  presence: 'PRESENT' | 'ATTENDU' | 'NON_PLANIFIE';
}

interface PresenceData {
  departement_id: number;
  departement_nom: string;
  date: string;
  collaborateurs: PresenceRow[];
  synthese: { effectif: number; presents: number; attendus: number; non_planifies: number };
}

const PRESENCE_STYLE: Record<PresenceRow['presence'], string> = {
  PRESENT: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  ATTENDU: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  NON_PLANIFIE: 'bg-slate-800 text-slate-400 border-slate-700',
};

const LEVEL_LABEL: Record<number, string> = {
  0: 'Super Admin',
  1: 'Admin entreprise',
  2: 'Chef de département',
  3: 'Collaborateur',
};

function errMsg(err: any, fallback: string): string {
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return String(detail[0].msg);
  return fallback;
}

export default function DepartementPage() {
  const [overview, setOverview] = useState<DeptOverview | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [candidates, setCandidates] = useState<Member[]>([]);
  const [planning, setPlanning] = useState<PlanningData | null>(null);
  const [presence, setPresence] = useState<PresenceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [filter, setFilter] = useState('');
  // Phase 4 Tranche B : planning create form toggle + fields.
  const [showPlanForm, setShowPlanForm] = useState(false);
  const [planForm, setPlanForm] = useState({ employe_id: '', date_jour: '', quart: 'STANDARD', poste_assigne: '' });
  const [planBusy, setPlanBusy] = useState(false);

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
      // Les candidats mobilisables ne concernent que le chef (le backend épingle son
      // département) ; pour un admin/CADC sans département ciblé, l'appel echoue en
      // 400 — on laisse simplement la liste vide (la vue "notice" s'affiche déjà).
      // Lectures Phase 4 scopees (planning + presence) : meme perimetre chef. Elles
      // echouent en 400 pour un admin/CADC sans département ciblé — on laisse alors
      // les sections vides (la vue "notice" s'affiche déjà pour ces rôles).
      try {
        const [cd, pl, pr] = await Promise.all([
          departmentAPI.listCandidates(),
          departmentAPI.getPlanning(),
          departmentAPI.getPresence(),
        ]);
        setCandidates(cd.data);
        setPlanning(pl.data);
        setPresence(pr.data);
      } catch {
        setCandidates([]);
        setPlanning(null);
        setPresence(null);
      }
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      if (err?.response?.status === 400 && typeof detail === 'string') {
        // Admin / CADC sans département ciblé : usage non prévu ici.
        setNotice(detail);
      } else {
        toast.error(errMsg(err, 'Impossible de charger le département'));
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  // Le chef (niveau 2) est le seul à atteindre la vue "overview" ; les niveaux 0/1
  // tombent sur la vue "notice". On derive neanmoins la competence du perimetre.
  const canManage = !!overview && overview.role_level_callant <= 2;

  async function handleAffect(member: Member) {
    setBusyId(member.id);
    try {
      await departmentAPI.affectMember(member.id);
      toast.success(`${member.full_name || member.username} ajouté au département`);
      await load();
    } catch (err: any) {
      toast.error(errMsg(err, "Échec de l'affectation"));
    } finally {
      setBusyId(null);
    }
  }

  async function handleRetire(member: Member) {
    setBusyId(member.id);
    try {
      await departmentAPI.removeMember(member.id);
      toast.success(`${member.full_name || member.username} retiré du département`);
      await load();
    } catch (err: any) {
      toast.error(errMsg(err, 'Échec du retrait'));
    } finally {
      setBusyId(null);
    }
  }

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

  const q = filter.trim().toLowerCase();
  const shownCandidates = q
    ? candidates.filter(c =>
        [c.username, c.full_name, c.matricule, c.email]
          .some(v => v && String(v).toLowerCase().includes(q)))
    : candidates;

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
            {overview.manager ? ` · Responsable : ${overview.manager.full_name || overview.manager.username}` : ''}
          </p>
        </div>
      </header>

      {/* Modules autorisés pour le département (lecture seule ici) */}
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
        <p className="text-[11px] text-slate-500 pt-1">
          L'allocation des modules d'un département relève de l'Administration Entreprise / CADC.
        </p>
      </section>

      {/* Presence du jour (statuts deduits des lignes reelles) */}
      <section className="rounded-xl border border-slate-700 bg-slate-900/60 p-4 space-y-3">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Clock className="w-4 h-4" /> Présence {presence ? `· ${presence.date}` : ''}
          </h2>
          {presence && (
            <div className="flex flex-wrap gap-1.5 text-[11px]">
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                {presence.synthese.presents} présents
              </span>
              <span className="px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
                {presence.synthese.attendus} attendus
              </span>
              <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                {presence.synthese.non_planifies} non planifiés
              </span>
            </div>
          )}
        </div>
        {!presence ? (
          <p className="text-xs text-slate-500">Aucune donnée de présence disponible.</p>
        ) : presence.collaborateurs.length === 0 ? (
          <p className="text-xs text-slate-500">Aucun collaborateur rattaché à ce département.</p>
        ) : (
          <ul className="divide-y divide-slate-800">
            {presence.collaborateurs.map(c => (
              <li key={c.employe_id} className="py-2 flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-sm text-slate-100 truncate">{c.full_name}</p>
                  <p className="text-[11px] text-slate-400 truncate">
                    @{c.username}
                    {c.planifie && c.quart ? ` · ${c.quart}${c.poste_assigne ? ` (${c.poste_assigne})` : ''}` : ''}
                  </p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  {c.pointe && (
                    <span className="text-[11px] font-mono text-slate-400">
                      {c.heure_arrivee}{c.heure_depart ? ` → ${c.heure_depart}` : ''}
                    </span>
                  )}
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold border ${PRESENCE_STYLE[c.presence]}`}>
                    {c.presence}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Planning de la semaine (tours de garde des collaborateurs) */}
      <section className="rounded-xl border border-slate-700 bg-slate-900/60 p-4 space-y-3">
        <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <CalendarDays className="w-4 h-4" /> Planning {planning ? `· ${planning.semaine} (${planning.du} → ${planning.au})` : ''}
        </h2>
        {!planning ? (
          <p className="text-xs text-slate-500">Aucune donnée de planning disponible.</p>
        ) : planning.lignes.length === 0 ? (
          <p className="text-xs text-slate-500">Aucun tour de garde planifié cette semaine pour le département.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-400">
                <tr className="border-b border-slate-800">
                  <th className="py-2 pr-3 font-semibold">Jour</th>
                  <th className="py-2 pr-3 font-semibold">Collaborateur</th>
                  <th className="py-2 pr-3 font-semibold">Quart</th>
                  <th className="py-2 pr-3 font-semibold">Poste</th>
                  <th className="py-2 font-semibold">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {planning.lignes.map(l => (
                  <tr key={l.id}>
                    <td className="py-2 pr-3 font-mono text-slate-300">{l.date_jour}</td>
                    <td className="py-2 pr-3 text-slate-100">{l.employe_nom}</td>
                    <td className="py-2 pr-3 text-slate-300">{l.quart}</td>
                    <td className="py-2 pr-3 text-slate-400">{l.poste_assigne}</td>
                    <td className="py-2">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                        {l.statut}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Affecter un collaborateur (competence du chef) */}
      {canManage && (
        <section className="rounded-xl border border-slate-700 bg-slate-900/60 p-4 space-y-3">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <UserPlus className="w-4 h-4" /> Affecter un collaborateur
          </h2>
          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              value={filter}
              onChange={e => setFilter(e.target.value)}
              placeholder="Rechercher par nom, identifiant, matricule…"
              className="w-full rounded-lg bg-slate-950/60 border border-slate-700 pl-9 pr-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
            />
          </div>
          {shownCandidates.length === 0 ? (
            <p className="text-xs text-slate-500">
              {candidates.length === 0
                ? "Tous les collaborateurs de l'entreprise sont déjà rattachés à votre département."
                : 'Aucun collaborateur ne correspond à cette recherche.'}
            </p>
          ) : (
            <ul className="flex flex-wrap gap-2">
              {shownCandidates.map(c => (
                <li key={c.id}>
                  <button
                    type="button"
                    onClick={() => handleAffect(c)}
                    disabled={busyId === c.id}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-100 border border-slate-700 hover:border-sky-500/50 hover:bg-sky-500/10 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    <UserPlus className="w-3.5 h-3.5" />
                    <span>{c.full_name || c.username}</span>
                    <span className="text-slate-500">@{c.username}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

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
              {canManage && m.role_level === 3 && (
                <div className="pt-1">
                  <button
                    type="button"
                    onClick={() => handleRetire(m)}
                    disabled={busyId === m.id}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-slate-800 text-rose-300 border border-slate-700 hover:border-rose-500/50 hover:bg-rose-500/10 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    <UserMinus className="w-3.5 h-3.5" /> Retirer du département
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
