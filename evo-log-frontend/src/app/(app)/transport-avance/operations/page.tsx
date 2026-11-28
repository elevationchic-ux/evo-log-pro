'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { apiClient } from '@/lib/api-client';
import { ArrowLeft } from 'lucide-react';

// ============================================================================
// Opérations transport avancées — endpoints d'écriture de
// /api/v1/transport-avance (tournées, livraisons, frais, carburant,
// temps de conduite, sous-traitance, accidents, maintenance, GPS,
// géofencing) + /api/v1/transport-avance-complete (dispatch, arrêts,
// POD, documents POD, analytics)
// ============================================================================

type Data = Record<string, unknown> | unknown[];

function Result({ data, loading, error }: { data: Data | null; loading: boolean; error: string | null }) {
  if (loading) return <p className="text-sm text-gray-400">Envoi en cours…</p>;
  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!data) return null;
  if (Array.isArray(data))
    return <p className="text-sm text-green-700">{data.length} enregistrement(s) retourné(s)</p>;
  const obj = data as Record<string, unknown>;
  if (typeof obj.note === 'string') return <p className="text-sm text-amber-700">{String(obj.note)}</p>;
  return <pre className="text-xs bg-gray-50 border rounded p-3 overflow-auto max-h-72">{JSON.stringify(data, null, 2)}</pre>;
}

interface Champ {
  name: string; label: string; type?: string; required?: boolean;
  num?: boolean; list?: boolean; textarea?: boolean; options?: string[];
}

function payload(vals: Record<string, string>, champs: Champ[]) {
  const out: Record<string, unknown> = {};
  for (const c of champs) {
    const raw = vals[c.name];
    if (raw === undefined || raw === '') continue;
    if (c.list) out[c.name] = raw.split(',').map((s) => Number(s.trim())).filter((n) => !Number.isNaN(n));
    else if (c.num) out[c.name] = Number(raw);
    else if (c.type === 'checkbox') out[c.name] = raw === 'true';
    else out[c.name] = raw;
  }
  return out;
}

function Form({ titre, champs, onSubmit, result, loading, error }: {
  titre: string;
  champs: Champ[];
  onSubmit: (v: Record<string, unknown>) => unknown;
  result: Data | null; loading: boolean; error: string | null;
}) {
  const [vals, setVals] = useState<Record<string, string>>({});
  return (
    <div className="bg-white border rounded-xl p-5 shadow-sm">
      <h3 className="font-semibold mb-3 text-sm">{titre}</h3>
      <form
        className="grid grid-cols-2 gap-3 mb-3"
        onSubmit={(e) => { e.preventDefault(); void onSubmit(payload(vals, champs)); }}
      >
        {champs.map((c) => (
          <label key={c.name} className={c.textarea ? 'col-span-2 text-sm' : 'text-sm'}>
            <span className="block text-xs text-gray-500 mb-1">{c.label}</span>
            {c.textarea ? (
              <textarea
                value={vals[c.name] ?? ''}
                onChange={(e) => setVals({ ...vals, [c.name]: e.target.value })}
                className="w-full border rounded px-2 py-1.5 text-sm"
                rows={2}
              />
            ) : c.type === 'select' ? (
              <select
                required={c.required}
                value={vals[c.name] ?? ''}
                onChange={(e) => setVals({ ...vals, [c.name]: e.target.value })}
                className="w-full border rounded px-2 py-1.5 text-sm"
              >
                <option value="">—</option>
                {(c.options ?? []).map((o) => <option key={o} value={o}>{o}</option>)}
              </select>
            ) : (
              <input
                type={c.type ?? 'text'}
                required={c.required}
                value={vals[c.name] ?? ''}
                onChange={(e) => setVals({ ...vals, [c.name]: e.target.value })}
                className="w-full border rounded px-2 py-1.5 text-sm"
              />
            )}
          </label>
        ))}
        <div className="col-span-2">
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
            Exécuter
          </button>
        </div>
      </form>
      <Result data={result} loading={loading} error={error} />
    </div>
  );
}

// GET rapide sans formulaire : bouton déclencheur
function QuickGet({ titre, run, url }: { titre: string; run: ReturnType<typeof useMut>; url: () => string }) {
  return (
    <div className="bg-white border rounded-xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm">{titre}</h3>
        <button
          type="button"
          onClick={() => void run.run(() => apiClient.get(url()))}
          className="px-3 py-1.5 bg-gray-700 text-white text-xs rounded-lg hover:bg-gray-800"
        >
          Charger
        </button>
      </div>
      <Result data={run.result} loading={run.loading} error={run.error} />
    </div>
  );
}

function useMut() {
  const [result, setResult] = useState<Data | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const run = async (fn: () => Promise<{ data: Data }>) => {
    setLoading(true); setError(null); setResult(null);
    try { setResult((await fn()).data); }
    catch (e: unknown) {
      const ax = e as { response?: { data?: { detail?: unknown } } };
      const d = ax?.response?.data?.detail;
      setError(typeof d === 'string' ? d : e instanceof Error ? e.message : 'Erreur');
    } finally { setLoading(false); }
  };
  return { result, loading, error, run };
}

const B = '/api/v1/transport-avance';
const BC = '/api/v1/transport-avance-complete';

export default function TransportAvanceOperationsPage() {
  const tournee = useMut();
  const livraison = useMut();
  const tourneeAction = useMut();
  const fraisKm = useMut();
  const plein = useMut();
  const temps = useMut();
  const sousTraitant = useMut();
  const contrat = useMut();
  const missionSt = useMut();
  const accident = useMut();
  const enquete = useMut();
  const maintenance = useMut();
  const execMaint = useMut();
  const gpsPos = useMut();
  const geoZone = useMut();
  const geoEvt = useMut();
  const dispatchList = useMut();
  const dispatchDetail = useMut();
  const equilibre = useMut();
  const optimisation = useMut();
  const planif = useMut();
  const attribution = useMut();
  const recalcul = useMut();
  const dispatchEdit = useMut();
  const arret = useMut();
  const arretsList = useMut();
  const pod = useMut();
  const podAction = useMut();
  const podList = useMut();
  const docPod = useMut();
  const docsPod = useMut();
  const tb = useMut();
  const kpi = useMut();
  const alertes = useMut();

  return (
    <div className="p-6 space-y-8">
      <div className="flex items-center gap-3">
        <Link href="/transport-avance/analytique" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Opérations transport avancées</h1>
          <p className="text-sm text-gray-500">
            Tournées, livraisons, sous-traitance, accidents, maintenance, GPS, géofencing, dispatch, POD.
          </p>
        </div>
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Tournées & livraisons</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Créer une tournée" champs={[
            { name: 'conducteur_id', label: 'ID conducteur', type: 'number', required: true, num: true },
            { name: 'camion_id', label: 'ID camion', type: 'number', required: true, num: true },
            { name: 'date_tournee', label: 'Date tournée', type: 'date', required: true },
            { name: 'type_tournee', label: 'Type (locale/nationale/…)' },
            { name: 'notes', label: 'Notes', textarea: true },
          ]} onSubmit={(v) => tournee.run(() => apiClient.post(`${B}/tournees`, v))} {...tournee} />
          <Form titre="Ajouter une livraison à une tournée" champs={[
            { name: 'tournee_id', label: 'ID tournée', type: 'number', required: true, num: true },
            { name: 'client_id', label: 'ID client', type: 'number', required: true, num: true },
            { name: 'point_dechargement', label: 'Point de déchargement', required: true },
            { name: 'heure_debut_prevue', label: 'Début prévu (HH:MM)' },
            { name: 'heure_fin_prevue', label: 'Fin prévue (HH:MM)' },
            { name: 'nombre_colis', label: 'Nb colis', type: 'number', num: true },
            { name: 'poids_total', label: 'Poids total (kg)', type: 'number', num: true },
            { name: 'commentaire', label: 'Commentaire', textarea: true },
          ]} onSubmit={(v) => {
            const { tournee_id, ...body } = v;
            return livraison.run(() => apiClient.post(`${B}/tournees/${tournee_id}/livraisons`, body));
          }} {...livraison} />
          <Form titre="Action sur tournée (optimiser / démarrer / compléter)" champs={[
            { name: 'tournee_id', label: 'ID tournée', type: 'number', required: true, num: true },
            { name: 'action', label: 'Action', type: 'select', required: true, options: ['optimiser', 'demarrer', 'completer'] },
          ]} onSubmit={(v) => {
            const map: Record<string, string> = { optimiser: 'optimiser', demarrer: 'demarrer', completer: 'completer' };
            const action = map[String(v.action)] ?? 'optimiser';
            return tourneeAction.run(() => apiClient.put(`${B}/tournees/${v.tournee_id}/${action}`));
          }} {...tourneeAction} />
        </div>
        {/* select options injectés via datalist-like : géré côté backend par valeur texte */}
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Frais, carburant & temps de conduite</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Frais kilométrique" champs={[
            { name: 'employe_id', label: 'ID employé', type: 'number', required: true, num: true },
            { name: 'mission_id', label: 'ID mission', type: 'number', num: true },
            { name: 'kilometrage_parcouru', label: 'Km parcourus', type: 'number', required: true, num: true },
            { name: 'kilometrage_theorique', label: 'Km théorique', type: 'number', num: true },
            { name: 'taux_indemnite', label: 'Taux indemnité (XAF/km)', type: 'number', num: true },
            { name: 'commentaires', label: 'Commentaires', textarea: true },
          ]} onSubmit={(v) => fraisKm.run(() => apiClient.post(`${B}/frais-km`, v))} {...fraisKm} />
          <Form titre="Plein carburant (véhicule)" champs={[
            { name: 'vehicule_id', label: 'ID véhicule', type: 'number', required: true, num: true },
            { name: 'date_plein', label: 'Date/heure', type: 'datetime-local', required: true },
            { name: 'litres', label: 'Litres', type: 'number', required: true, num: true },
            { name: 'prix_litre', label: 'Prix litre (XAF)', type: 'number', required: true, num: true },
            { name: 'kilometrage', label: 'Kilométrage', type: 'number', required: true, num: true },
            { name: 'station', label: 'Station', required: true },
            { name: 'numero_ticket', label: 'N° ticket' },
          ]} onSubmit={(v) => {
            const { vehicule_id, ...q } = v;
            return plein.run(() => apiClient.post(`${B}/carburant/plein`, null, { params: { vehicule_id, ...q } }));
          }} {...plein} />
          <Form titre="Temps de conduite" champs={[
            { name: 'conducteur_id', label: 'ID conducteur', type: 'number', required: true, num: true },
            { name: 'mission_id', label: 'ID mission', type: 'number', num: true },
            { name: 'date', label: 'Date', type: 'date', required: true },
            { name: 'heure_debut_conduite', label: 'Début (HH:MM)', required: true },
            { name: 'heure_fin_conduite', label: 'Fin (HH:MM)' },
            { name: 'temps_conduite', label: 'Minutes conduite', type: 'number', required: true, num: true },
            { name: 'temps_repos', label: 'Minutes repos', type: 'number', num: true },
            { name: 'commentaires', label: 'Commentaires', textarea: true },
          ]} onSubmit={(v) => temps.run(() => apiClient.post(`${B}/temps-conduite`, v))} {...temps} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Sous-traitance</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Créer un sous-traitant" champs={[
            { name: 'nom', label: 'Nom / Raison sociale', required: true },
            { name: 'code', label: 'Code' },
            { name: 'type_service', label: 'Type de service' },
            { name: 'specialite', label: 'Spécialité' },
            { name: 'numero_licence', label: 'N° licence' },
            { name: 'telephone', label: 'Téléphone' },
            { name: 'email', label: 'Email' },
            { name: 'ville', label: 'Ville' },
          ]} onSubmit={(v) => sousTraitant.run(() => apiClient.post(`${B}/sous-traitants`, v))} {...sousTraitant} />
          <Form titre="Contrat sous-traitant" champs={[
            { name: 'sous_traitant_id', label: 'ID sous-traitant', type: 'number', required: true, num: true },
            { name: 'numero_contrat', label: 'N° contrat', required: true },
            { name: 'type_service', label: 'Type de service' },
            { name: 'date_debut', label: 'Début', type: 'date', required: true },
            { name: 'date_fin', label: 'Fin', type: 'date' },
            { name: 'tarif_unitaire', label: 'Tarif unitaire', type: 'number', num: true },
            { name: 'unite_tarif', label: 'Unité tarif (km/tonne/…)' },
            { name: 'notes', label: 'Notes', textarea: true },
          ]} onSubmit={(v) => contrat.run(() => apiClient.post(`${B}/sous-traitants/contrats`, v))} {...contrat} />
          <Form titre="Mission sous-traitée" champs={[
            { name: 'sous_traitant_id', label: 'ID sous-traitant', type: 'number', required: true, num: true },
            { name: 'contrat_id', label: 'ID contrat', type: 'number', num: true },
            { name: 'client_id', label: 'ID client', type: 'number', required: true, num: true },
            { name: 'date_mission', label: 'Date mission', type: 'date', required: true },
            { name: 'point_depart', label: 'Point de départ', required: true },
            { name: 'point_arrivee', label: 'Point d’arrivée', required: true },
            { name: 'distance', label: 'Distance (km)', type: 'number', num: true },
            { name: 'type_marchandise', label: 'Type marchandise' },
            { name: 'poids', label: 'Poids (kg)', type: 'number', num: true },
            { name: 'cout_estime', label: 'Coût estimé (XAF)', type: 'number', num: true },
          ]} onSubmit={(v) => missionSt.run(() => apiClient.post(`${B}/sous-traitants/missions`, v))} {...missionSt} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Accidents & maintenance préventive</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Déclarer un accident" champs={[
            { name: 'vehicule_id', label: 'ID véhicule', type: 'number', required: true, num: true },
            { name: 'conducteur_id', label: 'ID conducteur', type: 'number', required: true, num: true },
            { name: 'mission_id', label: 'ID mission', type: 'number', num: true },
            { name: 'date_accident', label: 'Date/heure', type: 'datetime-local', required: true },
            { name: 'heure_accident', label: 'Heure (HH:MM)' },
            { name: 'lieu', label: 'Lieu', required: true },
            { name: 'type_accident', label: 'Type (collision/renversement/…)' },
            { name: 'gravite', label: 'Gravité (leger/modere/grave)' },
            { name: 'blesses', label: 'Blessés', type: 'number', num: true },
            { name: 'deces', label: 'Décès', type: 'number', num: true },
            { name: 'montant_dommages', label: 'Dommages (XAF)', type: 'number', num: true },
            { name: 'notes', label: 'Notes', textarea: true },
          ]} onSubmit={(v) => accident.run(() => apiClient.post(`${B}/accidents`, v))} {...accident} />
          <Form titre="Enquête accident" champs={[
            { name: 'accident_id', label: 'ID accident', type: 'number', required: true, num: true },
            { name: 'statut', label: 'Statut' },
            { name: 'constat', label: 'Constat', textarea: true },
            { name: 'notes', label: 'Notes', textarea: true },
            { name: 'montant_rembourse', label: 'Remboursé (XAF)', type: 'number', num: true },
            { name: 'date_clos', label: 'Date clôture', type: 'date' },
          ]} onSubmit={(v) => {
            const { accident_id, ...body } = v;
            return enquete.run(() => apiClient.put(`${B}/accidents/${accident_id}/enquete`, body));
          }} {...enquete} />
          <Form titre="Maintenance préventive planifiée" champs={[
            { name: 'vehicule_id', label: 'ID véhicule', type: 'number', required: true, num: true },
            { name: 'type_maintenance', label: 'Type (vidange/freins/…)', required: true },
            { name: 'kilometrage_prevu', label: 'Km prévu', type: 'number', required: true, num: true },
            { name: 'date_prevue', label: 'Date prévue', type: 'date', required: true },
            { name: 'periodicite', label: 'Périodicité (km)', type: 'number', num: true },
            { name: 'cout_estime', label: 'Coût estimé (XAF)', type: 'number', num: true },
            { name: 'notes', label: 'Notes', textarea: true },
          ]} onSubmit={(v) => maintenance.run(() => apiClient.post(`${B}/maintenance-preventive`, v))} {...maintenance} />
          <Form titre="Exécuter une maintenance" champs={[
            { name: 'maintenance_id', label: 'ID maintenance', type: 'number', required: true, num: true },
            { name: 'date_effective', label: 'Date effective', type: 'date' },
            { name: 'cout_reel', label: 'Coût réel (XAF)', type: 'number', num: true },
            { name: 'realise_par', label: 'Réalisé par' },
            { name: 'notes', label: 'Notes', textarea: true },
          ]} onSubmit={(v) => {
            const { maintenance_id, ...body } = v;
            return execMaint.run(() => apiClient.put(`${B}/maintenance-preventive/${maintenance_id}/executer`, body));
          }} {...execMaint} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">GPS & géofencing</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Position GPS véhicule" champs={[
            { name: 'vehicule_id', label: 'ID véhicule', type: 'number', required: true, num: true },
            { name: 'conducteur_id', label: 'ID conducteur', type: 'number', num: true },
            { name: 'latitude', label: 'Latitude', type: 'number', required: true, num: true },
            { name: 'longitude', label: 'Longitude', type: 'number', required: true, num: true },
            { name: 'vitesse', label: 'Vitesse (km/h)', type: 'number', num: true },
            { name: 'direction', label: 'Direction (°)', type: 'number', num: true },
            { name: 'statut_moteur', label: 'Moteur (on/off)' },
            { name: 'kilmetrage_actuel', label: 'Kilométrage', type: 'number', num: true },
            { name: 'alerte', label: 'Alerte' },
          ]} onSubmit={(v) => gpsPos.run(() => apiClient.post(`${B}/gps/positions`, v))} {...gpsPos} />
          <Form titre="Zone de géofencing" champs={[
            { name: 'nom_zone', label: 'Nom zone', required: true },
            { name: 'type_zone', label: 'Type (dépôt/client/zone-franche/…)' },
            { name: 'latitude_centre', label: 'Latitude centre', type: 'number', required: true, num: true },
            { name: 'longitude_centre', label: 'Longitude centre', type: 'number', required: true, num: true },
            { name: 'rayon_metres', label: 'Rayon (m)', type: 'number', required: true, num: true },
            { name: 'ville', label: 'Ville' },
            { name: 'limite_vitesse', label: 'Limite vitesse (km/h)', type: 'number', num: true },
            { name: 'description', label: 'Description', textarea: true },
          ]} onSubmit={(v) => geoZone.run(() => apiClient.post(`${B}/geofencing/zones`, v))} {...geoZone} />
          <Form titre="Événement véhicule (violation, excès…)" champs={[
            { name: 'vehicule_id', label: 'ID véhicule', type: 'number', required: true, num: true },
            { name: 'type_evenement', label: 'Type événement', required: true },
            { name: 'localisation', label: 'Localisation' },
            { name: 'operateur', label: 'Opérateur' },
            { name: 'description', label: 'Description', textarea: true },
          ]} onSubmit={(v) => geoEvt.run(() => apiClient.post(`${B}/geofencing/evenements`, v))} {...geoEvt} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Dispatch intelligent (complète)</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Optimisation de tournées" champs={[
            { name: 'missions_ids', label: 'IDs missions (séparés par virgule)', required: true, list: true },
            { name: 'contraintes', label: 'Contraintes (JSON, optionnel)', textarea: true },
          ]} onSubmit={(v) => {
            const body: Record<string, unknown> = { missions_ids: v.missions_ids };
            if (typeof v.contraintes === 'string' && v.contraintes.trim()) {
              try { body.contraintes = JSON.parse(v.contraintes); } catch { /* ignoré */ }
            }
            return optimisation.run(() => apiClient.post(`${BC}/dispatch/optimisation`, body));
          }} {...optimisation} />
          <Form titre="Planification automatique (journée)" champs={[
            { name: 'date_jour', label: 'Date', type: 'date', required: true },
          ]} onSubmit={(v) => planif.run(() => apiClient.post(`${BC}/dispatch/planification-automatique`, null, { params: { date_jour: v.date_jour } }))} {...planif} />
          <Form titre="Attribution intelligente d'une mission" champs={[
            { name: 'mission_id', label: 'ID mission', type: 'number', required: true, num: true },
          ]} onSubmit={(v) => attribution.run(() => apiClient.post(`${BC}/dispatch/attribution-intelligente/${v.mission_id}`))} {...attribution} />
          <Form titre="Recalcul itinéraire (événement)" champs={[
            { name: 'dispatch_id', label: 'ID dispatch', type: 'number', required: true, num: true },
            { name: 'evenement', label: 'Événement (panne/retard/…)', required: true },
          ]} onSubmit={(v) => recalcul.run(() => apiClient.post(`${BC}/dispatch/${v.dispatch_id}/recalcul`, null, { params: { evenement: v.evenement } }))} {...recalcul} />
          <Form titre="Modifier un dispatch" champs={[
            { name: 'dispatch_id', label: 'ID dispatch', type: 'number', required: true, num: true },
            { name: 'statut', label: 'Statut' },
            { name: 'distance_reelle', label: 'Distance réelle (km)', type: 'number', num: true },
            { name: 'duree_reelle', label: 'Durée réelle (min)', type: 'number', num: true },
            { name: 'cout_reel', label: 'Coût réel (XAF)', type: 'number', num: true },
            { name: 'notes', label: 'Notes', textarea: true },
          ]} onSubmit={(v) => {
            const { dispatch_id, ...body } = v;
            return dispatchEdit.run(() => apiClient.put(`${BC}/dispatch/${dispatch_id}`, body));
          }} {...dispatchEdit} />
          <Form titre="Équilibre de charge chauffeurs" champs={[
            { name: 'periode_debut', label: 'Début', type: 'date', required: true },
            { name: 'periode_fin', label: 'Fin', type: 'date', required: true },
          ]} onSubmit={(v) => equilibre.run(() => apiClient.get(`${BC}/dispatch/equilibre-charge`, {
            params: { periode_debut: v.periode_debut, periode_fin: v.periode_fin },
          }))} {...equilibre} />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4">
          <QuickGet titre="Liste des dispatches" run={dispatchList} url={() => `${BC}/dispatch`} />
          <Form titre="Détail dispatch" champs={[
            { name: 'dispatch_id', label: 'ID dispatch', type: 'number', required: true },
          ]} onSubmit={(v) => dispatchDetail.run(() => apiClient.get(`${BC}/dispatch/${v.dispatch_id}`))} {...dispatchDetail} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Arrêts de tournée</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Créer un arrêt" champs={[
            { name: 'dispatch_id', label: 'ID dispatch', type: 'number', required: true, num: true },
            { name: 'type_arret', label: 'Type (livraison/chargement/pause/…)', required: true },
            { name: 'ordre_sequence', label: 'Ordre séquence', type: 'number', required: true, num: true },
            { name: 'adresse', label: 'Adresse', required: true },
            { name: 'duree_estimee', label: 'Durée estimée (min)', type: 'number', num: true },
            { name: 'client_id', label: 'ID client', type: 'number', num: true },
            { name: 'latitude', label: 'Latitude', type: 'number', num: true },
            { name: 'longitude', label: 'Longitude', type: 'number', num: true },
          ]} onSubmit={(v) => arret.run(() => apiClient.post(`${BC}/arrets`, v))} {...arret} />
          <Form titre="Arrêts d'un dispatch" champs={[
            { name: 'dispatch_id', label: 'ID dispatch', type: 'number', required: true },
          ]} onSubmit={(v) => arretsList.run(() => apiClient.get(`${BC}/arrets/${v.dispatch_id}`))} {...arretsList} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Preuves de livraison (POD / e-POD)</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Créer une POD" champs={[
            { name: 'livraison_id', label: 'ID livraison', type: 'number', required: true, num: true },
            { name: 'signature_client', label: 'Signature (données/base64)' },
            { name: 'photo_marchandise', label: 'Photo marchandise (URL/base64)' },
            { name: 'coordonnees_livraison', label: 'Coordonnées livraison' },
          ]} onSubmit={(v) => pod.run(() => apiClient.post(`${BC}/pod`, v))} {...pod} />
          <Form titre="Action POD (valider / facturation / archivage)" champs={[
            { name: 'pod_id', label: 'ID POD', type: 'number', required: true, num: true },
            { name: 'action', label: 'Action', type: 'select', required: true, options: ['valider', 'integration-facturation', 'archivage-legal'] },
          ]} onSubmit={(v) => {
            const map: Record<string, string> = {
              valider: 'valider',
              'integration-facturation': 'integration-facturation',
              'archivage-legal': 'archivage-legal',
            };
            const action = map[String(v.action)] ?? 'valider';
            return podAction.run(() => apiClient.post(`${BC}/pod/${v.pod_id}/${action}`));
          }} {...podAction} />
          <Form titre="Lister les PODs" champs={[
            { name: 'statut', label: 'Statut (optionnel)' },
          ]} onSubmit={(v) => podList.run(() => apiClient.get(`${BC}/pod`, {
            params: v.statut ? { statut: v.statut } : undefined,
          }))} {...podList} />
          <Form titre="Ajouter un document POD" champs={[
            { name: 'pod_id', label: 'ID POD', type: 'number', required: true, num: true },
            { name: 'type_document', label: 'Type document', required: true },
            { name: 'nom_fichier', label: 'Nom fichier', required: true },
            { name: 'url_fichier', label: 'URL fichier', required: true },
            { name: 'type_mime', label: 'Type MIME' },
          ]} onSubmit={(v) => docPod.run(() => apiClient.post(`${BC}/documents-pod`, v))} {...docPod} />
          <Form titre="Documents d'une POD" champs={[
            { name: 'pod_id', label: 'ID POD', type: 'number', required: true },
          ]} onSubmit={(v) => docsPod.run(() => apiClient.get(`${BC}/documents-pod/${v.pod_id}`))} {...docsPod} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Analytics transport (complète)</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <QuickGet titre="Tableau de bord transport" run={tb} url={() => `${BC}/analytics/tableau-bord`} />
          <Form titre="KPI transport" champs={[
            { name: 'periode', label: 'Période (ex. 2025-01 ou mois)', required: true },
            { name: 'conducteur_id', label: 'ID conducteur', type: 'number', num: true },
            { name: 'camion_id', label: 'ID camion', type: 'number', num: true },
          ]} onSubmit={(v) => kpi.run(() => apiClient.get(`${BC}/analytics/kpi`, {
            params: {
              periode: v.periode,
              conducteur_id: v.conducteur_id ? Number(v.conducteur_id) : undefined,
              camion_id: v.camion_id ? Number(v.camion_id) : undefined,
            },
          }))} {...kpi} />
          <QuickGet titre="Alertes de performance" run={alertes} url={() => `${BC}/analytics/alertes`} />
        </div>
      </section>
    </div>
  );
}
