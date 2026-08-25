'use client';

import React, { useState, useEffect, useCallback } from 'react';
import ModuleLayout from '@/components/layout/ModuleLayout';
import { Map, Navigation, Settings2, RefreshCw, Box } from 'lucide-react';
import { useComingSoon } from '@/contexts/ComingSoonContext';
import { parcAPI } from '@/lib/api-client';

// Simple placeholder for Map
const MapPlaceholder = () => (
  <div className="w-full h-[600px] bg-slate-100 rounded-2xl flex items-center justify-center text-slate-400">
    <div className="text-center">
      <Map className="w-16 h-16 mx-auto mb-4" />
      <p className="text-sm font-semibold">Carte de la Cour - En développement</p>
    </div>
  </div>
);

export default function YardMapPage() {
  const [points, setPoints] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const { showComingSoon } = useComingSoon();

  const fetchYardPositions = useCallback(async () => {
    setRefreshing(true);
    try {
      const [emplacements, stocks] = await Promise.all([
        parcAPI.getEmplacements(),
        parcAPI.getStocksActifs()
      ]);
      const emplacementsData = emplacements.data || [];
      const stocksData = stocks.data || [];
      
      const mapPoints = stocksData.map((stock: any) => {
        const emp = emplacementsData.find((e: any) => e.id === stock.emplacement_id);
        if (!emp) return null;
        return {
          id: stock.numero_conteneur,
          label: `${stock.type_conteneur} - ${emp.code_emplacement}`,
          position: [emp.coordonnee_x || 4.0511 + (((emp.id || 0) % 100) - 50) * 0.0001, emp.coordonnee_y || 9.7679 + (Math.floor((emp.id || 0) / 100) % 100 - 50) * 0.0001], // fallback coords if missing
          status: stock.statut
        };
      }).filter(Boolean);
      
      setPoints(mapPoints);
    } catch (error) {
      console.error(error);
      console.log('Erreur lors du chargement de la cour');
    } finally {
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchYardPositions();
  }, [fetchYardPositions]);

  return (
    <ModuleLayout module="parc">
      <div className="max-w-[1600px] mx-auto py-8 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500 flex flex-col h-[calc(100vh-80px)]">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-6 gap-4 shrink-0">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
              <Map className="w-8 h-8 text-amber-600" />
              Vue de la Cour (Yard Management)
            </h1>
            <p className="text-sm text-slate-500 mt-2">Vue satellite des emplacements et conteneurs sur la cour.</p>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={fetchYardPositions}
              disabled={refreshing}
              className="bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 px-4 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 shadow-sm transition-all"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-amber-600' : ''}`} />
              Actualiser Cour
            </button>
            <button 
              onClick={() => showComingSoon('Configuration Zones')}
              className="bg-slate-800 hover:bg-slate-900 text-white px-4 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 shadow-sm transition-all"
            >
              <Settings2 className="w-4 h-4" />
              Configuration Zones
            </button>
          </div>
        </div>

        {/* Map Container */}
        <div className="flex-1 bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden flex flex-col relative">
          
          {/* Overlay Panel */}
          <div className="absolute top-4 left-4 z-[400] w-80 bg-white/95 backdrop-blur-md border border-slate-200 shadow-xl rounded-2xl overflow-hidden flex flex-col max-h-[80%]">
            <div className="p-4 border-b border-slate-100 bg-slate-50">
              <h3 className="font-bold text-slate-800 flex items-center gap-2">
                <Box className="w-5 h-5 text-amber-600" />
                Conteneurs sur site
              </h3>
            </div>
            <div className="p-2 flex-1 overflow-y-auto custom-scrollbar">
              {points.map((pt, i) => (
                <div key={i} className="flex items-center gap-3 p-3 hover:bg-slate-50 rounded-xl cursor-pointer transition-colors border-b border-slate-50 last:border-0">
                  <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center shrink-0">
                    <Box className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-800">{pt.id}</h4>
                    <p className="text-xs text-slate-500 truncate w-44">{pt.label}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="w-full h-full">
            <MapPlaceholder />
          </div>
        </div>

      </div>
    </ModuleLayout>
  );
}
