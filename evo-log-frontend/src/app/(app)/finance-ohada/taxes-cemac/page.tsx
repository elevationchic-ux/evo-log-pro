'use client';

import React, { useState } from 'react';
import {
  ShieldCheck, Search, Filter, Download, Building,
  CheckCircle2, AlertTriangle, DollarSign, Globe, Percent
} from 'lucide-react';
import { toast } from 'sonner';

interface TaxItem {
  id: string;
  code: string;
  name: string;
  rate: string;
  baseAmount: number;
  taxAmount: number;
  status: 'A_PAYER' | 'REGLE';
  authority: string;
}

const TAX_ITEMS: TaxItem[] = [
  { id: '1', code: 'TVA-CM', name: 'Taxe sur la Valeur Ajoutée (17.5% + CAC 10%)', rate: '19.25%', baseAmount: 37402597, taxAmount: 7200000, status: 'A_PAYER', authority: 'DGI Cameroun' },
  { id: '2', code: 'AIR-IS', name: 'Acompte Impôt sur les Sociétés (IS)', rate: '2.2% CA', baseAmount: 102200000, taxAmount: 2248400, status: 'A_PAYER', authority: 'DGI Grandes Entreprises' },
  { id: '3', code: 'TEC-CAT4', name: 'Tarif Extérieur Commun (TEC CEMAC - Cat 4)', rate: '30%', baseAmount: 10666666, taxAmount: 3200000, status: 'REGLE', authority: 'Douanes Portuaires' },
  { id: '4', code: 'PRC-ACH', name: 'Précompte sur Achats & Prestations Locales', rate: '5.5%', baseAmount: 14200000, taxAmount: 781000, status: 'REGLE', authority: 'DGI Cameroun' },
];

export default function FinanceOhadaTaxesCemac() {
  const [taxes, setTaxes] = useState<TaxItem[]>(TAX_ITEMS);

  const totalDue = taxes.filter(t => t.status === 'A_PAYER').reduce((acc, curr) => acc + curr.taxAmount, 0);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-emerald-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Réglementation Fiscale & Douanière
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KFIN_TAX
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <ShieldCheck className="w-8 h-8 text-emerald-400" />
            Fiscalité CEMAC & Douanes
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Calculateur TEC CEMAC, TVA 19.25%, acomptes IS, précomptes et télétransmissions DGI.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.success('Bordereau récapitulatif des taxes CEMAC généré')}
            className="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-emerald-500/25 transition-all cursor-pointer"
          >
            <Download className="w-4 h-4" /> Bordereau Fiscal
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Total Impôts & Taxes à Payer</div>
          <div className="text-2xl font-black text-amber-400 font-mono">
            {totalDue.toLocaleString()} <span className="text-xs font-normal">XAF</span>
          </div>
          <div className="text-[11px] text-amber-300/80 mt-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" /> Échéance au 15 du mois prochain
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Droits Douaniers Liquidés (Ce mois)</div>
          <div className="text-2xl font-black text-slate-100 font-mono">
            3,200,000 <span className="text-xs text-slate-400 font-normal">XAF</span>
          </div>
          <div className="text-[11px] text-emerald-400 mt-2">Quittances Sydonia acquittées</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Conformité DGI & CEMAC</div>
          <div className="text-2xl font-black text-emerald-400 font-mono">
            100% <span className="text-xs font-normal text-slate-400">À jour</span>
          </div>
          <div className="text-[11px] text-emerald-300/80 mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Aucun arriéré fiscal
          </div>
        </div>
      </div>

      {/* Table Fiscalité */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Code Taxe</th>
                <th className="py-3.5 px-4">Libellé de l Impôt / Taxe</th>
                <th className="py-3.5 px-4">Taux Applicable</th>
                <th className="py-3.5 px-4 text-right">Base d Imposition</th>
                <th className="py-3.5 px-4 text-right">Montant Taxe (XAF)</th>
                <th className="py-3.5 px-4">Administration Bénéficiaire</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {taxes.map(tax => (
                <tr key={tax.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-emerald-400">{tax.code}</td>
                  <td className="py-3.5 px-4 font-sans text-slate-100 font-semibold">{tax.name}</td>
                  <td className="py-3.5 px-4 text-amber-300 font-bold">{tax.rate}</td>
                  <td className="py-3.5 px-4 text-right text-slate-400">{tax.baseAmount.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-100">{tax.taxAmount.toLocaleString()}</td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{tax.authority}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      tax.status === 'REGLE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {tax.status === 'REGLE' ? 'Acquitté' : 'À Payer'}
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
