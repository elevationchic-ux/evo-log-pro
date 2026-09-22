'use client';

import React, { useState } from 'react';
import {
  Users, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Phone, Mail, FileBadge, Calendar, Building
} from 'lucide-react';
import { toast } from 'sonner';

interface Employee {
  id: string;
  matricule: string;
  fullName: string;
  department: string;
  position: string;
  contractType: 'CDI' | 'CDD' | 'STAGE' | 'PRESTATAIRE';
  entryDate: string;
  phone: string;
  medicalVisitExpiry: string;
  status: 'ACTIF' | 'CONGE' | 'SUSPENDU';
}

const EMPLOYEES_DATA: Employee[] = [];

export default function RhPersonnelEmployees() {
  const [employees, setEmployees] = useState<Employee[]>(EMPLOYEES_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = employees.filter(e =>
    e.fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    e.matricule.toLowerCase().includes(searchQuery.toLowerCase()) ||
    e.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
    e.position.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-pink-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Gestion Administrative du Personnel
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KRH_EMP
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Users className="w-8 h-8 text-pink-400" />
            Fiches Collaborateurs & Contrats
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Dossiers individuels, contrats de travail, suivi des visites médicales et gestion des affectations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Ouverture du formulaire d enregistrement d un collaborateur')}
            className="px-4 py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-pink-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Nouveau Collaborateur
          </button>
        </div>
      </div>

      {/* Table Collaborateurs */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par nom, matricule, département..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pink-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Matricule & Nom</th>
                <th className="py-3.5 px-4">Département & Poste</th>
                <th className="py-3.5 px-4">Type Contrat</th>
                <th className="py-3.5 px-4">Date d Embauche</th>
                <th className="py-3.5 px-4">Contact</th>
                <th className="py-3.5 px-4">Visite Médicale</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(e => (
                <tr key={e.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-pink-400">{e.matricule}</div>
                    <div className="font-sans text-slate-100 font-bold text-sm">{e.fullName}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans">
                    <div className="text-slate-100 font-medium">{e.position}</div>
                    <div className="text-[11px] text-slate-400 font-mono">{e.department}</div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 border border-slate-700 text-slate-300">
                      {e.contractType}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-300">{e.entryDate}</td>
                  <td className="py-3.5 px-4 text-slate-300">{e.phone}</td>
                  <td className="py-3.5 px-4 text-slate-300">{e.medicalVisitExpiry}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      e.status === 'ACTIF' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {e.status}
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
