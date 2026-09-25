'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  Clock, Plus, Search, ArrowLeft, Ship, RefreshCw,
} from 'lucide-react';

interface BerthAllocation {
  id: number;
  numero_escale: string;
  poste_quai: string;
  port: string;
  navire_nom: string;
  date_accostage: string | null;
  date_appareillage: string | null;
  statut: string;
  tonnage?: number | null;
  nombre_conteneurs?: number | null;
}

export default function PortOperationsBerthPlanningPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [berths, setBerths] = useState<BerthAllocation[]>([]);
  const [navires, setNavires] = useState<any[]>([]);
  const [ports, setPorts] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    navire_id: '' as string | number,
    port_id: '' as string | number,
    poste_quai: 'Poste 14 (Quai Conteneurs)',
    date_arrivee_prevue: '',
    date_depart_prevue: '',
    marchandise: '',
    tonnage: '',
    nombre_conteneurs: '',
    agent: '',
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [es, nv, pt] = await Promise.all([
        apiClient.get('/api/v1/acconage/escales', { params: { limit: 200 } }),
        apiClient.get('/api/v1/acconage/navires', { params: { limit: 500 } }).catch(() => null),
        apiClient.get('/api/v1/public/ports').catch(() => null),
      ]);
      const naviresList = Array.isArray(nv?.data) ? nv.data : [];
      const portsList = Array.isArray(pt?.data) ? pt.data : [];
      setNavires(naviresList);
      setPorts(portsList);
      const nomById: Record<number, string> = {};
      naviresList.forEach((n: any) => { nomById[n.id] = n.nom; });
      const portById: Record<number, string> = {};
      portsList.forEach((p: any) => { portById[p.id] = `${p.nom} (${p.code})`; });
      const rows = Array.isArray(es?.data) ? es.data : (es?.data?.items ?? []);
      setBerths(rows.map((e: any) => ({
        id: e.id,
        numero_escale: e.numero_escale || '',
        poste_quai: e.poste_quai || '',
        port: portById[e.port_id] || `Port #${e.port_id}`,
        navire_nom: nomById[e.navire_id] || `Navire #${e.navire_id}`,
        date_accostage: e.date_arrivee_prevue || e.date_arrivee_reelle || null,
        date_appareillage: e.date_depart_prevue || e.date_depart_reelle || null,
        statut: e.statut || '',
        tonnage: e.tonnage,
        nombre_conteneurs: e.nombre_conteneurs,
      })));
    } catch {
      toast.error(t("Les escales n'ont pas pu être chargées. Vérifiez votre connexion.", 'Port calls could not be loaded. Check your connection.'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.navire_id || !formData.port_id) {
      toast.error(t('Sélectionnez un navire et un port.', 'Select a ship and a port.'));
      return;
    }
    setSaving(true);
    try {
      await apiClient.post('/api/v1/acconage/escales', {
        navire_id: Number(formData.navire_id),
        port_id: Number(formData.port_id),
        poste_quai: formData.poste_quai || undefined,
        date_arrivee_prevue: formData.date_arrivee_prevue ? new Date(formData.date_arrivee_prevue).toISOString() : undefined,
        date_depart_prevue: formData.date_depart_prevue ? new Date(formData.date_depart_prevue).toISOString() : undefined,
        marchandise: formData.marchandise || undefined,
        tonnage: formData.tonnage ? Number(formData.tonnage) : undefined,
        nombre_conteneurs: formData.nombre_conteneurs ? Number(formData.nombre_conteneurs) : undefined,
        agent: formData.agent || undefined,
      });
      toast.success(t('Escale programmée et poste attribué.', 'Port call scheduled and berth assigned.'));
      setIsModalOpen(false);
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t("Échec de l'attribution du poste.", 'Berth assignment failed.'));
    } finally {
      setSaving(false);
    }
  };

  const filtered = berths.filter(b =>
    b.navire_nom.toLowerCase().includes(search.toLowerCase()) ||
    b.poste_quai.toLowerCase().includes(search.toLowerCase()) ||
    b.port.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Opérations Portuaires', 'Port Operations')}
        </Link>
        <span>/</span>
        <span className="text-white">{t("Planning d'Accostage & Attribution des Postes", 'Berth Planning & Assignment')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 text-cyan-400 rounded-xl border border-cyan-500/20">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2 flex-wrap">
              {t("Planning d'Accostage des Postes à Quai", 'Berth Allocation Planning')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono">
                KACC_PLN
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Affectation des postes d\'accostage aux navires (escales réelles)', 'Assigning berths to ships (real port calls)')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={load} className="flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-700 text-slate-300 text-sm hover:bg-slate-800">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> {t('Actualiser', 'Refresh')}
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm shadow-lg shadow-cyan-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Attribuer un Poste à Quai', 'Assign a Berth')}
          </button>
        </div>
      </div>

      {/* Main Table card */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder={t('Rechercher par navire, poste ou port...', 'Search by ship, berth or port...')}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400 text-sm">{t('Chargement des escales…', 'Loading port calls…')}</div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Ship className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">{t('Aucune attribution de poste active', 'No active berth assignment')}</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {t('Programmez une escale pour attribuer un poste à quai au premier navire attendu.', 'Schedule a port call to assign a berth to the next expected ship.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              {t('Programmer un accostage', 'Schedule a berthing')}
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">{t('Escale', 'Call')}</th>
                  <th className="py-3 px-4">{t('Poste / Quai', 'Berth / Quay')}</th>
                  <th className="py-3 px-4">{t('Port', 'Port')}</th>
                  <th className="py-3 px-4">{t('Navire Affecté', 'Assigned Ship')}</th>
                  <th className="py-3 px-4">{t('Fenêtre Accostage → Départ', 'Berthing → Departure')}</th>
                  <th className="py-3 px-4 rounded-r-xl">{t('Statut', 'Status')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(b => (
                  <tr key={b.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono text-xs text-slate-400">{b.numero_escale}</td>
                    <td className="py-3.5 px-4 font-semibold text-white">{b.poste_quai}</td>
                    <td className="py-3.5 px-4 text-xs text-slate-300">{b.port}</td>
                    <td className="py-3.5 px-4 font-medium text-cyan-400">{b.navire_nom}</td>
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-300">
                      {b.date_accostage ? new Date(b.date_accostage).toLocaleString(lang === 'en' ? 'en-GB' : 'fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : t('ETA Inconnu', 'Unknown ETA')}
                      {' → '}
                      {b.date_appareillage ? new Date(b.date_appareillage).toLocaleString(lang === 'en' ? 'en-GB' : 'fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : t('ETD Inconnu', 'Unknown ETD')}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {b.statut}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Attribution */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Clock className="w-5 h-5 text-cyan-400" />
              {t('Attribuer un Poste à Quai', 'Assign a Berth')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Enregistrement d\'une escale réelle (navire, port, fenêtre d\'accostage)', 'Record a real port call (ship, port, berthing window)')}
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Navire *', 'Ship *')}</label>
                {navires.length === 0 ? (
                  <p className="text-xs text-slate-500">{t('Aucun navire enregistré. Créez d\'abord une fiche navire.', 'No ship registered. Create a ship record first.')}</p>
                ) : (
                  <select
                    required
                    value={formData.navire_id}
                    onChange={e => setFormData({ ...formData, navire_id: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  >
                    <option value="">{t(' Choisir un navire ', ' Choose a ship ')}</option>
                    {navires.map(n => <option key={n.id} value={n.id}>{n.nom}{n.imo ? ` (${n.imo})` : ''}</option>)}
                  </select>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Port *', 'Port *')}</label>
                  <select
                    required
                    value={formData.port_id}
                    onChange={e => setFormData({ ...formData, port_id: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  >
                    <option value="">{t(' Choisir ', ' Choose ')}</option>
                    {ports.map(p => <option key={p.id} value={p.id}>{p.nom} ({p.code})</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t("Poste d'Accostage", 'Berth')}</label>
                  <input
                    type="text"
                    value={formData.poste_quai}
                    onChange={e => setFormData({ ...formData, poste_quai: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Accostage Prévu', 'Expected Berthing')}</label>
                  <input
                    type="datetime-local"
                    value={formData.date_arrivee_prevue}
                    onChange={e => setFormData({ ...formData, date_arrivee_prevue: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Appareillage Prévu', 'Expected Departure')}</label>
                  <input
                    type="datetime-local"
                    value={formData.date_depart_prevue}
                    onChange={e => setFormData({ ...formData, date_depart_prevue: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Marchandise', 'Cargo')}</label>
                  <input
                    type="text"
                    value={formData.marchandise}
                    onChange={e => setFormData({ ...formData, marchandise: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Tonnage (t)', 'Tonnage (t)')}</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.tonnage}
                    onChange={e => setFormData({ ...formData, tonnage: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
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
                  disabled={saving || navires.length === 0}
                  className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-60 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  {saving ? t('Enregistrement…', 'Saving…') : t('Confirmer Attribution', 'Confirm Assignment')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
