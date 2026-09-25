'use client';

import React from 'react';
import { MapPin } from 'lucide-react';

interface MapViewerProps {
  latitude?: number;
  longitude?: number;
  zoom?: number;
  markers?: { lat: number; lng: number; label?: string }[];
  className?: string;
}

export default function MapViewer({ latitude, longitude, markers = [], className = '' }: MapViewerProps) {
  return (
    <div className={`relative bg-slate-900 border border-slate-700 rounded-xl overflow-hidden ${className}`} style={{ minHeight: 400 }}>
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <MapPin className="w-12 h-12 text-sky-400 mx-auto mb-3" />
          <p className="text-lg font-medium text-slate-100">Carte Interactive</p>
          <p className="text-sm text-slate-400 mt-1">
            {latitude && longitude
              ? `Position : ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`
              : 'Aucune coordonnée disponible pour cet enregistrement'}
          </p>
          {markers.length > 0 && (
            <p className="text-xs text-slate-500 mt-2">{markers.length} point(s) affiche(s)</p>
          )}
        </div>
      </div>
    </div>
  );
}
