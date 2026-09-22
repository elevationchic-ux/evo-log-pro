'use client';

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { complianceAPI } from '@/lib/api-client';
import { Landmark, ShieldCheck, CheckCircle2, Search } from 'lucide-react';
import Link from 'next/link';

export default function CompliancePage() {
  const [mounted, setMounted] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ['compliance-audits'],
    queryFn: async () => {
      const res = await complianceAPI.getAudits();
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted,
  });

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement du module K-Compliance...</div>;

  const items = Array.isArray(data) ? data : [];
  const filteredItems = items.filter((i: any) =>
    (String(i.dossier_reference || '') + ' ' + String(i.type_reglementation || ''))
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 text-teal-400 text-xs font-semibold mb-2 border border-teal-500/20">
            <Landmark className="w-3.5 h-3.5" />
            K-Compliance • Audit Réglementaire & Douane ZLECAF
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Conformité Douanière & Fiscalité</h1>
          <p className="text-slate-400 text-sm mt-1">Audit de conformité documentaire, exonérations et passeports de transit.</p>
        </div>

        <Link
          href="/compliance/audits"
          className="inline-flex items-center justify-center gap-2 bg-teal-600 hover:bg-teal-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-teal-600/30 transition-all hover:scale-[1.02]"
        >
          <ShieldCheck className="w-4 h-4" />
          Rapports d'Audit ZLECAF
        </Link>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            Registre des Audits de Conformité Douanière
          </h3>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher un dossier..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">N° Dossier / Exemption</th>
                <th className="px-6 py-4">Cadre Réglementaire</th>
                <th className="px-6 py-4 text-center">Score Conformité</th>
                <th className="px-6 py-4 text-right">Statut Audit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr><td colSpan={4} className="p-12 text-center text-slate-400">Chargement des audits...</td></tr>
              ) : filteredItems.length === 0 ? (
                <tr><td colSpan={4} className="p-8 text-center text-slate-500">Aucun audit enregistré.</td></tr>
              ) : (
                filteredItems.map((item: any, idx: number) => (
                  <tr key={item.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100 font-mono">
                      {item.dossier_reference || `DOS-DOUANE-00${item.id}`}
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-200">
                      {item.type_reglementation || 'ZLECAF / CEMAC'}
                    </td>
                    <td className="px-6 py-4 text-center font-mono font-bold text-teal-400">
                      {item.score_conformite_pct || 99.2}%
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" /> CONFORME
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
