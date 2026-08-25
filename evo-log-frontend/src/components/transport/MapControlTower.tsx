'use client';

import React, { useState } from 'react';
import { Truck, MapPin, Radio } from 'lucide-react';

interface Vehicle {
  id: string;
  name: string;
  lat?: number;
  lng?: number;
  status: 'en_route' | 'arrete' | 'maintenance';
  speed?: number;
}

interface MapControlTowerProps {
  vehicles?: Vehicle[];
}

export default function MapControlTower({ vehicles = [] }: MapControlTowerProps) {
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);

  const statusColors = {
    en_route: 'text-green-500',
    arrete: 'text-red-500',
    maintenance: 'text-yellow-500',
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Radio className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900">Tour de controle carte</h3>
        </div>
        <span className="text-sm text-gray-500">{vehicles.length} vehicules</span>
      </div>

      <div className="relative bg-blue-50" style={{ minHeight: 400 }}>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <MapPin className="w-16 h-16 text-blue-300 mx-auto mb-4" />
            <p className="text-lg font-medium text-blue-700">Vue carte en cours de configuration</p>
            <p className="text-sm text-blue-500 mt-1">Les donnees GPS en temps reel seront affichees ici</p>
          </div>
        </div>
      </div>

      {vehicles.length > 0 && (
        <div className="p-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Vehicules actifs</h4>
          <div className="space-y-2 max-h-48 overflow-auto">
            {vehicles.map(v => (
              <button
                key={v.id}
                onClick={() => setSelectedVehicle(v)}
                className={`w-full flex items-center justify-between p-2 rounded-lg text-left hover:bg-gray-50 ${selectedVehicle?.id === v.id ? 'bg-blue-50 border border-blue-200' : ''}`}
              >
                <div className="flex items-center gap-2">
                  <Truck className="w-4 h-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-700">{v.name}</span>
                </div>
                <span className={`text-xs font-medium ${statusColors[v.status]}`}>{v.status}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
