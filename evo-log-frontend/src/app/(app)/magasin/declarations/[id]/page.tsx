'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { FileText, Search, Plus, Calendar, Edit, Ship, Truck, Loader2, Package, AlertTriangle, Check, Clock, Trash2 } from 'lucide-react'
import { CardSkeletonLoader } from '@/components/ui/Loaders'
import { magasinAPI } from '@/lib/api-client'
import { toast } from 'sonner'
import Link from 'next/link'

export default function DeclarationDetailPage({ params }: { params: { id: string } }) {
  const declarationId = parseInt(params.id)

  const { data: declaration, isLoading: loading } = useQuery({
    queryKey: ['declaration', declarationId],
    queryFn: async () => {
      const res = await magasinAPI.getDeclaration(declarationId)
      return res.data || null
    }
  })

  const { data: receptionTiming, isLoading: timingLoading } = useQuery({
    queryKey: ['receptionTiming', declarationId],
    queryFn: async () => {
      try {
        const res = await magasinAPI.getReceptionTimingPrediction(declarationId)
        return res.data || null
      } catch (e) {
        return null
      }
    },
    enabled: !!declarationId
  })

  if (loading || !declaration) {
    return (
      <ModuleLayout module="magasin">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <CardSkeletonLoader className="h-96 w-full mx-auto" />
          </div>
        </div>
      </ModuleLayout>
    )
  }

  // Helper to format date
  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return 'Non définie'
    return new Date(dateString).toLocaleDateString()
  }

  // Helper to format datetime
  const formatDateTime = (dateString: string | null | undefined) => {
    if (!dateString) return 'Non disponible'
    return new Date(dateString).toLocaleString()
  }

  return (
    <ModuleLayout module="magasin">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500">

        {/* Header */}
        <div className="flex justify-between items-end mb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
              <FileText className="w-5 h-5 text-blue-600" />
              Déclaration #{declaration.id}
            </h1>
            <p className="text-sm text-slate-500 mt-1">BL: {declaration.numero_bl}</p>
          </div>
          <div className="flex gap-2">
            <Link href="/magasin/declarations" className="px-4 py-2 rounded-xl text-sm font-semibold bg-slate-100 hover:bg-slate-200">
              Retour à la liste
            </Link>
          </div>
        </div>

        {/* Status Badge (if applicable) */}
        {declaration.statut && (
          <div className="mb-6 inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700">
            {declaration.statut}
          </div>
        )}

        {/* Informations Générales */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Ship className="w-5 h-5 text-blue-600" />
            Informations Générales
          </h2>
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-bold text-slate-900 mb-3">Identification</h3>
                <p className="text-sm text-slate-500"><strong>Numéro BL Interne:</strong> {declaration.numero_bl}</p>
                <p className="text-sm text-slate-500"><strong>Numéro BL Externe:</strong> {declaration.numero_bl_externe || 'Non spécifié'}</p>
                <p className="text-sm text-slate-500"><strong>Référence Booking:</strong> {declaration.reference_booking || 'Non spécifié'}</p>
                <p className="text-sm text-slate-500"><strong>Numéro de Scellé:</strong> {declaration.numero_scelle || 'Non spécifié'}</p>
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900 mb-3">Parties</h3>
                <p className="text-sm text-slate-500"><strong>Client:</strong> {declaration.client?.nom} {declaration.client?.prenom}</p>
                <p className="text-sm text-slate-500"><strong>Raison Sociale:</strong> {declaration.client?.raison_sociale || 'Non spécifié'}</p>
                <p className="text-sm text-slate-500"><strong>Expéditeur:</strong> {declaration.expediteur_shipper || 'Non spécifié'}</p>
                <p className="text-sm text-slate-500"><strong>Destinataire:</strong> {declaration.destinataire_consignee || 'Non spécifié'}</p>
                <p className="text-sm text-slate-500"><strong>Notify Party:</strong> {declaration.notify_party || 'Non spécifié'}</p>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-200">
              <h3 className="text-lg font-bold text-slate-900 mb-3">Navire & Ports</h3>
              <p className="text-sm text-slate-500"><strong>Nom du Navire:</strong> {declaration.nom_navire || 'Non spécifié'}</p>
              <p className="text-sm text-slate-500"><strong>Numéro de Voyage:</strong> {declaration.numero_voyage || 'Non spécifié'}</p>
              <p className="text-sm text-slate-500"><strong>Port de Chargement:</strong> {declaration.port_chargement || 'Non spécifié'}</p>
              <p className="text-sm text-slate-500"><strong>Port de Déchargement:</strong> {declaration.port_dechargement || 'Non spécifié'}</p>
              <p className="text-sm text-slate-500"><strong>Lieu de Livraison Finale:</strong> {declaration.lieu_livraison || 'Non spécifié'}</p>
            </div>
          </div>
        </div>

        {/* Marchandise Déclarée */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Package className="w-5 h-5 text-blue-600" />
            Marchandise Déclarée
          </h2>
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div className="mb-4">
              <p className="text-sm font-medium text-slate-700"><strong>Code Article:</strong> <span className="font-mono text-blue-600">{declaration.code_article}</span></p>
              {declaration.lignes && declaration.lignes[0] && (
                <>
                  <p className="text-sm font-medium text-slate-700 mb-1"><strong>Désignation:</strong> {declaration.lignes[0].article?.nom}</p>
                  <p className="text-sm font-medium text-slate-700"><strong>Quantité Déclarée:</strong> {parseFloat(declaration.lignes[0].quantite_declaree)} {declaration.lignes[0].unite_mesure}</p>
                  <p className="text-sm font-medium text-slate-700"><strong>Poids Brut:</strong> {declaration.poids_brut_kg?.toFixed(2) || 'Non spécifié'} kg</p>
                  <p className="text-sm font-medium text-slate-700"><strong>Poids Net:</strong> {declaration.poids_net_kg?.toFixed(2) || 'Non spécifié'} kg</p>
                  <p className="text-sm font-medium text-slate-700"><strong>Volume:</strong> {declaration.volume_m3?.toFixed(2) || 'Non spécifié'} m³</p>
                  <p className="text-sm font-medium text-slate-700"><strong>Nombre de Colis:</strong> {declaration.nombre_colis || 'Non spécifié'}</p>
                </>
              )}
            </div>
            {declaration.description_marchandises && (
              <div className="mt-4">
                <p className="text-sm font-medium text-slate-700 mb-1">Description Détaillée</p>
                <p className="text-sm text-slate-500">{declaration.description_marchandises}</p>
              </div>
            )}
          </div>
        </div>

        {/* Réceptions Associées */}
        {declaration.receptions && declaration.receptions.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Truck className="w-5 h-5 text-blue-600" />
              Réceptions Associées
            </h2>
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Numéro Réception</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Magasin Destinataire</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Date Réception</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Statut</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Quantité Réçue</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-slate-100">
                    {declaration.receptions.map((rec: any) => (
                      <tr key={rec.id} className="hover:bg-slate-50">
                        <td className="px-6 py-4">{rec.numero_reception}</td>
                        <td className="px-6 py-4">{rec.magasin_destination?.nom || 'Non spécifié'}</td>
                        <td className="px-6 py-4">{formatDate(rec.date_reception)}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                            rec.statut === 'VALIDEE' ? 'bg-emerald-100 text-emerald-700' :
                            rec.statut === 'EN_COURS' ? 'bg-blue-100 text-blue-700' :
                            rec.statut === 'ANNULEE' ? 'bg-red-100 text-red-700' :
                            'bg-amber-100 text-amber-700'
                          }`}>
                            {rec.statut}
                          </span>
                        </td>
                        <td className="px-6 py-4">{parseFloat(rec.quantite_recue)} {rec.unite_mesure}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Prédiction de Timing de Réception */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-600" />
            Prédiction de Timing de Réception
          </h2>
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            {timingLoading ? (
              <div className="text-center py-8">
                <CardSkeletonLoader className="w-24 h-24 mx-auto" />
                <p className="mt-2 text-sm text-slate-500">Calcul de la prédiction...</p>
              </div>
            ) : receptionTiming ? (
              <>
                <div className="mb-4">
                  <p className="text-sm font-medium text-slate-700"><strong>Date Estimée de Réception Complète:</strong></p>
                  <p className="text-lg font-bold text-slate-900">
                    {formatDate(receptionTiming.estimated_completion_date)}
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-slate-700"><strong>Basé sur l'historique:</strong></p>
                    <p className="text-sm text-slate-500">
                      {receptionTiming.based_on_history ? 'Oui' : 'Non (utilisation de la valeur par défaut de 7 jours)'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-700"><strong>Durée moyenne historique:</strong></p>
                    <p className="text-sm text-slate-500">
                      {receptionTiming.average_duration_days?.toFixed(1)} jours
                    </p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-sm font-medium text-slate-700"><strong>Taille de l'échantillon:</strong></p>
                    <p className="text-sm text-slate-500">
                      {receptionTiming.sample_size} déclarations historiques
                    </p>
                  </div>
                </div>
                {(!receptionTiming.based_on_history || receptionTiming.sample_size === 0) && (
                  <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                    <p className="text-sm text-yellow-800">
                      <AlertTriangle className="w-4 h-4 mr-1" /> Aucune donnée historique disponible pour cette déclaration. La prédiction utilise une estimation par défaut de 7 jours.
                    </p>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-sm text-slate-500">
                  Aucune donnée de prédiction disponible. Aucune réception historisée pour cette déclaration.
                </p>
              </div>
            )}
          </div>
        </div>

      </div>
    </ModuleLayout>
  )
}