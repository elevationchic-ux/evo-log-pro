'use client';

import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  Package,
  Search,
  CheckCircle2,
  Clock,
  AlertTriangle,
  FileText,
  Download,
  Calendar,
  Truck,
  Anchor,
  ShieldCheck,
  Plus,
  MapPin,
  X,
  ExternalLink
} from 'lucide-react';
import { b2bPortalAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function SuiviDossiersPortailB2B() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('q') || 'MSKU9823412';

  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [loading, setLoading] = useState(false);
  const [trackingResult, setTrackingResult] = useState<any | null>(null);
  const [dossiersList, setDossiersList] = useState<any[]>([]);
  const [selectedDossier, setSelectedDossier] = useState<any | null>(null);

  // E-Booking Modal
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);
  const [bookingTerminal, setBookingTerminal] = useState('DIT Terminal Port Douala');
  const [bookingDate, setBookingDate] = useState('2026-09-15');
  const [bookingSlot, setBookingSlot] = useState('08:00 - 12:00');
  const [bookingContainer, setBookingContainer] = useState('MSKU9823412');
  const [isSubmittingBooking, setIsSubmittingBooking] = useState(false);

  // Quote Modal
  const [isQuoteModalOpen, setIsQuoteModalOpen] = useState(false);
  const [quoteTcType, setQuoteTcType] = useState('40FT');
  const [quoteDest, setQuoteDest] = useState('Yaoundé Nsam');
  const [quoteWeight, setQuoteWeight] = useState('28000');
  const [calculatedQuote, setCalculatedQuote] = useState<any | null>(null);

  useEffect(() => {
    loadDossiers();
    if (initialQuery) {
      handleSearch(initialQuery);
    }
  }, []);

  const loadDossiers = async () => {
    try {
      const res = await b2bPortalAPI.getDossiers(1);
      const data = res.data || (Array.isArray(res) ? res : []);
      setDossiersList(data);
      if (data.length > 0) {
        setSelectedDossier(data[0]);
      }
    } catch (err) {
      console.error('Erreur chargement dossiers B2B', err);
    }
  };

  const handleSearch = async (queryToSearch?: string) => {
    const q = queryToSearch || searchQuery;
    if (!q) return;
    setLoading(true);
    try {
      const res = await b2bPortalAPI.trackCargo(q);
      const data = res.data || res;
      setTrackingResult(data);
      toast.success(`Tracking actualisé pour ${q}`);
    } catch (err) {
      toast.error('Erreur lors de la recherche du conteneur.');
    } finally {
      setLoading(false);
    }
  };

  const handleBookingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmittingBooking(true);
    try {
      const res = await b2bPortalAPI.createBooking({
        terminal: bookingTerminal,
        date_enlevement: bookingDate,
        creneau_horaire: bookingSlot,
        conteneur_no: bookingContainer
      });
      const data = res.data || res;
      toast.success(data.message || 'Réservation e-Booking confirmée avec succès !');
      setIsBookingModalOpen(false);
    } catch (err) {
      toast.error('Erreur lors de la création de la réservation e-Booking');
    } finally {
      setIsSubmittingBooking(false);
    }
  };

  const handleCalculateQuote = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await b2bPortalAPI.createQuote({
        type_fret: 'MARITIME',
        tc_type: quoteTcType,
        destination: quoteDest,
        poids_estime_kg: parseFloat(quoteWeight) || 20000
      });
      const data = res.data || res;
      setCalculatedQuote(data);
      toast.success('Devis instantané calculé !');
    } catch (err) {
      toast.error('Erreur lors du calcul du devis');
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 to-violet-950 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
                Portail Client • Suivi & E-Booking
              </span>
              <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                T-Code : KB2B_TRK
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
              <Package className="w-8 h-8 text-violet-400" />
              Suivi Dossiers, Tracking Conteneur & e-POD
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Visibilité temps réel sur vos conteneurs ISO 6346, état des franchises surestaries, documents GED et bons d'enlèvement.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setIsBookingModalOpen(true)}
              className="px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-bold flex items-center gap-2 shadow-lg shadow-violet-600/30 transition-all cursor-pointer"
            >
              <Calendar className="w-4 h-4" /> e-Booking Enlèvement
            </button>
            <button
              onClick={() => setIsQuoteModalOpen(true)}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold flex items-center gap-2 transition-all cursor-pointer"
            >
              <Plus className="w-4 h-4 text-violet-400" /> Simuler un Devis
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mt-6 flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-violet-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par N° Conteneur (ex: MSKU9823412, CMAU7461920) ou N° BL..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-violet-500/40 rounded-xl text-sm font-mono text-slate-100 placeholder-slate-500 focus:outline-none focus:border-violet-400"
            />
          </div>
          <button
            onClick={() => handleSearch()}
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-violet-600/30 transition-all cursor-pointer disabled:opacity-50"
          >
            {loading ? 'Recherche...' : 'Rechercher'}
          </button>
        </div>
      </div>

      {/* Tracking Result View */}
      {trackingResult && (
        <div className="bg-slate-900/90 border border-violet-500/30 rounded-3xl p-6 shadow-xl space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800 pb-5">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-lg font-black text-violet-400">{trackingResult.query}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-violet-500/10 text-violet-300 border border-violet-500/20">
                  {trackingResult.type_recherche}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                  {trackingResult.statut_actuel}
                </span>
              </div>
              <div className="text-xs text-slate-400 flex items-center gap-2 mt-1.5">
                <MapPin className="w-3.5 h-3.5 text-violet-400" /> Position : <span className="text-slate-200 font-semibold">{trackingResult.position_actuelle}</span>
                • Navire : <span className="text-slate-200 font-semibold">{trackingResult.navire}</span>
              </div>
            </div>

            {/* Franchise Surestaries Banner */}
            <div className="bg-slate-950 p-3.5 rounded-2xl border border-slate-800 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <div className="text-[10px] font-bold text-slate-400 uppercase">Franchise Surestaries Armateur</div>
                <div className="text-sm font-black font-mono text-slate-200">
                  <span className="text-emerald-400">{trackingResult.franchise_surestaries.jours_restants} jours restants</span> / {trackingResult.franchise_surestaries.jours_accordes} j accordés
                </div>
              </div>
            </div>
          </div>

          {/* Stepper Multi-Jalons */}
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Jalons & Chaîne Logistique</h3>
            <div className="space-y-3">
              {trackingResult.jalons.map((step: any, index: number) => (
                <div
                  key={index}
                  className={`flex items-start gap-4 p-3 rounded-2xl border transition-all ${
                    step.statut === 'DONE'
                      ? 'bg-slate-950/40 border-emerald-500/20 text-slate-300'
                      : step.statut === 'IN_PROGRESS'
                      ? 'bg-violet-950/20 border-violet-500/40 text-slate-100 shadow-md shadow-violet-950/50'
                      : 'bg-slate-950/20 border-slate-800/60 text-slate-400'
                  }`}
                >
                  <div
                    className={`w-7 h-7 rounded-xl flex items-center justify-center shrink-0 text-xs font-black mt-0.5 ${
                      step.statut === 'DONE'
                        ? 'bg-emerald-500 text-white shadow-md shadow-emerald-500/20'
                        : step.statut === 'IN_PROGRESS'
                        ? 'bg-violet-600 text-white animate-pulse'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {step.statut === 'DONE' ? '✓' : index + 1}
                  </div>
                  <div className="flex-1">
                    <div className="text-xs font-bold font-sans flex items-center justify-between">
                      <span>{step.etape}</span>
                      <span className="font-mono text-[11px] text-slate-400">{step.date}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Dossiers Actifs & Documents Téléchargeables */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Mes Dossiers Actifs</h3>
          <div className="space-y-3">
            {dossiersList.map((d) => (
              <div
                key={d.dossier_id}
                onClick={() => setSelectedDossier(d)}
                className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                  selectedDossier?.dossier_id === d.dossier_id
                    ? 'bg-violet-950/30 border-violet-500 text-white shadow-lg'
                    : 'bg-slate-900/80 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-xs font-bold text-violet-400">{d.dossier_id}</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-950 text-slate-300">
                    {d.statut}
                  </span>
                </div>
                <div className="text-xs font-semibold line-clamp-2">{d.description}</div>
                <div className="text-[10px] text-slate-400 mt-2 flex items-center justify-between">
                  <span>Conteneur: {d.conteneur_no}</span>
                  <span className="font-mono text-emerald-400">{d.montant_ht_xaf.toLocaleString()} XAF</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Détail Dossier Sélectionné + GED + e-POD */}
        {selectedDossier && (
          <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-3xl p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-base font-black text-slate-100">{selectedDossier.description}</h3>
                <div className="text-xs text-slate-400 mt-0.5">
                  Commercial référent : {selectedDossier.commercial} • {selectedDossier.contact_tel}
                </div>
              </div>
              <span className="px-3 py-1 bg-violet-500/10 text-violet-300 border border-violet-500/20 rounded-xl text-xs font-bold font-mono">
                {selectedDossier.progression_pct}% COMPLET
              </span>
            </div>

            {/* Documents GED Associés */}
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Documents Officiels Téléchargeables</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {(selectedDossier.documents || []).map((doc: any, i: number) => {
                  const docName = typeof doc === 'string' ? doc : doc.nom;
                  const docSize = typeof doc === 'string' ? 'PDF' : doc.taille;
                  return (
                    <div
                      key={i}
                      className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800 hover:border-violet-500/40 transition-all"
                    >
                      <div className="flex items-center gap-2.5 truncate">
                        <FileText className="w-4 h-4 text-violet-400 shrink-0" />
                        <div className="truncate">
                          <div className="text-xs font-mono font-bold text-slate-200 truncate">{docName}</div>
                          <div className="text-[10px] text-slate-500">{docSize} • Certifié EVO-LOG</div>
                        </div>
                      </div>
                      <button
                        onClick={() => toast.success(`Téléchargement sécurisé : ${docName}`)}
                        className="p-1.5 hover:bg-slate-800 text-slate-400 hover:text-violet-300 rounded-lg cursor-pointer"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Preuve de livraison e-POD */}
            <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" /> Preuve de Livraison Dématérialisée (e-POD)
                </h4>
                {selectedDossier.epod?.signed ? (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    SIGNÉ ÉLECTRONIQUEMENT
                  </span>
                ) : (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    LIVRAISON EN ATTENTE
                  </span>
                )}
              </div>

              {selectedDossier.epod?.signed ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-slate-500">Réceptionnaire :</span>{' '}
                    <span className="font-bold text-slate-200">{selectedDossier.epod.recipient}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Horodatage certifié :</span>{' '}
                    <span className="font-mono text-slate-200">{new Date(selectedDossier.epod.timestamp).toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Plombs de sécurité :</span>{' '}
                    <span className="font-bold text-emerald-400">{selectedDossier.epod.plomb_status}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Position GPS :</span>{' '}
                    <span className="font-mono text-slate-300">{selectedDossier.epod.geoloc}</span>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-500">
                  La signature et les photos de plombage s'afficheront automatiquement dès remise physique par le chauffeur EVO-LOG.
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Modal e-Booking */}
      {isBookingModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-violet-500/40 rounded-3xl w-full max-w-lg p-6 text-white shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-base font-bold flex items-center gap-2">
                <Calendar className="w-5 h-5 text-violet-400" /> Réservation e-Booking d'Enlèvement
              </h3>
              <button onClick={() => setIsBookingModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleBookingSubmit} className="py-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Terminal Portuaire / Magasin</label>
                <select
                  value={bookingTerminal}
                  onChange={(e) => setBookingTerminal(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-violet-500"
                >
                  <option value="DIT Terminal Port Douala">DIT Terminal Port Autonome de Douala</option>
                  <option value="KMT Terminal Port de Kribi">Kribi Multipurpose Terminal (KMT)</option>
                  <option value="MAD EVO-LOG Bassa">Magasin MAD Sous Douane EVO-LOG Bassa</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Date d'Enlèvement</label>
                  <input
                    type="date"
                    value={bookingDate}
                    onChange={(e) => setBookingDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Créneau Horaire</label>
                  <select
                    value={bookingSlot}
                    onChange={(e) => setBookingSlot(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-violet-500"
                  >
                    <option value="08:00 - 12:00">Matin (08:00 - 12:00)</option>
                    <option value="12:00 - 16:00">Après-midi (12:00 - 16:00)</option>
                    <option value="16:00 - 20:00">Soir (16:00 - 20:00)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">N° Conteneur ISO 6346</label>
                <input
                  type="text"
                  value={bookingContainer}
                  onChange={(e) => setBookingContainer(e.target.value)}
                  placeholder="ex: MSKU9823412"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm font-mono text-slate-100 focus:outline-none focus:border-violet-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsBookingModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingBooking}
                  className="px-5 py-2.5 rounded-xl text-xs font-bold bg-violet-600 hover:bg-violet-500 text-white shadow-lg shadow-violet-600/30 cursor-pointer disabled:opacity-50"
                >
                  {isSubmittingBooking ? 'Validation...' : 'Confirmer le Créneau'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Devis Instantané */}
      {isQuoteModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-violet-500/40 rounded-3xl w-full max-w-lg p-6 text-white shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-base font-bold flex items-center gap-2">
                <Plus className="w-5 h-5 text-violet-400" /> Simulateur de Devis Instantané B2B
              </h3>
              <button onClick={() => setIsQuoteModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCalculateQuote} className="py-4 space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Type Conteneur</label>
                  <select
                    value={quoteTcType}
                    onChange={(e) => setQuoteTcType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-violet-500"
                  >
                    <option value="20FT">20 Pieds (EVP)</option>
                    <option value="40FT">40 Pieds (HC/Dry)</option>
                    <option value="CONVENTIONNEL">Marchandises diverses</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Poids Brut (kg)</label>
                  <input
                    type="number"
                    value={quoteWeight}
                    onChange={(e) => setQuoteWeight(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-violet-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Destination Livraison</label>
                <input
                  type="text"
                  value={quoteDest}
                  onChange={(e) => setQuoteDest(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-violet-500"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl text-xs font-bold bg-violet-600 hover:bg-violet-500 text-white shadow-lg shadow-violet-600/30 transition-all cursor-pointer"
              >
                Calculer la Cotation
              </button>

              {calculatedQuote && (
                <div className="mt-4 p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Devis N° :</span>
                    <span className="font-mono text-xs font-bold text-violet-400">{calculatedQuote.reference_devis}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Total Hors Taxes :</span>
                    <span className="font-mono font-bold">{calculatedQuote.total_ht_xaf.toLocaleString()} XAF</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">TVA 19.25% Cameroun :</span>
                    <span className="font-mono text-blue-400">{calculatedQuote.tva_19_25_xaf.toLocaleString()} XAF</span>
                  </div>
                  <div className="flex items-center justify-between text-sm pt-2 border-t border-slate-800">
                    <span className="font-bold text-slate-200">Total TTC :</span>
                    <span className="font-mono font-black text-emerald-400">{calculatedQuote.total_ttc_xaf.toLocaleString()} XAF</span>
                  </div>
                </div>
              )}
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
