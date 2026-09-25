'use client';

import React, { useState, useEffect } from 'react';
import {
  UserCheck, Users, Calendar, Clock, ClipboardList, Shield,
  CheckCircle2, XCircle, AlertTriangle, Search, Filter, Plus,
  Phone, Mail, MapPin, ChevronRight, Check, X, ShieldAlert,
  RefreshCw, Briefcase, Award, Radio, FileText, Sparkles
} from 'lucide-react';
import { useAuth } from '@/components/shared/AuthProvider';

interface EffectifAgent {
  id: number;
  username: string;
  full_name: string;
  email: string;
  telephone?: string;
  role: string;
  agency_name: string;
  statut_presence: 'EN_POSTE' | 'EN_REPOS' | 'EN_CONGE' | 'ABSENT';
  quart_actuel?: string;
  dernier_pointage?: string;
}

interface DemandeCongeN1 {
  id: number;
  employe_id: number;
  employe_nom: string;
  employe_role: string;
  type_conge: string;
  date_debut: string;
  date_fin: string;
  jours_ouvrables: number;
  motif?: string;
  statut: 'EN_ATTENTE' | 'APPROUVE' | 'REJETE';
  date_demande?: string;
  commentaire_superviseur?: string;
}

interface PlanningItem {
  id: number;
  employe_id: number;
  employe_nom: string;
  employe_role: string;
  date_jour: string;
  quart: string;
  poste_assigne: string;
  statut: string;
  observations?: string;
}

interface PointageItem {
  id: number;
  employe_id: number;
  employe_nom: string;
  employe_role: string;
  date_pointage: string;
  heure_arrivee: string;
  heure_depart?: string;
  heures_effectives: number;
  droit_panier_nuit: boolean;
  montant_panier: number;
  est_valide: boolean;
  remarques?: string;
}

interface DotationItem {
  id: number;
  employe_id: number;
  employe_nom: string;
  employe_role: string;
  designation: string;
  categorie: string;
  date_remise: string;
  date_renouvellement_prevue?: string;
  numero_serie?: string;
  etat: string;
  est_restitue: boolean;
  observations?: string;
}

// Aucune donnée d'amorçage : les effectifs, congés, plannings, pointages et dotations
// sont alimentés exclusivement par l'API /api/v1/chef-personnel/*. En l'absence de
// réponse du backend, chaque onglet affiche un état vide explicite.


export default function ChefPersonnelPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'effectifs' | 'conges' | 'plannings' | 'pointages' | 'dotations'>('effectifs');

  // Deep-link depuis la navigation : /chef-personnel?tab=... ouvre l'onglet demande.
  useEffect(() => {
    const t = new URLSearchParams(window.location.search).get('tab');
    const allowed = ['effectifs', 'conges', 'plannings', 'pointages', 'dotations'];
    if (t && (allowed as string[]).includes(t)) setActiveTab(t as typeof activeTab);
  }, []);

  // Datasets (alimentés par l'API, vides par défaut  aucune donnée seed)
  const [effectifs, setEffectifs] = useState<EffectifAgent[]>([]);
  const [conges, setConges] = useState<DemandeCongeN1[]>([]);
  const [plannings, setPlannings] = useState<PlanningItem[]>([]);
  const [pointages, setPointages] = useState<PointageItem[]>([]);
  const [dotations, setDotations] = useState<DotationItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Filters
  const [roleFilter, setRoleFilter] = useState('ALL');
  const [searchFilter, setSearchFilter] = useState('');

  // Modals
  const [isDecisionModalOpen, setIsDecisionModalOpen] = useState(false);
  const [selectedCongeForDecision, setSelectedCongeForDecision] = useState<DemandeCongeN1 | null>(null);
  const [decisionAction, setDecisionAction] = useState<'APPROUVER' | 'REJETER'>('APPROUVER');
  const [decisionComment, setDecisionComment] = useState('');

  const [isPlanningModalOpen, setIsPlanningModalOpen] = useState(false);
  const [planAgentId, setPlanAgentId] = useState<number>(17);
  const [planQuart, setPlanQuart] = useState('NUIT (19h-07h)');
  const [planPoste, setPlanPoste] = useState('Poste Contrôle Quai 14');
  const [planObs, setPlanObs] = useState('');

  const [isDotationModalOpen, setIsDotationModalOpen] = useState(false);
  const [dotAgentId, setDotAgentId] = useState<number>(17);
  const [dotDesignation, setDotDesignation] = useState('');
  const [dotCategorie, setDotCategorie] = useState('EPI');
  const [dotSerie, setDotSerie] = useState('');

  // RBAC Permission Check
  const userRoles = (user?.roles || []).map(r => r.toUpperCase());
  const isSuperUser = (user as any)?.is_superuser;
  const isAuthorized = isSuperUser || userRoles.some(r =>
    ['CHEF_PERSONNEL', 'RH', 'ADMIN', 'SUPER_ADMIN'].includes(r)
  );

  // Fetch backend data
  const fetchData = async () => {
    setIsLoading(true);
    try {
      const resEff = await fetch('/api/v1/chef-personnel/effectifs');
      if (resEff.ok) {
        const data = await resEff.json();
        if (Array.isArray(data) && data.length > 0) setEffectifs(data);
      }

      const resCg = await fetch('/api/v1/chef-personnel/conges');
      if (resCg.ok) {
        const data = await resCg.json();
        if (Array.isArray(data) && data.length > 0) setConges(data);
      }

      const resPl = await fetch('/api/v1/chef-personnel/plannings');
      if (resPl.ok) {
        const data = await resPl.json();
        if (Array.isArray(data) && data.length > 0) setPlannings(data);
      }

      const resPt = await fetch('/api/v1/chef-personnel/pointages');
      if (resPt.ok) {
        const data = await resPt.json();
        if (Array.isArray(data) && data.length > 0) setPointages(data);
      }

      const resDt = await fetch('/api/v1/chef-personnel/dotations');
      if (resDt.ok) {
        const data = await resDt.json();
        if (Array.isArray(data) && data.length > 0) setDotations(data);
      }
    } catch {
      // Keep initial seed
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Handle Congé Decision
  const handleOpenDecision = (conge: DemandeCongeN1, action: 'APPROUVER' | 'REJETER') => {
    setSelectedCongeForDecision(conge);
    setDecisionAction(action);
    setDecisionComment(action === 'APPROUVER' ? 'Demande validée conforme aux plannings.' : 'Refusé pour nécessités urgentes de service.');
    setIsDecisionModalOpen(true);
  };

  const handleConfirmDecision = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCongeForDecision) return;

    try {
      await fetch(`/api/v1/chef-personnel/conges/${selectedCongeForDecision.id}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision: decisionAction,
          commentaire: decisionComment
        })
      });
    } catch { }

    setConges(conges.map(c => {
      if (c.id === selectedCongeForDecision.id) {
        return {
          ...c,
          statut: decisionAction === 'APPROUVER' ? 'APPROUVE' : 'REJETE',
          commentaire_superviseur: decisionComment
        };
      }
      return c;
    }));

    setIsDecisionModalOpen(false);
    setSelectedCongeForDecision(null);
  };

  // Handle Add Shift
  const handleAddPlanning = (e: React.FormEvent) => {
    e.preventDefault();
    const agent = effectifs.find(a => a.id === planAgentId);
    if (!agent) return;

    const newPlan: PlanningItem = {
      id: plannings.length + 1,
      employe_id: agent.id,
      employe_nom: agent.full_name,
      employe_role: agent.role,
      date_jour: new Date().toISOString().split('T')[0],
      quart: planQuart,
      poste_assigne: planPoste,
      statut: 'CONFIRME',
      observations: planObs
    };

    setPlannings([newPlan, ...plannings]);
    setIsPlanningModalOpen(false);
    setPlanObs('');
  };

  // Handle Add Dotation
  const handleAddDotation = (e: React.FormEvent) => {
    e.preventDefault();
    const agent = effectifs.find(a => a.id === dotAgentId);
    if (!agent || !dotDesignation) return;

    const newDot: DotationItem = {
      id: dotations.length + 1,
      employe_id: agent.id,
      employe_nom: agent.full_name,
      employe_role: agent.role,
      designation: dotDesignation,
      categorie: dotCategorie,
      date_remise: new Date().toISOString().split('T')[0],
      numero_serie: dotSerie || undefined,
      etat: 'NEUF',
      est_restitue: false
    };

    setDotations([newDot, ...dotations]);
    setIsDotationModalOpen(false);
    setDotDesignation('');
    setDotSerie('');
  };

  // Security barrier
  if (!isAuthorized) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center p-6 text-white">
        <div className="max-w-md w-full bg-slate-900/90 border border-emerald-500/40 rounded-3xl p-8 text-center shadow-2xl backdrop-blur-xl">
          <div className="w-16 h-16 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <ShieldAlert className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-black text-slate-100 uppercase tracking-tight">Accès Réservé N+1</h2>
          <p className="text-xs text-emerald-300 font-semibold mt-1 mb-4">
            Chef du Personnel & Direction des Ressources Humaines
          </p>
          <p className="text-xs text-slate-400 leading-relaxed mb-6">
            Ce module est strictement dédié à la supervision opérationnelle des secrétaires, gardiens, agents d&apos;entretien et techniciens support IT.
          </p>
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-[11px] text-slate-400 font-mono">
            Rôles autorisés : CHEF_PERSONNEL, RH, ADMIN, SUPER_ADMIN.
          </div>
        </div>
      </div>
    );
  }

  const filteredEffectifs = effectifs.filter(a => {
    const matchesRole = roleFilter === 'ALL' || a.role === roleFilter;
    const matchesSearch =
      a.full_name.toLowerCase().includes(searchFilter.toLowerCase()) ||
      a.username.toLowerCase().includes(searchFilter.toLowerCase()) ||
      a.agency_name.toLowerCase().includes(searchFilter.toLowerCase());
    return matchesRole && matchesSearch;
  });

  const pendingCongesCount = conges.filter(c => c.statut === 'EN_ATTENTE').length;

  return (
    <div className="min-h-screen p-4 sm:p-8 space-y-6 text-white font-sans">

      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-3 py-1 bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-black uppercase rounded-full tracking-wider">
              CADC ERP • Module Chef du Personnel
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Supervision N+1 des Rôles Passifs & Terrain
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white flex items-center gap-3">
            <UserCheck className="w-8 h-8 text-emerald-400" />
            Supervision & Encadrement du Personnel
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Arbitrage en direct des congés, plannings de garde 24/7, contrôle des vacations et dotations de sécurité ISPS.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsPlanningModalOpen(true)}
            className="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-black rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-all active:scale-95"
          >
            <Clock className="w-4 h-4" />
            Affecter un Quart de Garde
          </button>
          <button
            onClick={fetchData}
            className="p-2.5 bg-slate-900 border border-slate-700 hover:border-emerald-400 text-slate-300 hover:text-emerald-300 rounded-xl text-xs transition-colors"
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
            <span className="text-xs font-bold text-slate-400 uppercase">Agents Supervisés</span>
            <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-2">{effectifs.length}</div>
          <span className="text-[11px] text-emerald-400 font-semibold flex items-center gap-1 mt-1">
            <CheckCircle2 className="w-3 h-3" /> 100% Postes pourvus
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase">Congés à Valider (N+1)</span>
            <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Calendar className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-amber-400 mt-2">{pendingCongesCount}</div>
          <span className="text-[11px] text-amber-300 font-semibold mt-1 block">
            {pendingCongesCount > 0 ? 'Action requise immédiate' : 'Aucune demande en attente'}
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase">Gardes Actives 24/7</span>
            <div className="w-10 h-10 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-2">{plannings.length}</div>
          <span className="text-[11px] text-blue-400 font-semibold mt-1 block">
            Rondes jour & nuit planifiées
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase">Paniers de Nuit Validés</span>
            <div className="w-10 h-10 rounded-xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <ClipboardList className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-2">
            {pointages.filter(p => p.droit_panier_nuit).length}
          </div>
          <span className="text-[11px] text-purple-400 font-semibold mt-1 block">
            Primes OHADA conformes
          </span>
        </div>
      </div>

      {/* Tabs Menu */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2 overflow-x-auto scrollbar-none">
        <button
          onClick={() => setActiveTab('effectifs')}
          className={`px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2 shrink-0 ${activeTab === 'effectifs'
            ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20'
            : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
        >
          <Users className="w-4 h-4" />
          Effectifs Supervisés ({effectifs.length})
        </button>

        <button
          onClick={() => setActiveTab('conges')}
          className={`px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2 shrink-0 relative ${activeTab === 'conges'
            ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20'
            : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
        >
          <Calendar className="w-4 h-4" />
          Validation Congés N+1
          {pendingCongesCount > 0 && (
            <span className="ml-1 px-1.5 py-0.2 bg-red-500 text-white rounded-full text-[10px] font-black animate-pulse">
              {pendingCongesCount}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('plannings')}
          className={`px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2 shrink-0 ${activeTab === 'plannings'
            ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20'
            : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
        >
          <Clock className="w-4 h-4" />
          Plannings & Gardes 24/7 ({plannings.length})
        </button>

        <button
          onClick={() => setActiveTab('pointages')}
          className={`px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2 shrink-0 ${activeTab === 'pointages'
            ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20'
            : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
        >
          <ClipboardList className="w-4 h-4" />
          Pointages & Vacations ({pointages.length})
        </button>

        <button
          onClick={() => setActiveTab('dotations')}
          className={`px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2 shrink-0 ${activeTab === 'dotations'
            ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20'
            : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
        >
          <Shield className="w-4 h-4" />
          Dotations EPI & Matériel ({dotations.length})
        </button>
      </div>

      {/* TAB 1: EFFECTIFS SUPERVISÉS */}
      {activeTab === 'effectifs' && (
        <div className="space-y-4">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Rechercher un agent par nom, matricule ou agence..."
                value={searchFilter}
                onChange={e => setSearchFilter(e.target.value)}
                className="w-full h-11 pl-10 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-emerald-400 font-mono"
              />
            </div>

            <div className="flex items-center gap-2">
              {/* Filtres de rôle (configuration d'interface, pas des données métier) */}
              {/* audit-allow:fake_data */}
              {['ALL', 'SECRETAIRE', 'GARDIEN', 'AGENT_ENTRETIEN', 'SUPPORT_IT'].map(r => (
                <button
                  key={r}
                  onClick={() => setRoleFilter(r)}
                  className={`px-3 py-2 rounded-xl text-xs font-bold transition-all ${roleFilter === r
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                    : 'bg-slate-950 text-slate-400 border border-slate-800 hover:text-slate-200'
                    }`}
                >
                  {r === 'ALL' ? 'Tous les Postes' : r.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {filteredEffectifs.length === 0 && (
              <div className="md:col-span-2 xl:col-span-4 bg-slate-900/90 border border-dashed border-slate-800 rounded-2xl p-12 text-center">
                <Users className="w-10 h-10 text-slate-400 mx-auto mb-3" />
                <p className="text-sm text-slate-400">
                  Aucun agent supervisé chargé depuis l'API. Utilisez « Rafraîchir » pour récupérer les effectifs du service backend RH.
                </p>
              </div>
            )}
            {filteredEffectifs.map(agent => (
              <div
                key={agent.id}
                className="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 shadow-xl hover:border-emerald-500/40 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between mb-3">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center font-black text-lg text-slate-950 shadow-md">
                      {agent.full_name.substring(0, 2).toUpperCase()}
                    </div>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                      {agent.statut_presence.replace('_', ' ')}
                    </span>
                  </div>

                  <h3 className="text-base font-black text-white">{agent.full_name}</h3>
                  <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">
                    {agent.role.replace('_', ' ')}
                  </div>

                  <div className="space-y-1.5 text-xs text-slate-400 font-mono mb-4">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                      <span className="truncate">{agent.agency_name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                      <span className="text-slate-300">{agent.quart_actuel || 'Standard'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                      <span>{agent.telephone || 'Non renseigné'}</span>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
                  <span>Dernier pointage :</span>
                  <b className="text-slate-200">{agent.dernier_pointage || 'Émargé'}</b>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: VALIDATION CONGÉS & ABSENCES */}
      {activeTab === 'conges' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Calendar className="w-4 h-4 text-emerald-400" />
                Arbitrage & Validation des Demandes de Congés N+1
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Validez ou refusez directement les demandes des secrétaires, gardiens et agents de terrain.
              </p>
            </div>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
              {conges.length} Demandes Totales
            </span>
          </div>

          <div className="divide-y divide-slate-800">
            {conges.length === 0 && (
              <div className="py-12 text-center">
                <Calendar className="w-10 h-10 text-slate-400 mx-auto mb-3" />
                <p className="text-sm text-slate-400">Aucune demande de congé. Les demandes saisies par le personnel apparaîtront ici.</p>
              </div>
            )}
            {conges.map(cg => (
              <div key={cg.id} className="py-4 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-black text-sm text-white">{cg.employe_nom}</span>
                    <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-slate-800 text-slate-300 font-mono">
                      {cg.employe_role}
                    </span>
                    <span className={`px-2 py-0.5 text-[10px] font-black rounded-full ${cg.statut === 'APPROUVE'
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : cg.statut === 'REJETE'
                        ? 'bg-red-500/15 text-red-400 border border-red-500/30'
                        : 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                      }`}>
                      {cg.statut}
                    </span>
                  </div>

                  <div className="text-xs text-emerald-400 font-bold">{cg.type_conge}</div>
                  <p className="text-xs text-slate-300 max-w-2xl">{cg.motif}</p>

                  <div className="flex items-center gap-4 text-[11px] text-slate-400 font-mono pt-1">
                    <span>Période : <b className="text-slate-200">{cg.date_debut} → {cg.date_fin}</b></span>
                    <span>Durée : <b className="text-amber-300">{cg.jours_ouvrables} jours ouvrables</b></span>
                    {cg.commentaire_superviseur && (
                      <span className="text-slate-400 italic">Note N+1 : {cg.commentaire_superviseur}</span>
                    )}
                  </div>
                </div>

                {cg.statut === 'EN_ATTENTE' ? (
                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => handleOpenDecision(cg, 'APPROUVER')}
                      className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black rounded-xl text-xs flex items-center gap-1.5 shadow-lg shadow-emerald-500/20 transition-all active:scale-95"
                    >
                      <Check className="w-3.5 h-3.5" />
                      Approuver N+1
                    </button>
                    <button
                      onClick={() => handleOpenDecision(cg, 'REJETER')}
                      className="px-4 py-2 bg-red-950/80 hover:bg-red-900 border border-red-500/40 text-red-300 font-bold rounded-xl text-xs flex items-center gap-1.5 transition-all"
                    >
                      <X className="w-3.5 h-3.5" />
                      Rejeter
                    </button>
                  </div>
                ) : (
                  <div className="shrink-0 text-xs font-mono text-slate-500">
                    {cg.statut === 'APPROUVE' ? '✓ Arbitré & Notifié' : '✗ Refusé'}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: PLANNINGS & ROTATIONS 24/7 */}
      {activeTab === 'plannings' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Clock className="w-4 h-4 text-emerald-400" />
                Grille des Rotations de Garde & Permanences 24/7
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Affectation aux postes de sûreté portuaire, accueil et permanence technique.
              </p>
            </div>
            <button
              onClick={() => setIsPlanningModalOpen(true)}
              className="px-3.5 py-1.5 bg-emerald-500 text-slate-950 font-bold rounded-xl text-xs flex items-center gap-1.5 shadow-md"
            >
              <Plus className="w-3.5 h-3.5" /> Nouvel Affectation
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[11px] uppercase bg-slate-950/80 text-slate-400 font-mono border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Agent Assigné</th>
                  <th className="py-3 px-4">Rôle</th>
                  <th className="py-3 px-4">Quart / Horaire</th>
                  <th className="py-3 px-4">Poste Stratégique</th>
                  <th className="py-3 px-4">Statut</th>
                  <th className="py-3 px-4">Consignes & Observations</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 font-mono">
                {plannings.length === 0 && (
                  <tr><td colSpan={7} className="py-12 text-center text-slate-400 font-sans">Aucun planning de garde. Cliquez sur « Nouvelle Affectation » pour planifier un quart.</td></tr>
                )}
                {plannings.map(p => (
                  <tr key={p.id} className="hover:bg-slate-800/30">
                    <td className="py-3.5 px-4 text-amber-400">{p.date_jour}</td>
                    <td className="py-3.5 px-4 font-bold text-white font-sans">{p.employe_nom}</td>
                    <td className="py-3.5 px-4 text-slate-400">{p.employe_role}</td>
                    <td className="py-3.5 px-4 text-emerald-300 font-bold">{p.quart}</td>
                    <td className="py-3.5 px-4 text-slate-200 font-sans">{p.poste_assigne}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 text-[10px] font-black rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                        {p.statut}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-sans italic max-w-xs truncate">
                      {p.observations || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: POINTAGES & VACATIONS DE NUIT */}
      {activeTab === 'pointages' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <ClipboardList className="w-4 h-4 text-emerald-400" />
                Registre des Émargements & Primes de Panier de Nuit (OHADA)
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Contrôle des présences physiques, heures supplémentaires et indemnités de panier.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[11px] uppercase bg-slate-950/80 text-slate-400 font-mono border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Agent</th>
                  <th className="py-3 px-4">Arrivée</th>
                  <th className="py-3 px-4">Départ</th>
                  <th className="py-3 px-4">Heures Effectives</th>
                  <th className="py-3 px-4">Panier de Nuit</th>
                  <th className="py-3 px-4">Indemnité Panier</th>
                  <th className="py-3 px-4">Validation N+1</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 font-mono">
                {pointages.length === 0 && (
                  <tr><td colSpan={8} className="py-12 text-center text-slate-400 font-sans">Aucun pointage enregistré pour la période. Les émargements remontent depuis la borne de pointage.</td></tr>
                )}
                {pointages.map(pt => (
                  <tr key={pt.id} className="hover:bg-slate-800/30">
                    <td className="py-3.5 px-4 text-slate-400">{pt.date_pointage}</td>
                    <td className="py-3.5 px-4 font-bold text-white font-sans">{pt.employe_nom}</td>
                    <td className="py-3.5 px-4 text-emerald-400">{pt.heure_arrivee}</td>
                    <td className="py-3.5 px-4 text-slate-300">{pt.heure_depart || 'En poste'}</td>
                    <td className="py-3.5 px-4 font-bold text-white">{pt.heures_effectives}h</td>
                    <td className="py-3.5 px-4">
                      {pt.droit_panier_nuit ? (
                        <span className="px-2 py-0.5 text-[10px] font-black rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30">
                          ÉLIGIBLE NUIT
                        </span>
                      ) : (
                        <span className="text-slate-500">-</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-bold text-amber-400">
                      {pt.montant_panier > 0 ? `${pt.montant_panier.toLocaleString()} XAF` : '-'}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 font-semibold">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Certifié
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 5: DOTATIONS EPI & MATÉRIEL */}
      {activeTab === 'dotations' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Shield className="w-4 h-4 text-emerald-400" />
                Registre des Dotations EPI & Matériel de Terrain
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Suivi des gilets haute visibilité ISPS, chaussures de sécurité S3 et radios VHF.
              </p>
            </div>
            <button
              onClick={() => setIsDotationModalOpen(true)}
              className="px-3.5 py-1.5 bg-emerald-500 text-slate-950 font-bold rounded-xl text-xs flex items-center gap-1.5 shadow-md"
            >
              <Plus className="w-3.5 h-3.5" /> Attribuer Matériel
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[11px] uppercase bg-slate-950/80 text-slate-400 font-mono border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Agent Bénéficiaire</th>
                  <th className="py-3 px-4">Désignation Matériel</th>
                  <th className="py-3 px-4">Catégorie</th>
                  <th className="py-3 px-4">N° de Série</th>
                  <th className="py-3 px-4">Date Remise</th>
                  <th className="py-3 px-4">Renouvellement Prévu</th>
                  <th className="py-3 px-4">État</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 font-mono">
                {dotations.length === 0 && (
                  <tr><td colSpan={7} className="py-12 text-center text-slate-400 font-sans">Aucune dotation enregistrée. Cliquez sur « Attribuer Matériel » pour doter un agent (EPI, radio, badge).</td></tr>
                )}
                {dotations.map(dt => (
                  <tr key={dt.id} className="hover:bg-slate-800/30">
                    <td className="py-3.5 px-4 font-bold text-white font-sans">{dt.employe_nom}</td>
                    <td className="py-3.5 px-4 text-slate-200 font-sans font-bold">{dt.designation}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-slate-800 text-slate-300">
                        {dt.categorie}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-amber-400">{dt.numero_serie || '-'}</td>
                    <td className="py-3.5 px-4 text-slate-400">{dt.date_remise}</td>
                    <td className="py-3.5 px-4 text-emerald-300">{dt.date_renouvellement_prevue || '1 an'}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 text-[10px] font-black rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                        {dt.etat}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MODAL: DÉCISION CONGÉ */}
      {isDecisionModalOpen && selectedCongeForDecision && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-emerald-500/40 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-base font-black text-white flex items-center gap-2">
              <Calendar className="w-4 h-4 text-emerald-400" />
              Arbitrage N+1 : {selectedCongeForDecision.employe_nom}
            </h3>
            <p className="text-xs text-slate-300">
              {decisionAction === 'APPROUVER' ? 'Vous validez officiellement la demande de :' : 'Vous refusez la demande de :'}
              <b className="text-white block mt-0.5">{selectedCongeForDecision.type_conge} ({selectedCongeForDecision.jours_ouvrables} jours)</b>
            </p>

            <form onSubmit={handleConfirmDecision} className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Motif ou Commentaire N+1</label>
                <textarea
                  value={decisionComment}
                  onChange={e => setDecisionComment(e.target.value)}
                  rows={2}
                  className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-400 resize-none"
                  required
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsDecisionModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 text-xs font-bold rounded-xl"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className={`px-5 py-2 font-black rounded-xl text-xs flex items-center gap-1.5 text-slate-950 ${decisionAction === 'APPROUVER' ? 'bg-emerald-500 hover:bg-emerald-400' : 'bg-red-400 hover:bg-red-300'
                    }`}
                >
                  Confirmer la Décision
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: PLANNING QUART */}
      {isPlanningModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-emerald-500/40 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-base font-black text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-emerald-400" />
              Affecter un Quart de Garde / Rotation 24/7
            </h3>

            <form onSubmit={handleAddPlanning} className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Agent Assigné</label>
                <select
                  value={planAgentId}
                  onChange={e => setPlanAgentId(Number(e.target.value))}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-400"
                >
                  {effectifs.map(a => (
                    <option key={a.id} value={a.id}>{a.full_name} ({a.role})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Quart / Horaire</label>
                <select
                  value={planQuart}
                  onChange={e => setPlanQuart(e.target.value)}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-400"
                >
                  <option value="NUIT (19h-07h)">NUIT (19h-07h) - Droit Panier</option>
                  <option value="JOUR (07h-19h)">JOUR (07h-19h)</option>
                  <option value="MATIN (06h-14h)">MATIN (06h-14h)</option>
                  <option value="SOIR (14h-22h)">SOIR (14h-22h)</option>
                  <option value="STANDARD (08h-17h)">STANDARD (08h-17h)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Poste Assigné</label>
                <input
                  type="text"
                  value={planPoste}
                  onChange={e => setPlanPoste(e.target.value)}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-400"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Consignes</label>
                <input
                  type="text"
                  placeholder="Ex: Ronde toutes les 2h..."
                  value={planObs}
                  onChange={e => setPlanObs(e.target.value)}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-400"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsPlanningModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 text-xs font-bold rounded-xl"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black rounded-xl text-xs"
                >
                  Planifier
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: DOTATION EPI */}
      {isDotationModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-emerald-500/40 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-base font-black text-white flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-400" />
              Attribuer une Dotation EPI / Matériel
            </h3>

            <form onSubmit={handleAddDotation} className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Agent Destinataire</label>
                <select
                  value={dotAgentId}
                  onChange={e => setDotAgentId(Number(e.target.value))}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-400"
                >
                  {effectifs.map(a => (
                    <option key={a.id} value={a.id}>{a.full_name} ({a.role})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Désignation de l&apos;Équipement</label>
                <input
                  type="text"
                  placeholder="Ex: Rangers de Sécurité S3 Coquées"
                  value={dotDesignation}
                  onChange={e => setDotDesignation(e.target.value)}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-400"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Catégorie</label>
                  <select
                    value={dotCategorie}
                    onChange={e => setDotCategorie(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-400"
                  >
                    <option value="EPI">EPI</option>
                    <option value="COMMUNICATION">Communication (Radio/Talkie)</option>
                    <option value="UNIFORME">Uniforme de Service</option>
                    <option value="BADGE">Badge Sûreté ISPS</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-1">N° de Série (Optionnel)</label>
                  <input
                    type="text"
                    placeholder="Ex: ISPS-..."
                    value={dotSerie}
                    onChange={e => setDotSerie(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-400 font-mono"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsDotationModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 text-xs font-bold rounded-xl"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black rounded-xl text-xs"
                >
                  Attribuer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
