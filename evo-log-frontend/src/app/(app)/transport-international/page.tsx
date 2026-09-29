'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Truck, Globe, Shield, RefreshCw, PlusCircle,
  CheckCircle2, AlertTriangle, MapPin, ArrowRight
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import type {
  OrdreTransportResponse,
  CarnetTIRResponse,
} from '@/types/transport_international';

/**
 * Ecran "Transport International & TIR Routier".
 *
 * Batch 12 : le typage strict a révélé que CETTE PAGE NE POURVAIT PAS
 * FONCTIONNER telle quelle :
 *   1. Elle appelait `GET /ordres-transport` et `GET /carnets-tir` mais
 *      AUCUNE de ces routes n'existait côté backend (le `Promise.allSettled`
 *      avalait le 404, d'où l'affichage permanent "Aucun ordre de transport").
 *      → les deux routes GET LIST ont été ajoutées batch 12.
 *   2. Elle lisait `o.numero_ordre`, `o.mode_transport`, `o.pays_depart`,
 *      `o.incoterm`, `o.poids_kg` : ces champs n'existent pas sur
 *      `OrdreTransportResponse` (le backend a `numero_ot`, `type_transit`,
 *      `lieu_chargement`, `poids_net` / `poids_brut`, et PAS d'incoterm).
 *   3. Elle comparait `o.statut === 'créé'` / `'livré'` / `'annulé'` : les
 *      accents ne correspondent pas à l'enum `StatutTransport` backend
 *      (`PLANIFIE = "planifie"`, `LIVRE = "livre"`, `ANNULE = "annule"`),
 *      donc AUCUN filtre et AUCUN bouton d'action ne se déclenchait.
 *   4. Le formulaire "Créer un Ordre de Transport" envoyait un payload
 *      totalement déconnecté de `OrdreTransportCreate` (16 champs obligatoires
 *      côté backend, dont 4 FK `client_id / transporteur_id / camion_id /
 *      conducteur_id` non collectées ici). POST renvoyait systématiquement
 *      422, error avalee par `catch { console.error }`.
 *
 *   Le bouton de création est volontairement passé en "non implémenté"
 *   tant que les sélecteurs FK ne sont pas construits : préférer un
 *   refus explicite à un POST 422 muet (principe Zero-Mock).
 */

// Les chaines comparées à `statut` sortent de `StatutTransport` (backend,
// sans accent). Toute comparaison avec 'créé', 'livré', 'annulé' serait du
// code mort  elles sont explicitement retirées de la page batch 12.
const STATUTS = {
  PLANIFIE: 'planifie',
  EN_CHARGEMENT: 'en_chargement',
  EN_TRANSIT: 'en_transit',
  LIVRE: 'livre',
  RETARD: 'retard',
  ANNULE: 'annule',
  INCIDENT: 'incident',
} as const;

export default function TransportInternationalPage() {
  const [ordres, setOrdres] = useState<OrdreTransportResponse[]>([]);
  const [carnets, setCarnets] = useState<CarnetTIRResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setFetchError(null);
    try {
      const [resOrdres, resCarnets] = await Promise.allSettled([
        apiClient.get<OrdreTransportResponse[]>(
          '/api/v1/transport-international/ordres-transport',
          { params: { limit: 50 } },
        ),
        apiClient.get<CarnetTIRResponse[]>(
          '/api/v1/transport-international/carnets-tir',
          { params: { limit: 50 } },
        ),
      ]);
      if (resOrdres.status === 'fulfilled') {
        const data = resOrdres.value.data as unknown;
        setOrdres(Array.isArray(data) ? (data as OrdreTransportResponse[]) : []);
      } else {
        setOrdres([]);
        setFetchError('Liste ordres de transport indisponible (backend en erreur).');
      }
      if (resCarnets.status === 'fulfilled') {
        const data = resCarnets.value.data as unknown;
        setCarnets(Array.isArray(data) ? (data as CarnetTIRResponse[]) : []);
      } else {
        setCarnets([]);
      }
    } catch (err) {
      console.error('Transport international fetch error:', err);
      setFetchError('Erreur réseau inattendue.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleEnTransit = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/transport-international/ordres-transport/${id}/en-transit`);
      fetchData();
    } catch (err) {
      console.error('Erreur mise en transit:', err);
      toast.error("Échec de la mise en transit (voir console).");
    }
  };

  const handleLivrer = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/transport-international/ordres-transport/${id}/livre`);
      fetchData();
    } catch (err) {
      console.error('Erreur livraison:', err);
      toast.error("Échec de la marquage 'livré' (voir console).");
    }
  };

  // Les clés de `parStatut` doivent correspondre EXACTÉMENT à `StatutTransport`
  // backend (sans accent). Le switch précédent testait 'livré' / 'annulé' 
  // jamais égal, donc tous les OT tombaient dans le default ambre.
  const getStatutBadge = (s: string) => {
    switch (s) {
      case STATUTS.EN_TRANSIT: return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
      case STATUTS.LIVRE: return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case STATUTS.ANNULE: return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
      case STATUTS.INCIDENT: return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
      case STATUTS.RETARD: return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case STATUTS.PLANIFIE: return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
      case STATUTS.EN_CHARGEMENT: return 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30';
      default: return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    }
  };

  const handleCreateBlocked = () => {
    // Zero-Mock : on refuse d'ouvrir un formulaire dont le payload ne
    // correspondrait pas au contrat `OrdreTransportCreate` backend (4 FK
    // obligatoires non collectées + 5 champs numériques requis).
    toast(
      "Création d'OTI non implémentée : l'écran doit d'abord collecter les IDs client / transporteur / camion / conducteur (pickers FK) et les montants (poids net/brut, valeur, freight). Utiliser le POST /api/v1/transport-international/ordres-transport directement.",
      { duration: 8000 },
    );
  };

  const enTransit = ordres.filter((o) => o.statut === STATUTS.EN_TRANSIT).length;
  const livres = ordres.filter((o) => o.statut === STATUTS.LIVRE).length;

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Globe className="w-3.5 h-3.5" /> Transport International  TIR, CMR, Corridors CEMAC & Afrique Centrale
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Transport International & TIR Routier</h1>
          <p className="text-xs text-slate-400 mt-1">Gestion des ordres de transport internationaux, carnets TIR IRU, lettres de voiture CMR, et corridors Douala-N'Djaména-Bangui.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button
            onClick={handleCreateBlocked}
            title="Formulaire de création non implémenté : pickers FK manquants (client / transporteur / camion / conducteur)"
            className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-400 border border-slate-700 text-xs font-bold transition-all"
          >
            <PlusCircle className="w-4 h-4" /> Ordre Transport (N.I.)
          </button>
        </div>
      </div>

      {fetchError && (
        <div className="bg-amber-500/10 border border-amber-500/30 p-4 rounded-2xl flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-bold text-amber-300">{fetchError}</p>
            <p className="text-[11px] text-slate-400 mt-1">
              Les écrans n'affichent que des données réellement retournées par l'API ;
              aucun lot de démonstration n'est injecté en fallback.
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Ordres Transport', value: ordres.length, icon: Truck, color: 'text-indigo-400' },
          { label: 'En Transit', value: enTransit, icon: ArrowRight, color: 'text-cyan-400' },
          { label: 'Livrés', value: livres, icon: CheckCircle2, color: 'text-emerald-400' },
          { label: 'Carnets TIR', value: carnets.length, icon: Shield, color: 'text-amber-400' },
        ].map((s) => (
          <div key={s.label} className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">{s.label}</span>
              <s.icon className={`w-4 h-4 ${s.color}`} />
            </div>
            <p className={`text-2xl font-black mt-2 ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-slate-800 flex items-center gap-3">
          <Truck className="w-5 h-5 text-indigo-400" />
          <h2 className="text-base font-black text-white">Ordres de Transport International</h2>
          <span className="ml-auto text-xs text-slate-400">{ordres.length} ordres</span>
        </div>
        {loading ? (
          <div className="p-12 text-center text-slate-400"><RefreshCw className="w-6 h-6 animate-spin text-indigo-400 mx-auto mb-2" /></div>
        ) : ordres.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <Globe className="w-10 h-10 text-slate-400 mx-auto mb-2" />
            <p className="font-bold text-white">Aucun ordre de transport international</p>
            <p className="text-xs text-slate-500 mt-1">
              {fetchError
                ? "Liste indisponible : l'API n'a pas répondu."
                : "Aucun OT enregistré en base. Le bouton de création ouvre actuellement un point d'entrée non implémenté (pickers FK manquants)."}
            </p>
          </div>
        ) : (
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
                    <td className="px-5 py-4 text-slate-300">
                      {o.poids_net != null ? Number(o.poids_net).toLocaleString('fr-FR') : ''}
                    </td>
                    <td className="px-5 py-4">
                      <span className={`px-2.5 py-1 rounded-xl text-[11px] font-bold uppercase border ${getStatutBadge(o.statut)}`}>
                        {o.statut || ''}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        {o.statut === STATUTS.PLANIFIE || o.statut === STATUTS.EN_CHARGEMENT ? (
                          <button onClick={() => handleEnTransit(o.id)} className="px-3 py-1.5 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-400 border border-cyan-500/30 text-xs font-bold transition-all">
                            → Transit
                          </button>
                        ) : o.statut === STATUTS.EN_TRANSIT ? (
                          <button onClick={() => handleLivrer(o.id)} className="px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-bold transition-all">
                            Livrer
                          </button>
                        ) : null}
                      </div>
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
