'use client';

/**
 * Tableau de bord carburant de la flotte.
 *
 * Toutes les valeurs viennent de `GET /api/transport/fuel`, c'est-à-dire des
 * tickets réellement saisis par les conducteurs : aucun budget, aucun « niveau
 * de cuve » et aucune consommation ne sont simulés. La moyenne L/100 km n'est
 * publiée que pour les pleins encadrés par deux relevés d'index.
 */
import React, { useMemo } from 'react';
import Link from 'next/link';
import {
  Fuel, Plus, RefreshCw, BarChart3, Truck, Receipt,
  AlertTriangle, CheckCircle2, HelpCircle,
} from 'lucide-react';
import { transportAPI } from '@/lib/api-client';
import { useApi } from '@/hooks/useApi';
import { DataEmptyState, DataErrorState, DataLoadingState } from '@/components/shared/StatePanels';
import { SEUIL_SURCONSOMMATION_L100 } from '@/config/carburant';

interface TicketCarburant {
  id: number;
  numero_ticket: string | null;
  immatriculation: string | null;
  chauffeur: string | null;
  station: string | null;
  litres: number;
  prix_litre: number | null;
  cout: number;
  kilometrage: number | null;
  index_precedent: number | null;
  delta_km: number | null;
  conso_l100: number | null;
  date_plein: string | null;
  statut: string;
}

interface ConsommationParVehicule {
  immatriculation: string;
  litres: number;
  montant_xaf: number;
  tickets: number;
  part_pct: number;
  km_measure: number | null;
  conso_moyenne_l100: number | null;
}

interface SyntheseCarburant {
  items: TicketCarburant[];
  total: number;
  litres_total: number;
  cout_total: number;
  prix_moyen_litre: number;
  consommation_par_vehicule: ConsommationParVehicule[];
}

const SYNTHESE_VIDE: SyntheseCarburant = {
  items: [],
  total: 0,
  litres_total: 0,
  cout_total: 0,
  prix_moyen_litre: 0,
  consommation_par_vehicule: [],
};

const fmtNum = (n: number | null | undefined, digits = 0) =>
  n === null || n === undefined
    ? ''
    : new Intl.NumberFormat('fr-FR', { maximumFractionDigits: digits }).format(n);

const fmtDate = (iso: string | null) => {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString('fr-FR');
};

export default function TransportFuelDashboard() {
  const { data, loading, error, isEmpty, refetch } = useApi<SyntheseCarburant>(
    async () => {
      const res = await transportAPI.getFuel({ limit: 200 });
      const corps = res.data || {};
      return {
        items: Array.isArray(corps.items) ? corps.items : [],
        total: corps.total ?? 0,
        litres_total: corps.litres_total ?? 0,
        cout_total: corps.cout_total ?? 0,
        prix_moyen_litre: corps.prix_moyen_litre ?? 0,
        consommation_par_vehicule: Array.isArray(corps.consommation_par_vehicule)
          ? corps.consommation_par_vehicule
          : [],
      };
    },
    { isEmpty: (d) => d.total === 0 && d.items.length === 0 }
  );

  const synthese = data ?? SYNTHESE_VIDE;

  // Portée réelle des cumuls : date du premier et du dernier ticket reçu.
  const periode = useMemo(() => {
    const dates = synthese.items
      .map((t) => t.date_plein)
      .filter((d): d is string => Boolean(d))
      .sort();
    if (dates.length === 0) return null;
    return { debut: dates[0], fin: dates[dates.length - 1] };
  }, [synthese.items]);

  // Part des pleins réellement contrôlables (deux index relevés).
  const pleinsMesures = synthese.items.filter((t) => t.conso_l100 !== null).length;
  const derniersTickets = synthese.items.slice(0, 6);

  const kpis = [
    {
      label: 'Carburant collecté',
      value: fmtNum(synthese.litres_total, 0),
      unite: 'litres',
      detail: `${fmtNum(synthese.total)} ticket${synthese.total > 1 ? 's' : ''} enregistré${synthese.total > 1 ? 's' : ''}`,
    },
    {
      label: 'Dépense carburant',
      value: fmtNum(synthese.cout_total),
      unite: 'XAF',
      detail: 'Cumul des montants des tickets saisis',
    },
    {
      label: 'Prix moyen',
      value: synthese.prix_moyen_litre ? fmtNum(synthese.prix_moyen_litre) : '',
      unite: 'XAF / litre',
      detail: 'Prix constaté à la pompe, toutes stations confondues',
    },
    {
      label: 'Pleins contrôlés',
      value: `${fmtNum(pleinsMesures)} / ${fmtNum(synthese.items.length)}`,
      unite: 'avec index borné',
      detail: `Seuil de surveillance : ${SEUIL_SURCONSOMMATION_L100} L/100 km`,
    },
  ];

  return (
    <div className="min-h-screen p-4 sm:p-6 space-y-6 text-slate-100">
      {/* En-tête */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2 text-white">
            <Fuel className="text-amber-500" size={28} />
            Gestion Carburant
          </h1>
          <p className="text-slate-400 mt-1 text-sm">
            {periode
              ? `Cumuls établis sur les tickets du ${fmtDate(periode.debut)} au ${fmtDate(periode.fin)}`
              : 'Suivi des consommations à partir des tickets carburant saisis par les conducteurs'}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => refetch()}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-700 text-sm hover:bg-slate-800 transition-colors disabled:opacity-50"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            Actualiser
          </button>
          <Link
            href="/transport/saisie-ticket-carburant"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-sm font-medium transition-colors"
          >
            <Plus size={16} />
            Saisir Ticket
          </Link>
        </div>
      </div>

      {loading && <DataLoadingState rows={3} label="Chargement de la synthèse carburant…" />}
      {!loading && error && <DataErrorState error={error} onRetry={refetch} />}

      {!loading && !error && isEmpty && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80">
          <DataEmptyState
            title="Aucun ticket carburant enregistré"
            description="Les compteurs restent à zéro tant qu'aucun plein n'a été saisi. Enregistrez le premier ticket remis par vos conducteurs pour alimenter ce tableau de bord."
            actionLabel="Saisir un ticket carburant"
            actionHref="/transport/saisie-ticket-carburant"
          />
        </div>
      )}

      {!loading && !error && !isEmpty && (
        <>
          {/* Cartes d'indicateurs */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {kpis.map((k) => (
              <div
                key={k.label}
                className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5"
              >
                <div className="flex justify-between items-start mb-2">
                  <p className="text-xs text-slate-400">{k.label}</p>
                  <Fuel size={16} className="text-amber-400 opacity-60" />
                </div>
                <p className="text-2xl font-bold text-white">
                  {k.value}
                  <span className="text-sm font-normal text-slate-400 ml-1.5">{k.unite}</span>
                </p>
                <p className="text-xs text-slate-500 mt-1">{k.detail}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Consommation par véhicule */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
              <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                <Truck size={18} className="text-amber-400" />
                Consommation par véhicule
              </h3>
              <div className="space-y-4">
                {synthese.consommation_par_vehicule.map((v) => (
                  <div key={v.immatriculation}>
                    <div className="flex justify-between items-center mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium font-mono text-white">
                          {v.immatriculation}
                        </span>
                        <span className="text-xs text-slate-500">
                          {v.tickets} plein{v.tickets > 1 ? 's' : ''}
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-sm font-bold text-white">{fmtNum(v.litres, 1)} L</span>
                        <span className="text-xs text-slate-400 ml-2">
                          ({fmtNum(v.montant_xaf)} XAF)
                        </span>
                      </div>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-2">
                      <div
                        className="h-2 rounded-full bg-amber-500 transition-all"
                        style={{ width: `${Math.min(100, v.part_pct)}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-slate-500 mt-1">
                      <span>Part de la flotte : {fmtNum(v.part_pct, 1)} %</span>
                      {v.conso_moyenne_l100 !== null ? (
                        <span
                          className={
                            v.conso_moyenne_l100 > SEUIL_SURCONSOMMATION_L100
                              ? 'text-red-400 font-semibold'
                              : 'text-emerald-400'
                          }
                        >
                          {fmtNum(v.conso_moyenne_l100, 1)} L/100 km sur{' '}
                          {fmtNum(v.km_measure)} km mesurés
                        </span>
                      ) : (
                        <span className="text-slate-500 flex items-center gap-1">
                          <HelpCircle size={12} /> Consommation non mesurable
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-[11px] text-slate-400 mt-4 leading-relaxed">
                La moyenne n'est calculée que sur les pleins encadrés par deux relevés d'index ;
                un plein isolé ne fournit aucune consommation.
              </p>
            </div>

            {/* Derniers tickets */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-semibold text-white flex items-center gap-2">
                  <BarChart3 size={18} className="text-amber-400" />
                  Derniers tickets
                </h3>
                <Link href="/transport/fuel/history" className="text-xs text-amber-400 hover:underline">
                  Historique complet →
                </Link>
              </div>
              <div className="space-y-3">
                {derniersTickets.map((t) => (
                  <div
                    key={t.id}
                    className="flex items-center justify-between gap-3 p-3 rounded-xl bg-slate-800/40 hover:bg-slate-800/70 transition-colors"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-2 h-2 rounded-full shrink-0 bg-emerald-500" title="Ticket validé à la saisie" />
                      <div className="min-w-0">
                        <p className="text-sm font-medium font-mono text-white truncate">
                          {t.numero_ticket || `Ticket #${t.id}`}
                          <span className="text-slate-400 font-sans"> • {t.immatriculation || 'véhicule non identifié'}</span>
                        </p>
                        <p className="text-xs text-slate-500 truncate">
                          {fmtDate(t.date_plein)} • {t.chauffeur || 'chauffeur non rattaché'} • {t.station || 'station non précisée'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="text-sm font-bold text-amber-400">{fmtNum(t.litres, 1)} L</p>
                      <p className="text-xs text-slate-400">{fmtNum(t.cout)} XAF</p>
                      {t.conso_l100 !== null ? (
                        <span
                          className={`inline-flex items-center gap-1 text-[11px] font-medium ${t.conso_l100 > SEUIL_SURCONSOMMATION_L100 ? 'text-red-400' : 'text-emerald-400'
                            }`}
                        >
                          {t.conso_l100 > SEUIL_SURCONSOMMATION_L100 ? (
                            <AlertTriangle size={11} />
                          ) : (
                            <CheckCircle2 size={11} />
                          )}
                          {fmtNum(t.conso_l100, 1)} L/100 km
                        </span>
                      ) : (
                        <span className="text-[11px] text-slate-400">index non borné</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <Link
                href="/transport/saisie-ticket-carburant"
                className="mt-4 flex items-center justify-center gap-2 w-full py-2.5 rounded-xl border border-dashed border-amber-500/30 text-amber-400 text-sm hover:bg-amber-500/5 transition-colors"
              >
                <Receipt size={16} />
                Saisir un nouveau ticket
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
