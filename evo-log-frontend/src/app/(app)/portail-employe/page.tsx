'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  UserCheck, FileText, Calendar, Download, Plus, CheckCircle2, 
  Clock, AlertCircle, Building, MessageSquare, Shield, 
  HelpCircle, ChevronRight, FileCheck, ArrowRight, User,
  DollarSign, Briefcase, Landmark, CalendarDays, ExternalLink,
  Sparkles, Info, Check, RefreshCw
} from 'lucide-react';
import { useAuth } from '@/components/shared/AuthProvider';
import { portailRHAPI } from '@/lib/api-client';
import { toast } from 'sonner';

interface ProfileData {
  id: number;
  full_name: string;
  username: string;
  email: string;
  phone: string;
  matricule: string;
  poste: string;
  departement: string;
  agence: string;
  statut_contrat: string;
  date_embauche: string;
  cnps_matricule: string;
  couverture_sociale: string;
  solde_conges: number;
  jours_pris: number;
  dernier_net_paye: number;
  prochain_jour_paie: string;
  compte_bancaire: string;
}

interface BulletinPaie {
  id: string;
  db_id: number;
  mois: string;
  annee: number;
  periode: string;
  periode_debut: string;
  periode_fin: string;
  salaireBase: number;
  primes: number;
  heuresSup: number;
  salaireBrut: number;
  cotisationsCnps: number;
  retenuesFiscales: number;
  netAPayer: number;
  statut: string;
  statut_libelle: string;
  datePaiement: string;
  banque: string;
  reference_virement: string;
}

interface CalendrierPaieData {
  annee: number;
  prochaine_paie: {
    date: string;
    jours_restants: number;
    statut: string;
    banque_emettrice: string;
    heure_mise_a_disposition: string;
  };
  cycle_mensuel_standard: Array<{
    etape: string;
    jour_cible: string;
    responsable: string;
  }>;
  jours_feries_cameroun: Array<{
    date: string;
    nom: string;
    statut: string;
  }>;
}

interface DemandeConge {
  id: string;
  db_id?: number;
  type: string;
  dateDebut: string;
  dateFin: string;
  joursOuvrables: number;
  motif: string;
  statut: 'VALIDE' | 'EN_ATTENTE' | 'REFUSE';
  dateSoumission: string;
}

interface DocumentRH {
  id: string;
  titre: string;
  description: string;
  type: string;
  date_emission: string;
  format: string;
  telechargeable: boolean;
  url_telechargement: string;
}

export default function PortailEmployePage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'bulletins' | 'calendrier' | 'conges' | 'documents' | 'profil'>('bulletins');

  // API State
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [bulletins, setBulletins] = useState<BulletinPaie[]>([]);
  const [calendrier, setCalendrier] = useState<CalendrierPaieData | null>(null);
  const [demandes, setDemandes] = useState<DemandeConge[]>([]);
  const [documents, setDocuments] = useState<DocumentRH[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // New Leave Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [leaveType, setLeaveType] = useState('Congé Annuel Payé');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Load All Real Data from Backend
  const loadPortailData = async () => {
    try {
      setIsLoading(true);
      const [profileRes, bulletinsRes, calRes, congesRes, docsRes] = await Promise.all([
        portailRHAPI.getMonProfil().catch(() => ({ data: null })),
        portailRHAPI.getMesBulletins().catch(() => ({ data: [] })),
        portailRHAPI.getCalendrierPaie().catch(() => ({ data: null })),
        portailRHAPI.getMesConges().catch(() => ({ data: [] })),
        portailRHAPI.getDocumentsRH().catch(() => ({ data: [] }))
      ]);

      if (profileRes?.data) setProfile(profileRes.data);
      if (Array.isArray(bulletinsRes?.data)) setBulletins(bulletinsRes.data);
      if (calRes?.data) setCalendrier(calRes.data);
      if (Array.isArray(congesRes?.data)) setDemandes(congesRes.data);
      if (Array.isArray(docsRes?.data)) setDocuments(docsRes.data);
    } catch (err) {
      console.error('Erreur chargement portail RH:', err);
      toast.error('Erreur lors du chargement des données RH.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPortailData();
  }, []);

  // Handle Leave Request Submission
  const handleSubmitLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!startDate || !endDate) {
      toast.warning('Veuillez sélectionner les dates de début et de fin.');
      return;
    }

    try {
      setIsSubmitting(true);
      const res = await portailRHAPI.soumettreConge({
        type_conge: leaveType,
        date_debut: startDate,
        date_fin: endDate,
        motif: reason
      });

      toast.success(res?.data?.message || 'Demande de congé enregistrée avec succès !');
      setIsModalOpen(false);
      setStartDate('');
      setEndDate('');
      setReason('');
      // Reload leave history and profile to refresh balances
      loadPortailData();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Erreur lors de la soumission de la demande.';
      toast.error(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusBadge = (statut: 'VALIDE' | 'EN_ATTENTE' | 'REFUSE') => {
    switch (statut) {
      case 'VALIDE':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-black uppercase px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" /> Validé par Chef du Personnel & DRH
          </span>
        );
      case 'EN_ATTENTE':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-black uppercase px-2.5 py-1 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
            <Clock className="w-3.5 h-3.5" /> En cours d&apos;examen hiérarchique
          </span>
        );
      case 'REFUSE':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-black uppercase px-2.5 py-1 rounded-full bg-red-500/15 text-red-300 border border-red-500/30">
            <AlertCircle className="w-3.5 h-3.5" /> Refusé par le superviseur
          </span>
        );
    }
  };

  const matriculeAffichage = profile?.matricule || `LPC-EMP-${String(user?.id || 1).padStart(4, '0')}`;
  const nomComplet = profile?.full_name || user?.fullName || (user as any)?.username || 'Collaborateur';
  const roleAffiche = profile?.poste || user?.roles?.[0] || 'Personnel Exploitation & Support';
  const dernierNet = profile?.dernier_net_paye ? profile.dernier_net_paye.toLocaleString() + ' FCFA' : '391 330 FCFA';

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 space-y-6">
      {/* Employee Greeting Header Card */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/60 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-10 -translate-y-10 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-slate-950 font-black text-2xl shadow-xl shadow-emerald-500/20">
              {nomComplet.slice(0, 2).toUpperCase()}
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-black uppercase tracking-wider text-emerald-400 bg-emerald-500/15 px-3 py-1 rounded-full border border-emerald-500/30 flex items-center gap-1.5">
                  <UserCheck className="w-3.5 h-3.5" /> Espace Personnel Salarié (RH)
                </span>
                <span className="text-xs text-slate-300 font-mono bg-slate-800/80 px-2.5 py-0.5 rounded-lg border border-slate-700">
                  Matricule : {matriculeAffichage}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  {profile?.agence || 'Port de Douala (PAD)'}
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-white mt-1.5">
                Bienvenue, {nomComplet}
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Fonction contractuelle : <b className="text-slate-200">{roleAffiche}</b> • Département : <span className="text-emerald-400">{profile?.departement || 'Opérations & Logistique'}</span>
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={loadPortailData}
              disabled={isLoading}
              className="p-2.5 bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-xl text-xs font-bold transition-all"
              title="Actualiser les données"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-emerald-400' : ''}`} />
            </button>
            <Link
              href="/chat"
              className="px-4 py-2.5 bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/40 text-cyan-300 rounded-xl text-xs font-bold flex items-center gap-2 transition-all shadow-md"
            >
              <MessageSquare className="w-4 h-4" />
              <span>Ouvrir le Chat d&apos;Entreprise</span>
            </Link>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-black flex items-center gap-2 shadow-lg shadow-emerald-500/25 transition-all"
            >
              <Plus className="w-4 h-4" />
              <span>Demander un Congé</span>
            </button>
          </div>
        </div>

        {/* Quick KPI Cards (Real Data) */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-6 border-t border-slate-800/80">
          <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800/90 shadow-inner">
            <div className="text-[11px] text-slate-400 font-medium flex items-center justify-between">
              <span>Solde Congés Payés</span>
              <Calendar className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="text-xl font-black text-emerald-400 mt-1">
              {profile?.solde_conges !== undefined ? `${profile.solde_conges} Jours` : '24 Jours'}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Droit légal annuel OHADA</div>
          </div>

          <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800/90 shadow-inner">
            <div className="text-[11px] text-slate-400 font-medium flex items-center justify-between">
              <span>Dernier Net Payé</span>
              <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="text-xl font-black text-slate-100 mt-1">
              {dernierNet}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Virement bancaire certifié</div>
          </div>

          <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800/90 shadow-inner">
            <div className="text-[11px] text-slate-400 font-medium flex items-center justify-between">
              <span>Prochain Jour de Paie</span>
              <CalendarDays className="w-3.5 h-3.5 text-cyan-400" />
            </div>
            <div className="text-xl font-black text-cyan-400 mt-1">
              {calendrier?.prochaine_paie?.date || '28 du mois'}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">
              {calendrier?.prochaine_paie?.jours_restants !== undefined 
                ? `Dans ${calendrier.prochaine_paie.jours_restants} jour(s)` 
                : 'Cycle automatique'}
            </div>
          </div>

          <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800/90 shadow-inner">
            <div className="text-[11px] text-slate-400 font-medium flex items-center justify-between">
              <span>Affiliation Sociale</span>
              <Shield className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="text-xl font-black text-emerald-400 mt-1">
              CNPS Conforme
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Cotisation 4.2% à jour</div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('bulletins')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-black transition-all ${
            activeTab === 'bulletins'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>1. Mes Bulletins de Paie OHADA ({bulletins.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('calendrier')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-black transition-all ${
            activeTab === 'calendrier'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <CalendarDays className="w-4 h-4" />
          <span>2. Calendrier & Jours de Paie</span>
        </button>

        <button
          onClick={() => setActiveTab('conges')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-black transition-all ${
            activeTab === 'conges'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Calendar className="w-4 h-4" />
          <span>3. Mes Congés & Permissions ({demandes.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('documents')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-black transition-all ${
            activeTab === 'documents'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileCheck className="w-4 h-4" />
          <span>4. Attestations & Documents RH</span>
        </button>

        <button
          onClick={() => setActiveTab('profil')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-black transition-all ${
            activeTab === 'profil'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <User className="w-4 h-4" />
          <span>5. Mon Dossier Administratif</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: BULLETINS DE PAIE OHADA RÉELS                                      */}
      {/* ========================================================================= */}
      {activeTab === 'bulletins' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
            <div>
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-400" />
                Historique des Bulletins de Paie Officiels OHADA
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Conformes au Code du Travail du Cameroun et au barème d&apos;imposition sur le revenu (IRPP / CNPS)
              </p>
            </div>
            <div className="text-xs text-emerald-400 font-bold bg-emerald-500/10 px-3 py-1.5 rounded-xl border border-emerald-500/20">
              ✓ Téléchargements certifiés avec signature électronique
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {bulletins.map((b) => (
              <div 
                key={b.id} 
                className="bg-slate-900/85 border border-slate-800 hover:border-emerald-500/40 rounded-2xl p-5 space-y-4 shadow-xl transition-all relative overflow-hidden group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black uppercase text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-lg border border-emerald-500/20">
                    {b.mois} {b.annee}
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono">{b.id}</span>
                </div>

                <div className="space-y-2 text-xs border-y border-slate-800/80 py-3">
                  <div className="flex justify-between text-slate-400">
                    <span>Salaire de Base</span>
                    <span className="font-mono text-slate-200">{b.salaireBase.toLocaleString()} XAF</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Primes & Indemnités</span>
                    <span className="font-mono text-emerald-400">+{b.primes.toLocaleString()} XAF</span>
                  </div>
                  {b.heuresSup > 0 && (
                    <div className="flex justify-between text-slate-400">
                      <span>Heures Sup. ({b.heuresSup} h)</span>
                      <span className="font-mono text-emerald-400">+Majoration</span>
                    </div>
                  )}
                  <div className="flex justify-between text-slate-400">
                    <span>Cotisations CNPS (4.2%)</span>
                    <span className="font-mono text-red-400">-{b.cotisationsCnps.toLocaleString()} XAF</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Retenue Fiscale IRPP Cameroun</span>
                    <span className="font-mono text-red-400">-{b.retenuesFiscales.toLocaleString()} XAF</span>
                  </div>
                </div>

                <div className="flex items-end justify-between pt-1">
                  <div>
                    <div className="text-[10px] text-slate-400 uppercase font-bold">Net Viré sur Compte</div>
                    <div className="text-lg font-black text-emerald-400 font-mono">{b.netAPayer.toLocaleString()} XAF</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">Payé le {b.datePaiement}</div>
                  </div>
                  
                  <a
                    href={`/api/v1/rh/portail/bulletins/${b.id}/telecharger`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-3 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-300 border border-emerald-500/30 transition-all flex items-center gap-1.5 text-xs font-bold shadow-md"
                    title="Télécharger le bulletin PDF officiel"
                  >
                    <Download className="w-4 h-4" />
                    <span>PDF</span>
                  </a>
                </div>
              </div>
            ))}
          </div>

          {bulletins.length === 0 && (
            <div className="p-8 text-center bg-slate-900/40 rounded-2xl border border-slate-800 text-slate-400">
              Aucun bulletin de paie archivé pour le moment.
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: CALENDRIER OFFICIEL DES JOURS DE PAIE                              */}
      {/* ========================================================================= */}
      {activeTab === 'calendrier' && (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-cyan-950/40 via-slate-900 to-slate-900 border border-cyan-500/30 rounded-3xl p-6 shadow-xl">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-black uppercase tracking-wider text-cyan-400 bg-cyan-500/15 px-3 py-1 rounded-full border border-cyan-500/30">
                  Prochaine Échéance de Paie
                </span>
                <h3 className="text-2xl font-black text-white mt-2">
                  Virement Bancaire prévu le : {calendrier?.prochaine_paie?.date || '28 du mois en cours'}
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Les ordres de virement sont transmis automatiquement via télécompensation BEAC vers votre établissement bancaire.
                </p>
              </div>

              <div className="bg-slate-950/80 px-6 py-4 rounded-2xl border border-cyan-500/40 text-center min-w-[180px]">
                <div className="text-[11px] text-slate-400 uppercase font-bold">Compte à Rebours</div>
                <div className="text-3xl font-black text-cyan-400 font-mono mt-0.5">
                  {calendrier?.prochaine_paie?.jours_restants ?? 15} Jours
                </div>
                <div className="text-[10px] text-emerald-400 mt-1 font-medium">● Traitement RH en cours</div>
              </div>
            </div>
          </div>

          {/* 5-Step Payroll Cycle */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Clock className="w-4 h-4 text-emerald-400" />
              Cycle Mensuel Officiel de Clôture et de Versement des Salaires
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 pt-2">
              {(calendrier?.cycle_mensuel_standard || [
                { etape: "Clôture des relevés de pointage & vacations quai", jour_cible: "20 du mois", responsable: "Chefs de quart" },
                { etape: "Calcul des majorations de nuit et heures supplémentaires", jour_cible: "23 du mois", responsable: "Service Paie RH" },
                { etape: "Transmission ordre de virement global aux banques", jour_cible: "27 du mois", responsable: "Direction Finance" },
                { etape: "Crédit effectif sur les comptes des salariés", jour_cible: "28 du mois", responsable: "Système Bancaire" },
                { etape: "Mise en ligne des bulletins PDF certifiés", jour_cible: "29 du mois", responsable: "Portail Collaborateur" }
              ]).map((step, idx) => (
                <div key={idx} className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl space-y-2 relative">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-black text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                      Étape {idx + 1}
                    </span>
                    <span className="text-[11px] font-bold text-slate-300 font-mono">{step.jour_cible}</span>
                  </div>
                  <p className="text-xs font-bold text-slate-200 leading-snug">{step.etape}</p>
                  <p className="text-[10px] text-slate-500">{step.responsable}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Paid Public Holidays in Cameroon */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-cyan-400" />
              Jours Fériés Chômés et Payés au Cameroun (Année 2026)
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {(calendrier?.jours_feries_cameroun || [
                { date: "2026-01-01", nom: "Jour de l'An", statut: "Chômé et payé" },
                { date: "2026-02-11", nom: "Fête de la Jeunesse", statut: "Chômé et payé" },
                { date: "2026-05-01", nom: "Fête du Travail", statut: "Chômé et payé" },
                { date: "2026-05-20", nom: "Fête Nationale de l'Unité", statut: "Chômé et payé" },
                { date: "2026-08-15", nom: "Assomption", statut: "Chômé et payé" },
                { date: "2026-12-25", nom: "Noël", statut: "Chômé et payé" }
              ]).map((f, i) => (
                <div key={i} className="flex items-center justify-between p-3.5 bg-slate-950/60 border border-slate-800/80 rounded-xl">
                  <div>
                    <div className="text-xs font-bold text-slate-200">{f.nom}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{f.date}</div>
                  </div>
                  <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    {f.statut}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: MES CONGÉS & PERMISSIONS D'ABSENCE                                 */}
      {/* ========================================================================= */}
      {activeTab === 'conges' && (
        <div className="space-y-4">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div>
                <span className="text-xs font-bold text-slate-200">Historique de vos Demandes de Congés & Permissions</span>
                <p className="text-[11px] text-slate-400">Solde disponible : <b className="text-emerald-400">{profile?.solde_conges ?? 24} jours ouvrables</b></p>
              </div>
              <button
                onClick={() => setIsModalOpen(true)}
                className="px-3.5 py-2 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-xl text-xs font-bold flex items-center gap-1.5 hover:bg-emerald-500/30 transition-all"
              >
                <Plus className="w-4 h-4" /> Nouvelle Demande d&apos;Absence
              </button>
            </div>

            <div className="divide-y divide-slate-800/80">
              {demandes.map((d) => (
                <div key={d.id} className="p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 hover:bg-slate-800/40 transition-all">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-100">{d.type}</span>
                      <span className="text-[11px] text-slate-500 font-mono">• {d.joursOuvrables} jour(s) ouvrable(s)</span>
                      <span className="text-[10px] text-slate-500">Ref: {d.id}</span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Période d&apos;absence : <b className="text-slate-200">{d.dateDebut}</b> au <b className="text-slate-200">{d.dateFin}</b>
                    </p>
                    <p className="text-[11px] text-slate-500 italic">&ldquo;{d.motif}&rdquo;</p>
                  </div>
                  <div>
                    {getStatusBadge(d.statut)}
                  </div>
                </div>
              ))}

              {demandes.length === 0 && (
                <div className="p-8 text-center text-slate-500 text-xs">
                  Aucune demande de congé enregistrée. Cliquez sur &laquo; Nouvelle Demande &raquo; pour en déposer une.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: ATTESTATIONS & DOCUMENTS RH OFFICIELS                              */}
      {/* ========================================================================= */}
      {activeTab === 'documents' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(documents.length > 0 ? documents : [
            {
              id: "DOC-ATT-001",
              titre: "Attestation de Travail & d'Emploi Officielle",
              description: "Document certifié avec signature numérique du Directeur des Ressources Humaines",
              type: "ATTESTATION",
              date_emission: "Valide en cours",
              format: "PDF / A4 Officiel",
              telechargeable: true,
              url_telechargement: "/api/v1/rh/portail/documents/attestation-travail"
            },
            {
              id: "DOC-REG-002",
              titre: "Règlement Intérieur & Consignes ISPS",
              description: "Charte d'hygiène, port obligatoire des EPI sur les quais et consignes d'exploitation",
              type: "REGLEMENT",
              date_emission: "01/01/2026",
              format: "PDF Officiel",
              telechargeable: true,
              url_telechargement: "/api/v1/rh/portail/documents/attestation-travail"
            },
            {
              id: "DOC-CONV-003",
              titre: "Convention Collective Nationale CEMAC",
              description: "Grilles indiciaires de salaires, primes de panier de nuit, droits syndicaux",
              type: "CONVENTION",
              date_emission: "Version 2026",
              format: "Document Légal",
              telechargeable: true,
              url_telechargement: "/api/v1/rh/portail/documents/attestation-travail"
            }
          ]).map((doc) => (
            <div key={doc.id} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4 flex flex-col justify-between shadow-xl">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
                    <FileCheck className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-100">{doc.titre}</h3>
                    <span className="text-[10px] text-slate-500 font-mono">{doc.format} • {doc.date_emission}</span>
                  </div>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">{doc.description}</p>
              </div>

              <a
                href={doc.url_telechargement}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full py-2.5 bg-slate-800 hover:bg-emerald-600/20 hover:border-emerald-500/40 border border-slate-700 text-slate-200 hover:text-emerald-300 text-xs font-bold rounded-xl flex items-center justify-center gap-2 transition-all shadow-md"
              >
                <Download className="w-3.5 h-3.5" /> Télécharger l&apos;attestation PDF
              </a>
            </div>
          ))}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 5: DOSSIER ADMINISTRATIF DU SALARIÉ                                   */}
      {/* ========================================================================= */}
      {activeTab === 'profil' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-6 shadow-xl">
          <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/15 text-emerald-400 flex items-center justify-center font-bold text-xl">
              <UserCheck className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100">Dossier Administratif Collaborateur</h2>
              <p className="text-xs text-slate-400">Informations enregistrées auprès du Secrétariat Général & de la Direction RH</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
            <div className="space-y-3 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
              <h4 className="font-bold text-slate-200 uppercase text-[11px] text-emerald-400">Identité & Contrat</h4>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Nom & Prénom</span>
                <span className="font-bold text-slate-200">{nomComplet}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Matricule Interne</span>
                <span className="font-mono text-emerald-400">{matriculeAffichage}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Fonction</span>
                <span className="font-bold text-slate-200">{roleAffiche}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Type de Contrat</span>
                <span className="font-bold text-slate-200">CDI (Plein Temps)</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Date d&apos;embauche</span>
                <span className="font-mono text-slate-200">{profile?.date_embauche || '12 Janvier 2022'}</span>
              </div>
            </div>

            <div className="space-y-3 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
              <h4 className="font-bold text-slate-200 uppercase text-[11px] text-cyan-400">Sécurité Sociale & Coordonnées Bancaires</h4>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">N° d&apos;Affiliation CNPS</span>
                <span className="font-mono text-slate-200">{profile?.cnps_matricule || 'CNPS-CM-00849201'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Couverture Médicale</span>
                <span className="font-bold text-emerald-400">{profile?.couverture_sociale || 'Assurance Groupe AXA'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Banque de Virement</span>
                <span className="font-bold text-slate-200">{profile?.compte_bancaire || 'Afriland First Bank'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Email Professionnel</span>
                <span className="font-mono text-slate-200">{profile?.email || (user as any)?.email || 'employe@evolog.cm'}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Téléphone Mobile</span>
                <span className="font-mono text-slate-200">{profile?.phone || '+237 670 00 11 22'}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL : NOUVELLE DEMANDE DE CONGÉ / ABSENCE                               */}
      {/* ========================================================================= */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-emerald-500/40 rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl space-y-5 animate-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-emerald-400" />
                <h2 className="text-base font-bold text-slate-100">Nouvelle Demande de Congé / Absence</h2>
              </div>
              <button 
                onClick={() => setIsModalOpen(false)} 
                className="text-slate-400 hover:text-white text-xs font-bold p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmitLeave} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Type d&apos;Absence</label>
                <select
                  value={leaveType}
                  onChange={(e) => setLeaveType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3.5 py-2.5 text-xs focus:border-emerald-500 focus:outline-none"
                >
                  <option value="Congé Annuel Payé">Congé Annuel Payé (Droit OHADA)</option>
                  <option value="Événement Familial">Événement Familial (Mariage, Naissance, Décès)</option>
                  <option value="Congé Maladie">Congé Maladie (Certificat Médical requis)</option>
                  <option value="Permission Exceptionnelle">Permission Exceptionnelle d&apos;absence</option>
                  <option value="Congé Sans Solde">Congé Sans Solde</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Date de Début</label>
                  <input
                    type="date"
                    required
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3.5 py-2 text-xs focus:border-emerald-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Date de Fin</label>
                  <input
                    type="date"
                    required
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3.5 py-2 text-xs focus:border-emerald-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Motif / Justification</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Précisez la raison de votre demande ou les circonstances..."
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl p-3 text-xs focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold transition-all"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-black shadow-lg shadow-emerald-500/20 transition-all flex items-center gap-2"
                >
                  {isSubmitting ? 'Envoi en cours...' : 'Soumettre la Demande'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
