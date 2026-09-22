'use client'

import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Building2, Plus, Users, Layers } from 'lucide-react'

const companyAPI = {
  getDepartments: async (companyId: number) => {
    return {
      data: [
        { id: 1, name: 'Direction', manager: 'Admin Principal', users_count: 3, parent: null },
        { id: 2, name: 'Transport', manager: 'Responsable Transport', users_count: 5, parent: 'Direction' },
        { id: 3, name: 'Magasin', manager: 'Magasinier Principal', users_count: 8, parent: 'Direction' },
        { id: 4, name: 'Finance', manager: 'Comptable', users_count: 2, parent: 'Direction' }
      ]
    }
  }
}

export default function CompanyDepartmentsPage() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const { data: departments } = useQuery({
    queryKey: ['company-departments', 1],
    queryFn: async () => {
      const res = await companyAPI.getDepartments(1)
      return res.data || []
    },
    enabled: mounted,
  })

  if (!mounted) return null

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Départements</h1>
          <p className="text-gray-600 mt-1">Organiser les départements de votre entreprise</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          <Plus className="w-4 h-4" />
          Nouveau Département
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Départements ({departments?.length || 0})</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {departments?.map((dept: any) => (
            <div key={dept.id} className="border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-purple-100 rounded-lg">
                    <Building2 className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{dept.name}</h3>
                    <p className="text-sm text-gray-600">Chef: {dept.manager}</p>
                  </div>
                </div>
                <button className="p-2 hover:bg-gray-100 rounded-lg">
                  <Layers className="w-5 h-5 text-gray-400" />
                </button>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  <span>{dept.users_count} utilisateurs</span>
                </div>
                {dept.parent && <span>• Parent: {dept.parent}</span>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
