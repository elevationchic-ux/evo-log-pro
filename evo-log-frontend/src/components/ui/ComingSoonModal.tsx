'use client';

import React from 'react';
import { X, Sparkles } from 'lucide-react';

interface ComingSoonModalProps {
  isOpen: boolean;
  onClose: () => void;
  featureName?: string;
}

export function ComingSoonModal({ isOpen, onClose, featureName }: ComingSoonModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl">
        <div className="flex justify-between items-start mb-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-amber-100 rounded-xl">
              <Sparkles className="w-6 h-6 text-amber-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-slate-900">Bientôt Disponible</h3>
              <p className="text-sm text-slate-500">
                {featureName ? `${featureName} - ` : ''}Fonctionnalité en développement
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-lg transition"
          >
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        <div className="space-y-4">
          <p className="text-slate-600 text-sm">
            Cette fonctionnalité sera bientôt disponible. Nous travaillons activement à son développement.
          </p>
          <button
            onClick={onClose}
            className="w-full bg-amber-500 hover:bg-amber-600 text-white font-semibold py-3 px-4 rounded-xl transition"
          >
            Compris
          </button>
        </div>
      </div>
    </div>
  );
}