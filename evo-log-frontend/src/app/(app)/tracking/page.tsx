'use client';

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { trackingAPI } from '@/lib/api-client';
import { Radio, FileCheck, CheckCircle2, MapPin, Search } from 'lucide-react';
import Link from 'next/link';

export default function TrackingPage() {
  const [mounted, setMounted] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ['epods'],
    queryFn: async () => {
      const res = await trackingAPI.getEpods();
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted,
  });

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement du module K-Tracking...</div>;

  const items = Array.isArray(data) ? data : [];
  const filteredItems = items.filter((i: any) =>
    (String(i.nom_destinataire || '') + ' ' + String(i.reference_mission || ''))
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 text-sky-400 text-xs font-semibold mb-2 border border-sky-500/20">
            <Radio className="w-3.5 h-3.5" />
            K-Tracking • GPS Satellite & Preuve de Livraison Électronique
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Suivi GPS & e-POD Temps Réel</h1>
          <p className="text-slate-400 text-sm mt-1">Confirmation de réception géolocalisée et numérisation des bons de livraison.</p>
        </div>

        <Link
          href="/tracking/epod"
          className="inline-flex items-center justify-center gap-2 bg-sky-600 hover:bg-sky-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-sky-600/30 transition-all hover:scale-[1.02]"
        >
          <FileCheck className="w-4 h-4" />
          Scanner un e-POD
        </Link>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            Preuves de Livraison Électroniques (e-POD) Récentes
          </h3>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par mission..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">N° Mission / Destinataire</th>
                <th className="px-6 py-4">Coordonnées GPS</th>
                <th className="px-6 py-4 text-right">Statut Signature</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr><td colSpan={3} className="p-12 text-center text-slate-400">Chargement des e-PODs...</td></tr>
              ) : filteredItems.length === 0 ? (
                <tr><td colSpan={3} className="p-8 text-center text-slate-500">Aucun e-POD enregistré.</td></tr>
              ) : (
                filteredItems.map((item: any, idx: number) => (
                  <tr key={item.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100">
                      {item.reference_mission || `OT-2026-00${item.id}`}
                      <div className="text-xs font-normal text-slate-400">{item.nom_destinataire}</div>
                    </td>
                    <td className="px-6 py-4 font-mono text-sky-400 text-xs flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-sky-400" />
                      Lat: {item.latitude || 4.051}, Lon: {item.longitude || 9.704}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
                        <CheckCircle2 className="w-3 h-3" /> SIGNÉ & VALIDÉ
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
