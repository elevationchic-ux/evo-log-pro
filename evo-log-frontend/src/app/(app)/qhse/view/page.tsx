'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  ShieldCheck,
  ArrowLeft,
  ShieldAlert,
  Printer,
  Edit,
  MapPin,
  Clock,
  AlertTriangle,
  CheckCircle2,
  FileText
} from 'lucide-react';
import { qhseAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function QhseViewPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get('id');

  const [record, setRecord] = useState<any | null>(null);
  const [loading, setLoading] = useState(!!id);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    qhseAPI.getQhseRecord(Number(id))
      .then(res => setRecord(res.data))
      .catch(() => setError("Rapport d'audit QHSE introuvable ou accès refusé."))
      .finally(() => setLoading(false));
  }, [id]);

  if (!id) {
    return (
      <div className="p-6 max-w-2xl mx-auto text-center space-y-4">
        <ShieldCheck className="w-16 h-16 text-emerald-500/40 mx-auto" />
        <h1 className="text-xl font-bold text-on-surface">Consultation d'un Rapport QHSE</h1>
        <p className="text-sm text-on-surface-variant">
          Veuillez sélectionner un rapport d'inspection ou d'incident QHSE, ou saisir son numéro.
        </p>
        <div className="flex gap-2 justify-center">
          <input
            type="number"
            placeholder="ID du rapport QHSE"
            className="px-4 py-2 border border-outline rounded-xl text-sm bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                const val = (e.target as HTMLInputElement).value;
                if (val) router.push(`/qhse/view?id=${val}`);
              }
            }}
          />
          <button
            onClick={() => router.push('/qhse')}
            className="px-4 py-2 bg-primary text-on-primary rounded-xl text-sm font-semibold hover:opacity-90 flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" /> Retour QHSE
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

  if (error || !record) {
    return (
      <div className="p-6 max-w-xl mx-auto text-center space-y-4">
        <AlertTriangle className="w-14 h-14 text-amber-500 mx-auto" />
        <h2 className="text-xl font-bold text-on-surface">Rapport QHSE Introuvable</h2>
        <p className="text-sm text-on-surface-variant">{error || "Ce rapport de conformité QHSE n'existe pas."}</p>
        <button
          onClick={() => router.push('/qhse')}
          className="px-4 py-2 bg-primary text-on-primary rounded-xl text-sm font-semibold"
        >
          Retour au module QHSE
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-on-surface flex items-center gap-2">
              <ShieldCheck className="w-6 h-6 text-emerald-600" />
              Audit & Inspection QHSE #{record.id || id}
            </h1>
            <p className="text-sm text-on-surface-variant">
              Site / Emplacement : {record.site_location || 'Dépôt principal'} • Sécurité & Environnement
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => toast.success("Génération de la fiche d'inspection QHSE au format PDF...")}
            className="flex items-center gap-2 px-3 py-2 text-xs font-semibold border border-outline rounded-xl hover:bg-surface-container"
          >
            <Printer className="w-4 h-4" /> Imprimer Fiche
          </button>
          <button
            onClick={() => router.push(`/qhse/edit?id=${record.id || id}`)}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-on-primary rounded-xl hover:opacity-90"
          >
            <Edit className="w-4 h-4" /> Modifier l'Audit
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-primary" /> Périmètre & Évaluation des Risques
          </h2>
          <div className="space-y-2 text-xs">
            {[
              { label: 'Site / Zone Contrôlée', value: record.site_location || 'Non renseigné' },
              { label: 'Niveau de Risque', value: record.niveau_risque || 'Faible' },
              { label: 'Type de Contrôle', value: record.type_controle || 'Inspection de routine' },
              { label: 'Conformité EPI', value: record.conformite_epi ? '100% Conforme' : 'Conforme avec remarques' },
              { label: 'Auditeur / Inspecteur', value: record.inspecteur || 'Responsable QHSE' },
              { label: 'Date de Visite', value: record.created_at || 'Date courante' },
            ].map(row => (
              <div key={row.label} className="flex justify-between py-1 border-b border-outline/30">
                <span className="text-on-surface-variant">{row.label} :</span>
                <span className="font-medium text-on-surface">{row.value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <FileText className="w-4 h-4 text-emerald-600" /> Observations & Mesures Correctives
          </h2>
          <div className="text-xs text-on-surface space-y-3">
            <div>
              <p className="font-semibold text-on-surface-variant">Observations Relevées :</p>
              <p className="mt-1 bg-surface-container-low p-2.5 rounded-xl border border-outline/50">
                {record.observations || "Aucune anomalie ou non-conformité relevée lors de l'inspection."}
              </p>
            </div>
            <div>
              <p className="font-semibold text-on-surface-variant">Plan d'Actions Correctives :</p>
              <p className="mt-1 bg-surface-container-low p-2.5 rounded-xl border border-outline/50">
                {record.actions_correctives || "Maintien des consignes de sécurité et des vérifications journalières des extincteurs et trousses de secours."}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
