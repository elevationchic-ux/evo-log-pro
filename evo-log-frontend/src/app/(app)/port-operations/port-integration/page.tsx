'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { toast } from 'sonner';
import {
  Radio, ArrowLeft, RefreshCw, Server, Inbox
} from 'lucide-react';
import api from '@/lib/api';
import { useSettings } from '@/components/layout/SettingsProvider';

interface EDIExchange {
  id: number;
  systeme: string;
  type_message: string;
  reference_externe: string;
  direction: string;
  statut: string;
  horodatage: string;
  latence_ms: number | null;
}

// Catalogue de référence des partenaires EDI (documentation, pas des données d'exploitation).
// audit-allow:fake_data
const PARTENAIRES_EDI = [
  { name: 'GUCE Cameroun', role: 'Guichet Unique du Commerce Extérieur', endpoint: 'https://edi.guce.cm/v2/api' },
  { name: 'CAMCIS Douane', role: 'SysCOM (ex-CAMCIS)  déclarations en douane', endpoint: 'https://camcis.douanes.cm/edifact' },
  { name: 'PAD Douala SIP', role: 'Port Autonome de Douala  système d\'information portuaire', endpoint: 'https://sip.portdedouala.cm/edi' },
  { name: 'PAK Kribi PCS', role: 'Port Autonome de Kribi  Port Community System', endpoint: 'https://pcs.pak.cm/api/v1' },
];

export default function PortOperationsPortIntegrationPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [exchanges, setExchanges] = useState<EDIExchange[]>([]);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/integration/requetes', { params: { limit: 100 } });
      const data = res.data;
      const rows: any[] = Array.isArray(data) ? data : (data?.items ?? []);
      setExchanges(rows.map((r) => ({
        id: r.id,
        systeme: r.type_requete || `Intégration #${r.integration_id ?? ''}`,
        type_message: r.type_requete || '',
        reference_externe: r.reference_externe || r.numero_requete || '',
        direction: r.direction || 'INBOUND',
        statut: r.statut || '',
        horodatage: r.date_creation || r.date_envoi || '',
        latence_ms: r.duree_ms ?? null,
      })));
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t('Erreur de chargement', 'Failed to load'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    load();
  }, [load]);

  const handleRefresh = () => {
    load().then(() => toast.success(t('Journal actualisé.', 'Journal refreshed.')));
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Opérations Portuaires', 'Port Operations')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Passerelle EDI PAD / PAK & GUCE', 'EDI Gateway PAD / PAK & GUCE')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-pink-500/10 text-pink-400 rounded-xl border border-pink-500/20">
            <Radio className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              {t('Passerelle EDI & Intégration Portuaire', 'EDI Gateway & Port Integration')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-pink-500/10 text-pink-400 border border-pink-500/30 font-mono">
                KACC_EDI
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Interconnexion avec le Guichet Unique (GUCE), les Douanes (CAMCIS) et les autorités portuaires (PAD/PAK)', 'Interconnection with the One-Stop Shop (GUCE), Customs (CAMCIS) and port authorities (PAD/PAK)')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-pink-600 hover:bg-pink-500 disabled:opacity-50 text-white font-medium text-sm shadow-lg shadow-pink-600/30 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            {t('Actualiser le journal', 'Refresh journal')}
          </button>
        </div>
      </div>

      {/* Partenaires EDI (référence documentaire) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {PARTENAIRES_EDI.map((gw) => (
          <div key={gw.name} className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
            <div className="flex justify-between items-start gap-2">
              <span className="font-semibold text-white text-sm">{gw.name}</span>
              <span className="shrink-0 flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-700/50 text-slate-400 border border-slate-700">
                <Server className="w-3 h-3" /> {t('Non monitoré', 'Not monitored')}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-2">{gw.role}</p>
            <p className="text-xs font-mono text-slate-500 mt-2 truncate" title={gw.endpoint}>{gw.endpoint}</p>
          </div>
        ))}
      </div>

      {/* Journal des échanges (réel, pour l'instant vide) */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        <h3 className="text-base font-semibold text-white mb-4 flex items-center justify-between">
          <span>{t('Journal des Messages & Télécopies EDI', 'EDI Message & Telecopy Journal')}</span>
          <span className="text-xs text-slate-400">{t('Échanges EDIFACT / JSON sécurisés', 'Secured EDIFACT / JSON exchanges')}</span>
        </h3>

        {exchanges.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Inbox className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">{t('Aucun échange EDI journalisé', 'No EDI exchange logged')}</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1">
              {t('Les messages réels (CUSCAR, CUSDEC, BERMAN, COPRAR…) enregistrés via les intégrations apparaîtront ici.', 'Real messages (CUSCAR, CUSDEC, BERMAN, COPRAR…) recorded through the integrations will appear here.')}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">{t('Système Destinataire / Émetteur', 'Destination / Sender System')}</th>
                  <th className="py-3 px-4">{t('Type de Message', 'Message Type')}</th>
                  <th className="py-3 px-4">{t('Référence Externe', 'External Reference')}</th>
                  <th className="py-3 px-4">{t('Flux', 'Flow')}</th>
                  <th className="py-3 px-4">{t('Horodatage', 'Timestamp')}</th>
                  <th className="py-3 px-4">{t('Latence', 'Latency')}</th>
                  <th className="py-3 px-4 rounded-r-xl">{t('Statut', 'Status')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {exchanges.map(ex => (
                  <tr key={ex.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-medium text-white">{ex.systeme}</td>
                    <td className="py-3.5 px-4 text-xs font-mono text-pink-400">{ex.type_message}</td>
                    <td className="py-3.5 px-4 font-mono text-xs text-slate-300">{ex.reference_externe}</td>
                    <td className="py-3.5 px-4 text-xs">
                      <span className={`px-2 py-0.5 rounded font-mono text-[11px] ${ex.direction === 'OUTBOUND' ? 'bg-blue-500/10 text-blue-400' : 'bg-purple-500/10 text-purple-400'
                        }`}>
                        {ex.direction === 'OUTBOUND' ? t('↑ Sortant', '↑ Outbound') : t('↓ Entrant', '↓ Inbound')}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">{ex.horodatage}</td>
                    <td className="py-3.5 px-4 font-mono text-xs">{ex.latence_ms == null ? '' : `${ex.latence_ms} ms`}</td>
                    <td className="py-3.5 px-4 font-mono text-xs">{ex.statut}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
