'use client'

import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Users, Plus, Search, UserCheck, ShieldCheck, MoreVertical, Mail, XCircle } from 'lucide-react'
import { adminAPI } from '../../../../lib/api-client'
import { useAuth } from '../../../../components/layout/AuthProvider'

export default function CompanyUsersPage() {
  const [mounted, setMounted] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const companyId = user?.companyId ?? null

  useEffect(() => {
    setMounted(true)
  }, [])

  const { data: users, isLoading } = useQuery({
    queryKey: ['company-users', companyId, searchQuery],
    queryFn: async () => {
      const res = await adminAPI.getUsers({ search: searchQuery || undefined })
      return res.data
    },
    enabled: mounted && companyId !== null,
  })

  const inviteMutation = useMutation({
    mutationFn: async (data: any) => {
      if (companyId === null) throw new Error('Aucune société active')
      const res = await adminAPI.createUser({ ...data, role: data.role_level === 1 ? 'ADMIN' : 'OPERATEUR' })
      return res.data
    },
    onSuccess: () => {
      console.log('Invitation envoyée avec succès')
      queryClient.invalidateQueries({ queryKey: ['company-users', companyId] })
      setIsModalOpen(false)
    },
    onError: () => {
      console.log('Erreur lors de l\'invitation')
    },
  })

  const handleInvite = (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.target as HTMLFormElement)
    const payload = {
      email: formData.get('email'),
      full_name: formData.get('full_name'),
      role_level: parseInt(formData.get('role_level') as string),
      department: formData.get('department'),
      password: formData.get('password')
    }
    inviteMutation.mutate(payload)
  }

  if (!mounted) return null

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Gestion des Utilisateurs</h1>
          <p className="text-slate-400 mt-1">Gérer les utilisateurs de votre entreprise</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" />
          Inviter Utilisateur
        </button>
      </div>

      <div className="bg-slate-900 rounded-lg shadow-sm border border-slate-700">
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-100">Utilisateurs ({users?.length || 0})</h2>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>
        <div className="divide-y divide-slate-800">
          {users?.map((user: any) => (
            <div key={user.id} className="p-6 hover:bg-slate-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-blue-500/15 rounded-full">
                    <Users className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-100">{user.full_name}</h3>
                    <p className="text-sm text-slate-400">{user.username} • {user.email}</p>
                    <p className="text-xs text-slate-400 mt-1">{user.department?.name || 'Département non renseigné'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    user.role_level === 1 ? 'bg-purple-500/15 text-purple-300' :
                    user.role_level === 2 ? 'bg-blue-500/15 text-blue-300' :
                    'bg-slate-800 text-slate-200'
                  }`}>
                    {user.role_level === 1 ? 'Admin' : user.role_level === 2 ? 'Chef Dept' : 'User'}
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    user.is_active ? 'bg-green-500/15 text-green-300' : 'bg-red-500/15 text-red-300'
                  }`}>
                    {user.is_active ? 'Actif' : 'Inactif'}
                  </div>
                  <button className="px-3 py-1.5 text-sm border border-slate-600 rounded-lg hover:bg-slate-800">
                    <Mail className="w-4 h-4" />
                  </button>
                  <button className="px-3 py-1.5 text-sm border border-slate-600 rounded-lg hover:bg-slate-800">
                    <MoreVertical className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-slate-900 rounded-lg shadow-xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-slate-100">Inviter Utilisateur</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-slate-400">
                <XCircle className="w-6 h-6" />
              </button>
            </div>
            <form onSubmit={handleInvite} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-200 mb-1">Email</label>
                <input
                  name="email"
                  type="email"
                  required
                  className="w-full px-3 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="user@company.cm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-200 mb-1">Nom Complet</label>
                <input
                  name="full_name"
                  type="text"
                  required
                  className="w-full px-3 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Jean Dupont"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-200 mb-1">Mot de passe initial</label>
                <input
                  name="password"
                  type="password"
                  required
                  minLength={12}
                  className="w-full px-3 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500"
                  autoComplete="new-password"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-200 mb-1">Rôle</label>
                <select
                  name="role_level"
                  className="w-full px-3 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="3">Utilisateur Standard</option>
                  <option value="2">Chef Département</option>
                  <option value="1">Admin Entreprise</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-200 mb-1">Département</label>
                <input
                  name="department"
                  type="text"
                  className="w-full px-3 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Transport"
                />
              </div>
              <div className="flex justify-end gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-slate-600 rounded-lg hover:bg-slate-800"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Inviter
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
