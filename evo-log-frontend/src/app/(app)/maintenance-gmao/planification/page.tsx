'use client';

import React, { useState } from 'react';
import { Wrench, Play, RefreshCw, CheckCircle2, Clock } from 'lucide-react';
import { apiClient, apiUrl } from '@/lib/api-client';
import { toast } from 'sonner';

interface OtCree { ot_id: number; numero_ot: string; plan_id: number; asset_id: number; motif: string; }
interface Rapport {
  date_evaluation: string;
  plans_evalues: number;
  ots_crees: OtCree[];
  plans_ignores: { plan_id: number; motif: string }[];
  lubrifications_declenchees: { ot_id: number; numero_ot: string; point: string }[];
  erreurs: { plan_id: number; erreur: string }[];
}

export default function PlanificationGmaoPage() {
  const [rapport, setRapport] = useState<Rapport | null>(null);
  const [enCours, setEnCours] = useState(false);

  const evaluer = async () => {
    setEnCours(true);
    try {
      const res = await apiClient.post(apiUrl('/maintenance-planification/evaluer'), {});
      setRapport(res.data);
      toast.success(`${res.data.ots_crees.length} OT préventif(s) généré(s).`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Évaluation impossible');
    } finally {
      setEnCours(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-4 md:p-6">
      <header>
        <h1 className="flex items-center gap-2 text-xl font-semibold text-slate-100">
          <Wrench className="h-6 w-6 text-cyan-400" /> Planification préventive GMAO
        </h1>
        <p className="text-sm text-slate-400">
          Évalue les plans par compteurs réels (heures/km/cycles), échéances calendaires et lubrifications — génère les OT préventifs.
        </p>
      </header>

      <div className="rounded-xl border border-slate-700 bg-slate-900/50 p-6 text-center">
        <p className="mb-4 text-sm text-slate-400">
          Lance l'évaluation de tous les plans de maintenance actifs. Idempotent par jour : un second passage ne duplique aucun OT.
        </p>
        <button onClick={evaluer} disabled={enCours}
          className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-cyan-600 px-6 text-sm font-medium text-white hover:bg-cyan-500 disabled:opacity-50">
          {enCours ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          {enCours ? 'Évaluation…' : 'Évaluer et planifier'}
        </button>
      </div>

      {rapport && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {[
              ['Évaluation', rapport.date_evaluation, 'text-slate-300'],
              ['Plans évalués', String(rapport.plans_evalues), 'text-slate-100'],
              ['OT créés', String(rapport.ots_crees.length), 'text-emerald-400'],
              ['Lubrifications', String(rapport.lubrifications_declenchees.length), 'text-cyan-400'],
            ].map(([lbl, val, col]) => (
              <div key={lbl as string} className="rounded-xl border border-slate-700 bg-slate-900/60 p-4">
                <div className="text-[10px] uppercase text-slate-500">{lbl}</div>
                <div className={`text-lg font-bold ${col}`}>{val}</div>
              </div>
            ))}
          </div>

          {rapport.ots_crees.length > 0 && (
            <section className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4">
              <h2 className="mb-2 flex items-center gap-2 text-sm font-semibold text-emerald-300"><CheckCircle2 className="h-4 w-4" /> OT préventifs créés</h2>
              <ul className="space-y-1 font-mono text-xs">
                {rapport.ots_crees.map(ot => (
                  <li key={ot.ot_id} className="flex justify-between rounded bg-slate-900/60 px-2 py-1">
                    <span className="text-emerald-300">{ot.numero_ot}</span>
                    <span className="text-slate-400">{ot.motif}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {rapport.lubrifications_declenchees.length > 0 && (
            <section className="rounded-xl border border-cyan-500/30 bg-cyan-500/5 p-4">
              <h2 className="mb-2 flex items-center gap-2 text-sm font-semibold text-cyan-300"><Clock className="h-4 w-4" /> Graissages planifiés</h2>
              <ul className="space-y-1 font-mono text-xs">
                {rapport.lubrifications_declenchees.map(l => (
                  <li key={l.ot_id} className="flex justify-between rounded bg-slate-900/60 px-2 py-1">
                    <span className="text-cyan-300">{l.numero_ot}</span>
                    <span className="text-slate-400">{l.point}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {rapport.plans_ignores.length > 0 && (
            <details className="rounded-xl border border-slate-700 bg-slate-900/40 p-4 text-xs">
              <summary className="cursor-pointer text-slate-400">Plans ignorés ({rapport.plans_ignores.length})</summary>
              <ul className="mt-2 space-y-1 font-mono text-slate-500">
                {rapport.plans_ignores.map(p => <li key={p.plan_id}>plan #{p.plan_id} — {p.motif}</li>)}
              </ul>
            </details>
          )}

          {rapport.erreurs.length > 0 && (
            <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-4 text-xs text-red-300">
              {rapport.erreurs.map((e, i) => <div key={i}>plan #{e.plan_id} : {e.erreur}</div>)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
