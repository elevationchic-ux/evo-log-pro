'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { apiClient } from '@/lib/api-client';
import { ArrowLeft } from 'lucide-react';

// ============================================================================
// Analytique transport avancé — endpoints GET paramétrés de
// /api/v1/transport-avance (coûts km, carburant, temps de conduite,
// sous-traitants, accidents, maintenance, GPS, géofencing, conducteurs, KPIs)
// ============================================================================

type Data = Record<string, unknown>;

function Result({ data, loading, error }: { data: Data | null; loading: boolean; error: string | null }) {
  if (loading) return <p className="text-sm text-gray-400">Calcul en cours…</p>;
  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!data) return null;
  if (typeof data.note === 'string') return <p className="text-sm text-amber-700">{String(data.note)}</p>;
  return <pre className="text-xs bg-gray-50 border rounded p-3 overflow-auto max-h-72">{JSON.stringify(data, null, 2)}</pre>;
}

interface Champ { name: string; label: string; type?: string; required?: boolean }

function Form({ titre, champs, onSubmit, result, loading, error }: {
  titre: string;
  champs: Champ[];
  onSubmit: (v: Record<string, string>) => void;
  result: Data | null; loading: boolean; error: string | null;
}) {
  const [vals, setVals] = useState<Record<string, string>>({});
  return (
    <div className="bg-white border rounded-xl p-5 shadow-sm">
      <h3 className="font-semibold mb-3">{titre}</h3>
      <form
        className="grid grid-cols-2 gap-3 mb-3"
        onSubmit={(e) => { e.preventDefault(); onSubmit(vals); }}
      >
        {champs.map((c) => (
          <label key={c.name} className="text-sm">
            <span className="block text-xs text-gray-500 mb-1">{c.label}</span>
            <input
              type={c.type ?? 'text'}
              required={c.required}
              value={vals[c.name] ?? ''}
              onChange={(e) => setVals({ ...vals, [c.name]: e.target.value })}
              className="w-full border rounded px-2 py-1.5 text-sm"
            />
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

function useRun() {
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
const PERIODE: Champ[] = [
  { name: 'debut', label: 'Début (YYYY-MM-DD)', type: 'date', required: true },
  { name: 'fin', label: 'Fin (YYYY-MM-DD)', type: 'date', required: true },
];

export default function TransportAvanceAnalytiquePage() {
  const coutKm = useRun();
  const carburant = useRun();
  const temps = useRun();
  const sousTraitant = useRun();
  const accidents = useRun();
  const urgentes = useRun();
  const gpsPos = useRun();
  const gpsTraj = useRun();
  const geo = useRun();
  const conducteur = useRun();
  const kpiPonct = useRun();
  const kpiUtil = useRun();
  const kpiCarb = useRun();

  return (
    <div className="p-6 space-y-8">
      <div className="flex items-center gap-3">
        <Link href="/transport-avance/donnees" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Analytique transport avancé</h1>
          <p className="text-sm text-gray-500">Coûts, carburant, temps de conduite, accidents, GPS et KPIs flotte.</p>
        </div>
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Coûts & consommations</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Coût par kilomètre (mois)" champs={[
            { name: 'camion_id', label: 'ID camion', type: 'number', required: true },
            { name: 'mois', label: 'Mois (1-12)', type: 'number', required: true },
            { name: 'annee', label: 'Année', type: 'number', required: true },
          ]} onSubmit={(v) => coutKm.run(() => apiClient.get(`${B}/frais-km/cout/${v.camion_id}/${v.mois}/${v.annee}`))}
            {...coutKm} />
          <Form titre="Anomalie carburant" champs={[
            { name: 'vehicule_id', label: 'ID véhicule', type: 'number', required: true },
            { name: 'consommation_actuelle', label: 'Conso actuelle (L/100km)', type: 'number', required: true },
            { name: 'consommation_theorique', label: 'Conso théorique (L/100km)', type: 'number', required: true },
            { name: 'tolerance', label: 'Tolérance (0-1)', type: 'number' },
          ]} onSubmit={(v) => carburant.run(() => apiClient.get(`${B}/carburant/anomalie/${v.vehicule_id}`, {
            params: {
              consommation_actuelle: Number(v.consommation_actuelle),
              consommation_theorique: Number(v.consommation_theorique),
              tolerance: v.tolerance ? Number(v.tolerance) : undefined,
            },
          }))} {...carburant} />
          <Form titre="Variance carburant (KPI)" champs={[
            { name: 'vehicule_id', label: 'ID véhicule', type: 'number', required: true },
            ...PERIODE,
          ]} onSubmit={(v) => kpiCarb.run(() => apiClient.get(`${B}/kpi/variance-carburant/${v.vehicule_id}`, {
            params: { debut_periode: v.debut, fin_periode: v.fin },
          }))} {...kpiCarb} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Conduite & sécurité</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Conformité temps de conduite" champs={[
            { name: 'conducteur_id', label: 'ID conducteur', type: 'number', required: true },
            { name: 'date_verif', label: 'Date vérif (YYYY-MM-DD)', type: 'date', required: true },
          ]} onSubmit={(v) => temps.run(() => apiClient.get(`${B}/temps-conduite/conformite/${v.conducteur_id}/${v.date_verif}`))}
            {...temps} />
          <Form titre="Comportement conducteur" champs={[
            { name: 'conducteur_id', label: 'ID conducteur', type: 'number', required: true },
            ...PERIODE,
          ]} onSubmit={(v) => conducteur.run(() => apiClient.get(`${B}/conducteurs/${v.conducteur_id}/comportement`, {
            params: { debut_periode: v.debut, fin_periode: v.fin },
          }))} {...conducteur} />
          <Form titre="Statistiques accidents" champs={PERIODE}
            onSubmit={(v) => accidents.run(() => apiClient.get(`${B}/accidents/statistiques`, {
              params: { debut_periode: v.debut, fin_periode: v.fin },
            }))} {...accidents} />
          <Form titre="Vérification géofencing" champs={[
            { name: 'vehicule_id', label: 'ID véhicule', type: 'number', required: true },
            { name: 'latitude', label: 'Latitude', type: 'number', required: true },
            { name: 'longitude', label: 'Longitude', type: 'number', required: true },
          ]} onSubmit={(v) => geo.run(() => apiClient.get(`${B}/geofencing/verifier/${v.vehicule_id}`, {
            params: { latitude: Number(v.latitude), longitude: Number(v.longitude) },
          }))} {...geo} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Flotte, sous-traitance & KPIs</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Dernière position GPS" champs={[
            { name: 'vehicule_id', label: 'ID véhicule', type: 'number', required: true },
          ]} onSubmit={(v) => gpsPos.run(() => apiClient.get(`${B}/gps/derniere-position/${v.vehicule_id}`))}
            {...gpsPos} />
          <Form titre="Trajectoire GPS" champs={[
            { name: 'vehicule_id', label: 'ID véhicule', type: 'number', required: true },
            { name: 'debut', label: 'Début (ISO datetime)', type: 'datetime-local', required: true },
            { name: 'fin', label: 'Fin (ISO datetime)', type: 'datetime-local', required: true },
          ]} onSubmit={(v) => gpsTraj.run(() => apiClient.get(`${B}/gps/trajectoire/${v.vehicule_id}`, {
            params: { debut: v.debut, fin: v.fin },
          }))} {...gpsTraj} />
          <Form titre="Performance sous-traitant" champs={[
            { name: 'sous_traitant_id', label: 'ID sous-traitant', type: 'number', required: true },
            ...PERIODE,
          ]} onSubmit={(v) => sousTraitant.run(() => apiClient.get(`${B}/sous-traitants/${v.sous_traitant_id}/performance`, {
            params: { debut_periode: v.debut, fin_periode: v.fin },
          }))} {...sousTraitant} />
          <Form titre="Maintenances préventives urgentes" champs={[
            { name: 'jours_critique', label: 'Jours critique', type: 'number' },
          ]} onSubmit={(v) => urgentes.run(() => apiClient.get(`${B}/maintenance-preventive/urgentes`, {
            params: { jours_critique: v.jours_critique ? Number(v.jours_critique) : undefined },
          }))} {...urgentes} />
          <Form titre="Taux livraison ponctuelle" champs={PERIODE}
            onSubmit={(v) => kpiPonct.run(() => apiClient.get(`${B}/kpi/livraison-ponctuelle`, {
              params: { debut_periode: v.debut, fin_periode: v.fin },
            }))} {...kpiPonct} />
          <Form titre="Utilisation véhicule" champs={[
            { name: 'vehicule_id', label: 'ID véhicule', type: 'number', required: true },
            { name: 'jours', label: 'Jours (défaut 30)', type: 'number' },
          ]} onSubmit={(v) => kpiUtil.run(() => apiClient.get(`${B}/kpi/utilisation-vehicules/${v.vehicule_id}`, {
            params: { jours: v.jours ? Number(v.jours) : undefined },
          }))} {...kpiUtil} />
        </div>
      </section>
    </div>
  );
}
