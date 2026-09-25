'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Ship, Plus, Search, ArrowLeft, CheckCircle2,
  Anchor, Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import apiClient from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

const REGISTRY = 'consignation-services';

interface ConsignmentService {
  id: number;
  navire_nom: string;
  type_service: string;
  prestataire: string;
  date_demande: string;
  statut: string;
  montant_estime_xaf: number;
  commentaires?: string;
}

export default function PortOperationsVesselConsignmentPage() {
  const { language } = useSettings();
  const lang = language || 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [services, setServices] = useState<ConsignmentService[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    navire_nom: '',
    type_service: 'Pilotage & Remorquage',
    prestataire: '',
    date_demande: new Date().toISOString().slice(0, 10),
    montant_estime_xaf: 0,
    commentaires: '',
  });

  const fetchServices = useCallback(async () => {
    try {
      const res = await apiClient.get(`/api/v1/registres/${REGISTRY}`);
      const list = Array.isArray(res?.data) ? res.data : (res?.data?.items || []);
      setServices(
        list.map((r: any) => ({
          id: r.id,
          navire_nom: r.navire_nom || r.reference || '',
          type_service: r.type_service || '',
          prestataire: r.prestataire || '',
          date_demande: r.date_demande || '',
          statut: r.statut || 'DEMANDE',
          montant_estime_xaf: Number(r.montant_estime_xaf) || 0,
          commentaires: r.commentaires || '',
        }))
      );
    } catch {
      toast.error(t('Impossible de charger les services navires', 'Unable to load ship services'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    fetchServices();
  }, [fetchServices]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiClient.post(`/api/v1/registres/${REGISTRY}`, {
        reference: formData.navire_nom,
        statut: 'DEMANDE',
        ...formData,
      });
      toast.success(t('Service commandé et enregistré', 'Service ordered and recorded'));
      setIsModalOpen(false);
      setFormData({
        navire_nom: '', type_service: 'Pilotage & Remorquage', prestataire: '',
        date_demande: new Date().toISOString().slice(0, 10),
        montant_estime_xaf: 0, commentaires: '',
      });
      fetchServices();
    } catch {
      toast.error(t('Erreur réseau  enregistrement impossible', 'Network error  could not save'));
    } finally {
      setSaving(false);
    }
  };

  const marquerServi = async (svc: ConsignmentService) => {
    try {
      await apiClient.put(`/api/v1/registres/${REGISTRY}/${svc.id}`, { statut: 'SERVICE_FAIT' });
      toast.success(t('Service marqué comme effectué', 'Service marked as done'));
      fetchServices();
    } catch {
      toast.error(t('Erreur réseau  mise à jour impossible', 'Network error  could not update'));
    }
  };

  const filtered = services.filter(s =>
    s.navire_nom.toLowerCase().includes(search.toLowerCase()) ||
    s.type_service.toLowerCase().includes(search.toLowerCase()) ||
    s.prestataire.toLowerCase().includes(search.toLowerCase())
  );

  const statutBadge = (statut: string) => (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border flex items-center gap-1 w-fit ${statut === 'SERVICE_FAIT'
        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
        : statut === 'EN_COURS'
          ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
          : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
      }`}>
      {statut === 'SERVICE_FAIT' && <CheckCircle2 className="w-3 h-3" />}
      {statut === 'DEMANDE' ? t('Demandé', 'Requested') : statut === 'EN_COURS' ? t('En cours', 'In progress') : t('Effectué', 'Done')}
    </span>
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Opérations Portuaires', 'Port Operations')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Consignation Navire & Services Portuaires', 'Ship Consignment & Port Services')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-purple-500/10 text-purple-400 rounded-xl border border-purple-500/20">
            <Ship className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex flex-wrap items-center gap-2">
              {t('Consignation Navire & Services Armateurs', 'Ship Consignment & Shipowner Services')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/30 font-mono">
                KACC_CNS
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Assistance aux escales, pilotage, remorquage, avitaillement, soutage et relèves d\'équipage maritimes', 'Port call assistance, pilotage, towage, bunkering and maritime crew changes')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium text-sm shadow-lg shadow-purple-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Commander un Service Navire', 'Order a Ship Service')}
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
              placeholder={t('Rechercher par navire, service, prestataire...', 'Search by vessel, service, provider...')}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-16 flex items-center justify-center gap-2 text-slate-400">
            <Loader2 className="w-5 h-5 animate-spin" />
            {t('Chargement des services...', 'Loading services...')}
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Ship className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">{t('Aucun service de consignation enregistré', 'No consignment service recorded')}</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {t('Votre agence maritime n\'a pas encore ouvert de demande de prestation pour un navire en escale.', 'Your maritime agency has not opened a service request for a vessel in port yet.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              {t('Commander un premier service', 'Order a first service')}
            </button>
          </div>
        ) : (
          <>
            {/* Mobile cards */}
            <div className="space-y-3 lg:hidden">
              {filtered.map(svc => (
                <div key={svc.id} className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="font-semibold text-white text-sm flex items-center gap-1.5">
                        <Anchor className="w-3.5 h-3.5 text-purple-400" /> {svc.navire_nom}
                      </div>
                      <div className="text-xs text-slate-300">{svc.type_service}</div>
                    </div>
                    {statutBadge(svc.statut)}
                  </div>
                  <div className="text-xs text-slate-400">{svc.prestataire || ''}</div>
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs font-mono text-slate-400">
                    {svc.date_demande && <span>{svc.date_demande}</span>}
                    {svc.montant_estime_xaf > 0 && <span className="text-white">{svc.montant_estime_xaf.toLocaleString()} FCFA</span>}
                  </div>
                  {svc.statut !== 'SERVICE_FAIT' && (
                    <button
                      onClick={() => marquerServi(svc)}
                      className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-medium transition"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" /> {t('Marquer effectué', 'Mark as done')}
                    </button>
                  )}
                </div>
              ))}
            </div>
            {/* Desktop table */}
            <div className="hidden lg:block overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                  <tr>
                    <th className="py-3 px-4 rounded-l-xl">{t('Navire', 'Vessel')}</th>
                    <th className="py-3 px-4">{t('Service', 'Service')}</th>
                    <th className="py-3 px-4">{t('Prestataire', 'Provider')}</th>
                    <th className="py-3 px-4">{t('Date Demande', 'Request Date')}</th>
                    <th className="py-3 px-4">{t('Montant Estimé', 'Estimated Amount')}</th>
                    <th className="py-3 px-4">{t('Statut', 'Status')}</th>
                    <th className="py-3 px-4 rounded-r-xl text-right">{t('Actions', 'Actions')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filtered.map(svc => (
                    <tr key={svc.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-semibold text-white">
                        <div className="flex items-center gap-1.5">
                          <Anchor className="w-3.5 h-3.5 text-purple-400" /> {svc.navire_nom}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-200">{svc.type_service}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-400">{svc.prestataire || ''}</td>
                      <td className="py-3.5 px-4 text-xs font-mono text-slate-400">{svc.date_demande || ''}</td>
                      <td className="py-3.5 px-4 font-mono text-white text-xs">
                        {svc.montant_estime_xaf > 0 ? `${svc.montant_estime_xaf.toLocaleString()} FCFA` : ''}
                      </td>
                      <td className="py-3.5 px-4">{statutBadge(svc.statut)}</td>
                      <td className="py-3.5 px-4 text-right">
                        {svc.statut !== 'SERVICE_FAIT' && (
                          <button
                            onClick={() => marquerServi(svc)}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-medium transition"
                          >
                            <CheckCircle2 className="w-3 h-3" /> {t('Marquer effectué', 'Mark as done')}
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

      {/* Modal Commande Service */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Ship className="w-5 h-5 text-purple-400" />
              {t('Commander un Service Navire', 'Order a Ship Service')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Enregistrement dans le registre de consignation de l\'agence', 'Recording in the agency consignment register')}
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Nom du Navire *', 'Vessel Name *')}</label>
                <input
                  type="text"
                  required
                  value={formData.navire_nom}
                  onChange={e => setFormData({ ...formData, navire_nom: e.target.value })}
                  placeholder={t('Ex: MT ATLANTIC HARMONY', 'e.g. MT ATLANTIC HARMONY')}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Type de Service', 'Service Type')}</label>
                  <select
                    value={formData.type_service}
                    onChange={e => setFormData({ ...formData, type_service: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                  >
                    <option>{t('Pilotage & Remorquage', 'Pilotage & Towage')}</option>
                    <option>{t('Arrimage / Désarrimage', 'Lashing / Unlashing')}</option>
                    <option>{t('Soutage & Avitaillement', 'Bunkering & Supply')}</option>
                    <option>{t('Relève d\'équipage', 'Crew Change')}</option>
                    <option>{t('Nettoyage & Inspection de cale', 'Hold Cleaning & Inspection')}</option>
                    <option>{t('Évacuation déchets navire', 'Ship Waste Disposal')}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Prestataire', 'Provider')}</label>
                  <input
                    type="text"
                    value={formData.prestataire}
                    onChange={e => setFormData({ ...formData, prestataire: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Date de Demande', 'Request Date')}</label>
                  <input
                    type="date"
                    value={formData.date_demande}
                    onChange={e => setFormData({ ...formData, date_demande: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Montant Estimé (FCFA)', 'Estimated Amount (FCFA)')}</label>
                  <input
                    type="number"
                    min={0}
                    value={formData.montant_estime_xaf || ''}
                    onChange={e => setFormData({ ...formData, montant_estime_xaf: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Commentaires', 'Comments')}</label>
                <textarea
                  rows={2}
                  value={formData.commentaires}
                  onChange={e => setFormData({ ...formData, commentaires: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                />
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
                  disabled={saving}
                  className="px-5 py-2 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-sm font-medium rounded-xl shadow-lg transition flex items-center gap-2"
                >
                  {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                  {t('Enregistrer la Commande', 'Save the Order')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
