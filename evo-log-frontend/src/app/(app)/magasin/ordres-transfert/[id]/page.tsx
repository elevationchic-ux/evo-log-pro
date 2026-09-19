'use client'

import { useState, useEffect } from 'react'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { ArrowRightLeft, Search, Plus, Calendar, Edit, FileText, CheckCircle2, Truck, Box, Package, Loader2, Megaphone, AlertTriangle } from 'lucide-react'
import { CardSkeletonLoader } from '@/components/ui/Loaders'
import { magasinAPI, authAPI } from '@/lib/api-client'
import { toast } from 'sonner'
import Link from 'next/link'

export default function OrdreTransfertDetailPage({ params }: { params: { id: string } }) {
  const otId = parseInt(params.id)
  const [ot, setOt] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [userName, setUserName] = useState<string>('')
  const [bandeAssociee, setBandeAssociee] = useState<any>(null)
  const [checkingBande, setCheckingBande] = useState(false)

  useEffect(() => {
    fetchOt()
    fetchUserName()
  }, [])

  const fetchOt = async () => {
    try {
      setLoading(true)
      const res = await magasinAPI.getOrdreTransfert(otId)
      setOt(res.data || null)
    } catch (error) {
      console.error(error)
      toast.error('Erreur lors du chargement de l\'ordre de transfert')
    } finally {
      setLoading(false)
    }
  }

  const fetchUserName = async () => {
    try {
      const res = await authAPI.getMe()
      setUserName(res.data?.nom || 'Utilisateur')
    } catch (error) {
      console.error(error)
      setUserName('Utilisateur')
    }
  }

  const checkAssociatedBande = async () => {
    if (!otId) return
    setCheckingBande(true)
    try {
      const res = await magasinAPI.getBandeByOrdreTransfert(otId)
      setBandeAssociee(res.data || null)
    } catch (error) {
      // 404 means no bande associated
      setBandeAssociee(null)
    } finally {
      setCheckingBande(false)
    }
  }

  useEffect(() => {
    if (ot) {
      checkAssociatedBande()
    }
  }, [ot])

  const handleGenerateBande = async () => {
    if (!otId) return
    if (!userName) {
      toast.error('Impossible de récupérer l\'utilisateur courant')
      return
    }
    try {
      const res = await magasinAPI.createBandeFromOrdreTransfert(otId, userName)
      toast.success('Bande de livraison générée avec succès')
      setBandeAssociee(res.data)
      // Refetch OT to see updated status? Not needed.
    } catch (err: any) {
      console.error(err)
      toast.error(`Erreur: ${err.response?.data?.detail || 'Erreur inconnue'}`)
    }
  }

  const handleValiderPaiement = async () => {
    if (!otId) return
    if (!confirm('Êtes-vous sûr de vouloir valider le paiement et débloquer cet OT ?')) return
    
    try {
      await magasinAPI.validerPaiementOT(otId)
      toast.success('Paiement validé. Génération du Bon d\'Enlèvement en cours...')
      fetchOt() // Refresh to see new status
    } catch (err: any) {
      console.error(err)
      toast.error(`Erreur: ${err.response?.data?.detail || 'Erreur inconnue'}`)
    }
  }

  if (loading || !ot) {
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

  // Helper to get status badge class
  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      BROUILLON: 'bg-slate-100 text-slate-700',
      VALIDE: 'bg-blue-100 text-blue-700',
      EN_TRANSIT: 'bg-purple-100 text-purple-700',
      RECEPTIONNE: 'bg-emerald-100 text-emerald-700',
      ANNULE: 'bg-red-100 text-red-700'
    }
    return (
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${styles[status] || 'bg-slate-100 text-slate-700'}`}>
        {status}
      </span>
    )
  }

  return (
    <ModuleLayout module="magasin">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500">

        {/* Header */}
        <div className="flex justify-between items-end mb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
              <ArrowRightLeft className="w-6 h-6 text-blue-600" />
              Ordre de Transfert #{ot.id}
            </h1>
            <p className="text-sm text-slate-500 mt-1">Numéro: {ot.numero_ot}</p>
          </div>
          <div className="flex gap-2">
            {ot.statut === 'BROUILLON' && (
              <button
                onClick={handleValiderPaiement}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all"
              >
                <CheckCircle2 className="w-4 h-4" />
                Valider Paiement & Débloquer OT
              </button>
            )}
            {ot.statut !== 'BROUILLON' && ot.statut !== 'ANNULE' && (
              <a
                href={`${process.env.NEXT_PUBLIC_API_URL || 'https://backend-production-83b1.up.railway.app'}/documents/ot/${ot.numero_ot}_Bon_Enlevement.pdf`}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-slate-800 hover:bg-slate-900 text-white px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all"
              >
                <FileText className="w-4 h-4" />
                Télécharger Bon d'Enlèvement PDF
              </a>
            )}
            {ot.statut === 'VALIDE' && !bandeAssociee && (
              <button
                onClick={handleGenerateBande}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all"
              >
                <Megaphone className="w-4 h-4" />
                Générer la Bande de Livraison
              </button>
            )}
            {bandeAssociee && (
              <Link href={`/magasin/bandes-livraison/${bandeAssociee.id}`} className="px-4 py-2 rounded-xl text-sm font-semibold bg-slate-100 hover:bg-slate-200 flex items-center gap-2">
                <Package className="w-4 h-4" />
                Voir la Bande de Livraison associée
              </Link>
            )}
            <Link href="/magasin/ordres-transfert" className="px-4 py-2 rounded-xl text-sm font-semibold bg-slate-100 hover:bg-slate-200">
              Retour à la liste
            </Link>
          </div>
        </div>

        {/* Status Badge */}
        <div className="mb-6 inline-flex items-center px-3 py-1 rounded-full text-xs font-bold {getStatusBadge(ot.statut).replace('span', '').trim()}">
          {ot.statut}
        </div>

        {/* Main Info */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            Informations Générales
          </h2>
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-bold text-slate-900 mb-3">Trajet</h3>
                <p className="text-sm text-slate-500"><strong>Source:</strong> {ot.magasin_source?.nom || 'Non spécifié'}</p>
                <p className="text-sm text-slate-500"><strong>Destination:</strong> {ot.magasin_destination?.nom || 'Non spécifié'}</p>
                <p className="text-sm text-slate-500"><strong>Date prévue de transfert:</strong> {ot.date_transfert ? new Date(ot.date_transfert).toLocaleDateString() : 'Non définie'}</p>
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900 mb-3">Références & Dates</h3>
                <p className="text-sm text-slate-500"><strong>Numéro OT:</strong> {ot.numero_ot}</p>
                <p className="text-sm text-slate-500"><strong>Date de création:</strong> {ot.created_at ? new Date(ot.created_at).toLocaleString() : 'Non disponible'}</p>
                {ot.date_validation && (
                  <p className="text-sm text-slate-500"><strong>Date de validation:</strong> {new Date(ot.date_validation).toLocaleString()}</p>
                )}
                {ot.date_expedition && (
                  <p className="text-sm text-slate-500"><strong>Date d'expédition:</strong> {new Date(ot.date_expedition).toLocaleString()}</p>
                )}
                {ot.date_reception && (
                  <p className="text-sm text-slate-500"><strong>Date de réception:</strong> {new Date(ot.date_reception).toLocaleString()}</p>
                )}
              </div>
            </div>

            {ot.declaration && (
              <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-200">
                <h3 className="text-lg font-bold text-slate-900 mb-3">Déclaration Marchandises Associée</h3>
                <p className="text-sm text-slate-500"><strong>BL:</strong> {ot.declaration?.numero_bl}</p>
                <p className="text-sm text-slate-500"><strong>Client:</strong> {ot.declaration?.client?.nom} {ot.declaration?.client?.prenom}</p>
                <Link
                  href={`/magasin/declarations/${ot.declaration?.id}`}
                  className="mt-2 inline-flex items-center text-sm text-blue-600 hover:underline"
                >
                  Voir la déclaration
                  <ArrowRightLeft className="ml-2 h-4 w-4" />
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Articles */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Box className="w-5 h-5 text-blue-600" />
            Articles à Transférer
          </h2>
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            {ot.lignes && ot.lignes.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Code Article</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Désignation</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Quantité</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Unité</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-slate-100">
                    {ot.lignes.map((ligne: any) => (
                      <tr key={ligne.id} className="hover:bg-slate-50">
                        <td className="px-6 py-4 text-font-mono">{ligne.article?.code}</td>
                        <td className="px-6 py-4">{ligne.article?.nom}</td>
                        <td className="px-6 py-4">{parseFloat(ligne.quantite)}</td>
                        <td className="px-6 py-4">{ligne.article?.unite_mesure}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-slate-500 italic text-center py-8">Aucun article défini pour cet ordre de transfert.</p>
            )}
          </div>
        </div>

        {/* Actions History (optional) */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-600" />
            Historique des Actions
          </h2>
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div className="space-y-3">
              {ot.date_validation && (
                <div className="flex justify-between items-center text-sm">
                  <span>Validation</span>
                  <span className="text-slate-500">{new Date(ot.date_validation).toLocaleString()}</span>
                </div>
              )}
              {ot.date_expedition && (
                <div className="flex justify-between items-center text-sm">
                  <span>Expédition</span>
                  <span className="text-slate-500">{new Date(ot.date_expedition).toLocaleString()}</span>
                </div>
              )}
              {ot.date_reception && (
                <div className="flex justify-between items-center text-sm">
                  <span>Réception</span>
                  <span className="text-slate-500">{new Date(ot.date_reception).toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>
        </div>

      </div>
    </ModuleLayout>
  )
}