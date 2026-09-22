'use client';

import React, { useState, useEffect } from 'react';
import { Truck, MapPin, Navigation, Phone, Package, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';
import { toast } from 'sonner';

const MISSION = {
  id: 'MIS-2026-01847',
  depart: 'MAG3 Douala Port  Zone Portuaire, Quai 7',
  arrivee: 'Entrepôt Client BRASSERIES  Zone Industrielle Yaoundé',
  distance_km: 246,
  chargement: '32T  Matières premières (houblon)',
  vehicule: 'CMR-TK-4521  SCANIA R540',
  remorque: 'REM-2026-FR-40T  FRUEHAUF 40 tonnes',
  instructions: 'Respecter les délais de livraison. Ne pas dépasser 80 km/h en charge. Appeler le client 30 min avant arrivée.',
  contact_client: '+237 6 99 00 11 22',
  heure_chargement: '06:00',
  heure_arrivee_prevue: '12:30',
};

export default function MobileChauffeurMissionPage() {
  const [statut, setStatut] = useState<'CHARGE' | 'EN_ROUTE' | 'ARRIVE' | 'LIVRE'>('CHARGE');
  const [km, setKm] = useState(0);
  const [heure, setHeure] = useState('');

  useEffect(() => {
    setHeure(new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }));
    const t = setInterval(() => setHeure(new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })), 30000);
    return () => clearInterval(t);
  }, []);

  const etapesSuivantes: Record<typeof statut, typeof statut> = {
    CHARGE: 'EN_ROUTE', EN_ROUTE: 'ARRIVE', ARRIVE: 'LIVRE', LIVRE: 'LIVRE'
  };

  const avancer = () => {
    const next = etapesSuivantes[statut];
    if (next !== statut) {
      setStatut(next);
      const msgs: Record<string, string> = {
        EN_ROUTE: '🚛 Départ enregistré  Mission en route !',
        ARRIVE: '📍 Arrivée signalée  En attente de déchargement',
        LIVRE: '✅ Livraison confirmée  e-POD à signer'
      };
      toast.error("La mise à jour du statut de mission n'est pas encore raccordée à l'API.");
      if (next === 'EN_ROUTE') setKm(0);
      if (next === 'ARRIVE') setKm(MISSION.distance_km);
    }
  };

  const statutConfig: Record<typeof statut, { label: string; color: string; bg: string }> = {
    CHARGE: { label: 'Chargé  En attente départ', color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/30' },
    EN_ROUTE: { label: 'En route', color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/30' },
    ARRIVE: { label: 'Arrivé  Déchargement', color: 'text-violet-400', bg: 'bg-violet-500/10 border-violet-500/30' },
    LIVRE: { label: 'Livraison confirmée ✓', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30' },
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header mobile */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <Truck className="w-5 h-5 text-blue-400" />
          <div>
            <div className="text-xs font-black text-slate-100">Mission Active</div>
            <div className="text-[10px] font-mono text-blue-400">{MISSION.id}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs font-mono text-slate-300">{heure}</div>
          <div className="text-[10px] text-slate-500 font-mono">T-Code: KDRV_MIS</div>
        </div>
      </div>

      <div className="p-4 space-y-4 max-w-lg mx-auto">
        {/* Statut badge */}
        <div className={`p-3 rounded-2xl border text-center ${statutConfig[statut].bg}`}>
          <div className={`text-sm font-black ${statutConfig[statut].color}`}>{statutConfig[statut].label}</div>
        </div>

        {/* Carte mission */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3">
          <div className="flex items-start gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500 mt-0.5 shrink-0" />
            <div>
              <div className="text-[10px] text-slate-500 uppercase font-bold">Départ</div>
              <div className="text-xs font-bold text-slate-200">{MISSION.depart}</div>
            </div>
          </div>
          <div className="ml-1.5 w-0.5 h-8 bg-slate-700 rounded" />
          <div className="flex items-start gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500 mt-0.5 shrink-0" />
            <div>
              <div className="text-[10px] text-slate-500 uppercase font-bold">Arrivée</div>
              <div className="text-xs font-bold text-slate-200">{MISSION.arrivee}</div>
            </div>
          </div>
        </div>

        {/* Infos véhicule + charge */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-3">
            <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Tracteur</div>
            <div className="text-xs font-bold text-blue-400 font-mono">{MISSION.vehicule.split('  ')[0]}</div>
            <div className="text-[10px] text-slate-400">{MISSION.vehicule.split('  ')[1]}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-3">
            <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Chargement</div>
            <div className="text-xs font-bold text-amber-400">{MISSION.chargement}</div>
            <div className="text-[10px] text-slate-400">{MISSION.distance_km} km</div>
          </div>
        </div>

        {/* Horaires */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-3 text-center">
            <Clock className="w-4 h-4 text-slate-500 mx-auto mb-1" />
            <div className="text-[10px] text-slate-500 uppercase font-bold">Départ prévu</div>
            <div className="text-lg font-black text-slate-100">{MISSION.heure_chargement}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-3 text-center">
            <MapPin className="w-4 h-4 text-red-400 mx-auto mb-1" />
            <div className="text-[10px] text-slate-500 uppercase font-bold">Arrivée prévue</div>
            <div className="text-lg font-black text-emerald-400">{MISSION.heure_arrivee_prevue}</div>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-amber-500/5 border border-amber-500/20 rounded-2xl p-3">
          <div className="flex items-center gap-1.5 mb-2">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-[10px] font-black text-amber-400 uppercase tracking-wider">Instructions</span>
          </div>
          <p className="text-[11px] text-slate-300">{MISSION.instructions}</p>
        </div>

        {/* Actions mobiles */}
        <div className="grid grid-cols-2 gap-3">
          <a href={`tel:${MISSION.contact_client}`}
            className="py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-2xl flex items-center justify-center gap-2 transition-colors">
            <Phone className="w-4 h-4 text-emerald-400" /> Appeler Client
          </a>
          <button onClick={() => toast.info('Géolocalisation partagée avec le dispatching')}
            className="py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-2xl flex items-center justify-center gap-2 transition-colors cursor-pointer">
            <Navigation className="w-4 h-4 text-blue-400" /> Ma Position
          </button>
        </div>

        {/* Bouton principal avancement statut */}
        {statut !== 'LIVRE' && (
          <button onClick={avancer}
            className="w-full py-4 bg-gradient-to-r from-blue-600 to-violet-600 text-white font-black text-sm rounded-2xl shadow-lg shadow-blue-500/30 hover:opacity-90 transition-opacity cursor-pointer active:scale-95">
            {statut === 'CHARGE' && '🚛 Démarrer la mission'}
            {statut === 'EN_ROUTE' && '📍 Signaler arrivée destination'}
            {statut === 'ARRIVE' && '✅ Confirmer livraison'}
          </button>
        )}
        {statut === 'LIVRE' && (
          <a href="/mobile-chauffeur/epod-signature"
            className="block w-full py-4 bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-black text-sm rounded-2xl text-center shadow-lg shadow-emerald-500/20">
            ✍️ Signer le bon de livraison e-POD
          </a>
        )}
      </div>
    </div>
  );
}
