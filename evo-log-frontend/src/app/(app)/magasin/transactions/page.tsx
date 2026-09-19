'use client';

import { useEffect, useMemo, useState } from 'react';
import { ArrowRightLeft, RefreshCw } from 'lucide-react';
import { magasinAPI } from '@/lib/api-client';

type Movement = {
  id: number;
  reference: string;
  type_mouvement: string;
  quantite: number;
  date_mouvement?: string;
  stock_id?: number | null;
  operateur_id?: number | null;
  destination?: string | null;
};

export default function MagasinTransactionsPage() {
  const [rows, setRows] = useState<Movement[]>([]);
  const [filter, setFilter] = useState('TOUS');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await magasinAPI.getMouvements({ limit: 500 });
      const data = response.data;
      setRows(Array.isArray(data) ? data : data?.items || []);
    } catch (requestError: any) {
      setRows([]);
      setError(requestError?.response?.data?.detail || 'Impossible de charger les mouvements de stock.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = useMemo(
    () => rows.filter(row => filter === 'TOUS' || row.type_mouvement.toUpperCase() === filter),
    [rows, filter],
  );

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <ArrowRightLeft className="text-amber-400" size={28} /> Mouvements de stock
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">Historique persistant de l’entreprise courante</p>
        </div>
        <button onClick={load} disabled={loading} className="px-3 py-2 rounded-xl border border-border text-sm">
          <RefreshCw size={14} className={`inline mr-2 ${loading ? 'animate-spin' : ''}`} /> Actualiser
        </button>
      </div>
      {error && <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm">{error}</div>}
      <div className="flex gap-2 flex-wrap">
        {['TOUS', 'ENTREE', 'SORTIE', 'TRANSFERT', 'INVENTAIRE', 'AJUSTEMENT'].map(type => (
          <button key={type} onClick={() => setFilter(type)} className={`px-3 py-2 rounded-lg text-xs border ${filter === type ? 'border-amber-400 text-amber-300' : 'border-border text-muted-foreground'}`}>
            {type}
          </button>
        ))}
      </div>
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        {loading ? <div className="p-6 text-muted-foreground">Chargement...</div> : filtered.length === 0 ? (
          <div className="p-6 text-muted-foreground">Aucun mouvement enregistré.</div>
        ) : (
          <div className="divide-y divide-border">
            {filtered.map(row => (
              <div key={row.id} className="p-4 grid grid-cols-1 md:grid-cols-6 gap-2 text-sm">
                <span className="font-mono text-amber-400">{row.reference}</span>
                <span className="text-foreground">{row.type_mouvement}</span>
                <span className="text-foreground">{Number(row.quantite).toLocaleString('fr-FR')}</span>
                <span className="text-muted-foreground">Stock #{row.stock_id ?? 'indisponible'}</span>
                <span className="text-muted-foreground">Opérateur #{row.operateur_id ?? 'indisponible'}</span>
                <span className="text-muted-foreground">{row.date_mouvement || 'Date indisponible'}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
