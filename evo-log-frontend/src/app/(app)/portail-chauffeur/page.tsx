'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Truck, MapPin, Package, CheckCircle2, Clock, AlertTriangle,
  Fuel, ShieldCheck, Phone, Navigation, Camera, Edit3, Send,
  RefreshCw, Check, AlertOctagon, HelpCircle, FileCheck, Layers
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { Card, CardBody, CardHeader } from '@/components/design-system/Card';
import { Button } from '@/components/design-system/Button';
import { EmptyStates } from '@/components/design-system/EmptyState';
import { Input } from '@/components/design-system/Input';

interface MissionItem {
  id: number;
  numero_ordre?: string;
  reference?: string;
  client_nom?: string;
  telephone_client?: string;
  origine?: string;
  destination?: string;
  immatriculation?: string;
  statut: string;
  date_depart_prevue?: string;
  marchandise?: string;
  poids_kg?: number;
}

export default function PortailChauffeurPage() {
  const [activeTab, setActiveTab] = useState<'tournee' | 'inspection' | 'carburant' | 'epod' | 'sos'>('tournee');
  const [missions, setMissions] = useState<MissionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMission, setSelectedMission] = useState<MissionItem | null>(null);

  // Inspection state
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
  const [inspectionSubmitted, setInspectionSubmitted] = useState(false);

  // Carburant state
  const [fuelForm, setFuelForm] = useState({
    station: 'TotalEnergies Douala',
    litrage: '250',
    prix_litre: '828',
    kilometrage: '145200',
    numero_ticket: 'TKT-2026-09-88',
  });
  const [submittingFuel, setSubmittingFuel] = useState(false);

  // ePOD signature state
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasSignature, setHasSignature] = useState(false);
  const [receptionnaireNom, setReceptionnaireNom] = useState('');
  const [reserves, setReserves] = useState('');
  const [epodSubmitted, setEpodSubmitted] = useState(false);

  // SOS state
  const [sosType, setSosType] = useState('PANNE_MECANIQUE');
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

  const handleUpdateMissionStatus = async (missionId: number, nouveauStatut: string) => {
    try {
      await apiClient.put(`/api/v1/transport/missions/${missionId}`, { statut: nouveauStatut });
      toast.success(`Statut mis à jour : ${nouveauStatut}`);
      fetchMissions();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur mise à jour statut');
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
        kilometrage: parseInt(fuelForm.kilometrage),
        numero_ticket: fuelForm.numero_ticket,
        mission_id: selectedMission?.id,
      });
      toast.success('Plein de carburant enregistré avec succès');
      setFuelForm({
        station: 'TotalEnergies Douala',
        litrage: '',
        prix_litre: '828',
        kilometrage: '',
        numero_ticket: '',
      });
    } catch (err: any) {
      toast.error('Erreur enregistrement carburant');
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
      await apiClient.post(`/api/v1/transport/missions/${selectedMission.id}/livrer`, {
        signature_base64: signatureData,
        nom_receptionnaire: receptionnaireNom,
        reserves: reserves || 'Sans réserves',
      });
      toast.success('Émargement ePOD validé avec succès');
      setEpodSubmitted(true);
      fetchMissions();
    } catch (err: any) {
      toast.error('Erreur validation ePOD');
    }
  };

  const handleSendSos = async () => {
    try {
      await apiClient.post('/api/v1/qhse/incidents', {
        titre: `[SOS CONDUCTEUR] ${sosType} - Camion ${selectedMission?.immatriculation || 'En route'}`,
        type_incident: sosType,
        severite: 'CRITIQUE',
        description: sosComment || `Alerte déclenchée par le conducteur sur le corridor. Mission ID: ${selectedMission?.id}`,
        lieu: selectedMission?.destination || 'Corridor CEMAC',
      });
      setSosSent(true);
      toast.success('Alerte SOS transmise à la tour de contrôle avec succès !');
    } catch (err: any) {
      toast.error('Impossible d’envoyer le SOS');
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
      <div className="flex overflow-x-auto gap-2 p-1.5 bg-slate-100 rounded-2xl border border-slate-200">
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
                    : 'bg-white text-slate-900 shadow-md border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={`px-2 py-0.5 rounded-full text-[11px] font-mono ${
                  isActive ? 'bg-slate-900 text-white' : 'bg-slate-200 text-slate-700'
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
            <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-600" /> Vos Missions du Jour ({missions.length})
            </h2>

            {loading ? (
              <div className="p-8 text-center bg-white rounded-2xl border border-slate-200">
                <RefreshCw className="w-6 h-6 animate-spin mx-auto text-amber-600 mb-2" />
                <span className="text-xs text-slate-500">Chargement des missions...</span>
              </div>
            ) : missions.length === 0 ? (
              <Card>
                <CardBody>
                  <EmptyStates.NoData
                    description="Aucune mission en attente. Toutes vos livraisons sont à jour."
                  />
                </CardBody>
              </Card>
            ) : (
              missions.map((m) => (
                <div
                  key={m.id}
                  onClick={() => setSelectedMission(m)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                    selectedMission?.id === m.id
                      ? 'bg-amber-50/70 border-amber-400 shadow-md'
                      : 'bg-white border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-xs font-mono font-black text-slate-800">
                      #{m.numero_ordre || m.reference || `MIS-${m.id}`}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      m.statut === 'EN_ROUTE' ? 'bg-blue-100 text-blue-700' :
                      m.statut === 'LIVRE' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                    }`}>
                      {m.statut}
                    </span>
                  </div>

                  <div className="text-xs font-semibold text-slate-900 mb-1">
                    {m.client_nom || 'Client Destinataire'}
                  </div>

                  <div className="flex items-center gap-1.5 text-xs text-slate-500">
                    <MapPin className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                    <span className="truncate">{m.origine || 'Douala'} → {m.destination || 'Corridor'}</span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Détails de la mission sélectionnée & Actions terrain */}
          <div className="lg:col-span-2">
            {selectedMission ? (
              <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-6 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
                  <div>
                    <span className="text-xs font-mono text-amber-700 font-bold">Mission Active</span>
                    <h2 className="text-xl font-black text-slate-900">
                      #{selectedMission.numero_ordre || selectedMission.reference || `MIS-${selectedMission.id}`}
                    </h2>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleUpdateMissionStatus(selectedMission.id, 'EN_ROUTE')}
                      className="px-3 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition-colors"
                    >
                      Démarrer trajet
                    </button>
                    <button
                      onClick={() => handleUpdateMissionStatus(selectedMission.id, 'ARRIVE_QUAI')}
                      className="px-3 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold transition-colors"
                    >
                      Arrivé quai
                    </button>
                    <button
                      onClick={() => {
                        setActiveTab('epod');
                      }}
                      className="px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-colors"
                    >
                      Signer ePOD
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-2">
                    <span className="text-xs font-bold text-slate-500 uppercase">Itinéraire & Client</span>
                    <p className="text-sm font-bold text-slate-900">{selectedMission.client_nom || 'Client Partenaire'}</p>
                    <p className="text-xs text-slate-600 flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-emerald-600" /> Origine : {selectedMission.origine || 'Port Autonome de Douala'}
                    </p>
                    <p className="text-xs text-slate-600 flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-rose-600" /> Destination : {selectedMission.destination || 'Terminal Yaoundé'}
                    </p>
                    {selectedMission.telephone_client && (
                      <a
                        href={`tel:${selectedMission.telephone_client}`}
                        className="inline-flex items-center gap-2 text-xs font-bold text-indigo-600 mt-2 hover:underline"
                      >
                        <Phone className="w-3.5 h-3.5" /> Appeler le client : {selectedMission.telephone_client}
                      </a>
                    )}
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-2">
                    <span className="text-xs font-bold text-slate-500 uppercase">Véhicule & Marchandise</span>
                    <p className="text-sm font-bold text-slate-900">
                      Immatriculation : {selectedMission.immatriculation || 'LT-TRUCK-889'}
                    </p>
                    <p className="text-xs text-slate-600 flex items-center gap-1.5">
                      <Package className="w-3.5 h-3.5 text-indigo-600" /> Colis : {selectedMission.marchandise || 'Conteneur Dry 40ft'}
                    </p>
                    <p className="text-xs text-slate-600 flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-slate-600" /> Poids : {selectedMission.poids_kg ? `${selectedMission.poids_kg} kg` : '24 500 kg'}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
                <Navigation className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm font-bold text-slate-700">Sélectionnez une mission pour voir les détails</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Onglet 2 : Inspection Véhicule Début/Fin de Poste */}
      {activeTab === 'inspection' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" /> Checklist Sécurité & Contrôle Prise de Poste
              </h2>
              <p className="text-xs text-slate-500">
                Vérifiez chaque organe de sécurité avant de prendre le volant.
              </p>
            </div>
            {inspectionSubmitted && (
              <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" /> Inspection validée
              </span>
            )}
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
                    ? 'bg-emerald-50/60 border-emerald-300 text-slate-900'
                    : 'bg-rose-50/60 border-rose-300 text-rose-900'
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
            <Button
              onClick={() => {
                const checkedItems = Object.values(checklist).filter(v => v).length;
                const totalItems = Object.keys(checklist).length;
                if (checkedItems === totalItems) {
                  toast.success('Inspection validée avec succès !');
                  setInspectionSubmitted(true);
                } else {
                  toast.error(`Vérifiez tous les items : ${checkedItems}/${totalItems} items conformes`);
                }
              }}
              className="w-full"
            >
              Valider la prise de poste
            </Button>
          </div>
        </div>
      )}

      {/* Onglet 3 : Saisie Carburant Express */}
      {activeTab === 'carburant' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-6 max-w-2xl mx-auto">
          <div className="pb-4 border-b border-slate-100">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Fuel className="w-5 h-5 text-amber-600" /> Saisie Express Plein Carburant
            </h2>
            <p className="text-xs text-slate-500">
              Enregistrez immédiatement vos tickets de station-service avec kilométrage compteur.
            </p>
          </div>

          <form onSubmit={handleSubmitFuel} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">Station-Service</label>
                <input
                  type="text"
                  required
                  value={fuelForm.station}
                  onChange={(e) => setFuelForm({ ...fuelForm, station: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-amber-500 outline-none"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">N° Ticket / Reçu</label>
                <input
                  type="text"
                  required
                  value={fuelForm.numero_ticket}
                  onChange={(e) => setFuelForm({ ...fuelForm, numero_ticket: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-amber-500 outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">Volume (Litres)</label>
                <input
                  type="number"
                  inputMode="decimal"
                  step="0.01"
                  required
                  value={fuelForm.litrage}
                  onChange={(e) => setFuelForm({ ...fuelForm, litrage: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-amber-500 outline-none"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">Prix / Litre (XAF)</label>
                <input
                  type="number"
                  inputMode="numeric"
                  required
                  value={fuelForm.prix_litre}
                  onChange={(e) => setFuelForm({ ...fuelForm, prix_litre: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-amber-500 outline-none"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">Compteur Km</label>
                <input
                  type="number"
                  inputMode="numeric"
                  required
                  value={fuelForm.kilometrage}
                  onChange={(e) => setFuelForm({ ...fuelForm, kilometrage: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-amber-500 outline-none"
                />
              </div>
            </div>

            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-between text-xs">
              <span className="font-bold text-amber-900">Total calculé :</span>
              <span className="font-mono font-black text-amber-900 text-sm">
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
        <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-6 max-w-2xl mx-auto">
          <div className="pb-4 border-b border-slate-100">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Edit3 className="w-5 h-5 text-indigo-600" /> Signature Électronique de Livraison (ePOD)
            </h2>
            <p className="text-xs text-slate-500">
              Faites signer le réceptionnaire directement sur l’écran tactile.
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Nom du Réceptionnaire</label>
              <input
                type="text"
                placeholder="Ex: Jean-Paul MBIIDA"
                value={receptionnaireNom}
                onChange={(e) => setReceptionnaireNom(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Réserves éventuelles (si colis abîmé)</label>
              <textarea
                rows={2}
                placeholder="Indiquez les réserves ou 'Sans réserves'"
                value={reserves}
                onChange={(e) => setReserves(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-bold text-slate-700">Signature sur l’écran</label>
                <button
                  type="button"
                  onClick={clearSignature}
                  className="text-[11px] text-rose-600 font-bold hover:underline"
                >
                  Effacer
                </button>
              </div>

              <div className="border-2 border-dashed border-slate-300 rounded-2xl p-1 bg-slate-50">
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
                  className="w-full h-44 touch-none cursor-crosshair bg-white rounded-xl"
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
        <div className="bg-white rounded-2xl border border-rose-200 p-6 space-y-6 max-w-2xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-rose-100 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-rose-900 flex items-center gap-2">
                <AlertOctagon className="w-5 h-5 text-rose-600" /> Déclenchement d’Alerte Terrain / SOS
              </h2>
              <p className="text-xs text-rose-700">
                Signale immédiatement un événement critique au poste de contrôle et à la direction.
              </p>
            </div>
            {sosSent && (
              <span className="px-3 py-1 rounded-full bg-rose-100 text-rose-800 text-xs font-bold">
                Alerte transmise
              </span>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Nature de l’Incident</label>
              <select
                value={sosType}
                onChange={(e) => setSosType(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-rose-500 outline-none"
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
              <label className="text-xs font-bold text-slate-700 block mb-1">Précisions sur la localisation et la situation</label>
              <textarea
                rows={3}
                placeholder="Ex: Arrêté au PK 145 entre Douala et Edéa. Fumée blanche au moteur. Besoin d'une dépanneuse."
                value={sosComment}
                onChange={(e) => setSosComment(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-rose-500 outline-none"
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
