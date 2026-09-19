'use client';

import { useEffect, useMemo, useState } from 'react';
import { RefreshCw, ShoppingCart } from 'lucide-react';
import { purchaseAPI } from '@/lib/api-client';

type Requisition = {
  id: number | string;
  reference?: string | null;
  titre?: string | null;
  description?: string | null;
  libelle?: string | null;
  numero_ecriture?: string | null;
  montant?: number | null;
  montant_xaf?: number | null;
  statut?: string | null;
  date_creation?: string | null;
  created_at?: string | null;
};

export default function PurchasePage() {
  const [rows, setRows] = useState<Requisition[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await purchaseAPI.getRequisitions({ limit: 500 });
      const data = response.data;
      setRows(Array.isArray(data) ? data : data?.items || data?.data || []);
    } catch (requestError: any) {
      setRows([]);
      setError(requestError?.response?.data?.detail || 'Impossible de charger les réquisitions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = useMemo(() => rows.filter(row => {
    const text = `${row.reference || row.numero_ecriture || ''} ${row.titre || row.libelle || ''} ${row.description || ''}`.toLowerCase();
    return !search || text.includes(search.toLowerCase());
  }), [rows, search]);

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2"><ShoppingCart className="text-violet-400" size={28} /> Achats & Procurement</h1>
          <p className="text-muted-foreground mt-1 text-sm">Réquisitions persistées de l’entreprise courante</p>
        </div>
        <button onClick={load} disabled={loading} className="px-3 py-2 rounded-xl border border-border text-sm"><RefreshCw size={14} className={`inline mr-2 ${loading ? 'animate-spin' : ''}`} /> Actualiser</button>
      </div>
      {error && <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm">{error}</div>}
      <input className="w-full max-w-md bg-card border border-border rounded-xl px-4 py-2.5 text-sm" placeholder="Rechercher une réquisition..." value={search} onChange={event => setSearch(event.target.value)} />
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        {loading ? <div className="p-6 text-muted-foreground">Chargement...</div> : filtered.length === 0 ? <div className="p-6 text-muted-foreground">Aucune réquisition enregistrée.</div> : (
          <div className="divide-y divide-border">
            {filtered.map(row => <div key={row.id} className="p-4 grid grid-cols-1 md:grid-cols-5 gap-2 text-sm">
              <span className="font-mono text-violet-400">{row.reference || row.numero_ecriture || `Achat #${row.id}`}</span>
              <span className="text-foreground">{row.titre || row.libelle || 'Libellé indisponible'}</span>
              <span className="text-muted-foreground">{row.description || 'Description indisponible'}</span>
              <span className="text-foreground">{Number(row.montant ?? row.montant_xaf ?? 0).toLocaleString('fr-FR')} XAF</span>
              <span className="text-muted-foreground">{row.statut || 'Statut indisponible'}</span>
            </div>)}
          </div>
        )}
      </div>
      <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-amber-200">
        Les bons de commande ne sont pas affichés tant qu’un endpoint de persistance des commandes fournisseurs n’est pas raccordé.
      </div>
    </div>
  );
}
