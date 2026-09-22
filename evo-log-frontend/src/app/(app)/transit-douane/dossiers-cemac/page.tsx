'use client';

import React, { useState } from 'react';
import {
  Globe, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Archive, MapPin, Truck, Shield
} from 'lucide-react';
import { toast } from 'sonner';

interface TransitFolder {
  id: string;
  folderNumber: string;
  importer: string;
  countryDestination: string;
  corridorAxis: string;
  escortRequired: boolean;
  cautionDepositXaf: number;
  startDate: string;
  status: 'OUVERT' | 'EN_ROUTE_CEMAC' | 'ARRIVE_DESTINATION' | 'APURE_ARCHIVE';
}

const FOLDERS_DATA: TransitFolder[] = [];

export default function TransitDouaneDossiersCemac() {
  const [folders] = useState<TransitFolder[]>(FOLDERS_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = folders.filter(f =>
    f.folderNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
    f.importer.toLowerCase().includes(searchQuery.toLowerCase()) ||
    f.corridorAxis.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-cyan-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              Transit International Terrestre
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KDOU_COR
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Archive className="w-8 h-8 text-cyan-400" />
            Dossiers de Transit Corridors CEMAC
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Gestion des opérations de transit vers l hinterland (Tchad, RCA), cautionnements bancaires et apurement en douane.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Ouverture d un nouveau dossier de transit CEMAC')}
            className="px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-teal-500 text-white font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-cyan-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Nouveau Dossier CEMAC
          </button>
        </div>
      </div>

      {/* Table Dossiers CEMAC */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">N° Dossier Transit</th>
                <th className="py-3.5 px-4">Destinataire & Pays</th>
                <th className="py-3.5 px-4">Corridor & Itinéraire</th>
                <th className="py-3.5 px-4 text-center">Escorte Douane</th>
                <th className="py-3.5 px-4 text-right">Caution en Douane</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(f => (
                <tr key={f.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-cyan-400">{f.folderNumber}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-sans font-bold text-slate-100">{f.importer}</div>
                    <div className="text-[11px] text-slate-400 font-sans">{f.countryDestination}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-300 max-w-[280px]">{f.corridorAxis}</td>
                  <td className="py-3.5 px-4 text-center">
                    {f.escortRequired ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/10 text-red-400 border border-red-500/20">
                        🛡️ Requise
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400">
                        Non
                      </span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-right font-bold text-amber-400">{f.cautionDepositXaf.toLocaleString()} XAF</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      f.status === 'APURE_ARCHIVE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      f.status === 'EN_ROUTE_CEMAC' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {f.status}
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