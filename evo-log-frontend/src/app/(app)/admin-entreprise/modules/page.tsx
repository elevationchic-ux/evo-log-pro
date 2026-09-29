'use client';

// Phase 2  Ecran "Modules alloués / demandés" pour l'admin entreprise (niveau 1).
//
// Le CADC alloue un sous-ensemble de modules à l'entreprise (borne par le verrou
// max_modules du plan). L'admin voit l'état de CHAQUE module du catalogue :
//   - alloué      : dans Company.modules_actives ;
//   - accrédité   : une accréditation CADC datée en cours le débloque ;
//   - demande     : une demande est en attente d'arbitrage CADC ;
//   - verrouillé  : ni alloué ni accrédité  visible mais non accessible (grisé).
// Il peut émettre une demande d'accréditation vers le CADC pour un module
// verrouillé ; la demande n'accorde aucun droit tant qu'elle n'est pas convertie.

import React, { useState, useEffect, useCallback } from 'react';
import { Layers, Lock, CheckCircle2, Clock, Send, X, ShieldQuestion } from 'lucide-react';
import { toast } from 'sonner';
import { companyAdminAPI } from '@/lib/api-client';

interface ModuleState { key: string; etat: 'alloue' | 'accredite' | 'demande' | 'verrouille' }
interface DemandeItem { id: number; code: string; module: string; libelle?: string; motif?: string }
interface Overview {
  company_id: number;
  modules_actives: string[];
  max_modules: number | null;
  user_count: number;
  max_users: number | null;
  modules: ModuleState[];
  demandes: DemandeItem[];
}

const ETAT_META: Record<ModuleState['etat'], { label: string; cls: string; icon: any }> = {
  alloue: { label: 'Alloué', cls: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30', icon: CheckCircle2 },
  accredite: { label: 'Accrédité', cls: 'bg-sky-500/15 text-sky-300 border-sky-500/30', icon: ShieldQuestion },
  demande: { label: 'En demande', cls: 'bg-amber-500/15 text-amber-300 border-amber-500/30', icon: Clock },
  verrouille: { label: 'Verrouillé', cls: 'bg-slate-800 text-slate-500 border-slate-700', icon: Lock },
};

export default function AdminEntrepriseModulesPage() {
  const [data, setData] = useState<Overview | null>(null);
  const [loading, setLoading] = useState(true);
  const [requesting, setRequesting] = useState<string | null>(null);
  const [motif, setMotif] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await companyAdminAPI.modulesOverview();
      setData(res.data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Impossible de charger les modules');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const openRequest = (key: string) => { setRequesting(key); setMotif(''); };
  const closeRequest = () => { setRequesting(null); setMotif(''); };

  const submitRequest = async () => {
    if (!requesting) return;
    setSubmitting(true);
    try {
      await companyAdminAPI.requestModule({ module: requesting, motif: motif || undefined });
      toast.success('Demande transmise au CADC');
      closeRequest();
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Envoi impossible');
    } finally {
      setSubmitting(false);
    }
  };

  const cancelDemande = async (d: DemandeItem) => {
    if (!confirm(`Retirer la demande pour « ${d.module} » ?`)) return;
    try {
      await companyAdminAPI.cancelModuleRequest(d.id);
      toast.success('Demande retirée');
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Retrait impossible');
    }
  };

  if (loading) {
    return <div className="p-6 text-slate-400 text-sm">Chargement des modules…</div>;
  }
  if (!data) {
    return <div className="p-6 text-slate-500 text-sm">Aucune donnée d'entreprise.</div>;
  }

  const capInfo = data.max_modules == null ? 'illimité' : String(data.max_modules);
  const quotaUsers = data.max_users == null ? '' : `${data.user_count}/${data.max_users}`;

  return (
    <div className="p-4 sm:p-6 space-y-6">
      <header className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0">
          <Layers className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <h1 className="text-xl font-black text-slate-100">Modules alloués &amp; demandes</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Alloués&nbsp;: {data.modules_actives.length} · Verrou max du plan&nbsp;: {capInfo} · Collaborateurs&nbsp;: {quotaUsers}
          </p>
        </div>
      </header>

      {/* Demandes en attente */}
      {data.demandes.length > 0 && (
        <section className="space-y-2">
          <h2 className="text-sm font-bold text-amber-300">Demandes en attente d'arbitrage CADC</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {data.demandes.map(d => (
              <div key={d.id} className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-3 flex items-center justify-between gap-2">
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-amber-200 truncate">{d.module}</p>
                  <p className="text-[11px] text-slate-400 truncate">{d.libelle || d.code}</p>
                </div>
                <button onClick={() => cancelDemande(d)} className="p-1.5 rounded-lg text-slate-400 hover:text-red-300 hover:bg-red-500/10" title="Retirer la demande">
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Catalogue étatisé */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {data.modules.map(m => {
          const meta = ETAT_META[m.etat];
          const Icon = meta.icon;
          const canRequest = m.etat === 'verrouille';
          return (
            <div key={m.key}
              className={`rounded-xl border p-4 flex flex-col gap-3 transition ${
                m.etat === 'verrouille' ? 'border-slate-800 bg-slate-950/40 opacity-80' : 'border-slate-700 bg-slate-900/60'}`}>
              <div className="flex items-center justify-between">
                <span className="font-mono text-sm font-bold text-slate-200">{m.key}</span>
                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold border ${meta.cls}`}>
                  <Icon className="w-3 h-3" /> {meta.label}
                </span>
              </div>
              <div className="text-xs text-slate-400">
                {/* Batch 13 Zero-Mock : la variante accentuee 'alloué' ne pouvait
                    jamais matcher  le backend renvoie systematiquement 'alloue'
                    sans accent (company_admin.py l.421). Comparaison dead-code
                    retirée, tsc/TS2367 ne tombe plus dessus. */}
                {m.etat === 'alloue' ? 'Inclus dans votre abonnement.' :
                 m.etat === 'accredite' ? 'Débloqué par une accréditation CADC datée.' :
                 m.etat === 'demande' ? "Votre demande est en cours d'examen." :
                 'Non accessible  demandez une accréditation au CADC.'}
              </div>
              {canRequest && (
                <button onClick={() => openRequest(m.key)}
                  className="mt-auto inline-flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold">
                  <Send className="w-3.5 h-3.5" /> Demander au CADC
                </button>
              )}
            </div>
          );
        })}
      </section>

      {/* Modale de demande */}
      {requesting && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onClick={closeRequest}>
          <div className="w-full max-w-md rounded-2xl bg-slate-900 border border-slate-700 p-5 space-y-4" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-100">Demander le module « {requesting} »</h3>
              <button onClick={closeRequest} className="p-1.5 text-slate-400 hover:text-white"><X className="w-4 h-4" /></button>
            </div>
            <p className="text-xs text-slate-400">
              La demande est transmise au Super-Admin CADC. Elle ne débloque rien tant qu'elle n'est pas convertie en accréditation datée.
            </p>
            <textarea
              value={motif}
              onChange={e => setMotif(e.target.value)}
              rows={3}
              placeholder="Motif / besoin métier (facultatif)"
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100 focus:ring-2 focus:ring-indigo-500 resize-none"
            />
            <div className="flex justify-end gap-2">
              <button onClick={closeRequest} className="px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800">Annuler</button>
              <button onClick={submitRequest} disabled={submitting}
                className="px-4 py-2 rounded-lg text-sm font-bold bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50">
                {submitting ? 'Envoi…' : 'Envoyer la demande'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
