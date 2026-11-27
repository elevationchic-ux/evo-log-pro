'use client';

import React, { useEffect, useState } from 'react';
import { metierAPI } from '@/lib/api-client';
import {
  Fuel, Wallet, TrendingUp, AlertTriangle, ShieldCheck,
  Package, Ship, Users, RefreshCw,
} from 'lucide-react';

interface Widget {
  titre: string;
  icon: React.ReactNode;
  fetcher: () => Promise<{ data: Record<string, unknown> }>;
  render: (d: Record<string, unknown>) => React.ReactNode;
}

function num(v: unknown): string {
  if (v === null || v === undefined) return '—';
  const n = Number(v);
  return Number.isFinite(n) ? n.toLocaleString('fr-FR') : String(v);
}

function note(v: unknown): boolean {
  return typeof v === 'object' && v !== null && 'note' in (v as Record<string, unknown>);
}

const WIDGETS: Widget[] = [
  {
    titre: 'Cuves carburant en alerte',
    icon: <Fuel className="w-5 h-5" />,
    fetcher: () => metierAPI.getCuvesEnAlerte(20),
    render: (d) => note(d) ? <p className="text-sm text-gray-500">{String(d.note)}</p> : (
      <>
        <p className="text-2xl font-bold">{num(d.cuves_en_alerte ?? d.total ?? 0)}</p>
        <p className="text-xs text-gray-500">sous le seuil de 20 %</p>
      </>
    ),
  },
  {
    titre: 'Masse salariale',
    icon: <Wallet className="w-5 h-5" />,
    fetcher: () => metierAPI.getPaieCumuls(),
    render: (d) => note(d) ? <p className="text-sm text-gray-500">{String(d.note)}</p> : (
      <>
        <p className="text-2xl font-bold">{num(d.masse_brute_xaf)}</p>
        <p className="text-xs text-gray-500">XAF brut — {num(d.employes)} salariés</p>
      </>
    ),
  },
  {
    titre: 'Chiffre d’affaires',
    icon: <TrendingUp className="w-5 h-5" />,
    fetcher: () => metierAPI.getRentabilite(),
    render: (d) => note(d) ? <p className="text-sm text-gray-500">{String(d.note)}</p> : (
      <>
        <p className="text-2xl font-bold">{num(d.ca_ttc_xaf)}</p>
        <p className="text-xs text-gray-500">XAF TTC — {num(d.factures_total)} factures</p>
      </>
    ),
  },
  {
    titre: 'Trésorerie prévisionnelle',
    icon: <AlertTriangle className="w-5 h-5" />,
    fetcher: () => metierAPI.getFinancePrevisions(),
    render: (d) => note(d) ? <p className="text-sm text-gray-500">{String(d.note)}</p> : (
      <>
        <p className="text-2xl font-bold">{num(d.solde_net_previsionnel_xaf)}</p>
        <p className="text-xs text-gray-500">XAF net — {num(d.risques_decouvert)} risque(s) de découvert</p>
      </>
    ),
  },
  {
    titre: 'Écarts d’inventaire',
    icon: <Package className="w-5 h-5" />,
    fetcher: () => metierAPI.getMagasinEcarts(),
    render: (d) => note(d) ? <p className="text-sm text-gray-500">{String(d.note)}</p> : (
      <>
        <p className="text-2xl font-bold">{num(d.ecarts)}</p>
        <p className="text-xs text-gray-500">écarts sur {num(d.lignes_total)} lignes</p>
      </>
    ),
  },
  {
    titre: 'Marchandises dangereuses',
    icon: <ShieldCheck className="w-5 h-5" />,
    fetcher: () => metierAPI.getTransportDg(),
    render: (d) => note(d) ? <p className="text-sm text-gray-500">{String(d.note)}</p> : (
      <>
        <p className="text-2xl font-bold">{num(d.non_conformes ?? d.total ?? 0)}</p>
        <p className="text-xs text-gray-500">non conformes ADR</p>
      </>
    ),
  },
  {
    titre: 'Navigabilité fluviale',
    icon: <Ship className="w-5 h-5" />,
    fetcher: () => metierAPI.getFluvialNavigabilite(),
    render: (d) => note(d) ? <p className="text-sm text-gray-500">{String(d.note)}</p> : (
      <>
        <p className="text-2xl font-bold">{num(d.biefs_restent ?? d.total ?? 0)}</p>
        <p className="text-xs text-gray-500">biefs navigables</p>
      </>
    ),
  },
  {
    titre: 'Santé des modules',
    icon: <Users className="w-5 h-5" />,
    fetcher: () => metierAPI.getDashboardSante(),
    render: (d) => {
      const modules = d.modules as Record<string, unknown> | undefined;
      if (!modules || note(modules)) return <p className="text-sm text-gray-500">{String(modules?.note ?? '—')}</p>;
      return (
        <>
          <p className="text-2xl font-bold">{num(modules.degradees)}</p>
          <p className="text-xs text-gray-500">modules dégradés sur {num(modules.modules_total)}</p>
        </>
      );
    },
  },
];

export default function MetierPage() {
  const [data, setData] = useState<Record<string, Record<string, unknown>>>({});
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const entries = await Promise.allSettled(
      WIDGETS.map(async (w) => [w.titre, (await w.fetcher()).data] as const)
    );
    const next: Record<string, Record<string, unknown>> = {};
    entries.forEach((e) => {
      if (e.status === 'fulfilled') next[e.value[0]] = e.value[1];
    });
    setData(next);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Pilotage métier</h1>
          <p className="text-sm text-gray-500">
            Indicateurs analytiques temps réel — données réelles uniquement.
          </p>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 px-3 py-2 text-sm border rounded-lg hover:bg-gray-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Actualiser
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {WIDGETS.map((w) => (
          <div key={w.titre} className="bg-white border rounded-xl p-5 shadow-sm">
            <div className="flex items-center gap-2 text-gray-600 mb-3">
              {w.icon}
              <span className="text-sm font-medium">{w.titre}</span>
            </div>
            {data[w.titre] ? w.render(data[w.titre]) : (
              <p className="text-sm text-gray-400">{loading ? 'Chargement…' : 'Indisponible'}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
