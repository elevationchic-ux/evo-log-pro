'use client';

import React, { useState } from 'react';
import {
  ArrowDownLeft, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Container, MapPin, Calendar, Clock, Barcode
} from 'lucide-react';
import { toast } from 'sonner';

interface ReceptionItem {
  id: string;
  blNumber: string;
  containerNumber: string;
  shipper: string;
  cargoType: string;
  palletsCount: number;
  weightKg: number;
  arrivalDate: string;
  allocatedLocation: string;
  status: 'RECEPTIONNE' | 'EN_DECHARGEMENT' | 'ATTENTE_QUAI';
}

const RECEPTIONS: ReceptionItem[] = [
  { id: '1', blNumber: 'BL-2026-0881', containerNumber: 'MSCU8492019', shipper: 'TOTAL Energies Lubrifiants', cargoType: 'Fûts Huile Moteur 15W40', palletsCount: 40, weightKg: 18500, arrivalDate: '27/08/2026 08:30', allocatedLocation: 'Allée B - Racks 01 à 04', status: 'RECEPTIONNE' },
  { id: '2', blNumber: 'BL-2026-0880', containerNumber: 'CMAU1029384', shipper: 'Michelin Export France', cargoType: 'Pneumatiques Poids Lourds', palletsCount: 24, weightKg: 12000, arrivalDate: '27/08/2026 10:15', allocatedLocation: 'Allée D - Racks 01 à 02', status: 'EN_DECHARGEMENT' },
  { id: '3', blNumber: 'BL-2026-0879', containerNumber: 'SUDU9920192', shipper: 'Caterpillar Spare Parts', cargoType: 'Pièces de Rechange Engins', palletsCount: 16, weightKg: 8500, arrivalDate: '26/08/2026 14:00', allocatedLocation: 'Allée A - Bacs 10 à 15', status: 'RECEPTIONNE' },
];

export default function MagasinStockReception() {
  const [receptions, setReceptions] = useState<ReceptionItem[]>(RECEPTIONS);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = receptions.filter(r =>
    r.blNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.containerNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.shipper.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
              Quai de Réception MAG3 & Dépotage
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KMAG_RCP
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <ArrowDownLeft className="w-8 h-8 text-amber-400" />
            Réception Quai & Dépotage Conteneurs
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Enregistrement des entrées portuaires, contrôle de conformité BL/Manifeste, étiquetage codes-barres.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Ouverture de la session de scannage codes-barres réception')}
            className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/25 transition-all cursor-pointer"
          >
            <Barcode className="w-4 h-4" /> Scanner Entrée Quai
          </button>
        </div>
      </div>

      {/* Table Réceptions */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par n° BL, conteneur ou chargeur..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">N° BL / Document</th>
                <th className="py-3.5 px-4">Conteneur & Chargeur</th>
                <th className="py-3.5 px-4">Marchandise</th>
                <th className="py-3.5 px-4 text-center">Palettes</th>
                <th className="py-3.5 px-4 text-right">Poids Net</th>
                <th className="py-3.5 px-4">Emplacement Assigné</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(r => (
                <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-amber-400">{r.blNumber}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-slate-100">{r.containerNumber}</div>
                    <div className="text-[11px] text-slate-400 font-sans">{r.shipper}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{r.cargoType}</td>
                  <td className="py-3.5 px-4 text-center font-bold text-slate-200">{r.palletsCount} pal.</td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-200">{r.weightKg.toLocaleString()} kg</td>
                  <td className="py-3.5 px-4 text-amber-300 font-sans font-medium">{r.allocatedLocation}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      r.status === 'RECEPTIONNE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      r.status === 'EN_DECHARGEMENT' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {r.status === 'RECEPTIONNE' ? 'Stocké' : 'Déchargement'}
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
