'use client';

import React, { useState } from 'react';
import {
  Clock, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Calendar, UserCheck, Timer
} from 'lucide-react';
import { toast } from 'sonner';

interface AttendanceRecord {
  id: string;
  matricule: string;
  employeeName: string;
  department: string;
  date: string;
  checkIn: string;
  checkOut: string;
  hoursWorked: number;
  overtimeHours: number;
  status: 'PRESENT' | 'RETARD' | 'ABSENCE_JUSTIFIEE' | 'CONGE';
}

const ATTENDANCE_DATA: AttendanceRecord[] = [
  { id: '1', matricule: 'EMP-001', employeeName: 'Oumarou Bouba', department: 'Transport', date: '27/08/2026', checkIn: '06:00', checkOut: '15:30', hoursWorked: 9.5, overtimeHours: 1.5, status: 'PRESENT' },
  { id: '2', matricule: 'EMP-002', employeeName: 'Moïse Talla', department: 'Magasin WMS', date: '27/08/2026', checkIn: '07:45', checkOut: '17:00', hoursWorked: 9.25, overtimeHours: 1.25, status: 'PRESENT' },
  { id: '3', matricule: 'EMP-004', employeeName: 'Samuel Eto', department: 'Quai & Acconage', date: '27/08/2026', checkIn: '06:30', checkOut: '18:00', hoursWorked: 11.5, overtimeHours: 3.5, status: 'PRESENT' },
  { id: '4', matricule: 'EMP-005', employeeName: 'Béatrice Ngo', department: 'Transit Douane', date: '27/08/2026', checkIn: '08:30', checkOut: '17:00', hoursWorked: 8.0, overtimeHours: 0.0, status: 'PRESENT' },
];

export default function RhPersonnelTimeAttendance() {
  const [records] = useState<AttendanceRecord[]>(ATTENDANCE_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = records.filter(r =>
    r.employeeName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.matricule.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.department.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-pink-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Pointage & Temps de Travail
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KRH_ATT
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Clock className="w-8 h-8 text-pink-400" />
            Temps, Présences & Heures Supplémentaires
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Suivi des pointages biométriques quai/entrepôt, calcul des majorations d heures sup et gestion des shifts.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.success('Rapport d assiduité du jour exporté')}
            className="px-4 py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-pink-500/25 transition-all cursor-pointer"
          >
            <Download className="w-4 h-4" /> Rapport Pointage
          </button>
        </div>
      </div>

      {/* Table Pointages */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher collaborateur, matricule ou service..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pink-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Collaborateur</th>
                <th className="py-3.5 px-4">Département</th>
                <th className="py-3.5 px-4">Date</th>
                <th className="py-3.5 px-4 text-center">Pointage Entrée</th>
                <th className="py-3.5 px-4 text-center">Pointage Sortie</th>
                <th className="py-3.5 px-4 text-right">Heures Effectuées</th>
                <th className="py-3.5 px-4 text-right">Heures Sup (+25%/+50%)</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(r => (
                <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-pink-400">{r.matricule}</div>
                    <div className="font-sans text-slate-100 font-bold">{r.employeeName}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{r.department}</td>
                  <td className="py-3.5 px-4 text-slate-400">{r.date}</td>
                  <td className="py-3.5 px-4 text-center font-bold text-emerald-400">{r.checkIn}</td>
                  <td className="py-3.5 px-4 text-center font-bold text-blue-400">{r.checkOut}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-200">{r.hoursWorked} h</td>
                  <td className="py-3.5 px-4 text-right font-bold text-amber-400">
                    {r.overtimeHours > 0 ? `+${r.overtimeHours} h` : '-'}
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {r.status}
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
