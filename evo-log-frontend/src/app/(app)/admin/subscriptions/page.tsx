'use client'

import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { CreditCard, TrendingUp, DollarSign, RefreshCw, Download } from 'lucide-react'

const subscriptionsAPI = {
  getSubscriptions: async () => {
    return {
      data: [
        { id: 1, company: 'Cameroon Logistics SA', plan: 'Enterprise', amount: 500000, status: 'active', end_date: '2026-12-31' },
        { id: 2, company: 'CEMAC Express', plan: 'Pro', amount: 250000, status: 'active', end_date: '2026-06-30' },
        { id: 3, company: 'Port Transport', plan: 'Starter', amount: 100000, status: 'past_due', end_date: '2026-03-31' }
      ]
    }
  },
  getPlans: async () => {
    return {
      data: [
        { id: 1, name: 'Starter', prix_mensuel: 100000, prix_annuel: 1000000, max_users: 10, max_storage_mb: 1024 },
        { id: 2, name: 'Pro', prix_mensuel: 250000, prix_annuel: 2500000, max_users: 25, max_storage_mb: 25600 },
        { id: 3, name: 'Enterprise', prix_mensuel: 500000, prix_annuel: 5000000, max_users: 100, max_storage_mb: 102400 }
      ]
    }
  }
}

export default function SubscriptionsPage() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const { data: subscriptions } = useQuery({
    queryKey: ['subscriptions'],
    queryFn: async () => {
      const res = await subscriptionsAPI.getSubscriptions()
      return res.data || []
    },
    enabled: mounted,
  })

  const { data: plans } = useQuery({
    queryKey: ['plans'],
    queryFn: async () => {
      const res = await subscriptionsAPI.getPlans()
      return res.data || []
    },
    enabled: mounted,
  })

  if (!mounted) return null

  const totalRevenue = subscriptions?.reduce((sum: number, s: any) => sum + s.amount, 0) || 0

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Abonnements</h1>
          <p className="text-gray-600 mt-1">Plans, facturation et revenus SAAS</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          <Download className="w-4 h-4" />
          Exporter Rapport
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Revenu Mensuel</p>
              <p className="text-2xl font-bold text-gray-900">{(totalRevenue / 1000000).toFixed(1)}M FCFA</p>
            </div>
            <DollarSign className="w-8 h-8 text-green-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Abonnements Actifs</p>
              <p className="text-2xl font-bold text-green-600">{subscriptions?.filter((s: any) => s.status === 'active').length}</p>
            </div>
            <CreditCard className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">En Retard</p>
              <p className="text-2xl font-bold text-red-600">{subscriptions?.filter((s: any) => s.status === 'past_due').length}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-red-600" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Plans d'Abonnement</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {plans?.map((plan: any) => (
            <div key={plan.id} className="border border-gray-200 rounded-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
              <p className="text-3xl font-bold text-blue-600 mb-4">{plan.prix_mensuel.toLocaleString('fr-FR')} FCFA<span className="text-sm text-gray-600">/mois</span></p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• {plan.max_users} utilisateurs</li>
                <li>• {plan.max_storage_mb} MB stockage</li>
                <li>• Support prioritaire</li>
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
