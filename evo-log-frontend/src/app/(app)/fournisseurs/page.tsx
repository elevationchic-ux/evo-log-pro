'use client'

import React, { useState, useEffect } from 'react'
import { 
  Building2, 
  Plus, 
  Search, 
  Edit2, 
  Trash2, 
  Phone, 
  Mail, 
  MapPin,
  Loader2,
  Filter,
  Download
} from 'lucide-react'
import api from '@/lib/api'
import { toast } from 'sonner'

interface Fournisseur {
  id: number
  code: string
  nom: string
  email: string
  telephone: string
  adresse: string
  ville: string
  pays: string
  type: string
  status: 'active' | 'inactive'
  created_at: string
}

export default function FournisseursPage() {
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [showModal, setShowModal] = useState(false)
  const [editingFournisseur, setEditingFournisseur] = useState<Fournisseur | null>(null)

  useEffect(() => {
    loadFournisseurs()
  }, [])

  const loadFournisseurs = async () => {
    try {
      setIsLoading(true)
      const response = await api.get('/api/v1/suppliers')
      setFournisseurs(response.data || [])
    } catch (error) {
      console.error('Error loading fournisseurs:', error)
      setFournisseurs([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce fournisseur ?')) return
    
    try {
      await api.delete(`/api/v1/suppliers/${id}`)
      setFournisseurs(prev => prev.filter(f => f.id !== id))
    } catch (error) {
      console.error('Error deleting fournisseur:', error)
      toast.error('Erreur lors de la suppression du fournisseur.')
    }
  }

  const filteredFournisseurs = fournisseurs.filter(f => {
    const matchesSearch = f.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         f.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         f.email.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || f.type === filterType
    return matchesSearch && matchesType
  })

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-700 rounded w-1/3" />
          <div className="h-4 bg-slate-700 rounded w-1/2" />
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-slate-700 rounded" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/15 rounded-lg">
              <Building2 className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-100">Fournisseurs</h1>
              <p className="text-slate-400 text-sm">Gestion des fournisseurs et partenaires</p>
            </div>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Nouveau fournisseur
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-3 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher par nom, code ou email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Tous les types</option>
            <option value="transport">Transport</option>
            <option value="transit">Transit</option>
            <option value="douane">Douane</option>
            <option value="magasin">Magasin</option>
            <option value="autre">Autre</option>
          </select>
          <button className="flex items-center gap-2 px-4 py-2 border border-slate-600 rounded-lg hover:bg-slate-800">
            <Download className="w-4 h-4" />
            Exporter
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900 rounded-lg shadow overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-800">
          <thead className="bg-slate-800">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Code
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Nom
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Contact
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Statut
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-slate-900 divide-y divide-slate-800">
            {filteredFournisseurs.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                  {searchTerm || filterType !== 'all' 
                    ? 'Aucun fournisseur trouvé pour ces critères'
                    : 'Aucun fournisseur enregistré. Cliquez sur "Nouveau fournisseur" pour commencer.'}
                </td>
              </tr>
            ) : (
              filteredFournisseurs.map((fournisseur) => (
                <tr key={fournisseur.id} className="hover:bg-slate-800">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-100">
                    {fournisseur.code}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-slate-100">{fournisseur.nom}</div>
                    <div className="text-sm text-slate-400 flex items-center gap-1 mt-1">
                      <MapPin className="w-3 h-3" />
                      {fournisseur.ville}, {fournisseur.pays}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-slate-100 flex items-center gap-1">
                      <Mail className="w-3 h-3" />
                      {fournisseur.email}
                    </div>
                    <div className="text-sm text-slate-400 flex items-center gap-1 mt-1">
                      <Phone className="w-3 h-3" />
                      {fournisseur.telephone}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-500/15 text-blue-300">
                      {fournisseur.type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      fournisseur.status === 'active' 
                        ? 'bg-green-500/15 text-green-300' 
                        : 'bg-slate-800 text-slate-100'
                    }`}>
                      {fournisseur.status === 'active' ? 'Actif' : 'Inactif'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => {
                        setEditingFournisseur(fournisseur)
                        setShowModal(true)
                      }}
                      className="text-blue-600 hover:text-blue-200 mr-3"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(fournisseur.id)}
                      className="text-red-600 hover:text-red-200"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal Fournisseur Réel */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4">
            <h2 className="text-xl font-bold text-slate-100">
              {editingFournisseur ? 'Modifier le Fournisseur' : 'Nouveau Fournisseur B2B'}
            </h2>
            <form onSubmit={async (e) => {
              e.preventDefault();
              const target = e.target as any;
              const payload = {
                code: target.code.value,
                nom: target.nom.value,
                email: target.email.value,
                telephone: target.telephone.value,
                adresse: target.adresse.value,
                ville: target.ville.value,
                type: target.type.value,
                status: 'active'
              };
              try {
                if (editingFournisseur) {
                  await api.put(`/api/v1/suppliers/${editingFournisseur.id}`, payload);
                } else {
                  await api.post('/api/v1/suppliers', payload);
                }
                setShowModal(false);
                setEditingFournisseur(null);
                loadFournisseurs();
              } catch (err) {
                console.error(err);
              }
            }} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold mb-1 text-slate-200">Code Fournisseur *</label>
                  <input
                    name="code"
                    required
                    defaultValue={editingFournisseur?.code || `FOURN-${Date.now().toString().slice(-4)}`}
                    className="w-full px-3 py-2 border rounded-xl"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1 text-slate-200">Catégorie *</label>
                  <select name="type" defaultValue={editingFournisseur?.type || 'Transporteur'} className="w-full px-3 py-2 border rounded-xl">
                    <option value="Transporteur">Transporteur Routier</option>
                    <option value="Transitaire">Transitaire Partenaire</option>
                    <option value="Atelier & Pièces">Atelier & Pièces GMAO</option>
                    <option value="Hydrocarbures">Fournisseur Carburant</option>
                    <option value="Services">Services Généraux & Port</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-200">Raison Sociale / Nom *</label>
                <input
                  name="nom"
                  required
                  defaultValue={editingFournisseur?.nom || ''}
                  placeholder="Ex: CAMTRANS LOGISTICS SARL"
                  className="w-full px-3 py-2 border rounded-xl text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold mb-1 text-slate-200">Téléphone</label>
                  <input
                    name="telephone"
                    defaultValue={editingFournisseur?.telephone || ''}
                    placeholder="+237 6..."
                    className="w-full px-3 py-2 border rounded-xl"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1 text-slate-200">Email</label>
                  <input
                    name="email"
                    type="email"
                    defaultValue={editingFournisseur?.email || ''}
                    placeholder="contact@fournisseur.cm"
                    className="w-full px-3 py-2 border rounded-xl"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold mb-1 text-slate-200">Ville</label>
                  <input
                    name="ville"
                    defaultValue={editingFournisseur?.ville || 'Douala'}
                    className="w-full px-3 py-2 border rounded-xl"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1 text-slate-200">Adresse / Siège</label>
                  <input
                    name="adresse"
                    defaultValue={editingFournisseur?.adresse || ''}
                    placeholder="Zone Industrielle Bassa"
                    className="w-full px-3 py-2 border rounded-xl"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingFournisseur(null);
                  }}
                  className="px-4 py-2 bg-slate-800 rounded-xl hover:bg-slate-700 font-semibold"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-primary text-white rounded-xl hover:opacity-90 font-semibold"
                >
                  {editingFournisseur ? 'Enregistrer Modifications' : 'Créer Fournisseur'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
