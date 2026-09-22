'use client';

import React, { useEffect, useState } from 'react';
import { AlertTriangle, Package, Search } from 'lucide-react';
import { b2bPortalAPI } from '@/lib/api-client';

export default function B2BTrackingPage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    setQuery(new URLSearchParams(window.location.search).get('query') || '');
  }, []);

  const track = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setMessage(null);
    try {
      await b2bPortalAPI.trackCargo(query.trim());
    } catch {
      setMessage('Aucun suivi public réel n’est actuellement configuré pour cette référence.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        <h1 className="flex items-center gap-2 text-2xl font-black text-white">
          <Package className="h-6 w-6 text-amber-400" /> Suivi de cargaison
        </h1>
        <p className="mt-2 text-sm text-slate-400">Saisissez une référence existante pour interroger le suivi persistant.</p>
      </div>
      <form onSubmit={track} className="flex flex-col gap-3 rounded-2xl border border-slate-800 bg-slate-900 p-5 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input value={query} onChange={(event) => setQuery(event.target.value)} className="h-11 w-full rounded-xl border border-slate-700 bg-slate-950 pl-10 pr-4 text-sm text-white" placeholder="B/L, conteneur ou booking" />
        </div>
        <button disabled={loading} className="rounded-xl bg-amber-500 px-5 py-2 text-sm font-black text-slate-950 disabled:opacity-60">
          {loading ? 'Recherche...' : 'Rechercher'}
        </button>
      </form>
      {message && (
        <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-5 text-sm text-amber-200">
          <div className="flex gap-3"><AlertTriangle className="h-5 w-5 shrink-0" /> <span>{message} Aucune donnée fictive n’est affichée.</span></div>
        </div>
      )}
    </div>
  );
}
