"use client";

import React, { useState, useEffect, useCallback, Suspense } from 'react';
import {
  Wrench, Plus, Search, Loader2, Zap, RefreshCw, ClipboardList, PlayCircle, CheckCircle2
} from 'lucide-react';
import { useSearchParams } from 'next/navigation';
import { apiClient, fleetAPI } from '@/lib/api-client';
import { toast } from 'sonner';
import { useSettings } from '@/components/layout/SettingsProvider';

interface MaintenanceOrder {
  id: number;
  orderCode: string;
  vehiculeId: number | null;
  vehiclePlate: string;
  vehicleType: string;
  orderType: string;
  description: string;
  technicien: string;
  plannedDate: string;
  currentKm: number | null;
  cout: number | null;
  status: string;
}

interface FleetOption {
  id: number;
  immatriculation: string;
  detail: string;
  kilometrage: number;
}

const STATUT_COLORS: Record<string, string> = {
  TERMINE: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  EN_COURS: 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse',
  PLANIFIE: 'bg-slate-800 text-slate-400 border border-slate-700',
};

function PreventiveMaintenanceInner() {
  const { language } = useSettings();
  const lang = language || 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const searchParams = useSearchParams();
  const vehiculeFilter = searchParams.get('vehicule');

  const [orders, setOrders] = useState<MaintenanceOrder[]>([]);
  const [vehicles, setVehicles] = useState<FleetOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showGenModal, setShowGenModal] = useState(false);
  const [selectedVehiculeIds, setSelectedVehiculeIds] = useState<number[]>([]);

  const [form, setForm] = useState({
    vehicule_id: '',
    type_maintenance: 'preventive',
    date_debut: '',
    kilometrage: '',
    description: '',
    cout: '',
    realisateur: '',
  });

  const loadOrders = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/maintenance', {
        params: vehiculeFilter ? { vehicule_id: vehiculeFilter } : {},
      });
      const raw = Array.isArray(res.data) ? res.data : (res.data?.items || []);
      setOrders(raw.map((m: any) => ({
        id: m.id,
        orderCode: m.ordre_id || `OT-${m.id}`,
        vehiculeId: m.vehicule_id ?? null,
        vehiclePlate: m.vehicule || '',
        vehicleType: m.vehicule_detail || m.vehicule_type || '',
        orderType: (m.type_intervention || '').toUpperCase(),
        description: m.description || '',
        technicien: m.technicien || '',
        plannedDate: m.date_debut ? new Date(m.date_debut).toLocaleDateString(lang === 'en' ? 'en-GB' : 'fr-FR') : '',
        currentKm: m.kilometrage ?? null,
        cout: m.cout_estime_xaf ?? null,
        status: m.statut || 'PLANIFIE',
      })));
    } catch {
      setOrders([]);
      toast.error(t('Erreur réseau  chargement des OT impossible', 'Network error  could not load work orders'));
    } finally {
      setLoading(false);
    }
  }, [lang, vehiculeFilter]);

  const loadVehicles = useCallback(async () => {
    try {
      const res = await fleetAPI.getVehicles({ limit: 200 });
      const raw = res.data?.items || res.data || [];
      if (Array.isArray(raw)) {
        setVehicles(raw.map((v: any) => ({
          id: Number(v.id),
          immatriculation: v.immatriculation || '',
          detail: [v.marque, v.modele, v.type_vehicule].filter(Boolean).join(' '),
          kilometrage: Number(v.kilometrage) || 0,
        })));
      }
    } catch {
      setVehicles([]);
    }
  }, []);

  useEffect(() => {
    loadOrders();
    loadVehicles();
  }, [loadOrders, loadVehicles]);

  const filtered = orders.filter(o =>
    !searchQuery ||
    o.vehiclePlate.toLowerCase().includes(searchQuery.toLowerCase()) ||
    o.orderCode.toLowerCase().includes(searchQuery.toLowerCase()) ||
    o.technicien.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.vehicule_id) {
      toast.error(t('Sélectionnez un véhicule du parc.', 'Select a vehicle from the fleet.'));
      return;
    }
    setSaving(true);
    try {
      await apiClient.post('/api/v1/maintenance/ordres', {
        vehicule_id: Number(form.vehicule_id),
        type_maintenance: form.type_maintenance,
        date_debut: form.date_debut ? new Date(form.date_debut).toISOString() : undefined,
        kilometrage: form.kilometrage ? Number(form.kilometrage) : undefined,
        description: form.description || undefined,
        cout: form.cout ? Number(form.cout) : undefined,
        realisateur: form.realisateur || undefined,
        statut: 'planifie',
      });
      toast.success(t('Ordre de travail créé', 'Work order created'));
      setShowCreateModal(false);
      setForm({ vehicule_id: '', type_maintenance: 'preventive', date_debut: '', kilometrage: '', description: '', cout: '', realisateur: '' });
      loadOrders();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : t('Erreur réseau  création impossible', 'Network error  could not create'));
    } finally {
      setSaving(false);
    }
  };

  const handleGeneratePreventive = async () => {
    if (selectedVehiculeIds.length === 0) {
      toast.error(t('Sélectionnez au moins un véhicule.', 'Select at least one vehicle.'));
      return;
    }
    setSaving(true);
    try {
      const res = await apiClient.post('/api/v1/maintenance-gmao-avance/preventif/generer-ordres', selectedVehiculeIds);
      const generated = res.data?.ordres_generes ?? 0;
      const ignored = res.data?.vehicules_ignores?.length ?? 0;
      toast.success(
        generated > 0
          ? t(`${generated} OT préventif(s) planifié(s)`, `${generated} preventive work order(s) scheduled`)
          : t(`Aucun seuil atteint  ${ignored} véhicule(s) encore sous seuil (10 000 km / 3 mois)`, `No threshold reached  ${ignored} vehicle(s) still under threshold (10,000 km / 3 months)`)
      );
      setShowGenModal(false);
      setSelectedVehiculeIds([]);
      loadOrders();
    } catch {
      toast.error(t('Erreur réseau  génération impossible', 'Network error  generation failed'));
    } finally {
      setSaving(false);
    }
  };

  const advanceStatut = async (o: MaintenanceOrder) => {
    const next = o.status === 'PLANIFIE' ? 'en_cours' : o.status === 'EN_COURS' ? 'termine' : null;
    if (!next) return;
    try {
      const payload: any = { statut: next };
      if (next === 'termine') payload.date_fin = new Date().toISOString();
      await apiClient.put(`/api/v1/maintenance/ordres/${o.id}`, payload);
      loadOrders();
    } catch {
      toast.error(t('Erreur réseau  mise à jour impossible', 'Network error  update failed'));
    }
  };

  const toggleVehicule = (id: number) => {
    setSelectedVehiculeIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
              {t('GMAO - Maintenance Préventive & Corrective', 'CMMS - Preventive & Corrective Maintenance')}
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              {t('Seuils : 10 000 km / 3 mois', 'Thresholds: 10,000 km / 3 months')}
            </span>
            {vehiculeFilter && (
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
                {t('Filtré sur un véhicule', 'Filtered on one vehicle')}
              </span>
            )}
          </div>
          <h1 className="text-xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Wrench className="w-7 h-7 sm:w-8 sm:h-8 text-amber-400 shrink-0" />
            {t('Ordres de Travail GMAO', 'CMMS Work Orders')}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            {t('Planification des entretiens préventifs par seuils kilométriques, gestion des pannes et suivi en temps réel de l\u2019atelier mécanique.', 'Preventive maintenance planning by mileage thresholds, breakdown handling and real-time mechanical workshop tracking.')}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={loadOrders}
            className="p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-slate-300 hover:text-amber-400 transition-colors"
            title={t('Actualiser', 'Refresh')}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setShowGenModal(true)}
            className="px-4 py-2.5 bg-slate-800 border border-amber-500/40 text-amber-300 font-bold text-xs rounded-xl flex items-center gap-2 hover:bg-amber-500/10 transition-colors cursor-pointer"
          >
            <Zap className="w-4 h-4" /> {t('Générer OT Préventifs', 'Generate Preventive WOs')}
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2.5 bg-gradient-to-r from-amber-600 to-orange-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> {t('Nouvel OT', 'New Work Order')}
          </button>
        </div>
      </div>

      {/* Table OT */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t('Rechercher par véhicule, code OT ou technicien...', 'Search by vehicle, WO code or technician...')}
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-16 flex items-center justify-center gap-2 text-slate-400 text-sm">
            <Loader2 className="w-5 h-5 animate-spin text-amber-400" />
            {t('Chargement des ordres de travail...', 'Loading work orders...')}
          </div>
        ) : (
          <>
            {/* Mobile cards */}
            <div className="lg:hidden p-4 space-y-3">
              {filtered.length === 0 && (
                <div className="py-12 text-center">
                  <Wrench className="w-10 h-10 text-slate-300 mx-auto mb-2" />
                  <p className="text-sm text-slate-400 font-sans">
                    {t('Aucun ordre de travail enregistré pour l\u2019instant. Créez un OT ou générez des OT préventifs depuis les seuils du parc.', 'No work order on record yet. Create one or generate preventive WOs from fleet thresholds.')}
                  </p>
                </div>
              )}
              {filtered.map(o => (
                <div key={o.id} className="bg-slate-950/60 border border-slate-800 rounded-2xl p-4 space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-bold text-amber-400 font-mono text-sm">{o.orderCode}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${STATUT_COLORS[o.status] || 'bg-slate-800 text-slate-400'}`}>{o.status}</span>
                  </div>
                  <div className="font-sans font-bold text-slate-100 text-sm">{o.vehiclePlate} <span className="font-normal text-slate-400 text-xs"> {o.vehicleType}</span></div>
                  {o.description && <p className="text-xs text-slate-300 font-sans">{o.description}</p>}
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-slate-400 font-mono">
                    <span>{o.orderType || ''}</span>
                    <span>{t('Tech.', 'Tech.')}: {o.technicien}</span>
                    <span>{o.plannedDate}</span>
                    {o.currentKm != null && <span>{o.currentKm.toLocaleString()} km</span>}
                  </div>
                  {o.status !== 'TERMINE' && (
                    <button
                      onClick={() => advanceStatut(o)}
                      className="w-full mt-1 px-3 py-2 bg-amber-500/10 border border-amber-500/30 text-amber-300 rounded-xl text-[11px] font-bold flex items-center justify-center gap-1.5"
                    >
                      {o.status === 'PLANIFIE'
                        ? <><PlayCircle className="w-3.5 h-3.5" /> {t('Démarrer l\u2019intervention', 'Start intervention')}</>
                        : <><CheckCircle2 className="w-3.5 h-3.5" /> {t('Clôturer (terminé)', 'Close (done)')}</>}
                    </button>
                  )}
                </div>
              ))}
            </div>

            {/* Desktop table */}
            <div className="hidden lg:block overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                    <th className="py-3.5 px-4">{t('Code OT & Véhicule', 'WO Code & Vehicle')}</th>
                    <th className="py-3.5 px-4">{t('Intervention', 'Intervention')}</th>
                    <th className="py-3.5 px-4">{t('Technicien', 'Technician')}</th>
                    <th className="py-3.5 px-4">{t('Date Planifiée', 'Planned Date')}</th>
                    <th className="py-3.5 px-4 text-center">{t('Type', 'Type')}</th>
                    <th className="py-3.5 px-4 text-center">{t('Statut', 'Status')}</th>
                    <th className="py-3.5 px-4 text-center">{t('Action', 'Action')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={7} className="py-16 text-center">
                        <Wrench className="w-10 h-10 text-slate-300 mx-auto mb-2" />
                        <p className="text-sm text-slate-400 font-sans">
                          {t('Aucun ordre de travail enregistré pour l\u2019instant. Créez un OT ou générez des OT préventifs depuis les seuils du parc.', 'No work order on record yet. Create one or generate preventive WOs from fleet thresholds.')}
                        </p>
                      </td>
                    </tr>
                  )}
                  {filtered.map(o => (
                    <tr key={o.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="font-bold text-amber-400">{o.orderCode}</div>
                        <div className="font-sans font-bold text-slate-100 mt-0.5">{o.vehiclePlate}</div>
                        <div className="text-[11px] text-slate-400 font-sans">{o.vehicleType}</div>
                        {o.currentKm != null && (
                          <div className="text-[11px] text-slate-500 font-mono mt-0.5">{o.currentKm.toLocaleString()} km</div>
                        )}
                      </td>
                      <td className="py-3.5 px-4 max-w-[280px] text-[11px] text-slate-300 font-sans">{o.description || ''}</td>
                      <td className="py-3.5 px-4 font-sans text-slate-300">{o.technicien}</td>
                      <td className="py-3.5 px-4 text-slate-400">{o.plannedDate}</td>
                      <td className="py-3.5 px-4 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${o.orderType?.startsWith('PREVENT') ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                            o.orderType ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                              'bg-slate-800 text-slate-400'
                          }`}>
                          {o.orderType || ''}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${STATUT_COLORS[o.status] || 'bg-slate-800 text-slate-400'}`}>
                          {o.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        {o.status !== 'TERMINE' && (
                          <button
                            onClick={() => advanceStatut(o)}
                            className="px-2.5 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-300 rounded-lg text-[10px] font-bold hover:bg-amber-500/20 transition-colors"
                          >
                            {o.status === 'PLANIFIE' ? t('Démarrer', 'Start') : t('Clôturer', 'Close')}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Create OT Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-amber-500/30 rounded-3xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="font-bold text-slate-100 text-base flex items-center gap-2">
                <ClipboardList className="w-5 h-5 text-amber-400" />
                {t('Nouvel ordre de travail', 'New work order')}
              </h3>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-slate-100">✕</button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="sm:col-span-2">
                  <label className="block text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">{t('Véhicule *', 'Vehicle *')}</label>
                  <select
                    value={form.vehicule_id}
                    onChange={(e) => setForm({ ...form, vehicule_id: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  >
                    <option value="">{t(' Sélectionner ', ' Select ')}</option>
                    {vehicles.map(v => (
                      <option key={v.id} value={v.id}>{v.immatriculation}  {v.detail}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">{t('Type', 'Type')}</label>
                  <select
                    value={form.type_maintenance}
                    onChange={(e) => setForm({ ...form, type_maintenance: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  >
                    <option value="preventive">{t('Préventive', 'Preventive')}</option>
                    <option value="corrective">{t('Corrective (panne)', 'Corrective (breakdown)')}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">{t('Date prévue', 'Planned date')}</label>
                  <input
                    type="datetime-local"
                    value={form.date_debut}
                    onChange={(e) => setForm({ ...form, date_debut: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="block text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">{t('Kilométrage', 'Mileage')}</label>
                  <input
                    type="number" min="0"
                    value={form.kilometrage}
                    onChange={(e) => setForm({ ...form, kilometrage: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">{t('Coût estimé (FCFA)', 'Estimated cost (FCFA)')}</label>
                  <input
                    type="number" min="0"
                    value={form.cout}
                    onChange={(e) => setForm({ ...form, cout: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">{t('Technicien / Réalisateur', 'Technician / Provider')}</label>
                  <input
                    value={form.realisateur}
                    onChange={(e) => setForm({ ...form, realisateur: e.target.value })}
                    placeholder={t('Ex. Chef d\u2019équipe atelier', 'E.g. Workshop team lead')}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">{t('Description des travaux', 'Scope of work')}</label>
                  <textarea
                    rows={3}
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-amber-500 resize-none"
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={saving}
                className="w-full py-2.5 bg-gradient-to-r from-amber-600 to-orange-500 text-white font-bold text-xs rounded-xl disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                {t('Enregistrer l\u2019OT', 'Save work order')}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Generate Preventive Modal */}
      {showGenModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-amber-500/30 rounded-3xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="font-bold text-slate-100 text-base flex items-center gap-2">
                <Zap className="w-5 h-5 text-amber-400" />
                {t('Générer les OT préventifs', 'Generate preventive work orders')}
              </h3>
              <button onClick={() => setShowGenModal(false)} className="text-slate-400 hover:text-slate-100">✕</button>
            </div>
            <p className="text-xs text-slate-400">
              {t('Un OT n\u2019est créé que si le véhicule a dépassé 10 000 km ou 3 mois depuis son dernier entretien préventif enregistré. Les véhicules sous seuil sont ignorés.', 'A work order is only created once a vehicle exceeded 10,000 km or 3 months since its last recorded preventive service. Vehicles under threshold are skipped.')}
            </p>
            {vehicles.length === 0 ? (
              <div className="py-8 text-center text-sm text-slate-400">
                {t('Aucun véhicule au parc  enregistrez d\u2019abord vos véhicules.', 'No vehicle in the fleet  register your vehicles first.')}
              </div>
            ) : (
              <div className="space-y-1.5 max-h-[40vh] overflow-y-auto">
                {vehicles.map(v => (
                  <label key={v.id} className="flex items-center gap-3 px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl cursor-pointer hover:border-amber-500/50">
                    <input
                      type="checkbox"
                      checked={selectedVehiculeIds.includes(v.id)}
                      onChange={() => toggleVehicule(v.id)}
                      className="accent-amber-500"
                    />
                    <span className="font-mono text-xs font-bold text-amber-400">{v.immatriculation}</span>
                    <span className="text-xs text-slate-400 truncate flex-1">{v.detail}</span>
                    <span className="text-[11px] text-slate-500 font-mono shrink-0">{v.kilometrage.toLocaleString()} km</span>
                  </label>
                ))}
              </div>
            )}
            <button
              onClick={handleGeneratePreventive}
              disabled={saving || selectedVehiculeIds.length === 0}
              className="w-full py-2.5 bg-gradient-to-r from-amber-600 to-orange-500 text-white font-bold text-xs rounded-xl disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {saving && <Loader2 className="w-4 h-4 animate-spin" />}
              {t(`Générer pour ${selectedVehiculeIds.length} véhicule(s)`, `Generate for ${selectedVehiculeIds.length} vehicle(s)`)}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ParcVehiculesPreventiveMaintenance() {
  return (
    <Suspense
      fallback={
        <div className="py-16 flex items-center justify-center gap-2 text-slate-400 text-sm">
          <Loader2 className="w-5 h-5 animate-spin text-amber-400" />
        </div>
      }
    >
      <PreventiveMaintenanceInner />
    </Suspense>
  );
}
