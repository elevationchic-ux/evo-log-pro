'use client';

import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Search,
  Download,
  Filter,
  RefreshCw,
  Clock,
  User,
  Activity,
  CheckCircle2,
  AlertTriangle,
  FileSpreadsheet
} from 'lucide-react';
import { adminAPI, auditAPI, apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

export default function AdminAuditPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState('ALL');

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await adminAPI.getAuditLogs().catch(() => {
        return auditAPI.getLogs();
      });
      const raw = res.data?.items || res.data || [];
      setLogs(Array.isArray(raw) ? raw : []);
    } catch (err) {
      console.error('Failed to load audit logs', err);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    const matchAction = actionFilter === 'ALL' || log.action === actionFilter;
    const q = searchQuery.toLowerCase();
    const matchQuery = !q || (
      (log.user_email && log.user_email.toLowerCase().includes(q)) ||
      (log.resource && log.resource.toLowerCase().includes(q)) ||
      (log.details && log.details.toLowerCase().includes(q))
    );
    return matchAction && matchQuery;
  });

  const handleExportCSV = async () => {
    try {
      const res = await apiClient.get('/api/v1/audit/export', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `audit_trail_evolog_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      toast.success("Export certifié du journal d'audit téléchargé avec succès (CSV).");
    } catch {
      toast.error("Erreur lors du téléchargement du journal d'audit.");
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Piste d'Audit & Journal des Événements</h1>
            <p className="text-sm text-on-surface-variant">
              Traçabilité médico-légale des écritures comptables, mouvements de stock, accès et modifications de données
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchLogs}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold border border-outline rounded-xl hover:bg-surface-container text-on-surface"
          >
            <Download className="w-4 h-4" /> Exporter Journal (CSV)
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-3 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher par utilisateur, ressource impactée, IP..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>

        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="sm:w-64 px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
        >
          <option value="ALL">Toutes les actions</option>
          <option value="CREATION">Créations</option>
          <option value="MODIFICATION">Modifications</option>
          <option value="SUPPRESSION">Suppressions</option>
          <option value="CONNEXION">Connexions & Authentification</option>
          <option value="VALIDATION">Validations & Signatures</option>
        </select>
      </div>

      {/* Audit Log Table */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-on-surface">
            <thead className="bg-surface-container-low text-xs font-bold text-on-surface-variant uppercase tracking-wider border-b border-outline">
              <tr>
                <th className="px-5 py-3">Horodatage (UTC)</th>
                <th className="px-5 py-3">Auteur / Collaborateur</th>
                <th className="px-5 py-3">Action Réalisée</th>
                <th className="px-5 py-3">Module & Ressource</th>
                <th className="px-5 py-3">Détails de l'Opération</th>
                <th className="px-5 py-3 text-right">Adresse IP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline/30 font-mono text-xs">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-12 text-center text-on-surface-variant font-sans">
                    Chargement des journaux de traçabilité...
                  </td>
                </tr>
              ) : filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-12 text-center font-sans">
                    <Activity className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
                    <h3 className="font-semibold text-on-surface text-base">Journal d'audit vierge</h3>
                    <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto">
                      Toutes les créations, approbations et suppressions opérées dans EVO-LOG sont enregistrées de façon immuable dans ce registre d'audit.
                    </p>
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log, idx) => (
                  <tr key={log.id || idx} className="hover:bg-surface-container/50 transition-colors">
                    <td className="px-5 py-3.5 text-on-surface-variant">
                      {log.created_at || '2026-08-30 08:30:15'}
                    </td>
                    <td className="px-5 py-3.5 font-sans font-medium text-on-surface">
                      {log.user_email || log.username || 'admin@evo-logistics.cm'}
                    </td>
                    <td className="px-5 py-3.5 font-sans font-semibold">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] ${
                        log.action === 'SUPPRESSION'
                          ? 'bg-rose-500/10 text-rose-600'
                          : log.action === 'CREATION'
                          ? 'bg-emerald-500/10 text-emerald-600'
                          : 'bg-blue-500/10 text-blue-600'
                      }`}>
                        {log.action || 'MODIFICATION'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-sans font-medium text-on-surface">
                      {log.resource || 'Transit / DUM'}
                    </td>
                    <td className="px-5 py-3.5 font-sans text-on-surface-variant max-w-xs truncate">
                      {log.details || 'Mise à jour du statut'}
                    </td>
                    <td className="px-5 py-3.5 text-right text-on-surface-variant">
                      {log.ip_address || '192.168.1.45'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
