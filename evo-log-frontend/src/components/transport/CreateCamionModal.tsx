'use client';

import React, { useState } from 'react';
import { X } from 'lucide-react';

interface CreateCamionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
}

export default function CreateCamionModal({ isOpen, onClose, onSubmit }: CreateCamionModalProps) {
  const [formData, setFormData] = useState({ immatriculation: '', marque: '', modele: '', capacite: '', chauffeur: '' });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-slate-900 rounded-xl p-6 w-full max-w-lg">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold">Nouveau Camion</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-slate-400"><X className="w-5 h-5" /></button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-200 mb-1">Immatriculation</label>
            <input type="text" value={formData.immatriculation} onChange={e => setFormData({...formData, immatriculation: e.target.value})} className="w-full px-3 py-2 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">Marque</label>
              <input type="text" value={formData.marque} onChange={e => setFormData({...formData, marque: e.target.value})} className="w-full px-3 py-2 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">Modele</label>
              <input type="text" value={formData.modele} onChange={e => setFormData({...formData, modele: e.target.value})} className="w-full px-3 py-2 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-200 mb-1">Capacite (tonnes)</label>
            <input type="number" value={formData.capacite} onChange={e => setFormData({...formData, capacite: e.target.value})} className="w-full px-3 py-2 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
        <div className="flex gap-3 mt-6">
          <button onClick={onClose} className="flex-1 px-4 py-2 border border-slate-600 rounded-lg text-slate-200 hover:bg-slate-800">Annuler</button>
          <button onClick={() => onSubmit(formData)} className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Creer</button>
        </div>
      </div>
    </div>
  );
}