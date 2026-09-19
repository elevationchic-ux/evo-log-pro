'use client';

import React, { useState } from 'react';
import {
  FileText, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, ArrowUpDown, DollarSign, Printer, Send
} from 'lucide-react';
import { toast } from 'sonner';

interface Invoice {
  id: string;
  invoiceNumber: string;
  client: string;
  date: string;
  dueDate: string;
  amountHT: number;
  tva: number;
  amountTTC: number;
  status: 'PAYEE' | 'EN_ATTENTE' | 'RETARD' | 'PROFORMA';
  currency: 'XAF' | 'EUR' | 'USD';
}

const INVOICES_DATA: Invoice[] = [
  { id: '1', invoiceNumber: 'FAC-2026-0842', client: 'TOTAL Cameroun S.A.', date: '27/08/2026', dueDate: '26/09/2026', amountHT: 7127883, tva: 1372117, amountTTC: 8500000, status: 'EN_ATTENTE', currency: 'XAF' },
  { id: '2', invoiceNumber: 'FAC-2026-0841', client: 'SABC (Boissons du Cameroun)', date: '25/08/2026', dueDate: '24/09/2026', amountHT: 12578616, tva: 2421384, amountTTC: 15000000, status: 'PAYEE', currency: 'XAF' },
  { id: '3', invoiceNumber: 'FAC-2026-0840', client: 'CAMRAIL Transitaire', date: '20/08/2026', dueDate: '19/09/2026', amountHT: 10398323, tva: 2001677, amountTTC: 12400000, status: 'PAYEE', currency: 'XAF' },
  { id: '4', invoiceNumber: 'FAC-2026-0839', client: 'Export Bois Tchad Inc', date: '10/08/2026', dueDate: '25/08/2026', amountHT: 5500000, tva: 0, amountTTC: 5500000, status: 'RETARD', currency: 'XAF' },
  { id: '5', invoiceNumber: 'PRO-2026-0112', client: 'CIMENCAM Douala', date: '27/08/2026', dueDate: '10/09/2026', amountHT: 18000000, tva: 3465000, amountTTC: 21465000, status: 'PROFORMA', currency: 'XAF' },
];

export default function FinanceOhadaInvoicing() {
  const [invoices, setInvoices] = useState<Invoice[]>(INVOICES_DATA);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const filtered = invoices.filter(inv => {
    const matchStatus = filterStatus === 'ALL' || inv.status === filterStatus;
    const matchSearch = inv.invoiceNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        inv.client.toLowerCase().includes(searchQuery.toLowerCase());
    return matchStatus && matchSearch;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-emerald-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Facturation Intégrée Fret & Transit
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KFIN_FAC
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <FileText className="w-8 h-8 text-emerald-400" />
            Facturation Clients & Proformas
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Émission automatisée depuis les missions TMS, gestion des tarifs portuaires, calcul TVA 19.25% et devises.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Formulaire de création de facture client')}
            className="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-emerald-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Créer Facture
          </button>
        </div>
      </div>

      {/* Barre de Recherche et Filtres */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher par n° de facture ou client..."
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-mono"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto">
          {['ALL', 'PAYEE', 'EN_ATTENTE', 'RETARD', 'PROFORMA'].map(st => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition-all border ${
                filterStatus === st
                  ? 'bg-emerald-600/30 text-emerald-300 border-emerald-500'
                  : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-800'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Table des Factures */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">N° Facture</th>
                <th className="py-3.5 px-4">Client</th>
                <th className="py-3.5 px-4">Date</th>
                <th className="py-3.5 px-4">Échéance</th>
                <th className="py-3.5 px-4 text-right">Montant HT</th>
                <th className="py-3.5 px-4 text-right">TVA (19.25%)</th>
                <th className="py-3.5 px-4 text-right">Montant TTC (XAF)</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
                <th className="py-3.5 px-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(inv => (
                <tr key={inv.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-bold text-emerald-400">{inv.invoiceNumber}</td>
                  <td className="py-3 px-4 font-sans text-slate-100 font-medium">{inv.client}</td>
                  <td className="py-3 px-4 text-slate-400">{inv.date}</td>
                  <td className="py-3 px-4 text-slate-400">{inv.dueDate}</td>
                  <td className="py-3 px-4 text-right">{inv.amountHT.toLocaleString()}</td>
                  <td className="py-3 px-4 text-right text-slate-400">{inv.tva.toLocaleString()}</td>
                  <td className="py-3 px-4 text-right font-bold text-slate-100">{inv.amountTTC.toLocaleString()}</td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      inv.status === 'PAYEE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      inv.status === 'EN_ATTENTE' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                      inv.status === 'RETARD' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                      'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}>
                      {inv.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center flex items-center justify-center gap-1.5">
                    <button
                      onClick={() => toast.success(`Impression de la facture ${inv.invoiceNumber}`)}
                      className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"
                      title="Imprimer"
                    >
                      <Printer className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => toast.success(`Facture ${inv.invoiceNumber} envoyée par email`)}
                      className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"
                      title="Envoyer"
                    >
                      <Send className="w-3.5 h-3.5" />
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
