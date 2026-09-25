'use client';

import React, { useState, useEffect } from 'react';
import { Download, X } from 'lucide-react';

export default function PwaInstallPrompt() {
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
      if (!isStandalone && !localStorage.getItem('pwa-dismissed')) {
        setShowPrompt(true);
      }
    }, 5000);
    return () => clearTimeout(timer);
  }, []);

  const dismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-dismissed', 'true');
  };

  if (!showPrompt) return null;

  return (
    <div className="fixed bottom-4 right-4 bg-slate-900 border border-slate-700 rounded-xl shadow-lg p-4 max-w-sm z-50">
      <button onClick={dismiss} className="absolute top-2 right-2 text-gray-400 hover:text-slate-400"><X className="w-4 h-4" /></button>
      <div className="flex items-start gap-3">
        <div className="p-2 bg-blue-500/15 rounded-lg"><Download className="w-5 h-5 text-blue-600" /></div>
        <div>
          <h4 className="font-semibold text-slate-100 text-sm">Installer EVO-LOG</h4>
          <p className="text-xs text-slate-400 mt-1">Installez l&apos;application pour un acces rapide</p>
        </div>
      </div>
    </div>
  );
}