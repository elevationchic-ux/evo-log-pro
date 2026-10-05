'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Truck, Globe, Shield, RefreshCw, FileText, Route,
  CheckCircle2, AlertTriangle, MapPin, ArrowRight, Activity,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import type {
  OrdreTransportResponse,
  CarnetTIRResponse,
  CMRResponse,
  CorridorCEMACResponse,
  StatistiquesTransportInternational,
} from '@/types/transport_international';

/**
 * Ecran "Transport International & TIR Routier".
 *
 * Batch 12 : routes GET /ordres-transport et /carnets-tir ajoutées ; typage
 * aligné sur les vrais schémas backend ; statuts non accentués.
 *
 * Ce batch (honnêteté) :
 *   - Les KPI venaient de `Array.length` sur une tranche de 50 lignes :
 *     « 50 » s'affichait alors que des centaines d'OT existent. Les compteurs
 *     proviennent désormais de `GET /statistiques` (comptes/sommes SQL exacts).
 *   - Le module annonçait « TIR, CMR, Corridors CEMAC » mais ne rendait ni CMR
 *     ni corridors (et comptait seulement les carnets). Or `POST /cmr` et
 *     `POST /corridors-cemac` existaient SANS aucun GET : données write-only,
 *     écran mort. Les trois GET list + le rendu réel sont maintenant en place.
 *   - Bouton "Créer OT (N.I.)" supprimé : contrôle mort. La création d'un OT
 *     exige 4 sélecteurs FK (client/transporteur/camion/conducteur) hors périmètre ;
 *     l'écran dirige vers le flux mission/transit au lieu de simuler.
 *   - Gestion d'erreur par requête (plus de `Promise.allSettled` qui avalait le
 *     mutisme des carnets) et messages distincts 401/403 vs 500.
 */

// Statuts = valeurs exactes de `StatutTransport` (backend, sans accent).
const STATUTS = {
  PLANIFIE: 'planifie',
  EN_CHARGEMENT: 'en_chargement',
  EN_TRANSIT: 'en_transit',
  LIVRE: 'livre',
  RETARD: 'retard',
  ANNULE: 'annule',
  INCIDENT: 'incident',
} as const;

const STATUT_LABELS: Record<string, string> = {
  [STATUTS.PLANIFIE]: 'Planifié',
  [STATUTS.EN_CHARGEMENT]: 'En chargement',
  [STATUTS.EN_TRANSIT]: 'En transit',
  [STATUTS.LIVRE]: 'Livré',
  [STATUTS.RETARD]: 'En retard',
  [STATUTS.ANNULE]: 'Annulé',
  [STATUTS.INCIDENT]: 'Incident',
};

// Clés des requêtes ; sert à isoler les erreurs par section.
type ReqKey = 'stats' | 'ordres' | 'carnets' | 'cmr' | 'corridors';

const statutBadge = (s: string): string => {
  switch (s) {
    case STATUTS.EN_TRANSIT: return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
    case STATUTS.LIVRE: return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    case STATUTS.ANNULE:
    case STATUTS.INCIDENT: return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
    case STATUTS.RETARD: return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    case STATUTS.PLANIFIE: return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    case STATUTS.EN_CHARGEMENT: return 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30';
    // Statut inconnu/NULL : gris neutre, délibérément distinct du ambre "retard".
    default: return 'bg-slate-700/30 text-slate-400 border-slate-600/40';
  }
};

// Message d'erreur distinct selon le code HTTP (403 ≠ « backend en erreur »).
const messageErreur = (e: unknown, defaut: string): string => {
  const status = (e as { response?: { status?: number } })?.response?.status;
  if (status === 401 || status === 403) return "Droits insuffisants pour consulter cette donnée.";
  if (status === 404) return "Endpoint indisponible (404).";
  return defaut;
};

const fmtNum = (v: number | string | null | undefined): string => {
  const n = typeof v === 'string' ? parseFloat(v) : (v as number);
  return Number.isFinite(n) ? n.toLocaleString('fr-FR') : '';
};
const fmtDate = (iso: string | null): string => {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleDateString('fr-FR');
};

export default function TransportInternationalPage() {
  const [stats, setStats] = useState<StatistiquesTransportInternational | null>(null);
  const [ordres, setOrdres] = useState<OrdreTransportResponse[]>([]);
  const [carnets, setCarnets] = useState<CarnetTIRResponse[]>([]);
  const [cmrs, setCmrs] = useState<CMRResponse[]>([]);
  const [corridors, setCorridors] = useState<CorridorCEMACResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [erreurs, setErreurs] = useState<Partial<Record<ReqKey, string>>>({});

  const fetchData = useCallback(async () => {
    setLoading(true);
    setErreurs({});
    const [rStats, rOrdres, rCarnets, rCmr, rCorr] = await Promise.allSettled([
      apiClient.get<StatistiquesTransportInternational>('/api/v1/transport-international/statistiques'),
      apiClient.get<OrdreTransportResponse[]>('/api/v1/transport-international/ordres-transport', { params: { limit: 50 } }),
      apiClient.get<CarnetTIRResponse[]>('/api/v1/transport-international/carnets-tir', { params: { limit: 50 } }),
      apiClient.get<CMRResponse[]>('/api/v1/transport-international/cmr', { params: { limit: 50 } }),
      apiClient.get<CorridorCEMACResponse[]>('/api/v1/transport-international/corridors-cemac', { params: { limit: 50 } }),
    ]);

    const next: Partial<Record<ReqKey, string>> = {};

    if (rStats.status === 'fulfilled' && rStats.value.data) {
      setStats(rStats.value.data);
    } else {
      setStats(null);
      next.stats = messageErreur(rStats.status === 'rejected' ? rStats.reason : null, 'Statistiques indisponibles.');
    }

    if (rOrdres.status === 'fulfilled' && Array.isArray(rOrdres.value.data)) {
      setOrdres(rOrdres.value.data);
    } else {
      setOrdres([]);
      next.ordres = messageErreur(rOrdres.status === 'rejected' ? rOrdres.reason : null, 'Liste des ordres de transport indisponible.');
    }

    if (rCarnets.status === 'fulfilled' && Array.isArray(rCarnets.value.data)) {
      setCarnets(rCarnets.value.data);
    } else {
      setCarnets([]);
      next.carnets = messageErreur(rCarnets.status === 'rejected' ? rCarnets.reason : null, 'Liste des carnets TIR indisponible.');
    }

    if (rCmr.status === 'fulfilled' && Array.isArray(rCmr.value.data)) {
      setCmrs(rCmr.value.data);
    } else {
      setCmrs([]);
      next.cmr = messageErreur(rCmr.status === 'rejected' ? rCmr.reason : null, 'Liste des CMR indisponible.');
    }

    if (rCorr.status === 'fulfilled' && Array.isArray(rCorr.value.data)) {
      setCorridors(rCorr.value.data);
    } else {
      setCorridors([]);
      next.corridors = messageErreur(rCorr.status === 'rejected' ? rCorr.reason : null, 'Liste des corridors indisponible.');
    }

    setErreurs(next);
    setLoading(false);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleEnTransit = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/transport-international/ordres-transport/${id}/en-transit`);
      toast.success('Ordre passé en transit.');
      fetchData();
    } catch (err) {
      toast.error(messageErreur(err, "Échec de la mise en transit."));
    }
  };

  const handleLivrer = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/transport-international/ordres-transport/${id}/livre`);
      toast.success('Ordre marqué livré.');
      fetchData();
    } catch (err) {
      toast.error(messageErreur(err, "Échec du marquage 'livré'."));
    }
  };

  // KPI exacts depuis /statistiques (jamais depuis la tranche de 50 lignes).
  const totalOt = stats?.ordres_transport.total ?? 0;
  const enTransit = stats?.ordres_transport.par_statut[STATUTS.EN_TRANSIT] ?? 0;
  const livres = stats?.ordres_transport.par_statut[STATUTS.LIVRE] ?? 0;
  const tonnage = stats?.ordres_transport.tonnage_net ?? 0;
  const nbCarnets = stats?.carnets_tir ?? 0;
  const nbCmr = stats?.cmr ?? 0;
  const nbCorridors = stats?.corridors_cemac ?? 0;

  const kpis = [
    { label: 'Ordres Transport', value: totalOt, icon: Truck, color: 'text-indigo-400' },
    { label: 'En Transit', value: enTransit, icon: ArrowRight, color: 'text-cyan-400' },
    { label: 'Livrés', value: livres, icon: CheckCircle2, color: 'text-emerald-400' },
    { label: 'Tonnage net (t)', value: fmtNum(tonnage), icon: Activity, color: 'text-sky-400' },
    { label: 'Carnets TIR', value: nbCarnets, icon: Shield, color: 'text-amber-400' },
    { label: 'CMR émises', value: nbCmr, icon: FileText, color: 'text-violet-400' },
    { label: 'Corridors CEMAC', value: nbCorridors, icon: Route, color: 'text-emerald-400' },
  ];

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Globe className="w-3.5 h-3.5" /> Transport International  TIR, CMR, Corridors CEMAC
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Transport International &amp; TIR Routier</h1>
          <p className="text-xs text-slate-400 mt-1">
            Ordres de transport, carnets TIR, lettres de voiture CMR et corridors. Totaux issus de comptes SQL ;
            les listes affichent les 50 enregistrements les plus récents.
          </p>
        </div>
        <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all self-start">
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
        </button>
      </div>

      {erreurs.stats && (
        <div className="bg-amber-500/10 border border-amber-500/30 p-4 rounded-2xl flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <p className="text-xs font-bold text-amber-300">{erreurs.stats} Les compteurs sont indisponibles tant que cette route ne répond pas.</p>
        </div>
      )}

      {/* KPI réels */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        {kpis.map((s) => (
          <div key={s.label} className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">{s.label}</span>
              <s.icon className={`w-4 h-4 ${s.color}`} />
            </div>
            <p className={`text-2xl font-black mt-2 ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Ordres de transport */}
      <Section
        title="Ordres de Transport International"
        icon={<Truck className="w-5 h-5 text-indigo-400" />}
        count={totalOt} shown={ordres.length}
        loading={loading} error={erreurs.ordres}
        emptyText="Aucun ordre de transport enregistré. Un OT est créé depuis le flux mission / transit (l'API attend les IDs client, transporteur, camion et conducteur)."
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800/80">
                {['N° OT', 'Type transit', 'Chargement → Livraison', 'Destination', 'Poids net (t)', 'Statut', 'Actions'].map(h => (
                  <th key={h} className="px-5 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {ordres.map((o) => (
                <tr key={o.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-5 py-4 font-mono text-xs text-indigo-400">{o.numero_ot}</td>
                  <td className="px-5 py-4 text-slate-300 uppercase">{String(o.type_transit || '')}</td>
                  <td className="px-5 py-4 text-slate-300 flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-slate-500" />{o.lieu_chargement || ''}
                    <ArrowRight className="w-3 h-3 text-slate-500 mx-1" />
                    <MapPin className="w-3 h-3 text-cyan-500" />{o.lieu_livraison || ''}
                  </td>
                  <td className="px-5 py-4 text-slate-300">
                    {o.pays_destination || ''}
                    {o.code_pays_destination ? ` (${o.code_pays_destination})` : ''}
                  </td>
                  <td className="px-5 py-4 text-slate-300">{o.poids_net != null ? Number(o.poids_net).toLocaleString('fr-FR') : ''}</td>
                  <td className="px-5 py-4">
                    <span className={`px-2.5 py-1 rounded-xl text-[11px] font-bold uppercase border ${statutBadge(String(o.statut))}`}>
                      {STATUT_LABELS[String(o.statut)] || (o.statut ? String(o.statut) : 'inconnu')}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      {o.statut === STATUTS.PLANIFIE || o.statut === STATUTS.EN_CHARGEMENT ? (
                        <button onClick={() => handleEnTransit(o.id)} className="px-3 py-1.5 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-400 border border-cyan-500/30 text-xs font-bold transition-all">→ Transit</button>
                      ) : o.statut === STATUTS.EN_TRANSIT ? (
                        <button onClick={() => handleLivrer(o.id)} className="px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-bold transition-all">Livrer</button>
                      ) : null}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* Carnets TIR */}
      <Section
        title="Carnets TIR"
        icon={<Shield className="w-5 h-5 text-amber-400" />}
        count={nbCarnets} shown={carnets.length}
        loading={loading} error={erreurs.carnets}
        emptyText="Aucun carnet TIR enregistré."
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800/80">
                {['N° carnet', 'OT rattaché', 'Émission', 'Départ → Arrivée', 'Validité', 'Garantie', 'Statut'].map(h => (
                  <th key={h} className="px-5 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {carnets.map((c) => (
                <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-5 py-4 font-mono text-xs text-amber-400">{c.numero_carnet}</td>
                  <td className="px-5 py-4 text-slate-400 font-mono text-xs">#{c.ordre_transport_id}</td>
                  <td className="px-5 py-4 text-slate-300">{c.pays_emission || ''}{c.code_pays_emission ? ` (${c.code_pays_emission})` : ''}</td>
                  <td className="px-5 py-4 text-slate-300 flex items-center gap-1">
                    {c.bureau_depart || ''} <ArrowRight className="w-3 h-3 text-slate-500 mx-1" /> {c.bureau_arrivee || ''}
                  </td>
                  <td className="px-5 py-4 text-slate-300">{fmtDate(c.date_validite)}</td>
                  <td className="px-5 py-4 text-slate-300">{fmtNum(c.montant_garantie)} {c.devise || ''}</td>
                  <td className="px-5 py-4"><span className="px-2.5 py-1 rounded-xl text-[11px] font-bold uppercase border bg-slate-500/20 text-slate-300 border-slate-500/30">{c.statut || ''}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* CMR */}
      <Section
        title="Lettres de voiture CMR"
        icon={<FileText className="w-5 h-5 text-violet-400" />}
        count={nbCmr} shown={cmrs.length}
        loading={loading} error={erreurs.cmr}
        emptyText="Aucune CMR émise."
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800/80">
                {['N° CMR', 'Expéditeur', 'Destinataire', 'Chargement → Livraison', 'Poids net (t)', 'Signatures', 'Statut'].map(h => (
                  <th key={h} className="px-5 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {cmrs.map((c) => {
                const sigs = [c.signature_expediteur && 'Exp', c.signature_transporteur && 'Trsp', c.signature_destinataire && 'Dest'].filter(Boolean);
                return (
                  <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-5 py-4 font-mono text-xs text-violet-400">{c.numero_cmr}</td>
                    <td className="px-5 py-4 text-slate-300">{c.expediteur || ''}</td>
                    <td className="px-5 py-4 text-slate-300">{c.destinataire || ''}</td>
                    <td className="px-5 py-4 text-slate-300 flex items-center gap-1">
                      {c.lieu_chargement || ''} <ArrowRight className="w-3 h-3 text-slate-500 mx-1" /> {c.lieu_livraison || ''}
                    </td>
                    <td className="px-5 py-4 text-slate-300">{c.poids_net != null ? Number(c.poids_net).toLocaleString('fr-FR') : ''}</td>
                    <td className="px-5 py-4 text-xs text-slate-400">{sigs.length ? sigs.join(', ') : 'aucune'}</td>
                    <td className="px-5 py-4"><span className="px-2.5 py-1 rounded-xl text-[11px] font-bold uppercase border bg-slate-500/20 text-slate-300 border-slate-500/30">{c.statut || ''}</span></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Section>

      {/* Corridors CEMAC */}
      <Section
        title="Corridors CEMAC"
        icon={<Route className="w-5 h-5 text-emerald-400" />}
        count={nbCorridors} shown={corridors.length}
        loading={loading} error={erreurs.corridors}
        emptyText="Aucun corridor référencé."
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800/80">
                {['Corridor', 'Depart → Arrivée', 'Distance (km)', 'Durée estimée (h)', 'Statut'].map(h => (
                  <th key={h} className="px-5 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {corridors.map((c) => (
                <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-5 py-4 font-bold text-emerald-400">{c.nom}</td>
                  <td className="px-5 py-4 text-slate-300 flex items-center gap-1">
                    {c.pays_depart || ''} <ArrowRight className="w-3 h-3 text-slate-500 mx-1" /> {c.pays_arrivee || ''}
                  </td>
                  <td className="px-5 py-4 text-slate-300">{fmtNum(c.distance_km)}</td>
                  <td className="px-5 py-4 text-slate-300">{fmtNum(c.duree_estimee_heures)}</td>
                  <td className="px-5 py-4"><span className="px-2.5 py-1 rounded-xl text-[11px] font-bold uppercase border bg-slate-500/20 text-slate-300 border-slate-500/30">{c.statut || ''}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>
    </div>
  );
}

/** Conteneur de section à en-tête + états loading/erreur/vide honnêtes. */
function Section(props: {
  title: string;
  icon: React.ReactNode;
  count: number;
  shown: number;
  loading: boolean;
  error?: string;
  emptyText: string;
  children: React.ReactNode;
}) {
  const { title, icon, count, shown, loading, error, emptyText, children } = props;
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        {icon}
        <h2 className="text-base font-black text-white">{title}</h2>
        <span className="ml-auto text-xs text-slate-400">
          {count.toLocaleString('fr-FR')} au total{shown > 0 ? ` · ${shown} affiché(s)` : ''}
        </span>
      </div>
      {loading ? (
        <div className="p-12 text-center text-slate-400"><RefreshCw className="w-6 h-6 animate-spin text-indigo-400 mx-auto mb-2" /></div>
      ) : error ? (
        <div className="p-8 text-center text-slate-400">
          <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
          <p className="text-xs font-bold text-amber-300">{error}</p>
        </div>
      ) : shown === 0 ? (
        <div className="p-12 text-center text-slate-400">
          <Globe className="w-10 h-10 text-slate-500 mx-auto mb-2" />
          <p className="font-bold text-white">Rien à afficher</p>
          <p className="text-xs text-slate-500 mt-1">{emptyText}</p>
        </div>
      ) : (
        children
      )}
    </div>
  );
}
