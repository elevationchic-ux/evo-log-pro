'use client';

import React, { useState, useEffect } from 'react';
import {
  Truck,
  Plus,
  Search,
  Download,
  RefreshCw,
  ChevronRight,
  Wrench,
  Loader2
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { fleetAPI } from '@/lib/api-client';
import { exportToCSV } from '@/lib/export';
import { toast } from 'sonner';
import { useSettings } from '@/components/layout/SettingsProvider';

interface VehicleComplete {
  id: string;
  immatriculation: string;
  type: string;
  marque: string;
  modele: string;
  annee: number;
  carburant: string;
  kilometrage: number;
  statut: string;
  siteAffectation: string;
}

const TYPES = [
  'TRACTEUR', 'SEMI_REMORQUE', 'REACHSTACKER', 'ELEVATEUR', 'FOURGON', 'CAMION', 'BERLINE', 'PICKUP', 'VAN',
];

const STATUT_LABELS: Record<string, [string, string]> = {
  DISPONIBLE: ['Disponible (En parc)', 'Available (In yard)'],
  EN_MISSION: ['En mission (En route)', 'On mission (En route)'],
  EN_MAINTENANCE: ['En atelier GMAO', 'In maintenance shop'],
  HORS_SERVICE: ['Immobilisé', 'Out of service'],
  RESERVE: ['Réservé', 'Reserved'],
};

const normalizeStatut = (raw?: string | null): string => {
  const s = (raw || 'disponible').toUpperCase();
  if (s === 'EN_USAGE') return 'EN_MISSION';
  return s;
};

export default function ParcFleetCompletePage() {
  const { language } = useSettings();
  const lang = language || 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const router = useRouter();

  const [vehicles, setVehicles] = useState<VehicleComplete[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedVehicle, setSelectedVehicle] = useState<VehicleComplete | null>(null);

  const [formVehicle, setFormVehicle] = useState({
    immatriculation: '',
    type: 'TRACTEUR',
    marque: '',
    modele: '',
    annee: new Date().getFullYear(),
    carburant: 'diesel',
    kilometrage: 0,
    siteAffectation: 'Douala Port',
  });

  const loadVehicles = async () => {
    setLoading(true);
    try {
      const res = await fleetAPI.getVehicles({ limit: 200 });
      const raw = res.data?.items || res.data || [];
      if (Array.isArray(raw)) {
        setVehicles(raw.map((v: any) => ({
          id: v.id?.toString() || '',
          immatriculation: v.immatriculation || '',
          type: (v.type_vehicule || 'TRACTEUR').toUpperCase(),
          marque: v.marque || '',
          modele: v.modele || '',
          annee: Number(v.annee) || 0,
          carburant: v.carburant || '',
          kilometrage: Number(v.kilometrage) || 0,
          statut: normalizeStatut(v.status),
          siteAffectation: v.localisation || '',
        })));
      } else {
        setVehicles([]);
      }
    } catch {
      setVehicles([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVehicles();
  }, []);

  const handleCreateVehicle = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formVehicle.immatriculation || !formVehicle.marque) {
      toast.error(t('Veuillez renseigner l\'immatriculation et la marque.', 'Please provide the registration number and brand.'));
      return;
    }
    setSaving(true);
    try {
      await fleetAPI.createVehicle({
        immatriculation: formVehicle.immatriculation.toUpperCase(),
        marque: formVehicle.marque,
        modele: formVehicle.modele || undefined,
        annee: formVehicle.annee || undefined,
        type_vehicule: formVehicle.type,
        carburant: formVehicle.carburant || undefined,
        kilometrage: formVehicle.kilometrage || 0,
        localisation: formVehicle.siteAffectation || undefined,
      });
      toast.success(t('Véhicule enregistré au parc', 'Vehicle registered in the fleet'));
      setShowAddModal(false);
      setFormVehicle({
        immatriculation: '', type: 'TRACTEUR', marque: '', modele: '',
        annee: new Date().getFullYear(), carburant: 'diesel', kilometrage: 0,
        siteAffectation: 'Douala Port',
      });
      loadVehicles();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : t('Erreur réseau  enregistrement impossible', 'Network error  could not save'));
    } finally {
      setSaving(false);
    }
  };

  const filteredVehicles = vehicles.filter(v => {
    const matchesSearch =
      v.immatriculation.toLowerCase().includes(searchTerm.toLowerCase()) ||
      v.marque.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'ALL' || v.type === filterType;
    const matchesStatus = filterStatus === 'ALL' || v.statut === filterStatus;
    return matchesSearch && matchesType && matchesStatus;
  });

  const handleExport = () => {
    if (filteredVehicles.length === 0) {
      toast.error(t('Aucun véhicule à exporter', 'No vehicle to export'));
      return;
    }
    exportToCSV(
      filteredVehicles.map(v => ({
        'Immatriculation': v.immatriculation,
        'Type': v.type,
        'Marque': v.marque,
        'Modèle': v.modele,
        'Année': v.annee || '',
        'Carburant': v.carburant,
        'Kilométrage': v.kilometrage,
        'Statut': v.statut,
        'Base': v.siteAffectation,
      })),
      'parc_vehicules'
    );
    toast.success(t('Export CSV généré', 'CSV export generated'));
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Truck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-on-surface">
              {t('Répertoire 360° du Parc Véhicules & Engins', '360° Vehicle & Equipment Fleet Directory')}
            </h1>
            <p className="text-sm text-on-surface-variant">
              {t('Fiches techniques complètes • Tracteurs, semi-remorques, reachstackers et engins de quai', 'Complete technical sheets • Tractors, semi-trailers, reachstackers and wharf equipment')}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl bg-surface border border-outline hover:bg-surface-container text-on-surface transition-colors"
          >
            <Download className="w-4 h-4" />
            {t('Exporter Flotte', 'Export Fleet')}
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-95 transition-opacity"
          >
            <Plus className="w-4 h-4" />
            {t('Nouveau Véhicule / Engin', 'New Vehicle / Equipment')}
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-surface border border-outline rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            type="text"
            placeholder={t('Rechercher par immatriculation, marque...', 'Search by registration, brand...')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-surface-container-low border border-outline text-xs rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-surface-container-low border border-outline text-xs rounded-xl px-3 py-2 text-on-surface focus:outline-none focus:border-primary"
          >
            <option value="ALL">{t('Tous les types d\'engins', 'All equipment types')}</option>
            {TYPES.map(tt => (
              <option key={tt} value={tt}>{tt.replace(/_/g, ' ')}</option>
            ))}
          </select>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-surface-container-low border border-outline text-xs rounded-xl px-3 py-2 text-on-surface focus:outline-none focus:border-primary"
          >
            <option value="ALL">{t('Tous les statuts', 'All statuses')}</option>
            {Object.entries(STATUT_LABELS).map(([code, [fr, en]]) => (
              <option key={code} value={code}>{lang === 'en' ? en : fr}</option>
            ))}
          </select>

          <button
            onClick={loadVehicles}
            className="p-2 border border-outline rounded-xl hover:bg-surface-container text-on-surface-variant hover:text-on-surface"
            title={t('Actualiser', 'Refresh')}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Grid or Clean Slate State */}
      {loading ? (
        <div className="py-16 flex items-center justify-center gap-2 text-on-surface-variant">
          <Loader2 className="w-5 h-5 animate-spin" />
          {t('Chargement du parc...', 'Loading fleet...')}
        </div>
      ) : filteredVehicles.length === 0 ? (
        <div className="bg-surface border border-outline rounded-2xl p-12 text-center shadow-sm">
          <Truck className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
          <h3 className="font-semibold text-on-surface text-base">{t('Aucun véhicule ou engin dans le parc', 'No vehicle or equipment in the fleet')}</h3>
          <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto mb-4">
            {t('Commencez par enregistrer les tracteurs routiers, remorques ou chariots élévateurs de votre entreprise pour activer le suivi GMAO et le dispatching des missions.', 'Start by registering your company\'s road tractors, trailers or forklifts to enable maintenance tracking and mission dispatching.')}
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold text-xs hover:opacity-95"
          >
            {t('+ Enregistrer le Premier Véhicule', '+ Register the First Vehicle')}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredVehicles.map(v => (
            <div
              key={v.id}
              onClick={() => setSelectedVehicle(v)}
              className="bg-surface border border-outline rounded-2xl p-5 hover:border-primary transition-all cursor-pointer shadow-sm hover:shadow-md space-y-3"
            >
              <div className="flex justify-between items-start">
                <h3 className="font-bold text-lg font-mono text-primary">{v.immatriculation}</h3>
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${v.statut === 'DISPONIBLE' ? 'bg-emerald-500/10 text-emerald-600' :
                    v.statut === 'EN_MISSION' ? 'bg-blue-500/10 text-blue-600' :
                      v.statut === 'EN_MAINTENANCE' ? 'bg-amber-500/10 text-amber-600' :
                        v.statut === 'RESERVE' ? 'bg-slate-500/10 text-slate-500' :
                          'bg-red-500/10 text-red-600'
                  }`}>
                  {v.statut}
                </span>
              </div>

              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-on-surface-variant">{t('Modèle :', 'Model:')}</span>
                  <span className="font-medium text-on-surface">{v.marque} {v.modele} {v.annee ? `(${v.annee})` : ''}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-on-surface-variant">{t('Type d\'engin :', 'Equipment type:')}</span>
                  <span className="font-semibold text-on-surface">{v.type.replace(/_/g, ' ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-on-surface-variant">{t('Kilométrage :', 'Mileage:')}</span>
                  <span className="text-on-surface font-mono">{v.kilometrage.toLocaleString()} km</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-on-surface-variant">{t('Base / Affectation :', 'Base / Assignment:')}</span>
                  <span className="text-on-surface">{v.siteAffectation || ''}</span>
                </div>
              </div>

              <div className="pt-2 border-t border-outline/50 flex justify-between items-center text-[11px] text-on-surface-variant">
                <span>{t('Carburant', 'Fuel')}: <strong className="text-on-surface">{v.carburant || ''}</strong></span>
                <span className="text-primary font-bold flex items-center gap-0.5">
                  {t('Fiche 360°', '360° Sheet')} <ChevronRight className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Vehicle Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center border-b border-outline pb-3">
              <h3 className="font-bold text-on-surface text-base">{t('Enregistrer un Nouveau Véhicule / Engin', 'Register a New Vehicle / Equipment')}</h3>
              <button onClick={() => setShowAddModal(false)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <form onSubmit={handleCreateVehicle} className="space-y-3 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">{t('Immatriculation * :', 'Registration * :')}</label>
                  <input
                    type="text"
                    placeholder={t('Ex: LT-TR-8945', 'e.g. LT-TR-8945')}
                    value={formVehicle.immatriculation}
                    onChange={(e) => setFormVehicle({ ...formVehicle, immatriculation: e.target.value })}
                    required
                    minLength={5}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono uppercase focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">{t('Type d\'engin :', 'Equipment type:')}</label>
                  <select
                    value={formVehicle.type}
                    onChange={(e) => setFormVehicle({ ...formVehicle, type: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  >
                    {TYPES.map(tt => (
                      <option key={tt} value={tt}>{tt.replace(/_/g, ' ')}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">{t('Marque * :', 'Brand * :')}</label>
                  <input
                    type="text"
                    placeholder={t('Ex: Mercedes-Benz, Sinotruk, Kalmar', 'e.g. Mercedes-Benz, Sinotruk, Kalmar')}
                    value={formVehicle.marque}
                    onChange={(e) => setFormVehicle({ ...formVehicle, marque: e.target.value })}
                    required
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">{t('Modèle :', 'Model:')}</label>
                  <input
                    type="text"
                    placeholder={t('Ex: Actros 3340 / Gloria', 'e.g. Actros 3340 / Gloria')}
                    value={formVehicle.modele}
                    onChange={(e) => setFormVehicle({ ...formVehicle, modele: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">{t('Année de mise en circulation :', 'Year of circulation:')}</label>
                  <input
                    type="number"
                    min={1980}
                    max={new Date().getFullYear() + 1}
                    value={formVehicle.annee}
                    onChange={(e) => setFormVehicle({ ...formVehicle, annee: Number(e.target.value) })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">{t('Carburant :', 'Fuel:')}</label>
                  <select
                    value={formVehicle.carburant}
                    onChange={(e) => setFormVehicle({ ...formVehicle, carburant: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  >
                    <option value="diesel">Diesel</option>
                    <option value="essence">Essence</option>
                    <option value="gpl">GPL</option>
                    <option value="electrique">Électrique</option>
                    <option value="hybride">Hybride</option>
                  </select>
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">{t('Kilométrage initial :', 'Initial mileage:')}</label>
                  <input
                    type="number"
                    min={0}
                    value={formVehicle.kilometrage || ''}
                    onChange={(e) => setFormVehicle({ ...formVehicle, kilometrage: parseInt(e.target.value) || 0 })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-on-surface-variant font-medium mb-1">{t('Site d\'affectation :', 'Assignment site:')}</label>
                <select
                  value={formVehicle.siteAffectation}
                  onChange={(e) => setFormVehicle({ ...formVehicle, siteAffectation: e.target.value })}
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                >
                  <option value="Douala Port">{t('Douala Port (Base DIT)', 'Douala Port (DIT Base)')}</option>
                  <option value="Kribi Port">{t('Kribi Port (Base KMT)', 'Kribi Port (KMT Base)')}</option>
                  <option value="limbé">{t('Limbé Hub', 'Limbé Hub')}</option>
                  <option value="Yaoundé">{t('Yaoundé Gare MAD', 'Yaoundé MAD Terminal')}</option>
                </select>
              </div>

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-outline rounded-xl text-on-surface hover:bg-surface-container font-semibold"
                >
                  {t('Annuler', 'Cancel')}
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold hover:opacity-90 disabled:opacity-50 flex items-center gap-2"
                >
                  {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                  {t('Ajouter au Parc', 'Add to Fleet')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Selected Vehicle 360 Sheet Modal */}
      {selectedVehicle && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center border-b border-outline pb-3">
              <div>
                <h3 className="font-bold text-lg text-on-surface font-mono">{selectedVehicle.immatriculation}</h3>
                <span className="text-xs text-on-surface-variant">{selectedVehicle.type.replace(/_/g, ' ')}</span>
              </div>
              <button onClick={() => setSelectedVehicle(null)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-outline/40">
                <span className="text-on-surface-variant">{t('Marque & Modèle :', 'Brand & Model:')}</span>
                <span className="font-semibold text-on-surface">{selectedVehicle.marque} {selectedVehicle.modele} {selectedVehicle.annee ? `(${selectedVehicle.annee})` : ''}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-outline/40">
                <span className="text-on-surface-variant">{t('Carburant :', 'Fuel:')}</span>
                <span className="text-on-surface">{selectedVehicle.carburant || ''}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-outline/40">
                <span className="text-on-surface-variant">{t('Kilométrage :', 'Mileage:')}</span>
                <span className="font-mono text-on-surface">{selectedVehicle.kilometrage.toLocaleString()} km</span>
              </div>
              <div className="flex justify-between py-1 border-b border-outline/40">
                <span className="text-on-surface-variant">{t('Base Opérationnelle :', 'Operational Base:')}</span>
                <span className="text-on-surface">{selectedVehicle.siteAffectation || ''}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-outline/40">
                <span className="text-on-surface-variant">{t('Statut :', 'Status:')}</span>
                <span className="font-bold text-on-surface">{selectedVehicle.statut}</span>
              </div>
            </div>

            <div className="pt-3 flex justify-between items-center">
              <button
                onClick={() => router.push(`/parc-vehicules/preventive-maintenance?vehicule=${selectedVehicle.id}`)}
                className="px-3.5 py-2 border border-outline rounded-xl text-on-surface text-xs font-semibold hover:bg-surface-container flex items-center gap-1.5"
              >
                <Wrench className="w-3.5 h-3.5" />
                {t('Fiche Atelier', 'Workshop Sheet')}
              </button>
              <button
                onClick={() => setSelectedVehicle(null)}
                className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold text-xs"
              >
                {t('Fermer', 'Close')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
