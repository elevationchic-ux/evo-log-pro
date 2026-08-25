'use client'

import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Building2,
  Plus,
  Search,
  Filter,
  MoreVertical,
  CheckCircle2,
  XCircle,
  Edit,
  ShieldCheck,
  Users,
  Database,
  TrendingUp,
  RefreshCw,
  Download
} from 'lucide-react'

// Mock API
const tenantAPI = {
  getCompanies: async () => {
    return {
      data: [
        {
          id: 1,
          code: 'CAMLOG',
          nom: 'Cameroon Logistics SA',
          legal_form: 'SA',
          email: 'contact@camlog.cm',
          telephone: '+237 233 456 789',
          ville: 'Douala',
          is_active: true,
          is_verified: true,
          max_users: 50,
          current_users: 12,
          max_storage_mb: 51200,
          current_storage_mb: 2450,
          subdomain: 'camlog.evolog.cm',
          subscription_end: '2026-12-31',
          created_at: '2026-01-01'
        },
        {
          id: 2,
          code: 'CEMACLOG',
          nom: 'CEMAC Express',
          legal_form: 'SARL',
          email: 'info@cemac.cm',
          telephone: '+237 699 123 456',
          ville: 'Yaoundé',
          is_active: true,
          is_verified: false,
          max_users: 25,
          current_users: 8,
          max_storage_mb: 25600,
          current_storage_mb: 1200,
          subdomain: 'cemac.evolog.cm',
          subscription_end: '2026-06-30',
          created_at: '2026-01-15'
        },
        {
          id: 3,
          code: 'PORTTRANS',
          nom: 'Port Transport International',
          legal_form: 'SA',
          email: 'admin@porttrans.cm',
          telephone: '+237 677 987 654',
          ville: 'Kribi',
          is_active: false,
          is_verified: true,
          max_users: 100,
          current_users: 45,
          max_storage_mb: 102400,
          current_storage_mb: 8900,
          subdomain: 'porttrans.evolog.cm',
          subscription_end: '2026-03-31',
          created_at: '2026-01-20'
        }
      ]
    }
  },
  createCompany: async (data: any) => {
    return { data: { ...data, id: Date.now() } }
  },
  activateCompany: async (id: number) => {
    return { data: { success: true } }
  },
  suspendCompany: async (id: number) => {
    return { data: { success: true } }
  }
}

export default function CompaniesPage() {
  const [mounted, setMounted] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedCompany, setSelectedCompany] = useState<any>(null)
  const queryClient = useQueryClient()

  useEffect(() => {
    setMounted(true)
  }, [])

  const { data: companies, isLoading } = useQuery({
    queryKey: ['companies'],
    queryFn: async () => {
      const res = await tenantAPI.getCompanies()
      return res.data || []
    },
    enabled: mounted,
  })

  const createMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await tenantAPI.createCompany(payload)
      return res.data
    },
    onSuccess: () => {
      console.log('Entreprise créée avec succès')
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      setIsModalOpen(false)
    },
    onError: () => {
      console.log('Erreur lors de la création de l\'entreprise')
    },
  })

  const activateMutation = useMutation({
    mutationFn: async (id: number) => {
      const res = await tenantAPI.activateCompany(id)
      return res.data
    },
    onSuccess: () => {
      console.log('Entreprise activée')
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    },
  })

  const suspendMutation = useMutation({
    mutationFn: async (id: number) => {
      const res = await tenantAPI.suspendCompany(id)
      return res.data
    },
    onSuccess: () => {
      console.log('Entreprise suspendue')
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    },
  })

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.target as HTMLFormElement)
    const payload = {
      code: formData.get('code'),
      nom: formData.get('nom'),
      legal_form: formData.get('legal_form'),
      email: formData.get('email'),
      telephone: formData.get('telephone'),
      ville: formData.get('ville'),
      subscription_plan_id: 1
    }
    createMutation.mutate(payload)
  }

  if (!mounted) return null

  const activeCompanies = companies?.filter((c: any) => c.is_active) || []
  const trialCompanies = companies?.filter((c: any) => !c.is_verified) || []

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Entreprises</h1>
          <p className="text-gray-600 mt-1">
            Créer et gérer les entreprises clientes du SAAS
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" />
          Nouvelle Entreprise
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Entreprises</p>
              <p className="text-2xl font-bold text-gray-900">{companies?.length || 0}</p>
            </div>
            <Building2 className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Actives</p>
              <p className="text-2xl font-bold text-green-600">{activeCompanies.length}</p>
            </div>
            <CheckCircle2 className="w-8 h-8 text-green-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">En Essai</p>
              <p className="text-2xl font-bold text-orange-600">{trialCompanies.length}</p>
            </div>
            <ShieldCheck className="w-8 h-8 text-orange-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Utilisateurs Totaux</p>
              <p className="text-2xl font-bold text-gray-900">
                {companies?.reduce((sum: number, c: any) => sum + c.current_users, 0) || 0}
              </p>
            </div>
            <Users className="w-8 h-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Companies List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Entreprises Configurées</h2>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <button className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                <Filter className="w-4 h-4" />
                Filtrer
              </button>
              <button className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                <RefreshCw className="w-4 h-4" />
                Actualiser
              </button>
            </div>
          </div>
        </div>
        <div className="divide-y divide-gray-200">
          {companies?.map((company: any) => (
            <div key={company.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-lg ${
                    company.is_active ? 'bg-green-100' : 'bg-red-100'
                  }`}>
                    <Building2 className={`w-6 h-6 ${
                      company.is_active ? 'text-green-600' : 'text-red-600'
                    }`} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{company.nom}</h3>
                    <p className="text-sm text-gray-600">{company.code} • {company.legal_form}</p>
                    <p className="text-xs text-gray-500 mt-1">{company.ville} • {company.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <p className={`text-sm font-medium ${
                      company.is_active ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {company.is_active ? 'Actif' : 'Suspendu'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {company.is_verified ? 'Vérifié' : 'En essai'}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Utilisateurs</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {company.current_users}/{company.max_users}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Stockage</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {company.current_storage_mb}MB / {company.max_storage_mb}MB
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        if (company.is_active) {
                          suspendMutation.mutate(company.id)
                        } else {
                          activateMutation.mutate(company.id)
                        }
                      }}
                      className={`px-3 py-1.5 text-sm rounded-lg ${
                        company.is_active
                          ? 'border border-red-300 text-red-600 hover:bg-red-50'
                          : 'border border-green-300 text-green-600 hover:bg-green-50'
                      }`}
                    >
                      {company.is_active ? 'Suspendre' : 'Activer'}
                    </button>
                    <button className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Nouvelle Entreprise</h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Code</label>
                  <input
                    name="code"
                    type="text"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="CAMLOG"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nom</label>
                  <input
                    name="nom"
                    type="text"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Cameroon Logistics SA"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Forme Juridique</label>
                  <select
                    name="legal_form"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="SA">SA</option>
                    <option value="SARL">SARL</option>
                    <option value="SAS">SAS</option>
                    <option value="EURL">EURL</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    name="email"
                    type="email"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="contact@company.cm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Téléphone</label>
                  <input
                    name="telephone"
                    type="tel"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="+237 233 456 789"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ville</label>
                  <input
                    name="ville"
                    type="text"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Douala"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Créer Entreprise
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
