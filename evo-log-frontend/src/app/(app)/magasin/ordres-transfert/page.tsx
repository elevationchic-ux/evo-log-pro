'use client'

import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { ArrowRightLeft, Search, Plus, Calendar, Edit, FileText, CheckCircle2, Truck, Box, Link as LinkIcon } from 'lucide-react'
import { CardSkeletonLoader } from '@/components/ui/Loaders'
import { magasinAPI } from '@/lib/api-client'
import { toast } from 'sonner'
import Link from 'next/link'

export default function OrdresTransfertPage() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [showModal, setShowModal] = useState(false)

  const { data: ordres = [], isLoading: loading } = useQuery({
    queryKey: ['ordres_transfert'],
    queryFn: async () => {
      const res = await magasinAPI.getOrdresTransfert()
      const d = res.data
      return Array.isArray(d) ? d : (d?.items ?? [])
    }
  })

  // Referentiel reels pour resoudre les noms de magasins (donnees reelles, jamais inventees)
  const { data: magasins = [] } = useQuery({
    queryKey: ['magasins_lookup'],
    queryFn: async () => {
      const res = await magasinAPI.getMagasins()
      const d = res.data
      return Array.isArray(d) ? d : (d?.items ?? [])
    }
  })
  const magasinNom = (id: number | null | undefined) =>
    magasins.find((m: any) => m.id === id)?.nom || ''

  const actionMutation = useMutation({
    mutationFn: async ({ otId, action }: { otId: number, action: 'valider' | 'expedier' | 'receptionner' | 'annuler' }) => {
      if (action === 'valider') return magasinAPI.validerOrdreTransfert(otId);
      if (action === 'expedier') return magasinAPI.expedierOrdreTransfert(otId);
      if (action === 'receptionner') return magasinAPI.receptionnerOrdreTransfert(otId);
      if (action === 'annuler') return magasinAPI.annulerOrdreTransfert(otId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ordres_transfert'] })
    },
    onError: (error: any) => {
      toast.error(`Erreur: ${error.response?.data?.detail || "Erreur de connexion"}`)
    }
  })

  const handleAction = (otId: number, action: 'valider' | 'expedier' | 'receptionner' | 'annuler') => {
    if (confirm(`Voulez-vous vraiment ${action} cet ordre de transfert ?`)) {
      actionMutation.mutate({ otId, action })
    }
  }

  const filteredOrdres = ordres.filter((o: any) =>
    o.reference?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    magasinNom(o.entrepot_source_id)?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    magasinNom(o.entrepot_dest_id)?.toLowerCase().includes(searchQuery.toLowerCase())
  ).sort((a: any, b: any) => b.id - a.id)

  const getStatusBadge = (status: string) => {
    const styles = {
      brouillon: 'bg-slate-900 text-slate-300',
      valide: 'bg-blue-500/15 text-blue-300',
      paye: 'bg-amber-500/15 text-amber-300',
      expedie: 'bg-purple-500/15 text-purple-300',
      receptionne: 'bg-emerald-500/15 text-emerald-300',
      annule: 'bg-red-500/15 text-red-300'
    } as any
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
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-200 flex items-center gap-3">
              <ArrowRightLeft className="w-8 h-8 text-blue-600" />
              Ordres de Transfert (OT)
            </h1>
            <p className="text-sm text-slate-500 mt-2">Gérez les transferts de marchandises entre vos différents magasins.</p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 shadow-sm transition-all"
          >
            <Plus className="w-5 h-5" />
            Nouvel OT
          </button>
        </div>

        {/* Search */}
        <div className="bg-slate-900 p-4 rounded-2xl shadow-sm border border-slate-700 mb-6 flex flex-col sm:flex-row gap-4 justify-between items-center">
          <div className="relative w-full sm:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Rechercher (Numéro OT, Magasin)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-600 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm outline-none bg-slate-800"
            />
          </div>
        </div>

        {/* Table */}
        <div className="bg-slate-900 rounded-2xl shadow-sm border border-slate-700 overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-800/80 border-b border-slate-700 text-xs uppercase font-bold text-slate-500">
              <tr>
                <th className="px-6 py-4">Numéro OT</th>
                <th className="px-6 py-4">Trajet (Source → Dest)</th>
                <th className="px-6 py-4">Marchandises</th>
                <th className="px-6 py-4">Statut</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr><td colSpan={5} className="px-6 py-12"><CardSkeletonLoader /></td></tr>
              ) : filteredOrdres.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-16 text-center text-slate-500 font-medium">
                    Aucun ordre de transfert trouvé.
                  </td>
                </tr>
              ) : filteredOrdres.map((ot: any) => (
                <tr key={ot.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4">
                    <Link href={`/magasin/ordres-transfert/${ot.id}`}>
                      <div className="font-mono font-black text-blue-600">{ot.reference}</div>
                    </Link>
                    <div className="text-xs text-slate-500 flex items-center gap-1 mt-1 font-bold">
                      <Calendar className="w-3.5 h-3.5" />
                      {ot.date_transfert ? new Date(ot.date_transfert).toLocaleDateString() : ''}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="bg-slate-900 px-3 py-1.5 rounded-lg text-sm font-bold text-slate-300">
                        {magasinNom(ot.entrepot_source_id)}
                      </div>
                      <ArrowRightLeft className="w-4 h-4 text-slate-400" />
                      <div className="bg-blue-500/10 px-3 py-1.5 rounded-lg text-sm font-bold text-blue-300">
                        {magasinNom(ot.entrepot_dest_id)}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-bold text-slate-200">
                      {ot.quantite != null ? `${Number(ot.quantite)} unité(s)` : ''}
                    </div>
                    {ot.motif && (
                      <div className="text-xs text-slate-500 mt-1">{ot.motif}</div>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    {getStatusBadge(ot.statut)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex justify-end gap-2">
                      <Link href={`/magasin/ordres-transfert/${ot.id}`} className="p-2 text-blue-600 hover:bg-blue-500/10 rounded-lg transition-colors" title="Voir les détails">
                        <FileText className="w-4 h-4" />
                      </Link>
                      {ot.statut === 'brouillon' && (
                        <button onClick={() => handleAction(ot.id, 'valider')} className="p-2 text-blue-600 hover:bg-blue-500/10 rounded-lg transition-colors" title="Valider (Déstocker source)">
                          <CheckCircle2 className="w-5 h-5" />
                        </button>
                      )}
                      {ot.statut === 'valide' && (
                        <button onClick={() => handleAction(ot.id, 'expedier')} className="p-2 text-purple-600 hover:bg-purple-500/10 rounded-lg transition-colors" title="Expédier (En transit)">
                          <Truck className="w-5 h-5" />
                        </button>
                      )}
                      {(ot.statut === 'valide' || ot.statut === 'expedie' || ot.statut === 'paye') && (
                        <button onClick={() => handleAction(ot.id, 'receptionner')} className="p-2 text-emerald-600 hover:bg-emerald-500/10 rounded-lg transition-colors" title="Réceptionner (Stocker destination)">
                          <Box className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Modal Form */}
        {showModal && (
          <OTModal
            onClose={() => setShowModal(false)}
            onSuccess={() => { setShowModal(false); queryClient.invalidateQueries({ queryKey: ['ordres_transfert'] }); }}
          />
        )}
      </div>
    </ModuleLayout>
  )
}

function OTModal({ onClose, onSuccess }: { onClose: () => void, onSuccess: () => void }) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    magasin_source_id: '',
    magasin_dest_id: '',
    motif: '',
    code_article: '',
    quantite: ''
  })

  const [magasins, setMagasins] = useState<any[]>([])
  const [articleInfo, setArticleInfo] = useState<any>(null)

  useEffect(() => {
    // Referentiel magasins reel (endpoint /magasin/magasins)
    magasinAPI.getMagasins()
      .then(res => {
        const d = res.data
        setMagasins(Array.isArray(d) ? d : (d?.items ?? []))
      })
      .catch(console.error)
  }, [])

  useEffect(() => {
    if (formData.code_article.length === 7) {
      magasinAPI.getArticleByCode(formData.code_article)
        .then(res => setArticleInfo(res.data))
        .catch(() => setArticleInfo(null))
    } else {
      setArticleInfo(null)
    }
  }, [formData.code_article])

  const mutation = useMutation({
    mutationFn: (data: any) => magasinAPI.createOrdreTransfert(data),
    onSuccess: () => {
      toast.success('Ordre de transfert créé avec succès')
      queryClient.invalidateQueries({ queryKey: ['ordres_transfert'] })
      onSuccess()
    },
    onError: (err: any) => {
      toast.error(`Erreur: ${err.response?.data?.detail || "Erreur inconnue"}`)
    }
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!articleInfo) {
      toast.error("Code article invalide.");
      return
    }

    if (formData.magasin_source_id === formData.magasin_dest_id) {
      toast.error("Le magasin source et destination doivent être différents.");
      return
    }

    // Contrat reel de l'API: OrdreTransfertCreate (un article par transfert)
    const payload = {
      entrepot_source_id: parseInt(formData.magasin_source_id),
      entrepot_dest_id: parseInt(formData.magasin_dest_id),
      article_id: articleInfo.id,
      quantite: parseFloat(formData.quantite),
      motif: formData.motif || null
    }

    mutation.mutate(payload)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden animate-in zoom-in-95 duration-200 my-8">
        <div className="px-6 py-4 border-b border-slate-700 flex justify-between items-center bg-slate-800">
          <h2 className="text-xl font-bold text-slate-200 flex items-center gap-2">
            <ArrowRightLeft className="w-5 h-5 text-blue-600" />
            Nouvel Ordre de Transfert
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-400"><span className="material-symbols-outlined">close</span></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-6">

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-bold text-slate-300 mb-1">Magasin Source *</label>
              <select
                required
                value={formData.magasin_source_id}
                onChange={e => setFormData({ ...formData, magasin_source_id: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none bg-slate-800"
              >
                <option value="">Sélectionner...</option>
                {magasins.map(m => (
                  <option key={m.id} value={m.id}>{m.nom}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-300 mb-1">Magasin Destination *</label>
              <select
                required
                value={formData.magasin_dest_id}
                onChange={e => setFormData({ ...formData, magasin_dest_id: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none bg-slate-800 text-slate-200"
              >
                <option value="">Sélectionner...</option>
                {magasins.map(m => (
                  <option key={m.id} value={m.id}>{m.nom}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="bg-slate-800 p-5 rounded-2xl border border-slate-700 space-y-4">
            <h3 className="font-bold text-slate-200">Article à transférer</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-bold text-slate-300 mb-1">Code Article (7 chiffres) *</label>
                <input
                  type="text"
                  required
                  pattern="\d{7}"
                  maxLength={7}
                  value={formData.code_article}
                  onChange={e => setFormData({ ...formData, code_article: e.target.value.replace(/\D/g, '') })}
                  placeholder="Ex: 1111110"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-600 outline-none font-mono text-sm bg-slate-900"
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-slate-300 mb-1">Quantité *</label>
                <div className="flex gap-2">
                  <input
                    type="number" step="0.001" required disabled={!articleInfo}
                    value={formData.quantite}
                    onChange={e => setFormData({ ...formData, quantite: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-600 outline-none disabled:bg-slate-900 text-sm font-bold"
                  />
                  {articleInfo && (
                    <div className="flex items-center px-3 bg-slate-700 text-slate-300 font-bold rounded-xl text-xs">
                      {articleInfo.unite_mesure}
                    </div>
                  )}
                </div>
              </div>
              <div className="col-span-2">
                <div className="bg-slate-900 p-2 rounded-lg border border-slate-700 text-sm flex items-center">
                  {articleInfo ? (
                    <span><span className="font-bold text-emerald-600 mr-2">Produit reconnu:</span> {articleInfo.designation}</span>
                  ) : (
                    <span className="text-slate-400 italic">Le produit s'affichera ici automatiquement...</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-300 mb-1">Motif du transfert</label>
            <input
              type="text"
              value={formData.motif}
              onChange={e => setFormData({ ...formData, motif: e.target.value })}
              placeholder="Ex: Rééquilibrage stock, Demande client..."
              className="w-full px-4 py-2 rounded-xl border border-slate-600 outline-none text-sm"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
            <button type="button" onClick={onClose} className="px-5 py-2.5 rounded-xl text-sm font-bold text-slate-400 hover:bg-slate-800 transition-colors">Annuler</button>
            <button
              type="submit"
              disabled={!articleInfo}
              className="px-5 py-2.5 rounded-xl text-sm font-bold bg-blue-600 hover:bg-blue-700 text-white transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Créer l'OT (Brouillon)
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}