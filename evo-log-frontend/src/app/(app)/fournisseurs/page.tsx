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
      alert('Erreur lors de la suppression')
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
          <div className="h-8 bg-gray-200 rounded w-1/3" />
          <div className="h-4 bg-gray-200 rounded w-1/2" />
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded" />
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
            <div className="p-2 bg-blue-100 rounded-lg">
              <Building2 className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Fournisseurs</h1>
              <p className="text-gray-600 text-sm">Gestion des fournisseurs et partenaires</p>
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
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Tous les types</option>
            <option value="transport">Transport</option>
            <option value="transit">Transit</option>
            <option value="douane">Douane</option>
            <option value="magasin">Magasin</option>
            <option value="autre">Autre</option>
          </select>
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            <Download className="w-4 h-4" />
            Exporter
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Code
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nom
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Contact
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Statut
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredFournisseurs.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                  {searchTerm || filterType !== 'all' 
                    ? 'Aucun fournisseur trouvé pour ces critères'
                    : 'Aucun fournisseur enregistré. Cliquez sur "Nouveau fournisseur" pour commencer.'}
                </td>
              </tr>
            ) : (
              filteredFournisseurs.map((fournisseur) => (
                <tr key={fournisseur.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {fournisseur.code}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{fournisseur.nom}</div>
                    <div className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                      <MapPin className="w-3 h-3" />
                      {fournisseur.ville}, {fournisseur.pays}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 flex items-center gap-1">
                      <Mail className="w-3 h-3" />
                      {fournisseur.email}
                    </div>
                    <div className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                      <Phone className="w-3 h-3" />
                      {fournisseur.telephone}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {fournisseur.type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      fournisseur.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
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
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(fournisseur.id)}
                      className="text-red-600 hover:text-red-900"
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

      {/* Modal placeholder */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <h2 className="text-xl font-bold mb-4">
              {editingFournisseur ? 'Modifier le fournisseur' : 'Nouveau fournisseur'}
            </h2>
            <p className="text-gray-600 mb-4">Formulaire en cours de développement...</p>
            <button
              onClick={() => {
                setShowModal(false)
                setEditingFournisseur(null)
              }}
              className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
            >
              Fermer
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
