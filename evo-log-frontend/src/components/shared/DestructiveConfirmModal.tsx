'use client';

import React from 'react';

interface DestructiveConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  severity?: 'critical' | 'warning';
  isOhadaImpact?: boolean;
}

export function DestructiveConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmLabel = 'Confirmer l\'Opération',
  cancelLabel = 'Annuler',
  severity = 'critical',
  isOhadaImpact = false,
}: DestructiveConfirmModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-in fade-in duration-150">
      <div
        className="w-full max-w-md rounded-2xl bg-surface border border-outline shadow-2xl p-6 text-on-surface animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start gap-4 mb-4">
          <div
            className={`h-12 w-12 rounded-xl flex items-center justify-center shrink-0 ${
              severity === 'critical'
                ? 'bg-rose-500/10 text-rose-500 border border-rose-500/20'
                : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
            }`}
          >
            <span className="material-symbols-outlined text-[28px]">
              {severity === 'critical' ? 'gavel' : 'warning'}
            </span>
          </div>

          <div>
            <h3 className="text-base font-bold text-on-surface">{title}</h3>
            <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
              {description}
            </p>
          </div>
        </div>

        {isOhadaImpact && (
          <div className="p-3 mb-5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 text-xs flex items-start gap-2">
            <span className="material-symbols-outlined text-[18px] shrink-0 mt-0.5">policy</span>
            <p className="leading-snug">
              <strong>Mention Réglementaire SYSCOHADA :</strong> Cette écriture est soumise à la piste d'audit légale immuable. Une fois validée, elle ne pourra être corrigée que par une écriture d'extourne.
            </p>
          </div>
        )}

        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl border border-outline hover:bg-surface-container text-xs font-bold text-on-surface transition-colors"
          >
            {cancelLabel}
          </button>
          <button
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className={`px-4 py-2 rounded-xl text-xs font-bold text-white shadow-md transition-colors ${
              severity === 'critical'
                ? 'bg-rose-600 hover:bg-rose-700'
                : 'bg-amber-600 hover:bg-amber-700'
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
