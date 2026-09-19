'use client';

import React, { useState } from 'react';
import {
  ShieldCheck, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Globe, FileBadge, Building, RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';

interface GuceComplianceDoc {
  id: string;
  referenceGuce: string;
  documentType: 'CERTIFICAT_PHYTOSANITAIRE' | 'CERTIFICAT_ORIGINE_CEMAC' | 'ATTESTATION_SGS_COTECNIA' | 'AUTORISATION_MINCOMMERCE';
  importer: string;
  issueDate: string;
  status: 'VALIDE' | 'EN_INSPECTION' | 'REJETE';
  issuingAuthority: string;
}

const COMPLIANCE_DOCS: GuceComplianceDoc[] = [
  { id: '1', referenceGuce: 'GUCE-2026-PHY-0994', documentType: 'CERTIFICAT_PHYTOSANITAIRE', importer: 'SABC Boissons', issueDate: '26/08/2026', status: 'VALIDE', issuingAuthority: 'Ministère de l Agriculture (MINADER)' },
  { id: '2', referenceGuce: 'GUCE-2026-CO-0112', documentType: 'CERTIFICAT_ORIGINE_CEMAC', importer: 'TOTAL Cameroun', issueDate: '25/08/2026', status: 'VALIDE', issuingAuthority: 'Chambre de Commerce (CCIMA)' },
  { id: '3', referenceGuce: 'GUCE-2026-SGS-4481', documentType: 'ATTESTATION_SGS_COTECNIA', importer: 'CIMENCAM', issueDate: '24/08/2026', status: 'EN_INSPECTION', issuingAuthority: 'SGS Cameroun S.A.' },
];

export default function TransitDouaneCompliance() {
  const [docs] = useState<GuceComplianceDoc[]>(COMPLIANCE_DOCS);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = docs.filter(d =>
    d.referenceGuce.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.importer.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.issuingAuthority.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-cyan-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              Guichet Unique GUCE & Contrôle Réglementaire
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KDOU_CMP
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <ShieldCheck className="w-8 h-8 text-cyan-400" />
            Conformité Guichet Unique (GUCE) & SGS
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Télétransmission et contrôle des certificats phytosanitaires, attestations de conformité SGS/COTECNIA et autorisations préalables.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.success('Synchronisation API Guichet Unique effectuée')}
            className="px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-teal-500 text-white font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-cyan-500/25 transition-all cursor-pointer"
          >
            <RefreshCw className="w-4 h-4" /> Synchroniser GUCE
          </button>
        </div>
      </div>

      {/* Table Documents Conformité */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Réf. GUCE & Type</th>
                <th className="py-3.5 px-4">Opérateur / Importateur</th>
                <th className="py-3.5 px-4">Autorité Émettrice</th>
                <th className="py-3.5 px-4">Date Délivrance</th>
                <th className="py-3.5 px-4 text-center">Statut Conformité</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(d => (
                <tr key={d.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-cyan-400">{d.referenceGuce}</div>
                    <div className="text-[11px] text-slate-400 font-sans">{d.documentType}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-100 font-bold">{d.importer}</td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{d.issuingAuthority}</td>
                  <td className="py-3.5 px-4 text-slate-400">{d.issueDate}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      d.status === 'VALIDE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
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
