'use client';

import React from 'react';
import { Navigation, MapPin, Inbox } from 'lucide-react';

interface VehiclePosition {
  id: string | number;
  latitude?: number;
  longitude?: number;
  lat?: number;
  lng?: number;
  vitesse?: number;
  speed?: number;
  vehicule_id?: number;
  immatriculation?: string;
  statut_vehicule?: string;
  status?: string;
}

interface LiveMapProps {
  vehicles?: VehiclePosition[];
  positions?: LiveMapProps['vehicles'];
  className?: string;
}

// Tour de contrôle : rend les positions GPS réellement remontées par le backend.
// Aucune donnée simulée  si le flux est vide, on affiche un état vide neutre.
export default function LiveMap({ vehicles = [], positions = [], className = '' }: LiveMapProps) {
  const rows: VehiclePosition[] = (vehicles && vehicles.length > 0 ? vehicles : positions) || [];

  if (rows.length === 0) {
    return (
      <div
        className={`relative flex items-center justify-center rounded-xl border border-slate-800 bg-slate-950/40 ${className}`}
        style={{ minHeight: 400 }}
      >
        <div className="text-center">
          <Inbox className="mx-auto mb-3 h-12 w-12 text-slate-300" />
          <p className="text-lg font-medium text-white">Aucune position GPS remontée</p>
          <p className="mt-1 text-sm text-slate-400">
            Les véhicules apparaîtront ici dès qu&apos;une position sera publiée par la télémétrie.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`rounded-xl border border-slate-800 bg-slate-950/40 ${className}`} style={{ minHeight: 400 }}>
      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-white">
          <Navigation className="h-4 w-4 text-cyan-400" />
          Suivi en temps réel
        </div>
        <span className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-0.5 text-xs font-mono text-cyan-300">
          {rows.length} position(s)
        </span>
      </div>
      <div className="max-h-[520px] divide-y divide-slate-800 overflow-y-auto">
        {rows.map((p) => {
          const lat = p.latitude ?? p.lat;
          const lng = p.longitude ?? p.lng;
          const speed = p.vitesse ?? p.speed ?? 0;
          const label = p.immatriculation || (p.vehicule_id != null ? `Véhicule #${p.vehicule_id}` : `#${p.id}`);
          const status = p.statut_vehicule || p.status || '';
          return (
            <div key={String(p.id)} className="flex items-center justify-between gap-3 px-4 py-3 text-sm">
              <div className="flex items-center gap-3">
                <MapPin className={`h-4 w-4 shrink-0 ${speed > 0 ? 'text-cyan-400' : 'text-slate-500'}`} />
                <div>
                  <div className="font-medium text-white">{label}</div>
                  <div className="font-mono text-xs text-slate-500">
                    {lat != null && lng != null ? `${Number(lat).toFixed(5)}, ${Number(lng).toFixed(5)}` : 'Coordonnées indisponibles'}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-mono text-xs text-cyan-300">{Number(speed).toFixed(1)} km/h</div>
                <div className="text-[11px] text-slate-500">{status}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
