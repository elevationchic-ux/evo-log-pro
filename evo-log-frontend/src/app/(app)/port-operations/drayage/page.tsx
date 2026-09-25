'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  Truck, Plus, Search, ArrowLeft, RefreshCw, ArrowRight
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { toast } from 'sonner';

interface TransfertDrayage {
  id: number;
  conteneur_id: number;
  numero_navette: string;
  numero_conteneur: string;
  provenance_quai: string;
  destination_mad: string;
  tracteur_parc: string;
  chauffeur_navette: string;
  heure_chargement: string | null;
  statut: string;
}

const TYPES_CONTENEUR = [
  'dry_20', 'dry_40', 'dry_40_hc', 'reefer_20', 'reefer_40',
  'open_top_20', 'open_top_40', 'flat_rack_20', 'flat_rack_40', 'tank_20', 'platform',
];

export default function PortOperationsDrayagePage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [transferts, setTransferts] = useState<TransfertDrayage[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [confirmingId, setConfirmingId] = useState<number | null>(null);

  const [formData, setFormData] = useState({
    numero_conteneur: '',
    type_conteneur: 'dry_20',
    provenance_quai: 'Poste 14 (Terre-plein Sous-douane)',
    destination_mad: 'Entrepôt MAD Bonabéri (Douala)',
    tracteur_parc: 'Tracteur Kalmar TT-04',
    chauffeur_navette: '',
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/container-lifecycle/', { params: { limit: 100 } });
      const conteneurs: any[] = Array.isArray(res?.data?.data) ? res.data.data : [];
      const details = await Promise.all(
        conteneurs.map(c =>
          apiClient.get(`/api/v1/container-lifecycle/${c.id}`).then(r => r?.data ?? null).catch(() => null)
        )
      );
      const rows: TransfertDrayage[] = [];
      details.forEach((d: any) => {
        if (!d) return;
        (Array.isArray(d.cycles) ? d.cycles : []).forEach((cy: any) => {
          // Un transfert drayage = un cycle documenté avec une localisation (mouvement quai ↔ MAD)
          if (!cy.localisation) return;
          rows.push({
            id: cy.id,
            conteneur_id: d.id,
            numero_navette: cy.voyage || '',
            numero_conteneur: d.numero,
            provenance_quai: cy.localisation,
            destination_mad: cy.localisation,
            tracteur_parc: cy.operateur_manutention || '',
            chauffeur_navette: cy.operateur_dechargement || '',
            heure_chargement: cy.date_arrivee || cy.date_sortie || null,
            statut: cy.statut === 'stocke' || cy.statut === 'sorti' ? 'LIVRE_MAD' : (cy.statut || 'EN_TRANSIT'),
          });
        });
      });
      rows.sort((a, b) => (b.heure_chargement || '').localeCompare(a.heure_chargement || ''));
      setTransferts(rows.slice(0, 150));
    } catch {
      toast.error(t('Les transferts n\'ont pas pu être chargés. Vérifiez votre connexion.', 'Transfers could not be loaded. Check your connection.'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => { load(); }, [load]);

  const resolveConteneurId = async (numero: string, type: string): Promise<number> => {
    const q = await apiClient.get('/api/v1/container-lifecycle/', { params: { search: numero, limit: 20 } });
    const found = (Array.isArray(q?.data?.data) ? q.data.data : []).find((c: any) => c.numero === numero);
    if (found) return found.id;
    const taille = type.includes('40') ? 40 : 20;
    const created = await apiClient.post('/api/v1/container-lifecycle/', {
      numero, type_conteneur: type, taille_pieds: taille, etat: 'clean',
    });
    if (!created?.data?.id) throw new Error(t('Fiche conteneur créée côté entrepôt.', 'Container record created in yard.'));
    return created.data.id;
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const numero = formData.numero_conteneur.trim().toUpperCase();
    if (!numero) {
      toast.error(t('Numéro de conteneur requis.', 'Container number required.'));
      return;
    }
    setSaving(true);
    try {
      const conteneurId = await resolveConteneurId(numero, formData.type_conteneur);
      const navette = `NAV-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${String(Math.floor(Math.random() * 900) + 100)}`;
      await apiClient.post(`/api/v1/container-lifecycle/${conteneurId}/cycle`, {
        voyage: navette,
        statut: 'quai',
        localisation: formData.provenance_quai,
        operateur_dechargement: formData.chauffeur_navette || undefined,
        operateur_manutention: formData.tracteur_parc || undefined,
      });
      toast.success(t('Bon de navette enregistré.', 'Shuttle order recorded.'));
      setIsModalOpen(false);
      setFormData(f => ({ ...f, numero_conteneur: '', chauffeur_navette: '' }));
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t('Échec de l\'enregistrement du transfert.', 'Failed to save transfer.'));
    } finally {
      setSaving(false);
    }
  };

  const confirmerMAD = async (tr: TransfertDrayage) => {
    setConfirmingId(tr.id);
    try {
      await apiClient.post(`/api/v1/container-lifecycle/${tr.conteneur_id}/cycle`, {
        voyage: tr.numero_navette !== '' ? tr.numero_navette : undefined,
        statut: 'stocke',
        localisation: tr.destination_mad,
        operateur_dechargement: tr.chauffeur_navette !== '' ? tr.chauffeur_navette : undefined,
        operateur_manutention: tr.tracteur_parc !== '' ? tr.tracteur_parc : undefined,
      });
      toast.success(t('Réception au MAD enregistrée.', 'Delivery at MAD recorded.'));
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t('Échec de la confirmation MAD.', 'MAD confirmation failed.'));
    } finally {
      setConfirmingId(null);
    }
  };

  const filtered = transferts.filter(t2 =>
    t2.numero_conteneur.toLowerCase().includes(search.toLowerCase()) ||
    t2.numero_navette.toLowerCase().includes(search.toLowerCase()) ||
    t2.destination_mad.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Opérations Portuaires', 'Port Operations')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Drayage & Transferts Terres-Pleins / MAD', 'Drayage & Yard / ECD Warehouse Transfers')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20">
            <Truck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2 flex-wrap">
              {t('Drayage & Transferts Portuaires MAD', 'Drayage & Port ECD-Warehouse Transfers')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 font-mono">
                KACC_DRY
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Évacuation des conteneurs du quai vers les magasins avancés sous-douane (MAD) et zones logistiques', 'Evacuation of containers from the quay to bonded forward warehouses (MAD) and logistics zones')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={load} className="flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-700 text-slate-300 text-sm hover:bg-slate-800">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> {t('Actualiser', 'Refresh')}
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-medium text-sm shadow-lg shadow-amber-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Lancer un Transfert Navette', 'Launch a Shuttle Transfer')}
          </button>
        </div>
      </div>

      {/* Main Table card */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder={t('Rechercher conteneur, navette, destination MAD...', 'Search container, shuttle, MAD destination...')}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-amber-500 font-mono"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400 text-sm">{t('Chargement des transferts…', 'Loading transfers…')}</div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Truck className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">{t('Aucun transfert de drayage en cours', 'No active drayage transfer')}</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {t('Tous les conteneurs déchargés sont actuellement sur terre-plein ou déjà réceptionnés en magasin. Démarrez un transfert navette.', 'All discharged containers are currently on the yard or already received in warehouse. Start a shuttle transfer.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              {t('Lancer une première navette drayage', 'Launch the first drayage shuttle')}
            </button>
          </div>
        ) : (
          <>
            {/* Mobile card list */}
            <div className="space-y-3 lg:hidden">
              {filtered.map(tr => (
                <div key={tr.id} className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-sm font-bold text-white">{tr.numero_conteneur}</span>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${tr.statut === 'LIVRE_MAD'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                      {tr.statut === 'LIVRE_MAD' ? t('Livré MAD', 'Delivered MAD') : tr.statut}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400">
                    <span>{tr.numero_navette}</span> · <ArrowRight className="w-3 h-3 inline" /> {tr.destination_mad}
                  </div>
                  <div className="text-xs text-slate-400">{tr.tracteur_parc}  {tr.chauffeur_navette}</div>
                  {tr.statut !== 'LIVRE_MAD' && (
                    <button
                      onClick={() => confirmerMAD(tr)}
                      disabled={confirmingId === tr.id}
                      className="w-full px-2.5 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 disabled:opacity-60 text-emerald-400 text-xs font-medium rounded-lg border border-emerald-500/30 transition"
                    >
                      {confirmingId === tr.id ? t('Enregistrement…', 'Saving…') : t('Confirmer MAD', 'Confirm MAD Delivery')}
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
                    <th className="py-3 px-4 rounded-l-xl">{t('N° Navette', 'Shuttle No.')}</th>
                    <th className="py-3 px-4">{t('N° Conteneur', 'Container No.')}</th>
                    <th className="py-3 px-4">{t('Localisation', 'Location')}</th>
                    <th className="py-3 px-4">{t('Engin & Chauffeur', 'Equipment & Driver')}</th>
                    <th className="py-3 px-4">{t('Départ', 'Departure')}</th>
                    <th className="py-3 px-4">{t('Statut', 'Status')}</th>
                    <th className="py-3 px-4 rounded-r-xl text-right">{t('Action', 'Action')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filtered.map(tr => (
                    <tr key={tr.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-mono font-medium text-amber-400">{tr.numero_navette}</td>
                      <td className="py-3.5 px-4 font-mono text-white font-bold">{tr.numero_conteneur}</td>
                      <td className="py-3.5 px-4 text-xs">
                        <span className="text-white font-medium">{tr.destination_mad}</span>
                      </td>
                      <td className="py-3.5 px-4 text-xs">
                        <span className="text-slate-300 block">{tr.tracteur_parc}</span>
                        <span className="text-slate-400">{tr.chauffeur_navette}</span>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-xs text-slate-400">
                        {tr.heure_chargement ? new Date(tr.heure_chargement).toLocaleString(lang === 'en' ? 'en-GB' : 'fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : ''}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${tr.statut === 'LIVRE_MAD'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          }`}>
                          {tr.statut === 'LIVRE_MAD' ? t('Livré MAD', 'Delivered MAD') : tr.statut}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        {tr.statut !== 'LIVRE_MAD' && (
                          <button
                            onClick={() => confirmerMAD(tr)}
                            disabled={confirmingId === tr.id}
                            className="px-2.5 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 disabled:opacity-60 text-emerald-400 text-xs rounded border border-emerald-500/30 transition"
                          >
                            {confirmingId === tr.id ? t('Enregistrement…', 'Saving…') : t('Confirmer MAD', 'Confirm MAD')}
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

      {/* Modal Lancement Drayage */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Truck className="w-5 h-5 text-amber-400" />
              {t('Lancer un Transfert Drayage', 'Launch a Drayage Transfer')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Ordre de transfert d\'un conteneur vers un magasin avancé sous-douane (MAD)', 'Transfer order for a container to a bonded forward warehouse (MAD)')}
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('N° Conteneur (ISO 6346) *', 'Container No. (ISO 6346) *')}</label>
                  <input
                    type="text"
                    required
                    value={formData.numero_conteneur}
                    onChange={e => setFormData({ ...formData, numero_conteneur: e.target.value })}
                    placeholder="TGHU 850124-7"
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500 font-mono uppercase"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Type de Conteneur', 'Container Type')}</label>
                  <select
                    value={formData.type_conteneur}
                    onChange={e => setFormData({ ...formData, type_conteneur: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  >
                    {TYPES_CONTENEUR.map(tt => <option key={tt} value={tt}>{tt}</option>)}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Provenance Quai', 'Quay Origin')}</label>
                  <input
                    type="text"
                    value={formData.provenance_quai}
                    onChange={e => setFormData({ ...formData, provenance_quai: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Destination MAD', 'MAD Destination')}</label>
                  <select
                    value={formData.destination_mad}
                    onChange={e => setFormData({ ...formData, destination_mad: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  >
                    <option value="Entrepôt MAD Bonabéri (Douala)">Entrepôt MAD Bonabéri (Douala)</option>
                    <option value="Terre-plein Extérieur Bassa (Douala)">Terre-plein Extérieur Bassa</option>
                    <option value="Magasin Sous-Douane Mboro (Kribi)">Magasin Sous-Douane Mboro (Kribi)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Tracteur de Parc', 'Yard Tractor')}</label>
                  <input
                    type="text"
                    value={formData.tracteur_parc}
                    onChange={e => setFormData({ ...formData, tracteur_parc: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Chauffeur Navette', 'Shuttle Driver')}</label>
                  <input
                    type="text"
                    value={formData.chauffeur_navette}
                    onChange={e => setFormData({ ...formData, chauffeur_navette: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
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
                  disabled={saving}
                  className="px-5 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-60 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  {saving ? t('Enregistrement…', 'Saving…') : t('Valider le Bon de Navette', 'Confirm Shuttle Order')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
