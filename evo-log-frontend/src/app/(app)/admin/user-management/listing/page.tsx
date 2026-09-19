'use client';

import { useEffect, useMemo, useState } from 'react';
import { RefreshCw, Search, Users } from 'lucide-react';
import { adminAPI } from '@/lib/api-client';

type UserRow = {
  id: number;
  username?: string;
  full_name?: string | null;
  email: string;
  phone?: string | null;
  is_active: boolean;
  company_id?: number | null;
  roles?: Array<{ name?: string }>;
  department?: { name?: string } | null;
  last_login?: string | null;
};

export default function UserManagementPage() {
  const [users, setUsers] = useState<UserRow[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await adminAPI.getUsers({ limit: 500 });
      const data = response.data;
      setUsers(Array.isArray(data) ? data : data?.items || []);
    } catch (requestError: any) {
      setUsers([]);
      setError(requestError?.response?.data?.detail || 'Impossible de charger les utilisateurs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = useMemo(() => users.filter(user => {
    const query = search.toLowerCase();
    return !query || `${user.full_name || ''} ${user.username || ''} ${user.email}`.toLowerCase().includes(query);
  }), [users, search]);

  const toggleStatus = async (user: UserRow) => {
    try {
      await adminAPI.toggleUserStatus(user.id, { is_active: !user.is_active });
      await load();
    } catch (requestError: any) {
      setError(requestError?.response?.data?.detail || 'Impossible de modifier le statut.');
    }
  };

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2"><Users className="text-slate-400" size={28} /> Gestion des utilisateurs</h1>
          <p className="text-muted-foreground mt-1 text-sm">Comptes persistés de l’entreprise courante</p>
        </div>
        <button onClick={load} disabled={loading} className="px-3 py-2 rounded-xl border border-border text-sm"><RefreshCw size={14} className={`inline mr-2 ${loading ? 'animate-spin' : ''}`} /> Actualiser</button>
      </div>
      {error && <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm">{error}</div>}
      <div className="relative max-w-md">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm" placeholder="Rechercher nom, email..." value={search} onChange={event => setSearch(event.target.value)} />
      </div>
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        {loading ? <div className="p-6 text-muted-foreground">Chargement...</div> : filtered.length === 0 ? <div className="p-6 text-muted-foreground">Aucun utilisateur enregistré.</div> : (
          <div className="divide-y divide-border">
            {filtered.map(user => (
              <div key={user.id} className="p-4 grid grid-cols-1 md:grid-cols-6 gap-2 items-center text-sm">
                <span className="font-semibold text-foreground">{user.full_name || user.username || 'Nom indisponible'}</span>
                <span className="text-muted-foreground">{user.email}</span>
                <span className="text-muted-foreground">{user.roles?.map(role => role.name).filter(Boolean).join(', ') || 'Rôle indisponible'}</span>
                <span className="text-muted-foreground">{user.department?.name || 'Département indisponible'}</span>
                <span className={user.is_active ? 'text-emerald-400' : 'text-amber-400'}>{user.is_active ? 'ACTIF' : 'INACTIF'}</span>
                <button onClick={() => toggleStatus(user)} className="px-2 py-1 rounded-lg border border-border text-xs text-foreground">{user.is_active ? 'Désactiver' : 'Activer'}</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
