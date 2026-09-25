'use client';

import React from 'react';
import { X, History } from 'lucide-react';

interface HistoriqueCouplageModalProps {
  isOpen: boolean;
  onClose: () => void;
  couplageId?: string;
}

export default function HistoriqueCouplageModal({ isOpen, onClose }: HistoriqueCouplageModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-slate-900 rounded-xl p-6 w-full max-w-2xl max-h-[80vh] overflow-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold">Historique de couplage</h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-slate-400"><X className="w-5 h-5" /></button>
        </div>
        <div className="space-y-3">
          <p className="text-sm text-slate-400 text-center py-8">Aucun historique de couplage disponible</p>
        </div>
      </div>
    </div>
  );
}