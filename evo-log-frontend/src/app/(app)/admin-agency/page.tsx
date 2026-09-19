'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Building2, Search, Plus, CheckCircle2, MapPin, Phone, Mail,
  Users, RefreshCw, X, Shield, Globe
} from 'lucide-react';
import { adminAgencyAPI } from '@/lib/api-client';

interface AgencyItem {
  id: number;
  code: string;
  name: string;
  address?: string;
  city?: string;
  country?: string;
  phone?: string;
  email?: string;
  is_active: boolean;
  is_headquarters: boolean;
  users_count: number;
}

export default function AdminAgencyPage() {
  const [items, setItems] = useState<AgencyItem[]>([]);
  const [stats, setStats] = useState({
    total_agences: 0,
    actives: 0,
    sieges_sociaux: 0,
    repartition_villes: [] as { ville: string; agences: number }[],
  });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Formulaire
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    address: 'Quai Maritime n°3, Port Autonome',
    city: 'Douala',
    country: 'Cameroun',
    phone: '+237 233 42 10 00',
    email: 'direction@cadc-log.cm',
    is_active: true,
    is_headquarters: false,
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resList, resStats] = await Promise.allSettled([
        adminAgencyAPI.getAll({ search: search || undefined }),
        adminAgencyAPI.getStats()
      ]);

      if (resList.status === 'fulfilled' && resList.value.data) {
        setItems(resList.value.data.items || []);
      }
      if (resStats.status === 'fulfilled' && resStats.value.data) {
        setStats(resStats.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement agences:', err);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await adminAgencyAPI.create(formData);
      setIsModalOpen(false);
      setFormData({
        code: '',
        name: '',
        address: 'Quai Maritime n°3, Port Autonome',
        city: 'Douala',
        country: 'Cameroun',
        phone: '+237 233 42 10 00',
        email: 'direction@cadc-log.cm',
        is_active: true,
        is_headquarters: false,
      });
      await fetchData();
    } catch (err) {
      console.error('Erreur création agence:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Confirmer la suppression ou désactivation de cette agence ?')) return;
    try {
      await adminAgencyAPI.delete(id);
      await fetchData();
    } catch (err) {
      console.error('Erreur suppression agence:', err);
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Building2 className="w-3.5 h-3.5" /> Gouvernance & Réseau d'Agences
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Agences & Succursales Régionales
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Déploiement territorial et gestion multi-sites (Douala Port, Kribi Deep Sea, Yaoundé, Garoua).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchData()}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
            title="Actualiser"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-lg shadow-blue-600/20 transition-all"
          >
            <Plus className="w-4 h-4" /> Nouvelle Succursale
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Total Agences</span>
            <Building2 className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.total_agences}
          </div>
          <div className="text-xs text-slate-500 mt-1">Implantations physiques</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Agences Opérationnelles</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            {stats.actives}
          </div>
          <div className="text-xs text-slate-500 mt-1">Connectées au réseau temps réel</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Siège Social</span>
            <Shield className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.sieges_sociaux > 0 ? 'Direction Générale' : 'Actif'}
          </div>
          <div className="text-xs text-slate-500 mt-1">Douala Bonanjo / PAD</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Villes Couvertes</span>
            <Globe className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.repartition_villes.length || 3}
          </div>
          <div className="text-xs text-slate-500 mt-1">Corridors Douala, Kribi, Nord</div>
        </div>
      </div>

      {/* Search */}
      <div className="flex bg-slate-900/60 p-4 rounded-2xl border border-slate-800 max-w-md">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Rechercher par nom d'agence, code, ville..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Grid of Agencies */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full py-12 text-center text-slate-400">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
            Chargement des agences...
          </div>
        ) : items.length === 0 ? (
          <div className="col-span-full py-12 text-center text-slate-500">
            Aucune agence enregistrée.
          </div>
        ) : (
          items.map((a) => (
            <div key={a.id} className="bg-slate-900/80 border border-slate-800 p-6 rounded-3xl shadow-xl hover:border-slate-700 transition-all space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-mono font-bold text-blue-400 px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20">
                    {a.code}
                  </span>
                  <h3 className="text-lg font-bold text-white mt-2 flex items-center gap-2">
                    {a.name}
                  </h3>
                </div>
                {a.is_headquarters && (
                  <span className="text-[11px] font-bold px-2 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400">
                    Siège
                  </span>
                )}
              </div>

              <div className="space-y-2 text-xs text-slate-300 pt-2 border-t border-slate-800/60">
                <div className="flex items-center gap-2">
                  <MapPin className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                  <span>{a.city}, {a.country} ({a.address || 'Quartier Portuaire'})</span>
                </div>
                {a.phone && (
                  <div className="flex items-center gap-2">
                    <Phone className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span>{a.phone}</span>
                  </div>
                )}
                {a.email && (
                  <div className="flex items-center gap-2">
                    <Mail className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span>{a.email}</span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <Users className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                  <span>{a.users_count} collaborateur(s) rattaché(s)</span>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between">
                <span className={`inline-flex items-center gap-1 text-xs font-bold ${
                  a.is_active ? 'text-emerald-400' : 'text-slate-500'
                }`}>
                  <span className={`w-2 h-2 rounded-full ${a.is_active ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                  {a.is_active ? 'Opérationnelle' : 'Inactif'}
                </span>
                <button
                  onClick={() => handleDelete(a.id)}
                  className="text-xs text-rose-400 hover:text-rose-300 font-medium"
                >
                  Supprimer
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal Création Agence */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Building2 className="w-5 h-5 text-blue-400" /> Nouvelle Succursale
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Code Agence (Trigramme)</label>
                  <input
                    type="text"
                    required
                    placeholder="ex: KBI"
                    value={formData.code}
                    onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Nom de l'Agence</label>
                  <input
                    type="text"
                    required
                    placeholder="ex: Agence Port Kribi"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Ville</label>
                  <input
                    type="text"
                    required
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Pays</label>
                  <input
                    type="text"
                    required
                    value={formData.country}
                    onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Adresse Complète</label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Téléphone</label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <input
                  type="checkbox"
                  id="hq"
                  checked={formData.is_headquarters}
                  onChange={(e) => setFormData({ ...formData, is_headquarters: e.target.checked })}
                  className="rounded bg-slate-800 border-slate-700 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="hq" className="text-xs font-semibold text-slate-300">
                  Désigner comme Siège Social (Headquarters)
                </label>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold shadow-lg shadow-blue-600/20 transition-all"
                >
                  Créer l'Agence
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
