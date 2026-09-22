'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  FileSearch,
  ArrowLeft,
  FileText,
  Package,
  Clock,
  CheckCircle2,
  MapPin,
  Printer,
  Download,
  AlertTriangle
} from 'lucide-react';
import { transitAPI } from '@/lib/api-client';
import { toast } from 'sonner';

import CompanyDocumentHeader, { CompanyDocumentFooter } from '@/components/documents/CompanyDocumentHeader';

export default function TransitViewPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get('id');
  const [transit, setTransit] = useState<any | null>(null);
  const [loading, setLoading] = useState(!!id);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    transitAPI.getTransit(Number(id))
      .then(res => setTransit(res.data))
      .catch(() => setError('Dossier de transit introuvable ou accès refusé.'))
      .finally(() => setLoading(false));
  }, [id]);

  if (!id) {
    return (
      <div className="p-6 max-w-2xl mx-auto text-center space-y-4">
        <FileSearch className="w-16 h-16 text-on-surface-variant/40 mx-auto" />
        <h1 className="text-xl font-bold text-on-surface">Consultation d'un Dossier de Transit</h1>
        <p className="text-sm text-on-surface-variant">
          Accédez à cette page en cliquant sur l'icône "Voir" depuis la liste des dossiers de transit, ou saisissez un numéro de dossier ci-dessous.
        </p>
        <div className="flex gap-2 justify-center">
          <input
            type="number"
            placeholder="N° de dossier"
            className="px-4 py-2 border border-outline rounded-xl text-sm text-on-surface bg-surface-container-low focus:outline-none focus:border-primary"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                const val = (e.target as HTMLInputElement).value;
                if (val) router.push(`/transit/view?id=${val}`);
              }
            }}
          />
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-surface border border-outline rounded-xl text-sm font-semibold hover:bg-surface-container flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" /> Retour
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-6 space-y-4 animate-pulse">
        <div className="h-8 bg-surface-container rounded w-1/3" />
        <div className="h-4 bg-surface-container rounded w-1/2" />
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-16 bg-surface-container rounded" />
        ))}
      </div>
    );
  }

  if (error || !transit) {
    return (
      <div className="p-6 max-w-xl mx-auto text-center space-y-4">
        <AlertTriangle className="w-14 h-14 text-amber-500 mx-auto" />
        <h2 className="text-xl font-bold text-on-surface">Dossier Introuvable</h2>
        <p className="text-sm text-on-surface-variant">{error || 'Ce dossier de transit n\'existe pas ou vous n\'y avez pas accès.'}</p>
        <button
          onClick={() => router.push('/transit')}
          className="px-4 py-2 bg-primary text-on-primary rounded-xl text-sm font-semibold"
        >
          Retour à la liste
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
      {/* Dynamic Company Document Header */}
      <CompanyDocumentHeader
        documentTitle="Fiche de Déclaration Douanière & Transit"
        documentNumber={transit.numero_dossier || String(transit.id)}
        documentDate={transit.date_arrivee || new Date().toISOString().slice(0, 10)}
        documentReference={transit.numero_dum || transit.reference}
      />

      {/* Action Bar (Hidden on Print) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-4 print:hidden">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-on-surface">
              Dossier Transit #{transit.numero_dossier || transit.id}
            </h1>
            <p className="text-xs text-on-surface-variant">
              {transit.regime || 'Transit CEMAC'} • {transit.bureau_douane || 'Bureau Douane Douala Port'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 px-3 py-2 text-xs font-semibold border border-outline rounded-xl hover:bg-surface-container text-on-surface"
          >
            <Printer className="w-4 h-4" /> Imprimer Titre
          </button>
          <button
            onClick={() => router.push(`/transit/edit?id=${transit.id}`)}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-on-primary rounded-xl hover:opacity-90"
          >
            Modifier le Dossier
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Infos Générales */}
        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2">Informations Générales</h2>
          <div className="space-y-2 text-xs">
            {[
              { label: 'N° DUM', value: transit.numero_dum || transit.reference || 'Non enregistré' },
              { label: 'Régime Douanier', value: transit.regime || 'Transit ordinaire' },
              { label: 'Bureau de Douane', value: transit.bureau_douane || 'PAD Douala' },
              { label: 'Navire / Escale', value: transit.navire || 'Non renseigné' },
              { label: 'Port de Chargement', value: transit.port_chargement || 'Non renseigné' },
              { label: 'Date Arrivée', value: transit.date_arrivee || 'Non renseignée' },
            ].map(row => (
              <div key={row.label} className="flex justify-between py-1 border-b border-outline/30">
                <span className="text-on-surface-variant">{row.label} :</span>
                <span className="font-medium text-on-surface">{row.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Marchandises */}
        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2">Marchandises & Conteneurs</h2>
          <div className="space-y-2 text-xs">
            {[
              { label: 'Désignation Marchandise', value: transit.designation || 'Non spécifiée' },
              { label: 'Poids Brut (kg)', value: transit.poids_brut ? `${transit.poids_brut} kg` : 'Non renseigné' },
              { label: 'Nombre de Conteneurs', value: transit.nb_conteneurs || '0' },
              { label: 'Position SH / NDP', value: transit.position_sh || 'Non renseignée' },
              { label: 'Valeur FOB (FCFA)', value: transit.valeur_fob ? `${Number(transit.valeur_fob).toLocaleString('fr-FR')} FCFA` : 'Non renseignée' },
              { label: 'Droits et Taxes', value: transit.droits_taxes ? `${Number(transit.droits_taxes).toLocaleString('fr-FR')} FCFA` : '0 FCFA' },
            ].map(row => (
              <div key={row.label} className="flex justify-between py-1 border-b border-outline/30">
                <span className="text-on-surface-variant">{row.label} :</span>
                <span className="font-medium text-on-surface">{row.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Statut */}
        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-3 md:col-span-2">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2">État d'Avancement du Dossier</h2>
          <div className="flex flex-wrap gap-3">
            {['DUM Déposée', 'Vérification Documentaire', 'Liquidation', 'BAE Délivré', 'Enlèvement Quai', 'Livraison Finale'].map((step, i) => {
              const done = i <= 2;
              return (
                <div key={step} className={`flex items-center gap-2 px-3 py-2 rounded-xl border text-xs font-semibold ${
                  done ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-600' : 'bg-surface-container border-outline text-on-surface-variant'
                }`}>
                  {done ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Clock className="w-3.5 h-3.5" />}
                  {step}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Standardized Legal Footer */}
      <CompanyDocumentFooter />
    </div>
  );
}
