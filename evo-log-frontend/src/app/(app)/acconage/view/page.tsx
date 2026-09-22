'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  Anchor,
  ArrowLeft,
  Ship,
  Clock,
  CheckCircle2,
  Calendar,
  Layers,
  FileText,
  Printer,
  Edit,
  AlertTriangle
} from 'lucide-react';
import { acconageAPI } from '@/lib/api-client';
import { toast } from 'sonner';

import CompanyDocumentHeader from '@/components/documents/CompanyDocumentHeader';
import AcconageTemporaryDockersManager from '@/components/acconage/AcconageTemporaryDockersManager';

export default function AcconageViewPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get('id');

  const [operation, setOperation] = useState<any | null>(null);
  const [loading, setLoading] = useState(!!id);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    acconageAPI.getAcconage(Number(id))
      .then(res => setOperation(res.data))
      .catch(() => setError("Opération d'acconage introuvable ou accès restreint."))
      .finally(() => setLoading(false));
  }, [id]);

  if (!id) {
    return (
      <div className="p-6 max-w-2xl mx-auto text-center space-y-4">
        <Anchor className="w-16 h-16 text-cyan-500/40 mx-auto" />
        <h1 className="text-xl font-bold text-on-surface">Consultation d'une Opération d'Acconage</h1>
        <p className="text-sm text-on-surface-variant">
          Veuillez sélectionner une escale ou opération depuis le tableau de bord acconage, ou renseigner son identifiant.
        </p>
        <div className="flex gap-2 justify-center">
          <input
            type="number"
            placeholder="ID de l'escale / opération"
            className="px-4 py-2 border border-outline rounded-xl text-sm bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                const val = (e.target as HTMLInputElement).value;
                if (val) router.push(`/acconage/view?id=${val}`);
              }
            }}
          />
          <button
            onClick={() => router.push('/acconage')}
            className="px-4 py-2 bg-primary text-on-primary rounded-xl text-sm font-semibold hover:opacity-90 flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" /> Retour Acconage
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-6 space-y-4 animate-pulse max-w-5xl mx-auto">
        <div className="h-8 bg-surface-container rounded w-1/3" />
        <div className="h-4 bg-surface-container rounded w-1/2" />
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-20 bg-surface-container rounded-2xl" />
        ))}
      </div>
    );
  }

  if (error || !operation) {
    return (
      <div className="p-6 max-w-xl mx-auto text-center space-y-4">
        <AlertTriangle className="w-14 h-14 text-amber-500 mx-auto" />
        <h2 className="text-xl font-bold text-on-surface">Escale ou Opération Introuvable</h2>
        <p className="text-sm text-on-surface-variant">{error || "Cette fiche d'acconage n'existe pas."}</p>
        <button
          onClick={() => router.push('/acconage')}
          className="px-4 py-2 bg-primary text-on-primary rounded-xl text-sm font-semibold"
        >
          Retour à la liste des opérations
        </button>
      </div>
    );
  }

  const handlePrint = () => {
    toast.success('Génération et impression du dossier officiel d\'acconage...');
    window.print();
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
      {/* Official Corporate Header with Logo & Legal Info */}
      <CompanyDocumentHeader
        documentTitle="FICHE D'ESCALE & MANUTENTION PORTUAIRE"
        documentNumber={operation.numero_escale || `ESC-${operation.id}`}
        documentDate={operation.date_arrivee ? new Date(operation.date_arrivee).toLocaleDateString('fr-FR') : new Date().toLocaleDateString('fr-FR')}
        documentReference={`QUAI-${operation.quai || 'PAD'}-ROT-${operation.id}`}
      />

      {/* Screen Header Controls (Hidden on print) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5 print:hidden">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-on-surface flex items-center gap-2">
              <Ship className="w-6 h-6 text-cyan-600" />
              {operation.nom_navire || `Navire Escale #${operation.numero_escale || operation.id}`}
            </h1>
            <p className="text-sm text-on-surface-variant">
              Poste à quai : {operation.quai || 'Quai Conteneurs PAD'} • Armateur : {operation.armateur || 'Non renseigné'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrint}
            className="flex items-center gap-2 px-3 py-2 text-xs font-semibold border border-outline rounded-xl hover:bg-surface-container"
          >
            <Printer className="w-4 h-4" /> Imprimer Document Officiel
          </button>
          <button
            onClick={() => router.push(`/acconage/edit?id=${operation.id}`)}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-on-primary rounded-xl hover:opacity-90"
          >
            <Edit className="w-4 h-4" /> Modifier l'Escale
          </button>
        </div>
      </div>

      {/* Grid details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Détails Opérationnels */}
        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Anchor className="w-4 h-4 text-primary" /> Manutention & Mouvements Quai
          </h2>
          <div className="space-y-2 text-xs">
            {[
              { label: 'N° Escale', value: operation.numero_escale || `ESC-${operation.id}` },
              { label: "Type d'Opération", value: operation.type_operation || 'Déchargement / Chargement' },
              { label: 'Conteneurs 20ft', value: operation.nb_20ft || 0 },
              { label: 'Conteneurs 40ft', value: operation.nb_40ft || 0 },
              { label: 'Total TEU', value: `${operation.nombre_conteneurs || 0} TEU` },
              { label: 'Tonnage Total Brut', value: operation.tonnage ? `${operation.tonnage} T` : 'En cours de pointage' },
            ].map(row => (
              <div key={row.label} className="flex justify-between py-1 border-b border-outline/30">
                <span className="text-on-surface-variant">{row.label} :</span>
                <span className="font-medium text-on-surface">{row.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Cadences & Moyens Déployés */}
        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-600" /> Moyens Nautiques & Cadences
          </h2>
          <div className="space-y-2 text-xs">
            {[
              { label: 'Grues Portiques Affectées', value: operation.grues || 'Portique STS 01 & STS 02' },
              { label: 'Équipes de Dockers', value: operation.equipes || '2 Shifts (24h/24)' },
              { label: 'Cadence Moyenne', value: operation.cadence ? `${operation.cadence} mvts/h` : '22 mouvements/heure' },
              { label: 'Remorquage & Pilotage', value: operation.remorquage || 'Effectué par PAD Harbour' },
              { label: 'Date Arrivée Quai (ETA/ATA)', value: operation.date_arrivee || 'Conforme au plan de tirage' },
              { label: 'Date Départ Prévue (ETD)', value: operation.date_depart || 'Selon avancement shifts' },
            ].map(row => (
              <div key={row.label} className="flex justify-between py-1 border-b border-outline/30">
                <span className="text-on-surface-variant">{row.label} :</span>
                <span className="font-medium text-on-surface">{row.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Dockers Temporaires & Shifts — Restriction stricte à la durée du déchargement */}
      <div className="pt-4 border-t border-outline">
        <AcconageTemporaryDockersManager
          escaleId={operation.id}
          escaleNumero={operation.numero_escale || `ESC-${operation.id}`}
          escaleStatut={operation.statut || 'EN_COURS'}
          navireNom={operation.nom_navire}
        />
      </div>
    </div>
  );
}
