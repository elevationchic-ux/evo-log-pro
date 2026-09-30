'use client';

import React, { useEffect, useState } from 'react';
import {
  Archive, Search, AlertTriangle, RefreshCw, MapPin, Database,
} from 'lucide-react';
import { transitAvanceAPI } from '@/lib/api-client';

interface Dossier {
  id: number;
  numero_dossier: string;
  type_transit: string;
  regime_douanier: string;
  marchandise: string | null;
  origine: string | null;
  destination: string | null;
  pays_origine_code: string | null;
  pays_destination_code: string | null;
  moyen_transport: string | null;
  numero_connaisse: string | null;
  numero_tir: string | null;
  poids_net: number | null;
  montant_total: number | null;
  reference_sygdonia: string | null;
  statut: string;
  date_ouverture: string;
}

// Statut réel du dossier : 'ouvert' par défaut, puis clôture (values non garanties → fallback neutre).
const STATUT_STYLES: Record<string, string> = {
  ouvert: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
  en_cours: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
  cloture: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  ferme: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  archive: 'bg-slate-800 text-slate-400 border border-slate-700',
};

function xaf(n: number | null | undefined): string {
  if (n === null || n === undefined) return '';
  return Math.round(n).toLocaleString('fr-FR');
}

function dateCourte(iso: string | null | undefined): string {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString('fr-FR');
}

function axe(d: Dossier): string {
  const o = d.pays_origine_code || d.origine || '?';
  const dst = d.pays_destination_code || d.destination || '?';
  return `${o} → ${dst}`;
}

export default function TransitDouaneDossiersCemac() {
  const [folders, setFolders] = useState<Dossier[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const charger = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await transitAvanceAPI.getDossiers({ limit: 500 });
      setFolders(res.data ?? []);
    } catch {
      setFolders([]);
      setError('Données indisponibles. Vérifiez votre connexion ou réessayez.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    charger();
  }, []);

  const filtered = folders.filter(f => {
    const q = searchQuery.toLowerCase();
    return (
      f.numero_dossier.toLowerCase().includes(q) ||
      (f.destination ?? '').toLowerCase().includes(q) ||
      (f.marchandise ?? '').toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-cyan-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              Transit International Terrestre
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wider uppercase bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1.5">
              <Database className="w-3 h-3" /> Source : dossiers enregistrés
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Archive className="w-8 h-8 text-cyan-400" />
            Dossiers de Transit Corridors CEMAC
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Dossiers de transit réellement enregistrés (import/export/transit terrestre).
            Les montants affichés sont ceux portés au dossier.
          </p>
        </div>
      </div>

      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher n° dossier, destination ou marchandise..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>
        </div>

        {loading ? (
          <div className="p-10 text-center text-slate-400 text-sm">Chargement des dossiers…</div>
        ) : error ? (
          <div className="p-10 text-center space-y-3">
            <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
            <p className="text-sm text-slate-300">{error}</p>
            <button
              onClick={charger}
              className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-bold"
            >
              <RefreshCw className="w-4 h-4" /> Réessayer
            </button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-10 text-center space-y-2">
            <Archive className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-400">
              {folders.length === 0
                ? 'Aucun dossier de transit enregistré.'
                : 'Aucun dossier ne correspond à cette recherche.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider bg-slate-950">
                  <th className="py-3.5 px-4">N° Dossier</th>
                  <th className="py-3.5 px-4">Origine → Destination</th>
                  <th className="py-3.5 px-4">Type / Régime</th>
                  <th className="py-3.5 px-4">Marchandise</th>
                  <th className="py-3.5 px-4 text-right">Montant total</th>
                  <th className="py-3.5 px-4">Ouverture</th>
                  <th className="py-3.5 px-4 text-center">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {filtered.map(f => (
                  <tr key={f.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-cyan-400">{f.numero_dossier}</td>
                    <td className="py-3.5 px-4">
                      <div className="font-sans font-bold text-slate-100 flex items-center gap-1.5">
                        <MapPin className="w-3.5 h-3.5 text-slate-500" /> {axe(f)}
                      </div>
                      <div className="text-[11px] text-slate-400 font-sans">{f.destination ?? ''}</div>
                    </td>
                    <td className="py-3.5 px-4 font-sans text-slate-300">
                      <div>{f.type_transit}</div>
                      <div className="text-[11px] text-slate-500">{f.regime_douanier}</div>
                    </td>
                    <td className="py-3.5 px-4 font-sans text-slate-300 max-w-[220px] truncate">{f.marchandise ?? ''}</td>
                    <td className="py-3.5 px-4 text-right font-bold text-amber-400">{xaf(f.montant_total)}</td>
                    <td className="py-3.5 px-4 text-slate-400">{dateCourte(f.date_ouverture)}</td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${STATUT_STYLES[(f.statut || '').toLowerCase()] ?? 'bg-slate-800 text-slate-400 border border-slate-700'}`}>
                        {f.statut}
                      </span>
                    </td>
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
