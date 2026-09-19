'use client'

import { useState, useEffect } from 'react'
import { adminAPI } from '@/lib/api-client'
import GenericDataPage from '@/components/ui/GenericDataPage'
import { History, ShieldAlert } from 'lucide-react'

export default function AuditOperationTrace() {
  const [logs, setLogs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchLogs() {
      try {
        const res = await adminAPI.getAuditLogs()
        setLogs(res.data || [])
      } catch (err) {
        console.error('Error fetching audit logs:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchLogs()
  }, [])

  const columns = [
    {
      key: 'timestamp',
      label: 'Date & Heure',
      render: (val: any) => (
        <span className="text-sm font-medium text-slate-700">
          {new Date(val).toLocaleString()}
        </span>
      ),
    },
    {
      key: 'user',
      label: 'Utilisateur',
      render: (val: any, row: any) => (
        <div>
          <div className="font-semibold text-slate-900">{row.user?.username || val || 'Système'}</div>
          <div className="text-xs text-slate-500">{row.ip_address || '127.0.0.1'}</div>
        </div>
      ),
    },
    {
      key: 'action',
      label: 'Action',
      render: (val: any) => {
        let style = 'bg-slate-50 text-slate-700 ring-slate-600/20'
        if (val?.includes('CREATE') || val?.includes('LOGIN')) style = 'bg-emerald-50 text-emerald-700 ring-emerald-600/20'
        if (val?.includes('UPDATE') || val?.includes('MODIFIED')) style = 'bg-blue-50 text-blue-700 ring-blue-600/20'
        if (val?.includes('DELETE') || val?.includes('FAILED')) style = 'bg-red-50 text-red-700 ring-red-600/20'

        return (
          <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${style}`}>
            {val || 'UNKNOWN_ACTION'}
          </span>
        )
      }
    },
    {
      key: 'resource',
      label: 'Ressource',
      render: (val: any) => (
        <div className="text-sm text-slate-600 font-mono">
          {val || 'N/A'}
        </div>
      )
    },
    {
      key: 'details',
      label: 'Détails',
      render: (val: any) => (
        <div className="text-xs text-slate-500 truncate max-w-[200px]" title={JSON.stringify(val)}>
          {val ? JSON.stringify(val) : '-'}
        </div>
      )
    },
    {
      key: 'status',
      label: 'Statut',
      render: (val: any, row: any) => (
        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${row.status === 'ERROR' ? 'bg-red-50 text-red-700' : 'bg-emerald-50 text-emerald-700'}`}>
          {row.status === 'ERROR' ? <ShieldAlert className="w-3 h-3" /> : null}
          {row.status === 'ERROR' ? 'Échec' : 'Succès'}
        </span>
      )
    }
  ]

  return (
    <GenericDataPage
      title="Traces d'Opérations (Audit Logs)"
      description="Historique immuable de toutes les actions système, modifications de données et tentatives d'accès."
      icon={<History className="w-6 h-6 text-slate-600" />}
      columns={columns}
      data={logs}
      isLoading={loading}
      onExport={() => console.log('Export logs')}
    />
  )
}
