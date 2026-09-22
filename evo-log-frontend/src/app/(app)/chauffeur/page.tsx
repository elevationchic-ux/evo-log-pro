'use client';

import React, { useState, useEffect } from 'react';
import { Truck, MapPin, Package, CheckCircle2, Navigation, Clock, AlertTriangle } from 'lucide-react';
import { transportAPI } from '@/lib/api-client';
import { toast } from 'sonner';
import SignaturePadModal from '@/components/transport/SignaturePadModal';

export default function ChauffeurPage() {
  const [missions, setMissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // EPOD Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedMissionId, setSelectedMissionId] = useState<string | number | null>(null);

  useEffect(() => {
    fetchMissions();
  }, []);

  const fetchMissions = async () => {
    try {
      // In a real app, we'd fetch only the missions assigned to the current driver
      const data = await transportAPI.getMissions();
      // Filter for missions that can be delivered (EN_ROUTE, EN_COURS, etc)
      // Assuming for demo we show EN_ROUTE and EN_CHARGEMENT
      const activeMissions = (data as any).data.filter((m: any) => m.statut === 'EN_ROUTE' || m.statut === 'VALIDE' || m.status === 'in_progress');
      setMissions(activeMissions);
    } catch (err: any) {
      setError(err.message || 'Erreur lors du chargement des missions');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenEPOD = (missionId: string | number) => {
    setSelectedMissionId(missionId);
    setIsModalOpen(true);
  };

  const handleSaveEPOD = async (signatureBase64: string, nom_receptionnaire: string) => {
    if (!selectedMissionId) return;
    try {
      await transportAPI.livrerMission(selectedMissionId, signatureBase64, nom_receptionnaire);
      setIsModalOpen(false);
      setSelectedMissionId(null);
      fetchMissions(); // Refresh the list
    } catch (err: any) {
      toast.error(err.message || 'Erreur lors de la livraison');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="bg-red-50 text-red-600 p-4 rounded-xl flex items-center gap-3">
          <AlertTriangle className="w-5 h-5" />
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header Mobile */}
      <div className="bg-blue-600 text-white p-6 rounded-b-3xl shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold mb-1">Espace Chauffeur</h1>
          <p className="text-blue-100 text-sm">Gérez vos livraisons en temps réel</p>
        </div>
        <a
          href="/portail-chauffeur"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 text-xs font-black transition-colors shadow-md"
        >
          <span>Ouvrir le Nouveau Portail Conducteur</span>
          <Navigation className="w-3.5 h-3.5" />
        </a>
      </div>

      {/* Main Content */}
      <div className="p-4 mt-2 space-y-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold text-gray-900">Missions en cours</h2>
          <span className="bg-blue-100 text-blue-700 text-xs font-bold px-2.5 py-1 rounded-full">
            {missions.length} active(s)
          </span>
        </div>

        {missions.length === 0 ? (
          <div className="bg-white rounded-2xl p-8 text-center shadow-sm border border-gray-100">
            <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-gray-900 font-medium mb-1">Aucune mission</h3>
            <p className="text-sm text-gray-500">Vous n'avez pas de livraison en attente pour le moment.</p>
          </div>
        ) : (
          missions.map((mission) => (
            <div key={mission.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="p-4 border-b border-gray-50">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                      <Truck className="w-5 h-5" />
                    </span>
                    <div>
                      <p className="text-xs text-gray-500 font-medium">{mission.reference || `Mission #${mission.id}`}</p>
                      <p className="text-sm font-bold text-gray-900">{mission.merchandise || 'Fret Divers'}</p>
                    </div>
                  </div>
                  <span className="bg-yellow-100 text-yellow-800 text-xs font-semibold px-2 py-1 rounded-md">
                    En route
                  </span>
                </div>

                <div className="space-y-3 relative before:absolute before:inset-0 before:ml-2.5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-200 before:to-transparent">
                  <div className="relative flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full bg-white border-2 border-gray-300 flex items-center justify-center z-10">
                      <div className="w-1.5 h-1.5 rounded-full bg-gray-400"></div>
                    </div>
                    <div className="flex-1">
                      <p className="text-xs text-gray-500 uppercase">Origine</p>
                      <p className="text-sm font-medium text-gray-900">{mission.origin || 'Dépôt Douala'}</p>
                    </div>
                  </div>
                  <div className="relative flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full bg-white border-2 border-blue-500 flex items-center justify-center z-10">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-600"></div>
                    </div>
                    <div className="flex-1">
                      <p className="text-xs text-blue-500 uppercase">Destination</p>
                      <p className="text-sm font-medium text-gray-900">{mission.destination || 'Client Final'}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="p-4 bg-gray-50/50 flex gap-3">
                <button
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl text-sm font-medium hover:bg-gray-50 transition-colors"
                  onClick={() => toast.error("L'ouverture du GPS n'est pas encore raccordée à l'API.")}
                >
                  <Navigation className="w-4 h-4" />
                  Naviguer
                </button>
                <button
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors shadow-sm shadow-blue-200"
                  onClick={() => handleOpenEPOD(mission.id)}
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Livrer
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <SignaturePadModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveEPOD}
      />
    </div>
  );
}
