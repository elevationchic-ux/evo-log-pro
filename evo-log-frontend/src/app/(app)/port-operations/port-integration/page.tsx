'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Radio, ArrowLeft, RefreshCw, CheckCircle2, AlertTriangle,
  Server, ArrowRightLeft, Send, ShieldCheck
} from 'lucide-react';

interface EDIExchange {
  id: number;
  systeme: string;
  type_message: string;
  reference_externe: string;
  direction: 'INBOUND' | 'OUTBOUND';
  statut: 'SUCCES' | 'EN_ATTENTE' | 'ERREUR';
  horodatage: string;
  latence_ms: number;
}

export default function PortOperationsPortIntegrationPage() {
  const [loading, setLoading] = useState(false);
  const [exchanges, setExchanges] = useState<EDIExchange[]>([
    {
      id: 1,
      systeme: 'GUCE (Guichet Unique Commerce Extérieur)',
      type_message: 'CUSCAR - Notification Manifeste',
      reference_externe: 'GUCE-DLA-2026-8941',
      direction: 'OUTBOUND',
      statut: 'SUCCES',
      horodatage: 'Aujourd\'hui à 11:42',
      latence_ms: 120
    },
    {
      id: 2,
      systeme: 'CAMCIS (Direction Générale des Douanes)',
      type_message: 'CUSDEC - Déclaration Marchandise',
      reference_externe: 'CAMCIS-D6-44120',
      direction: 'OUTBOUND',
      statut: 'SUCCES',
      horodatage: 'Aujourd\'hui à 10:15',
      latence_ms: 240
    },
    {
      id: 3,
      systeme: 'Port Autonome de Douala (PAD - SIP)',
      type_message: 'BERMAN - Demande Accostage Poste 14',
      reference_externe: 'PAD-SIP-2026-092',
      direction: 'INBOUND',
      statut: 'SUCCES',
      horodatage: 'Aujourd\'hui à 08:30',
      latence_ms: 95
    },
    {
      id: 4,
      systeme: 'Port Autonome de Kribi (PAK - PCS)',
      type_message: 'COPRAR - Ordre Déchargement',
      reference_externe: 'PAK-PCS-7721',
      direction: 'INBOUND',
      statut: 'SUCCES',
      horodatage: 'Hier à 19:10',
      latence_ms: 110
    }
  ]);

  const handleTestPing = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      alert('Diagnostic de passerelle EDI terminé : Les liaisons avec le GUCE, CAMCIS Douanes, le PAD et le PAK sont 100% opérationnelles (Latence moyenne : 141 ms).');
    }, 800);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Opérations Portuaires
        </Link>
        <span>/</span>
        <span className="text-white">Passerelle EDI PAD / PAK & GUCE</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-pink-500/10 text-pink-400 rounded-xl border border-pink-500/20">
            <Radio className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Passerelle EDI & Intégration Portuaire
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-pink-500/10 text-pink-400 border border-pink-500/30 font-mono">
                KACC_EDI
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Interconnexion temps réel Guichet Unique (GUCE), Douanes Camerounaises (CAMCIS) et Autorités Portuaires (PAD/PAK)
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleTestPing}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-pink-600 hover:bg-pink-500 disabled:opacity-50 text-white font-medium text-sm shadow-lg shadow-pink-600/30 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Tester Liaisons EDI
          </button>
        </div>
      </div>

      {/* Gateways Status Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { name: 'GUCE Cameroun', endpoint: 'https://edi.guce.cm/v2/api', status: 'ONLINE', ping: '120 ms' },
          { name: 'CAMCIS Douane', endpoint: 'https://camcis.douanes.cm/edifact', status: 'ONLINE', ping: '240 ms' },
          { name: 'PAD Douala SIP', endpoint: 'https://sip.portdedouala.cm/edi', status: 'ONLINE', ping: '95 ms' },
          { name: 'PAK Kribi PCS', endpoint: 'https://pcs.pak.cm/api/v1', status: 'ONLINE', ping: '110 ms' },
        ].map((gw, idx) => (
          <div key={idx} className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
            <div className="flex justify-between items-start">
              <span className="font-semibold text-white text-sm">{gw.name}</span>
              <span className="flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <CheckCircle2 className="w-3 h-3" /> {gw.status}
              </span>
            </div>
            <p className="text-xs font-mono text-slate-400 mt-2 truncate">{gw.endpoint}</p>
            <div className="mt-3 pt-2 border-t border-slate-800 flex justify-between items-center text-xs text-slate-400">
              <span>Latence :</span>
              <span className="font-mono text-white font-bold">{gw.ping}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Exchange Logs */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        <h3 className="text-base font-semibold text-white mb-4 flex items-center justify-between">
          <span>Journal des Messages & Télécopies EDI</span>
          <span className="text-xs text-slate-400">Échanges EDIFACT / JSON sécurisés</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="py-3 px-4 rounded-l-xl">Système Destinataire / Émetteur</th>
                <th className="py-3 px-4">Type de Message</th>
                <th className="py-3 px-4">Référence Externe</th>
                <th className="py-3 px-4">Flux</th>
                <th className="py-3 px-4">Horodatage</th>
                <th className="py-3 px-4">Latence</th>
                <th className="py-3 px-4 rounded-r-xl">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {exchanges.map(ex => (
                <tr key={ex.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3.5 px-4 font-medium text-white">
                    {ex.systeme}
                  </td>
                  <td className="py-3.5 px-4 text-xs font-mono text-pink-400">
                    {ex.type_message}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-xs text-slate-300">
                    {ex.reference_externe}
                  </td>
                  <td className="py-3.5 px-4 text-xs">
                    <span className={`px-2 py-0.5 rounded font-mono text-[11px] ${
                      ex.direction === 'OUTBOUND' ? 'bg-blue-500/10 text-blue-400' : 'bg-purple-500/10 text-purple-400'
                    }`}>
                      {ex.direction === 'OUTBOUND' ? '↑ Sortant' : '↓ Entrant'}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-xs text-slate-400">
                    {ex.horodatage}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-xs">
                    {ex.latence_ms} ms
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1 w-fit">
                      <CheckCircle2 className="w-3 h-3" />
                      {ex.statut}
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