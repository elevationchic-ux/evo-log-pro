'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldCheck, FileText, CheckCircle2,
  AlertTriangle, Calendar, Loader2
} from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}
function authH(): Record<string, string> {
  const token = getToken();
  return { ...(token ? { Authorization: `Bearer ${token}` } : {}), 'Content-Type': 'application/json' };
}

interface TVADeclaration {
  periode: string;
  tva_collectee: number;
  ca_taxable: number;
  tva_deductible_immo: number;
  tva_deductible_charges: number;
  credit_tva_anterieur: number;
  operations_exonerees: number;
  net_tva_payer: number;
  date_limite_paiement: string;
  statut: string;
}

interface ISDeclaration {
  exercice: number;
  base_imposable: number;
  is_brut: number;
  taux_is: number;
  minimum_perception: number;
  is_exigible: number;
  acomptes_verses: number;
  solde_is: number;
  prochaine_echeance: string;
  statut: string;
}

interface DIPEData {
  periode: string;
  nb_employes: number;
  masse_salariale_brute: number;
  ircm_verse: number;
  cnps_patron: number;
  cnps_employe: number;
  fne_verse: number;
  statut: string;
}

export default function ComptabiliteOhadaTaxPackageCemac() {
  const [tab, setTab] = useState<'TVA' | 'IS' | 'DIPE' | 'LIASSE'>('TVA');
  const [tvaData, setTvaData] = useState<TVADeclaration | null>(null);
  const [isData, setIsData] = useState<ISDeclaration | null>(null);
  const [dipeData, setDipeData] = useState<DIPEData | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentPeriode = new Date().toISOString().slice(0, 7);
  const currentExercice = new Date().getFullYear();

  const loadTVA = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/comptabilite-avance/declarations-tva?periode=${currentPeriode}`, { headers: authH() });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        setError(body.detail || `Erreur ${res.status}`);
        setTvaData(null);
      } else {
        setTvaData(await res.json());
      }
    } catch {
      setError('Impossible de contacter le serveur.');
    } finally { setLoading(false); }
  }, [currentPeriode]);

  const loadIS = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/comptabilite-avance/declarations-is?annee=${currentExercice}`, { headers: authH() });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        setError(body.detail || `Erreur ${res.status}`);
        setIsData(null);
      } else {
        setIsData(await res.json());
      }
    } catch {
      setError('Impossible de contacter le serveur.');
    } finally { setLoading(false); }
  }, [currentExercice]);

  const loadDIPE = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/rh-avance/dipe-mensuel?periode=${currentPeriode}`, { headers: authH() });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        setError(body.detail || `Erreur ${res.status}`);
        setDipeData(null);
      } else {
        setDipeData(await res.json());
      }
    } catch {
      setError('Impossible de contacter le serveur.');
    } finally { setLoading(false); }
  }, [currentPeriode]);

  useEffect(() => {
    if (tab === 'TVA') loadTVA();
    else if (tab === 'IS') loadIS();
    else if (tab === 'DIPE') loadDIPE();
    else { setLoading(false); setError(null); }
  }, [tab, loadTVA, loadIS, loadDIPE]);

  const validerTVA = async () => {
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/comptabilite-avance/declarations-tva/valider`, {
        method: 'POST',
        headers: authH(),
        body: JSON.stringify({ periode: currentPeriode }),
      });
      const d = await res.json().catch(() => ({}));
      if (res.ok) {
        toast.success(d.message || 'Déclaration TVA enregistrée.');
        await loadTVA();
      } else {
        toast.error(d.detail || 'Erreur lors de la validation.');
      }
    } catch {
      toast.error('Erreur réseau.');
    } finally { setSubmitting(false); }
  };

  // Derived TVA values
  const tvaCollectee = tvaData?.tva_collectee ?? 0;
  const caTaxable = tvaData?.ca_taxable ?? 0;
  const tvaDeductibleImmo = tvaData?.tva_deductible_immo ?? 0;
  const tvaDeductibleCharges = tvaData?.tva_deductible_charges ?? 0;
  const creditAnterieur = tvaData?.credit_tva_anterieur ?? 0;
  const operationsExonerees = tvaData?.operations_exonerees ?? 0;
  const netTVA = tvaData?.net_tva_payer ?? (tvaCollectee - tvaDeductibleImmo - tvaDeductibleCharges + creditAnterieur);
  const dateLimite = tvaData?.date_limite_paiement ?? `${currentPeriode}-15`;

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
              Fiscalité DGI Cameroun & Zone CEMAC
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <ShieldCheck className="w-8 h-8 text-violet-400" />
            Liasse Fiscale CEMAC & Déclarations
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            TVA (19.25%), IS (30%), DIPE. Données agrégées depuis le grand livre réel.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {[
          { key: 'TVA', label: 'Déclaration TVA (19.25%)' },
          { key: 'IS', label: 'Impôt sur les Sociétés (IS)' },
          { key: 'DIPE', label: 'État DIPE (salaires)' },
          { key: 'LIASSE', label: 'Liasse Fiscale' },
        ].map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key as typeof tab)}
            className={`px-4 py-2.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all border ${
              tab === t.key
                ? 'bg-violet-600 text-white border-violet-500 shadow-md shadow-violet-600/30'
                : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:bg-slate-800 hover:text-slate-200'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-3 px-4 py-3 bg-red-950/60 border border-red-800/40 rounded-2xl text-xs text-red-300">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center gap-2 py-8 text-slate-400 text-xs">
          <Loader2 className="w-5 h-5 animate-spin" /> Chargement…
        </div>
      )}

      {/* ─── TVA ─── */}
      {tab === 'TVA' && !loading && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-base font-black text-slate-100">Déclaration Mensuelle de TVA — {currentPeriode}</h3>
              <p className="text-xs text-slate-400 font-mono">Taux normal : 17.5% + CAC 10% = 19.25% | Source : Grand Livre</p>
            </div>
            <span className={`font-mono text-xs font-bold px-3 py-1 rounded-xl border ${
              netTVA > 0 ? 'text-red-400 bg-red-500/10 border-red-500/20' : 'text-blue-400 bg-blue-500/10 border-blue-500/20'
            }`}>
              {netTVA > 0 ? 'Net à Payer' : netTVA < 0 ? 'Crédit' : 'NULL'} : {Math.abs(netTVA).toLocaleString('fr-FR')} XAF
            </span>
          </div>

          {tvaData ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs font-mono">
                <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between text-slate-200 font-sans font-bold border-b border-slate-800 pb-2">
                    <span>1. TVA COLLECTÉE (443x)</span>
                    <span className="text-violet-400">{tvaCollectee.toLocaleString('fr-FR')} XAF</span>
                  </div>
                  <div className="flex justify-between text-slate-400"><span>CA taxable HT (comptes 70x)</span><span className="text-slate-200">{caTaxable.toLocaleString('fr-FR')} XAF</span></div>
                  <div className="flex justify-between text-slate-400"><span>Opérations exonérées</span><span className="text-slate-200">{operationsExonerees.toLocaleString('fr-FR')} XAF</span></div>
                </div>
                <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between text-slate-200 font-sans font-bold border-b border-slate-800 pb-2">
                    <span>2. TVA DÉDUCTIBLE (445x)</span>
                    <span className="text-emerald-400">{(tvaDeductibleImmo + tvaDeductibleCharges).toLocaleString('fr-FR')} XAF</span>
                  </div>
                  <div className="flex justify-between text-slate-400"><span>Sur immobilisations (4452x)</span><span className="text-slate-200">{tvaDeductibleImmo.toLocaleString('fr-FR')} XAF</span></div>
                  <div className="flex justify-between text-slate-400"><span>Sur charges courantes (4451x)</span><span className="text-slate-200">{tvaDeductibleCharges.toLocaleString('fr-FR')} XAF</span></div>
                  <div className="flex justify-between text-slate-400"><span>Crédit TVA reporté antérieur</span><span className="text-slate-200">{Math.abs(creditAnterieur).toLocaleString('fr-FR')} XAF</span></div>
                </div>
              </div>

              <div className="bg-slate-950 rounded-2xl border border-slate-800 p-4 text-xs font-mono">
                <div className="flex justify-between font-bold text-slate-100 text-sm">
                  <span className="font-sans">= NET TVA À PAYER (Ligne 25 DGI)</span>
                  <span className={netTVA >= 0 ? 'text-red-400' : 'text-blue-400'}>{netTVA >= 0 ? netTVA.toLocaleString('fr-FR') : `Crédit ${Math.abs(netTVA).toLocaleString('fr-FR')}`} XAF</span>
                </div>
              </div>

              <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-amber-500/10 text-amber-400 rounded-xl">
                    <Calendar className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-slate-100 font-sans">Date limite de paiement</div>
                    <div className="text-[11px] text-slate-400 font-mono">{dateLimite}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-[11px] font-bold px-2 py-0.5 rounded ${
                    tvaData.statut === 'BROUILLON' ? 'bg-slate-800 text-slate-400' : 'bg-emerald-500/10 text-emerald-400'
                  }`}>{tvaData.statut}</span>
                  <button
                    onClick={validerTVA}
                    disabled={submitting || tvaData.statut !== 'BROUILLON'}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl font-sans flex items-center gap-2"
                  >
                    {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                    {submitting ? 'Enregistrement…' : 'Valider la déclaration'}
                  </button>
                </div>
              </div>
              <p className="text-[11px] text-slate-500 italic">
                ⚠ La transmission e-bulletin DGI n&apos;est pas intégrée. Après validation, déposez le formulaire papier ou EDI auprès de votre centre des impôts.
              </p>
            </>
          ) : (
            <div className="py-8 text-center text-slate-500 text-xs">
              Aucune donnée TVA disponible pour {currentPeriode}. Vérifiez que des écritures sont comptabilisées.
            </div>
          )}
        </div>
      )}

      {/* ─── IS ─── */}
      {tab === 'IS' && !loading && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-base font-black text-slate-100">Impôt sur les Sociétés (IS) — Exercice {currentExercice}</h3>
              <p className="text-xs text-slate-400 font-mono">Taux : 30% | Minimum de perception : 1 000 000 XAF | Source : Compte de résultat</p>
            </div>
          </div>
          {isData ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs font-mono">
              <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-3">
                <div className="text-slate-200 font-sans font-bold border-b border-slate-800 pb-2">CALCUL IS</div>
                {[
                  ['Résultat fiscal (résultat net CR)', `${isData.base_imposable.toLocaleString('fr-FR')} XAF`],
                  [`IS Brut (${isData.taux_is}%)`, `${isData.is_brut.toLocaleString('fr-FR')} XAF`],
                  ['Minimum de perception (CGI Art. 69)', `${isData.minimum_perception.toLocaleString('fr-FR')} XAF`],
                  ['IS Exigible (max)', `${isData.is_exigible.toLocaleString('fr-FR')} XAF`],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between text-slate-400"><span>{k}</span><span className="text-slate-200 font-bold">{v}</span></div>
                ))}
              </div>
              <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-3">
                <div className="text-slate-200 font-sans font-bold border-b border-slate-800 pb-2">ACOMPTES & SOLDE</div>
                {[
                  ['Acomptes versés', `${isData.acomptes_verses.toLocaleString('fr-FR')} XAF`],
                  ['Solde IS', `${isData.solde_is.toLocaleString('fr-FR')} XAF`],
                  ['Prochaine échéance', isData.prochaine_echeance],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between text-slate-400"><span>{k}</span><span className="text-slate-200">{v}</span></div>
                ))}
                <div className="flex justify-between text-slate-400 pt-2 border-t border-slate-800">
                  <span>Statut</span><span className="text-slate-200 font-bold">{isData.statut}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="py-8 text-center text-slate-500 text-xs">
              Compte de résultat non établi pour {currentExercice}. Générez-le d&apos;abord dans États Financiers.
            </div>
          )}
        </div>
      )}

      {/* ─── DIPE ─── */}
      {tab === 'DIPE' && !loading && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-base font-black text-slate-100">DIPE — {currentPeriode}</h3>
              <p className="text-xs text-slate-400 font-mono">Document d&apos;Information sur le Personnel Employé (DGI / CNPS Cameroun)</p>
            </div>
          </div>
          {dipeData && dipeData.statut !== 'AUCUNE_DONNEE' ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
              {[
                { label: 'Effectif', value: `${dipeData.nb_employes} salariés`, color: 'text-slate-100' },
                { label: 'Masse Salariale Brute', value: `${dipeData.masse_salariale_brute.toLocaleString('fr-FR')} XAF`, color: 'text-violet-400' },
                { label: 'IRCM retenu (DGI)', value: `${dipeData.ircm_verse.toLocaleString('fr-FR')} XAF`, color: 'text-amber-400' },
                { label: 'CNPS Part Patronale', value: `${dipeData.cnps_patron.toLocaleString('fr-FR')} XAF`, color: 'text-blue-400' },
                { label: 'CNPS Part Salariale', value: `${dipeData.cnps_employe.toLocaleString('fr-FR')} XAF`, color: 'text-emerald-400' },
                { label: 'FNE (1%)', value: `${dipeData.fne_verse.toLocaleString('fr-FR')} XAF`, color: 'text-slate-300' },
              ].map(k => (
                <div key={k.label} className="bg-slate-950 p-4 rounded-2xl border border-slate-800">
                  <div className="text-[11px] text-slate-400 mb-2 uppercase tracking-wider font-sans">{k.label}</div>
                  <div className={`text-lg font-black ${k.color}`}>{k.value}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-slate-500 text-xs">
              Aucune fiche de paie enregistrée pour {currentPeriode}. Saisissez la paie dans le module RH pour alimenter le DIPE.
            </div>
          )}
        </div>
      )}

      {/* ─── LIASSE ─── */}
      {tab === 'LIASSE' && !loading && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
          <div className="border-b border-slate-800 pb-3">
            <h3 className="text-base font-black text-slate-100">Liasse Fiscale &amp; Statistique SYSCOHADA — Exercice {currentExercice}</h3>
            <p className="text-xs text-slate-400 font-mono">Tableaux officiels DGI (formats 1 à 36)</p>
          </div>
          <div className="flex items-start gap-3 px-4 py-5 bg-slate-950 border border-slate-800 rounded-2xl">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="text-xs text-slate-300 space-y-2 font-sans">
              <p className="font-bold text-amber-300">Génération automatique de la liasse non implémentée.</p>
              <p>
                Les tableaux de la liasse fiscale (SIG, TAFIRE, annexes, tableaux 20, etc.) necessitent un moteur de génération
                au format officiel DGI (EDI/XML ou PDF normalisé). Ce moteur n&apos;est pas encore disponible.
              </p>
              <p>
                En attendant, les données sources sont accessibles :
              </p>
              <ul className="list-disc list-inside space-y-1 text-slate-400 ml-2">
                <li>Bilan → page <strong>États Financiers</strong> (Actif/Passif)</li>
                <li>Compte de Résultat → page <strong>États Financiers</strong> (produits/charges)</li>
                <li>Grand Livre → page <strong>Grand Livre</strong></li>
                <li>Balance → page <strong>Balance</strong></li>
              </ul>
              <p className="text-slate-500 italic">Export manuel vers formulaire DGI papier ou logiciel de télédéclaration à partir de ces états.</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
            <FileText className="w-4 h-4" />
            <span>Statut : en attente de développement du module export DGI</span>
          </div>
        </div>
      )}
    </div>
  );
}
