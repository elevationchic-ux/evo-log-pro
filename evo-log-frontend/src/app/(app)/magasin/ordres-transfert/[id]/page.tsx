'use client'

import { useState, useEffect } from 'react'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { ArrowRightLeft, Calendar, FileText, CheckCircle2, Megaphone, Package } from 'lucide-react'
import { CardSkeletonLoader } from '@/components/ui/Loaders'
import { magasinAPI, authAPI, apiClient } from '@/lib/api-client'
import { toast } from 'sonner'
import Link from 'next/link'

export default function OrdreTransfertDetailPage({ params }: { params: { id: string } }) {
  const otId = parseInt(params.id)
  const [ot, setOt] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [userName, setUserName] = useState<string>('')
  const [bandeAssociee, setBandeAssociee] = useState<any>(null)
  const [magasins, setMagasins] = useState<any[]>([])
  const [article, setArticle] = useState<any>(null)

  useEffect(() => {
    fetchOt()
    fetchUserName()
    // Referentiel magasins reel (resolucodes noms)
    magasinAPI.getMagasins()
      .then(res => {
        const d = res.data
        setMagasins(Array.isArray(d) ? d : (d?.items ?? []))
      })
      .catch(console.error)
  }, [])

  const magasinNom = (id: number | null | undefined) =>
    magasins.find((m: any) => m.id === id)?.nom || 'Non spécifié'

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

  // Resoudre l'article reellement rattache a cet OT
  useEffect(() => {
    if (ot?.article_id) {
      apiClient.get(`/api/magasin/articles/${ot.article_id}`)
        .then((res: any) => setArticle(res.data || null))
        .catch(() => setArticle(null))
    } else {
      setArticle(null)
    }
  }, [ot])

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
    try {
      const res = await magasinAPI.getBandeByOrdreTransfert(otId)
      // L'API reelle renvoie la liste des bandes derivees de cet OT
      const list = Array.isArray(res.data) ? res.data : (res.data ? [res.data] : [])
      setBandeAssociee(list[0] ?? null)
    } catch (error) {
      setBandeAssociee(null)
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
    } catch (err: any) {
      console.error(err)
      toast.error(`Erreur: ${err.response?.data?.detail || 'Erreur inconnue'}`)
    }
  }

  const handleValiderPaiement = async () => {
    if (!otId) return
    if (!confirm('Êtes-vous sûr de vouloir valider le paiement de cet OT ?')) return
    try {
      await magasinAPI.validerPaiementOT(otId)
      toast.success('Paiement validé')
      fetchOt() // Rafraichir le statut reel
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

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      brouillon: 'bg-slate-900 text-slate-300',
      valide: 'bg-blue-500/15 text-blue-300',
      paye: 'bg-amber-500/15 text-amber-300',
      expedie: 'bg-purple-500/15 text-purple-300',
      receptionne: 'bg-emerald-500/15 text-emerald-300',
      annule: 'bg-red-500/15 text-red-300'
    }
    return (
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${styles[status] || 'bg-slate-900 text-slate-300'}`}>
        {(status || '').toUpperCase()}
      </span>
    )
  }

  return (
    <ModuleLayout module="magasin">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-end gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-200 flex items-center gap-3">
              <ArrowRightLeft className="w-6 h-6 text-blue-600" />
              Ordre de Transfert #{ot.id}
            </h1>
            <p className="text-sm text-slate-500 mt-1">Référence: {ot.reference}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {ot.statut === 'valide' && (
              <button
                onClick={handleValiderPaiement}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all"
              >
                <CheckCircle2 className="w-4 h-4" />
                Valider le paiement
              </button>
            )}
            {['valide', 'paye', 'expedie'].includes(ot.statut) && !bandeAssociee && (
              <button
                onClick={handleGenerateBande}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all"
              >
                <Megaphone className="w-4 h-4" />
                Générer la Bande de Livraison
              </button>
            )}
            {bandeAssociee && (
              <Link href={`/magasin/bandes-livraison/${bandeAssociee.id}`} className="px-4 py-2 rounded-xl text-sm font-semibold bg-slate-900 hover:bg-slate-700 flex items-center gap-2">
                <Package className="w-4 h-4" />
                Voir la Bande de Livraison associée
              </Link>
            )}
            <Link href="/magasin/ordres-transfert" className="px-4 py-2 rounded-xl text-sm font-semibold bg-slate-900 hover:bg-slate-700">
              Retour à la liste
            </Link>
          </div>
        </div>

        {/* Status Badge */}
        <div className="mb-6">
          {getStatusBadge(ot.statut)}
        </div>

        {/* Main Info */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-slate-200 mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            Informations Générales
          </h2>
          <div className="bg-slate-900 rounded-2xl shadow-sm border border-slate-700 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-bold text-slate-200 mb-3">Trajet</h3>
                <p className="text-sm text-slate-500"><strong>Source:</strong> {magasinNom(ot.entrepot_source_id)}</p>
                <p className="text-sm text-slate-500"><strong>Destination:</strong> {magasinNom(ot.entrepot_dest_id)}</p>
                <p className="text-sm text-slate-500"><strong>Date de transfert:</strong> {ot.date_transfert ? new Date(ot.date_transfert).toLocaleDateString() : 'Non définie'}</p>
                {ot.motif && (
                  <p className="text-sm text-slate-500"><strong>Motif:</strong> {ot.motif}</p>
                )}
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-200 mb-3">Références & Dates</h3>
                <p className="text-sm text-slate-500"><strong>Référence:</strong> {ot.reference}</p>
                <p className="text-sm text-slate-500"><strong>Date de création:</strong> {ot.created_at ? new Date(ot.created_at).toLocaleString() : 'Non disponible'}</p>
                {ot.montant_paiement != null && (
                  <p className="text-sm text-slate-500"><strong>Montant paiement:</strong> {Number(ot.montant_paiement).toLocaleString()} FCFA</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Article */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-slate-200 mb-4 flex items-center gap-2">
            <Package className="w-5 h-5 text-blue-600" />
            Article transféré
          </h2>
          <div className="bg-slate-900 rounded-2xl shadow-sm border border-slate-700 p-6">
            {article ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-800">
                  <thead className="bg-slate-800">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Code Article</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Désignation</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Quantité</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500">Unité</th>
                    </tr>
                  </thead>
                  <tbody className="bg-slate-900 divide-y divide-slate-800">
                    <tr className="hover:bg-slate-800">
                      <td className="px-6 py-4 font-mono text-slate-200">{article.code}</td>
                      <td className="px-6 py-4 text-slate-200">{article.designation}</td>
                      <td className="px-6 py-4 text-slate-200">{ot.quantite != null ? Number(ot.quantite) : ''}</td>
                      <td className="px-6 py-4 text-slate-200">{article.unite_mesure || ''}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-slate-500 italic text-center py-8">Aucun article défini pour cet ordre de transfert.</p>
            )}
          </div>
        </div>

        {/* Lifecycle */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-slate-200 mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-600" />
            Cycle de vie
          </h2>
          <div className="bg-slate-900 rounded-2xl shadow-sm border border-slate-700 p-6">
            <ol className="space-y-2 text-sm">
              <li className="flex justify-between items-center">
                <span className="text-slate-300">Création (brouillon)</span>
                <span className="text-slate-500">{ot.created_at ? new Date(ot.created_at).toLocaleString() : ''}</span>
              </li>
              <li className="flex justify-between items-center">
                <span className="text-slate-300">Statut actuel</span>
                <span>{getStatusBadge(ot.statut)}</span>
              </li>
              {ot.updated_at && (
                <li className="flex justify-between items-center">
                  <span className="text-slate-300">Dernière mise à jour</span>
                  <span className="text-slate-500">{new Date(ot.updated_at).toLocaleString()}</span>
                </li>
              )}
            </ol>
          </div>
        </div>

      </div>
    </ModuleLayout>
  )
}
