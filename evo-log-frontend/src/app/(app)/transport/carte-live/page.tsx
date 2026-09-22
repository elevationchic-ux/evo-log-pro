'use client'

import React, { useState } from 'react'
import dynamic from 'next/dynamic'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Badge } from '@/components/ui/badge'
import { Activity, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import api from '@/lib/api-client'

// Leaflet component needs SSR disabled
const LiveMap = dynamic(() => import('@/components/transport/LiveMap'), {
  ssr: false,
  loading: () => (
    <div className="h-[600px] w-full bg-gray-100 animate-pulse rounded-lg flex items-center justify-center">
      <span className="text-gray-400 font-medium">Chargement de la carte...</span>
    </div>
  )
})

interface CamionPosition {
  id: number
  immatriculation: string
  lat: number
  lng: number
  speed: number
  status: string
  last_update: string
}

export default function CarteLivePage() {
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date())

  // Fetch live positions every 30 seconds
  const { data: positions, isLoading, isError, refetch, isFetching } = useQuery<CamionPosition[]>({
    queryKey: ['telematics-live-gps'],
    queryFn: async () => {
      const response = await api.get('/api/v1/telematics/live-gps')
      setLastRefreshed(new Date())
      return response.data
    },
    refetchInterval: 30000, // Poll every 30s
  })

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Live Control Tower</h1>
          <p className="text-muted-foreground mt-1">
            Suivi GPS en temps réel de la flotte de transport
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center text-sm text-gray-500">
            <Activity className="w-4 h-4 mr-2 text-green-500 animate-pulse" />
            Dernière sync: {lastRefreshed.toLocaleTimeString()}
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => refetch()} 
            disabled={isFetching}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isFetching ? 'animate-spin' : ''}`} />
            Rafraîchir
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Colonne de la carte */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader className="pb-4">
              <CardTitle>Carte Interactive</CardTitle>
              <CardDescription>Positions actualisées toutes les 30 secondes</CardDescription>
            </CardHeader>
            <CardContent>
              {isError ? (
                <div className="h-[600px] w-full bg-red-50 rounded-lg flex flex-col items-center justify-center text-red-500">
                  <p>Erreur lors du chargement des données GPS.</p>
                  <Button variant="outline" className="mt-4" onClick={() => refetch()}>Réessayer</Button>
                </div>
              ) : (
                <LiveMap positions={positions || []} />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Colonne du statut rapide */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Véhicules Actifs</CardTitle>
              <CardDescription>Vue d'ensemble de la flotte</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-blue-600">
                {isLoading ? '-' : (positions?.length || 0)}
              </div>
              <p className="text-sm text-gray-500 mt-1">véhicules en mouvement ou en mission</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Détails Rapides</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
                {isLoading ? (
                  Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="animate-pulse space-y-2 mb-4">
                      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                      <div className="h-3 bg-gray-100 rounded w-3/4"></div>
                    </div>
                  ))
                ) : positions?.length === 0 ? (
                  <p className="text-sm text-gray-500 italic">Aucun véhicule actif détecté.</p>
                ) : (
                  positions?.map(pos => (
                    <div key={pos.id} className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-semibold text-sm">{pos.immatriculation}</span>
                        <Badge variant={pos.speed > 0 ? "default" : "secondary"} className="text-[10px]">
                          {pos.speed > 0 ? 'En route' : 'À l\'arrêt'}
                        </Badge>
                      </div>
                      <div className="text-xs text-gray-600">Vitesse: {pos.speed.toFixed(1)} km/h</div>
                      <div className="text-[10px] text-gray-400 mt-1 truncate">Statut ERP: {pos.status}</div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
