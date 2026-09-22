'use client'

import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Download, RefreshCw, TrendingUp, DollarSign, Package, AlertCircle } from 'lucide-react'
import apiClient from '../../../../lib/api-client'
import { useAuth } from '../../../../components/layout/AuthProvider'

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']

export default function B2BReportingPage() {
  const [mounted, setMounted] = useState(false)
  const [reportType, setReportType] = useState('activite')
  const { user } = useAuth()
  const companyId = user?.companyId ?? null

  useEffect(() => {
    setMounted(true)
  }, [])

  const { data: report } = useQuery({
    queryKey: ['b2b-report', companyId, reportType],
    queryFn: async () => {
      if (companyId === null) throw new Error('Aucune société active')
      const res = await apiClient.get(`/api/v1/b2b/portal/${companyId}/reports/${reportType}`)
      return res.data
    },
    enabled: mounted && companyId !== null,
  })

  if (!mounted) return null

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Rapports Personnalisés</h1>
          <p className="text-gray-600 mt-1">Rapports personnalisés pour votre entreprise</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            <RefreshCw className="w-4 h-4" />
            Actualiser
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            <Download className="w-4 h-4" />
            Exporter
          </button>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setReportType('activite')}
          className={`px-4 py-2 rounded-lg ${reportType === 'activite' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
        >
          Activité
        </button>
        <button
          onClick={() => setReportType('financier')}
          className={`px-4 py-2 rounded-lg ${reportType === 'financier' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
        >
          Financier
        </button>
        <button
          onClick={() => setReportType('operations')}
          className={`px-4 py-2 rounded-lg ${reportType === 'operations' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
        >
          Opérations
        </button>
      </div>

      {report && (
        <>
          {/* KPIs */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Commandes</p>
                  <p className="text-2xl font-bold text-gray-900">{report.kpis.commandes}</p>
                </div>
                <Package className="w-8 h-8 text-blue-600" />
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Livraisons</p>
                  <p className="text-2xl font-bold text-gray-900">{report.kpis.livraisons}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Chiffre d'Affaires</p>
                  <p className="text-2xl font-bold text-gray-900">{(report.kpis.chiffre_affaires / 1000000).toFixed(1)}M FCFA</p>
                </div>
                <DollarSign className="w-8 h-8 text-purple-600" />
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Litiges</p>
                  <p className="text-2xl font-bold text-gray-900">{report.kpis.litiges}</p>
                </div>
                <AlertCircle className="w-8 h-8 text-red-600" />
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Évolution Mensuelle</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={report.graphiques.evolution_mensuelle}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="mois" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="commandes" stroke="#3B82F6" name="Commandes" />
                  <Line type="monotone" dataKey="livraisons" stroke="#10B981" name="Livraisons" />
                  <Line type="monotone" dataKey="factures" stroke="#F59E0B" name="Factures" />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Répartition des Services</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={report.graphiques.repartition_services}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ nom, valeur }) => `${nom}: ${valeur}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="valeur"
                  >
                    {report.graphiques.repartition_services.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Financial KPIs */}
          {reportType === 'financier' && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Indicateurs Financiers</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-gray-600">Marge</p>
                  <p className="text-2xl font-bold text-green-600">{(report.kpis.marge / 1000000).toFixed(1)}M FCFA</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600">Dépenses</p>
                  <p className="text-2xl font-bold text-blue-600">{(report.kpis.depenses / 1000000).toFixed(1)}M FCFA</p>
                </div>
                <div className="p-4 bg-red-50 rounded-lg">
                  <p className="text-sm text-gray-600">Factures Impayées</p>
                  <p className="text-2xl font-bold text-red-600">{report.kpis.factures_impayees}</p>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
