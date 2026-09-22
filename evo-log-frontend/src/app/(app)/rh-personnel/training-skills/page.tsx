'use client';

import React, { useState } from 'react';
import {
  Award, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, ShieldCheck, BookOpen, GraduationCap, Calendar
} from 'lucide-react';
import { toast } from 'sonner';

interface CertificationSkill {
  id: string;
  employeeName: string;
  matricule: string;
  certificationName: string;
  category: 'CACES_CARISTE' | 'ISPS_PORTUAIRE' | 'MATIERES_DANGEREUSES' | 'SECOURISME' | 'ECO_CONDUITE';
  issueDate: string;
  expiryDate: string;
  issuingBody: string;
  status: 'VALIDE' | 'EXPIRE_BIENTOT' | 'EXPIRE';
}

const SKILLS_DATA: CertificationSkill[] = [
  { id: '1', employeeName: 'Moïse Talla', matricule: 'EMP-002', certificationName: 'CACES R489 Catégorie 3 & 4 (Chariots Élévateurs)', category: 'CACES_CARISTE', issueDate: '10/05/2023', expiryDate: '10/05/2028', issuingBody: 'APAVE Cameroun', status: 'VALIDE' },
  { id: '2', employeeName: 'Oumarou Bouba', matricule: 'EMP-001', certificationName: 'Certificat Transport Matières Dangereuses (ADR/CEMAC)', category: 'MATIERES_DANGEREUSES', issueDate: '15/09/2024', expiryDate: '15/09/2026', issuingBody: 'Ministère des Transports Cameroun', status: 'EXPIRE_BIENTOT' },
  { id: '3', employeeName: 'Samuel Eto', matricule: 'EMP-004', certificationName: 'Sûreté Portuaire & Code ISPS Niveau 2', category: 'ISPS_PORTUAIRE', issueDate: '01/12/2023', expiryDate: '01/12/2026', issuingBody: 'Port Autonome de Douala (PAD)', status: 'VALIDE' },
  { id: '4', employeeName: 'Eric Fotso', matricule: 'EMP-007', certificationName: 'Éco-Conduite & Sécurité Routière PL', category: 'ECO_CONDUITE', issueDate: '20/01/2024', expiryDate: '20/01/2027', issuingBody: 'TotalEnergies Academy', status: 'VALIDE' },
];

export default function RhPersonnelTrainingSkills() {
  const [skills] = useState<CertificationSkill[]>(SKILLS_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = skills.filter(s =>
    s.employeeName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.certificationName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.issuingBody.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-pink-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Habilitations & Compétences Portuaires
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KRH_TRN
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Award className="w-8 h-8 text-pink-400" />
            Certifications, CACES & Formations ISPS
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Suivi des validités des permis caristes CACES, habilitations sûreté portuaire PAD et formations réglementaires.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Enregistrement d une nouvelle certification')}
            className="px-4 py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-pink-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Ajouter Habilitation
          </button>
        </div>
      </div>

      {/* Table Habilitations */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher collaborateur, certification, organisme..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pink-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Collaborateur</th>
                <th className="py-3.5 px-4">Certification & Habilitation</th>
                <th className="py-3.5 px-4">Organisme Émetteur</th>
                <th className="py-3.5 px-4">Date Délivrance</th>
                <th className="py-3.5 px-4">Date Expiration</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(s => (
                <tr key={s.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-pink-400">{s.matricule}</div>
                    <div className="font-sans text-slate-100 font-bold">{s.employeeName}</div>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="font-sans font-bold text-slate-100">{s.certificationName}</div>
                    <div className="text-[11px] text-slate-400 font-mono">{s.category}</div>
                  </td>
                  <td className="py-3.5 px-4 text-slate-300 font-sans">{s.issuingBody}</td>
                  <td className="py-3.5 px-4 text-slate-400">{s.issueDate}</td>
                  <td className="py-3.5 px-4 font-bold text-slate-200">{s.expiryDate}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      s.status === 'VALIDE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse'
                    }`}>
                      {s.status === 'VALIDE' ? '✓ Valide' : '⚠️ Expire Bientôt'}
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
