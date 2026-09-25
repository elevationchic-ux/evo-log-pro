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
      
      // MissionStatus (enum reel, minuscules, sans accent) : planifiee | en_cours |
      // terminee | annulee | en_retard. Les comparaisons en majuscules ('PLANIFIE',
      // 'EN_ROUTE', 'LIVRE'...) ne reussissaient jamais : les trois KPI etaient
      // figes a 0 quel que soit le contenu de la base.
      setStats({
        total: data.length,
        planifie: data.filter((m: any) => m.statut === 'planifiee').length,
        enRoute: data.filter((m: any) => m.statut === 'en_cours').length,
        livre: data.filter((m: any) => m.statut === 'terminee').length
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
      <div className="flex-1 min-w-[320px] max-w-sm bg-slate-800/50 rounded-2xl border border-slate-700 p-4 flex flex-col max-h-[800px]">
        <div className="flex items-center justify-between mb-4 px-2">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${color}`} />
            <h3 className="font-bold text-slate-200">{title}</h3>
          </div>
          <span className="bg-slate-700 text-slate-400 text-xs font-bold px-2 py-1 rounded-full">
            {colMissions.length}
          </span>
        </div>
        
        <div className="flex-1 overflow-y-auto pr-2 space-y-4 pb-4">
          {colMissions.length === 0 ? (
            <div className="h-24 border-2 border-dashed border-slate-700 rounded-xl flex items-center justify-center text-sm text-slate-400">
              Aucun dossier
            </div>
          ) : (
            colMissions.map((mission) => (
              <div 
                key={mission.id} 
                className="bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-700 hover:shadow-md transition-shadow cursor-grab active:cursor-grabbing group"
              >
                <div className="flex justify-between items-start mb-3">
                  <span className="text-xs font-bold text-blue-600 bg-blue-500/10 px-2 py-1 rounded-md">
                    {mission.reference}
                  </span>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      onClick={() => window.open(`/transport/documents/bl/${mission.id}`, '_blank')}
                      className="p-1 hover:bg-slate-800 rounded text-slate-500 hover:text-blue-600 transition-colors"
                      title="Imprimer BL"
                    >
                      <Printer className="w-4 h-4" />
                    </button>
                    <GripVertical className="w-4 h-4 text-slate-300" />
                  </div>
                </div>
                
                {/* `nature_fret` n'existe pas dans MissionResponse : l'appel `.replace()`
                    sur undefined levait une TypeError qui vidait toute la page.
                    Le champ reel est `type_mission`. */}
                <h4 className="text-sm font-semibold text-slate-200 mb-1 line-clamp-1">
                  {(mission.type_mission || '').replace(/_/g, ' ') || 'Mission'}
                </h4>
                
                <div className="space-y-2 mt-3">
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    {/* MissionResponse (schemas/transport.py) expose point_depart /
                        point_arrivee, pas origine / destination. */}
                    <span className="truncate">{mission.point_depart} → {mission.point_arrivee}</span>
                  </div>
                  
                  {mission.date_debut_prevue && (
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      <span>{format(new Date(mission.date_debut_prevue), 'dd MMM yyyy', { locale: fr })}</span>
                    </div>
                  )}
                  
                  <div className="pt-2 mt-2 border-t border-slate-700 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1 font-medium text-slate-300">
                      <Truck className="w-3.5 h-3.5 text-indigo-500" />
                      Tracteur assigné
                    </div>
                    {mission.camion_id ? (
                      <span className="text-emerald-600 bg-emerald-500/10 px-1.5 py-0.5 rounded font-bold text-[10px]">OK</span>
                    ) : (
                      <span className="text-red-600 bg-red-500/10 px-1.5 py-0.5 rounded font-bold text-[10px]">À FAIRE</span>
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
      <div className="h-full flex flex-col animate-in fade-in duration-500 bg-slate-900">
        
        {/* Header & KPIs */}
        <div className="bg-slate-900 border-b border-slate-700 px-6 py-6 shrink-0">
          <div className="max-w-[1600px] mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
              <div>
                <h1 className="text-2xl font-bold text-slate-200 flex items-center gap-3">
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
                    className="pl-9 pr-4 py-2 border border-slate-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  />
                </div>
                <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-sm">
                  Planifier / Dispatcher
                </button>
              </div>
            </div>

            {/* KPI Cards Mini */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 flex items-center gap-4">
                <div className="p-3 bg-slate-700/50 rounded-lg text-slate-400"><Map className="w-5 h-5" /></div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Total Missions</p>
                  <p className="text-2xl font-bold text-slate-200">{stats.total}</p>
                </div>
              </div>
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 flex items-center gap-4">
                <div className="p-3 bg-blue-200/50 rounded-lg text-blue-300"><Calendar className="w-5 h-5" /></div>
                <div>
                  <p className="text-sm font-medium text-blue-300">En Planification</p>
                  <p className="text-2xl font-bold text-blue-200">{stats.planifie}</p>
                </div>
              </div>
              <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 flex items-center gap-4">
                <div className="p-3 bg-amber-200/50 rounded-lg text-amber-300"><Truck className="w-5 h-5" /></div>
                <div>
                  <p className="text-sm font-medium text-amber-300">En Route</p>
                  <p className="text-2xl font-bold text-amber-200">{stats.enRoute}</p>
                </div>
              </div>
              <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 flex items-center gap-4">
                <div className="p-3 bg-emerald-200/50 rounded-lg text-emerald-300"><TrendingUp className="w-5 h-5" /></div>
                <div>
                  <p className="text-sm font-medium text-emerald-300">Livrées</p>
                  <p className="text-2xl font-bold text-emerald-200">{stats.livre}</p>
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
              {/* Colonnes branchees sur les vrais MissionStatus. Les libelles
                  precedents ('BROUILLON', 'EN_ATTENTE_AFFECTATION', 'EN_CHARGEMENT',
                  'LIVRE', 'FACTUREE') ne correspondent a aucune valeur de l'enum :
                  les quatre colonnes etaient systematiquement vides. */}
              {renderKanbanColumn('Planifié & Validé', 'bg-blue-500', ['planifiee'])}
              {renderKanbanColumn('En Cours d\'Exécution', 'bg-amber-500', ['en_cours'])}
              {renderKanbanColumn('Clôturé / Terminé', 'bg-emerald-500', ['terminee'])}
              {renderKanbanColumn('Annulé / En retard', 'bg-red-500', ['annulee', 'en_retard'])}
            </div>
          )}
        </div>
        
      </div>
    </ModuleLayout>
  );
}
