'use client'

import { LayoutDashboard, Route, Package, BarChart3 } from 'lucide-react'

export default function TransportAvancePage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">🚚 K-Transport Avancé</h1>
        <p className="text-gray-600">Système de transport avancé avec optimisation et analytics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <LayoutDashboard className="w-5 h-5 text-cyan-600" />
            <span className="font-semibold">Dashboard</span>
          </div>
          <p className="text-sm text-gray-600">Vue d'ensemble transport avancé</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <Route className="w-5 h-5 text-cyan-600" />
            <span className="font-semibold">Optimisation Routes</span>
          </div>
          <p className="text-sm text-gray-600">Planification intelligente des itinéraires</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <Package className="w-5 h-5 text-cyan-600" />
            <span className="font-semibold">Gestion Complexes</span>
          </div>
          <p className="text-sm text-gray-600">Chargements et expéditions complexes</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="w-5 h-5 text-cyan-600" />
            <span className="font-semibold">Analytics</span>
          </div>
          <p className="text-sm text-gray-600">Statistiques et performances</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <h2 className="text-lg font-semibold mb-4">Fonctionnalités Transport Avancé</h2>
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-cyan-500 rounded-full mt-2"></div>
            <div>
              <h3 className="font-medium">Optimisation des itinéraires en temps réel</h3>
              <p className="text-sm text-gray-600">Algorithmes avancés pour minimiser les coûts et le temps de transport</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-cyan-500 rounded-full mt-2"></div>
            <div>
              <h3 className="font-medium">Gestion des chargements complexes</h3>
              <p className="text-sm text-gray-600">Support multi-modal et expéditions spécialisées</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-cyan-500 rounded-full mt-2"></div>
            <div>
              <h3 className="font-medium">Analytics prédictifs</h3>
              <p className="text-sm text-gray-600">Prévisions de demande et optimisation de la flotte</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}