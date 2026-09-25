'use client';

import React, { useState } from 'react';
import { X, AlertTriangle } from 'lucide-react';

interface HseBlockModalProps {
  isOpen: boolean;
  onClose: () => void;
  onBlock: (reason: string) => void;
}

export default function HseBlockModal({ isOpen, onClose, onBlock }: HseBlockModalProps) {
  const [reason, setReason] = useState('');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-slate-900 rounded-xl p-6 w-full max-w-md">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-red-500/15 rounded-lg"><AlertTriangle className="w-6 h-6 text-red-600" /></div>
          <h3 className="text-lg font-semibold text-slate-100">Blocage HSE</h3>
        </div>
        <p className="text-sm text-slate-400 mb-4">Cette action bloquera le vehicule pour des raisons de securite (Hygiene, Securite, Environnement).</p>
        <textarea
          value={reason}
          onChange={e => setReason(e.target.value)}
          placeholder="Motif du blocage HSE..."
          className="w-full px-3 py-2 border border-slate-600 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-red-500"
          rows={3}
        />
        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 px-4 py-2 border border-slate-600 rounded-lg text-slate-200 hover:bg-slate-800">Annuler</button>
          <button onClick={() => onBlock(reason)} disabled={!reason.trim()} className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50">Bloquer</button>
        </div>
      </div>
    </div>
  );
}