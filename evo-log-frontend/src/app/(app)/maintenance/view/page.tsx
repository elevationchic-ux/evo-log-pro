'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  Wrench,
  ArrowLeft,
  Truck,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Printer,
  Edit,
  User,
  Calendar,
  Layers
} from 'lucide-react';
import { maintenanceAPI } from '@/lib/api-client';
import { toast } from 'sonner';

import CompanyDocumentHeader, { CompanyDocumentFooter } from '@/components/documents/CompanyDocumentHeader';

export default function MaintenanceViewPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get('id');

  const [order, setOrder] = useState<any | null>(null);
  const [loading, setLoading] = useState(!!id);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    maintenanceAPI.getMaintenance(Number(id))
      .then(res => setOrder(res.data))
      .catch(() => setError("Ordre de travail de maintenance introuvable ou accès refusé."))
      .finally(() => setLoading(false));
  }, [id]);

  if (!id) {
    return (
      <div className="p-6 max-w-2xl mx-auto text-center space-y-4">
        <Wrench className="w-16 h-16 text-amber-500/40 mx-auto" />
        <h1 className="text-xl font-bold text-on-surface">Consultation d'un Ordre de Travail Atelier</h1>
        <p className="text-sm text-on-surface-variant">
          Veuillez sélectionner un ordre d'intervention depuis la liste de maintenance, ou saisir son numéro.
        </p>
        <div className="flex gap-2 justify-center">
          <input
            type="number"
            placeholder="N° Ordre de travail"
            className="px-4 py-2 border border-outline rounded-xl text-sm bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                const val = (e.target as HTMLInputElement).value;
                if (val) router.push(`/maintenance/view?id=${val}`);
              }
            }}
          />
          <button
            onClick={() => router.push('/maintenance')}
            className="px-4 py-2 bg-primary text-on-primary rounded-xl text-sm font-semibold hover:opacity-90 flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" /> Retour GMAO
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

  if (error || !order) {
    return (
      <div className="p-6 max-w-xl mx-auto text-center space-y-4">
        <AlertTriangle className="w-14 h-14 text-amber-500 mx-auto" />
        <h2 className="text-xl font-bold text-on-surface">Ordre de Travail Introuvable</h2>
        <p className="text-sm text-on-surface-variant">{error || "Cet ordre de maintenance GMAO n'existe pas."}</p>
        <button
          onClick={() => router.push('/maintenance')}
          className="px-4 py-2 bg-primary text-on-primary rounded-xl text-sm font-semibold"
        >
          Retour à la GMAO
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
      {/* Official Dynamic Document Header */}
      <CompanyDocumentHeader
        documentTitle="Ordre de Travail & Réparation Atelier GMAO"
        documentNumber={String(order.id || id)}
        documentDate={order.created_at?.slice(0, 10) || new Date().toISOString().slice(0, 10)}
        documentReference={order.immatriculation_camion || order.vehicule_immatriculation}
      />

      {/* Screen action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-4 print:hidden">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-on-surface flex items-center gap-2">
              <Wrench className="w-5 h-5 text-amber-600" />
              Ordre de Travail #{order.id || id}
            </h1>
            <p className="text-xs text-on-surface-variant">
              Véhicule : {order.immatriculation_camion || order.vehicule_immatriculation || 'Non assigné'} • Atelier GMAO
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 px-3 py-2 text-xs font-semibold border border-outline rounded-xl hover:bg-surface-container text-on-surface"
          >
            <Printer className="w-4 h-4" /> Imprimer Fiche Atelier
          </button>
          <button
            onClick={() => router.push(`/maintenance/edit?id=${order.id || id}`)}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-on-primary rounded-xl hover:opacity-90"
          >
            <Edit className="w-4 h-4" /> Modifier OT
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Descriptif OT */}
        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Truck className="w-4 h-4 text-primary" /> Détails de l'Intervention
          </h2>
          <div className="space-y-2 text-xs">
            {[
              { label: 'Immatriculation Engin', value: order.immatriculation_camion || order.vehicule_immatriculation || 'Non spécifié' },
              { label: 'Type de Maintenance', value: order.type_maintenance || 'Curative / Dépannage' },
              { label: 'Priorité', value: order.priorite || 'Normale' },
              { label: 'Statut Atelier', value: order.statut || 'En cours' },
              { label: 'Kilométrage Compteur', value: order.kilometrage ? `${order.kilometrage} km` : 'Non relevé' },
              { label: 'Date Déclaration', value: order.created_at || 'Date courante' },
            ].map(row => (
              <div key={row.label} className="flex justify-between py-1 border-b border-outline/30">
                <span className="text-on-surface-variant">{row.label} :</span>
                <span className="font-medium text-on-surface">{row.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Diagnostic et Pièces */}
        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Layers className="w-4 h-4 text-amber-600" /> Diagnostic & Pièces Remplacées
          </h2>
          <div className="text-xs text-on-surface space-y-3">
            <div>
              <p className="font-semibold text-on-surface-variant">Description du Problème :</p>
              <p className="mt-1 bg-surface-container-low p-2.5 rounded-xl border border-outline/50">
                {order.description || "Aucun descriptif fourni à la création de l'ordre de travail."}
              </p>
            </div>
            <div>
              <p className="font-semibold text-on-surface-variant">Pièces de Rechange Commandées / Sorties :</p>
              <p className="mt-1 bg-surface-container-low p-2.5 rounded-xl border border-outline/50">
                {order.pieces || "Aucune pièce magasin imputée à cet ordre."}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
