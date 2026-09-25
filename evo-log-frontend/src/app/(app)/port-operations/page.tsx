'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Ship, Anchor, FileText, Activity, AlertTriangle, Scale,
  Truck, BarChart3, Radio, Plus, RefreshCw, Search,
  CheckCircle2, Clock, MapPin, ArrowUpRight, Loader2
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { useSettings } from '@/components/layout/SettingsProvider';

interface Escale {
  id: number;
  numero_escale?: string;
  navire_nom?: string;
  port?: string;
  poste_quai?: string;
  quai_attribue?: string;
  date_arrivee_estimee?: string;
  date_depart_estimee?: string;
  statut?: string;
  nombre_conteneurs?: number;
}

export default function PortOperationsMainPage() {
  const { language } = useSettings();
  const lang = language || 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

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
    quai_attribue: '',
    date_arrivee_estimee: '',
    date_depart_estimee: '',
    nombre_conteneurs: 0,
  });

  const fetchEscales = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/acconage-avance/escales');
      const list = Array.isArray(res.data) ? res.data : [];
      setEscales(
        list.map((e: any) => ({
          ...e,
          quai_attribue: e.poste_quai || undefined,
          port: e.poste_quai ? String(e.poste_quai).split('  ')[0] : undefined,
        }))
      );
    } catch {
      setEscales([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEscales();
  }, []);

  const resetForm = () =>
    setFormData({
      numero_escale: '',
      navire_nom: '',
      port: 'Douala (Quai 14)',
      quai_attribue: '',
      date_arrivee_estimee: '',
      date_depart_estimee: '',
      nombre_conteneurs: 0,
    });

  const handleCreateEscale = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const posteQuai = [formData.port, formData.quai_attribue].filter(Boolean).join('  ');
      await apiClient.post('/api/v1/acconage-avance/escales', {
        numero_escale: formData.numero_escale || undefined,
        navire_nom: formData.navire_nom,
        poste_quai: posteQuai || undefined,
        date_arrivee_prevue: formData.date_arrivee_estimee
          ? new Date(formData.date_arrivee_estimee).toISOString()
          : undefined,
        date_depart_prevue: formData.date_depart_estimee
          ? new Date(formData.date_depart_estimee).toISOString()
          : undefined,
        nombre_conteneurs: formData.nombre_conteneurs || undefined,
      });
      toast.success(t('Escale programmée', 'Port call scheduled'));
      setIsModalOpen(false);
      resetForm();
      fetchEscales();
    } catch {
      toast.error(t('Erreur réseau : l\'escale n\'a pas pu être enregistrée.', 'Network error: the port call could not be saved.'));
    } finally {
      setSubmitting(false);
    }
  };

  const filteredEscales = escales.filter(item => {
    const matchSearch =
      (item.navire_nom || '').toLowerCase().includes(search.toLowerCase()) ||
      (item.numero_escale || '').toLowerCase().includes(search.toLowerCase());
    const matchPort =
      selectedPort === 'ALL' || (item.port || '').toLowerCase().includes(selectedPort.toLowerCase());
    return matchSearch && matchPort;
  });

  const submodules = [
    { title: t('Manifestes & Escales', 'Manifests & Port Calls'), desc: t('Gestion des cargaisons & manifestes', 'Cargo & manifest management'), path: '/port-operations/manifests', icon: FileText, tcode: 'KACC_MNF' },
    { title: t('Opérations de Quai', 'Wharf Operations'), desc: t('Manutention & affectation grues', 'Stevedoring & crane assignment'), path: '/port-operations/quai-operations', icon: Anchor, tcode: 'KACC_OPS' },
    { title: t('Planning Accostage', 'Berth Planning'), desc: t('Attribution des postes à quai', 'Berth allocation'), path: '/port-operations/berth-planning', icon: Clock, tcode: 'KACC_PLN' },
    { title: t('Pont-Bascule VGM', 'VGM Weighbridge'), desc: t('Pesage certifié SOLAS conteneurs', 'SOLAS-certified container weighing'), path: '/port-operations/weighbridge', icon: Scale, tcode: 'KACC_VGM' },
    { title: t('Drayage & MAD', 'Drayage & MAD'), desc: t('Transferts terre-pleins sous douane', 'Bonded yard transfers'), path: '/port-operations/drayage', icon: Truck, tcode: 'KACC_DRY' },
    { title: t('Consignation Navire', 'Ship Consignment'), desc: t('Services armateurs & relève équipage', 'Shipowner services & crew change'), path: '/port-operations/vessel-consignment', icon: Ship, tcode: 'KACC_CNS' },
    { title: t('Statistiques & Cadences', 'Stats & Rates'), desc: t('Mouvements/h & temps en rade', 'Moves/h & anchorage time'), path: '/port-operations/maritime-stats', icon: BarChart3, tcode: 'KACC_STA' },
    { title: t('Passerelle EDI PAD/PAK', 'PAD/PAK EDI Gateway'), desc: t('Guichet unique GUCE & Douane', 'GUCE single window & Customs'), path: '/port-operations/port-integration', icon: Radio, tcode: 'KACC_EDI' },
    { title: t('Avaries & Incidents', 'Damages & Incidents'), desc: t('Constats contradictoires sur quai', 'Joint survey reports on wharf'), path: '/port-operations/incidents', icon: AlertTriangle, tcode: 'KACC_INC' },
  ];

  const cloturees = escales.filter(e => e.statut === 'CLOTUREE').length;

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
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex flex-wrap items-center gap-2">
                {t('Opérations Portuaires & Quai', 'Port & Wharf Operations')}
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 font-mono">
                  KM01 • PAD / PAK
                </span>
              </h1>
              <p className="text-sm text-slate-400">
                {t('Supervision des escales maritimes, déchargement quai, pesage SOLAS et coordination des opérations', 'Supervision of port calls, wharf discharge, SOLAS weighing and operations coordination')}
              </p>
            </div>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={fetchEscales}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm shadow-lg shadow-blue-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Programmer une Escale', 'Schedule a Port Call')}
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800/80">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase">{t('Navires à Quai', 'Ships at Berth')}</span>
            <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
              <Ship className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">
            {escales.filter(e => e.statut === 'A_QUAI').length}
          </p>
          <span className="text-xs text-slate-400 flex items-center gap-1 mt-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> {t('Escales en cours', 'Ongoing port calls')}
          </span>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800/80">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase">{t('Escales Programmées', 'Scheduled Port Calls')}</span>
            <div className="p-2 bg-amber-500/10 text-amber-400 rounded-lg">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">
            {escales.filter(e => e.statut === 'PROGRAMMEE' || !e.statut).length}
          </p>
          <span className="text-xs text-amber-400 mt-1">{t('À confirmer à l\'arrivée', 'To confirm on arrival')}</span>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800/80">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase">{t('Conteneurs Déclarés', 'Declared Containers')}</span>
            <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
              <Anchor className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">
            {escales.reduce((acc, curr) => acc + (curr.nombre_conteneurs || 0), 0).toLocaleString()} EVP
          </p>
          <span className="text-xs text-slate-400 mt-1">{t('Total déclaré sur escales', 'Total declared across port calls')}</span>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800/80">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase">{t('Escales Clôturées', 'Closed Port Calls')}</span>
            <div className="p-2 bg-purple-500/10 text-purple-400 rounded-lg">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">
            {escales.length > 0 ? Math.round((cloturees / escales.length) * 100) : 0}%
          </p>
          <span className="text-xs text-purple-400 mt-1">
            {cloturees} / {escales.length} {t('clôturées', 'closed')}
          </span>
        </div>
      </div>

      {/* Submodules Grid */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span>{t('Sous-Modules Opérationnels', 'Operational Submodules')}</span>
          <span className="text-xs text-slate-400 font-normal">({submodules.length} {t('modules disponibles', 'modules available')})</span>
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
                    <div className="p-2.5 rounded-xl bg-blue-600 text-white shadow-md">
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
                  <span>{t('Accéder à la console', 'Open console')}</span>
                  <span className="text-blue-400 font-medium">{t('Ouvrir →', 'Open →')}</span>
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
            <h2 className="text-lg font-semibold text-white">{t('Registre des Escales Navires', 'Ship Port Call Register')}</h2>
            <p className="text-xs text-slate-400">{t('Suivi des mouvements d\'accostage, déchargement et appareillage', 'Tracking of berthing, discharging and sailing movements')}</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder={t('Rechercher navire ou N° escale...', 'Search vessel or port call no...')}
                className="pl-9 pr-4 py-1.5 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
              />
            </div>
            <select
              value={selectedPort}
              onChange={e => setSelectedPort(e.target.value)}
              className="px-3 py-1.5 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
            >
              <option value="ALL">{t('Tous les ports', 'All ports')}</option>
              <option value="Douala">{t('Douala (PAD Quai 14)', 'Douala (PAD Wharf 14)')}</option>
              <option value="Kribi">{t('Kribi (PAK Mboro)', 'Kribi (PAK Mboro)')}</option>
            </select>
          </div>
        </div>

        {/* Table / Empty State */}
        {loading ? (
          <div className="py-16 text-center text-slate-400">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-400" />
            {t('Chargement des escales maritimes...', 'Loading maritime port calls...')}
          </div>
        ) : filteredEscales.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Ship className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">{t('Aucune escale maritime enregistrée', 'No maritime port call recorded')}</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {t('L\'entreprise n\'a pas encore saisi d\'escale navire pour cette sélection. Commencez par programmer la première escale de votre structure.', 'Your company has not entered a port call for this selection yet. Schedule your first port call.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              {t('Programmer une première escale', 'Schedule a first port call')}
            </button>
          </div>
        ) : (
          <>
            {/* Mobile cards */}
            <div className="space-y-3 lg:hidden">
              {filteredEscales.map(escale => (
                <div key={escale.id} className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="font-mono text-xs text-blue-400">{escale.numero_escale || `#${escale.id}`}</div>
                      <div className="text-white font-medium">{escale.navire_nom || ''}</div>
                    </div>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border shrink-0 ${escale.statut === 'A_QUAI'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : escale.statut === 'CLOTUREE'
                          ? 'bg-slate-500/10 text-slate-400 border-slate-500/20'
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      }`}>
                      {escale.statut || 'PROGRAMMEE'}
                    </span>
                  </div>
                  {escale.poste_quai && (
                    <div className="flex items-center gap-1.5 text-xs text-slate-300">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" /> {escale.poste_quai}
                    </div>
                  )}
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400 font-mono">
                    {escale.date_arrivee_estimee && <span>ETA: {new Date(escale.date_arrivee_estimee).toLocaleDateString('fr-FR')}</span>}
                    {escale.nombre_conteneurs ? <span>{escale.nombre_conteneurs} EVP</span> : null}
                  </div>
                  <Link href={`/port-operations/manifests?escale=${escale.id}`} className="text-xs text-blue-400 hover:text-blue-300 underline">
                    {t('Voir Manifeste', 'View Manifest')}
                  </Link>
                </div>
              ))}
            </div>
            {/* Desktop table */}
            <div className="hidden lg:block overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                  <tr>
                    <th className="py-3 px-4 rounded-l-xl">{t('N° Escale', 'Port Call No.')}</th>
                    <th className="py-3 px-4">{t('Navire', 'Vessel')}</th>
                    <th className="py-3 px-4">{t('Port & Quai', 'Port & Berth')}</th>
                    <th className="py-3 px-4">{t('Arrivée Estimée', 'Estimated Arrival')}</th>
                    <th className="py-3 px-4">{t('Conteneurs', 'Containers')}</th>
                    <th className="py-3 px-4">{t('Statut', 'Status')}</th>
                    <th className="py-3 px-4 rounded-r-xl text-right">{t('Actions', 'Actions')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filteredEscales.map((escale, idx) => (
                    <tr key={escale.id || idx} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-mono font-medium text-blue-400">
                        {escale.numero_escale || `#${escale.id}`}
                      </td>
                      <td className="py-3.5 px-4 text-white font-medium">
                        {escale.navire_nom || ''}
                      </td>
                      <td className="py-3.5 px-4 text-slate-300">
                        <div className="flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5 text-slate-400" />
                          <span>{escale.poste_quai || ''}</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 text-xs">
                        {escale.date_arrivee_estimee ? new Date(escale.date_arrivee_estimee).toLocaleDateString('fr-FR') : ''}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-white">
                        {escale.nombre_conteneurs ? `${escale.nombre_conteneurs} EVP` : ''}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${escale.statut === 'A_QUAI'
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
                          {t('Voir Manifeste', 'View Manifest')}
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Modal Nouvelle Escale */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Ship className="w-5 h-5 text-blue-400" />
              {t('Programmer une Escale Navire', 'Schedule a Ship Port Call')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Enregistrez une nouvelle escale sur le port de Douala ou Kribi', 'Register a new port call at Douala or Kribi port')}
            </p>

            <form onSubmit={handleCreateEscale} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Nom du Navire *', 'Vessel Name *')}</label>
                <input
                  type="text"
                  required
                  value={formData.navire_nom}
                  onChange={e => setFormData({ ...formData, navire_nom: e.target.value })}
                  placeholder={t('Ex: CMA CGM CAMEROUN, MAERSK KRIBI', 'e.g. CMA CGM CAMEROUN, MAERSK KRIBI')}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t("Port d'escale", 'Port of Call')}</label>
                  <select
                    value={formData.port}
                    onChange={e => setFormData({ ...formData, port: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="Douala (Quai 14)">{t('Douala (PAD Quai 14)', 'Douala (PAD Wharf 14)')}</option>
                    <option value="Kribi (PAK Mboro)">{t('Kribi (PAK Port en Eau Profonde)', 'Kribi (PAK Deep-Water Port)')}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Poste à Quai', 'Berth')}</label>
                  <input
                    type="text"
                    value={formData.quai_attribue}
                    onChange={e => setFormData({ ...formData, quai_attribue: e.target.value })}
                    placeholder={t('Ex: Quai 14, Poste 1', 'e.g. Wharf 14, Berth 1')}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Arrivée Estimée (ETA)', 'Estimated Arrival (ETA)')}</label>
                  <input
                    type="datetime-local"
                    value={formData.date_arrivee_estimee}
                    onChange={e => setFormData({ ...formData, date_arrivee_estimee: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Départ Estimé (ETD)', 'Estimated Departure (ETD)')}</label>
                  <input
                    type="datetime-local"
                    value={formData.date_depart_estimee}
                    onChange={e => setFormData({ ...formData, date_depart_estimee: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('N° Escale (auto si vide)', 'Port Call No. (auto if blank)')}</label>
                  <input
                    type="text"
                    value={formData.numero_escale}
                    onChange={e => setFormData({ ...formData, numero_escale: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Nombre Estimé de Conteneurs (EVP)', 'Estimated Containers (TEU)')}</label>
                  <input
                    type="number"
                    min={0}
                    value={formData.nombre_conteneurs || ''}
                    onChange={e => setFormData({ ...formData, nombre_conteneurs: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  {t('Annuler', 'Cancel')}
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-medium rounded-xl shadow-lg transition flex items-center gap-2"
                >
                  {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
                  {submitting ? t('Enregistrement...', 'Saving...') : t('Confirmer Escale', 'Confirm Port Call')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
