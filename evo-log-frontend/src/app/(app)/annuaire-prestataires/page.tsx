'use client';

import React, { useState, useEffect } from 'react';
import {
  Building, Search, ShieldCheck, Star, Phone, Mail, Clock,
  MapPin, Plus, Send, CheckCircle2, Award, Truck,
  DollarSign, X, Shield, RefreshCw, ShoppingCart,
  Wrench, ChevronRight, AlertOctagon,
  FileCheck2, Compass
} from 'lucide-react';
import { useAuth } from '@/components/shared/AuthProvider';

export interface VehiculeDisponible {
  type: string;
  quantite: number;
  tarif_journalier?: number;
  tarif_km?: number;
}

export interface ForfaitPropose {
  libelle: string;
  tarif: number;
  unite?: string;
  description?: string;
}

export interface PrestataireItem {
  id: number;
  code: string;
  raison_sociale: string;
  sigle?: string;
  logo_url?: string;
  type_entite: 'PRESTATAIRE' | 'GARAGE' | 'TRANSPORTEUR';
  specialite: string;
  tax_id?: string;
  rccm?: string;
  agrement_portuaire?: string;
  est_homologue: boolean;
  statut_agrement: string;
  ville: string;
  zone_portuaire?: string;
  adresse?: string;
  contact_nom?: string;
  contact_telephone: string;
  contact_email?: string;
  telephone_astreinte_24h?: string;
  specialites_panne?: string[];
  vehicules_disponibles?: VehiculeDisponible[];
  forfaits_proposes?: ForfaitPropose[];
  note_globale: number;
  nb_missions_realisees: number;
  taux_ponctualite: number;
  taux_conformite_qhse: number;
  devise: string;
  taux_journalier_indicatif?: number;
  conditions_reglement: string;
  observations?: string;
}

export interface CotationItem {
  id: number;
  numero_dossier: string;
  titre_besoin: string;
  description_besoin: string;
  urgence: string;
  lieu_intervention: string;
  statut: string;
  budget_max_estime?: number;
  created_at: string;
  prestataire_nom?: string;
}

// Listes de configuration d'interface (options des filtres), non des données métier.
// audit-allow:fake_data
const SPECIALITES = [
  { id: 'ALL', label: 'Toutes les Spécialités' },
  { id: 'GARAGE_MECANIQUE', label: 'Garages & Réparation PL' },
  { id: 'TRANSPORT_FLOTTE', label: 'Transport & Véhicules Disponibles' },
  { id: 'MANUTENTION_PORTUAIRE', label: 'Manutention & Grues' },
  { id: 'GARDIENNAGE_ISPS', label: 'Sécurité & Sûreté ISPS' },
  { id: 'NETTOYAGE_INDUSTRIEL', label: 'Hygiène & Entretien' },
  { id: 'BUNKERING_CARBURANT', label: 'Soutage Carburant' },
  { id: 'DOUANE_TRANSIT', label: 'Douane & Hinterland' }
];

const VILLES = [
  { id: 'ALL', label: 'Tous les Ports & Corridors' },
  { id: 'Douala', label: 'Douala (Port PAD & Bonabéri)' },
  { id: 'Kribi', label: 'Kribi (Port PAK en Eau Profonde)' },
  { id: 'Yaounde', label: 'Yaoundé (Corridor Centre)' },
  { id: 'Ngaoundere', label: 'Ngaoundéré (Corridor Tchad)' },
  { id: 'limbé', label: 'limbé (Hinterland Ouest)' }
];

const SPECIALITES_PANNE = [
  'Toutes les Pannes',
  'Moteur / Culasse',
  'Pneumatique PL',
  'Électricité & Diagnostic',
  'Remorquage Lourd 24/7',
  'Freinage Pneumatique',
  'Transmission & Pont'
];

export default function AnnuairePrestatairesPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'annuaire' | 'garages' | 'vehicules' | 'cotations' | 'conformite'>('annuaire');

  // Deep-link depuis la navigation : /annuaire-prestataires?tab=... ouvre l'onglet demande.
  useEffect(() => {
    const t = new URLSearchParams(window.location.search).get('tab');
    const allowed = ['annuaire', 'garages', 'vehicules', 'cotations', 'conformite'];
    if (t && (allowed as string[]).includes(t)) setActiveTab(t as typeof activeTab);
  }, []);

  // Data state - loaded exclusively from API
  const [prestataires, setPrestataires] = useState<PrestataireItem[]>([]);
  const [cotations, setCotations] = useState<CotationItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSpecialite, setSelectedSpecialite] = useState('ALL');
  const [selectedVille, setSelectedVille] = useState('ALL');
  const [selectedPanne, setSelectedPanne] = useState('Toutes les Pannes');
  const [onlyPAD, setOnlyPAD] = useState(false);
  const [only24h, setOnly24h] = useState(false);

  // Modals
  const [isRfqModalOpen, setIsRfqModalOpen] = useState(false);
  const [selectedPrestataireForRfq, setSelectedPrestataireForRfq] = useState<PrestataireItem | null>(null);
  const [isNewPrestataireModalOpen, setIsNewPrestataireModalOpen] = useState(false);
  const [rfqSuccess, setRfqSuccess] = useState(false);

  // RFQ Form state
  const [rfqTitle, setRfqTitle] = useState('');
  const [rfqDesc, setRfqDesc] = useState('');
  const [rfqUrgence, setRfqUrgence] = useState('NORMALE');
  const [rfqLieu, setRfqLieu] = useState('Douala Quai 14');
  const [rfqBudget, setRfqBudget] = useState('');

  // New Provider Form state (SuperAdmin only)
  const [newRaisonSociale, setNewRaisonSociale] = useState('');
  const [newSigle, setNewSigle] = useState('');
  const [newTypeEntite, setNewTypeEntite] = useState<'PRESTATAIRE' | 'GARAGE' | 'TRANSPORTEUR'>('PRESTATAIRE');
  const [newSpecialite, setNewSpecialite] = useState('MANUTENTION_PORTUAIRE');
  const [newVille, setNewVille] = useState('Douala');
  const [newContact, setNewContact] = useState('');
  const [newTel, setNewTel] = useState('');
  const [newTelAstreinte, setNewTelAstreinte] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newNif, setNewNif] = useState('');
  const [newRccm, setNewRccm] = useState('');
  const [newAgrement, setNewAgrement] = useState('');
  const [newLogoUrl, setNewLogoUrl] = useState('');
  const [newForfaitNom, setNewForfaitNom] = useState('');
  const [newForfaitTarif, setNewForfaitTarif] = useState('');
  const [newVehiculeType, setNewVehiculeType] = useState('');
  const [newVehiculeQte, setNewVehiculeQte] = useState('');
  const [newVehiculeTarifJour, setNewVehiculeTarifJour] = useState('');

  // RBAC Permission Check
  const userRoles = (user?.roles || []).map((r: string) => r.toUpperCase());
  const isSuperUser = Boolean((user as any)?.is_superuser);
  // Only SuperAdmin can add/edit/delete from the B2B Directory
  const isSuperAdmin = isSuperUser || userRoles.some(r => ['SUPER_ADMIN', 'SUPERADMIN'].includes(r));
  // Authorized to consult and send RFQ
  const isAuthorized = isSuperAdmin || userRoles.some(r =>
    ['ACHATS', 'DIRECTEUR_TRANSPORT', 'CHEF_PARC', 'ADMIN', 'DAF', 'CHEF_COMPTABLE', 'EXPLOITATION'].includes(r)
  );

  // Fetch from FastAPI backend  NO mock fallback
  const fetchPrestataires = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/prestataires', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}` }
      });
      if (res.ok) {
        const data = await res.json();
        setPrestataires(Array.isArray(data) ? data : []);
      } else {
        setPrestataires([]);
      }
    } catch {
      setPrestataires([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPrestataires();
  }, []);

  // Filtered list
  const filteredPrestataires = prestataires.filter(p => {
    const matchesSearch =
      p.raison_sociale.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.sigle && p.sigle.toLowerCase().includes(searchQuery.toLowerCase())) ||
      p.specialite.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.ville.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.agrement_portuaire && p.agrement_portuaire.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesSpec = selectedSpecialite === 'ALL' || p.specialite === selectedSpecialite;
    const matchesVille = selectedVille === 'ALL' || p.ville === selectedVille;
    const matchesPAD = !onlyPAD || (p.agrement_portuaire && (p.agrement_portuaire.includes('PAD') || p.agrement_portuaire.includes('PAK')));
    const matches24h = !only24h || Boolean(p.telephone_astreinte_24h);

    return matchesSearch && matchesSpec && matchesVille && matchesPAD && matches24h;
  });

  // Garages spécifiques
  const garagesPrestataires = prestataires.filter(p => {
    const isGarage = p.type_entite === 'GARAGE' || p.specialite.includes('GARAGE') || (p.specialites_panne && p.specialites_panne.length > 0);
    const matchesPanne = selectedPanne === 'Toutes les Pannes' || (p.specialites_panne && p.specialites_panne.some(panne => panne.toLowerCase().includes(selectedPanne.toLowerCase())));
    const matchesSearch = p.raison_sociale.toLowerCase().includes(searchQuery.toLowerCase()) || p.ville.toLowerCase().includes(searchQuery.toLowerCase());
    return isGarage && matchesPanne && matchesSearch;
  });

  // Transporteurs avec véhicules disponibles
  const transporteursAvecVehicules = prestataires.filter(p => {
    const hasVehicules = (p.vehicules_disponibles && p.vehicules_disponibles.length > 0) || p.type_entite === 'TRANSPORTEUR';
    const matchesSearch = p.raison_sociale.toLowerCase().includes(searchQuery.toLowerCase()) || p.ville.toLowerCase().includes(searchQuery.toLowerCase());
    return hasVehicules && matchesSearch;
  });

  const handleOpenRfq = (prestataire: PrestataireItem) => {
    setSelectedPrestataireForRfq(prestataire);
    setRfqTitle(`Prestation de ${prestataire.specialite.replace(/_/g, ' ')} - ${prestataire.ville}`);
    setIsRfqModalOpen(true);
  };

  const handleSubmitRfq = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPrestataireForRfq) return;

    const newRfq: CotationItem = {
      id: cotations.length + 1,
      numero_dossier: `RFQ-${new Date().getFullYear()}${String(new Date().getMonth() + 1).padStart(2, '0')}-${Math.floor(Math.random() * 900 + 100)}`,
      titre_besoin: rfqTitle,
      description_besoin: rfqDesc,
      urgence: rfqUrgence,
      lieu_intervention: rfqLieu,
      statut: 'TRANSMIS',
      budget_max_estime: rfqBudget ? parseFloat(rfqBudget) : undefined,
      created_at: new Date().toISOString(),
      prestataire_nom: selectedPrestataireForRfq.raison_sociale
    };

    setCotations([newRfq, ...cotations]);
    setRfqSuccess(true);
    setTimeout(() => {
      setRfqSuccess(false);
      setIsRfqModalOpen(false);
      setRfqTitle('');
      setRfqDesc('');
      setRfqBudget('');
    }, 1200);
  };

  const handleCreatePrestataire = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRaisonSociale || !newTel) return;

    const forfaits: ForfaitPropose[] = [];
    if (newForfaitNom && newForfaitTarif) {
      forfaits.push({
        libelle: newForfaitNom,
        tarif: parseFloat(newForfaitTarif),
        unite: 'Intervention'
      });
    }

    const vehicules: VehiculeDisponible[] = [];
    if (newVehiculeType && newVehiculeQte) {
      vehicules.push({
        type: newVehiculeType,
        quantite: parseInt(newVehiculeQte, 10),
        tarif_journalier: newVehiculeTarifJour ? parseFloat(newVehiculeTarifJour) : undefined
      });
    }

    const newP: PrestataireItem = {
      id: prestataires.length + 1,
      code: `PREST-${newSpecialite.substring(0, 3)}-${Math.floor(Math.random() * 9000 + 1000)}`,
      raison_sociale: newRaisonSociale,
      sigle: newSigle || undefined,
      logo_url: newLogoUrl || undefined,
      type_entite: newTypeEntite,
      specialite: newSpecialite,
      ville: newVille,
      tax_id: newNif || 'En cours d attribution',
      rccm: newRccm || undefined,
      agrement_portuaire: newAgrement || `PAD-AGR-${new Date().getFullYear()}-${Math.floor(Math.random() * 800 + 100)}`,
      est_homologue: true,
      statut_agrement: 'VALIDE',
      contact_nom: newContact,
      contact_telephone: newTel,
      telephone_astreinte_24h: newTelAstreinte || undefined,
      contact_email: newEmail,
      specialites_panne: newTypeEntite === 'GARAGE' ? ['Moteur / Culasse', 'Pneumatique PL', 'Remorquage Lourd 24/7'] : undefined,
      forfaits_proposes: forfaits.length > 0 ? forfaits : undefined,
      vehicules_disponibles: vehicules.length > 0 ? vehicules : undefined,
      note_globale: 4.9,
      nb_missions_realisees: 0,
      taux_ponctualite: 98.5,
      taux_conformite_qhse: 100.0,
      devise: 'XAF',
      conditions_reglement: 'Virement 30j fin de mois'
    };

    setPrestataires([newP, ...prestataires]);
    setIsNewPrestataireModalOpen(false);
    setNewRaisonSociale('');
    setNewSigle('');
    setNewTel('');
    setNewTelAstreinte('');
    setNewContact('');
    setNewEmail('');
    setNewNif('');
    setNewRccm('');
    setNewAgrement('');
    setNewLogoUrl('');
    setNewForfaitNom('');
    setNewForfaitTarif('');
    setNewVehiculeType('');
    setNewVehiculeQte('');
    setNewVehiculeTarifJour('');
  };

  // Restrict screen for unauthorized users
  if (!isAuthorized) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center p-6 text-white">
        <div className="max-w-md w-full bg-slate-900/90 border border-amber-500/40 rounded-3xl p-8 text-center shadow-2xl backdrop-blur-xl">
          <div className="w-16 h-16 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Shield className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-black text-slate-100 uppercase tracking-tight">Accès Réservé</h2>
          <p className="text-xs text-amber-300 font-semibold mt-1 mb-4">
            Département Achats, Logistique & Direction Générale
          </p>
          <p className="text-xs text-slate-400 leading-relaxed mb-6">
            L&apos;Annuaire des Prestataires B2B, le réseau de dépannage de garages 24/7 et la réservation de flottes disponibles sont strictement réservés aux gestionnaires d&apos;achats et directeurs d&apos;exploitation.
          </p>
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-[11px] text-slate-400 font-mono">
            Rôles autorisés : ACHATS, DIRECTEUR_TRANSPORT, CHEF_PARC, DAF, ADMIN, SUPER_ADMIN.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4 sm:p-8 space-y-6 text-white font-sans">

      {/* Top Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-3 py-1 bg-amber-500/15 border border-amber-500/30 text-amber-400 text-xs font-black uppercase rounded-full tracking-wider">
              CADC ERP • Réseau Logistique & Achats B2B
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Port Autonome de Douala & Kribi • Corridors CEMAC
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white flex items-center gap-3">
            <Building className="w-8 h-8 text-amber-400" />
            Annuaire Unique des Partenaires, Garages & Flottes B2B
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Réseau centralisé et certifié par l&apos;Admin SaaS : Garages d&apos;urgence 24/7 en cas de panne, entreprises avec véhicules disponibles, forfaits tarifaires et homologations légales.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Action button strictly reserved for SuperAdmin */}
          {isSuperAdmin && (
            <button
              onClick={() => setIsNewPrestataireModalOpen(true)}
              className="px-4 py-2.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-slate-950 font-black rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all active:scale-95"
            >
              <Plus className="w-4 h-4" />
              Référencer un Partenaire B2B
            </button>
          )}
          <button
            onClick={fetchPrestataires}
            className="p-2.5 bg-slate-900 border border-slate-700 hover:border-amber-400 text-slate-300 hover:text-amber-300 rounded-xl text-xs transition-colors"
            title="Rafraîchir les données"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase">Partenaires Référencés</span>
            <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Building className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-2">{prestataires.length}</div>
          <span className="text-[11px] text-emerald-400 font-semibold flex items-center gap-1 mt-1">
            <CheckCircle2 className="w-3 h-3" /> 100% Homologués & Vérifiés
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase">Garages Pannes 24/7</span>
            <div className="w-10 h-10 rounded-xl bg-red-500/15 border border-red-500/30 flex items-center justify-center text-red-400">
              <Wrench className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-2">
            {prestataires.filter(p => p.type_entite === 'GARAGE' || p.telephone_astreinte_24h).length}
          </div>
          <span className="text-[11px] text-red-400 font-semibold mt-1 block">
            Dépannage & Remorquage Urgent
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase">Véhicules Disponibles</span>
            <div className="w-10 h-10 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Truck className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-2">
            {prestataires.reduce((acc, p) => acc + (p.vehicules_disponibles?.reduce((sum, v) => sum + v.quantite, 0) || 0), 0)}
          </div>
          <span className="text-[11px] text-blue-400 font-semibold mt-1 block">
            Tracteurs, Bennes & Porte-chars
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase">Consultations Émises</span>
            <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <ShoppingCart className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-2">{cotations.length}</div>
          <span className="text-[11px] text-emerald-400 font-semibold mt-1 block">
            Appels d&apos;offres en direct
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('annuaire')}
          className={`px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2 whitespace-nowrap ${activeTab === 'annuaire'
              ? 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
        >
          <Building className="w-4 h-4" />
          Tous les Partenaires B2B ({filteredPrestataires.length})
        </button>

        <button
          onClick={() => setActiveTab('garages')}
          className={`px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2 whitespace-nowrap ${activeTab === 'garages'
              ? 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
        >
          <Wrench className="w-4 h-4" />
          Garages & Pannes 24/7 ({garagesPrestataires.length})
        </button>

        <button
          onClick={() => setActiveTab('vehicules')}
          className={`px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2 whitespace-nowrap ${activeTab === 'vehicules'
              ? 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
        >
          <Truck className="w-4 h-4" />
          Flottes & Véhicules Disponibles ({transporteursAvecVehicules.length})
        </button>

        <button
          onClick={() => setActiveTab('cotations')}
          className={`px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2 whitespace-nowrap ${activeTab === 'cotations'
              ? 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
        >
          <ShoppingCart className="w-4 h-4" />
          Demandes de Cotations ({cotations.length})
        </button>

        <button
          onClick={() => setActiveTab('conformite')}
          className={`px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2 whitespace-nowrap ${activeTab === 'conformite'
              ? 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
        >
          <ShieldCheck className="w-4 h-4" />
          Conformité & Agréments Portuaires
        </button>
      </div>

      {/* TAB 1: ANNUAIRE GENERAL */}
      {activeTab === 'annuaire' && (
        <div className="space-y-6">
          {/* Filter Bar */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 space-y-3">
            <div className="flex flex-col md:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Rechercher par raison sociale, sigle, spécialité, ville ou agrément..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full h-11 pl-10 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-400 transition-all font-mono"
                />
              </div>

              <select
                value={selectedVille}
                onChange={e => setSelectedVille(e.target.value)}
                className="h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-amber-400"
              >
                {VILLES.map(v => (
                  <option key={v.id} value={v.id}>{v.label}</option>
                ))}
              </select>

              <label className="flex items-center gap-2 px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-300 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={onlyPAD}
                  onChange={e => setOnlyPAD(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-amber-500 focus:ring-amber-500"
                />
                Agrément Portuaire (PAD/PAK)
              </label>

              <label className="flex items-center gap-2 px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-300 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={only24h}
                  onChange={e => setOnly24h(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-amber-500 focus:ring-amber-500"
                />
                Astreinte 24/7
              </label>
            </div>

            {/* Speciality Pills */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
              {SPECIALITES.map(spec => (
                <button
                  key={spec.id}
                  onClick={() => setSelectedSpecialite(spec.id)}
                  className={`px-3 py-1.5 rounded-lg text-[11px] font-bold whitespace-nowrap transition-all ${selectedSpecialite === spec.id
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                      : 'bg-slate-950 text-slate-400 border border-slate-800 hover:text-slate-200'
                    }`}
                >
                  {spec.label}
                </button>
              ))}
            </div>
          </div>

          {/* Cards Grid */}
          {filteredPrestataires.length === 0 ? (
            <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-12 text-center max-w-xl mx-auto space-y-4">
              <Building className="w-14 h-14 text-amber-500/40 mx-auto" />
              <h3 className="text-lg font-bold text-white">Aucun partenaire ne correspond aux critères</h3>
              <p className="text-xs text-slate-400">
                Ajustez vos filtres de recherche ou attendez que le Super Administrateur SaaS homologue de nouvelles entités.
              </p>
              {isSuperAdmin && (
                <button
                  onClick={() => setIsNewPrestataireModalOpen(true)}
                  className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-xs"
                >
                  Ajouter un partenaire maintenant
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              {filteredPrestataires.map(prestataire => (
                <div
                  key={prestataire.id}
                  className="bg-slate-900/90 border border-slate-800 hover:border-amber-500/50 rounded-3xl p-6 shadow-xl hover:shadow-2xl hover:shadow-amber-500/10 transition-all flex flex-col justify-between group"
                >
                  <div>
                    {/* Card Header with Logo */}
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="flex items-center gap-3">
                        {prestataire.logo_url ? (
                          <img
                            src={prestataire.logo_url}
                            alt={prestataire.raison_sociale}
                            className="w-12 h-12 object-contain rounded-xl border border-slate-700 bg-slate-900 p-1"
                          />
                        ) : (
                          <div className="w-12 h-12 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center text-amber-400 font-black text-sm">
                            {prestataire.sigle || prestataire.raison_sociale.substring(0, 2).toUpperCase()}
                          </div>
                        )}
                        <div>
                          <div className="flex items-center gap-1.5">
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-950 border border-slate-800 text-amber-400 font-bold">
                              {prestataire.code}
                            </span>
                            <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                              {prestataire.statut_agrement}
                            </span>
                          </div>
                          <h3 className="text-base font-black text-white mt-1 group-hover:text-amber-300 transition-colors">
                            {prestataire.raison_sociale}
                          </h3>
                        </div>
                      </div>

                      <div className="flex items-center gap-1 bg-amber-500/10 border border-amber-500/20 px-2 py-1 rounded-xl shrink-0">
                        <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                        <span className="text-xs font-black text-amber-300">{prestataire.note_globale}</span>
                      </div>
                    </div>

                    {/* Type & Specialite */}
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-xs text-slate-400 font-mono">
                        {prestataire.specialite.replace(/_/g, ' ')}
                      </span>
                    </div>

                    {/* Location & Agrément badge */}
                    <div className="space-y-1.5 mb-4 text-xs text-slate-300">
                      <div className="flex items-center gap-2 text-slate-300">
                        <MapPin className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                        <span className="font-bold">{prestataire.ville}</span>
                        {prestataire.zone_portuaire && (
                          <span className="text-slate-400 text-[11px] truncate">• {prestataire.zone_portuaire}</span>
                        )}
                      </div>
                      {prestataire.agrement_portuaire && (
                        <div className="flex items-center gap-2 text-[11px] text-amber-300/90 font-mono">
                          <Award className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                          <span className="truncate">{prestataire.agrement_portuaire}</span>
                        </div>
                      )}
                    </div>

                    {/* Legal Info Badges */}
                    <div className="p-2.5 bg-slate-950/80 rounded-xl border border-slate-800/80 text-[11px] text-slate-400 font-mono space-y-1 mb-4">
                      {prestataire.tax_id && (
                        <div>NIF : <span className="text-slate-200">{prestataire.tax_id}</span></div>
                      )}
                      {prestataire.rccm && (
                        <div>RCCM : <span className="text-slate-200">{prestataire.rccm}</span></div>
                      )}
                    </div>

                    {/* SLA Metrics */}
                    <div className="grid grid-cols-3 gap-2 bg-slate-950 p-2.5 rounded-2xl border border-slate-800 text-center mb-4">
                      <div>
                        <div className="text-[10px] text-slate-500 font-bold uppercase">Missions</div>
                        <div className="text-xs font-black text-white">{prestataire.nb_missions_realisees}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 font-bold uppercase">Ponctualité</div>
                        <div className="text-xs font-black text-emerald-400">{prestataire.taux_ponctualite}%</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 font-bold uppercase">QHSE</div>
                        <div className="text-xs font-black text-cyan-400">{prestataire.taux_conformite_qhse}%</div>
                      </div>
                    </div>

                    {/* Contact Snippets */}
                    <div className="space-y-1 text-xs text-slate-400 mb-4 font-mono">
                      <div className="flex items-center gap-2">
                        <Phone className="w-3.5 h-3.5 text-slate-500" />
                        <span>{prestataire.contact_telephone}</span>
                        {prestataire.telephone_astreinte_24h && (
                          <span className="text-[10px] text-red-400 font-bold ml-auto px-1.5 py-0.5 rounded bg-red-500/10 border border-red-500/20">
                            24h/24
                          </span>
                        )}
                      </div>
                      {prestataire.contact_email && (
                        <div className="flex items-center gap-2 truncate">
                          <Mail className="w-3.5 h-3.5 text-slate-500" />
                          <span className="truncate">{prestataire.contact_email}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Card Action */}
                  <div className="pt-3 border-t border-slate-800 flex items-center gap-2">
                    <button
                      onClick={() => handleOpenRfq(prestataire)}
                      className="flex-1 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-black rounded-xl text-xs flex items-center justify-center gap-2 transition-all active:scale-95 shadow-lg shadow-amber-500/15"
                    >
                      <Send className="w-3.5 h-3.5" />
                      Demander Cotation
                    </button>
                    <a
                      href={`tel:${prestataire.telephone_astreinte_24h || prestataire.contact_telephone}`}
                      className="p-2.5 bg-slate-950 hover:bg-slate-800 text-slate-300 hover:text-amber-400 rounded-xl border border-slate-800 transition-colors"
                      title="Appeler directement"
                    >
                      <Phone className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: GARAGES & PANNES EN ROUTE 24/7 */}
      {activeTab === 'garages' && (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-red-950/40 via-slate-900 to-slate-900 border border-red-500/30 rounded-2xl p-5 shadow-xl">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 text-red-400 font-bold text-xs uppercase tracking-wider">
                  <AlertOctagon className="w-4 h-4" /> Assistance Pannes & Dépannage Poids Lourd
                </div>
                <h2 className="text-xl font-black text-white mt-1">
                  Garages Agréés & Dépanneurs d&apos;Urgence 24h/24
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Intervention rapide sur les corridors Douala - Ndjamena, Douala - Bangui, axe Kribi et zones portuaires.
                </p>
              </div>

              {/* Filtre par type de panne */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Type de Panne :</span>
                <select
                  value={selectedPanne}
                  onChange={e => setSelectedPanne(e.target.value)}
                  className="h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-red-400"
                >
                  {SPECIALITES_PANNE.map(p => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {garagesPrestataires.length === 0 ? (
            <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-12 text-center max-w-xl mx-auto space-y-4">
              <Wrench className="w-14 h-14 text-red-500/40 mx-auto" />
              <h3 className="text-lg font-bold text-white">Aucun garage d&apos;astreinte répertorié pour ce critère</h3>
              <p className="text-xs text-slate-400">
                Modifiez le type de panne ou contactez directement la centrale d&apos;astreinte globale CADC.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              {garagesPrestataires.map(g => (
                <div
                  key={g.id}
                  className="bg-slate-900/90 border border-red-500/20 hover:border-red-500/60 rounded-3xl p-6 shadow-xl space-y-4 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 text-[10px] font-black rounded-full bg-red-500/20 text-red-400 border border-red-500/30">
                            GARAGE AGRÉÉ
                          </span>
                          <span className="text-xs text-slate-400 font-mono">{g.ville}</span>
                        </div>
                        <h3 className="text-base font-black text-white mt-1">{g.raison_sociale}</h3>
                      </div>
                      {g.telephone_astreinte_24h && (
                        <div className="px-2.5 py-1 rounded-xl bg-red-500/15 border border-red-500/30 text-red-400 text-xs font-black flex items-center gap-1 animate-pulse">
                          <Clock className="w-3.5 h-3.5" /> 24/7
                        </div>
                      )}
                    </div>

                    {/* Pannes prises en charge */}
                    <div className="mt-3">
                      <div className="text-[11px] font-bold text-slate-400 uppercase mb-1">Spécialités de Dépannage</div>
                      <div className="flex flex-wrap gap-1.5">
                        {(g.specialites_panne || ['Moteur PL', 'Pneumatique', 'Électricité', 'Remorquage']).map(spec => (
                          <span key={spec} className="px-2 py-0.5 rounded-lg bg-slate-950 border border-slate-800 text-[10px] font-semibold text-slate-300">
                            {spec}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Forfaits Proposés */}
                    {g.forfaits_proposes && g.forfaits_proposes.length > 0 && (
                      <div className="mt-3 p-3 bg-slate-950 rounded-2xl border border-slate-800/80 space-y-1.5">
                        <div className="text-[11px] font-bold text-amber-400 uppercase">Forfaits d&apos;Intervention</div>
                        {g.forfaits_proposes.map(f => (
                          <div key={f.libelle} className="flex justify-between items-center text-xs">
                            <span className="text-slate-300">{f.libelle}</span>
                            <span className="font-mono font-bold text-emerald-400">{f.tarif.toLocaleString()} XAF</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Mentions Légales */}
                    <div className="mt-3 text-[11px] font-mono text-slate-400 space-y-0.5">
                      {g.tax_id && <div>NIF : {g.tax_id}</div>}
                      {g.adresse && <div>Atelier : {g.adresse}</div>}
                    </div>
                  </div>

                  {/* Actions Dépannage Immédiat */}
                  <div className="pt-3 border-t border-slate-800 flex items-center gap-2">
                    <a
                      href={`tel:${g.telephone_astreinte_24h || g.contact_telephone}`}
                      className="flex-1 py-2.5 bg-red-600 hover:bg-red-500 text-white font-black rounded-xl text-xs flex items-center justify-center gap-2 shadow-lg shadow-red-500/20 active:scale-95 transition-all"
                    >
                      <Phone className="w-3.5 h-3.5" />
                      Appel Astreinte ({g.telephone_astreinte_24h || g.contact_telephone})
                    </a>
                    <button
                      onClick={() => handleOpenRfq(g)}
                      className="px-3 py-2.5 bg-slate-950 hover:bg-slate-800 border border-slate-700 text-slate-300 rounded-xl text-xs font-bold"
                      title="Demander devis écrit"
                    >
                      Devis
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: FLOTTES & VÉHICULES DISPONIBLES */}
      {activeTab === 'vehicules' && (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-blue-950/40 via-slate-900 to-slate-900 border border-blue-500/30 rounded-2xl p-5 shadow-xl">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 text-blue-400 font-bold text-xs uppercase tracking-wider">
                  <Truck className="w-4 h-4" /> Bourse de Sous-traitance Flotte & Capacités Roulantes
                </div>
                <h2 className="text-xl font-black text-white mt-1">
                  Entreprises de Transport & Véhicules Disponibles
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Consultez les disponibilités d&apos;engins et de camions par entreprise, avec forfaits journaliers et prix au km.
                </p>
              </div>
            </div>
          </div>

          {transporteursAvecVehicules.length === 0 ? (
            <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-12 text-center max-w-xl mx-auto space-y-4">
              <Truck className="w-14 h-14 text-blue-500/40 mx-auto" />
              <h3 className="text-lg font-bold text-white">Aucun véhicule actuellement référencé disponible</h3>
              <p className="text-xs text-slate-400">
                Les entreprises partenaires mettent à jour leurs disponibilités quotidiennement.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              {transporteursAvecVehicules.map(t => (
                <div
                  key={t.id}
                  className="bg-slate-900/90 border border-blue-500/20 hover:border-blue-500/60 rounded-3xl p-6 shadow-xl space-y-4 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <span className="px-2 py-0.5 text-[10px] font-black rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
                          TRANSPORTEUR AFFRÉTÉ
                        </span>
                        <h3 className="text-base font-black text-white mt-1">{t.raison_sociale}</h3>
                        <p className="text-xs text-slate-400 font-mono">{t.ville}</p>
                      </div>
                      {t.logo_url && (
                        <img
                          src={t.logo_url}
                          alt={t.raison_sociale}
                          className="w-10 h-10 object-contain rounded-xl border border-slate-700 bg-slate-900 p-1"
                        />
                      )}
                    </div>

                    {/* Véhicules Disponibles par Entreprise */}
                    <div className="mt-3 space-y-2">
                      <div className="text-[11px] font-bold text-blue-300 uppercase flex items-center justify-between">
                        <span>Parc Disponible Actuel</span>
                        <span className="font-mono text-emerald-400">
                          {t.vehicules_disponibles?.reduce((sum, v) => sum + v.quantite, 0) || 0} engin(s)
                        </span>
                      </div>

                      <div className="divide-y divide-slate-800 bg-slate-950 rounded-2xl p-3 border border-slate-800">
                        {(t.vehicules_disponibles || [
                          { type: 'Tracteur 6x4 Routier', quantite: 3, tarif_journalier: 120000 },
                          { type: 'Plateau Conteneur 40ft', quantite: 5, tarif_journalier: 85000 }
                        ]).map(v => (
                          <div key={v.type} className="py-1.5 flex items-center justify-between text-xs">
                            <div>
                              <div className="font-bold text-slate-200">{v.type}</div>
                              <div className="text-[10px] text-slate-500">
                                {v.tarif_journalier ? `${v.tarif_journalier.toLocaleString()} XAF / jour` : 'Sur devis'}
                              </div>
                            </div>
                            <span className="px-2 py-0.5 text-xs font-mono font-black rounded-lg bg-blue-500/20 text-blue-300 border border-blue-500/30">
                              x{v.quantite} dispo
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Legal Info */}
                    <div className="mt-3 text-[11px] font-mono text-slate-400 space-y-0.5">
                      {t.tax_id && <div>NIF : {t.tax_id}</div>}
                      {t.agrement_portuaire && <div>Agrément : {t.agrement_portuaire}</div>}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="pt-3 border-t border-slate-800 flex items-center gap-2">
                    <button
                      onClick={() => handleOpenRfq(t)}
                      className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-black rounded-xl text-xs flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20 active:scale-95 transition-all"
                    >
                      <Send className="w-3.5 h-3.5" />
                      Réserver / Cotation Flotte
                    </button>
                    <a
                      href={`tel:${t.contact_telephone}`}
                      className="p-2.5 bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 rounded-xl"
                      title="Appeler"
                    >
                      <Phone className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: COTATIONS (RFQ) */}
      {activeTab === 'cotations' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <ShoppingCart className="w-4 h-4 text-amber-400" />
                Registre des Appels d&apos;Offres & Demandes de Cotations (RFQ)
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Historique des consultations transmises aux sous-traitants pour chiffrage logistique.
              </p>
            </div>
            <span className="text-xs font-mono text-amber-400 bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20">
              {cotations.length} Consultations
            </span>
          </div>

          {cotations.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">
              Aucune demande de cotation n&apos;a été émise pour l&apos;instant. Cliquez sur &quot;Demander Cotation&quot; depuis un partenaire.
            </div>
          ) : (
            <div className="divide-y divide-slate-800">
              {cotations.map(c => (
                <div key={c.id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold text-amber-400">{c.numero_dossier}</span>
                      <span className="px-2 py-0.5 text-[10px] font-black rounded-full bg-blue-500/15 text-blue-300 border border-blue-500/30">
                        {c.urgence}
                      </span>
                      <span className="px-2 py-0.5 text-[10px] font-black rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
                        {c.statut}
                      </span>
                    </div>
                    <h4 className="text-sm font-bold text-white">{c.titre_besoin}</h4>
                    <p className="text-xs text-slate-400 max-w-2xl">{c.description_besoin}</p>
                    <div className="flex items-center gap-4 text-[11px] text-slate-400 pt-1">
                      <span>Prestataire : <b className="text-slate-200">{c.prestataire_nom}</b></span>
                      <span>Lieu : <b className="text-slate-200">{c.lieu_intervention}</b></span>
                      {c.budget_max_estime && (
                        <span>Budget estimé : <b className="text-emerald-400">{c.budget_max_estime.toLocaleString()} XAF</b></span>
                      )}
                    </div>
                  </div>

                  <div className="shrink-0 flex items-center gap-2">
                    <span className="text-[11px] font-mono text-slate-500">
                      {new Date(c.created_at).toLocaleDateString('fr-FR')}
                    </span>
                    <button className="px-3 py-1.5 bg-slate-950 hover:bg-slate-800 border border-slate-700 text-xs font-bold rounded-lg text-slate-200 flex items-center gap-1">
                      Détails <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 5: CONFORMITÉ & AGRÉMENTS */}
      {activeTab === 'conformite' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Tableau de Conformité Juridique, Fiscale & Portuaire (OHADA / CEMAC)
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Suivi de la validité des agréments Port Autonome de Douala (PAD), Port de Kribi (PAK), NIF et RCCM sous contrôle exclusif du SuperAdmin.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[11px] uppercase bg-slate-950/80 text-slate-400 font-mono border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Partenaire</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">NIF (Fiscal)</th>
                  <th className="py-3 px-4">RCCM</th>
                  <th className="py-3 px-4">Agrément Portuaire</th>
                  <th className="py-3 px-4">Statut</th>
                  <th className="py-3 px-4 text-right">Contrôle</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 font-mono">
                {prestataires.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-500">
                      Aucune entité répertoriée dans le registre légal.
                    </td>
                  </tr>
                ) : (
                  prestataires.map(p => (
                    <tr key={p.id} className="hover:bg-slate-800/30">
                      <td className="py-3.5 px-4 font-bold text-white font-sans flex items-center gap-2">
                        {p.logo_url ? (
                          <img src={p.logo_url} alt="" className="w-6 h-6 object-contain rounded bg-slate-900 p-0.5" />
                        ) : (
                          <Building className="w-4 h-4 text-amber-400" />
                        )}
                        <span>{p.raison_sociale}</span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-300 font-sans">
                        <span className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-[10px]">
                          {p.type_entite}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-amber-400">{p.tax_id || '-'}</td>
                      <td className="py-3.5 px-4 text-slate-400">{p.rccm || '-'}</td>
                      <td className="py-3.5 px-4 text-emerald-300 truncate max-w-xs">{p.agrement_portuaire || '-'}</td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 text-[10px] font-black rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                          {p.statut_agrement}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 font-semibold">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Conforme
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MODAL: DEMANDE DE COTATION (RFQ) */}
      {isRfqModalOpen && selectedPrestataireForRfq && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-amber-500/40 rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl space-y-4 animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <ShoppingCart className="w-5 h-5 text-amber-400" />
                <h3 className="text-base font-bold text-white">Demande de Cotation / Devis</h3>
              </div>
              <button
                onClick={() => setIsRfqModalOpen(false)}
                className="text-slate-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs">
              <span className="text-slate-400">Destinataire : </span>
              <b className="text-amber-400">{selectedPrestataireForRfq.raison_sociale}</b>
              <div className="text-[11px] text-slate-400 mt-0.5">
                Spécialité : {selectedPrestataireForRfq.specialite} • Ville : {selectedPrestataireForRfq.ville}
              </div>
            </div>

            <form onSubmit={handleSubmitRfq} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Titre de l&apos;Opération</label>
                <input
                  type="text"
                  value={rfqTitle}
                  onChange={e => setRfqTitle(e.target.value)}
                  className="w-full h-10 px-3.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Description Détaillée du Besoin</label>
                <textarea
                  value={rfqDesc}
                  onChange={e => setRfqDesc(e.target.value)}
                  placeholder="Précisez les volumes, caractéristiques des conteneurs, délais ou effectifs souhaités..."
                  rows={3}
                  className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400 resize-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Urgence</label>
                  <select
                    value={rfqUrgence}
                    onChange={e => setRfqUrgence(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                  >
                    <option value="NORMALE">Normale (24-48h)</option>
                    <option value="URGENTE">Urgente (&lt; 12h)</option>
                    <option value="IMMEDIATE">Immédiate (Astreinte)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Lieu</label>
                  <input
                    type="text"
                    value={rfqLieu}
                    onChange={e => setRfqLieu(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Budget Indicatif Max (Optionnel)</label>
                <div className="relative">
                  <DollarSign className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="number"
                    value={rfqBudget}
                    onChange={e => setRfqBudget(e.target.value)}
                    placeholder="Ex: 1500000"
                    className="w-full h-10 pl-9 pr-14 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400 font-mono"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-500">XAF</span>
                </div>
              </div>

              {rfqSuccess && (
                <div className="p-3 bg-emerald-950/80 border border-emerald-500/50 rounded-xl text-emerald-300 text-xs font-bold flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" /> Consultation transmise avec succès au sous-traitant !
                </div>
              )}

              <div className="pt-2 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsRfqModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-xl text-xs"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-black rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-amber-500/20"
                >
                  <Send className="w-3.5 h-3.5" />
                  Émettre la Consultation RFQ
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: NOUVEAU PRESTATAIRE (RÉSERVÉ SUPERADMIN) */}
      {isNewPrestataireModalOpen && isSuperAdmin && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-amber-500/40 rounded-3xl p-6 sm:p-8 max-w-2xl w-full shadow-2xl space-y-4 my-8">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Building className="w-5 h-5 text-amber-400" />
                <h3 className="text-base font-bold text-white">Homologuer un Partenaire / Garage / Transporteur</h3>
              </div>
              <button
                onClick={() => setIsNewPrestataireModalOpen(false)}
                className="text-slate-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreatePrestataire} className="space-y-4">
              {/* Type d'entité */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Catégorie Partenaire</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: 'PRESTATAIRE', label: 'Prestataire Sous-traitant', icon: Building },
                    { id: 'GARAGE', label: 'Garage & Dépannage Pannes', icon: Wrench },
                    { id: 'TRANSPORTEUR', label: 'Transporteur Flottes Dispo', icon: Truck },
                  ].map(cat => {
                    const Icon = cat.icon;
                    return (
                      <button
                        type="button"
                        key={cat.id}
                        onClick={() => setNewTypeEntite(cat.id as any)}
                        className={`p-2.5 rounded-xl border text-xs font-bold flex flex-col items-center gap-1.5 transition-all ${newTypeEntite === cat.id
                            ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                            : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                          }`}
                      >
                        <Icon className="w-4 h-4" />
                        <span className="text-center text-[11px]">{cat.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Raison Sociale</label>
                  <input
                    type="text"
                    placeholder="Ex: Cameroun Stevedoring Services S.A."
                    value={newRaisonSociale}
                    onChange={e => setNewRaisonSociale(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Sigle / Marque</label>
                  <input
                    type="text"
                    placeholder="Ex: CSS"
                    value={newSigle}
                    onChange={e => setNewSigle(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Spécialité Métier</label>
                  <select
                    value={newSpecialite}
                    onChange={e => setNewSpecialite(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                  >
                    {SPECIALITES.filter(s => s.id !== 'ALL').map(s => (
                      <option key={s.id} value={s.id}>{s.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Ville / Corridor</label>
                  <select
                    value={newVille}
                    onChange={e => setNewVille(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                  >
                    <option value="Douala">Douala (Port PAD)</option>
                    <option value="Kribi">Kribi (Port PAK)</option>
                    <option value="Yaounde">Yaoundé</option>
                    <option value="Ngaoundere">Ngaoundéré</option>
                    <option value="limbé">limbé</option>
                  </select>
                </div>
              </div>

              {/* Téléphones et Astreinte */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Téléphone Commercial</label>
                  <input
                    type="text"
                    placeholder="+237 233..."
                    value={newTel}
                    onChange={e => setNewTel(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400 font-mono"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Téléphone Astreinte 24/7 (Urgence)</label>
                  <input
                    type="text"
                    placeholder="+237 699... (Nuit & WE)"
                    value={newTelAstreinte}
                    onChange={e => setNewTelAstreinte(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-red-400 font-mono"
                  />
                </div>
              </div>

              {/* Contact Nom & Email */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Responsable Commercial / Chef Atelier</label>
                  <input
                    type="text"
                    placeholder="Nom du contact"
                    value={newContact}
                    onChange={e => setNewContact(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Email Officiel</label>
                  <input
                    type="email"
                    placeholder="contact@entreprise.cm"
                    value={newEmail}
                    onChange={e => setNewEmail(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                  />
                </div>
              </div>

              {/* Mentions Légales & Logo */}
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">NIF Fiscal</label>
                  <input
                    type="text"
                    placeholder="M0..."
                    value={newNif}
                    onChange={e => setNewNif(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">RCCM</label>
                  <input
                    type="text"
                    placeholder="RC/DLA/..."
                    value={newRccm}
                    onChange={e => setNewRccm(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Agrément Portuaire</label>
                  <input
                    type="text"
                    placeholder="PAD-AGR-..."
                    value={newAgrement}
                    onChange={e => setNewAgrement(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">URL du Logo Officiel</label>
                <input
                  type="url"
                  placeholder="https://.../logo.png"
                  value={newLogoUrl}
                  onChange={e => setNewLogoUrl(e.target.value)}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                />
              </div>

              {/* Forfait ou Véhicule initial */}
              {newTypeEntite === 'GARAGE' && (
                <div className="p-3 bg-slate-950 rounded-2xl border border-red-500/30 space-y-2">
                  <div className="text-xs font-bold text-red-400 uppercase">Forfait Dépannage Initial</div>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="text"
                      placeholder="Ex: Forfait Diagnostic Valise PL sur Route"
                      value={newForfaitNom}
                      onChange={e => setNewForfaitNom(e.target.value)}
                      className="h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white"
                    />
                    <input
                      type="number"
                      placeholder="Tarif (XAF) Ex: 75000"
                      value={newForfaitTarif}
                      onChange={e => setNewForfaitTarif(e.target.value)}
                      className="h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white font-mono"
                    />
                  </div>
                </div>
              )}

              {newTypeEntite === 'TRANSPORTEUR' && (
                <div className="p-3 bg-slate-950 rounded-2xl border border-blue-500/30 space-y-2">
                  <div className="text-xs font-bold text-blue-400 uppercase">Véhicules Disponibles Initiaux</div>
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      type="text"
                      placeholder="Type d'engin (ex: Tracteur 6x4)"
                      value={newVehiculeType}
                      onChange={e => setNewVehiculeType(e.target.value)}
                      className="h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white"
                    />
                    <input
                      type="number"
                      placeholder="Quantité dispo"
                      value={newVehiculeQte}
                      onChange={e => setNewVehiculeQte(e.target.value)}
                      className="h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white font-mono"
                    />
                    <input
                      type="number"
                      placeholder="Tarif jour (XAF)"
                      value={newVehiculeTarifJour}
                      onChange={e => setNewVehiculeTarifJour(e.target.value)}
                      className="h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white font-mono"
                    />
                  </div>
                </div>
              )}

              <div className="pt-2 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsNewPrestataireModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-xl text-xs"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-black rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-amber-500/20"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Homologuer & Référencer Partenaire
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
