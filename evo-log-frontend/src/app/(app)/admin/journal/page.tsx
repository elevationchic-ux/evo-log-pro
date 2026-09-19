'use client';

import { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Book, CheckCircle, RefreshCw } from 'lucide-react';
import { auditAPI } from '@/lib/api-client';

type AuditLog = {
  id: string;
  timestamp: string;
  user_email?: string;
  action: string;
  category?: string;
  target?: string;
  ip?: string | null;
  status: 'SUCCESS' | 'FAILED';
};

export default function AdminJournalPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await auditAPI.getLogs({ limit: 500 });
      const data = response.data;
      setLogs(Array.isArray(data) ? data : data?.items || []);
    } catch (requestError: any) {
      setLogs([]);
      setError(requestError?.response?.data?.detail || 'Impossible de charger le journal d’audit.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = useMemo(() => logs.filter(log => {
    const text = `${log.user_email || ''} ${log.action} ${log.target || ''}`.toLowerCase();
    return !search || text.includes(search.toLowerCase());
  }), [logs, search]);

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2"><Book className="text-slate-400" size={28} /> Journal d’audit système</h1>
          <p className="text-muted-foreground mt-1 text-sm">Événements réellement enregistrés par l’API</p>
        </div>
        <button onClick={load} disabled={loading} className="px-3 py-2 rounded-xl border border-border text-sm"><RefreshCw size={14} className={`inline mr-2 ${loading ? 'animate-spin' : ''}`} /> Actualiser</button>
      </div>
      {error && <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm">{error}</div>}
      <input className="w-full max-w-md bg-card border border-border rounded-xl px-4 py-2.5 text-sm" placeholder="Rechercher..." value={search} onChange={event => setSearch(event.target.value)} />
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        {loading ? <div className="p-6 text-muted-foreground">Chargement...</div> : filtered.length === 0 ? <div className="p-6 text-muted-foreground">Aucun événement d’audit enregistré.</div> : (
          <div className="divide-y divide-border">
            {filtered.map(log => (
              <div key={log.id} className="p-4 grid grid-cols-1 md:grid-cols-6 gap-2 text-sm">
                <span className="font-mono text-slate-400">{log.id}</span>
                <span className="text-foreground">{log.user_email || 'Utilisateur indisponible'}</span>
                <span className="text-slate-300">{log.action}</span>
                <span className="text-slate-400">{log.target || 'Ressource indisponible'}</span>
                <span className="text-slate-500">{log.timestamp}</span>
                <span className={log.status === 'SUCCESS' ? 'text-emerald-400' : 'text-red-400'}>{log.status === 'SUCCESS' ? <CheckCircle className="inline w-4 h-4 mr-1" /> : <AlertCircle className="inline w-4 h-4 mr-1" />}{log.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
