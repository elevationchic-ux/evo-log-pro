'use client';

import React, { useState } from 'react';
import {
  FileCheck, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Building, Landmark, Calendar, Printer, FileSpreadsheet
} from 'lucide-react';
import { toast } from 'sonner';

interface SocialDeclaration {
  id: string;
  type: 'DIPE_MENSUEL' | 'DIPE_ANNUEL' | 'BORDEREAU_CNPS' | 'CREDIT_FONCIER' | 'FNE';
  period: string;
  grossBaseXaf: number;
  totalContributionXaf: number;
  submissionDeadline: string;
  filingStatus: 'TRANSMIS' | 'VALIDE' | 'A_TELETRANSMETTRE';
  referenceReceipt: string;
}

const DECLARATIONS_DATA: SocialDeclaration[] = [
  { id: '1', type: 'DIPE_MENSUEL', period: 'Août 2026', grossBaseXaf: 78450000, totalContributionXaf: 14200000, submissionDeadline: '15/09/2026', filingStatus: 'A_TELETRANSMETTRE', referenceReceipt: 'EN_ATTENTE' },
  { id: '2', type: 'BORDEREAU_CNPS', period: 'Août 2026', grossBaseXaf: 78450000, totalContributionXaf: 8786400, submissionDeadline: '15/09/2026', filingStatus: 'A_TELETRANSMETTRE', referenceReceipt: 'EN_ATTENTE' },
  { id: '3', type: 'DIPE_MENSUEL', period: 'Juillet 2026', grossBaseXaf: 76200000, totalContributionXaf: 13800000, submissionDeadline: '15/08/2026', filingStatus: 'VALIDE', referenceReceipt: 'DGI-DIPE-20260814-8849' },
  { id: '4', type: 'BORDEREAU_CNPS', period: 'Juillet 2026', grossBaseXaf: 76200000, totalContributionXaf: 8534400, submissionDeadline: '15/08/2026', filingStatus: 'VALIDE', referenceReceipt: 'CNPS-REC-20260812-1029' },
];

export default function RhPersonnelSocialDeclarations() {
  const [declarations] = useState<SocialDeclaration[]>(DECLARATIONS_DATA);

  const handleExportDIPE = () => {
    toast.success('Génération du fichier DIPE au format normalisé DGI Cameroun (EDI-DIPE XML/TXT)');
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-pink-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Conformité Fiscale & Sociale Cameroun
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KRH_DIP
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <FileCheck className="w-8 h-8 text-pink-400" />
            Déclarations Sociales & DIPE Cameroun
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Génération du Document d Information sur le Personnel Employé (DIPE), bordereaux de cotisations CNPS, Crédit Foncier et FNE.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExportDIPE}
            className="px-4 py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-pink-500/25 transition-all cursor-pointer"
          >
            <FileSpreadsheet className="w-4 h-4" /> Générer Fichier DIPE
          </button>
        </div>
      </div>

      {/* Table Déclarations */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Type de Déclaration</th>
                <th className="py-3.5 px-4">Période</th>
                <th className="py-3.5 px-4 text-right">Masse Salariale Brute</th>
                <th className="py-3.5 px-4 text-right">Montant Total à Reverser</th>
                <th className="py-3.5 px-4">Date Limite de Dépôt</th>
                <th className="py-3.5 px-4">N° Quittance / Récépissé</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
                <th className="py-3.5 px-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {declarations.map(d => (
                <tr key={d.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-pink-400">{d.type}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-200 font-bold">{d.period}</td>
                  <td className="py-3.5 px-4 text-right text-slate-300">{d.grossBaseXaf.toLocaleString()} XAF</td>
                  <td className="py-3.5 px-4 text-right font-bold text-emerald-400">{d.totalContributionXaf.toLocaleString()} XAF</td>
                  <td className="py-3.5 px-4 text-slate-400">{d.submissionDeadline}</td>
                  <td className="py-3.5 px-4 text-blue-400 font-bold">{d.referenceReceipt}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      d.filingStatus === 'VALIDE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {d.filingStatus}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <button
                      onClick={() => toast.success(`Téléchargement de l état ${d.type} ${d.period}`)}
                      className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg mx-auto"
                    >
                      <Download className="w-3.5 h-3.5" />
                    </button>
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
