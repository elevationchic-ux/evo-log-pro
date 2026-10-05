'use client';

// Écran « Douane & Circuits CAMCIS » (vue du module Port Operations).
//
// Ce qui a été retiré et pourquoi (règle produit « aucune donnée factice ») :
//  - le numéro de DUM par défaut « DUM-2026-IM4-8842 » et la valeur CIF figée
//    à 35 000 000 XAF étaient inventés dans le composant ;
//  - l'ancienne passerelle affichait un circuit de contrôle « calculé » et un
//    plafond de caution (500 M, dossiers DOS-2026-xxxx) codés en dur : le
//    circuit douanier est un acte à valeur légale, l'ERP ne doit PAS le
//    simuler. Ces trois endpoints renvoyaient donc un 501 = écran mort.
//
// Approche honnête : l'ERP devient le REGISTRE où le déclarant enregistre ce
// que la DGD/CAMCIS lui a RÉELLEMENT notifié (circuit, accusé de
// télétransmission, quittance) et suit son cautionnement. Toutes les valeurs
// affichées viennent des tables cautions_douanieres / dum_customs_records ;
// tant que rien n'est saisi, l'écran dit « non enregistré », jamais un chiffre
// par défaut.
//
// Teinte : sky #0EA5E9 = identité du module Port Operations (modulePalette).
// Les pastilles VERT/BLEU/JAUNE/ROUGE restent sémantiques (couleur du circuit
// notifié), elles ne suivent pas la couleur du module.

import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldAlert, CheckCircle2, AlertTriangle, XCircle, Search,
  RefreshCw, Send, Plus, Landmark, Clock, ArrowUpRight, X, Save,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

interface Resultat {
  numero_dum: string;
  systeme: string;
  circuit: string | null;
  statut_recevabilite: string | null;
  date_attribution: string | null;
  description: string | null;
  delai_traitement_estime: string | null;
  inspecteur_assigne: string | null;
  quittance_tresor_emise: boolean;
  numero_quittance: string | null;
  teletransmis_le?: string | null;
  numero_accuse_camcis?: string | null;
  montant_garanti_xaf?: number;
  apure?: boolean;
}
interface Statut {
  banque_cautionnaire: string | null;
  nb_cautions_actives: number;
  plafond_autorise_xaf: number;
  montant_engage_xaf: number;
  disponible_xaf: number;
  taux_utilisation_pourcent: number;
  alerte_depassement: boolean;
  dossiers_en_cours: Resultat[];
}
interface Caution {
  id: number;
  reference: string;
  banque_cautionnaire: string | null;
  formule: string | null;
  plafond_autorise_xaf: number;
  devise: string;
  statut: string;
}

const NAS = '';

export default function RealCustomsPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const loc = lang === 'en' ? 'en-GB' : 'fr-FR';

  const [statut, setStatut] = useState<Statut | null>(null);
  const [cautions, setCautions] = useState<Caution[]>([]);
  const [dossiers, setDossiers] = useState<Resultat[]>([]);
  const [erreur, setErreur] = useState('');
  const [chargement, setChargement] = useState(false);

  const [dumInput, setDumInput] = useState('');
  const [recherche, setRecherche] = useState(false);
  const [resultat, setResultat] = useState<Resultat | null>(null);
  const [introouve, setIntroouve] = useState(false);

  const [modalCaution, setModalCaution] = useState(false);
  const [formCaution, setFormCaution] = useState({ reference: '', banque_cautionnaire: '', formule: 'Garantie globale', plafond: '', devise: 'XAF' });
  const [modalCircuit, setModalCircuit] = useState(false);
  const [formCircuit, setFormCircuit] = useState({ circuit: 'VERT', inspecteur: '', recevabilite: '', delai: '', description: '' });
  const [formAccuse, setFormAccuse] = useState('');
  const [enregistrer, setEnregistrer] = useState(false);

  const nb = (v: number | null | undefined, dec = 0) =>
    v === null || v === undefined ? NAS : new Intl.NumberFormat(loc, { maximumFractionDigits: dec }).format(Number(v));

  const dateCourte = (iso: string | null | undefined) => {
    if (!iso) return NAS;
    const d = new Date(iso);
    return isNaN(d.getTime()) ? String(iso) : d.toLocaleDateString(loc, { day: '2-digit', month: 'short', year: 'numeric' });
  };

  const detailErreur = (err: any, fallback: string) =>
    err?.response?.data?.detail || fallback;

  const charger = useCallback(async () => {
    setChargement(true);
    setErreur('');
    const echecs: string[] = [];
    try {
      const s = await apiClient.get('/api/v1/real-customs/cautions/statut');
      setStatut(s.data as Statut);
    } catch { echecs.push('cautions'); }
    try {
      const c = await apiClient.get('/api/v1/real-customs/cautions');
      setCautions(Array.isArray(c.data?.data) ? c.data.data : []);
    } catch { echecs.push('cautions-list'); }
    try {
      const d = await apiClient.get('/api/v1/real-customs/dossiers');
      setDossiers(Array.isArray(d.data?.data) ? d.data.data : []);
    } catch { echecs.push('dossiers'); }
    if (echecs.length) setErreur(t(`Données douanières incomplètes (${echecs.join(', ')}).`, `Customs data incomplete (${echecs.join(', ')}).`));
    setChargement(false);
  }, [t, lang]);

  useEffect(() => { charger(); }, [charger]);

  const rechercher = async () => {
    const numero = dumInput.trim();
    if (!numero) { setResultat(null); setIntroouve(false); return; }
    setRecherche(true); setIntroouve(false); setResultat(null);
    try {
      const res = await apiClient.get(`/api/v1/real-customs/camcis/circuits/${encodeURIComponent(numero)}`);
      const data = res.data as Resultat & { enregistre?: boolean };
      if (data.enregistre === false) {
        setResultat(data); setIntroouve(true);
      } else {
        setResultat(data);
      }
    } catch (err: any) {
      setErreur(detailErreur(err, t('Recherche impossible.', 'Lookup failed.')));
    } finally {
      setRecherche(false);
    }
  };

  const creerCaution = async () => {
    if (!formCaution.plafond || Number(formCaution.plafond) <= 0) {
      setErreur(t('Indiquez un plafond de garantie réel.', 'Enter a real guarantee ceiling.')); return;
    }
    setEnregistrer(true);
    try {
      await apiClient.post('/api/v1/real-customs/cautions', {
        reference: formCaution.reference || undefined,
        banque_cautionnaire: formCaution.banque_cautionnaire || null,
        formule: formCaution.formule || null,
        plafond_autorise_xaf: Number(formCaution.plafond),
        devise: formCaution.devise || 'XAF',
      });
      setModalCaution(false);
      setFormCaution({ reference: '', banque_cautionnaire: '', formule: 'Garantie globale', plafond: '', devise: 'XAF' });
      await charger();
    } catch (err: any) {
      setErreur(detailErreur(err, t('Enregistrement de la caution impossible.', 'Failed to record caution.')));
    } finally { setEnregistrer(false); }
  };

  const enregistrerCircuit = async () => {
    if (!dumInput.trim()) { setErreur(t('Numéro de DUM requis.', 'DUM number required.')); return; }
    setEnregistrer(true);
    try {
      await apiClient.post('/api/v1/real-customs/camcis/circuits', {
        numero_dum: dumInput.trim(),
        circuit: formCircuit.circuit,
        inspecteur_assigne: formCircuit.inspecteur || null,
        statut_recevabilite: formCircuit.recevabilite || null,
        delai_traitement_estime: formCircuit.delai || null,
        description: formCircuit.description || null,
      });
      setModalCircuit(false);
      await rechercher();
      await charger();
    } catch (err: any) {
      setErreur(detailErreur(err, t('Enregistrement du circuit impossible.', 'Failed to record circuit.')));
    } finally { setEnregistrer(false); }
  };

  const teletransmettre = async () => {
    if (!dumInput.trim()) { setErreur(t('Numéro de DUM requis.', 'DUM number required.')); return; }
    setEnregistrer(true);
    try {
      await apiClient.post('/api/v1/real-customs/camcis/teletransmettre', {
        numero_dum: dumInput.trim(),
        numero_accuse_camcis: formAccuse.trim() || null,
      });
      setFormAccuse('');
      await rechercher();
      await charger();
    } catch (err: any) {
      setErreur(detailErreur(err, t('Journalisation de la télétransmission impossible.', 'Failed to log teletransmission.')));
    } finally { setEnregistrer(false); }
  };

  const apurer = async (numero: string) => {
    const quittance = window.prompt(t(
      `Numéro de quittance de sortie réellement émis pour ${numero} (laisser vide si non disponible) :`,
      `Actual exit quittance number issued for ${numero} (leave empty if unavailable):`
    ));
    if (quittance === null) return;
    setEnregistrer(true);
    try {
      await apiClient.post('/api/v1/real-customs/cautions/apurer', {
        numero_dum: numero,
        numero_quittance: quittance.trim() || null,
      });
      await charger();
      if (numero === dumInput.trim()) await rechercher();
    } catch (err: any) {
      setErreur(detailErreur(err, t('Apurement impossible.', 'Discharge failed.')));
    } finally { setEnregistrer(false); }
  };

  const badgeCircuit = (c: string | null) => {
    switch (c) {
      case 'VERT': return { cls: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/40', icon: CheckCircle2, lib: t('Circuit VERT · Bon à Enlever immédiat', 'GREEN circuit · Immediate release') };
      case 'BLEU': return { cls: 'bg-blue-500/15 text-blue-400 border-blue-500/40', icon: CheckCircle2, lib: t('Circuit BLEU · Audit a posteriori', 'BLUE circuit · Post-clearance audit') };
      case 'JAUNE': return { cls: 'bg-amber-500/15 text-amber-400 border-amber-500/40', icon: AlertTriangle, lib: t('Circuit JAUNE · Examen documentaire', 'AMBER circuit · Documentary check') };
      case 'ROUGE': return { cls: 'bg-rose-500/15 text-rose-400 border-rose-500/40', icon: XCircle, lib: t('Circuit ROUGE · Visite physique', 'RED circuit · Physical inspection') };
      default: return null;
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-bold uppercase tracking-wider mb-2">
            <ShieldAlert className="w-3.5 h-3.5" /> {t('Cameroun · Registre CAMCIS & GUCE', 'Cameroon · CAMCIS & GUCE register')}
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">{t('Douane & Circuits CAMCIS', 'Customs & CAMCIS circuits')}</h1>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            {t('Registre local des résultats notifiés par la DGD et suivi du cautionnement. L\'ERP n\'émet aucune valeur : il enregistre ce que le guichet douanier a réellement communiqué.',
              'Local register of results notified by the customs authority and guarantee tracking. The ERP invents nothing: it stores what the customs counter actually communicated.')}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button onClick={charger} disabled={chargement}
            className="min-h-[44px] flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold active:scale-95">
            <RefreshCw className={`w-3.5 h-3.5 ${chargement ? 'animate-spin' : ''}`} /> {t('Actualiser', 'Refresh')}
          </button>
          <button onClick={() => setModalCaution(true)}
            className="min-h-[44px] flex items-center gap-2 px-4 py-2 rounded-2xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold active:scale-95">
            <Plus className="w-3.5 h-3.5" /> {t('Nouvelle caution', 'New guarantee')}
          </button>
        </div>
      </div>

      {erreur && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-semibold flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" /> {erreur}
        </div>
      )}

      {/* Supervision caution */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">{t('Caution souscrite', 'Guarantee ceiling')}</span>
            <Landmark className="w-4 h-4 text-sky-400" />
          </div>
          <p className="text-xl font-black text-white mt-2">{nb(statut?.plafond_autorise_xaf)} XAF</p>
          <p className="text-[11px] text-slate-400 mt-1 truncate" title={statut?.banque_cautionnaire || ''}>
            {statut?.banque_cautionnaire || t('Aucune caution active enregistrée', 'No active guarantee recorded')}
          </p>
        </div>
        <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">{t('Montant engagé', 'Amount committed')}</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-xl font-black text-amber-400 mt-2">{nb(statut?.montant_engage_xaf)} XAF</p>
          <p className="text-[11px] text-slate-400 mt-1">{t(`Utilisation : ${nb(statut?.taux_utilisation_pourcent, 1)} %`, `Utilisation: ${nb(statut?.taux_utilisation_pourcent, 1)} %`)}</p>
        </div>
        <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">{t('Disponible', 'Available')}</span>
            <ArrowUpRight className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-xl font-black text-cyan-400 mt-2">{nb(statut?.disponible_xaf)} XAF</p>
          <p className="text-[11px] text-slate-400 mt-1">{t('Crédit d\'enlèvement restant', 'Remaining removal credit')}</p>
        </div>
        <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">{t('Seuil de dépassement', 'Overlimit threshold')}</span>
            <AlertTriangle className={`w-4 h-4 ${statut?.alerte_depassement ? 'text-rose-400' : 'text-emerald-400'}`} />
          </div>
          <p className={`text-xl font-black mt-2 ${statut?.alerte_depassement ? 'text-rose-400' : 'text-emerald-400'}`}>
            {statut?.alerte_depassement ? t('CRITIQUE · dépassé', 'CRITICAL · exceeded') : t('SÉCURISÉ', 'SAFE')}
          </p>
          <p className="text-[11px] text-slate-400 mt-1">{statut?.dossiers_en_cours?.length ?? 0} {t('dossier(s) en cours', 'file(s) in progress')}</p>
        </div>
      </div>

      {/* Registre des cautions */}
      <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-3xl">
        <h2 className="text-sm font-bold text-white mb-3">{t('Registre des cautions souscrites', 'Guarantee register')}</h2>
        {cautions.length === 0 ? (
          <p className="text-xs text-slate-400">{t('Aucune caution enregistrée. Saisissez le plafond réellement souscrit auprès de votre banque cautionnaire.', 'No guarantee recorded. Enter the ceiling actually underwritten with your surety bank.')}</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] text-xs">
              <thead className="text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="text-left p-2">{t('Référence', 'Reference')}</th>
                  <th className="text-left p-2">{t('Banque', 'Bank')}</th>
                  <th className="text-left p-2">{t('Formule', 'Scheme')}</th>
                  <th className="text-right p-2">{t('Plafond', 'Ceiling')}</th>
                  <th className="text-left p-2">{t('Statut', 'Status')}</th>
                </tr>
              </thead>
              <tbody>
                {cautions.map((c) => (
                  <tr key={c.id} className="border-b border-slate-800/60">
                    <td className="p-2 font-semibold text-white">{c.reference}</td>
                    <td className="p-2 text-slate-300">{c.banque_cautionnaire || NAS}</td>
                    <td className="p-2 text-slate-300">{c.formule || NAS}</td>
                    <td className="p-2 text-right text-slate-200">{nb(c.plafond_autorise_xaf)} {c.devise}</td>
                    <td className="p-2 text-slate-300">{c.statut}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Suivi d'une DUM */}
      <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-3xl space-y-4">
        <h2 className="text-sm font-bold text-white">{t('Suivi d\'une déclaration (DUM)', 'Track a declaration (DUM)')}</h2>
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
            <input type="text" value={dumInput} onChange={(e) => setDumInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && rechercher()}
              placeholder={t('Numéro de DUM (ex. relevé sur votre dossier)', 'DUM number (from your file)')}
              className="w-full min-h-[44px] bg-slate-950/60 border border-slate-800 rounded-2xl pl-11 pr-4 py-3 text-sm text-white focus:outline-none focus:border-sky-500" />
          </div>
          <div className="flex gap-2">
            <button onClick={rechercher} disabled={recherche || !dumInput.trim()}
              className="min-h-[44px] flex-1 md:flex-none px-5 py-3 rounded-2xl bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white font-bold text-xs flex items-center justify-center gap-2">
              {recherche ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />} {t('Consulter', 'Look up')}
            </button>
            <button onClick={() => { setFormCircuit({ circuit: 'VERT', inspecteur: '', recevabilite: '', delai: '', description: '' }); setModalCircuit(true); }}
              disabled={!dumInput.trim()}
              className="min-h-[44px] flex-1 md:flex-none px-5 py-3 rounded-2xl bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 font-bold text-xs flex items-center justify-center gap-2 border border-slate-700">
              <Save className="w-4 h-4" /> {t('Enregistrer le circuit notifié', 'Record notified circuit')}
            </button>
          </div>
        </div>

        {introouve && (
          <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-semibold">
            {t(`Aucun résultat n'a encore été enregistré pour ${dumInput.trim()}. Saisissez le circuit officiellement notifié par la DGD via « Enregistrer le circuit notifié ».`,
              `No result recorded yet for ${dumInput.trim()}. Enter the circuit officially notified by the customs office via "Record notified circuit".`)}
          </div>
        )}

        {resultat && !introouve && (() => {
          const b = badgeCircuit(resultat.circuit);
          const Icon = b?.icon ?? ShieldAlert;
          return (
            <div className="space-y-4 rounded-2xl bg-slate-950/40 border border-slate-800/60 p-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div>
                  <div className="text-xs text-slate-400">{t('Résultat enregistré pour', 'Recorded result for')} <span className="font-bold text-white">{resultat.numero_dum}</span></div>
                  <div className="text-[11px] text-slate-500 mt-1">{resultat.systeme} · {t('notifié le', 'notified on')} {dateCourte(resultat.date_attribution)}</div>
                </div>
                {b ? (
                  <div className={`px-4 py-2 rounded-2xl border ${b.cls} flex items-center gap-2`}>
                    <Icon className="w-5 h-5" /> <span className="text-sm font-black">{b.lib}</span>
                  </div>
                ) : <span className="text-xs text-amber-400">{t('Circuit non notifié', 'Circuit not notified')}</span>}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800/60">
                  <span className="text-[11px] text-slate-400">{t('Action requise', 'Required action')}</span>
                  <p className="text-sm font-bold text-white mt-1 break-words">{resultat.description || NAS}</p>
                  <p className="text-[11px] text-slate-400 mt-1">{t('Délai estimé', 'Est. time')}: {resultat.delai_traitement_estime || NAS}</p>
                </div>
                <div className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800/60">
                  <span className="text-[11px] text-slate-400">{t('Inspecteur assigné', 'Assigned inspector')}</span>
                  <p className="text-sm font-bold text-white mt-1 break-words">{resultat.inspecteur_assigne || NAS}</p>
                  <p className="text-[11px] text-slate-400 mt-1">{t('Recevabilité', 'Receivability')}: {resultat.statut_recevabilite || NAS}</p>
                </div>
                <div className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800/60">
                  <span className="text-[11px] text-slate-400">{t('Télétransmission', 'Teletransmission')}</span>
                  <p className="text-sm font-bold text-white mt-1 break-words">{resultat.numero_accuse_camcis || t('Non attestée', 'Not logged')}</p>
                  <p className="text-[11px] text-slate-400 mt-1">
                    {resultat.apure
                      ? <span className="text-emerald-400 font-bold">{t('Caution apurée', 'Guarantee discharged')}</span>
                      : <span className="text-amber-400 font-bold">{t('Caution en cours', 'Guarantee open')}</span>}
                  </p>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-2 pt-2">
                <div className="flex flex-1 gap-2">
                  <input value={formAccuse} onChange={(e) => setFormAccuse(e.target.value)}
                    placeholder={t("N° d'accuse réellement renvoyé par CAMCIS", 'Actual CAMCIS acknowledgement number')}
                    className="flex-1 min-w-0 bg-slate-950/60 border border-slate-800 rounded-2xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500" />
                  <button onClick={teletransmettre} disabled={enregistrer}
                    className="min-h-[44px] px-4 rounded-2xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-bold flex items-center gap-2">
                    <Send className="w-4 h-4" /> {t('Attester', 'Log')}
                  </button>
                </div>
                {!resultat.apure && (
                  <button onClick={() => apurer(resultat.numero_dum)} disabled={enregistrer}
                    className="min-h-[44px] px-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" /> {t('Apurer la caution', 'Discharge guarantee')}
                  </button>
                )}
              </div>
            </div>
          );
        })()}
      </div>

      {/* Dossiers suivis */}
      <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-3xl">
        <h2 className="text-sm font-bold text-white mb-3">{t('DUM suivies par l\'entreprise', 'DUMs tracked by the company')}</h2>
        {dossiers.length === 0 ? (
          <p className="text-xs text-slate-400">{t('Aucune DUM enregistrée. Recherchez un numéro puis enregistrez le résultat notifié par la douane.', 'No DUM recorded. Look up a number then record the result notified by customs.')}</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[820px] text-xs">
              <thead className="text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="text-left p-2">DUM</th>
                  <th className="text-left p-2">{t('Circuit', 'Circuit')}</th>
                  <th className="text-left p-2">{t('Bureau', 'Office')}</th>
                  <th className="text-left p-2">{t('Accusé', 'Ack. number')}</th>
                  <th className="text-right p-2">{t('Garanti', 'Guaranteed')}</th>
                  <th className="text-left p-2">{t('Apurement', 'Discharge')}</th>
                </tr>
              </thead>
              <tbody>
                {dossiers.map((d) => {
                  const b = badgeCircuit(d.circuit);
                  return (
                    <tr key={d.numero_dum} className="border-b border-slate-800/60">
                      <td className="p-2 font-semibold text-white">{d.numero_dum}</td>
                      <td className="p-2">{b ? <span className={`px-2 py-0.5 rounded-lg border ${b.cls}`}>{d.circuit}</span> : <span className="text-slate-500">{NAS}</span>}</td>
                      <td className="p-2 text-slate-300">{d.systeme}</td>
                      <td className="p-2 text-slate-300 break-words">{d.numero_accuse_camcis || NAS}</td>
                      <td className="p-2 text-right text-slate-200">{nb(d.montant_garanti_xaf)}</td>
                      <td className="p-2">{d.apure ? <span className="text-emerald-400">{t('Apurée', 'Discharged')}</span> : <span className="text-amber-400">{t('En cours', 'Open')}</span>}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal nouvelle caution */}
      {modalCaution && (
        <div className="fixed inset-0 z-[100] bg-black/70 flex items-center justify-center p-4" onClick={() => setModalCaution(false)}>
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white">{t('Enregistrer une caution douanière', 'Record a customs guarantee')}</h3>
              <button onClick={() => setModalCaution(false)}><X className="w-4 h-4 text-slate-400" /></button>
            </div>
            <Field label={t('Référence (optionnelle)', 'Reference (optional)')} value={formCaution.reference} onChange={(v) => setFormCaution({ ...formCaution, reference: v })} placeholder="CAU-2026-0001" />
            <Field label={t('Banque cautionnaire', 'Surety bank')} value={formCaution.banque_cautionnaire} onChange={(v) => setFormCaution({ ...formCaution, banque_cautionnaire: v })} />
            <Field label={t('Formule', 'Scheme')} value={formCaution.formule} onChange={(v) => setFormCaution({ ...formCaution, formule: v })} />
            <Field label={t('Plafond autorisé (XAF)', 'Authorized ceiling (XAF)')} value={formCaution.plafond} onChange={(v) => setFormCaution({ ...formCaution, plafond: v })} type="number" />
            <button onClick={creerCaution} disabled={enregistrer}
              className="min-h-[44px] w-full rounded-2xl bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white text-xs font-bold">
              {t('Enregistrer', 'Save')}
            </button>
          </div>
        </div>
      )}

      {/* Modal enregistrement circuit */}
      {modalCircuit && (
        <div className="fixed inset-0 z-[100] bg-black/70 flex items-center justify-center p-4" onClick={() => setModalCircuit(false)}>
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white">{t('Circuit notifié par la DGD', 'Circuit notified by customs')}</h3>
              <button onClick={() => setModalCircuit(false)}><X className="w-4 h-4 text-slate-400" /></button>
            </div>
            <div>
              <label className="text-[11px] text-slate-400">{t('Circuit attribué', 'Assigned circuit')}</label>
              <select value={formCircuit.circuit} onChange={(e) => setFormCircuit({ ...formCircuit, circuit: e.target.value })}
                className="w-full mt-1 min-h-[44px] bg-slate-950/60 border border-slate-800 rounded-2xl px-3 py-2 text-sm text-white focus:outline-none focus:border-sky-500">
                {['VERT', 'BLEU', 'JAUNE', 'ROUGE'].map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <Field label={t('Inspecteur assigné', 'Assigned inspector')} value={formCircuit.inspecteur} onChange={(v) => setFormCircuit({ ...formCircuit, inspecteur: v })} />
            <Field label={t('Statut de recevabilité', 'Receivability status')} value={formCircuit.recevabilite} onChange={(v) => setFormCircuit({ ...formCircuit, recevabilite: v })} />
            <Field label={t('Délai estimé notifié', 'Notified estimated time')} value={formCircuit.delai} onChange={(v) => setFormCircuit({ ...formCircuit, delai: v })} />
            <Field label={t('Description / action requise', 'Description / required action')} value={formCircuit.description} onChange={(v) => setFormCircuit({ ...formCircuit, description: v })} />
            <button onClick={enregistrerCircuit} disabled={enregistrer}
              className="min-h-[44px] w-full rounded-2xl bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white text-xs font-bold">
              {t('Enregistrer le résultat', 'Save result')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, value, onChange, placeholder = '', type = 'text' }: {
  label: string; value: string; onChange: (v: string) => void; placeholder?: string; type?: string;
}) {
  return (
    <div>
      <label className="text-[11px] text-slate-400">{label}</label>
      <input type={type} value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)}
        className="w-full mt-1 min-h-[44px] bg-slate-950/60 border border-slate-800 rounded-2xl px-3 py-2 text-sm text-white focus:outline-none focus:border-sky-500" />
    </div>
  );
}
