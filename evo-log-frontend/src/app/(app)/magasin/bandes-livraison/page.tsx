'use client'

import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { FileText, Search, Plus, Calendar, Edit, Ship, Truck, Loader2, HelpCircle as CircleHelp, Package } from 'lucide-react'
import { CardSkeletonLoader } from '@/components/ui/Loaders'
import { magasinAPI } from '@/lib/api-client'
import { toast } from 'sonner'
import Link from 'next/link'

export default function BandeLivraisonPage() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [showModal, setShowModal] = useState(false)

  const { data: bandes = [], isLoading: loading, refetch: fetchBandres } = useQuery({
    queryKey: ['bandes'],
    queryFn: async () => {
      const res = await magasinAPI.getBandes()
      return res.data || []
    }
  })

  const filteredBandres = bandes.filter((b: any) =>
    (b.declaration?.numero_bl || b.ordre_transfert?.reference)?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    b.chauffeur_nom?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    b.matricule_vehicule?.toLowerCase().includes(searchQuery.toLowerCase())
  ).sort((a: any, b: any) => b.id - a.id)

  return (
    <ModuleLayout module="magasin">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500">

        {/* Header */}
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-200 flex items-center gap-3">
              <Truck className="w-8 h-8 text-blue-600" />
              Bandes de Livraison
            </h1>
            <p className="text-sm text-slate-500 mt-2">Suivi des livraisons aux clients ou entre magasins.</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 shadow-sm transition-all"
            >
              <Plus className="w-5 h-5" />
              Nouvelle Bande
            </button>
            <button
              onClick={() => fetchBandres()}
              className="bg-slate-700 hover:bg-slate-300 text-slate-200 px-4 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all"
            >
              <Loader2 className="w-4 h-4" />
              Actualiser
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="bg-slate-900 p-4 rounded-2xl shadow-sm border border-slate-700 mb-6 flex flex-col sm:flex-row gap-4 justify-between items-center">
          <div className="relative w-full sm:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Rechercher (BL, Réf OT, Chauffeur, Véhicule)..."
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
                <th className="px-6 py-4">Référence Source</th>
                <th className="px-6 py-4">Date Livraison</th>
                <th className="px-6 py-4">Chauffeur / Véhicule</th>
                <th className="px-6 py-4">Statut</th>
                <th className="px-6 py-4">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr><td colSpan={5} className="px-6 py-12"><CardSkeletonLoader /></td></tr>
              ) : filteredBandres.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-16 text-center text-slate-500 font-medium">
                    Aucune bande de livraison trouvée.
                  </td>
                </tr>
              ) : filteredBandres.map((bande: any) => {
                const source = bande.declaration ? (
                  <>
                    <Package className="w-4 h-4 text-blue-600 mr-1" />
                    <span className="font-mono">{bande.declaration?.numero_bl}</span>
                  </>
                ) : bande.ordre_transfert ? (
                  <>
                    <Truck className="w-4 h-4 text-green-600 mr-1" />
                    <span className="font-mono">{bande.ordre_transfert?.reference}</span>
                  </>
                ) : (
                  <span className="text-slate-400 italic">Inconnu</span>
                )
                return (
                  <tr key={bande.id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-6 py-4">
                      {source}
                    </td>
                    <td className="px-6 py-4">
                      {bande.date_livraison ? (
                        <span className="text-slate-400">{new Date(bande.date_livraison).toLocaleDateString()}</span>
                      ) : (
                        <span className="text-slate-400 italic">Non définie</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-1">
                        {bande.chauffeur_nom && (
                          <div className="font-medium">
                            <CircleHelp className="w-3 h-3 mr-1" /> {bande.chauffeur_nom}
                          </div>
                        )}
                        {bande.matricule_vehicule && (
                          <div className="text-xs text-slate-500">
                            <Truck className="w-3 h-3 mr-1" /> {bande.matricule_vehicule}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                        bande.statut === 'VALIDEE' ? 'bg-emerald-500/15 text-emerald-300' :
                        bande.statut === 'EN_COURS' ? 'bg-blue-500/15 text-blue-300' :
                        bande.statut === 'ANNULEE' ? 'bg-red-500/15 text-red-300' :
                        'bg-amber-500/15 text-amber-300'
                      }`}>
                        {bande.statut}
                      </span>
                    </td>
                    <td className="px-6 py-4 flex gap-2">
                      <Link href={`/magasin/bandes-livraison/${bande.id}`} className="text-sm font-medium text-blue-600 hover:underline">
                        Voir
                      </Link>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Modal Form */}
        {showModal && (
          <BandeLivraisonModal
            onClose={() => setShowModal(false)}
            onSuccess={() => { setShowModal(false); fetchBandres(); }}
          />
        )}
      </div>
    </ModuleLayout>
  )
}

function BandeLivraisonModal({ onClose, onSuccess }: { onClose: () => void, onSuccess: () => void }) {
  const [activeTab, setActiveTab] = useState<'source' | 'transport'>('source')

  const [formData, setFormData] = useState({
    source_type: '', // 'declaration' or 'ordre_transfert'
    source_id: '',
    chauffeur_nom: '',
    matricule_vehicule: '',
    signature_chauffeur: '',
    signature_magasinier: '',
    signature_transporteur: '',
    date_livraison: '',
  })

  const [clients, setClients] = useState<any[]>([])
  const [declarations, setDeclarations] = useState<any[]>([])
  const [ordresTransfert, setOrdresTransfert] = useState<any[]>([])

  useEffect(() => {
    // Fetch clients for maybe display? Not needed for source selection but we may need for reference
    magasinAPI.getClients()
      .then(res => setClients(res.data || []))
      .catch(console.error)

    magasinAPI.getDeclarations()
      .then(res => setDeclarations(res.data || []))
      .catch(console.error)

    magasinAPI.getOrdresTransfert()
      .then(res => setOrdresTransfert(res.data || []))
      .catch(console.error)
  }, [])

  const mutation = useMutation({
    mutationFn: (data: any) => magasinAPI.createBande(data),
    onSuccess: () => {
      toast.success('Bande de livraison créée avec succès')
      onSuccess()
    },
    onError: (err: any) => {
      toast.error(`Erreur: ${err.response?.data?.detail || "Erreur inconnue"}`)
    }
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate source selection
    if (!formData.source_type || !formData.source_id) {
      toast.error("Veuillez sélectionner une source (Déclaration ou Ordre de Transfert) et son ID.")
      return
    }

    const sourceIdNum = parseInt(formData.source_id)
    if (isNaN(sourceIdNum)) {
      toast.error("ID de source invalide")
      return
    }

    const payload = {
      ...formData,
      [formData.source_type === 'declaration' ? 'commande_id' : 'ordre_transfert_id']: sourceIdNum,
      // Ensure the other foreign key is null
      [formData.source_type === 'declaration' ? 'ordre_transfert_id' : 'commande_id']: null,
      date_livraison: formData.date_livraison ? new Date(formData.date_livraison).toISOString() : null,
    }

    // Clean empty strings
    Object.keys(payload).forEach(key => {
      if (payload[key as keyof typeof payload] === '') {
        (payload as any)[key] = null
      }
    })

    mutation.mutate(payload)
  }

  const InputField = ({ label, field, type = "text", required = false, placeholder = "" }: { label: string, field: keyof typeof formData, type?: string, required?: boolean, placeholder?: string }) => (
    <div>
      <label className="block text-sm font-bold text-slate-300 mb-1">{label} {required && '*'}</label>
      <input
        type={type}
        required={required}
        value={formData[field]}
        onChange={e => setFormData({...formData, [field]: e.target.value})}
        placeholder={placeholder}
        className="w-full px-4 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none text-sm"
      />
    </div>
  )

  const SelectField = ({ label, field, options, required = false }: { label: string, field: keyof typeof formData, options: { value: string; label: string }[], required?: boolean }) => (
    <div>
      <label className="block text-sm font-bold text-slate-300 mb-1">{label} {required && '*'}</label>
      <select
        required={required}
        value={formData[field]}
        onChange={e => setFormData({...formData, [field]: e.target.value})}
        className="w-full px-4 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none text-sm"
      >
        <option value="">Sélectionner une option...</option>
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  )

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden animate-in zoom-in-95 duration-200 my-8">
        <div className="px-6 py-4 border-b border-slate-700 flex justify-between items-center bg-slate-800">
          <h2 className="text-xl font-bold text-slate-200 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            Nouvelle Bande de Livraison
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-400"><span className="material-symbols-outlined">close</span></button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-700 px-6 pt-4 gap-6 bg-slate-800">
          {[
            { id: 'source', label: 'Source' },
            { id: 'transport', label: 'Transport & Livraison' }
          ].map(t => (
            <button
              key={t.id}
              type="button"
              onClick={() => setActiveTab(t.id as any)}
              className={`pb-3 text-sm font-bold border-b-2 transition-colors ${activeTab === t.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-300'}`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">

          {/* TAB 1 : SOURCE */}
          <div className={activeTab === 'source' ? 'block' : 'hidden'}>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-slate-300 mb-1">Type de Source *</label>
                <select
                  required
                  value={formData.source_type}
                  onChange={e => setFormData({...formData, source_type: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none text-sm"
                >
                  <option value="">Sélectionner le type...</option>
                  <option value="declaration">Déclaration Marchandises</option>
                  <option value="ordre_transfert">Ordre de Transfert</option>
                </select>
              </div>

              <div className={formData.source_type === 'declaration' ? 'block' : 'hidden'}>
                <label className="block text-sm font-bold text-slate-300 mb-1">Déclaration *</label>
                <select
                  required
                  value={formData.source_id}
                  onChange={e => setFormData({...formData, source_id: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none text-sm"
                >
                  <option value="">Sélectionner une déclaration...</option>
                  {declarations.map(dec => (
                    <option key={dec.id} value={dec.id}>
                      BL: {dec.numero_bl} - {dec.client?.nom} {dec.client?.prenom}
                    </option>
                  ))}
                </select>
              </div>

              <div className={formData.source_type === 'ordre_transfert' ? 'block' : 'hidden'}>
                <label className="block text-sm font-bold text-slate-300 mb-1">Ordre de Transfert *</label>
                <select
                  required
                  value={formData.source_id}
                  onChange={e => setFormData({...formData, source_id: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none text-sm"
                >
                  <option value="">Sélectionner un ordre de transfert...</option>
                  {ordresTransfert.map(ot => (
                    <option key={ot.id} value={ot.id}>
                      Ref: {ot.reference} - {ot.magasin_destination?.nom} ({ot.statut})
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* TAB 2 : TRANSPORT & LIVRAISON */}
          <div className={activeTab === 'transport' ? 'block' : 'hidden'}>
            <div className="space-y-4">
              <InputField label="Nom du Chauffeur" field="chauffeur_nom" placeholder="Ex: Jean Dupont" />
              <InputField label="Matricule du Véhicule" field="matricule_vehicule" placeholder="Ex: ABC-1234" />
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-slate-300 mb-1">Signature Chauffeur (base64 ou URL)</label>
                  <InputField label="Signature Chauffeur" field="signature_chauffeur" placeholder="Données signature..." />
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-300 mb-1">Signature Magasinier (base64 ou URL)</label>
                  <InputField label="Signature Magasinier" field="signature_magasinier" placeholder="Données signature..." />
                </div>
              </div>
              <InputField label="Signature Transporteur (base64 ou URL)" field="signature_transporteur" placeholder="Données signature..." />
              <div className="mt-4">
                <label className="block text-sm font-bold text-slate-300 mb-1">Date de Livraison prévue</label>
                <input
                  type="date"
                  value={formData.date_livraison}
                  onChange={e => setFormData({...formData, date_livraison: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none text-sm"
                />
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center mt-8 pt-4 border-t border-slate-700">
            <div className="text-xs text-slate-400">
              * Champs obligatoires
            </div>
            <div className="flex gap-3">
              <button type="button" onClick={onClose} className="px-5 py-2.5 rounded-xl text-sm font-bold text-slate-400 hover:bg-slate-800 transition-colors">Annuler</button>
              <button
                type="submit"
                disabled={!formData.source_type || !formData.source_id}
                className="px-5 py-2.5 rounded-xl text-sm font-bold bg-blue-600 hover:bg-blue-700 text-white transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Créer la Bande de Livraison
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}