'use client';

/**
 * Mon Espace Salarié (portail RH self-service).
 *
 * Contrat d'affichage : chaque case provient de /api/v1/rh/portail/*. Une
 * information absente du dossier reste « Non renseigné » ; elle n'est jamais
 * remplacée par un numéro CNPS, un nom de banque, un salaire moyen ou une date
 * de virement de complaisance. Les statuts et types comparés sont les VALEURS
 * brutes d'enum rendues par l'API (en_attente, approuve, conge_annuel).
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import {
  UserCheck, FileText, Calendar, Download, Plus, CheckCircle2, Clock,
  AlertCircle, MessageSquare, CalendarDays, User, DollarSign, RefreshCw,
  FileCheck, AlertTriangle, X, Inbox, ShieldQuestion
} from 'lucide-react';
import { useAuth } from '@/components/shared/AuthProvider';
import { portailRHAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { toast } from 'sonner';

// ─── Contrat de données (miroir des dictionnaires du routeur rh.py) ──────────

interface ProfilSalarie {
  id: number;
  full_name: string | null;
  username: string | null;
  email: string | null;
  phone: string | null;
  matricule: string | null;
  poste: string | null;
  departement: string | null;
  agence: string | null;
  statut_contrat: string | null;
  date_embauche: string | null;
  cnps_matricule: string | null;
  couverture_sociale: string | null;
  compte_bancaire: string | null;
  solde_conges: number;
  jours_pris: number;
  droit_conge_annuel: number;
  annee_reference: number;
  dernier_net_paye: number | null;
  derniere_periode_paie: string | null;
}

interface Bulletin {
  id: number;
  reference: string;
  periode: string | null;
  mois_libelle: string | null;
  annee: number | null;
  periode_debut: string | null;
  periode_fin: string | null;
  salaire_base: number;
  heures_supplementaires: number;
  indemnite_heures_sup: number;
  primes: number;
  salaire_brut: number;
  cotisations_cnps: number;
  retenues_fiscales: number;
  autres_deductions: number;
  total_deductions: number;
  taux_cnps: number | null;
  net_a_payer: number;
  statut: string | null;
  date_paiement: string | null;
  devise: string | null;
}

interface DemandeConge {
  id: number;
  reference: string;
  type_conge: string | null;
  date_debut: string | null;
  date_fin: string | null;
  nombre_jours: number | null;
  statut: string | null;
  motif: string | null;
  date_demande: string | null;
  date_approbation: string | null;
  commentaire_approbation: string | null;
  motif_refus: string | null;
}

interface DocumentRH {
  id: number | string;
  reference: string;
  titre: string | null;
  type: string | null;
  nom_fichier: string | null;
  numero_document: string | null;
  organisme_emetteur: string | null;
  date_emission: string | null;
  date_expiration: string | null;
  statut: string | null;
  telechargeable: boolean;
  url_telechargement: string | null;
  raison_indisponibilite: string | null;
}

interface CalendrierPaie {
  annee: number;
  entreprise: string | null;
  fiches_enregistrees: number;
  jours_paiement_observes: number[];
  derniere_date_paiement: string | null;
  prochaine_paie: {
    date: string;
    jours_restants: number;
    jour_paiement_constate: number;
    base: string;
  } | null;
  message: string | null;
  jours_feries_cameroun: Array<{ date: string; nom: string; statut: string }>;
  fetes_mobiles_incluses: boolean;
}

// ─── Vocabulaire métier (clés = valeurs d'enum réellement stockées) ──────────

type Bilingue = { fr: string; en: string };

const NAS: Bilingue = { fr: 'Non renseigné', en: 'Not provided' };

const TYPES_CONGE: Record<string, Bilingue> = {
  conge_annuel: { fr: 'Congé annuel payé', en: 'Paid annual leave' },
  conge_maladie: { fr: 'Congé maladie', en: 'Sick leave' },
  conge_maternite: { fr: 'Congé maternité', en: 'Maternity leave' },
  conge_paternite: { fr: 'Congé paternité', en: 'Paternity leave' },
  conge_exceptionnel: { fr: 'Congé exceptionnel', en: 'Special leave' },
  conge_sans_solde: { fr: 'Congé sans solde', en: 'Unpaid leave' },
  absence_autorisee: { fr: 'Absence autorisée', en: 'Authorised absence' },
};

const STATUTS_CONGE: Record<string, { libelle: Bilingue; cls: string; icone: typeof CheckCircle2 }> = {
  en_attente: {
    libelle: { fr: 'En attente de décision N+1', en: 'Awaiting line-manager decision' },
    cls: 'bg-amber-500/15 text-amber-300 border-amber-500/30', icone: Clock,
  },
  approuve: {
    libelle: { fr: 'Approuvé', en: 'Approved' },
    cls: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30', icone: CheckCircle2,
  },
  en_cours: {
    libelle: { fr: 'En cours', en: 'In progress' },
    cls: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30', icone: Calendar,
  },
  termine: {
    libelle: { fr: 'Terminé', en: 'Completed' },
    cls: 'bg-slate-500/15 text-slate-300 border-slate-500/30', icone: CheckCircle2,
  },
  refuse: {
    libelle: { fr: 'Refusé', en: 'Rejected' },
    cls: 'bg-red-500/15 text-red-300 border-red-500/30', icone: AlertCircle,
  },
  annule: {
    libelle: { fr: 'Annulé', en: 'Cancelled' },
    cls: 'bg-slate-500/15 text-slate-400 border-slate-600/40', icone: X,
  },
};

const STATUTS_PAIE: Record<string, Bilingue> = {
  en_attente: { fr: 'En attente de paiement', en: 'Awaiting payment' },
  paye: { fr: 'Payé', en: 'Paid' },
  annule: { fr: 'Annulé', en: 'Cancelled' },
};

const TYPES_DOCUMENT: Record<string, Bilingue> = {
  ATTESTATION: { fr: 'Attestation de travail', en: 'Employment certificate' },
  attestation: { fr: 'Attestation de travail', en: 'Employment certificate' },
  cv: { fr: 'Curriculum vitae', en: 'Curriculum vitae' },
  diplome: { fr: 'Diplôme', en: 'Diploma' },
  contrat: { fr: 'Contrat de travail', en: 'Employment contract' },
  casier: { fr: 'Casier judiciaire', en: 'Criminal record' },
  certificat: { fr: 'Certificat', en: 'Certificate' },
};

// Fêtes à date fixe du Code du travail camerounais : la clé est le MM-JJ pour
// traduire un libellé rendu en français par l'API.
const FETES_EN: Record<string, string> = {
  '01-01': "New Year's Day",
  '02-11': 'Youth Day',
  '05-01': 'Labour Day',
  '05-20': 'National Unity Day',
  '08-15': 'Assumption',
  '11-01': "All Saints' Day",
  '12-25': 'Christmas',
};

const RAISONS_INDISPONIBILITE: Record<string, Bilingue> = {
  FICHIER_NON_DISPONIBLE: {
    fr: 'Le fichier n’est plus dans le coffre de stockage.',
    en: 'The file is no longer available in storage.',
  },
  AUCUN_CONTRAT_ENREGISTRE: {
    fr: 'Aucun contrat enregistré : aucune attestation ne peut être délivrée.',
    en: 'No contract on file: no certificate can be issued.',
  },
};

const onglets = ['bulletins', 'calendrier', 'conges', 'documents', 'profil'] as const;
type Onglet = typeof onglets[number];

const estVide = (v: unknown) => v === null || v === undefined || String(v).trim() === '';

const inputCls =
  'min-h-[44px] w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-xs text-slate-100 ' +
  'placeholder:text-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500/40';

export default function PortailEmployePage() {
  const { user } = useAuth();
  const { language } = useSettings();
  const lang = (language || 'fr') as 'fr' | 'en';
  const locale = lang === 'en' ? 'en-GB' : 'fr-FR';

  const dite = useCallback((b: Bilingue | undefined | null) => {
    if (!b) return null;
    return lang === 'en' ? b.en : b.fr;
  }, [lang]);

  const t = useCallback((fr: string, en: string) => (lang === 'en' ? en : fr), [lang]);

  const [activeTab, setActiveTab] = useState<Onglet>('bulletins');
  const [profil, setProfil] = useState<ProfilSalarie | null>(null);
  const [bulletins, setBulletins] = useState<Bulletin[]>([]);
  const [calendrier, setCalendrier] = useState<CalendrierPaie | null>(null);
  const [demandes, setDemandes] = useState<DemandeConge[]>([]);
  const [documents, setDocuments] = useState<DocumentRH[]>([]);
  const [loading, setLoading] = useState(true);
  const [erreur, setErreur] = useState('');

  const [modalOuvert, setModalOuvert] = useState(false);
  const [typeChoisi, setTypeChoisi] = useState('conge_annuel');
  const [dateDebut, setDateDebut] = useState('');
  const [dateFin, setDateFin] = useState('');
  const [motif, setMotif] = useState('');
  const [envoi, setEnvoi] = useState(false);
  const [telechargementEnCours, setTelechargementEnCours] = useState('');

  // Deep-link depuis la navigation : /portail-employe?tab=... ouvre l'onglet demandé.
  useEffect(() => {
    const demande = new URLSearchParams(window.location.search).get('tab');
    if (demande && (onglets as readonly string[]).includes(demande)) setActiveTab(demande as Onglet);
  }, []);

  const charger = useCallback(async () => {
    setLoading(true);
    setErreur('');
    // Chaque appel est suivi séparément : une défaillance partielle est annoncée
    // plutôt que masquée derrière un tableau vide.
    const résultats: string[] = [];
    const suivre = async <T,>(nom: string, requete: Promise<{ data: T }>, appliquer: (v: T) => void, repli: T) => {
      try {
        const res = await requete;
        appliquer((res?.data ?? repli) as T);
      } catch {
        résultats.push(nom);
        appliquer(repli);
      }
    };
    await Promise.all([
      suivre('profil', portailRHAPI.getMonProfil(), v => setProfil(v as ProfilSalarie | null), null),
      suivre('bulletins', portailRHAPI.getMesBulletins(), v => setBulletins(Array.isArray(v) ? v : []), []),
      suivre('calendrier', portailRHAPI.getCalendrierPaie(), v => setCalendrier(v as CalendrierPaie | null), null),
      suivre('conges', portailRHAPI.getMesConges(), v => setDemandes(Array.isArray(v) ? v : []), []),
      suivre('documents', portailRHAPI.getDocumentsRH(), v => setDocuments(Array.isArray(v) ? v : []), []),
    ]);
    if (résultats.length) {
      setErreur(t(
        `Service /api/v1/rh/portail injoignable pour : ${résultats.join(', ')}.`,
        `/api/v1/rh/portail service unreachable for: ${résultats.join(', ')}.`
      ));
    }
    setLoading(false);
  }, [t]);

  useEffect(() => {
    charger();
  }, [charger]);

  const montant = useCallback((v: number | null | undefined, devise = 'XAF') => {
    if (estVide(v)) return dite(NAS);
    return `${new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(Number(v))} ${devise}`;
  }, [locale, dite]);

  const enLettres = useCallback((iso: string | null | undefined) => {
    if (estVide(iso)) return dite(NAS);
    const d = new Date(String(iso));
    if (Number.isNaN(d.getTime())) return String(iso);
    return new Intl.DateTimeFormat(locale, { day: '2-digit', month: 'long', year: 'numeric' }).format(d);
  }, [locale, dite]);

  const champsValeur = useCallback((v: string | null | undefined) => (estVide(v) ? dite(NAS) : String(v)), [dite]);

  // Le nombre de jours ouvrables est estimé ici exactement comme le fait le
  // serveur (5 jours retenus sur 7 calendaires) : l'affichage est donc une
  // annonce, pas une donnée lue en base, et elle est annoncée comme telle.
  const joursEstimes = useMemo(() => {
    if (!dateDebut || !dateFin) return null;
    const debut = new Date(dateDebut);
    const fin = new Date(dateFin);
    if (Number.isNaN(debut.getTime()) || Number.isNaN(fin.getTime()) || fin < debut) return null;
    const joursCalendaires = Math.floor((fin.getTime() - debut.getTime()) / 86400000) + 1;
    return Math.max(1, Math.floor(joursCalendaires * 5 / 7));
  }, [dateDebut, dateFin]);

  const soumettreDemande = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!dateDebut || !dateFin) {
      toast.error(t('Renseignez la date de début et la date de fin.', 'Provide the start and end dates.'));
      return;
    }
    if (new Date(dateFin) < new Date(dateDebut)) {
      toast.error(t('La date de fin précède la date de début.', 'The end date is before the start date.'));
      return;
    }
    setEnvoi(true);
    try {
      const res = await portailRHAPI.soumettreConge({
        type_conge: typeChoisi,
        date_debut: dateDebut,
        date_fin: dateFin,
        motif: motif.trim(),
      });
      toast.success(t(
        'Demande enregistrée, transmise à votre responsable N+1 et à la DRH.',
        'Request saved and forwarded to your line manager and HR.'
      ));
      setModalOuvert(false);
      setDateDebut('');
      setDateFin('');
      setMotif('');
      // L'historique et le solde sont relus en base, jamais mis à jour à la main.
      await charger();
      if (res?.data?.reference) {
        toast.info(t(`Référence de la demande : ${res.data.reference}`, `Request reference: ${res.data.reference}`));
      }
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : t('Envoi impossible.', 'Submission failed.'));
    } finally {
      setEnvoi(false);
    }
  };

  const telecharger = async (cle: string, requete: Promise<any>, nomFichier: string) => {
    setTelechargementEnCours(cle);
    try {
      const res = await requete;
      const type = res?.headers?.['content-type'] || 'application/octet-stream';
      const url = URL.createObjectURL(new Blob([res.data], { type }));
      const lien = document.createElement('a');
      lien.href = url;
      lien.download = nomFichier;
      document.body.appendChild(lien);
      lien.click();
      lien.remove();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      const detail = err?.response?.data instanceof Blob
        ? await err.response.data.text().then(txt => {
            try { return JSON.parse(txt)?.detail; } catch { return null; }
          })
        : err?.response?.data?.detail;
      toast.error(typeof detail === 'string' && detail
        ? detail
        : t('Téléchargement impossible : le document n’est pas disponible.', 'Download failed: the document is not available.'));
    } finally {
      setTelechargementEnCours('');
    }
  };

  const nomComplet = profil?.full_name || user?.fullName || (user as any)?.username || dite(NAS);
  const initiales = estVide(nomComplet) ? '–' : nomComplet.slice(0, 2).toUpperCase();

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 space-y-6">
      {/* Bandeau d'erreur de chargement */}
      {erreur && (
        <div role="alert" className="flex items-start gap-3 border border-amber-500/40 bg-amber-500/10 rounded-2xl px-4 py-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <p className="text-xs text-amber-200 font-semibold flex-1 leading-relaxed">{erreur}</p>
          <button
            type="button"
            onClick={charger}
            className="min-h-[44px] min-w-[44px] p-2 rounded-lg text-amber-300 hover:text-white hover:bg-amber-500/20 flex items-center justify-center"
            aria-label={t('Réessayer', 'Retry')}
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Cartes KPI : uniquement des valeurs lues en base */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/60 border border-slate-800 rounded-3xl p-5 sm:p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-10 -translate-y-10 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-5">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 sm:w-16 sm:h-16 shrink-0 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-slate-950 font-black text-xl sm:text-2xl shadow-xl shadow-emerald-500/20">
              {initiales}
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-black uppercase tracking-wider text-emerald-400 bg-emerald-500/15 px-3 py-1 rounded-full border border-emerald-500/30 flex items-center gap-1.5">
                  <UserCheck className="w-3.5 h-3.5" /> {t('Espace salarié', 'Employee workspace')}
                </span>
                <span className="text-xs text-slate-300 font-mono bg-slate-800/80 px-2.5 py-1 rounded-lg border border-slate-700">
                  {t('Matricule', 'Staff ID')} : {champsValeur(profil?.matricule)}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  {champsValeur(profil?.agence)}
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-white mt-1.5 break-words">
                {t('Bonjour', 'Welcome')}, {nomComplet}
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                {t('Fonction', 'Job title')} : <b className="text-slate-200">{champsValeur(profil?.poste)}</b>
                {' • '}{t('Département', 'Department')} :{' '}
                <span className="text-emerald-400">{champsValeur(profil?.departement)}</span>
                {' • '}{t('Contrat', 'Contract')} :{' '}
                <span className="text-slate-200">{champsValeur(profil?.statut_contrat)}</span>
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={charger}
              disabled={loading}
              className="min-h-[44px] px-3.5 py-2.5 bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-xl text-xs font-bold transition-all disabled:opacity-50"
              title={t('Actualiser les données', 'Refresh data')}
              aria-label={t('Actualiser les données', 'Refresh data')}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-emerald-400' : ''}`} />
            </button>
            <Link
              href="/chat"
              className="min-h-[44px] px-4 py-2.5 bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/40 text-cyan-300 rounded-xl text-xs font-bold flex items-center gap-2 transition-all shadow-md"
            >
              <MessageSquare className="w-4 h-4" />
              <span>{t('Chat d’entreprise', 'Company chat')}</span>
            </Link>
            <button
              onClick={() => setModalOuvert(true)}
              className="min-h-[44px] px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-black flex items-center gap-2 shadow-lg shadow-emerald-500/25 transition-all"
            >
              <Plus className="w-4 h-4" />
              <span>{t('Demander un congé', 'Request leave')}</span>
            </button>
          </div>
        </div>

        <div className="relative z-10 grid grid-cols-2 lg:grid-cols-4 gap-3 mt-6 pt-6 border-t border-slate-800/80">
          <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800/90 shadow-inner">
            <div className="text-[11px] text-slate-400 font-medium flex items-center justify-between gap-2">
              <span className="truncate">{t('Solde de congés', 'Leave balance')}</span>
              <Calendar className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            </div>
            <div className="text-xl font-black text-emerald-400 mt-1">
              {estVide(profil?.solde_conges) ? dite(NAS) : `${profil?.solde_conges} ${t('j', 'd')}`}
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">
              {profil
                ? t(`Droit ${profil.droit_conge_annuel} j • ${profil.annee_reference}`, `${profil.droit_conge_annuel} days entitlement • ${profil.annee_reference}`)
                : dite(NAS)}
            </div>
          </div>

          <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800/90 shadow-inner">
            <div className="text-[11px] text-slate-400 font-medium flex items-center justify-between gap-2">
              <span className="truncate">{t('Congés pris', 'Leave taken')}</span>
              <CalendarDays className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            </div>
            <div className="text-xl font-black text-slate-100 mt-1">
              {estVide(profil?.jours_pris) ? dite(NAS) : `${profil?.jours_pris} ${t('j', 'd')}`}
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">
              {t('Approuvés sur l’année de référence', 'Approved within the reference year')}
            </div>
          </div>

          <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800/90 shadow-inner">
            <div className="text-[11px] text-slate-400 font-medium flex items-center justify-between gap-2">
              <span className="truncate">{t('Dernier net payé', 'Last net pay')}</span>
              <DollarSign className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            </div>
            <div className="text-xl font-black text-slate-100 mt-1 truncate">
              {montant(profil?.dernier_net_paye)}
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">
              {profil?.derniere_periode_paie
                ? `${t('Période', 'Period')} : ${enLettres(profil.derniere_periode_paie)}`
                : t('Aucune fiche de paie enregistrée', 'No payslip on record')}
            </div>
          </div>

          <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800/90 shadow-inner">
            <div className="text-[11px] text-slate-400 font-medium flex items-center justify-between gap-2">
              <span className="truncate">{t('Prochaine paie', 'Next payday')}</span>
              <Clock className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            </div>
            <div className="text-xl font-black text-cyan-400 mt-1">
              {calendrier?.prochaine_paie ? enLettres(calendrier.prochaine_paie.date) : dite(NAS)}
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">
              {calendrier?.prochaine_paie
                ? t(`Dans ${calendrier.prochaine_paie.jours_restants} j`, `In ${calendrier.prochaine_paie.jours_restants} days`)
                : t('Aucun versement enregistré', 'No payment recorded yet')}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('bulletins')}
          className={`min-h-[44px] flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-black transition-all ${activeTab === 'bulletins' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <FileText className="w-4 h-4" />
          <span>{t('Mes bulletins de paie', 'My payslips')} ({bulletins.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('calendrier')}
          className={`min-h-[44px] flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-black transition-all ${activeTab === 'calendrier' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <CalendarDays className="w-4 h-4" />
          <span>{t('Calendrier de paie', 'Payroll calendar')}</span>
        </button>
        <button
          onClick={() => setActiveTab('conges')}
          className={`min-h-[44px] flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-black transition-all ${activeTab === 'conges' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <Calendar className="w-4 h-4" />
          <span>{t('Mes congés', 'My leave')} ({demandes.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('documents')}
          className={`min-h-[44px] flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-black transition-all ${activeTab === 'documents' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <FileCheck className="w-4 h-4" />
          <span>{t('Attestations & documents', 'Certificates & documents')} ({documents.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('profil')}
          className={`min-h-[44px] flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-black transition-all ${activeTab === 'profil' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <User className="w-4 h-4" />
          <span>{t('Mon dossier administratif', 'My personnel file')}</span>
        </button>
      </div>

      {/* ─── ONGLET 1 : BULLETINS ─── */}
      {activeTab === 'bulletins' && (
        <div className="space-y-5">
          <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
            <h2 className="text-sm sm:text-base font-bold text-slate-100 flex items-center gap-2">
              <FileText className="w-4 h-4 text-emerald-400 shrink-0" />
              {t('Bulletins de paie enregistrés à votre nom', 'Payslips recorded under your name')}
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              {t(
                'Chaque montant est lu sur la fiche de paie en base. Le document imprimable n’est pas signé électroniquement : le cachet et la signature de la DRH restent manuscrits.',
                'Every amount is read from the payslip held in the database. The printable document is not electronically signed: the HR stamp and signature remain handwritten.'
              )}
            </p>
          </div>

          {loading && !bulletins.length && <EtatChargement t={t} />}

          {!loading && !bulletins.length && (
            <EtatVide
              icone={Inbox}
              titre={t('Aucun bulletin de paie enregistré', 'No payslip recorded')}
              texte={t(
                'La paie n’a pas encore été clôturée à votre nom : rien ne peut être affiché ni téléchargé.',
                'Payroll has not yet been closed for you: there is nothing to display or download.'
              )}
            />
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {bulletins.map((b) => (
              <div key={b.id} className="bg-slate-900/85 border border-slate-800 hover:border-emerald-500/40 rounded-2xl p-5 space-y-3 shadow-xl transition-all">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-black uppercase text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-lg border border-emerald-500/20 truncate">
                    {b.mois_libelle || b.periode || dite(NAS)} {b.annee ?? ''}
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono shrink-0">{b.reference}</span>
                </div>

                <div className="space-y-2 text-xs border-y border-slate-800/80 py-3">
                  <Ligne libelle={t('Salaire de base', 'Base salary')} valeur={montant(b.salaire_base, b.devise || 'XAF')} />
                  <Ligne libelle={t('Primes & indemnités', 'Bonuses & allowances')} valeur={`+${montant(b.primes, b.devise || 'XAF')}`} classe="text-emerald-400" />
                  {b.heures_supplementaires > 0 && (
                    <Ligne
                      libelle={`${t('Heures supplémentaires', 'Overtime')} (${b.heures_supplementaires} h)`}
                      valeur={`+${montant(b.indemnite_heures_sup, b.devise || 'XAF')}`}
                      classe="text-emerald-400"
                    />
                  )}
                  <Ligne libelle={t('Salaire brut', 'Gross salary')} valeur={montant(b.salaire_brut, b.devise || 'XAF')} />
                  <Ligne
                    libelle={b.taux_cnps
                      ? `${t('Cotisations CNPS', 'Social security')} (${(b.taux_cnps * 100).toFixed(2)} %)`
                      : t('Cotisations CNPS', 'Social security')}
                    valeur={`-${montant(b.cotisations_cnps, b.devise || 'XAF')}`}
                    classe="text-red-400"
                  />
                  <Ligne libelle={t('Retenue fiscale (IR)', 'Income tax withholding')} valeur={`-${montant(b.retenues_fiscales, b.devise || 'XAF')}`} classe="text-red-400" />
                  {b.autres_deductions > 0 && (
                    <Ligne libelle={t('Autres retenues', 'Other deductions')} valeur={`-${montant(b.autres_deductions, b.devise || 'XAF')}`} classe="text-red-400" />
                  )}
                </div>

                <div className="flex items-end justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-[11px] text-slate-400 uppercase font-bold">{t('Net à payer', 'Net pay')}</div>
                    <div className="text-lg font-black text-emerald-400 font-mono">{montant(b.net_a_payer, b.devise || 'XAF')}</div>
                    <div className="text-[11px] text-slate-500 mt-0.5">
                      {dite(STATUTS_PAIE[String(b.statut || '').toLowerCase()]) || champsValeur(b.statut)}
                      {b.date_paiement ? ` • ${t('Payé le', 'Paid on')} ${enLettres(b.date_paiement)}` : ''}
                    </div>
                  </div>
                  <button
                    onClick={() => telecharger(`bul-${b.id}`, portailRHAPI.telechargerBulletin(b.id), `bulletin-${b.reference}.html`)}
                    disabled={telechargementEnCours === `bul-${b.id}`}
                    className="shrink-0 min-h-[44px] px-3.5 py-2.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-300 border border-emerald-500/30 transition-all flex items-center gap-1.5 text-xs font-bold disabled:opacity-50"
                    title={t('Ouvrir le bulletin imprimable', 'Open the printable payslip')}
                  >
                    <Download className="w-4 h-4" />
                    <span>{telechargementEnCours === `bul-${b.id}` ? '…' : t('Imprimer', 'Print')}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── ONGLET 2 : CALENDRIER ─── */}
      {activeTab === 'calendrier' && (
        <div className="space-y-5">
          <div className="bg-gradient-to-r from-cyan-950/40 via-slate-900 to-slate-900 border border-cyan-500/30 rounded-3xl p-5 sm:p-6 shadow-xl">
            <span className="text-xs font-black uppercase tracking-wider text-cyan-400 bg-cyan-500/15 px-3 py-1 rounded-full border border-cyan-500/30">
              {t('Prochaine échéance de paie', 'Next payroll run')}
            </span>
            {calendrier?.prochaine_paie ? (
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mt-3">
                <div>
                  <h3 className="text-xl sm:text-2xl font-black text-white">
                    {enLettres(calendrier.prochaine_paie.date)}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    {t(
                      `Date projetée à partir du jour ${calendrier.prochaine_paie.jour_paiement_constate}, médiane des ${calendrier.fiches_enregistrees} versements enregistrés pour ${calendrier.entreprise || dite(NAS)}.`,
                      `Date projected from day ${calendrier.prochaine_paie.jour_paiement_constate}, the median of ${calendrier.fiches_enregistrees} payments recorded for ${calendrier.entreprise || dite(NAS)}.`
                    )}
                  </p>
                </div>
                <div className="bg-slate-950/80 px-6 py-4 rounded-2xl border border-cyan-500/40 text-center min-w-[160px]">
                  <div className="text-[11px] text-slate-400 uppercase font-bold">{t('Compte à rebours', 'Countdown')}</div>
                  <div className="text-3xl font-black text-cyan-400 font-mono mt-0.5">
                    {calendrier.prochaine_paie.jours_restants}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">{t('jours', 'days')}</div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-300 mt-3 leading-relaxed">
                {t(
                  'Aucun versement de salaire n’est encore enregistré pour cette entreprise : aucune date de paie ne peut être annoncée. Les dates affichées ici seront calculées à partir des paiements réellement effectués.',
                  'No salary payment has been recorded for this company yet: no payday can be announced. The dates shown here will be computed from payments actually made.'
                )}
              </p>
            )}
            {calendrier?.derniere_date_paiement && (
              <p className="text-[11px] text-slate-500 mt-3">
                {t('Dernier versement constaté le', 'Last payment recorded on')} {enLettres(calendrier.derniere_date_paiement)}
              </p>
            )}
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-cyan-400" />
              {t(`Jours fériés chômés et payés (${calendrier?.annee ?? new Date().getFullYear()})`, `Paid public holidays (${calendrier?.annee ?? new Date().getFullYear()})`)}
            </h3>
            {loading && !calendrier && <EtatChargement t={t} />}
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
              {(calendrier?.jours_feries_cameroun || []).map((f, i) => {
                const cle = String(f.date).slice(5);
                const nom = lang === 'en' ? (FETES_EN[cle] || f.nom) : f.nom;
                const paye = lang === 'en'
                  ? (/pay/i.test(f.statut) ? 'Paid' : f.statut)
                  : f.statut;
                return (
                  <div key={i} className="flex items-center justify-between gap-3 p-3.5 bg-slate-950/60 border border-slate-800/80 rounded-xl">
                    <div className="min-w-0">
                      <div className="text-xs font-bold text-slate-200 truncate">{nom}</div>
                      <div className="text-[11px] text-slate-500 font-mono">{enLettres(f.date)}</div>
                    </div>
                    <span className="text-[11px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 shrink-0">
                      {paye}
                    </span>
                  </div>
                );
              })}
            </div>
            {calendrier?.fetes_mobiles_incluses === false && (
              <p className="text-[11px] text-slate-500 leading-relaxed">
                {t(
                  'Liste limitée aux fêtes à date fixe du Code du travail : les fêtes mobiles (Pâques, Ascension, Pentecôte, Aï-el Kébir, Fin Ramadan) dépendent du calendrier lunaire et ne sont pas calculées.',
                  'Only fixed-date holidays under the labour code are listed: mobile feasts (Easter, Ascension, Pentecost, Eid al-Kebir, Eid al-Fitr) follow the lunar calendar and are not computed.'
                )}
              </p>
            )}
          </div>
        </div>
      )}

      {/* ─── ONGLET 3 : CONGÉS ─── */}
      {activeTab === 'conges' && (
        <div className="space-y-4">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div>
                <span className="text-xs font-bold text-slate-200">
                  {t('Historique de vos demandes', 'History of your requests')}
                </span>
                <p className="text-[11px] text-slate-400">
                  {t('Solde disponible', 'Remaining balance')} :{' '}
                  <b className="text-emerald-400">
                    {estVide(profil?.solde_conges) ? dite(NAS) : `${profil?.solde_conges} ${t('jours ouvrables', 'working days')}`}
                  </b>
                </p>
              </div>
              <button
                onClick={() => setModalOuvert(true)}
                className="min-h-[44px] px-4 py-2.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-xl text-xs font-bold flex items-center gap-1.5 hover:bg-emerald-500/30 transition-all"
              >
                <Plus className="w-4 h-4" /> {t('Nouvelle demande', 'New request')}
              </button>
            </div>

            {loading && !demandes.length && <EtatChargement t={t} />}

            <div className="divide-y divide-slate-800/80">
              {demandes.map((d) => {
                const statut = String(d.statut || '').toLowerCase();
                const badge = STATUTS_CONGE[statut];
                const Icone = badge?.icone || AlertCircle;
                return (
                  <div key={d.id} className="p-4 flex flex-col lg:flex-row lg:items-start lg:justify-between gap-3 hover:bg-slate-800/40 transition-all">
                    <div className="space-y-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-bold text-slate-100">
                          {dite(TYPES_CONGE[String(d.type_conge || '').toLowerCase()]) || champsValeur(d.type_conge)}
                        </span>
                        <span className="text-[11px] text-slate-500 font-mono">
                          • {d.nombre_jours ?? dite(NAS)} {t('jour(s) ouvrable(s)', 'working day(s)')}
                        </span>
                        <span className="text-[11px] text-slate-500 font-mono">{d.reference}</span>
                      </div>
                      <p className="text-xs text-slate-400">
                        {t('Période', 'Period')} : <b className="text-slate-200">{enLettres(d.date_debut)}</b>
                        {' '}{t('au', 'to')} <b className="text-slate-200">{enLettres(d.date_fin)}</b>
                      </p>
                      <p className="text-[11px] text-slate-500">
                        {t('Déposée le', 'Filed on')} {enLettres(d.date_demande)}
                      </p>
                      {d.motif ? (
                        <p className="text-[11px] text-slate-500 italic">« {d.motif} »</p>
                      ) : (
                        <p className="text-[11px] text-slate-600 italic">{t('Aucun motif précisé', 'No reason given')}</p>
                      )}
                      {statut === 'refuse' && d.motif_refus && (
                        <p className="text-[11px] text-red-300">
                          {t('Motif du refus', 'Reason for rejection')} : {d.motif_refus}
                        </p>
                      )}
                      {(statut === 'approuve' || statut === 'en_cours' || statut === 'termine') && d.commentaire_approbation && (
                        <p className="text-[11px] text-emerald-300">
                          {t('Commentaire du décideur', 'Decision comment')} : {d.commentaire_approbation}
                        </p>
                      )}
                    </div>
                    <span className={`inline-flex items-center gap-1 self-start text-[11px] font-black uppercase px-2.5 py-1 rounded-full border shrink-0 ${badge?.cls || 'bg-slate-500/15 text-slate-300 border-slate-600/40'}`}>
                      <Icone className="w-3.5 h-3.5" />
                      {badge ? dite(badge.libelle) : champsValeur(d.statut)}
                    </span>
                  </div>
                );
              })}

              {!loading && !demandes.length && (
                <EtatVide
                  icone={Calendar}
                  titre={t('Aucune demande enregistrée', 'No request recorded')}
                  texte={t(
                    'Déposez une demande depuis l’onglet : elle partira chez votre responsable N+1 et à la DRH.',
                    'File a request here: it will be routed to your line manager and HR.'
                  )}
                />
              )}
            </div>
          </div>
        </div>
      )}

      {/* ─── ONGLET 4 : DOCUMENTS ─── */}
      {activeTab === 'documents' && (
        <div className="space-y-5">
          <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
            <h2 className="text-sm sm:text-base font-bold text-slate-100">
              {t('Pièces de votre dossier', 'Documents held in your file')}
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              {t(
                'Seules les pièces réellement versées à votre dossier apparaissent. Une pièce téléchargeable est un fichier qui existe dans le coffre.',
                'Only documents actually filed under your record are listed. A downloadable item is a file that exists in storage.'
              )}
            </p>
          </div>

          {loading && !documents.length && <EtatChargement t={t} />}
          {!loading && !documents.length && (
            <EtatVide
              icone={FileCheck}
              titre={t('Aucune pièce au dossier', 'No document on file')}
              texte={t('Aucun document et aucun contrat enregistré pour l’instant.', 'No document and no contract recorded so far.')}
            />
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {documents.map((doc) => {
              const cle = `doc-${doc.id}`;
              const raison = doc.raison_indisponibilite ? RAISONS_INDISPONIBILITE[doc.raison_indisponibilite] : null;
              const nomFichier = doc.nom_fichier
                || (/attestation/i.test(String(doc.type)) ? `attestation-travail-${doc.id}.html` : `document-${doc.id}`);
              const telechargeable = Boolean(doc.telechargeable) && Boolean(doc.url_telechargement);
              return (
                <div key={String(doc.id)} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4 flex flex-col justify-between shadow-xl">
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 shrink-0 rounded-xl bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
                        <FileCheck className="w-5 h-5" />
                      </div>
                      <div className="min-w-0">
                        <h3 className="text-sm font-bold text-slate-100 break-words">
                          {doc.titre || dite(TYPES_DOCUMENT[String(doc.type || '')]) || champsValeur(doc.type)}
                        </h3>
                        <span className="text-[11px] text-slate-500 font-mono">{doc.reference}</span>
                      </div>
                    </div>
                    <div className="text-[11px] text-slate-400 space-y-1">
                      <p>{t('Émis le', 'Issued on')} {enLettres(doc.date_emission)}</p>
                      {doc.date_expiration && <p>{t('Expire le', 'Expires on')} {enLettres(doc.date_expiration)}</p>}
                      {doc.organisme_emetteur && <p className="truncate">{t('Émetteur', 'Issuer')} : {doc.organisme_emetteur}</p>}
                      <p>{t('Numéro', 'Number')} : {champsValeur(doc.numero_document)}</p>
                    </div>
                  </div>

                  {telechargeable ? (
                    <button
                      onClick={() => telecharger(
                        cle,
                        typeof doc.id === 'number'
                          ? portailRHAPI.telechargerDocument(doc.id)
                          : portailRHAPI.telechargerAttestationTravail(),
                        nomFichier
                      )}
                      disabled={telechargementEnCours === cle}
                      className="w-full min-h-[44px] py-2.5 bg-slate-800 hover:bg-emerald-600/20 hover:border-emerald-500/40 border border-slate-700 text-slate-200 hover:text-emerald-300 text-xs font-bold rounded-xl flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                    >
                      <Download className="w-3.5 h-3.5" />
                      {telechargementEnCours === cle ? t('Téléchargement…', 'Downloading…') : t('Télécharger', 'Download')}
                    </button>
                  ) : (
                    <div className="w-full min-h-[44px] px-3 py-2.5 bg-slate-950/60 border border-slate-800 text-slate-500 text-[11px] rounded-xl flex items-center justify-center gap-2 text-center leading-snug">
                      <ShieldQuestion className="w-3.5 h-3.5 shrink-0" />
                      <span>{raison ? dite(raison) : t('Pièce non téléchargeable', 'Document not downloadable')}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ─── ONGLET 5 : DOSSIER ADMINISTRATIF ─── */}
      {activeTab === 'profil' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-6 shadow-xl">
          <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
            <div className="w-12 h-12 shrink-0 rounded-xl bg-emerald-500/15 text-emerald-400 flex items-center justify-center">
              <UserCheck className="w-6 h-6" />
            </div>
            <div className="min-w-0">
              <h2 className="text-sm sm:text-base font-bold text-slate-100">
                {t('Dossier administratif du salarié', 'Employee administrative file')}
              </h2>
              <p className="text-xs text-slate-400">
                {t('Informations enregistrées par la DRH', 'Information recorded by HR')}
              </p>
            </div>
          </div>

          {loading && !profil && <EtatChargement t={t} />}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
            <div className="space-y-2 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
              <h4 className="font-bold uppercase text-[11px] text-emerald-400">{t('Identité & contrat', 'Identity & contract')}</h4>
              <Ligne libelle={t('Nom & prénom', 'Full name')} valeur={champsValeur(nomComplet)} gras />
              <Ligne libelle={t('Identifiant de connexion', 'Username')} valeur={champsValeur(profil?.username)} mono />
              <Ligne libelle={t('Matricule', 'Staff ID')} valeur={champsValeur(profil?.matricule)} mono />
              <Ligne libelle={t('Fonction', 'Job title')} valeur={champsValeur(profil?.poste)} gras />
              <Ligne libelle={t('Département', 'Department')} valeur={champsValeur(profil?.departement)} />
              <Ligne libelle={t('Agence', 'Office')} valeur={champsValeur(profil?.agence)} />
              <Ligne libelle={t('Type de contrat', 'Contract type')} valeur={champsValeur(profil?.statut_contrat)} gras />
              <Ligne libelle={t('Date d’embauche', 'Hire date')} valeur={enLettres(profil?.date_embauche)} mono />
            </div>

            <div className="space-y-2 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
              <h4 className="font-bold uppercase text-[11px] text-cyan-400">
                {t('Protection sociale & coordonnées', 'Social cover & contact details')}
              </h4>
              <Ligne libelle={t('N° affiliation CNPS', 'Social security number')} valeur={champsValeur(profil?.cnps_matricule)} mono />
              <Ligne libelle={t('Couverture médicale', 'Health cover')} valeur={champsValeur(profil?.couverture_sociale)} />
              <Ligne libelle={t('Compte bancaire', 'Bank account')} valeur={champsValeur(profil?.compte_bancaire)} />
              <Ligne libelle={t('E-mail professionnel', 'Work email')} valeur={champsValeur(profil?.email || (user as any)?.email)} mono />
              <Ligne libelle={t('Téléphone', 'Phone')} valeur={champsValeur(profil?.phone)} mono />
              <Ligne libelle={t('Solde de congés', 'Leave balance')} valeur={`${profil?.solde_conges ?? '—'} ${t('jours ouvrables', 'working days')}`} />
              <p className="text-[11px] text-slate-500 leading-relaxed pt-2 border-t border-slate-800">
                {t(
                  'Le numéro CNPS, la mutuelle et le RIB ne sont pas stockés dans le dossier RH : ils restent « Non renseigné » tant que la DRH ne les a pas saisis. Aucun valeur de complaisance n’est affichée sur un document social.',
                  'The social security number, health cover and bank details are not stored in the HR file: they stay “Not provided” until HR records them. No placeholder value is ever shown on a social document.'
                )}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ─── MODALE : NOUVELLE DEMANDE ─── */}
      {modalOuvert && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-end sm:items-center justify-center p-0 sm:p-4"
          role="dialog"
          aria-modal="true"
          aria-label={t('Nouvelle demande de congé', 'New leave request')}
        >
          <div className="bg-slate-900 border border-emerald-500/40 rounded-t-3xl sm:rounded-3xl p-5 sm:p-8 w-full max-w-lg shadow-2xl space-y-5 max-h-[92vh] overflow-y-auto">
            <div className="flex items-center justify-between gap-3 border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2 min-w-0">
                <Calendar className="w-5 h-5 text-emerald-400 shrink-0" />
                <h2 className="text-sm sm:text-base font-bold text-slate-100">
                  {t('Nouvelle demande de congé', 'New leave request')}
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setModalOuvert(false)}
                className="min-h-[44px] min-w-[44px] p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl flex items-center justify-center"
                aria-label={t('Fermer', 'Close')}
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={soumettreDemande} className="space-y-4">
              <div>
                <label htmlFor="type-conge" className="block text-xs font-bold text-slate-300 uppercase mb-1">
                  {t('Type d’absence', 'Leave type')}
                </label>
                <select
                  id="type-conge"
                  value={typeChoisi}
                  onChange={(e) => setTypeChoisi(e.target.value)}
                  className={inputCls}
                >
                  {Object.entries(TYPES_CONGE).map(([valeur, lib]) => (
                    <option key={valeur} value={valeur}>{dite(lib)}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label htmlFor="debut" className="block text-xs font-bold text-slate-300 uppercase mb-1">
                    {t('Date de début', 'Start date')}
                  </label>
                  <input id="debut" type="date" required value={dateDebut} onChange={(e) => setDateDebut(e.target.value)} className={inputCls} />
                </div>
                <div>
                  <label htmlFor="fin" className="block text-xs font-bold text-slate-300 uppercase mb-1">
                    {t('Date de fin', 'End date')}
                  </label>
                  <input id="fin" type="date" required value={dateFin} onChange={(e) => setDateFin(e.target.value)} min={dateDebut || undefined} className={inputCls} />
                </div>
              </div>

              {joursEstimes !== null && (
                <p className="text-[11px] text-slate-400">
                  {t(
                    `Estimation : ${joursEstimes} jour(s) ouvrable(s). Le décompte définitif est calculé à l’enregistrement.`,
                    `Estimate: ${joursEstimes} working day(s). The final count is computed when the request is saved.`
                  )}
                </p>
              )}

              <div>
                <label htmlFor="motif" className="block text-xs font-bold text-slate-300 uppercase mb-1">
                  {t('Motif (facultatif)', 'Reason (optional)')}
                </label>
                <textarea
                  id="motif"
                  rows={3}
                  value={motif}
                  onChange={(e) => setMotif(e.target.value)}
                  placeholder={t('Précisez le contexte de votre demande…', 'Describe the context of your request…')}
                  className={`${inputCls} resize-y`}
                />
              </div>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setModalOuvert(false)}
                  className="min-h-[44px] px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold transition-all"
                >
                  {t('Annuler', 'Cancel')}
                </button>
                <button
                  type="submit"
                  disabled={envoi}
                  className="min-h-[44px] px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-black shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-60"
                >
                  {envoi ? t('Envoi en cours…', 'Submitting…') : t('Soumettre la demande', 'Submit request')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Sous-composants d'affichage ─────────────────────────────────────────────

function Ligne({ libelle, valeur, mono, gras, classe = '' }: {
  libelle: string;
  valeur: React.ReactNode;
  mono?: boolean;
  gras?: boolean;
  classe?: string;
}) {
  return (
    <div className="flex items-start justify-between gap-3 py-1 border-b border-slate-800/70 last:border-0">
      <span className="text-slate-400 shrink-0">{libelle}</span>
      <span className={`text-right break-words min-w-0 ${mono ? 'font-mono' : ''} ${gras ? 'font-bold' : ''} ${classe || 'text-slate-200'}`}>
        {valeur}
      </span>
    </div>
  );
}

function EtatChargement({ t }: { t: (fr: string, en: string) => string }) {
  return (
    <div className="p-8 text-center text-xs text-slate-500 flex items-center justify-center gap-2">
      <RefreshCw className="w-4 h-4 animate-spin" />
      <span>{t('Chargement de vos données RH…', 'Loading your HR data…')}</span>
    </div>
  );
}

function EtatVide({ icone: Icone, titre, texte }: {
  icone: typeof Inbox;
  titre: string;
  texte: string;
}) {
  return (
    <div className="p-8 sm:p-10 text-center bg-slate-900/40 rounded-2xl border border-slate-800">
      <div className="w-12 h-12 mx-auto rounded-2xl bg-slate-800/80 border border-slate-700 flex items-center justify-center mb-3">
        <Icone className="w-6 h-6 text-slate-500" />
      </div>
      <p className="text-sm font-bold text-slate-300">{titre}</p>
      <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto leading-relaxed">{texte}</p>
    </div>
  );
}
