'use client';

import React, { useEffect, useState } from 'react';
import { transportAPI } from '@/lib/api-client';
import { ModuleLayout } from '@/components/layout/ModuleLayout';
import { Calendar, Filter, GripVertical, Map, MapPin, Search, TrendingUp, Truck, Printer } from 'lucide-react';
import { CardSkeletonLoader } from '@/components/ui/Loaders';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function PlanningPage() {
  const [missions, setMissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // KPI Stats
  const [stats, setStats] = useState({
    total: 0,
    planifie: 0,
    enRoute: 0,
    livre: 0
  });

  useEffect(() => {
    loadMissions();
  }, []);

  const loadMissions = async () => {
    try {
      setLoading(true);
      const res = await transportAPI.getMissions();
      const data = res.data || [];
      setMissions(data);
      
      // Calculate stats
      setStats({
        total: data.length,
        planifie: data.filter((m: any) => m.statut === 'PLANIFIE' || m.statut === 'BROUILLON').length,
        enRoute: data.filter((m: any) => m.statut === 'EN_ROUTE' || m.statut === 'EN_CHARGEMENT').length,
        livre: data.filter((m: any) => m.statut === 'LIVRE' || m.statut === 'TERMINEE').length
      });
      
    } catch (error) {
      console.error('Error loading planning', error);
    } finally {
      setLoading(false);
    }
  };

  const renderKanbanColumn = (title: string, color: string, filterStatuses: string[]) => {
    const colMissions = missions.filter(m => filterStatuses.includes(m.statut));
    
    return (
      <div className="flex-1 min-w-[320px] max-w-sm bg-slate-50/50 rounded-2xl border border-slate-200 p-4 flex flex-col max-h-[800px]">
        <div className="flex items-center justify-between mb-4 px-2">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${color}`} />
            <h3 className="font-bold text-slate-800">{title}</h3>
          </div>
          <span className="bg-slate-200 text-slate-600 text-xs font-bold px-2 py-1 rounded-full">
            {colMissions.length}
          </span>
        </div>
        
        <div className="flex-1 overflow-y-auto pr-2 space-y-4 pb-4">
          {colMissions.length === 0 ? (
            <div className="h-24 border-2 border-dashed border-slate-200 rounded-xl flex items-center justify-center text-sm text-slate-400">
              Aucun dossier
            </div>
          ) : (
            colMissions.map((mission) => (
              <div 
                key={mission.id} 
                className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow cursor-grab active:cursor-grabbing group"
              >
                <div className="flex justify-between items-start mb-3">
                  <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded-md">
                    {mission.reference}
                  </span>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      onClick={() => window.open(`/transport/documents/bl/${mission.id}`, '_blank')}
                      className="p-1 hover:bg-slate-100 rounded text-slate-500 hover:text-blue-600 transition-colors"
                      title="Imprimer BL"
                    >
                      <Printer className="w-4 h-4" />
                    </button>
                    <GripVertical className="w-4 h-4 text-slate-300" />
                  </div>
                </div>
                
                <h4 className="text-sm font-semibold text-slate-800 mb-1 line-clamp-1">
                  {mission.nature_fret.replace(/_/g, ' ')}
                </h4>
                
                <div className="space-y-2 mt-3">
                  <div className="flex items-center gap-2 text-xs text-slate-600">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span className="truncate">{mission.origine} → {mission.destination}</span>
                  </div>
                  
                  {mission.date_chargement_prevue && (
                    <div className="flex items-center gap-2 text-xs text-slate-600">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      <span>{format(new Date(mission.date_chargement_prevue), 'dd MMM yyyy', { locale: fr })}</span>
                    </div>
                  )}
                  
                  <div className="pt-2 mt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1 font-medium text-slate-700">
                      <Truck className="w-3.5 h-3.5 text-indigo-500" />
                      Tracteur assigné
                    </div>
                    {mission.camion_id ? (
                      <span className="text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded font-bold text-[10px]">OK</span>
                    ) : (
                      <span className="text-red-600 bg-red-50 px-1.5 py-0.5 rounded font-bold text-[10px]">À FAIRE</span>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    );
  };

  return (
    <ModuleLayout module="transport">
      <div className="h-full flex flex-col animate-in fade-in duration-500 bg-slate-100">
        
        {/* Header & KPIs */}
        <div className="bg-white border-b border-slate-200 px-6 py-6 shrink-0">
          <div className="max-w-[1600px] mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
              <div>
                <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
                  <Calendar className="w-7 h-7 text-indigo-600" />
                  K-Planning Global (SAP PP)
                </h1>
                <p className="text-slate-500 text-sm mt-1">
                  Planification visuelle des missions, allocation des camions et suivi du dispatching.
                </p>
              </div>
              
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input 
                    type="text" 
                    placeholder="Rechercher un OT..." 
                    className="pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  />
                </div>
                <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-sm">
                  Planifier / Dispatcher
                </button>
              </div>
            </div>

            {/* KPI Cards Mini */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex items-center gap-4">
                <div className="p-3 bg-slate-200/50 rounded-lg text-slate-600"><Map className="w-5 h-5" /></div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Total Missions</p>
                  <p className="text-2xl font-bold text-slate-800">{stats.total}</p>
                </div>
              </div>
              <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 flex items-center gap-4">
                <div className="p-3 bg-blue-200/50 rounded-lg text-blue-700"><Calendar className="w-5 h-5" /></div>
                <div>
                  <p className="text-sm font-medium text-blue-800">En Planification</p>
                  <p className="text-2xl font-bold text-blue-900">{stats.planifie}</p>
                </div>
              </div>
              <div className="bg-amber-50 border border-amber-100 rounded-xl p-4 flex items-center gap-4">
                <div className="p-3 bg-amber-200/50 rounded-lg text-amber-700"><Truck className="w-5 h-5" /></div>
                <div>
                  <p className="text-sm font-medium text-amber-800">En Route</p>
                  <p className="text-2xl font-bold text-amber-900">{stats.enRoute}</p>
                </div>
              </div>
              <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-4 flex items-center gap-4">
                <div className="p-3 bg-emerald-200/50 rounded-lg text-emerald-700"><TrendingUp className="w-5 h-5" /></div>
                <div>
                  <p className="text-sm font-medium text-emerald-800">Livrées</p>
                  <p className="text-2xl font-bold text-emerald-900">{stats.livre}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Kanban Board */}
        <div className="flex-1 overflow-x-auto p-6">
          {loading ? (
            <div className="flex gap-6 max-w-[1600px] mx-auto h-full">
              <CardSkeletonLoader /><CardSkeletonLoader /><CardSkeletonLoader />
            </div>
          ) : (
            <div className="flex gap-6 max-w-[1600px] mx-auto h-full">
              {renderKanbanColumn('À Planifier (Garde-Fou)', 'bg-slate-400', ['BROUILLON', 'EN_ATTENTE_AFFECTATION'])}
              {renderKanbanColumn('Planifié & Validé', 'bg-blue-500', ['PLANIFIE'])}
              {renderKanbanColumn('En Cours d\'Exécution', 'bg-amber-500', ['EN_CHARGEMENT', 'EN_ROUTE'])}
              {renderKanbanColumn('Clôturé / Livré', 'bg-emerald-500', ['LIVRE', 'TERMINEE', 'FACTUREE'])}
            </div>
          )}
        </div>
        
      </div>
    </ModuleLayout>
  );
}
