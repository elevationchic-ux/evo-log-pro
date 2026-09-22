'use client';

import React from 'react';

export type BadgeVariant = 
  | 'default' 
  | 'success' 
  | 'warning' 
  | 'error' 
  | 'info' 
  | 'pending'
  | 'transit'
  | 'loading'
  | 'delivered'
  | 'maintenance'
  | 'planified';

interface StatusBadgeProps {
  label: string;
  variant?: BadgeVariant;
  icon?: boolean;
  pulse?: boolean;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-slate-500/10 text-slate-600 dark:text-slate-400',
  success: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
  warning: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
  error: 'bg-red-500/10 text-red-600 dark:text-red-400',
  info: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
  pending: 'bg-slate-500/10 text-slate-600 dark:text-slate-400',
  transit: 'bg-blue-500/15 text-blue-600 dark:text-blue-400',
  loading: 'bg-amber-500/15 text-amber-700 dark:text-amber-400',
  delivered: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400',
  maintenance: 'bg-red-500/15 text-red-700 dark:text-red-400',
  planified: 'bg-violet-500/15 text-violet-700 dark:text-violet-400',
};

const iconMap: Record<BadgeVariant, string> = {
  default: 'circle',
  success: 'check_circle',
  warning: 'warning',
  error: 'error',
  info: 'info',
  pending: 'schedule',
  transit: 'local_shipping',
  loading: 'sync',
  delivered: 'check_circle',
  maintenance: 'build',
  planified: 'event',
};

export function StatusBadge({ label, variant = 'default', icon = false, pulse = false }: StatusBadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wide ${variantClasses[variant]}`}>
      {icon && (
        <span className={`material-symbols-outlined text-[12px] ${pulse ? 'animate-pulse' : ''}`}>
          {iconMap[variant]}
        </span>
      )}
      {label}
    </span>
  );
}

// Predefined status badges for common use cases
export const StatusBadges = {
  Transport: {
    EN_ROUTE: <StatusBadge label="En Route" variant="transit" icon pulse />,
    LIVRÉ: <StatusBadge label="Livré" variant="delivered" icon />,
    CHARGEMENT: <StatusBadge label="Chargement" variant="loading" icon pulse />,
    ATTENTE: <StatusBadge label="En Attente" variant="pending" icon />,
    RETARD: <StatusBadge label="Retard" variant="error" icon />,
  },
  Magasin: {
    RÉCEPTIONNÉ: <StatusBadge label="Réceptionné" variant="success" icon />,
    EN_STOCK: <StatusBadge label="En Stock" variant="info" icon />,
    PRÉPARATION: <StatusBadge label="Préparation" variant="loading" icon pulse />,
    EXPÉDIÉ: <StatusBadge label="Expédié" variant="transit" icon />,
    INVENTAIRE: <StatusBadge label="Inventaire" variant="warning" icon />,
  },
  Finance: {
    PAYÉE: <StatusBadge label="Payée" variant="success" icon />,
    EN_ATTENTE: <StatusBadge label="En Attente" variant="pending" icon />,
    EN_RETARD: <StatusBadge label="Retard" variant="error" icon />,
    VALIDÉE: <StatusBadge label="Validée" variant="success" icon />,
    BROUILLON: <StatusBadge label="Brouillon" variant="default" icon />,
  },
  Douane: {
    VALIDÉ: <StatusBadge label="Validé" variant="success" icon />,
    EN_COURS: <StatusBadge label="En Cours" variant="loading" icon pulse />,
    TAXATION: <StatusBadge label="Taxation" variant="warning" icon />,
    BAE: <StatusBadge label="BAE Émis" variant="success" icon />,
    REFUSÉ: <StatusBadge label="Refusé" variant="error" icon />,
  },
  Maintenance: {
    PLANIFIÉE: <StatusBadge label="Planifiée" variant="planified" icon />,
    EN_COURS: <StatusBadge label="En Cours" variant="loading" icon pulse />,
    TERMINÉE: <StatusBadge label="Terminée" variant="success" icon />,
    URGENTE: <StatusBadge label="Urgente" variant="error" icon pulse />,
  },
};

export default StatusBadge;