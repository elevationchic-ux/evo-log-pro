'use client';

import React, { useState, useEffect } from 'react';
import {
  Truck, MapPin, Zap, Navigation, AlertTriangle, CheckCircle2,
  Clock, User, Phone, Fuel, Package, BarChart3, ChevronRight,
  Activity, Shield, Target, RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { transportAPI } from '@/lib/api-client';
import { EmptyStates } from '@/components/design-system/EmptyState';
import { Button } from '@/components/design-system/Button';

interface VehicleData {
  id: string;
  immat: string;
  model: string;
  chauffeur: string;
  tel: string;
  statut: string;
  mission: string;
  position: string;
  gps: { lat: number; lng: number };
  kmParcourus: number;
  kmTotal: number;
  fuel: number;
  vitesse: number;
  carburantConsomme: number;
  poids: string;
  prochainArret: string;
  alerts: string[];
}

export default function TransportDispatchPage() {
  const [selectedVehicle, setSelectedVehicle] = useState<string | null>(null);
  const [fleet, setFleet] = useState<VehicleData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFleet();
  }, []);

  const loadFleet = async () => {
    try {
      const res = await transportAPI.getCamions();
      const d = res.data;
      const list = Array.isArray(d) ? d : (d?.items || (Array.isArray(res) ? res : []));
      // Transform API data to expected format
      const transformed = list.map((c: any) => ({
        id: c.id?.toString() || `TRK-${c.id}`,
        immat: c.immatriculation || 'N/A',
        model: c.modele || 'Modèle inconnu',
        chauffeur: c.chauffeur_nom || 'Non assigné',
        tel: c.chauffeur_telephone || 'N/A',
        statut: c.statut || 'DISPONIBLE',
        mission: c.mission_reference || '',
        position: c.position || 'Non disponible',
        gps: { lat: 0, lng: 0 },
        kmParcourus: c.km_parcourus || 0,
        kmTotal: c.km_total || 0,
        fuel: c.niveau_carburant || 0,
        vitesse: c.vitesse || 0,
        carburantConsomme: c.carburant_consomme || 0,
        poids: `${c.poids_actuel || 0} T / ${c.capacite || 30} T`,
        prochainArret: c.prochain_arret || 'Non disponible',
        alerts: c.alertes || []
      }));
      setFleet(transformed);
      if (transformed.length > 0 && !selectedVehicle) {
        setSelectedVehicle(transformed[0].id);
      }
    } catch (err) {
      console.error('Error loading fleet:', err);
      toast.error('Impossible de charger la flotte');
      setFleet([]);
    } finally {
      setLoading(false);
    }
  };

  const selectedVehicleData = fleet.find(v => v.id === selectedVehicle);

  const statutColors: Record<string, string> = {
    'EN_TRANSIT': 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    'CHARGEMENT': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    'LIVRAISON': 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    'DISPONIBLE': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  };

  const fleetKpis = [
    { label: 'Camions en Transit', value: fleet.filter(v => v.statut === 'EN_TRANSIT' || v.statut === 'EN TRANSIT').length, color: 'text-blue-400' },
    { label: 'En Chargement', value: fleet.filter(v => v.statut === 'CHARGEMENT').length, color: 'text-amber-400' },
    { label: 'En Livraison', value: fleet.filter(v => v.statut === 'LIVRAISON').length, color: 'text-purple-400' },
    { label: 'Disponibles', value: fleet.filter(v => v.statut === 'DISPONIBLE').length, color: 'text-emerald-400' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <Truck className="w-6 h-6 text-amber-400" /> Dispatch & Suivi Flotte en Temps Réel
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">GPS live · Affectation missions · Consommation carburant · e-POD · Alertes corridor CEMAC</p>
        </div>
        <Button
          onClick={() => toast.info('Formulaire de création de mission transport')}
          className="flex items-center gap-2"
        >
          <Zap className="w-4 h-4" /> Affecter Mission
        </Button>
      </div>

      {/* Fleet KPIs */}
      <div className="grid grid-cols-4 gap-3">
        {fleetKpis.map((k, i) => (
          <div key={i} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 text-center">
            <div className={`text-3xl font-black ${k.color} font-mono`}>{k.value}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">{k.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Fleet List */}
        <div className="space-y-2 lg:col-span-1">
          {loading ? (
            <div className="p-8 text-center text-slate-400">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" />
              <span className="text-sm">Chargement de la flotte...</span>
            </div>
          ) : fleet.length === 0 ? (
            <div className="p-8">
              <EmptyStates.NoData
                description="Aucun véhicule dans la flotte."
                action={{
                  label: 'Rafraîchir',
                  onClick: loadFleet
                }}
              />
            </div>
          ) : (
            fleet.map(v => (
              <button
                key={v.id}
                onClick={() => setSelectedVehicle(v.id)}
                className={`w-full text-left p-4 rounded-2xl border transition-all ${selectedVehicle === v.id ? 'bg-amber-500/10 border-amber-500/40' : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'}`}
              >
              <div className="flex items-center gap-3">
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${statutColors[v.statut.replace(/\s/g, '_')] || 'bg-slate-700 text-slate-400'}`}>
                  <Truck className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-black text-white">{v.immat}</span>
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${statutColors[v.statut.replace(/\s/g, '_')] || 'bg-slate-700 text-slate-400 border-slate-600'}`}>{v.statut}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 truncate">{v.chauffeur}</div>
                  <div className="text-[10px] text-slate-500 truncate mt-0.5">{v.position}</div>
                </div>
                {v.alerts.length > 0 && <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />}
              </div>

              {/* Fuel Bar */}
              <div className="mt-2 flex items-center gap-2">
                <Fuel className="w-3 h-3 text-slate-500" />
                <div className="flex-1 bg-slate-800 rounded-full h-1.5">
                  <div
                    className={`h-full rounded-full ${(v.fuel || 0) > 50 ? 'bg-emerald-500' : (v.fuel || 0) > 25 ? 'bg-amber-500' : 'bg-red-500'}`}
                    style={{ width: `${v.fuel || 0}%` }}
                  ></div>
                </div>
                <span className="text-[10px] font-mono text-slate-400">{v.fuel || 0}%</span>
              </div>
            </button>
            ))
          )}
        </div>

        {/* Vehicle Detail */}
        <div className="lg:col-span-2">
          {selectedVehicle ? (
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-5 shadow-xl">
              {/* Vehicle header */}
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg font-black text-white font-mono">{selectedVehicleData?.immat || 'N/A'}</span>
                    <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${statutColors[selectedVehicleData?.statut?.replace(/\s/g, '_')] || 'bg-slate-700 text-slate-400 border-slate-600'}`}>{selectedVehicleData?.statut || 'N/A'}</span>
                  </div>
                  <div className="text-xs text-slate-400">{selectedVehicleData?.model || 'N/A'}</div>
                </div>
                <button onClick={() => toast.error("L'appel chauffeur n'est pas encore raccordé à l'API.")} className="p-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-xl hover:bg-emerald-500/20 transition-colors">
                  <Phone className="w-4 h-4" />
                </button>
              </div>

              {/* GPS Map Placeholder */}
              <div className="bg-slate-950 rounded-2xl h-48 flex items-center justify-center border border-slate-800 relative overflow-hidden">
                <div className="absolute inset-0 opacity-5">
                  <svg width="100%" height="100%">
                    {Array.from({ length: 15 }).map((_, i) => (
                      <line key={`h${i}`} x1="0" y1={`${i * 7}%`} x2="100%" y2={`${i * 7}%`} stroke="#6366f1" strokeWidth="1" />
                    ))}
                    {Array.from({ length: 20 }).map((_, i) => (
                      <line key={`v${i}`} x1={`${i * 5}%`} y1="0" x2={`${i * 5}%`} y2="100%" stroke="#6366f1" strokeWidth="1" />
                    ))}
                  </svg>
                </div>
                <div className="text-center z-10">
                  <MapPin className="w-8 h-8 text-amber-400 mx-auto mb-1 animate-bounce" />
                  <div className="text-xs font-bold text-white">{selectedVehicleData?.position || 'Non disponible'}</div>
                  <div className="text-[11px] text-slate-400 font-mono mt-0.5">{selectedVehicleData?.gps?.lat?.toFixed(4) || '0'}°N, {selectedVehicleData?.gps?.lng?.toFixed(4) || '0'}°E</div>
                  <div className="text-[10px] text-amber-400/60 mt-0.5">GPS mis à jour il y a 45 sec</div>
                </div>
              </div>

              {/* Mission & metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {[
                  { label: 'Mission', value: selectedVehicleData?.mission || 'Aucune', icon: Target },
                  { label: 'Chauffeur', value: selectedVehicleData?.chauffeur || 'Non assigné', icon: User },
                  { label: 'Vitesse', value: `${selectedVehicleData?.vitesse || 0} km/h`, icon: Activity },
                  { label: 'Km parcourus', value: `${(selectedVehicleData?.kmParcourus || 0).toLocaleString()} km`, icon: Navigation },
                  { label: 'Charge', value: selectedVehicleData?.poids || '0 T', icon: Package },
                  { label: 'Carburant', value: `${selectedVehicleData?.fuel || 0}%  ${selectedVehicleData?.carburantConsomme || 0}L consommés`, icon: Fuel },
                ].map((m, i) => {
                  const Icon = m.icon;
                  return (
                    <div key={i} className="bg-slate-950 border border-slate-800/60 rounded-xl p-3">
                      <div className="flex items-center gap-1.5 mb-1">
                        <Icon className="w-3.5 h-3.5 text-amber-400" />
                        <span className="text-[10px] text-slate-500 uppercase font-semibold">{m.label}</span>
                      </div>
                      <div className="text-xs font-bold text-slate-200 truncate">{m.value}</div>
                    </div>
                  );
                })}
              </div>

              {/* Alerts */}
              {selectedVehicleData?.alerts && selectedVehicleData.alerts.length > 0 && (
                <div className="space-y-2">
                  {selectedVehicleData.alerts.map((alert, i) => (
                    <div key={i} className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl flex items-center gap-2 text-xs text-amber-300">
                      <AlertTriangle className="w-4 h-4 shrink-0" />
                      {alert}
                    </div>
                  ))}
                </div>
              )}

              {/* Next stop */}
              <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-xl text-xs text-blue-300">
                <strong>Prochain arrêt :</strong> {selectedVehicleData?.prochainArret || 'Non disponible'}
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-8 flex items-center justify-center h-full">
              <EmptyStates.NoData
                description="Sélectionnez un véhicule pour voir les détails en temps réel."
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
