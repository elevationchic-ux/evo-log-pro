'use client';

import React, { useState } from 'react';
import {
  Users, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Phone, Award, Clock, ShieldCheck, FileBadge
} from 'lucide-react';
import { toast } from 'sonner';

interface Driver {
  id: string;
  matricule: string;
  name: string;
  phone: string;
  licenseNumber: string;
  licenseCategory: string;
  licenseExpiry: string;
  medicalCheckExpiry: string;
  drivingHoursWeekly: number;
  status: 'DISPONIBLE' | 'EN_MISSION' | 'REPOS_OBLIGATOIRE' | 'CONGE';
  scoreSecurite: number;
}

const DRIVERS_DATA: Driver[] = [
  { id: '1', matricule: 'DRV-001', name: 'Oumarou Bouba', phone: '+237 699 11 22 33', licenseNumber: 'PC-2018-84920', licenseCategory: 'Poids Lourd (E/C)', licenseExpiry: '15/12/2027', medicalCheckExpiry: '10/11/2026', drivingHoursWeekly: 38, status: 'EN_MISSION', scoreSecurite: 98 },
  { id: '2', matricule: 'DRV-002', name: 'Jean-Pierre Ndongo', phone: '+237 677 44 55 66', licenseNumber: 'PC-2019-10293', licenseCategory: 'Poids Lourd (E/C)', licenseExpiry: '20/06/2028', medicalCheckExpiry: '05/01/2027', drivingHoursWeekly: 42, status: 'EN_MISSION', scoreSecurite: 94 },
  { id: '3', matricule: 'DRV-003', name: 'Eric Fotso', phone: '+237 694 77 88 99', licenseNumber: 'PC-2020-55481', licenseCategory: 'Poids Lourd (E/C)', licenseExpiry: '08/09/2026', medicalCheckExpiry: '12/09/2026', drivingHoursWeekly: 48, status: 'REPOS_OBLIGATOIRE', scoreSecurite: 89 },
  { id: '4', matricule: 'DRV-004', name: 'Aliou Mohamadou', phone: '+237 655 00 33 22', licenseNumber: 'PC-2021-99201', licenseCategory: 'Poids Lourd (E/C)', licenseExpiry: '30/03/2029', medicalCheckExpiry: '18/04/2027', drivingHoursWeekly: 12, status: 'DISPONIBLE', scoreSecurite: 96 },
];

export default function TransportFlotteDrivers() {
  const [drivers, setDrivers] = useState<Driver[]>(DRIVERS_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = drivers.filter(d =>
    d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.matricule.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.phone.includes(searchQuery)
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-blue-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-blue-500/20 text-blue-300 border border-blue-500/30">
              Gestion du Capital Humain Routier
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KTRN_DRV
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Users className="w-8 h-8 text-blue-400" />
            Gestion des Chauffeurs & Temps de Repos
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Suivi des permis CEMAC, aptitudes médicales, conformité temps de conduite/repos et éco-conduite.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Formulaire d enregistrement d un nouveau chauffeur')}
            className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-blue-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Nouveau Chauffeur
          </button>
        </div>
      </div>

      {/* Table Chauffeurs */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par nom, matricule, téléphone..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Matricule & Nom</th>
                <th className="py-3.5 px-4">Contact</th>
                <th className="py-3.5 px-4">Permis CEMAC</th>
                <th className="py-3.5 px-4">Visite Médicale</th>
                <th className="py-3.5 px-4 text-center">Heures Conduite Hebdo</th>
                <th className="py-3.5 px-4 text-center">Score Sécurité</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(d => (
                <tr key={d.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-blue-400">{d.matricule}</div>
                    <div className="font-sans text-slate-100 font-bold text-sm">{d.name}</div>
                  </td>
                  <td className="py-3.5 px-4 text-slate-300">{d.phone}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-slate-200">{d.licenseCategory}</div>
                    <div className="text-[11px] text-slate-400">Exp: {d.licenseExpiry}</div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="text-slate-300 font-sans">{d.medicalCheckExpiry}</span>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`font-bold ${d.drivingHoursWeekly > 45 ? 'text-red-400' : 'text-slate-200'}`}>
                      {d.drivingHoursWeekly} h / 45 h max
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center font-bold text-emerald-400">
                    {d.scoreSecurite}/100
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      d.status === 'DISPONIBLE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      d.status === 'EN_MISSION' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {d.status}
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
