'use client';

import React, { useEffect, useRef } from 'react';
import { useI18n } from '@/hooks/useI18n';
import { Construction, X } from 'lucide-react';

interface ComingSoonModalProps {
  isOpen: boolean;
  onClose: () => void;
  featureName?: string;
}

export function ComingSoonModal({ isOpen, onClose, featureName }: ComingSoonModalProps) {
  const t = useI18n();
  const modalRef = useRef<HTMLDivElement>(null);

  const handleClose = (e?: React.MouseEvent | KeyboardEvent) => {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    onClose();
  };

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleClose(e);
    };
    if (isOpen) document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[100] animate-in fade-in duration-200" 
        onClick={handleClose}
      />
      <div className="fixed inset-0 flex items-center justify-center z-[110] p-4 pointer-events-none">
        <div 
          ref={modalRef}
          className="bg-surface border border-outline w-full max-w-md rounded-2xl shadow-2xl p-6 pointer-events-auto flex flex-col items-center text-center animate-in zoom-in-95 duration-200"
        >
          <button 
            type="button"
            onClick={handleClose}
            className="absolute top-4 right-4 p-2 text-on-surface-variant hover:bg-surface-container rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
            <Construction className="w-8 h-8 text-primary animate-pulse" />
          </div>
          
          <h2 className="text-xl font-bold text-on-surface mb-2">
            Module en construction
          </h2>
          
          <p className="text-on-surface-variant text-sm mb-6">
            La fonctionnalité <strong className="text-on-surface">{featureName || 'demandée'}</strong> est actuellement en cours d'intégration. Elle sera disponible lors du prochain déploiement.
          </p>
          
          <button 
            type="button"
            onClick={handleClose}
            className="w-full py-2.5 bg-primary text-on-primary font-bold rounded-xl hover:opacity-90 transition-opacity"
          >
            {t.common?.close || 'Fermer'}
          </button>
        </div>
      </div>
    </>
  );
}
