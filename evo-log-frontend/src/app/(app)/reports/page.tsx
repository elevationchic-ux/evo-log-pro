'use client'

import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Package,
  Truck,
  ShieldCheck,
  FileText,
  Download,
  RefreshCw,
  Calendar,
  Filter
} from 'lucide-react'

// Mock API pour les KPIs et rapports
const reportingAPI = {
  getExecutiveDashboard: async () => {
    return {
      data: {
        kpis: [
          { code: 'KPI-CA', nom: 'Chiffre d\'Affaires', valeur: 284500000, tendance: 'hausse', variation: 12.5 },
          { code: 'KPI-MARGE', nom: 'Marge Nette', valeur: 45200000, tendance: 'hausse', variation: 8.3 },
          { code: 'KPI-CLIENTS', nom: 'Clients Actifs', valeur: 142, tendance: 'hausse', variation: 5.2 },
          { code: 'KPI-DOUANE', nom: 'Délai Douane (j)', valeur: 3.2, tendance: 'baisse', variation: -15.4 },
        ],
        rapports_recentes: [
          { id: 1, titre: 'Rapport Mensuel Janvier', type: 'financier', date: '2026-01-15' },
          { id: 2, titre: 'Rapport QHSE Q1', type: 'qhse', date: '2026-01-10' },
          { id: 3, titre: 'Rapport Performance Port', type: 'operationnel', date: '2026-01-08' },
        ]
      }
    }
  }
}

export default function ReportsPage() {
  const [mounted, setMounted] = useState(false)
  const [period, setPeriod] = useState('month')

  useEffect(() => {
    setMounted(true)
  }, [])

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['executive-dashboard', period],
    queryFn: async () => {
      const res = await reportingAPI.getExecutiveDashboard()
      return res.data
    },
    enabled: mounted,
  })

  if (!mounted) return null

  const kpis = dashboard?.kpis || []
  const rapports = dashboard?.rapports_recentes || []

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Exécutif</h1>
          <p className="text-gray-600 mt-1">
            Indicateurs clés de performance et rapports consolidés
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="week">Cette Semaine</option>
            <option value="month">Ce Mois</option>
            <option value="quarter">Ce Trimestre</option>
            <option value="year">Cette Année</option>
          </select>
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            <Download className="w-4 h-4" />
            Exporter
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {kpis.map((kpi) => (
          <div key={kpi.code} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                {kpi.code === 'KPI-CA' && <DollarSign className="w-6 h-6 text-blue-600" />}
                {kpi.code === 'KPI-MARGE' && <TrendingUp className="w-6 h-6 text-green-600" />}
                {kpi.code === 'KPI-CLIENTS' && <Package className="w-6 h-6 text-purple-600" />}
                {kpi.code === 'KPI-DOUANE' && <ShieldCheck className="w-6 h-6 text-orange-600" />}
              </div>
              <div className={`flex items-center gap-1 text-sm ${
                kpi.tendance === 'hausse' ? 'text-green-600' : 'text-red-600'
              }`}>
                {kpi.tendance === 'hausse' ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
                <span>{Math.abs(kpi.variation)}%</span>
              </div>
            </div>
            <p className="text-sm text-gray-600">{kpi.nom}</p>
            <p className="text-2xl font-bold text-gray-900">
              {kpi.code === 'KPI-CA' || kpi.code === 'KPI-MARGE' 
                ? `${(kpi.valeur / 1000000).toFixed(1)}M FCFA`
                : kpi.valeur.toLocaleString('fr-FR')
              }
            </p>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Performance Financière</h2>
            <BarChart3 className="w-5 h-5 text-gray-400" />
          </div>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <p className="text-gray-500">Graphique en cours de développement</p>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Performance Opérationnelle</h2>
            <Truck className="w-5 h-5 text-gray-400" />
          </div>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <p className="text-gray-500">Graphique en cours de développement</p>
          </div>
        </div>
      </div>

      {/* Recent Reports */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Rapports Récents</h2>
            <button className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700">
              <FileText className="w-4 h-4" />
              Voir tous les rapports
            </button>
          </div>
        </div>
        <div className="divide-y divide-gray-200">
          {rapports.map((rapport) => (
            <div key={rapport.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-gray-100 rounded-lg">
                    <FileText className="w-6 h-6 text-gray-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{rapport.titre}</h3>
                    <p className="text-sm text-gray-600">{rapport.type} • {rapport.date}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
                    Voir
                  </button>
                  <button className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
                    Télécharger
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:bg-gray-50">
          <div className="p-3 bg-blue-100 rounded-lg">
            <FileText className="w-6 h-6 text-blue-600" />
          </div>
          <div className="text-left">
            <p className="font-semibold text-gray-900">Générer Rapport</p>
            <p className="text-sm text-gray-600">Créer un nouveau rapport</p>
          </div>
        </button>
        <button className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:bg-gray-50">
          <div className="p-3 bg-green-100 rounded-lg">
            <Download className="w-6 h-6 text-green-600" />
          </div>
          <div className="text-left">
            <p className="font-semibold text-gray-900">Exporter Données</p>
            <p className="text-sm text-gray-600">Excel, CSV, PDF</p>
          </div>
        </button>
        <button className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:bg-gray-50">
          <div className="p-3 bg-purple-100 rounded-lg">
            <Calendar className="w-6 h-6 text-purple-600" />
          </div>
          <div className="text-left">
            <p className="font-semibold text-gray-900">Planifier Rapport</p>
            <p className="text-sm text-gray-600">Automatisation</p>
          </div>
        </button>
      </div>
    </div>
  )
}
