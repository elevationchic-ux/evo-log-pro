'use client';

import React, { useState } from 'react';
import {
  Banknote, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Calculator, FileText, Send, Printer
} from 'lucide-react';
import { toast } from 'sonner';

interface PayrollRecord {
  id: string;
  matricule: string;
  employeeName: string;
  position: string;
  baseSalary: number;
  overtimeAmount: number;
  allowances: number;
  grossSalary: number;
  cnpsDeduction: number;
  irgmTax: number;
  netPayable: number;
  status: 'CALCULE' | 'VALIDE' | 'PAYE';
}

const PAYROLL_DATA: PayrollRecord[] = [
  { id: '1', matricule: 'EMP-001', employeeName: 'Oumarou Bouba', position: 'Chauffeur Poids Lourd Corridor', baseSalary: 350000, overtimeAmount: 45000, allowances: 50000, grossSalary: 445000, cnpsDeduction: 18690, irgmTax: 49000, netPayable: 377310, status: 'VALIDE' },
  { id: '2', matricule: 'EMP-002', employeeName: 'Moïse Talla', position: 'Cariste Senior MAG3', baseSalary: 280000, overtimeAmount: 22000, allowances: 30000, grossSalary: 332000, cnpsDeduction: 13944, irgmTax: 26400, netPayable: 291656, status: 'VALIDE' },
  { id: '3', matricule: 'EMP-003', employeeName: 'Marie Essomba', position: 'Expert Comptable OHADA', baseSalary: 850000, overtimeAmount: 0, allowances: 150000, grossSalary: 1000000, cnpsDeduction: 42000, irgmTax: 205000, netPayable: 753000, status: 'PAYE' },
  { id: '4', matricule: 'EMP-004', employeeName: 'Samuel Eto', position: 'Responsable Quai & Dépotage', baseSalary: 420000, overtimeAmount: 35000, allowances: 60000, grossSalary: 515000, cnpsDeduction: 21630, irgmTax: 63000, netPayable: 430370, status: 'CALCULE' },
];

export default function RhPersonnelPayrollOhada() {
  const [payrolls, setPayrolls] = useState<PayrollRecord[]>(PAYROLL_DATA);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMonth, setSelectedMonth] = useState('2026-08');

  const filtered = payrolls.filter(p =>
    p.employeeName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.matricule.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.position.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalNet = payrolls.reduce((acc, curr) => acc + curr.netPayable, 0);
  const totalCnps = payrolls.reduce((acc, curr) => acc + curr.cnpsDeduction, 0);
  const totalIrgm = payrolls.reduce((acc, curr) => acc + curr.irgmTax, 0);

  const handleValidatePayroll = () => {
    toast.success('Paie du mois validée. Ordres de virement bancaires et Mobile Money générés.');
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-pink-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Livre de Paie & Fiscalité Cameroun
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KRH_PAY
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Banknote className="w-8 h-8 text-pink-400" />
            Livre de Paie OHADA & Bulletins de Salaire
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Calcul légal des salaires, retenues CNPS (4.2%), barème progressif IRGM Cameroun, Crédit Foncier et FNE.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleValidatePayroll}
            className="px-4 py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-pink-500/25 transition-all cursor-pointer"
          >
            <CheckCircle2 className="w-4 h-4" /> Valider & Clôturer Paie
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Total Net à Payer (XAF)</div>
          <div className="text-2xl font-black text-emerald-400 font-mono">
            {totalNet.toLocaleString()} <span className="text-xs font-normal text-slate-400">XAF</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-2">Virements Afriland / SGC / MoMo</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Cotisations CNPS Salariales (4.2%)</div>
          <div className="text-2xl font-black text-pink-400 font-mono">
            {totalCnps.toLocaleString()} <span className="text-xs font-normal text-slate-400">XAF</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-2">À reverser à la CNPS Cameroun</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Retenues IRGM / Impôts</div>
          <div className="text-2xl font-black text-amber-400 font-mono">
            {totalIrgm.toLocaleString()} <span className="text-xs font-normal text-slate-400">XAF</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-2">Barème progressif DGI Cameroun</div>
        </div>
      </div>

      {/* Table Paie */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par employé, matricule ou poste..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pink-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Matricule & Collaborateur</th>
                <th className="py-3.5 px-4 text-right">Salaire Base</th>
                <th className="py-3.5 px-4 text-right">Heures Sup / Primes</th>
                <th className="py-3.5 px-4 text-right">Salaire Brut</th>
                <th className="py-3.5 px-4 text-right">CNPS (4.2%)</th>
                <th className="py-3.5 px-4 text-right">IRGM Impôt</th>
                <th className="py-3.5 px-4 text-right">Net à Payer</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
                <th className="py-3.5 px-4 text-center">Bulletin</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(p => (
                <tr key={p.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-pink-400">{p.matricule}</div>
                    <div className="font-sans text-slate-100 font-bold">{p.employeeName}</div>
                    <div className="text-[11px] text-slate-400 font-sans">{p.position}</div>
                  </td>
                  <td className="py-3.5 px-4 text-right text-slate-200">{p.baseSalary.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-right text-slate-300">
                    {(p.overtimeAmount + p.allowances).toLocaleString()}
                  </td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-100">{p.grossSalary.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-right text-pink-400">-{p.cnpsDeduction.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-right text-amber-400">-{p.irgmTax.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-right font-black text-emerald-400 text-sm">
                    {p.netPayable.toLocaleString()} XAF
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      p.status === 'PAYE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      p.status === 'VALIDE' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {p.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <button
                      onClick={() => toast.success(`Impression bulletin de paie OHADA de ${p.employeeName}`)}
                      className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg mx-auto"
                      title="Imprimer Bulletin"
                    >
                      <Printer className="w-3.5 h-3.5" />
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
