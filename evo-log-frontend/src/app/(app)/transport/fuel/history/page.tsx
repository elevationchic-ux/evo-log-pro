'use client';

/**
 * Historique et analyse des consommations carburant.
 *
 * Les lignes viennent de `GET /api/v1/transport/fuel`, consolidées sur la
 * période choisie : la même source que le tableau de bord, donc les totaux des
 * deux écrans ne peuvent pas diverger. Aucune consommation télémétrique n'est
 * simulée  la moyenne L/100 km n'existe que pour les pleins encadrés par deux
 * relevés d'index (champ `conso_moyenne_l100`, null sinon).
 */
import React, { useMemo, useState } from 'react';
import Link from 'next/link';
import {
  Fuel, ArrowLeft, Download, Search, RefreshCw, Plus,
  AlertTriangle, CheckCircle2, HelpCircle, BarChart3,
} from 'lucide-react';
import { toast } from 'sonner';
import { transportAPI } from '@/lib/api-client';
import { useApi } from '@/hooks/useApi';
import { DataEmptyState, DataErrorState, DataLoadingState } from '@/components/shared/StatePanels';
import { exportToCSV } from '@/lib/export';
import { SEUIL_SURCONSOMMATION_L100 } from '@/config/carburant';

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
  total: number;
  litres_total: number;
  cout_total: number;
  prix_moyen_litre: number;
  consommation_par_vehicule: ConsommationParVehicule[];
}

const SYNTHESE_VIDE: SyntheseCarburant = {
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

const fmtDateFr = (iso: string) => {
  if (!iso) return '';
  const d = new Date(`${iso}T00:00:00`);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleDateString('fr-FR');
};

/** Diagnostic : on compare au seuil FuelGuard, on ne déclare rien de « conforme »
 *  sans mesure  un plein isolé ne permet pas de calculer une consommation. */
function diagnostic(conso: number | null) {
  if (conso === null) {
    return {
      label: 'Non mesurable',
      detail: `Aucun plein encadré par deux relevés d'index sur la période`,
      classe: 'bg-slate-500/10 text-slate-300 border-slate-600',
      Icone: HelpCircle,
    };
  }
  if (conso > SEUIL_SURCONSOMMATION_L100) {
    return {
      label: `Surconsommation (> ${SEUIL_SURCONSOMMATION_L100} L/100 km)`,
      detail: `Moyenne constatée de ${conso} L/100 km`,
      classe: 'bg-red-500/10 text-red-400 border-red-500/20',
      Icone: AlertTriangle,
    };
  }
  return {
    label: `Sous le seuil (${SEUIL_SURCONSOMMATION_L100} L/100 km)`,
    detail: `Moyenne constatée de ${conso} L/100 km`,
    classe: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    Icone: CheckCircle2,
  };
}

export default function TransportFuelHistoryPage() {
  const [depuis, setDepuis] = useState('');
  const [jusqua, setJusqua] = useState('');
  const [search, setSearch] = useState('');

  // limit=1 : seuls les cumuls et la consolidation sont affichés ici, et le
  // backend les calcule déjà sur la période entière (pas sur la page).
  const { data, loading, error, isEmpty, refetch } = useApi<SyntheseCarburant>(
    async () => {
      const res = await transportAPI.getFuel({
        depuis: depuis || undefined,
        jusqua: jusqua || undefined,
        limit: 1,
      });
      return { ...SYNTHESE_VIDE, ...(res.data || {}) };
    },
    { isEmpty: (d) => d.total === 0 && d.consommation_par_vehicule.length === 0 }
  );

  const synthese = data ?? SYNTHESE_VIDE;
  const periodes = useMemo(
    () =>
      [...synthese.consommation_par_vehicule].sort(
        (a, b) => b.litres - a.litres
      ),
    [synthese.consommation_par_vehicule]
  );

  const filtrees = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return periodes;
    return periodes.filter((v) => v.immatriculation.toLowerCase().includes(q));
  }, [periodes, search]);

  const libellePeriode =
    depuis || jusqua
      ? `${depuis ? fmtDateFr(depuis) : 'origine'} → ${jusqua ? fmtDateFr(jusqua) : "aujourd'hui"}`
      : 'historique complet';

  const vehiculesMesures = periodes.filter((v) => v.conso_moyenne_l100 !== null).length;

  const exporter = () => {
    if (filtrees.length === 0) {
      toast.error('Aucune consommation à exporter pour cette période.');
      return;
    }
    // Valeurs brutes (non formatées) : le CSV doit rester exploitable par un
    // tableur, y compris avec les décimales françaises.
    exportToCSV(
      filtrees.map((v) => ({
        immatriculation: v.immatriculation,
        periode: libellePeriode,
        tickets: v.tickets,
        litres: v.litres,
        km_mesures: v.km_measure ?? '',
        conso_l100: v.conso_moyenne_l100 ?? '',
        montant_xaf: v.montant_xaf,
        part_flotte_pct: v.part_pct,
        diagnostic: diagnostic(v.conso_moyenne_l100).label,
      })),
      `historique-carburant-${new Date().toISOString().slice(0, 10)}`
    );
    toast.success(`${filtrees.length} véhicule(s) exporté(s) en CSV.`);
  };

  const reinitialiser = () => {
    setDepuis('');
    setJusqua('');
    setSearch('');
    refetch();
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/transport/fuel" className="hover:text-amber-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Carburant
        </Link>
        <span>/</span>
        <span className="text-white">Historique & analyse des consommations</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20">
            <Fuel className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Historique Carburant
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 font-mono">
                KTRN_HST
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Consommation consolidée par véhicule d'après les tickets saisis  période : {libellePeriode}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/transport/saisie-ticket-carburant"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-100 font-medium text-sm border border-slate-700 transition"
          >
            <Plus className="w-4 h-4" />
            Saisir un ticket
          </Link>
          <button
            onClick={exporter}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-medium text-sm shadow-lg shadow-amber-600/30 transition"
          >
            <Download className="w-4 h-4" />
            Exporter CSV
          </button>
        </div>
      </div>

      {/* Filtre de période : la requête repart sur le backend, aucun filtrage
          local ne peut faire croire à une période couverte. */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-4 flex flex-col sm:flex-row sm:items-end gap-3">
        <label className="flex flex-col gap-1 text-xs text-slate-400">
          Du
          <input
            type="date"
            value={depuis}
            onChange={(e) => setDepuis(e.target.value)}
            className="px-3 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
          />
        </label>
        <label className="flex flex-col gap-1 text-xs text-slate-400">
          Au
          <input
            type="date"
            value={jusqua}
            onChange={(e) => setJusqua(e.target.value)}
            className="px-3 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
          />
        </label>
        <div className="flex items-center gap-2">
          <button
            onClick={refetch}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-600/30 font-medium text-sm transition"
          >
            <Search className="w-4 h-4" />
            Appliquer
          </button>
          <button
            onClick={reinitialiser}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 font-medium text-sm transition"
          >
            <RefreshCw className="w-4 h-4" />
            Tout
          </button>
        </div>
        <p className="sm:ml-auto text-xs text-slate-500">
          {fmtNum(synthese.total)} ticket(s) • {vehiculesMesures}/{periodes.length} véhicule(s) avec consommation mesurée
        </p>
      </div>

      {/* KPI de période */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { titre: 'Carburant consommé', valeur: `${fmtNum(synthese.litres_total, 1)} L` },
          { titre: 'Dépense', valeur: `${fmtNum(synthese.cout_total)} XAF` },
          { titre: 'Prix moyen au litre', valeur: synthese.prix_moyen_litre ? `${fmtNum(synthese.prix_moyen_litre)} XAF` : 'Non calculable' },
          { titre: 'Véhicules concernés', valeur: `${periodes.length}` },
        ].map((kpi) => (
          <div key={kpi.titre} className="bg-slate-900/80 rounded-2xl border border-slate-800 p-4">
            <p className="text-xs text-slate-400 uppercase tracking-wide">{kpi.titre}</p>
            <p className="mt-2 text-xl font-bold text-white font-mono">{kpi.valeur}</p>
          </div>
        ))}
      </div>

      {/* Tableau */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="flex items-center gap-2 text-white font-semibold">
            <BarChart3 className="w-5 h-5 text-amber-400" />
            Consommation par véhicule
          </div>
          <div className="relative flex-1 sm:max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Rechercher une immatriculation..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>

        {loading && <DataLoadingState rows={4} label="Chargement de la consolidation carburant…" />}
        {!loading && error && <DataErrorState error={error} onRetry={refetch} />}
        {!loading && !error && isEmpty && (
          <DataEmptyState
            title="Aucun ticket carburant sur cette période"
            description={`La période ${libellePeriode} ne contient aucun enregistrement. L'historique se construit à partir des tickets saisis par les conducteurs, rien n'est reconstitué par télémétrie.`}
            actionLabel="Saisir un ticket carburant"
            actionHref="/transport/saisie-ticket-carburant"
          />
        )}
        {!loading && !error && !isEmpty && filtrees.length === 0 && (
          <p className="py-10 text-center text-sm text-slate-400">
            Aucune immatriculation ne correspond à « {search} ».
          </p>
        )}

        {!loading && !error && filtrees.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Véhicule</th>
                  <th className="py-3 px-4">Tickets</th>
                  <th className="py-3 px-4">Litres</th>
                  <th className="py-3 px-4">Km mesurés</th>
                  <th className="py-3 px-4">Moyenne L/100 km</th>
                  <th className="py-3 px-4">Dépense (XAF)</th>
                  <th className="py-3 px-4">Part flotte</th>
                  <th className="py-3 px-4 rounded-r-xl">Diagnostic</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtrees.map((v) => {
                  const diag = diagnostic(v.conso_moyenne_l100);
                  return (
                    <tr key={v.immatriculation} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-semibold text-white">
                        <Link
                          href={`/transport/fuel?immatriculation=${encodeURIComponent(v.immatriculation)}`}
                          className="hover:text-amber-400"
                        >
                          {v.immatriculation}
                        </Link>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-xs text-slate-400">{fmtNum(v.tickets)}</td>
                      <td className="py-3.5 px-4 font-mono text-xs text-white">{fmtNum(v.litres, 1)} L</td>
                      <td className="py-3.5 px-4 font-mono text-xs text-slate-400">
                        {v.km_measure === null ? 'non relevé' : `${fmtNum(v.km_measure)} km`}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-xs font-bold text-white">
                        {v.conso_moyenne_l100 === null ? '' : `${v.conso_moyenne_l100} L/100km`}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-xs text-amber-400 font-bold">
                        {fmtNum(v.montant_xaf)}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-xs text-slate-300">{fmtNum(v.part_pct, 1)} %</td>
                      <td className="py-3.5 px-4">
                        <span
                          title={diag.detail}
                          className={`px-2.5 py-1 rounded-full text-xs font-semibold border flex items-center gap-1 w-fit ${diag.classe}`}
                        >
                          <diag.Icone className="w-3 h-3" />
                          {diag.label}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
