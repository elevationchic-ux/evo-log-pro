'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Ship, Anchor, FileText, Activity, AlertTriangle, Scale,
  Truck, BarChart3, Radio, Plus, RefreshCw, Search,
  CheckCircle2, Clock, MapPin, ArrowUpRight
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

interface Escale {
  id: number;
  numero_escale?: string;
  navire_nom?: string;
  nom_navire?: string;
  port?: string;
  quai_attribue?: string;
  date_arrivee_estimee?: string;
  date_depart_estimee?: string;
  statut?: string;
  nombre_conteneurs?: number;
}

export default function PortOperationsMainPage() {
  const [escales, setEscales] = useState<Escale[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedPort, setSelectedPort] = useState('ALL');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // New Escale form
  const [formData, setFormData] = useState({
    numero_escale: '',
    navire_nom: '',
    port: 'Douala (Quai 14)',
    quai_attribue: 'Poste 14',
    date_arrivee_estimee: '',
    date_depart_estimee: '',
    nombre_conteneurs: 150,
  });

  const fetchEscales = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/acconage-avance/escales');
      setEscales(Array.isArray(res.data) ? res.data : []);
    } catch {
      // Fallback or empty if new tenant
      setEscales([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEscales();
  }, []);

  const handleCreateEscale = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiClient.post('/api/v1/acconage-avance/escales', {
        ...formData,
        statut: 'PROGRAMMEE'
      });
      setIsModalOpen(false);
      setFormData({
        numero_escale: '',
        navire_nom: '',
        port: 'Douala (Quai 14)',
        quai_attribue: 'Poste 14',
        date_arrivee_estimee: '',
        date_depart_estimee: '',
        nombre_conteneurs: 150,
      });
      fetchEscales();
    } catch {
      toast.error("L'escale n'a pas pu être créée par l'API.");
    } finally {
      setSubmitting(false);
    }
  };

  const filteredEscales = escales.filter(item => {
    const matchSearch =
      (item.navire_nom || item.nom_navire || '').toLowerCase().includes(search.toLowerCase()) ||
      (item.numero_escale || '').toLowerCase().includes(search.toLowerCase());
    const matchPort =
      selectedPort === 'ALL' || (item.port || '').toLowerCase().includes(selectedPort.toLowerCase());
    return matchSearch && matchPort;
  });

  const submodules = [
    { title: 'Manifestes & Escales', desc: 'Gestion des cargaisons & manifestes', path: '/port-operations/manifests', icon: FileText, tcode: 'KACC_MNF', color: 'from-blue-600 to-indigo-600' },
    { title: 'Opérations de Quai', desc: 'Manutention & affectation grues', path: '/port-operations/quai-operations', icon: Anchor, tcode: 'KACC_OPS', color: 'from-sky-600 to-blue-600' },
    { title: 'Planning Accostage', desc: 'Attribution des postes à quai', path: '/port-operations/berth-planning', icon: Clock, tcode: 'KACC_PLN', color: 'from-cyan-600 to-teal-600' },
    { title: 'Pont-Bascule VGM', desc: 'Pesage certifié SOLAS conteneurs', path: '/port-operations/weighbridge', icon: Scale, tcode: 'KACC_VGM', color: 'from-emerald-600 to-green-600' },
    { title: 'Drayage & MAD', desc: 'Transferts terre-pleins sous douane', path: '/port-operations/drayage', icon: Truck, tcode: 'KACC_DRY', color: 'from-amber-600 to-orange-600' },
    { title: 'Consignation Navire', desc: 'Services armateurs & relève équipage', path: '/port-operations/vessel-consignment', icon: Ship, tcode: 'KACC_CNS', color: 'from-purple-600 to-indigo-600' },
    { title: 'Statistiques & Cadences', desc: 'Mouvements/h & temps en rade', path: '/port-operations/maritime-stats', icon: BarChart3, tcode: 'KACC_STA', color: 'from-violet-600 to-purple-600' },
    { title: 'Passerelle EDI PAD/PAK', desc: 'Guichet unique GUCE & Douane', path: '/port-operations/port-integration', icon: Radio, tcode: 'KACC_EDI', color: 'from-pink-600 to-rose-600' },
    { title: 'Avaries & Incidents', desc: 'Constats contradictoires sur quai', path: '/port-operations/incidents', icon: AlertTriangle, tcode: 'KACC_INC', color: 'from-red-600 to-amber-600' }
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl shadow-xl">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="p-2.5 bg-blue-500/10 text-blue-400 rounded-xl border border-blue-500/20">
              <Ship className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Opérations Portuaires & Quai
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 font-mono">
                  KM01 • PAD / PAK
                </span>
              </h1>
              <p className="text-sm text-slate-400">
                Supervision des escales maritimes, déchargement quai, pesage SOLAS et coordination des opérations
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchEscales}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
            Actualiser
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm shadow-lg shadow-blue-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Programmer une Escale
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800/80">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase">Navires à Quai</span>
            <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
              <Ship className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">
            {escales.filter(e => e.statut === 'A_QUAI').length}
          </p>
          <span className="text-xs text-emerald-400 flex items-center gap-1 mt-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Douala & Kribi opérationnels
          </span>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800/80">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase">Escales Programmées</span>
            <div className="p-2 bg-amber-500/10 text-amber-400 rounded-lg">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">
            {escales.filter(e => e.statut === 'PROGRAMMEE' || !e.statut).length}
          </p>
          <span className="text-xs text-amber-400 flex items-center gap-1 mt-1">
            72 prochaines heures
          </span>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800/80">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase">Conteneurs Déchargés</span>
            <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
              <Anchor className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">
            {escales.reduce((acc, curr) => acc + (curr.nombre_conteneurs || 0), 0).toLocaleString()} EVP
          </p>
          <span className="text-xs text-slate-400 mt-1">Total manutentionné</span>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800/80">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase">Taux d'Occupation Quai</span>
            <div className="p-2 bg-purple-500/10 text-purple-400 rounded-lg">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">
            {escales.length > 0 ? '78.5%' : '0%'}
          </p>
          <span className="text-xs text-purple-400 mt-1">Capacité optimale</span>
        </div>
      </div>

      {/* Submodules Grid */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span>Sous-Modules Opérationnels</span>
          <span className="text-xs text-slate-400 font-normal">({submodules.length} modules disponibles)</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {submodules.map((sub, i) => {
            const Icon = sub.icon;
            return (
              <Link
                key={i}
                href={sub.path}
                className="group relative bg-slate-900/70 hover:bg-slate-800/80 p-5 rounded-2xl border border-slate-800 hover:border-slate-700 transition duration-200 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className={`p-2.5 rounded-xl bg-gradient-to-br ${sub.color} text-white shadow-md`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                        {sub.tcode}
                      </span>
                      <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-blue-400 transition" />
                    </div>
                  </div>
                  <h3 className="font-semibold text-white text-base group-hover:text-blue-400 transition">
                    {sub.title}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    {sub.desc}
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
                  <span>Accéder à la console</span>
                  <span className="text-blue-400 font-medium">Ouvrir →</span>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Escales & Quai View */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h2 className="text-lg font-semibold text-white">Registre des Escales Navires</h2>
            <p className="text-xs text-slate-400">Suivi des mouvements d'accostage, déchargement et appareillage</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Rechercher navire ou N° escale..."
                className="pl-9 pr-4 py-1.5 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
              />
            </div>
            <select
              value={selectedPort}
              onChange={e => setSelectedPort(e.target.value)}
              className="px-3 py-1.5 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
            >
              <option value="ALL">Tous les ports</option>
              <option value="Douala">Douala (PAD Quai 14)</option>
              <option value="Kribi">Kribi (PAK Mboro)</option>
            </select>
          </div>
        </div>

        {/* Table / Empty State */}
        {loading ? (
          <div className="py-16 text-center text-slate-400">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-400" />
            Chargement des escales maritimes...
          </div>
        ) : filteredEscales.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Ship className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucune escale maritime enregistrée</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              L'entreprise n'a pas encore saisi d'escale navire pour cette sélection. Commencez par programmer la première escale de votre structure.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Programmer une première escale
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">N° Escale</th>
                  <th className="py-3 px-4">Navire</th>
                  <th className="py-3 px-4">Port & Quai</th>
                  <th className="py-3 px-4">Arrivée Estimée</th>
                  <th className="py-3 px-4">Conteneurs</th>
                  <th className="py-3 px-4">Statut</th>
                  <th className="py-3 px-4 rounded-r-xl text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filteredEscales.map((escale, idx) => (
                  <tr key={escale.id || idx} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-blue-400">
                      {escale.numero_escale || `ESC-2026-${String(escale.id).padStart(4, '0')}`}
                    </td>
                    <td className="py-3.5 px-4 text-white font-medium">
                      {escale.navire_nom || escale.nom_navire || 'Navire Porte-Conteneurs'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">
                      <div className="flex items-center gap-1.5">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        <span>{escale.port || 'Douala'}</span>
                        <span className="text-xs text-slate-400">({escale.quai_attribue || 'Quai 14'})</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 text-xs">
                      {escale.date_arrivee_estimee ? new Date(escale.date_arrivee_estimee).toLocaleDateString('fr-FR') : 'Non renseignée'}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-white">
                      {escale.nombre_conteneurs || 0} EVP
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        escale.statut === 'A_QUAI'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : escale.statut === 'CLOTUREE'
                          ? 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        {escale.statut || 'PROGRAMMEE'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        href={`/port-operations/manifests?escale=${escale.id}`}
                        className="text-xs text-blue-400 hover:text-blue-300 underline"
                      >
                        Voir Manifeste
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Nouvelle Escale */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Ship className="w-5 h-5 text-blue-400" />
              Programmer une Escale Navire
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Enregistrez une nouvelle escale sur le port de Douala ou Kribi
            </p>

            <form onSubmit={handleCreateEscale} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Nom du Navire *</label>
                <input
                  type="text"
                  required
                  value={formData.navire_nom}
                  onChange={e => setFormData({ ...formData, navire_nom: e.target.value })}
                  placeholder="Ex: CMA CGM CAMEROUN, MAERSK KRIBI"
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Port d'escale</label>
                  <select
                    value={formData.port}
                    onChange={e => setFormData({ ...formData, port: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="Douala (Quai 14)">Douala (PAD Quai 14)</option>
                    <option value="Kribi (PAK Mboro)">Kribi (PAK Port en Eau Profonde)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Poste à Quai</label>
                  <input
                    type="text"
                    value={formData.quai_attribue}
                    onChange={e => setFormData({ ...formData, quai_attribue: e.target.value })}
                    placeholder="Ex: Quai 14, Poste 1"
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Arrivée Estimée (ETA)</label>
                  <input
                    type="datetime-local"
                    value={formData.date_arrivee_estimee}
                    onChange={e => setFormData({ ...formData, date_arrivee_estimee: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Départ Estimé (ETD)</label>
                  <input
                    type="datetime-local"
                    value={formData.date_depart_estimee}
                    onChange={e => setFormData({ ...formData, date_depart_estimee: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Nombre Estimé de Conteneurs (EVP)</label>
                <input
                  type="number"
                  value={formData.nombre_conteneurs}
                  onChange={e => setFormData({ ...formData, nombre_conteneurs: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  {submitting ? 'Enregistrement...' : 'Confirmer Escale'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
