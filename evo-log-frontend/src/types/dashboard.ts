// API Service for Dashboard Module

export interface KPICard {
  id: string;
  title: string;
  value: number | string;
  trend: number;
  trendDirection: 'up' | 'down';
  icon: string;
  color: string;
}

export interface Alert {
  id: string;
  type: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  module: string;
}

export interface Operation {
  id: string;
  type: string;
  reference: string;
  module: string;
  user: string;
  timestamp: string;
  status: 'pending' | 'in_progress' | 'completed';
}

export interface DashboardData {
  kpis: KPICard[];
  alerts: Alert[];
  operations: Operation[];
  systemHealth: {
    cpu: number;
    memory: number;
    storage: number;
  };
}

