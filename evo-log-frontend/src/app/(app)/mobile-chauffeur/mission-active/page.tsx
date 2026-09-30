'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Truck, MapPin, Navigation, Phone, Package, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';
import { toast } from 'sonner';
import { transportAPI } from '@/lib/api-client';

interface Mission {
  id: number;
  reference: string;
  statut: string;
  point_depart?: string;
  point_arrivee?: string;
  distance_km?: number;
  camion?: { immatriculation?: string; marque?: string; modele?: string };
  chauffeur?: { nom_complet?: string; telephone?: string };
  notes?: string;
  date_debut_prevue?: string;
  date_fin_prevue?: string;
}

export default function MobileChauffeurMissionPage() {
  const [mission, setMission] = useState<Mission | null>(null);
  const [statut, setStatut] = useState<'CHARGE' | 'EN_ROUTE' | 'ARRIVE' | 'LIVRE'>('CHARGE');
  const [km, setKm] = useState(0);
  const [heure, setHeure] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchActiveMission = useCallback(async () => {
    try {
      const res: any = await transportAPI.getMissions({ limit: 50, statut: 'en_cours' });
      const body = res.data ?? res;
      const list: Mission[] = Array.isArray(body) ? body : (body.items || []);
      // Try en_cours first, fallback to planifiee
      let active = list.find(m => m.statut === 'en_cours') || list.find(m => m.statut === 'planifiee') || list[0] || null;
      setMission(active);
      if (active) {
        // Map backend statut to mobile steps
        if (active.statut === 'terminee' || active.statut === 'livree') setStatut('LIVRE');
        else if (active.statut === 'en_cours') setStatut('EN_ROUTE');
        else setStatut('CHARGE');
      }
    } catch {
      setMission(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchActiveMission();
    setHeure(new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }));
    const t = setInterval(() => setHeure(new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })), 30000);
    return () => clearInterval(t);
  }, [fetchActiveMission]);

  const etapesSuivantes: Record<typeof statut, typeof statut> = {
    CHARGE: 'EN_ROUTE', EN_ROUTE: 'ARRIVE', ARRIVE: 'LIVRE', LIVRE: 'LIVRE'
  };

  const avancer = () => {
    const next = etapesSuivantes[statut];
    if (next !== statut) {
      setStatut(next);
      const msgs: Record<string, string> = {
        EN_ROUTE: 'Départ enregistré — Mission en route !',
        ARRIVE: 'Arrivée signalée — En attente de déchargement',
        LIVRE: 'Livraison confirmée — e-POD à signer'
      };
      toast.success(msgs[next] ?? '');
      if (next === 'EN_ROUTE') setKm(0);
      if (next === 'ARRIVE') setKm(mission?.distance_km ?? 0);
    }
  };

  const statutConfig: Record<typeof statut, { label: string; color: string; bg: string }> = {
    CHARGE: { label: 'Chargé — En attente départ', color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/30' },
    EN_ROUTE: { label: 'En route', color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/30' },
    ARRIVE: { label: 'Arrivé — Déchargement', color: 'text-violet-400', bg: 'bg-violet-500/10 border-violet-500/30' },
    LIVRE: { label: 'Livraison confirmée ✓', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30' },
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <div className="text-slate-400 text-sm animate-pulse">Chargement...</div>
      </div>
    );
  }

  if (!mission) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100">
        <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center gap-2 sticky top-0 z-10">
          <Truck className="w-5 h-5 text-blue-400" />
          <div className="text-xs font-black text-slate-100">Mission Active</div>
        </div>
        <div className="p-4 max-w-lg mx-auto">
          <div className="p-12 text-center bg-slate-900 border border-slate-800 rounded-2xl mt-8">
            <Navigation className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-slate-300">Aucune mission assignée</h3>
            <p className="text-sm text-slate-500 mt-1">Contactez votre responsable d&apos;exploitation pour recevoir une mission.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header mobile */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <Truck className="w-5 h-5 text-blue-400" />
          <div>
            <div className="text-xs font-black text-slate-100">Mission Active</div>
            <div className="text-[11px] font-mono text-blue-400">{mission.reference}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs font-mono text-slate-300">{heure}</div>
          <div className="text-[11px] text-slate-500 font-mono">T-Code: KDRV_MIS</div>
        </div>
      </div>

      <div className="p-4 space-y-4 max-w-lg mx-auto">
        {/* Statut badge */}
        <div className={`p-3 rounded-2xl border text-center ${statutConfig[statut].bg}`}>
          <div className={`text-sm font-black ${statutConfig[statut].color}`}>{statutConfig[statut].label}</div>
        </div>

        {/* Trajet */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-emerald-400 mt-2 shrink-0" />
            <div>
              <div className="text-[11px] text-slate-500 uppercase font-bold">Départ</div>
              <div className="text-sm text-slate-200">{mission.point_depart || 'Non précisé'}</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-red-400 mt-2 shrink-0" />
            <div>
              <div className="text-[11px] text-slate-500 uppercase font-bold">Arrivée</div>
              <div className="text-sm text-slate-200">{mission.point_arrivee || 'Non précisé'}</div>
            </div>
          </div>
          {mission.distance_km && (
            <div className="text-xs text-slate-400 font-mono border-t border-slate-800 pt-2">
              <MapPin className="w-3 h-3 inline mr-1" />{mission.distance_km} km
            </div>
          )}
        </div>

        {/* Véhicule */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="text-[11px] text-slate-500 uppercase font-bold mb-2">Véhicule</div>
          <div className="text-sm text-slate-200 font-mono">
            {mission.camion?.immatriculation || 'Non assigné'}
            {mission.camion?.marque && <span className="text-slate-400 ml-2">{mission.camion.marque} {mission.camion.modele}</span>}
          </div>
        </div>

        {/* Contact */}
        {mission.chauffeur?.telephone && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex items-center gap-3">
            <Phone className="w-4 h-4 text-blue-400" />
            <div>
              <div className="text-[11px] text-slate-500 uppercase font-bold">Contact exploitation</div>
              <div className="text-sm text-slate-200">{mission.chauffeur.telephone}</div>
            </div>
          </div>
        )}

        {/* Notes / Instructions */}
        {mission.notes && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
            <div className="text-[11px] text-slate-500 uppercase font-bold mb-1">
              <AlertTriangle className="w-3 h-3 inline mr-1 text-amber-400" />Consignes
            </div>
            <p className="text-xs text-slate-300">{mission.notes}</p>
          </div>
        )}

        {/* Bouton progression */}
        {statut !== 'LIVRE' && (
          <button
            onClick={avancer}
            className="w-full py-4 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-bold rounded-2xl text-sm transition-colors flex items-center justify-center gap-2"
          >
            <CheckCircle2 className="w-5 h-5" />
            {statut === 'CHARGE' ? 'Confirmer le départ' : statut === 'EN_ROUTE' ? 'Signaler arrivée' : 'Confirmer livraison'}
          </button>
        )}
      </div>
    </div>
  );
}
