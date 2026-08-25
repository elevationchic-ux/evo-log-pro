'use client'

import React, { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import ModuleLayout from '@/components/layout/ModuleLayout'
import { ArrowLeft, Truck, MapPin, Package, Calendar, CircleDollarSign } from 'lucide-react'
import { CardSkeletonLoader } from '@/components/ui/Loaders'

export default function ClientTransportHistoryPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string

  const [client, setClient] = useState<any>(null)
  const [missions, setMissions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [clientRes, missionsRes] = await Promise.all([
          fetch(`http://localhost:8000/api/master-data/tiers/${id}`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }),
          fetch(`http://localhost:8000/api/transport/missions/client/${id}`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
        ])

        if (clientRes.ok) setClient(await clientRes.json())
        if (missionsRes.ok) setMissions(await missionsRes.json())
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  if (loading) return <ModuleLayout module="master-data"><div className="p-8"><CardSkeletonLoader /></div></ModuleLayout>
  if (!client) return <ModuleLayout module="master-data"><div className="p-8 text-center text-slate-500 font-bold">Client introuvable</div></ModuleLayout>

  const totalCA = missions.reduce((acc, m) => acc + (parseFloat(m.montant_fret) || 0), 0)

  return (
    <ModuleLayout module="master-data">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500">
        
        {/* Header */}
        <div className="mb-8 flex items-center gap-4">
          <button onClick={() => router.back()} className="p-2 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 text-slate-500 hover:text-slate-700 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
              Historique Transport
            </h1>
            <p className="text-sm text-slate-500 mt-1">Missions effectuées pour le client <strong className="text-slate-800">{client.raison_sociale}</strong></p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center gap-4">
            <div className="p-4 bg-blue-100 text-blue-600 rounded-xl"><Truck className="w-6 h-6" /></div>
            <div>
              <p className="text-sm font-bold text-slate-500">Total Missions</p>
              <h3 className="text-2xl font-black text-slate-900">{missions.length}</h3>
            </div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center gap-4">
            <div className="p-4 bg-emerald-100 text-emerald-600 rounded-xl"><CircleDollarSign className="w-6 h-6" /></div>
            <div>
              <p className="text-sm font-bold text-slate-500">Chiffre d'Affaires Transport</p>
              <h3 className="text-2xl font-black text-slate-900">{totalCA.toLocaleString()} FCFA</h3>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50/80 border-b border-slate-100 text-xs uppercase font-bold text-slate-500">
              <tr>
                <th className="px-6 py-4">OT</th>
                <th className="px-6 py-4">Trajet</th>
                <th className="px-6 py-4">Ressources</th>
                <th className="px-6 py-4">Fret</th>
                <th className="px-6 py-4">Montant</th>
                <th className="px-6 py-4">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {missions.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500 font-medium">
                    Aucune mission de transport trouvée pour ce client.
                  </td>
                </tr>
              ) : missions.sort((a, b) => b.id - a.id).map(mission => (
                <tr key={mission.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-black text-slate-900">OT-{mission.id.toString().padStart(4, '0')}</div>
                    <div className="text-xs text-slate-500 font-medium flex items-center gap-1 mt-1">
                      <Calendar className="w-3 h-3" /> {new Date(mission.date_creation || Date.now()).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1 text-sm font-bold">
                      <div className="flex items-center gap-1.5 text-slate-700">
                        <MapPin className="w-3.5 h-3.5 text-emerald-600" /> {mission.origine}
                      </div>
                      <div className="flex items-center gap-1.5 text-slate-700">
                        <MapPin className="w-3.5 h-3.5 text-red-600" /> {mission.destination}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1 text-sm font-bold">
                      <div className="flex items-center gap-1.5 text-slate-700">
                        <Truck className="w-3.5 h-3.5 text-slate-400" />
                        {mission.camion?.immatriculation || `Camion ${mission.camion_id}`}
                      </div>
                      <div className="text-xs text-slate-500 ml-5">
                        {mission.chauffeur?.nom ? `${mission.chauffeur.nom} ${mission.chauffeur.prenom}` : `Chauffeur ${mission.chauffeur_id}`}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <Package className="w-4 h-4 text-slate-400" />
                      <div>
                        <div className="text-sm font-bold text-slate-800">{mission.nature_fret}</div>
                        <div className="text-xs font-medium text-slate-500">{mission.poids_kg} kg | {mission.volume_m3} m³</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-black text-slate-900">
                    {mission.montant_fret ? `${parseFloat(mission.montant_fret).toLocaleString()} FCFA` : '-'}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${mission.statut === 'TERMINEE' || mission.statut === 'FACTUREE' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                      {mission.statut.replace('_', ' ')}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </ModuleLayout>
  )
}
