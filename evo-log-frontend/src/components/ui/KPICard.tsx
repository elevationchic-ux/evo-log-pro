'use client';

import React from 'react';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'default' | 'emerald' | 'amber' | 'red' | 'blue' | 'violet' | 'pink';
  loading?: boolean;
}

const colorClasses = {
  default: 'bg-primary/10 text-primary',
  emerald: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
  amber: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
  red: 'bg-red-500/10 text-red-600 dark:text-red-400',
  blue: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
  violet: 'bg-violet-500/10 text-violet-600 dark:text-violet-400',
  pink: 'bg-pink-500/10 text-pink-600 dark:text-pink-400',
};

export function KPICard({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend, 
  color = 'default',
  loading = false 
}: KPICardProps) {
  
  if (loading) {
    return (
      <div className="erp-card p-6 animate-pulse">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-lg bg-slate-200 dark:bg-slate-700" />
          <div className="flex-1">
            <div className="h-4 w-24 rounded bg-slate-200 dark:bg-slate-700 mb-2" />
            <div className="h-8 w-16 rounded bg-slate-200 dark:bg-slate-700" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="erp-card p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-on-surface-variant truncate">
            {title}
          </p>
          <p className="text-3xl font-bold text-on-surface mt-1 truncate">
            {value}
          </p>
          {subtitle && (
            <p className="text-sm text-on-surface-variant mt-1 truncate">
              {subtitle}
            </p>
          )}
          {trend && (
            <div className={`flex items-center gap-1 mt-2 text-sm font-medium ${
              trend.isPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'
            }`}>
              <span className="material-symbols-outlined text-[16px]">
                {trend.isPositive ? 'trending_up' : 'trending_down'}
              </span>
              <span>{trend.value}%</span>
              <span className="text-on-surface-variant font-normal">vs mois dernier</span>
            </div>
          )}
        </div>
        
        {icon && (
          <div className={`flex-shrink-0 p-3 rounded-xl ${colorClasses[color]}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}

export default KPICard;