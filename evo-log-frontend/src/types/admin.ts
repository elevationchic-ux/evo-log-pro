import { apiClient } from '@/lib/api-client';

export interface User {
  id: number;
  username: string;
  email: string;
  roles: string[];
  is_active: boolean;
  mfa_enabled: boolean;
}

export interface Permission {
  code: string;
  name: string;
  module: string;
}

export interface DbRole {
  code: string;
  name: string;
  description: string;
  is_active: boolean;
  permissions: Permission[];
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: {
    read: boolean;
    create: boolean;
    modify: boolean;
    delete: boolean;
    approve: boolean;
  };
  isActive: boolean;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  severity: 'critical' | 'warning' | 'info';
  event: string;
  admin: string;
  target: string;
  details: string;
}

export interface SystemHealth {
  cpuUsage: number;
  memoryUsage: number;
  dbConnectionPool: number;
  activeConnections: number;
}

