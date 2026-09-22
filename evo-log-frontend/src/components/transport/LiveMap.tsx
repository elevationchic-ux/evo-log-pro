'use client';

import React from 'react';
import { MapPin, Navigation } from 'lucide-react';

interface VehiclePosition {
  id: string;
  lat: number;
  lng: number;
  speed?: number;
  driver?: string;
}

interface LiveMapProps {
  vehicles?: VehiclePosition[];
  positions?: any[];
  className?: string;
}

export default function LiveMap({ vehicles = [], positions = [], className = '' }: LiveMapProps) {
  const activeCount = vehicles.length > 0 ? vehicles.length : positions.length;
  return (
    <div className={`relative bg-blue-50 border border-blue-200 rounded-xl overflow-hidden ${className}`} style={{ minHeight: 400 }}>
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <Navigation className="w-12 h-12 text-blue-400 mx-auto mb-3" />
          <p className="text-lg font-medium text-blue-700">Suivi en temps reel</p>
          <p className="text-sm text-blue-500 mt-1">{activeCount} vehicule(s) connecte(s)</p>
          <div className="mt-4 flex items-center justify-center gap-2 text-xs text-blue-400">
            <MapPin className="w-3 h-3" />
            <span>GPS tracking en cours de configuration</span>
          </div>
        </div>
      </div>
    </div>
  );
}
