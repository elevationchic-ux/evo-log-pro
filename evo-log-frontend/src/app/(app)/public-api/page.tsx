'use client';

import React, { useState, useEffect } from 'react';
import {
  Globe, Search, Anchor, DollarSign, Send, CheckCircle2,
  RefreshCw, Ship, Compass, ShieldCheck, ArrowRight
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function PublicApiPage() {
  const [rates, setRates] = useState<any[]>([]);
  const [ports, setPorts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Tracking public
  const [trackRef, setTrackRef] = useState('');
  const [trackResult, setTrackResult] = useState<any>(null);
  const [tracking, setTracking] = useState(false);
  const [trackError, setTrackError] = useState('');

  // Formulaire contact
  const [contactForm, setContactForm] = useState({
    nom: '',
    email: '',
    telephone: '',
    societe: '',
    sujet: 'Demande de cotation conteneur 40HC',
    message: 'Bonjour, nous souhaitons expédier 3 conteneurs 40 pieds d\'Anvers vers N\'Djamena via Douala.',
  });
  const [contactSuccess, setContactSuccess] = useState('');

  useEffect(() => {
    async function loadPublicData() {
      setLoading(true);
      try {
        const [resRates, resPorts] = await Promise.allSettled([
          apiClient.get('/api/v1/public/taux-devises'),
          apiClient.get('/api/v1/public/ports')
        ]);
        if (resRates.status === 'fulfilled' && resRates.value.data) {
          setRates(resRates.value.data);
        }
        if (resPorts.status === 'fulfilled' && resPorts.value.data) {
          setPorts(resPorts.value.data);
        }
      } catch (err) {
        console.error('Erreur chargement données publiques:', err);
      } finally {
        setLoading(false);
      }
    }
    loadPublicData();
  }, []);

  const handleTrack = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!trackRef.trim()) return;
    setTracking(true);
    setTrackError('');
    setTrackResult(null);
    try {
      const res = await apiClient.get(`/api/v1/public/track/${encodeURIComponent(trackRef.trim())}`);
      setTrackResult(res.data);
    } catch (err: any) {
      setTrackError('Aucune expédition trouvée pour cette référence. Veuillez vérifier votre saisie.');
    } finally {
      setTracking(false);
    }
  };

  const handleContactSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await apiClient.post('/api/v1/public/contact', contactForm);
      setContactSuccess(res.data.message || 'Votre message a bien été transmis.');
      setContactForm({
        nom: '',
        email: '',
        telephone: '',
        societe: '',
        sujet: '',
        message: '',
      });
    } catch (err) {
      console.error('Erreur envoi contact public:', err);
    }
  };

  return (
    <div className="space-y-8 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 p-8 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-bold uppercase tracking-wider mb-2">
          <Globe className="w-3.5 h-3.5" /> Services Ouverts au Public & Chargeurs
        </div>
        <h1 className="text-3xl font-black text-white tracking-tight">
          Portail Public & Suivi Libre d'Expéditions
        </h1>
        <p className="text-xs text-slate-400 mt-2 max-w-2xl">
          Consultez en libre accès les informations officielles : traçabilité de votre fret conteneurisé, taux de référence de la Banque des États de l'Afrique Centrale (BEAC) et annuaire des terminaux portuaires.
        </p>
      </div>

      {/* Public Tracking Section */}
      <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-3xl shadow-xl space-y-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Search className="w-5 h-5 text-cyan-400" /> Suivi Public de Conteneur ou Dossier
        </h2>
        <p className="text-xs text-slate-400">
          Entrez un numéro de conteneur (ex: MSKU-908123), un numéro de dossier de transit ou un numéro de connaissement :
        </p>

        <form onSubmit={handleTrack} className="flex gap-3 max-w-xl">
          <input
            type="text"
            required
            placeholder="ex: MSKU-908123, DOS-2026-001..."
            value={trackRef}
            onChange={(e) => setTrackRef(e.target.value)}
            className="flex-1 px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
          <button
            type="submit"
            disabled={tracking}
            className="px-6 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-bold rounded-xl flex items-center gap-2 disabled:opacity-50 shadow-lg shadow-cyan-600/20 transition-all"
          >
            {tracking ? 'Recherche...' : <><Search className="w-4 h-4" /> Suivre</>}
          </button>
        </form>

        {trackError && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-xs text-rose-400 font-medium">
            {trackError}
          </div>
        )}

        {trackResult && (
          <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-xs font-mono font-bold text-cyan-400">
                Réf. {trackResult.reference}
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-bold">
                {trackResult.statut}
              </span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div>
                <span className="text-slate-500 block">Type :</span>
                <span className="font-semibold text-white uppercase">{trackResult.type}</span>
              </div>
              {trackResult.port_actuel && (
                <div>
                  <span className="text-slate-500 block">Port actuel :</span>
                  <span className="font-semibold text-white">{trackResult.port_actuel}</span>
                </div>
              )}
              {trackResult.emplacement && (
                <div>
                  <span className="text-slate-500 block">Emplacement :</span>
                  <span className="font-semibold text-white">{trackResult.emplacement}</span>
                </div>
              )}
              {trackResult.destination && (
                <div>
                  <span className="text-slate-500 block">Destination :</span>
                  <span className="font-semibold text-white">{trackResult.destination}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Grid Rates & Ports */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* BEAC Rates */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-emerald-400" /> Taux Officiels BEAC en Vigueur
          </h3>
          <p className="text-xs text-slate-400">
            Cours de change applicables aux déclarations douanières et règlements du commerce extérieur :
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2.5 px-3">Devise</th>
                  <th className="py-2.5 px-3">Taux Achat (XAF)</th>
                  <th className="py-2.5 px-3">Taux Vente (XAF)</th>
                  <th className="py-2.5 px-3">Taux Moyen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {rates.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="py-6 text-center text-slate-500">
                      Taux BEAC fixes : 1 EUR = 655.957 XAF • 1 USD = 615.50 XAF
                    </td>
                  </tr>
                ) : (
                  rates.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-800/30">
                      <td className="py-2.5 px-3 font-bold text-cyan-400">{r.devise}</td>
                      <td className="py-2.5 px-3">{r.taux_achat}</td>
                      <td className="py-2.5 px-3">{r.taux_vente}</td>
                      <td className="py-2.5 px-3 font-semibold text-emerald-400">{r.taux_moyen || r.taux_achat}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Ports Directory */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Anchor className="w-5 h-5 text-blue-400" /> Terminaux Portuaires Camerounais
          </h3>
          <p className="text-xs text-slate-400">
            Capacités opérationnelles et tirants d'eau autorisés pour l'accostage maritime :
          </p>

          <div className="space-y-3">
            {ports.length === 0 ? (
              <div className="text-xs text-slate-500 py-6 text-center">
                Port Autonome de Douala (PAD) & Port Autonome de Kribi (PAK) opérationnels.
              </div>
            ) : (
              ports.map((p) => (
                <div key={p.id} className="p-4 rounded-2xl bg-slate-800/50 border border-slate-800 flex items-center justify-between">
                  <div>
                    <div className="font-bold text-white text-sm">{p.nom} ({p.code})</div>
                    <div className="text-xs text-slate-400">{p.ville} • {p.autorite_portuaire}</div>
                  </div>
                  <div className="text-right font-mono text-xs text-cyan-400">
                    Tirant : {p.tirant_eau_max || '11.5'} m
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Public Contact Form */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4 max-w-2xl mx-auto">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Send className="w-5 h-5 text-emerald-400" /> Demande de Renseignement ou Cotation
        </h3>
        <p className="text-xs text-slate-400">
          Nos équipes commerciales logistiques vous répondent sous 2 heures ouvrées :
        </p>

        {contactSuccess && (
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-xs text-emerald-400 font-medium">
            {contactSuccess}
          </div>
        )}

        <form onSubmit={handleContactSubmit} className="space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 mb-1 font-semibold">Nom complet</label>
              <input
                type="text"
                required
                value={contactForm.nom}
                onChange={(e) => setContactForm({ ...contactForm, nom: e.target.value })}
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1 font-semibold">Adresse Email</label>
              <input
                type="email"
                required
                value={contactForm.email}
                onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-semibold">Sujet de la demande</label>
            <input
              type="text"
              required
              value={contactForm.sujet}
              onChange={(e) => setContactForm({ ...contactForm, sujet: e.target.value })}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-semibold">Votre message</label>
            <textarea
              rows={3}
              required
              value={contactForm.message}
              onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <button
            type="submit"
            className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/20 transition-all"
          >
            Envoyer ma Demande
          </button>
        </form>
      </div>
    </div>
  );
}
