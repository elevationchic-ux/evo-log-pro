'use client'

import React, { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { transportAPI } from '@/lib/api-client'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { User, Calendar, MapPin, CheckCircle2, AlertTriangle, ShieldAlert, FileText, ArrowLeft, Fuel, Truck } from 'lucide-react'
import { CardSkeletonLoader } from '@/components/ui/Loaders'

export default function DriverProfilePage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string

  const [driver, setDriver] = useState<any>(null)
  const [missions, setMissions] = useState<any[]>([])
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDriverData = async () => {
      try {
        const [driverRes, missionsRes, docsRes] = await Promise.all([
          // Note: you may need to add getChauffeur to transportAPI
          fetch(`http://localhost:8000/api/transport/chauffeurs/${id}`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }),
          fetch(`http://localhost:8000/api/transport/missions/chauffeur/${id}`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }),
          fetch(`http://localhost:8000/api/transport/chauffeurs/${id}/documents`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
        ])

        if (driverRes.ok) setDriver(await driverRes.json())
        if (missionsRes.ok) setMissions(await missionsRes.json())
        if (docsRes.ok) setDocuments(await docsRes.json())
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchDriverData()
  }, [id])

  if (loading) return <ModuleLayout module="transport"><div className="p-8"><CardSkeletonLoader /></div></ModuleLayout>
  if (!driver) return <ModuleLayout module="transport"><div className="p-8 text-center text-slate-500 font-bold">Chauffeur introuvable</div></ModuleLayout>

  const isExpired = (dateString: string) => new Date(dateString) < new Date()
  const activeMissions = missions.filter(m => m.statut === 'EN_ROUTE' || m.statut === 'AFFECTEE')
  const completedMissions = missions.filter(m => m.statut === 'TERMINEE' || m.statut === 'FACTUREE')

  return (
    <ModuleLayout module="transport">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500">
        
        {/* Header */}
        <div className="mb-8 flex items-center gap-4">
          <button onClick={() => router.back()} className="p-2 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 text-slate-500 hover:text-slate-700 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
              Profil Conducteur
            </h1>
            <p className="text-sm text-slate-500 mt-1">Détails, KPI et historique de {driver.nom} {driver.prenom}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column: Identity & KPIs */}
          <div className="lg:col-span-1 flex flex-col gap-6">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-2xl font-bold">
                  {driver.nom.charAt(0)}{driver.prenom.charAt(0)}
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-900">{driver.nom} {driver.prenom}</h2>
                  <p className="text-sm text-slate-500 font-medium">Permis: {driver.numero_permis}</p>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex justify-between items-center py-3 border-b border-slate-100">
                  <span className="text-slate-500 font-medium text-sm">Téléphone</span>
                  <span className="text-slate-800 font-bold">{driver.telephone}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-slate-100">
                  <span className="text-slate-500 font-medium text-sm">Date d'embauche</span>
                  <span className="text-slate-800 font-bold">{new Date(driver.date_embauche).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between items-center py-3">
                  <span className="text-slate-500 font-medium text-sm">Statut</span>
                  {driver.statut === 'DISPONIBLE' ? (
                    <span className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-bold flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Disponible
                    </span>
                  ) : (
                    <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-bold flex items-center gap-1">
                      <Truck className="w-3.5 h-3.5" /> {driver.statut.replace('_', ' ')}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* KPIs */}
            <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl shadow-sm border border-slate-700 p-6 text-white relative overflow-hidden">
              <div className="absolute -right-6 -top-6 text-white/5">
                <User className="w-48 h-48" />
              </div>
              <h3 className="font-bold mb-6 text-slate-300 relative z-10">Performances Globales</h3>
              <div className="grid grid-cols-2 gap-4 relative z-10">
                <div className="bg-white/10 p-4 rounded-xl backdrop-blur-sm border border-white/10">
                  <div className="text-3xl font-black">{completedMissions.length}</div>
                  <div className="text-xs font-bold text-slate-400 mt-1 uppercase tracking-wider">Missions<br/>Terminées</div>
                </div>
                <div className="bg-white/10 p-4 rounded-xl backdrop-blur-sm border border-white/10">
                  <div className="text-3xl font-black">{activeMissions.length}</div>
                  <div className="text-xs font-bold text-slate-400 mt-1 uppercase tracking-wider">Missions<br/>En cours</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Missions & Documents */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            
            {/* Documents */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-5 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
                <h3 className="font-bold text-slate-800 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-blue-600" /> Documents de Conduite
                </h3>
              </div>
              <div className="p-5">
                {documents.length === 0 ? (
                  <p className="text-center text-slate-500 py-4 text-sm font-medium">Aucun document enregistré.</p>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {documents.map(doc => {
                      const expired = isExpired(doc.date_expiration);
                      return (
                        <div key={doc.id} className={`p-4 rounded-xl border ${expired ? 'bg-red-50 border-red-200' : 'bg-white border-slate-200'}`}>
                          <div className="flex items-center gap-3 mb-2">
                            {expired ? <ShieldAlert className="w-5 h-5 text-red-600" /> : <CheckCircle2 className="w-5 h-5 text-emerald-600" />}
                            <h4 className="font-bold text-slate-800">{doc.type_document}</h4>
                          </div>
                          <p className="text-sm font-bold text-slate-500 mb-2">{doc.numero}</p>
                          <div className={`text-xs font-bold ${expired ? 'text-red-600' : 'text-slate-500'}`}>
                            Expire le: {new Date(doc.date_expiration).toLocaleDateString()}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Historique Missions */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-5 border-b border-slate-100 bg-slate-50/50">
                <h3 className="font-bold text-slate-800 flex items-center gap-2">
                  <Truck className="w-5 h-5 text-blue-600" /> Historique des Missions
                </h3>
              </div>
              <div className="divide-y divide-slate-100 max-h-[400px] overflow-y-auto custom-scrollbar">
                {missions.length === 0 ? (
                  <p className="text-center text-slate-500 py-8 text-sm font-medium">Aucune mission assignée.</p>
                ) : (
                  missions.sort((a, b) => b.id - a.id).map(mission => (
                    <div key={mission.id} className="p-5 hover:bg-slate-50 transition-colors">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center gap-2">
                          <span className="font-black text-lg text-slate-900">OT-{mission.id.toString().padStart(4, '0')}</span>
                          <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${mission.statut === 'TERMINEE' || mission.statut === 'FACTUREE' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                            {mission.statut.replace('_', ' ')}
                          </span>
                        </div>
                        <span className="text-xs font-bold text-slate-400">
                          {new Date(mission.date_creation || Date.now()).toLocaleDateString()}
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-6 text-sm">
                        <div className="flex flex-col gap-2 relative">
                          <div className="flex items-center gap-2 text-slate-700">
                            <MapPin className="w-4 h-4 text-emerald-600" /> <span className="font-bold">{mission.point_depart}</span>
                          </div>
                          <div className="flex items-center gap-2 text-slate-700">
                            <MapPin className="w-4 h-4 text-red-600" /> <span className="font-bold">{mission.point_arrivee}</span>
                          </div>
                        </div>
                        <div className="flex-1 border-l-2 border-slate-100 pl-6 space-y-2">
                          {mission.prix_carburant_prevu && (
                            <div className="flex justify-between">
                              <span className="text-slate-500 text-xs">Frais Carburant Prévus</span>
                              <span className="font-bold text-slate-800 text-xs">{mission.prix_carburant_prevu} FCFA</span>
                            </div>
                          )}
                          <div className="flex justify-between">
                            <span className="text-slate-500 text-xs">Frais Route Prévus</span>
                            <span className="font-bold text-slate-800 text-xs">{mission.frais_route_prevus} FCFA</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

          </div>
        </div>
      </div>
    </ModuleLayout>
  )
}
