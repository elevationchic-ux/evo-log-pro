'use client';

import React from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  color?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
}

const colorMap = {
  default: 'from-slate-500/10 to-slate-600/5 border-slate-200 dark:border-slate-700',
  primary: 'from-indigo-500/10 to-indigo-600/5 border-indigo-200 dark:border-indigo-800',
  success: 'from-emerald-500/10 to-emerald-600/5 border-emerald-200 dark:border-emerald-800',
  warning: 'from-amber-500/10 to-amber-600/5 border-amber-200 dark:border-amber-800',
  danger: 'from-red-500/10 to-red-600/5 border-red-200 dark:border-red-800',
  info: 'from-blue-500/10 to-blue-600/5 border-blue-200 dark:border-blue-800',
};

const iconColorMap = {
  default: 'text-slate-500',
  primary: 'text-indigo-500',
  success: 'text-emerald-500',
  warning: 'text-amber-500',
  danger: 'text-red-500',
  info: 'text-blue-500',
};

export function StatCard({ 
  label, 
  value, 
  change, 
  changeLabel = 'vs période précédente',
  icon,
  color = 'default' 
}: StatCardProps) {
  const isPositive = change !== undefined && change >= 0;

  return (
    <div className={`relative overflow-hidden rounded-xl border bg-gradient-to-br ${colorMap[color]} p-5`}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-on-surface-variant">{label}</p>
          <p className="text-2xl font-bold text-on-surface">{value}</p>
          
          {change !== undefined && (
            <div className={`flex items-center gap-1 text-sm ${
              isPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'
            }`}>
              <span className="material-symbols-outlined text-[16px]">
                {isPositive ? 'trending_up' : 'trending_down'}
              </span>
              <span className="font-semibold">{Math.abs(change)}%</span>
              <span className="text-on-surface-variant text-xs">{changeLabel}</span>
            </div>
          )}
        </div>

        {icon && (
          <div className={`p-2 rounded-lg bg-surface/50 ${iconColorMap[color]}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}

export default StatCard;