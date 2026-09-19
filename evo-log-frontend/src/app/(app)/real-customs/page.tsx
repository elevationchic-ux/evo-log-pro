'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldAlert, CheckCircle2, AlertTriangle, XCircle, Search,
  RefreshCw, Send, Download, FileText, Landmark, Clock, ArrowUpRight
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface CircuitResult {
  numero_dum: string;
  systeme: string;
  circuit: 'VERT' | 'BLEU' | 'JAUNE' | 'ROUGE';
  statut_recevabilite: string;
  date_attribution: string;
  description: string;
  delai_traitement_estime: string;
  inspecteur_assigne: string;
  quittance_tresor_emise: boolean;
  numero_quittance?: string | null;
}

interface CautionsStatut {
  banque_cautionnaire: string;
  plafond_autorise_xaf: number;
  montant_engage_xaf: number;
  disponible_xaf: number;
  taux_utilisation_pourcent: number;
  alerte_depassement: boolean;
  dossiers_en_cours: any[];
}

export default function RealCustomsPage() {
  const [dumInput, setDumInput] = useState('DUM-2026-IM4-8842');
  const [circuit, setCircuit] = useState<CircuitResult | null>(null);
  const [cautions, setCautions] = useState<CautionsStatut | null>(null);
  const [loading, setLoading] = useState(false);
  const [transmitting, setTransmitting] = useState(false);
  const [txMessage, setTxMessage] = useState<string | null>(null);

  const fetchCautionStatus = useCallback(async () => {
    try {
      const res = await apiClient.get('/api/v1/real-customs/cautions/statut');
      if (res.data) {
        setCautions(res.data);
      }
    } catch (err) {
      console.error('Erreur caution status:', err);
    }
  }, []);

  const handleSearchCircuit = async () => {
    if (!dumInput) return;
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/real-customs/camcis/circuits/${encodeURIComponent(dumInput)}`);
      setCircuit(res.data);
    } catch (err) {
      console.error('Erreur recherche circuit:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTeletransmettre = async () => {
    setTransmitting(true);
    setTxMessage(null);
    try {
      const res = await apiClient.post('/api/v1/real-customs/camcis/teletransmettre', {
        numero_dum: dumInput,
        valeur_cif_xaf: 35000000.0,
        bureau: 'DLA-PORT VII'
      });
      setTxMessage(`DUM transmise avec succès ! Quittance: ${res.data?.numero_quittance || 'OK'}`);
      handleSearchCircuit();
    } catch (err) {
      console.error('Erreur télétransmission:', err);
      setTxMessage('Erreur lors de la télétransmission.');
    } finally {
      setTransmitting(false);
    }
  };

  useEffect(() => {
    fetchCautionStatus();
    handleSearchCircuit();
  }, [fetchCautionStatus]);

  const getCircuitBadge = (c: string) => {
    switch (c) {
      case 'VERT':
        return { bg: 'bg-emerald-500/20', text: 'text-emerald-400', border: 'border-emerald-500/40', icon: CheckCircle2, label: 'Circuit VERT — BAE Immédiat' };
      case 'BLEU':
        return { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/40', icon: CheckCircle2, label: 'Circuit BLEU — Audit a posteriori' };
      case 'JAUNE':
        return { bg: 'bg-amber-500/20', text: 'text-amber-400', border: 'border-amber-500/40', icon: AlertTriangle, label: 'Circuit JAUNE — Examen Documentaire' };
      case 'ROUGE':
      default:
        return { bg: 'bg-rose-500/20', text: 'text-rose-400', border: 'border-rose-500/40', icon: XCircle, label: 'Circuit ROUGE — Scanner & Visite Physique' };
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-2">
            <ShieldAlert className="w-3.5 h-3.5" /> Douane Camerounaise • CAMCIS & Guichet Unique GUCE
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Passerelle Douane & Circuits CAMCIS
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Supervision temps-réel du ciblage douanier, télétransmission EDI Sydonia World, et gestion des crédits d'enlèvement.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => { fetchCautionStatus(); handleSearchCircuit(); }}
            className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all shadow-md active:scale-95"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </button>
        </div>
      </div>

      {/* Cautions & Plafonds Crédits d'Enlèvement */}
      {cautions && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">Caution Globale</span>
              <Landmark className="w-4 h-4 text-emerald-400" />
            </div>
            <p className="text-xl font-black text-white mt-2">
              {(cautions.plafond_autorise_xaf || 0).toLocaleString('fr-FR')} XAF
            </p>
            <p className="text-[11px] text-slate-400 mt-1">Banque: {cautions.banque_cautionnaire}</p>
          </div>

          <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">Montant Engagé</span>
              <Clock className="w-4 h-4 text-amber-400" />
            </div>
            <p className="text-xl font-black text-amber-400 mt-2">
              {(cautions.montant_engage_xaf || 0).toLocaleString('fr-FR')} XAF
            </p>
            <p className="text-[11px] text-slate-400 mt-1">Taux: {cautions.taux_utilisation_pourcent}%</p>
          </div>

          <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">Disponible Immédiat</span>
              <ArrowUpRight className="w-4 h-4 text-cyan-400" />
            </div>
            <p className="text-xl font-black text-cyan-400 mt-2">
              {(cautions.disponible_xaf || 0).toLocaleString('fr-FR')} XAF
            </p>
            <p className="text-[11px] text-slate-400 mt-1">Crédit d'enlèvement actif</p>
          </div>

          <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">Alerte Seuil Dépassement</span>
              <AlertTriangle className={`w-4 h-4 ${cautions.alerte_depassement ? 'text-rose-400' : 'text-emerald-400'}`} />
            </div>
            <p className={`text-xl font-black mt-2 ${cautions.alerte_depassement ? 'text-rose-400' : 'text-emerald-400'}`}>
              {cautions.alerte_depassement ? 'CRITIQUE (>80%)' : 'SÉCURISÉ'}
            </p>
            <p className="text-[11px] text-slate-400 mt-1">{cautions.dossiers_en_cours?.length || 0} dossiers en cours</p>
          </div>
        </div>
      )}

      {/* Query Bar */}
      <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-3xl flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="flex-1 flex items-center gap-3 w-full">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={dumInput}
              onChange={(e) => setDumInput(e.target.value)}
              placeholder="Numéro DUM (ex: DUM-2026-IM4-8842)"
              className="w-full bg-slate-950/60 border border-slate-800 rounded-2xl pl-11 pr-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500 transition-colors"
            />
          </div>
          <button
            onClick={handleSearchCircuit}
            disabled={loading}
            className="px-5 py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-900/20 transition-all"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            Vérifier CAMCIS
          </button>
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <button
            onClick={handleTeletransmettre}
            disabled={transmitting}
            className="flex-1 md:flex-none px-5 py-3 rounded-2xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-cyan-900/20 transition-all"
          >
            <Send className="w-4 h-4" />
            Télétransmettre DUM
          </button>
        </div>
      </div>

      {txMessage && (
        <div className="p-4 rounded-2xl bg-slate-800/90 border border-cyan-500/40 text-cyan-300 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          {txMessage}
        </div>
      )}

      {/* Circuit Detail Card */}
      {circuit && (() => {
        const badge = getCircuitBadge(circuit.circuit);
        const Icon = badge.icon;
        return (
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-3xl space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
              <div>
                <div className="text-xs text-slate-400">Résultat d'analyse de risque douanier</div>
                <h2 className="text-2xl font-black text-white mt-1">{circuit.numero_dum}</h2>
                <div className="text-xs text-slate-400 mt-1">{circuit.systeme} • {circuit.date_attribution}</div>
              </div>
              <div className={`px-5 py-3 rounded-2xl border ${badge.bg} ${badge.border} ${badge.text} flex items-center gap-3`}>
                <Icon className="w-6 h-6" />
                <div>
                  <div className="text-xs uppercase tracking-wider font-bold">Circuit Attribué</div>
                  <div className="text-lg font-black">{badge.label}</div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800/60">
                <span className="text-xs font-medium text-slate-400">Action Douanière Requise</span>
                <p className="text-sm font-bold text-white mt-1">{circuit.description}</p>
                <p className="text-xs text-slate-400 mt-2">Délai estimé: <strong className="text-slate-200">{circuit.delai_traitement_estime}</strong></p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800/60">
                <span className="text-xs font-medium text-slate-400">Inspecteur Assigné</span>
                <p className="text-sm font-bold text-white mt-1">{circuit.inspecteur_assigne}</p>
                <p className="text-xs text-slate-400 mt-2">Statut: <span className="text-emerald-400 font-bold">{circuit.statut_recevabilite}</span></p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800/60">
                <span className="text-xs font-medium text-slate-400">Quittance du Trésor Public</span>
                <p className="text-sm font-bold text-white mt-1">
                  {circuit.numero_quittance ? circuit.numero_quittance : 'En attente de validation'}
                </p>
                <p className="text-xs text-slate-400 mt-2">
                  Paiement: {circuit.quittance_tresor_emise ? <span className="text-emerald-400 font-bold">Acquitté</span> : <span className="text-amber-400 font-bold">En suspens</span>}
                </p>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
}
