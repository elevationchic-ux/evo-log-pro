'use client';

import { useEffect, useMemo, useState } from 'react';
import { ArrowRightLeft, CreditCard, RefreshCw, TrendingDown, TrendingUp } from 'lucide-react';
import { transactionsAPI } from '@/lib/api-client';

type Transaction = {
  id: number;
  facture_numero?: string | null;
  facture_id: number;
  montant: number;
  date_paiement?: string | null;
  mode_paiement?: string | null;
  reference?: string | null;
  statut?: string | null;
  notes?: string | null;
};

export default function FinanceTransactionsPage() {
  const [rows, setRows] = useState<Transaction[]>([]);
  const [filter, setFilter] = useState('TOUS');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await transactionsAPI.getAll({ limit: 500 });
      const data = response.data;
      setRows(Array.isArray(data) ? data : data?.items || []);
    } catch (requestError: any) {
      setRows([]);
      setError(requestError?.response?.data?.detail || 'Impossible de charger les transactions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = useMemo(() => rows.filter(row => {
    const type = Number(row.montant) >= 0 ? 'ENCAISSEMENT' : 'PAIEMENT';
    const text = `${row.reference || ''} ${row.facture_numero || ''} ${row.notes || ''}`.toLowerCase();
    return (filter === 'TOUS' || filter === type) && (!search || text.includes(search.toLowerCase()));
  }), [rows, filter, search]);

  const total = rows.reduce((sum, row) => sum + Number(row.montant || 0), 0);
  const entries = rows.filter(row => Number(row.montant) >= 0).reduce((sum, row) => sum + Number(row.montant || 0), 0);
  const exits = rows.filter(row => Number(row.montant) < 0).reduce((sum, row) => sum + Math.abs(Number(row.montant || 0)), 0);

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2"><CreditCard className="text-emerald-400" size={28} /> Transactions financières</h1>
          <p className="text-muted-foreground mt-1 text-sm">Règlements persistés de l’entreprise courante</p>
        </div>
        <button onClick={load} disabled={loading} className="px-3 py-2 rounded-xl border border-border text-sm"><RefreshCw size={14} className={`inline mr-2 ${loading ? 'animate-spin' : ''}`} /> Actualiser</button>
      </div>
      {error && <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm">{error}</div>}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5"><TrendingUp className="text-emerald-400" size={16} /><div className="text-2xl font-bold text-emerald-400 mt-2">{entries.toLocaleString('fr-FR')} XAF</div><div className="text-xs text-muted-foreground">Encaissements persistés</div></div>
        <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-5"><TrendingDown className="text-red-400" size={16} /><div className="text-2xl font-bold text-red-400 mt-2">{exits.toLocaleString('fr-FR')} XAF</div><div className="text-xs text-muted-foreground">Montants sortants enregistrés</div></div>
        <div className="rounded-2xl border border-blue-500/20 bg-blue-500/5 p-5"><ArrowRightLeft className="text-blue-400" size={16} /><div className="text-2xl font-bold text-blue-400 mt-2">{total.toLocaleString('fr-FR')} XAF</div><div className="text-xs text-muted-foreground">Solde calculé sur les données reçues</div></div>
      </div>
      <div className="flex flex-wrap gap-3">
        <input className="flex-1 min-w-[220px] bg-card border border-border rounded-xl px-4 py-2.5 text-sm" placeholder="Rechercher référence ou facture..." value={search} onChange={event => setSearch(event.target.value)} />
        {['TOUS', 'ENCAISSEMENT', 'PAIEMENT'].map(value => <button key={value} onClick={() => setFilter(value)} className={`px-3 py-2 rounded-xl border text-xs ${filter === value ? 'border-emerald-400 text-emerald-300' : 'border-border text-muted-foreground'}`}>{value}</button>)}
      </div>
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        {loading ? <div className="p-6 text-muted-foreground">Chargement...</div> : filtered.length === 0 ? <div className="p-6 text-muted-foreground">Aucune transaction enregistrée.</div> : (
          <div className="divide-y divide-border">
            {filtered.map(row => <div key={row.id} className="p-4 grid grid-cols-1 md:grid-cols-6 gap-2 text-sm">
              <span className="font-mono text-emerald-400">{row.reference || `Paiement #${row.id}`}</span>
              <span className="text-foreground">{row.facture_numero || `Facture #${row.facture_id}`}</span>
              <span className="text-foreground">{Number(row.montant).toLocaleString('fr-FR')} XAF</span>
              <span className="text-muted-foreground">{row.mode_paiement || 'Mode indisponible'}</span>
              <span className="text-muted-foreground">{row.date_paiement || 'Date indisponible'}</span>
              <span className="text-muted-foreground">{row.statut || 'Statut indisponible'}</span>
            </div>)}
          </div>
        )}
      </div>
    </div>
  );
}
