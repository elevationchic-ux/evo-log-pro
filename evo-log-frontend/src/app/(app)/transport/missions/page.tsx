'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { transportAPI } from '@/lib/api-client';
import { Mission } from '@/types';
import { ModuleLayout } from '@/components/layout/ModuleLayout';
import { Truck, MapPin, Calendar, Package, Search, Filter, FilterX } from 'lucide-react';
import { CardSkeletonLoader } from '@/components/ui/Loaders';

export default function MissionsPage() {
  const [missions, setMissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters State
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');

  useEffect(() => {
    loadMissions();
  }, []);

  const loadMissions = async () => {
    try {
      const response = await transportAPI.getMissions();
      const d = response.data;
      const list = Array.isArray(d) ? d : (d?.items || (Array.isArray(response) ? response : []));
      setMissions(list);
    } catch (error) {
      console.error('Error loading missions:', error);
      setMissions([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatutColor = (statut: string) => {
    switch (statut) {
      case 'BROUILLON': return 'bg-slate-100 text-slate-800';
      case 'EN_ATTENTE_AFFECTATION': return 'bg-indigo-100 text-indigo-800';
      case 'EN_CHARGEMENT': return 'bg-blue-100 text-blue-800';
      case 'EN_ROUTE': return 'bg-amber-100 text-amber-800';
      case 'EN_LIVRAISON': return 'bg-orange-100 text-orange-800';
      case 'LIVRE':
      case 'TERMINEE': return 'bg-emerald-100 text-emerald-800';
      case 'FACTUREE': return 'bg-purple-100 text-purple-800';
      default: return 'bg-slate-100 text-slate-800';
    }
  };

  // Advanced Filtering Logic safely
  const filteredMissions = useMemo(() => {
    const safeList = Array.isArray(missions) ? missions : [];
    return safeList.filter(m => {
      // Search
      const searchStr = `${m.reference} ${m.origine} ${m.destination} ${m.nature_fret}`.toLowerCase();
      if (searchTerm && !searchStr.includes(searchTerm.toLowerCase())) return false;
      
      // Status
      if (statusFilter && m.statut !== statusFilter) return false;

      // Date
      if (dateFilter) {
        const mDate = new Date(m.date_creation || Date.now()).toISOString().split('T')[0];
        if (mDate !== dateFilter) return false;
      }

      return true;
    }).sort((a, b) => b.id - a.id);
  }, [missions, searchTerm, statusFilter, dateFilter]);

  const clearFilters = () => {
    setSearchTerm('');
    setStatusFilter('');
    setDateFilter('');
  };

  const activeFiltersCount = (searchTerm ? 1 : 0) + (statusFilter ? 1 : 0) + (dateFilter ? 1 : 0);

  return (
    <ModuleLayout module="transport">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500">
        
        {/* Header */}
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
              <Package className="w-8 h-8 text-blue-600" />
              Missions de Transport
            </h1>
            <p className="text-sm text-slate-500 mt-2">Suivi global, historique et recherche avancée des ordres de transport.</p>
          </div>
          <button onClick={() => window.location.href='/transport/dispatch'} className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 shadow-sm transition-all">
            <span className="material-symbols-outlined text-[20px]">add</span>
            Nouvel Ordre (Dispatch)
          </button>
        </div>

        {/* Filters Bar */}
        <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-200 mb-6 flex flex-col sm:flex-row gap-4 items-center">
          <div className="flex-1 w-full relative">
            <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input 
              type="text" 
              placeholder="Rechercher (Référence, Origine, Destination, Fret...)" 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm outline-none"
            />
          </div>
          <div className="flex gap-4 w-full sm:w-auto">
            <select 
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm outline-none"
            >
              <option value="">Tous les statuts</option>
              <option value="BROUILLON">Brouillon</option>
              <option value="EN_ATTENTE_AFFECTATION">En attente affectation</option>
              <option value="EN_ROUTE">En route</option>
              <option value="TERMINEE">Terminée</option>
              <option value="FACTUREE">Facturée</option>
            </select>
            <input 
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm outline-none"
            />
            {activeFiltersCount > 0 && (
              <button 
                onClick={clearFilters}
                className="px-4 py-2.5 rounded-xl bg-slate-100 text-slate-600 hover:bg-slate-200 text-sm font-bold flex items-center gap-2"
                title="Effacer les filtres"
              >
                <FilterX className="w-4 h-4" />
                <span className="hidden sm:inline">Effacer</span>
              </button>
            )}
          </div>
        </div>

        {/* Missions List */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-100 flex justify-between items-center">
            <h3 className="font-bold text-slate-800 flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400" />
              Résultats de recherche
            </h3>
            <span className="text-xs font-bold text-blue-600 bg-blue-100 px-2 py-1 rounded-full">{filteredMissions.length} Missions</span>
          </div>

          <table className="w-full text-left border-collapse">
            <thead className="bg-white border-b border-slate-100 text-xs uppercase font-bold text-slate-500">
              <tr>
                <th className="px-6 py-4">Référence</th>
                <th className="px-6 py-4">Trajet</th>
                <th className="px-6 py-4">Ressources</th>
                <th className="px-6 py-4">Fret</th>
                <th className="px-6 py-4">Statut</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr><td colSpan={5} className="px-6 py-12"><CardSkeletonLoader /></td></tr>
              ) : filteredMissions.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-16 text-center">
                    <Package className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                    <p className="text-slate-500 font-medium text-lg">Aucune mission ne correspond à vos filtres.</p>
                  </td>
                </tr>
              ) : filteredMissions.map((mission) => (
                <tr key={mission.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-black text-slate-900">{mission.reference}</div>
                    <div className="text-xs font-bold text-slate-400 flex items-center gap-1 mt-1">
                      <Calendar className="w-3.5 h-3.5" />
                      {new Date(mission.date_creation || Date.now()).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1.5 text-sm font-bold">
                      <div className="flex items-center gap-2 text-slate-700">
                        <MapPin className="w-4 h-4 text-emerald-600" /> {mission.origine}
                      </div>
                      <div className="flex items-center gap-2 text-slate-700">
                        <MapPin className="w-4 h-4 text-red-600" /> {mission.destination}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1 text-sm font-bold">
                      <div className="flex items-center gap-1.5 text-slate-700">
                        <Truck className="w-4 h-4 text-slate-400" /> 
                        {mission.camion?.immatriculation || `Camion ID ${mission.camion_id}`}
                      </div>
                      <div className="text-xs text-slate-500 ml-5.5">
                        {mission.chauffeur?.nom ? `${mission.chauffeur.nom} ${mission.chauffeur.prenom}` : `Chauffeur ID ${mission.chauffeur_id}`}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-bold text-slate-800">{mission.nature_fret}</div>
                    <div className="text-xs font-medium text-slate-500 mt-1">{mission.poids_kg} kg | {mission.volume_m3} m³</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${getStatutColor(mission.statut)}`}>
                      {mission.statut.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button 
                      onClick={() => window.open(`/transport/documents/bl/${mission.id}`, '_blank')}
                      className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg transition-colors flex items-center gap-1.5 ml-auto"
                      title="Imprimer le Bon de Livraison"
                    >
                      <span className="material-symbols-outlined text-[16px]">print</span>
                      BL
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </ModuleLayout>
  );
}
