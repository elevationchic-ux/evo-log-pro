'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Truck, MapPin, Package, CheckCircle2, Clock, AlertTriangle,
  Fuel, ShieldCheck, Phone, Navigation, Camera, Edit3, Send,
  RefreshCw, Check, AlertOctagon, HelpCircle, FileCheck, Layers
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

// Contrat réel de GET /api/v1/transport/missions (payload _mission_payload) :
// enum statut minuscule (planifiee|en_cours|terminee|annulee|en_retard),
// relations camion/chauffeur/client sérialisées en objets ou null.
interface MissionItem {
  id: number;
  reference?: string | null;
  type_mission?: string | null;
  statut: string;
  origine?: string | null;
  destination?: string | null;
  point_depart?: string | null;
  point_arrivee?: string | null;
  date_debut_prevue?: string | null;
  date_fin_prevue?: string | null;
  camion?: { id: number; immatriculation: string } | null;
  chauffeur?: { id: number; nom: string; prenom: string } | null;
  client?: { id: number; nom: string; telephone: string | null } | null;
  montant_fret?: number | null;
  numero_bl?: string | null;
}

const STATUT_LABELS: Record<string, string> = {
  planifiee: 'Planifiée',
  en_cours: 'En cours',
  terminee: 'Terminée',
  annulee: 'Annulée',
  en_retard: 'En retard',
};

function statutBadgeClasses(statut: string): string {
  switch (statut) {
    case 'en_cours': return 'bg-blue-500/15 text-blue-300';
    case 'terminee': return 'bg-emerald-500/15 text-emerald-300';
    case 'annulee': return 'bg-slate-500/15 text-slate-400';
    case 'en_retard': return 'bg-rose-500/15 text-rose-300';
    default: return 'bg-amber-500/15 text-amber-300';
  }
}

export default function PortailChauffeurPage() {
  const [activeTab, setActiveTab] = useState<'tournee' | 'inspection' | 'carburant' | 'epod' | 'sos'>('tournee');
  const [missions, setMissions] = useState<MissionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMission, setSelectedMission] = useState<MissionItem | null>(null);

  // Inspection state : aide-mémoire local uniquement. Aucun endpoint
  // d'inspection n'existe côté backend ; le formulaire n'affirme jamais
  // archiver quoi que ce soit (politique zéro mock).
  const [checklist, setChecklist] = useState({
    pneus: true,
    freins: true,
    feux: true,
    extincteur: true,
    niveaux_huile_eau: true,
    carte_grise: true,
    assurance_cemac: true,
    visite_technique: true,
  });

  // Carburant state : champs vides, aucune valeur d'exemple pré-remplie.
  const [fuelForm, setFuelForm] = useState({
    station: '',
    litrage: '',
    prix_litre: '',
    kilometrage: '',
    numero_ticket: '',
  });
  const [submittingFuel, setSubmittingFuel] = useState(false);

  // ePOD signature state
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasSignature, setHasSignature] = useState(false);
  const [receptionnaireNom, setReceptionnaireNom] = useState('');
  const [reserves, setReserves] = useState('');
  const [epodSubmitted, setEpodSubmitted] = useState(false);

  // SOS state : gravite + lieu saisis par le conducteur (champs requis côté API).
  const [sosType, setSosType] = useState('PANNE_MECANIQUE');
  const [sosLieu, setSosLieu] = useState('');
  const [sosComment, setSosComment] = useState('');
  const [sosSent, setSosSent] = useState(false);

  const fetchMissions = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/transport/missions');
      const data = res.data;
      const list = Array.isArray(data) ? data : (data.data || data.items || []);
      setMissions(list);
      if (list.length > 0 && !selectedMission) {
        setSelectedMission(list[0]);
      }
    } catch (err: any) {
      toast.error('Impossible de charger les missions du chauffeur');
    } finally {
      setLoading(false);
    }
  }, [selectedMission]);

  useEffect(() => {
    fetchMissions();
  }, [fetchMissions]);

  // Canvas signature handlers
  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    setIsDrawing(true);
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const rect = canvas.getBoundingClientRect();
    const x = 'touches' in e ? e.touches[0].clientX - rect.left : e.clientX - rect.left;
    const y = 'touches' in e ? e.touches[0].clientY - rect.top : e.clientY - rect.top;
    ctx.beginPath();
    ctx.moveTo(x, y);
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const rect = canvas.getBoundingClientRect();
    const x = 'touches' in e ? e.touches[0].clientX - rect.left : e.clientX - rect.left;
    const y = 'touches' in e ? e.touches[0].clientY - rect.top : e.clientY - rect.top;
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#1e293b';
    ctx.lineTo(x, y);
    ctx.stroke();
    setHasSignature(true);
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const clearSignature = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      setHasSignature(false);
    }
  };

  // Transition réelle : POST /missions/{id}/demarrer (le PUT {statut:'EN_ROUTE'}
  // n'existait pas — enum minuscule côté API, et le démarrage horodate aussi
  // le kilomètre de départ côté serveur).
  const handleDemarrerMission = async (missionId: number) => {
    try {
      await apiClient.post(`/api/v1/transport/missions/${missionId}/demarrer`, {});
      toast.success('Mission démarrée : passage en cours');
      fetchMissions();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur démarrage de la mission');
    }
  };

  const handleSubmitFuel = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingFuel(true);
    try {
      await apiClient.post('/api/v1/transport/fuel', {
        station: fuelForm.station,
        litrage: parseFloat(fuelForm.litrage),
        prix_litre: parseFloat(fuelForm.prix_litre),
        kilometrage: parseInt(fuelForm.kilometrage, 10),
        numero_ticket: fuelForm.numero_ticket,
        mission_id: selectedMission?.id,
      });
      toast.success('Plein de carburant enregistré avec succès');
      setFuelForm({
        station: '',
        litrage: '',
        prix_litre: '',
        kilometrage: '',
        numero_ticket: '',
      });
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur enregistrement carburant');
    } finally {
      setSubmittingFuel(false);
    }
  };

  const handleSubmitEpod = async () => {
    if (!selectedMission) {
      toast.error('Veuillez sélectionner une mission');
      return;
    }
    if (!receptionnaireNom) {
      toast.error('Nom du réceptionnaire requis');
      return;
    }
    try {
      const canvas = canvasRef.current;
      const signatureData = canvas ? canvas.toDataURL('image/png') : '';
      // Clés réelles de LivraisonRequest : signature, nom_receptionnaire, note.
      await apiClient.post(`/api/v1/transport/missions/${selectedMission.id}/livrer`, {
        signature: signatureData,
        nom_receptionnaire: receptionnaireNom,
        note: reserves,
      });
      toast.success('Émargement ePOD validé avec succès');
      setEpodSubmitted(true);
      fetchMissions();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur validation ePOD');
    }
  };

  // Contrat réel POST /api/v1/incidents/ : lieu + description requis,
  // type_accident et gravite (chaîne libre, minuscule par convention QHSE).
  const handleSendSos = async () => {
    if (!sosLieu.trim()) {
      toast.error('Lieu de l\'incident requis');
      return;
    }
    if (!sosComment.trim()) {
      toast.error('Description de la situation requise');
      return;
    }
    try {
      await apiClient.post('/api/v1/incidents/', {
        lieu: sosLieu.trim(),
        description: sosComment.trim(),
        type_accident: sosType,
        gravite: 'critique',
      });
      setSosSent(true);
      toast.success('Alerte SOS transmise à la tour de contrôle avec succès !');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Impossible d\'envoyer le SOS');
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header Conducteur */}
      <div className="bg-gradient-to-r from-slate-900 via-amber-950 to-slate-900 rounded-3xl p-6 sm:p-8 text-white border border-amber-900/40 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 text-xs font-bold uppercase tracking-wider">
            <Truck className="w-3.5 h-3.5" /> Portail Collaborateur Conducteur
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Espace Mobilité & Chauffeur Routier
          </h1>
          <p className="text-sm text-slate-300">
            Gestion tactile de votre tournée, inspection véhicule, carburant, signature ePOD et alertes sécurité.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchMissions}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold border border-slate-700 transition-colors shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </button>
          <button
            onClick={() => setActiveTab('sos')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition-colors shadow-lg shadow-rose-600/30"
          >
            <AlertOctagon className="w-4 h-4 animate-pulse" />
            SOS Incident
          </button>
        </div>
      </div>

      {/* Barre d'onglets ergonomique */}
      <div className="flex overflow-x-auto gap-2 p-1.5 bg-slate-900 rounded-2xl border border-slate-700">
        {[
          { id: 'tournee', label: 'Ma Tournée', icon: Navigation, count: missions.length },
          { id: 'inspection', label: 'Inspection Véhicule', icon: ShieldCheck },
          { id: 'carburant', label: 'Saisie Carburant', icon: Fuel },
          { id: 'epod', label: 'Émargement ePOD', icon: Edit3 },
          { id: 'sos', label: 'SOS / Litige Route', icon: AlertOctagon, danger: true },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl text-xs sm:text-sm font-bold whitespace-nowrap transition-all ${
                isActive
                  ? tab.danger
                    ? 'bg-rose-600 text-white shadow-md'
                    : 'bg-slate-900 text-slate-200 shadow-md border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/10'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={`px-2 py-0.5 rounded-full text-[11px] font-mono ${
                  isActive ? 'bg-slate-900 text-white' : 'bg-slate-700 text-slate-300'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Onglet 1 : Ma Tournée & Feuille de Route */}
      {activeTab === 'tournee' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Liste des missions */}
          <div className="lg:col-span-1 space-y-3">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-600" /> Vos Missions du Jour ({missions.length})
            </h2>

            {loading ? (
              <div className="p-8 text-center bg-slate-900 rounded-2xl border border-slate-700">
                <RefreshCw className="w-6 h-6 animate-spin mx-auto text-amber-600 mb-2" />
                <span className="text-xs text-slate-500">Chargement des missions...</span>
              </div>
            ) : missions.length === 0 ? (
              <div className="p-8 text-center bg-slate-900 rounded-2xl border border-slate-700">
                <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
                <p className="text-sm font-bold text-slate-200">Aucune mission enregistrée</p>
                <p className="text-xs text-slate-500">Le serveur ne renvoie aucune mission pour ce compte.</p>
              </div>
            ) : (
              missions.map((m) => (
                <div
                  key={m.id}
                  onClick={() => setSelectedMission(m)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                    selectedMission?.id === m.id
                      ? 'bg-amber-50/70 border-amber-400 shadow-md'
                      : 'bg-slate-900 border-slate-700 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-xs font-mono font-black text-slate-200">
                      {m.reference || `Mission #${m.id}`}
                    </span>
                    <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${statutBadgeClasses(m.statut)}`}>
                      {STATUT_LABELS[m.statut] || m.statut}
                    </span>
                  </div>

                  <div className="text-xs font-semibold text-slate-200 mb-1">
                    {m.client?.nom || 'Client non enregistré'}
                  </div>

                  <div className="flex items-center gap-1.5 text-xs text-slate-500">
                    <MapPin className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                    <span className="truncate">
                      {(m.origine || m.point_depart) && (m.destination || m.point_arrivee)
                        ? `${m.origine || m.point_depart} → ${m.destination || m.point_arrivee}`
                        : 'Itinéraire non enregistré'}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Détails de la mission sélectionnée & Actions terrain */}
          <div className="lg:col-span-2">
            {selectedMission ? (
              <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-700 gap-3">
                  <div>
                    <span className="text-xs font-mono text-amber-300 font-bold">
                      {STATUT_LABELS[selectedMission.statut] || selectedMission.statut}
                    </span>
                    <h2 className="text-xl font-black text-slate-200">
                      {selectedMission.reference || `Mission #${selectedMission.id}`}
                    </h2>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleDemarrerMission(selectedMission.id)}
                      disabled={selectedMission.statut !== 'planifiee' && selectedMission.statut !== 'en_retard'}
                      className="px-3 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-bold transition-colors"
                    >
                      Démarrer trajet
                    </button>
                    <button
                      onClick={() => {
                        setActiveTab('epod');
                      }}
                      disabled={selectedMission.statut === 'terminee' || selectedMission.statut === 'annulee'}
                      className="px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-xs font-bold transition-colors"
                    >
                      Signer ePOD
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-slate-800 border border-slate-700 space-y-2">
                    <span className="text-xs font-bold text-slate-500 uppercase">Itinéraire & Client</span>
                    <p className="text-sm font-bold text-slate-200">
                      {selectedMission.client?.nom || 'Client non enregistré'}
                    </p>
                    <p className="text-xs text-slate-400 flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-emerald-600" />
                      Origine : {selectedMission.origine || selectedMission.point_depart || 'Non enregistré'}
                    </p>
                    <p className="text-xs text-slate-400 flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-rose-600" />
                      Destination : {selectedMission.destination || selectedMission.point_arrivee || 'Non enregistré'}
                    </p>
                    {selectedMission.client?.telephone && (
                      <a
                        href={`tel:${selectedMission.client.telephone}`}
                        className="inline-flex items-center gap-2 text-xs font-bold text-indigo-600 mt-2 hover:underline"
                      >
                        <Phone className="w-3.5 h-3.5" /> Appeler le client : {selectedMission.client.telephone}
                      </a>
                    )}
                  </div>

                  <div className="p-4 rounded-xl bg-slate-800 border border-slate-700 space-y-2">
                    <span className="text-xs font-bold text-slate-500 uppercase">Véhicule & Cargaison</span>
                    <p className="text-sm font-bold text-slate-200">
                      Immatriculation : {selectedMission.camion?.immatriculation || 'Camion non affecté'}
                    </p>
                    <p className="text-xs text-slate-400 flex items-center gap-1.5">
                      <Package className="w-3.5 h-3.5 text-indigo-600" />
                      Type de mission : {selectedMission.type_mission || 'Non enregistré'}
                    </p>
                    <p className="text-xs text-slate-400 flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-slate-400" />
                      B/L : {selectedMission.numero_bl || 'Non rattaché'}
                    </p>
                    <p className="text-xs text-slate-400 flex items-center gap-1.5">
                      <Navigation className="w-3.5 h-3.5 text-slate-400" />
                      Fret : {selectedMission.montant_fret != null
                        ? `${selectedMission.montant_fret.toLocaleString()} FCFA`
                        : 'Non enregistré'}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center bg-slate-900 rounded-2xl border border-slate-700">
                <Navigation className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm font-bold text-slate-300">Sélectionnez une mission pour voir les détails</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Onglet 2 : Inspection Véhicule Début/Fin de Poste */}
      {activeTab === 'inspection' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-700">
            <div>
              <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" /> Checklist Sécurité & Contrôle Prise de Poste
              </h2>
              <p className="text-xs text-slate-500">
                Vérifiez chaque organe de sécurité avant de prendre le volant.
              </p>
            </div>
          </div>

          {/* Honnêteté zéro mock : aucun endpoint d'inspection n'existe côté
              serveur. Cette coche reste un aide-mémoire local, rien n'est
              transmis ni archivé — la page ne prétend pas le contraire. */}
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/40 flex items-start gap-3 text-xs">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <span className="text-amber-200">
              Service d'enregistrement d'inspection non déployé côté serveur :
              cette checklist est un aide-mémoire local uniquement. Aucune
              validation n'est transmise ni archivée. Signalez toute anomalie
              via l'onglet SOS Incident, qui alimente le registre réel des
              incidents.
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { key: 'pneus', label: 'État & Pression des Pneus' },
              { key: 'freins', label: 'Freinage & Circuits d’Air' },
              { key: 'feux', label: 'Éclairage & Signalisation' },
              { key: 'extincteur', label: 'Extincteur Conforme & Plombé' },
              { key: 'niveaux_huile_eau', label: 'Niveaux d’Huile & Liquides' },
              { key: 'carte_grise', label: 'Carte Grise à Bord' },
              { key: 'assurance_cemac', label: 'Assurance CEMAC Valide' },
              { key: 'visite_technique', label: 'Contrôle Technique à Jour' },
            ].map((item) => (
              <label
                key={item.key}
                className={`flex items-start gap-3 p-4 rounded-xl border cursor-pointer transition-all ${
                  checklist[item.key as keyof typeof checklist]
                    ? 'bg-emerald-50/60 border-emerald-500/50 text-slate-200'
                    : 'bg-rose-50/60 border-rose-500/50 text-rose-200'
                }`}
              >
                <input
                  type="checkbox"
                  checked={checklist[item.key as keyof typeof checklist]}
                  onChange={(e) => setChecklist({ ...checklist, [item.key]: e.target.checked })}
                  className="mt-0.5 rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4"
                />
                <span className="text-xs font-semibold">{item.label}</span>
              </label>
            ))}
          </div>

          <div className="pt-4 flex justify-end">
            <button
              onClick={() => setChecklist({
                pneus: true, freins: true, feux: true, extincteur: true,
                niveaux_huile_eau: true, carte_grise: true,
                assurance_cemac: true, visite_technique: true,
              })}
              className="px-6 py-2.5 rounded-xl bg-slate-700 hover:bg-slate-600 text-white text-xs font-bold transition-colors shadow-sm"
            >
              Réinitialiser l'aide-mémoire (local, non archivé)
            </button>
          </div>
        </div>
      )}

      {/* Onglet 3 : Saisie Carburant Express */}
      {activeTab === 'carburant' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6 max-w-2xl mx-auto">
          <div className="pb-4 border-b border-slate-700">
            <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
              <Fuel className="w-5 h-5 text-amber-600" /> Saisie Express Plein Carburant
            </h2>
            <p className="text-xs text-slate-500">
              Enregistrez immédiatement vos tickets de station-service avec kilométrage compteur.
            </p>
          </div>

          <form onSubmit={handleSubmitFuel} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Station-Service</label>
                <input
                  type="text"
                  required
                  value={fuelForm.station}
                  onChange={(e) => setFuelForm({ ...fuelForm, station: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-amber-500 outline-none"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">N° Ticket / Reçu</label>
                <input
                  type="text"
                  required
                  value={fuelForm.numero_ticket}
                  onChange={(e) => setFuelForm({ ...fuelForm, numero_ticket: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-amber-500 outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Volume (Litres)</label>
                <input
                  type="number"
                  inputMode="decimal"
                  step="0.01"
                  required
                  value={fuelForm.litrage}
                  onChange={(e) => setFuelForm({ ...fuelForm, litrage: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-amber-500 outline-none"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Prix / Litre (XAF)</label>
                <input
                  type="number"
                  inputMode="numeric"
                  required
                  value={fuelForm.prix_litre}
                  onChange={(e) => setFuelForm({ ...fuelForm, prix_litre: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-amber-500 outline-none"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Compteur Km</label>
                <input
                  type="number"
                  inputMode="numeric"
                  required
                  value={fuelForm.kilometrage}
                  onChange={(e) => setFuelForm({ ...fuelForm, kilometrage: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-amber-500 outline-none"
                />
              </div>
            </div>

            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/40 flex items-center justify-between text-xs">
              <span className="font-bold text-amber-200">Total calculé :</span>
              <span className="font-mono font-black text-amber-200 text-sm">
                {((parseFloat(fuelForm.litrage) || 0) * (parseFloat(fuelForm.prix_litre) || 0)).toLocaleString()} XAF
              </span>
            </div>

            <button
              type="submit"
              disabled={submittingFuel}
              className="w-full py-3 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold transition-colors shadow-sm"
            >
              {submittingFuel ? 'Enregistrement en cours...' : 'Enregistrer le ticket de carburant'}
            </button>
          </form>
        </div>
      )}

      {/* Onglet 4 : Émargement ePOD Tactile */}
      {activeTab === 'epod' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6 max-w-2xl mx-auto">
          <div className="pb-4 border-b border-slate-700">
            <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
              <Edit3 className="w-5 h-5 text-indigo-600" /> Signature Électronique de Livraison (ePOD)
            </h2>
            <p className="text-xs text-slate-500">
              Faites signer le réceptionnaire directement sur l’écran tactile.
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Nom du Réceptionnaire</label>
              <input
                type="text"
                placeholder="Ex: Jean-Paul MBIIDA"
                value={receptionnaireNom}
                onChange={(e) => setReceptionnaireNom(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Réserves éventuelles (si colis abîmé)</label>
              <textarea
                rows={2}
                placeholder="Indiquez les réserves ou 'Sans réserves'"
                value={reserves}
                onChange={(e) => setReserves(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-bold text-slate-300">Signature sur l’écran</label>
                <button
                  type="button"
                  onClick={clearSignature}
                  className="text-[11px] text-rose-600 font-bold hover:underline"
                >
                  Effacer
                </button>
              </div>

              <div className="border-2 border-dashed border-slate-600 rounded-2xl p-1 bg-slate-800">
                <canvas
                  ref={canvasRef}
                  width={500}
                  height={180}
                  onMouseDown={startDrawing}
                  onMouseMove={draw}
                  onMouseUp={stopDrawing}
                  onMouseLeave={stopDrawing}
                  onTouchStart={startDrawing}
                  onTouchMove={draw}
                  onTouchEnd={stopDrawing}
                  className="w-full h-44 touch-none cursor-crosshair bg-slate-900 rounded-xl"
                />
              </div>
            </div>

            <button
              type="button"
              disabled={!hasSignature || epodSubmitted}
              onClick={handleSubmitEpod}
              className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-xs font-bold transition-colors shadow-sm"
            >
              {epodSubmitted ? 'Livraison Validée avec Succès' : 'Valider & Enregistrer l’ePOD'}
            </button>
          </div>
        </div>
      )}

      {/* Onglet 5 : SOS Incident & Litige Route */}
      {activeTab === 'sos' && (
        <div className="bg-slate-900 rounded-2xl border border-rose-500/40 p-6 space-y-6 max-w-2xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-rose-500/30 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-rose-200 flex items-center gap-2">
                <AlertOctagon className="w-5 h-5 text-rose-600" /> Déclenchement d’Alerte Terrain / SOS
              </h2>
              <p className="text-xs text-rose-300">
                Signale immédiatement un événement critique au poste de contrôle et à la direction.
              </p>
            </div>
            {sosSent && (
              <span className="px-3 py-1 rounded-full bg-rose-500/15 text-rose-300 text-xs font-bold">
                Alerte transmise
              </span>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Nature de l’Incident</label>
              <select
                value={sosType}
                onChange={(e) => setSosType(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-rose-500 outline-none"
              >
                <option value="PANNE_MECANIQUE">Panne mécanique (Moteur / Boîte / Freinage)</option>
                <option value="CREVAISON">Crevaison multiple / Éclatement pneu</option>
                <option value="ACCIDENT">Accident de la circulation</option>
                <option value="BARRAGE_CORRIDOR">Blocage / Barrage routier / Tracasserie</option>
                <option value="LITIGE_PESAGE">Litige au pont-bascule / Surcharge</option>
                <option value="VOL_AGRESSION">Tentative de vol / Agression</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Lieu de l'incident (obligatoire)</label>
              <input
                type="text"
                value={sosLieu}
                onChange={(e) => setSosLieu(e.target.value)}
                placeholder="Ex: PK 145 axe Douala–Edéa"
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-rose-500 outline-none"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Précisions sur la situation (obligatoire)</label>
              <textarea
                rows={3}
                placeholder="Ex: Fumée blanche au moteur. Besoin d'une dépanneuse."
                value={sosComment}
                onChange={(e) => setSosComment(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-rose-500 outline-none"
              />
            </div>

            <button
              type="button"
              onClick={handleSendSos}
              className="w-full py-3.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-black uppercase tracking-wider transition-colors shadow-lg shadow-rose-600/30 flex items-center justify-center gap-2"
            >
              <AlertOctagon className="w-4 h-4" /> Envoyer l’alerte immédiate à la tour de contrôle
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
