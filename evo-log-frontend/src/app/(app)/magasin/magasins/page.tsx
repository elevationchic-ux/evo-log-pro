'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Warehouse, ArrowLeft, Plus, Search } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import { magasinAPI } from '@/lib/api-client';

interface Magasin {
  id: number;
  code: string;
  nom: string;
  adresse?: string;
  ville?: string;
  telephone?: string;
  responsable?: string;
  capacite?: number;
  superficie?: number;
  is_active: boolean;
}

export default function MagasinsPage() {
  const [magasins, setMagasins] = useState<Magasin[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchMagasins = useCallback(async () => {
    try {
      const res: any = await magasinAPI.getMagasins({ search: search || undefined, limit: 200 });
      const body = res.data ?? res;
      setMagasins(body.items || []);
      setTotal(body.total || 0);
    } catch (err: any) {
      if (err?.response?.status === 501) {
        toast.warning('Module magasins non configure');
      } else {
        toast.error('Erreur chargement magasins');
      }
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { fetchMagasins(); }, [fetchMagasins]);

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-white animate-in fade-in duration-300">
      <Link href="/magasin/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-4">
        <ArrowLeft className="w-4 h-4" /> Retour au Dashboard
      </Link>

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-black flex items-center gap-3">
            <Warehouse className="w-7 h-7 text-amber-400" />
            Gestion des Magasins
          </h1>
          <p className="text-sm text-slate-400 mt-1">{total} entrepot(s) enregistre(s)</p>
        </div>
      </div>

      <div className="relative mb-4 max-w-md">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Rechercher par code, nom ou ville..."
          className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500"
        />
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Chargement...</div>
      ) : magasins.length === 0 ? (
        <div className="text-center py-12 bg-slate-900 border border-slate-800 rounded-2xl">
          <Warehouse className="w-12 h-12 mx-auto text-slate-600 mb-3" />
          <p className="text-slate-400">Aucun magasin enregistre</p>
        </div>
      ) : (
        <div className="overflow-x-auto bg-slate-900 border border-slate-800 rounded-2xl">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-xs tracking-wider">
                <th className="py-3 px-4">Code</th>
                <th className="py-3 px-4">Nom</th>
                <th className="py-3 px-4">Ville</th>
                <th className="py-3 px-4">Responsable</th>
                <th className="py-3 px-4 text-right">Capacite</th>
                <th className="py-3 px-4 text-center">Actif</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {magasins.map((m) => (
                <tr key={m.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-mono font-bold text-amber-400">{m.code}</td>
                  <td className="py-3 px-4 font-medium">{m.nom}</td>
                  <td className="py-3 px-4 text-slate-400">{m.ville || '-'}</td>
                  <td className="py-3 px-4 text-slate-300">{m.responsable || '-'}</td>
                  <td className="py-3 px-4 text-right font-mono">{m.capacite ? `${m.capacite.toLocaleString()} m³` : '-'}</td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                      m.is_active
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-red-500/10 text-red-400 border border-red-500/20'
                    }`}>
                      {m.is_active ? 'Oui' : 'Non'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
