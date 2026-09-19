'use client';

import React, { useState, useEffect } from 'react';
import { transportAPI } from '@/lib/api-client';
import { Package, MapPin, Truck, CheckCircle2, Camera, AlertTriangle, CheckCircle, Navigation, Phone } from 'lucide-react';
import { CardSkeletonLoader } from '@/components/ui/Loaders';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { toast } from 'sonner';

export default function EPodPage() {
  const [mission, setMission] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [statusUpdated, setStatusUpdated] = useState(false);

  // Pour le MVP, on prend la dernière mission "EN_ROUTE" du système
  useEffect(() => {
    loadActiveMission();

    const handleOnline = async () => {
      const pendingUpdates = JSON.parse(localStorage.getItem('pending_mission_updates') || '[]');
      if (pendingUpdates.length > 0) {
        for (const update of pendingUpdates) {
          try {
            await transportAPI.updateStatut(update.missionId, update.statut);
          } catch (e) {
            console.error('Failed to sync', e);
          }
        }
        localStorage.removeItem('pending_mission_updates');
        toast.success("Synchronisation hors-ligne terminée.");
      }
    };
    window.addEventListener('online', handleOnline);
    return () => window.removeEventListener('online', handleOnline);
  }, []);

  const loadActiveMission = async () => {
    try {
      setLoading(true);
      const res = await transportAPI.getMissions();
      const activeMissions = res.data?.filter((m: any) => m.statut === 'EN_ROUTE' || m.statut === 'EN_CHARGEMENT') || [];
      if (activeMissions.length > 0) {
        setMission(activeMissions[0]); // Prendre la première mission active
      } else {
        setMission(null);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (newStatus: string) => {
    if (!mission) return;
    try {
      setActionLoading(true);
      if (!navigator.onLine) {
        // Mode hors ligne
        const pendingUpdates = JSON.parse(localStorage.getItem('pending_mission_updates') || '[]');
        pendingUpdates.push({ missionId: mission.id, statut: newStatus, timestamp: new Date().toISOString() });
        localStorage.setItem('pending_mission_updates', JSON.stringify(pendingUpdates));
        setMission({ ...mission, statut: newStatus });
        toast.warning("Réseau indisponible. Mise à jour enregistrée hors-ligne.");
        if (newStatus === 'LIVRE') {
          setStatusUpdated(true);
          setTimeout(() => setStatusUpdated(false), 3000);
        }
        return;
      }
      
      await transportAPI.updateStatut(mission.id, newStatus);
      setMission({ ...mission, statut: newStatus });
      if (newStatus === 'LIVRE') {
        setStatusUpdated(true);
        setTimeout(() => setStatusUpdated(false), 3000);
      }
    } catch (err) {
      console.error("Erreur de mise à jour", err);
      toast.error("Erreur lors de la mise à jour du statut.");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[80vh] flex flex-col p-4">
        <CardSkeletonLoader />
      </div>
    );
  }

  if (!mission) {
    return (
      <div className="min-h-[80vh] bg-slate-50 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-24 h-24 bg-slate-200 rounded-full flex items-center justify-center mb-6">
          <Truck className="w-12 h-12 text-slate-400" />
        </div>
        <h2 className="text-2xl font-black text-slate-800 mb-2">Aucune Mission</h2>
        <p className="text-slate-500 mb-8">Vous n'avez aucune mission active assignée pour le moment. Reposez-vous bien !</p>
        <button 
          onClick={loadActiveMission}
          className="w-full max-w-xs py-4 bg-blue-600 text-white rounded-2xl font-bold text-lg shadow-lg hover:bg-blue-700 active:scale-95 transition-all"
        >
          Actualiser
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 pb-24 font-sans">
      
      {/* App Bar Mobile */}
      <div className="bg-blue-600 pt-12 pb-6 px-6 text-white rounded-b-3xl shadow-lg relative overflow-hidden">
        <div className="absolute top-0 right-0 opacity-10 transform translate-x-1/3 -translate-y-1/3">
          <Truck className="w-48 h-48" />
        </div>
        <p className="text-blue-100 text-sm font-bold uppercase tracking-widest mb-1">EVO-LOG E-POD</p>
        <h1 className="text-3xl font-black mb-4">Mission Actuelle</h1>
        <div className="inline-flex items-center gap-2 bg-blue-700/50 px-3 py-1.5 rounded-full text-sm font-bold border border-blue-500/50">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          {mission.statut.replace('_', ' ')}
        </div>
      </div>

      {/* Main Content */}
      <div className="px-4 -mt-4 relative z-10 space-y-4">
        
        {/* Mission Card */}
        <div className="bg-white rounded-3xl p-6 shadow-xl shadow-slate-200/50 border border-slate-100">
          <div className="flex justify-between items-start mb-6 border-b border-slate-100 pb-4">
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">RÉFÉRENCE</p>
              <p className="text-xl font-black text-blue-600">{mission.reference}</p>
            </div>
            <div className="text-right">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">DATE</p>
              <p className="text-sm font-bold text-slate-700">
                {format(new Date(mission.date_chargement_prevue || Date.now()), 'dd/MM/yyyy')}
              </p>
            </div>
          </div>

          <div className="space-y-6 relative">
            <div className="absolute left-3 top-2 bottom-2 w-0.5 bg-slate-200 z-0"></div>
            
            <div className="relative z-10 flex items-start gap-4">
              <div className="w-6 h-6 rounded-full bg-emerald-100 border-4 border-white shadow-sm flex items-center justify-center shrink-0">
                <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
              </div>
              <div>
                <p className="text-xs font-bold text-emerald-600 uppercase mb-0.5">Origine</p>
                <p className="font-bold text-slate-800 text-lg leading-tight">{mission.origine}</p>
              </div>
            </div>

            <div className="relative z-10 flex items-start gap-4">
              <div className="w-6 h-6 rounded-full bg-red-100 border-4 border-white shadow-sm flex items-center justify-center shrink-0 mt-1">
                <div className="w-2 h-2 rounded-full bg-red-500"></div>
              </div>
              <div>
                <p className="text-xs font-bold text-red-600 uppercase mb-0.5">Destination</p>
                <p className="font-bold text-slate-800 text-lg leading-tight">{mission.destination}</p>
                <p className="text-sm text-slate-500 mt-1">{mission.distance_km} km</p>
              </div>
            </div>
          </div>
        </div>

        {/* Cargo Details */}
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
          <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Package className="w-5 h-5 text-indigo-500" />
            Marchandise
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 p-3 rounded-2xl">
              <p className="text-xs text-slate-500 font-semibold mb-1">Type de Fret</p>
              <p className="font-bold text-slate-800 text-sm">{mission.nature_fret.replace('_', ' ')}</p>
            </div>
            <div className="bg-slate-50 p-3 rounded-2xl">
              <p className="text-xs text-slate-500 font-semibold mb-1">Poids</p>
              <p className="font-bold text-slate-800 text-sm">{mission.poids_kg ? `${mission.poids_kg} Kg` : 'N/A'}</p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4">
          <button className="bg-white flex flex-col items-center justify-center gap-2 p-4 rounded-3xl shadow-sm border border-slate-100 text-slate-600 active:bg-slate-50 transition-colors">
            <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
              <Navigation className="w-6 h-6" />
            </div>
            <span className="text-sm font-bold">Naviguer</span>
          </button>
          <button className="bg-white flex flex-col items-center justify-center gap-2 p-4 rounded-3xl shadow-sm border border-slate-100 text-slate-600 active:bg-slate-50 transition-colors">
            <div className="w-12 h-12 rounded-full bg-amber-50 text-amber-600 flex items-center justify-center">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <span className="text-sm font-bold">Signaler</span>
          </button>
        </div>

      </div>

      {/* Floating Action Button (POD) */}
      {mission.statut !== 'LIVRE' && (
        <div className="fixed bottom-0 left-0 right-0 p-4 bg-white/80 backdrop-blur-md border-t border-slate-200 z-50">
          {mission.statut === 'EN_CHARGEMENT' ? (
            <button 
              onClick={() => handleUpdateStatus('EN_ROUTE')}
              disabled={actionLoading}
              className="w-full py-4 bg-amber-500 text-white rounded-2xl font-black text-lg shadow-lg shadow-amber-500/30 hover:bg-amber-600 active:scale-95 transition-all flex items-center justify-center gap-3"
            >
              <Truck className="w-6 h-6" />
              Démarrer le Trajet
            </button>
          ) : (
            <button 
              onClick={() => handleUpdateStatus('LIVRE')}
              disabled={actionLoading}
              className="w-full py-4 bg-emerald-500 text-white rounded-2xl font-black text-lg shadow-lg shadow-emerald-500/30 hover:bg-emerald-600 active:scale-95 transition-all flex items-center justify-center gap-3"
            >
              <Camera className="w-6 h-6" />
              Scanner BL & Valider Livraison
            </button>
          )}
        </div>
      )}

      {/* Success Overlay */}
      {statusUpdated && (
        <div className="fixed inset-0 bg-emerald-500 z-[100] flex flex-col items-center justify-center animate-in fade-in duration-300">
          <div className="w-32 h-32 bg-white rounded-full flex items-center justify-center mb-6 animate-bounce shadow-2xl">
            <CheckCircle className="w-16 h-16 text-emerald-500" />
          </div>
          <h2 className="text-4xl font-black text-white mb-2 text-center px-4">LIVRAISON CONFIRMÉE !</h2>
          <p className="text-emerald-100 font-bold text-center px-6">La preuve de livraison a été envoyée au Dispatch avec succès.</p>
        </div>
      )}

    </div>
  );
}
