'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Zap, ArrowLeft, ShieldCheck, AlertTriangle, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { transportAPI } from '@/lib/api-client';

interface ConsommationVehicule {
  immatriculation: string;
  litres: number;
  tickets: number;
  conso_moyenne_l100?: number | null;
}

interface Ticket {
  id: number;
  immatriculation?: string | null;
  date_plein?: string | null;
  conso_l100?: number | null;
  notes?: string | null;
}

interface Alerte {
  cle: string;
  type: 'surconsommation' | 'signalement';
  immatriculation: string;
  valeur?: number | null;
  detail: string;
}

const SEUIL_L100 = 45; // aligne sur le seuil FuelGuard du portail chauffeur
const RE_ANOMALIE = /anomal|siphonn|alerte consommation/i;

const fmtDate = (iso?: string | null) => {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? String(iso) : d.toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' });
};

export default function FuelGuardAlertsPage() {
  const [alertes, setAlertes] = useState<Alerte[]>([]);
  const [stats, setStats] = useState({ vehicules: 0, mesures: 0, tickets: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res: any = await transportAPI.getFuel({ limit: 500 });
      const body = res.data ?? res;
      const parVehicule: ConsommationVehicule[] = body?.consommation_par_vehicule || [];
      const tickets: Ticket[] = body?.items || [];

      const found: Alerte[] = [];
      for (const v of parVehicule) {
        if (v.conso_moyenne_l100 != null && v.conso_moyenne_l100 > SEUIL_L100) {
          found.push({
            cle: `cons-${v.immatriculation}`,
            type: 'surconsommation',
            immatriculation: v.immatriculation,
            valeur: v.conso_moyenne_l100,
            detail: `${v.conso_moyenne_l100.toFixed(1)} L/100km sur ${v.tickets} plein(s) mesure(s) — seuil ${SEUIL_L100}`,
          });
        }
      }
      for (const t of tickets) {
        if (t.notes && RE_ANOMALIE.test(t.notes)) {
          const date = fmtDate(t.date_plein);
          found.push({
            cle: `sig-${t.id}`,
            type: 'signalement',
            immatriculation: t.immatriculation || 'Véhicule non précisé',
            detail: date ? `${t.notes} (${date})` : t.notes,
            valeur: t.conso_l100 ?? null,
          });
        }
      }

      setAlertes(found);
      setStats({
        vehicules: parVehicule.length,
        mesures: parVehicule.filter(v => v.conso_moyenne_l100 != null).length,
        tickets: body?.total ?? tickets.length,
      });
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Impossible de charger les données carburant.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 text-white animate-in fade-in duration-500">
      <Link href="/fuel-guard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6">
        <ArrowLeft className="w-4 h-4" /> Retour à la télémétrie
      </Link>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
        <div className="flex items-center gap-3 pb-6 border-b border-slate-800 mb-6">
          <div className="w-12 h-12 bg-orange-500/10 text-orange-400 rounded-2xl flex items-center justify-center border border-orange-500/20">
            <Zap className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black">Journal d'Alertes Anti-Fraude</h1>
            <p className="text-sm text-slate-400">
              Anomalies calculées sur les pleins réellement enregistrés (seuil {SEUIL_L100} L/100km).
            </p>
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400 flex items-center justify-center gap-2">
            <Loader2 className="w-5 h-5 animate-spin text-orange-400" /> Analyse des pleins enregistrés…
          </div>
        ) : error ? (
          <div className="p-8 text-center bg-red-500/5 border border-red-500/20 rounded-2xl">
            <AlertTriangle className="w-10 h-10 text-red-400 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-slate-200">Données indisponibles</h3>
            <p className="text-sm text-slate-400 mt-1">{error}</p>
            <button onClick={load} className="mt-4 px-4 py-2 rounded-xl bg-slate-800 text-slate-200 text-xs font-bold border border-slate-700 hover:bg-slate-700 cursor-pointer">
              Réessayer
            </button>
          </div>
        ) : alertes.length > 0 ? (
          <div className="space-y-3">
            {alertes.map(a => (
              <div key={a.cle} className="p-4 bg-red-500/5 border border-red-500/20 rounded-2xl flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <div>
                  <div className="text-sm font-black text-red-300">
                    {a.immatriculation} — {a.type === 'surconsommation' ? 'Surconsommation mesurée' : 'Signalement chauffeur'}
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">{a.detail}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center bg-slate-950 border border-slate-800 rounded-2xl">
            <ShieldCheck className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-slate-200">Aucune anomalie sur les pleins enregistrés</h3>
            <p className="text-sm text-slate-400 mt-1">
              {stats.tickets} ticket(s) analysé(s), {stats.mesures}/{stats.vehicules} véhicule(s) avec consommation mesurée.
            </p>
            <p className="text-xs text-slate-500 mt-2">
              La télémétrie IoT de niveau de réservoir n'est pas branchée : cette vue reflète uniquement les pleins saisis,
              et ne garantit pas l'absence de siphonnage non documenté.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
