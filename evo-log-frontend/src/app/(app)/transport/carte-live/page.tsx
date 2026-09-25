'use client'

import React, { useState } from 'react'
import dynamic from 'next/dynamic'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Badge } from '@/components/ui/badge'
import { Activity, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import api from '@/lib/api-client'
import { useSettings } from '@/components/layout/SettingsProvider'

// Leaflet component needs SSR disabled
const LiveMap = dynamic(() => import('@/components/transport/LiveMap'), {
  ssr: false,
  loading: () => (
    <div className="flex h-[600px] w-full animate-pulse items-center justify-center rounded-lg bg-slate-900">
      <span className="font-medium text-slate-500">Chargement de la carte...</span>
    </div>
  )
})

interface CamionPosition {
  id: number
  vehicule_id?: number
  latitude?: number
  longitude?: number
  vitesse?: number
  statut_vehicule?: string
  horodatage?: string
}

export default function CarteLivePage() {
  const { language } = useSettings()
  const lang = language === 'en' ? 'en' : 'fr'
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr)
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date())

  // Fetch live positions every 30 seconds
  const { data: positions, isLoading, isError, refetch, isFetching } = useQuery<CamionPosition[]>({
    queryKey: ['telematics-live-gps'],
    queryFn: async () => {
      const response = await api.get('/api/v1/telematics/positions', { params: { depuis_minutes: 1440, limit: 200 } })
      setLastRefreshed(new Date())
      const payload = response.data
      return Array.isArray(payload) ? payload : (payload?.data || payload?.positions || payload?.items || [])
    },
    refetchInterval: 30000, // Poll every 30s
  })

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-4 pb-24 text-slate-100 sm:p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">{t('Live Control Tower', 'Live Control Tower')}</h1>
          <p className="mt-1 text-slate-400">
            {t('Suivi GPS en temps réel de la flotte de transport', 'Real-time GPS tracking of the transport fleet')}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center text-sm text-slate-400">
            <Activity className="mr-2 h-4 w-4 animate-pulse text-cyan-400" />
            {t('Dernière sync', 'Last sync')}: {lastRefreshed.toLocaleTimeString()}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
            {t('Rafraîchir', 'Refresh')}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        {/* Colonne de la carte */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader className="pb-4">
              <CardTitle>{t('Carte Interactive', 'Interactive Map')}</CardTitle>
              <CardDescription>{t('Positions actualisées toutes les 30 secondes', 'Positions refreshed every 30 seconds')}</CardDescription>
            </CardHeader>
            <CardContent>
              {isError ? (
                <div className="flex h-[600px] w-full flex-col items-center justify-center rounded-lg border border-rose-500/30 bg-rose-500/10 text-rose-300">
                  <p>{t('Erreur lors du chargement des données GPS.', 'Failed to load GPS data.')}</p>
                  <Button variant="outline" className="mt-4" onClick={() => refetch()}>{t('Réessayer', 'Retry')}</Button>
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
              <CardTitle>{t('Véhicules Actifs', 'Active Vehicles')}</CardTitle>
              <CardDescription>{t("Vue d'ensemble de la flotte", 'Fleet overview')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-cyan-400">
                {isLoading ? '-' : (positions?.length || 0)}
              </div>
              <p className="mt-1 text-sm text-slate-400">
                {t('véhicules en mouvement ou en mission', 'vehicles moving or on mission')}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t('Détails Rapides', 'Quick Details')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="max-h-[400px] space-y-4 overflow-y-auto pr-2">
                {isLoading ? (
                  Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="mb-4 animate-pulse space-y-2">
                      <div className="h-4 w-1/2 rounded bg-slate-800"></div>
                      <div className="h-3 w-3/4 rounded bg-slate-800/60"></div>
                    </div>
                  ))
                ) : positions?.length === 0 ? (
                  <p className="text-sm italic text-slate-400">{t('Aucun véhicule actif détecté.', 'No active vehicle detected.')}</p>
                ) : (
                  positions?.map((pos) => (
                    <div key={pos.id} className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
                      <div className="mb-2 flex items-start justify-between">
                        <span className="text-sm font-semibold text-white">
                          {pos.vehicule_id != null ? `Véhicule #${pos.vehicule_id}` : `#${pos.id}`}
                        </span>
                        <Badge variant={(pos.vitesse ?? 0) > 0 ? 'default' : 'secondary'} className="text-[10px]">
                          {(pos.vitesse ?? 0) > 0 ? t('En route', 'Moving') : t("À l'arrêt", 'Stopped')}
                        </Badge>
                      </div>
                      <div className="text-xs text-slate-400">
                        {t('Vitesse', 'Speed')}: {(pos.vitesse ?? 0).toFixed(1)} km/h
                      </div>
                      <div className="mt-1 truncate text-[10px] text-slate-500">
                        {t('Statut ERP', 'ERP status')}: {pos.statut_vehicule || ''}
                      </div>
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
