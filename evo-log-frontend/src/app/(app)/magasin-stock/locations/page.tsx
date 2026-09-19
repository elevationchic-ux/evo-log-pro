'use client';

import React, { useState } from 'react';
import {
  MapPin, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Grid, Layers, Box
} from 'lucide-react';
import { toast } from 'sonner';

interface LocationRack {
  id: string;
  zone: string;
  aisle: string;
  rack: string;
  level: string;
  fullCode: string;
  capacityPallets: number;
  occupiedPallets: number;
  currentCargo: string;
  status: 'DISPONIBLE' | 'PARTIEL' | 'PLEIN' | 'BLOQUE';
}

const LOCATIONS_DATA: LocationRack[] = [
  { id: '1', zone: 'Zone A (Matières Dangereuses)', aisle: 'Allée A', rack: 'Rack 01', level: 'Niveau 1', fullCode: 'MAG3-A-01-N1', capacityPallets: 10, occupiedPallets: 10, currentCargo: 'Huiles & Lubrifiants TOTAL', status: 'PLEIN' },
  { id: '2', zone: 'Zone A (Matières Dangereuses)', aisle: 'Allée A', rack: 'Rack 02', level: 'Niveau 2', fullCode: 'MAG3-A-02-N2', capacityPallets: 10, occupiedPallets: 4, currentCargo: 'Batteries Poids Lourds', status: 'PARTIEL' },
  { id: '3', zone: 'Zone B (Marchandises Générales)', aisle: 'Allée B', rack: 'Rack 01', level: 'Niveau 1', fullCode: 'MAG3-B-01-N1', capacityPallets: 15, occupiedPallets: 0, currentCargo: 'Aucun (Emplacement Libre)', status: 'DISPONIBLE' },
  { id: '4', zone: 'Zone C (Froid & Contrôlé)', aisle: 'Allée C', rack: 'Rack 04', level: 'Niveau 3', fullCode: 'MAG3-C-04-N3', capacityPallets: 8, occupiedPallets: 8, currentCargo: 'Produits Brasserie SABC', status: 'PLEIN' },
];

export default function MagasinStockLocations() {
  const [locations, setLocations] = useState<LocationRack[]>(LOCATIONS_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = locations.filter(l =>
    l.fullCode.toLowerCase().includes(searchQuery.toLowerCase()) ||
    l.zone.toLowerCase().includes(searchQuery.toLowerCase()) ||
    l.currentCargo.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
              Cartographie & Slotting WMS
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KMAG_SLT
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <MapPin className="w-8 h-8 text-amber-400" />
            Emplacements & Cartographie MAG3
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Visualisation 2D/3D des allées, racks, niveaux de stockage et optimisation des trajets de caristes.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Ajout d une nouvelle travée de racks dans l entrepôt')}
            className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Créer Emplacement
          </button>
        </div>
      </div>

      {/* Table Emplacements */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par code emplacement, allée ou contenu..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Code Emplacement</th>
                <th className="py-3.5 px-4">Zone & Allée</th>
                <th className="py-3.5 px-4">Marchandise Stockée</th>
                <th className="py-3.5 px-4 text-center">Occupation</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(l => (
                <tr key={l.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-amber-400 text-sm">{l.fullCode}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-sans font-semibold text-slate-100">{l.zone}</div>
                    <div className="text-[11px] text-slate-400 font-mono">{l.aisle} • {l.rack} • {l.level}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{l.currentCargo}</td>
                  <td className="py-3.5 px-4 text-center font-bold text-slate-200">
                    {l.occupiedPallets} / {l.capacityPallets} pal.
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      l.status === 'DISPONIBLE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      l.status === 'PARTIEL' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                      l.status === 'PLEIN' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                      'bg-red-500/10 text-red-400 border border-red-500/20'
                    }`}>
                      {l.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
