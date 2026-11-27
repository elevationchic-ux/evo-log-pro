'use client';

import React, { useState } from 'react';
import { metierAPI } from '@/lib/api-client';

type Data = Record<string, unknown>;

function Result({ data, loading, error }: { data: Data | null; loading: boolean; error: string | null }) {
  if (loading) return <p className="text-sm text-gray-400">Calcul en cours…</p>;
  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!data) return null;
  if (typeof data.note === 'string') return <p className="text-sm text-amber-700">{String(data.note)}</p>;
  return (
    <pre className="text-xs bg-gray-50 border rounded p-3 overflow-auto max-h-72">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

interface Champ { name: string; label: string; type?: string; required?: boolean; placeholder?: string }

function Form({ titre, champs, onSubmit, result, loading, error }: {
  titre: string;
  champs: Champ[];
  onSubmit: (vals: Record<string, string>) => void;
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
              placeholder={c.placeholder}
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
      setError(e instanceof Error ? e.message : 'Erreur');
    } finally { setLoading(false); }
  };
  return { result, loading, error, run };
}

export default function MetierCalculsPage() {
  const fretAerien = useRun();
  const fretFerro = useRun();
  const fretFluvial = useRun();
  const fret3pl = useRun();
  const tarif = useRun();
  const conges = useRun();
  const bulletin = useRun();
  const cycle = useRun();
  const coursier = useRun();
  const corrosion = useRun();
  const valorisation = useRun();
  const froid = useRun();

  return (
    <div className="p-6 space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Calculateurs & analyses détaillées</h1>
        <p className="text-sm text-gray-500">Formulaires de calcul fret/tarif et recherches paramétrées.</p>
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Calculateurs de fret & tarifs</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Fret aérien" onSubmit={(v) => fretAerien.run(() => metierAPI.postFretAerien(v.code_tarif, Number(v.poids_kg)))}
            champs={[
              { name: 'code_tarif', label: 'Code tarif', required: true },
              { name: 'poids_kg', label: 'Poids (kg)', type: 'number', required: true },
            ]} {...fretAerien} />
          <Form titre="Fret ferroviaire" onSubmit={(v) => fretFerro.run(() => metierAPI.postFretFerrovial(v.code_tarif, Number(v.tonnes), Number(v.distance_km), v.type_marchandise || undefined))}
            champs={[
              { name: 'code_tarif', label: 'Code tarif', required: true },
              { name: 'tonnes', label: 'Tonnage', type: 'number', required: true },
              { name: 'distance_km', label: 'Distance (km)', type: 'number', required: true },
              { name: 'type_marchandise', label: 'Type marchandise' },
            ]} {...fretFerro} />
          <Form titre="Fret fluvial (lettre de voiture)" onSubmit={(v) => fretFluvial.run(() => metierAPI.postFretFluvial(Number(v.waybill_id), v.code_tarif))}
            champs={[
              { name: 'waybill_id', label: 'ID lettre de voiture', type: 'number', required: true },
              { name: 'code_tarif', label: 'Code tarif', required: true },
            ]} {...fretFluvial} />
          <Form titre="Fret 3PL" onSubmit={(v) => fret3pl.run(() => metierAPI.postFret3pl(v.code_tarif, Number(v.poids_kg)))}
            champs={[
              { name: 'code_tarif', label: 'Code tarif', required: true },
              { name: 'poids_kg', label: 'Poids (kg)', type: 'number', required: true },
            ]} {...fret3pl} />
          <Form titre="Tarif grille (HT + TVA)" onSubmit={(v) => tarif.run(() => metierAPI.postTarifCalculer(v.code, Number(v.quantite)))}
            champs={[
              { name: 'code', label: 'Code tarif', required: true },
              { name: 'quantite', label: 'Quantité', type: 'number', required: true },
            ]} {...tarif} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3 border-b pb-2">Analyses paramétrées</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Form titre="Congés collaborateur" onSubmit={(v) => conges.run(() => metierAPI.getRhConges(v.collaborateur))}
            champs={[{ name: 'collaborateur', label: 'Nom collaborateur', required: true }]}
            {...conges} />
          <Form titre="Bulletin de paie" onSubmit={(v) => bulletin.run(() => metierAPI.getPaieBulletin(Number(v.employe_id), Number(v.annee), Number(v.mois)))}
            champs={[
              { name: 'employe_id', label: 'ID employé', type: 'number', required: true },
              { name: 'annee', label: 'Année', type: 'number', required: true, placeholder: '2025' },
              { name: 'mois', label: 'Mois', type: 'number', required: true, placeholder: '1-12' },
            ]} {...bulletin} />
          <Form titre="Cycle conteneur" onSubmit={(v) => cycle.run(() => metierAPI.getConteneurCycle(Number(v.cycle_id)))}
            champs={[{ name: 'cycle_id', label: 'ID cycle', type: 'number', required: true }]}
            {...cycle} />
          <Form titre="Performance coursier" onSubmit={(v) => coursier.run(() => metierAPI.getCoursierPerformance(v.livreur))}
            champs={[{ name: 'livreur', label: 'Nom livreur', required: true }]}
            {...coursier} />
          <Form titre="Corrosion pipeline" onSubmit={(v) => corrosion.run(() => metierAPI.getPipelineCorrosion(v.troncon, Number(v.seuil)))}
            champs={[
              { name: 'troncon', label: 'Tronçon', required: true },
              { name: 'seuil', label: 'Seuil min (mm)', type: 'number', required: true, placeholder: '3' },
            ]} {...corrosion} />
          <Form titre="Valorisation douanière" onSubmit={(v) => valorisation.run(() => metierAPI.getDouaneValorisation(Number(v.valuation_id)))}
            champs={[{ name: 'valuation_id', label: 'ID valorisation', type: 'number', required: true }]}
            {...valorisation} />
          <Form titre="Bilan chambre froide" onSubmit={(v) => froid.run(() => metierAPI.getFroidBilan(v.chambre))}
            champs={[{ name: 'chambre', label: 'Nom chambre', required: true }]}
            {...froid} />
        </div>
      </section>
    </div>
  );
}
