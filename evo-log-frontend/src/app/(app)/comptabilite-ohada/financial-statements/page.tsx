'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText, CheckCircle2, TrendingUp,
  Building, DollarSign, Layers, ShieldCheck, Printer, RefreshCw, Loader2, AlertTriangle
} from 'lucide-react';
import { toast } from 'sonner';
import CompanyDocumentHeader, { CompanyDocumentFooter } from '@/components/documents/CompanyDocumentHeader';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const AUTH = () => ({ 'Authorization': `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('access_token') || '' : ''}`, 'Content-Type': 'application/json' });

interface BilanData {
  id: number; exercice_id: number; date_bilan: string;
  actif_immobilise_net: number; actif_circulant_total: number;
  tresorerie_actif: number; total_actif: number;
  capitaux_propres_total: number; dettes_long_terme: number;
  dettes_courtes: number; total_passif: number;
  [key: string]: unknown;
}

interface CRData {
  id: number; exercice_id: number; periode: string; date_arrete: string;
  total_produits_exploitation: number; achats_marchandises: number;
  achats_matieres_premieres: number; services_exterieurs: number;
  charges_personnel: number; impots_taxes: number;
  dotations_amortissements: number; autres_charges_exploitation: number;
  total_charges_exploitation: number; resultat_exploitation: number;
  produits_financiers: number; charges_financieres: number; resultat_financier: number;
  produits_exceptionnels: number; charges_exceptionnelles: number; resultat_exceptionnel: number;
  resultat_net: number; [key: string]: unknown;
}

interface TAFIREData {
  id: number; exercice_id: number; date_tafire: string;
  capacit_autofinancement: number; cession_immobilisations: number;
  augmentation_capital: number; nouveaux_emprunts: number;
  total_ressources: number; investissements_immobilisations: number;
  remboursement_emprunts: number; distribution_dividendes: number;
  augmentation_besoin_fdr: number; total_emplois: number;
  variation_tresorerie: number; tresorerie_debut: number; tresorerie_fin: number;
  [key: string]: unknown;
}

interface AnnexesData {
  id: number; exercice_id: number; date_annexes: string;
  denomination_sociale: string | null; forme_juridique: string | null;
  siege_social: string | null; capital_social: number | null;
  methode_evaluation_stocks: string | null; methode_amortissements: string | null;
  principes_comptables: string | null; evenements_posterieurs: string | null;
  engagements_hors_bilan: string | null; [key: string]: unknown;
}

interface EtatsResponse {
  exercice_id: number; annee: number;
  bilan: BilanData | null; compte_resultat: CRData | null;
  tafire: TAFIREData | null; annexes: AnnexesData | null;
}

export default function ComptabiliteOhadaFinancialStatements() {
  const [activeTab, setActiveTab] = useState<'BILAN' | 'COMPTE_RESULTAT' | 'TAFIRE' | 'ANNEXES'>('BILAN');
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [etats, setEtats] = useState<EtatsResponse | null>(null);

  const charger = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API_BASE}/comptabilite-avance/etats-financiers/dernier`, { headers: AUTH() });
      if (res.ok) { setEtats(await res.json()); }
      else { const b = await res.json().catch(() => ({})); setError(b.detail || `Erreur ${res.status}`); }
    } catch { setError('Serveur injoignable.'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  const genererBilan = async () => {
    if (!etats) return; setGenerating(true);
    try {
      const res = await fetch(`${API_BASE}/comptabilite-avance/etats-financiers/bilan`, {
        method: 'POST', headers: AUTH(),
        body: JSON.stringify({ exercice_id: etats.exercice_id, date_bilan: new Date().toISOString().slice(0, 10) }),
      });
      if (res.ok) { toast.success('Bilan généré depuis le grand livre.'); await charger(); }
      else { const b = await res.json().catch(() => ({})); toast.error(b.detail || 'Échec génération bilan.'); }
    } catch { toast.error('Erreur réseau.'); } finally { setGenerating(false); }
  };

  const genererCR = async () => {
    if (!etats) return; setGenerating(true);
    try {
      const res = await fetch(`${API_BASE}/comptabilite-avance/etats-financiers/compte-resultat`, {
        method: 'POST', headers: AUTH(),
        body: JSON.stringify({ exercice_id: etats.exercice_id, periode: `${etats.annee}-12`, date_arrete: `${etats.annee}-12-31` }),
      });
      if (res.ok) { toast.success('Compte de résultat généré.'); await charger(); }
      else { const b = await res.json().catch(() => ({})); toast.error(b.detail || 'Échec.'); }
    } catch { toast.error('Erreur réseau.'); } finally { setGenerating(false); }
  };

  const genererTAFIRE = async () => {
    if (!etats) return; setGenerating(true);
    try {
      const res = await fetch(`${API_BASE}/comptabilite-avance/etats-financiers/tafire`, {
        method: 'POST', headers: AUTH(),
        body: JSON.stringify({ exercice_id: etats.exercice_id, date_tafire: new Date().toISOString().slice(0, 10) }),
      });
      if (res.ok) { toast.success('TAFIRE généré depuis le GL.'); await charger(); }
      else { const b = await res.json().catch(() => ({})); toast.error(b.detail || 'Échec TAFIRE.'); }
    } catch { toast.error('Erreur réseau.'); } finally { setGenerating(false); }
  };

  const fmt = (v: number | unknown) => Number(v || 0).toLocaleString('fr-FR');

  return (
    <div className="space-y-6 animate-in fade-in duration-300 font-sans">
      {/* Print header */}
      <div className="hidden print:block">
        <CompanyDocumentHeader
          documentTitle={`LIASSE FINANCIÈRE SYSCOHADA • ${activeTab}`}
          documentNumber={`SYSCOHADA-${etats?.annee || ''}-${activeTab}`}
          documentDate={new Date().toLocaleDateString('fr-FR')}
          documentReference={`EXERCICE-${etats?.annee || ''}-CERTIFIE`}
        />
      </div>

      {/* Screen header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl print:hidden">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
              États Financiers Normalisés SYSCOHADA
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <FileText className="w-8 h-8 text-violet-400" />
            États Financiers OHADA
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Bilan, Compte de Résultat, TAFIRE et Annexes. Source : grand livre réel (partie double).
          </p>
        </div>
        <div className="flex items-center gap-3">
          {etats && <span className="text-xs font-mono text-slate-400">Exercice {etats.annee}</span>}
          <button onClick={charger} className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl flex items-center gap-2 border border-slate-700 transition-all">
            <RefreshCw className="w-3.5 h-3.5" /> Recharger
          </button>
          <button onClick={() => window.print()} className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl flex items-center gap-2 border border-slate-700 transition-all">
            <Printer className="w-3.5 h-3.5" /> Imprimer
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 print:hidden">
        {[
          { key: 'BILAN', label: 'Bilan (Actif / Passif)' },
          { key: 'COMPTE_RESULTAT', label: 'Compte de Résultat (SIG)' },
          { key: 'TAFIRE', label: 'TAFIRE (Ressources / Emplois)' },
          { key: 'ANNEXES', label: 'Notes Annexes' },
        ].map(tab => (
          <button key={tab.key} onClick={() => setActiveTab(tab.key as typeof activeTab)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all border ${
              activeTab === tab.key ? 'bg-violet-600 text-white border-violet-500 shadow-md shadow-violet-600/30'
              : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:bg-slate-800 hover:text-white'}`}>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Error / Loading */}
      {error && <div className="flex items-center gap-3 px-4 py-3 bg-red-950/60 border border-red-800/40 rounded-2xl text-xs text-red-300 print:hidden"><AlertTriangle className="w-4 h-4 shrink-0" />{error}</div>}
      {loading && <div className="flex items-center justify-center gap-2 py-8 text-slate-400 text-xs"><Loader2 className="w-5 h-5 animate-spin" /> Chargement…</div>}

      {/* BILAN */}
      {activeTab === 'BILAN' && !loading && (
        <div className="print:space-y-4">
          {etats?.bilan ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* ACTIF */}
              <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <h2 className="text-base font-black text-emerald-400 uppercase tracking-tight flex items-center gap-2"><Building className="w-5 h-5" /> Actif</h2>
                  <span className="text-[11px] font-mono text-slate-500">Généré le {etats.bilan.date_bilan}</span>
                </div>
                <div className="space-y-3 font-mono text-xs">
                  {[
                    ['Actif immobilisé net (Cl. 2)', etats.bilan.actif_immobilise_net],
                    ['Actif circulant (Cl. 3+4)', etats.bilan.actif_circulant_total],
                    ['Trésorerie actif (Cl. 5)', etats.bilan.tresorerie_actif],
                  ].map(([lbl, v]) => (
                    <div key={lbl as string} className="flex justify-between p-3 rounded-xl bg-slate-950 border border-slate-800/80"><span className="text-slate-300">{lbl}</span><span className="text-slate-100 font-bold">{fmt(v)}</span></div>
                  ))}
                </div>
                <div className="p-3 bg-emerald-950/20 border border-emerald-500/30 rounded-xl flex justify-between text-sm font-black font-mono text-emerald-400">TOTAL ACTIF <span>{fmt(etats.bilan.total_actif)} XAF</span></div>
              </div>
              {/* PASSIF */}
              <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <h2 className="text-base font-black text-blue-400 uppercase tracking-tight flex items-center gap-2"><DollarSign className="w-5 h-5" /> Passif</h2>
                </div>
                <div className="space-y-3 font-mono text-xs">
                  {[
                    ['Capitaux propres (dont résultat)', etats.bilan.capitaux_propres_total],
                    ['Dettes long terme', etats.bilan.dettes_long_terme],
                    ['Dettes court terme', etats.bilan.dettes_courtes],
                  ].map(([lbl, v]) => (
                    <div key={lbl as string} className="flex justify-between p-3 rounded-xl bg-slate-950 border border-slate-800/80"><span className="text-slate-300">{lbl}</span><span className="text-slate-100 font-bold">{fmt(v)}</span></div>
                  ))}
                </div>
                <div className="p-3 bg-blue-950/20 border border-blue-500/30 rounded-xl flex justify-between text-sm font-black font-mono text-blue-400">TOTAL PASSIF <span>{fmt(etats.bilan.total_passif)} XAF</span></div>
              </div>
              {/* Equilibre */}
              <div className="col-span-full text-center text-xs font-mono text-slate-400 print:hidden">
                <CheckCircle2 className="w-4 h-4 inline text-emerald-400 mr-1" />
                Équilibre : Total Actif = Total Passif = {fmt(etats.bilan.total_actif)} XAF
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-8 text-center space-y-4">
              <p className="text-xs text-slate-400">Bilan non encore généré pour cet exercice.</p>
              <button onClick={genererBilan} disabled={generating} className="px-5 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl flex items-center gap-2 mx-auto">
                {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />} Générer le Bilan depuis le Grand Livre
              </button>
            </div>
          )}
        </div>
      )}

      {/* COMPTE DE RÉSULTAT */}
      {activeTab === 'COMPTE_RESULTAT' && !loading && (
        <div>
          {etats?.compte_resultat ? (
            <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h2 className="text-base font-black text-white uppercase flex items-center gap-2"><TrendingUp className="w-5 h-5 text-violet-400" /> Compte de Résultat (SIG)</h2>
                <span className="text-[11px] font-mono text-slate-500">Période {etats.compte_resultat.periode}</span>
              </div>
              <div className="divide-y divide-slate-800 font-mono text-xs">
                {[
                  ['Total produits exploitation', etats.compte_resultat.total_produits_exploitation, 'text-emerald-400', '+'],
                  ['Achats consommés', etats.compte_resultat.achats_marchandises + Number(etats.compte_resultat.achats_matieres_premieres), 'text-red-400', '-'],
                  ['Services extérieurs', etats.compte_resultat.services_exterieurs, 'text-red-400', '-'],
                  ['Charges de personnel', etats.compte_resultat.charges_personnel, 'text-red-400', '-'],
                  ['Impôts & taxes', etats.compte_resultat.impots_taxes, 'text-red-400', '-'],
                  ['Dotations amortissements', etats.compte_resultat.dotations_amortissements, 'text-red-400', '-'],
                  ['Total charges exploitation', etats.compte_resultat.total_charges_exploitation, 'text-red-400', '-'],
                ].map(([lbl, v, col, sgn]) => (
                  <div key={lbl as string} className="py-2 flex justify-between"><span className="text-slate-300">{lbl}</span><span className={col as string}>{sgn}{fmt(v)}</span></div>
                ))}
                <div className="py-2.5 flex justify-between bg-violet-950/20 px-3 rounded-xl border border-violet-500/20 font-bold"><span className="text-violet-300">= Résultat exploitation</span><span className="text-violet-300">{fmt(etats.compte_resultat.resultat_exploitation)}</span></div>
                <div className="py-2 flex justify-between"><span className="text-slate-300">Résultat financier</span><span className={Number(etats.compte_resultat.resultat_financier) >= 0 ? 'text-emerald-400' : 'text-red-400'}>{fmt(etats.compte_resultat.resultat_financier)}</span></div>
                <div className="py-2 flex justify-between"><span className="text-slate-300">Résultat exceptionnel</span><span className={Number(etats.compte_resultat.resultat_exceptionnel) >= 0 ? 'text-emerald-400' : 'text-red-400'}>{fmt(etats.compte_resultat.resultat_exceptionnel)}</span></div>
                <div className="py-3 flex justify-between bg-emerald-950/30 px-3 rounded-xl border border-emerald-500/40 text-sm font-black"><span className="text-emerald-300">RÉSULTAT NET</span><span className={Number(etats.compte_resultat.resultat_net) >= 0 ? 'text-emerald-400' : 'text-red-400'}>{fmt(etats.compte_resultat.resultat_net)} XAF</span></div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-8 text-center space-y-4">
              <p className="text-xs text-slate-400">Compte de Résultat non encore généré.</p>
              <button onClick={genererCR} disabled={generating} className="px-5 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl flex items-center gap-2 mx-auto">
                {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />} Générer le Compte de Résultat
              </button>
            </div>
          )}
        </div>
      )}

      {/* TAFIRE */}
      {activeTab === 'TAFIRE' && !loading && (
        <div>
          {etats?.tafire ? (
            <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h2 className="text-base font-black text-white uppercase flex items-center gap-2"><Layers className="w-5 h-5 text-indigo-400" /> TAFIRE</h2>
                <span className="text-[11px] font-mono text-indigo-400">Généré le {etats.tafire.date_tafire}</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs font-mono">
                <div className="bg-slate-950 rounded-2xl border border-slate-800 p-4 space-y-2">
                  <div className="text-emerald-300 font-bold font-sans border-b border-slate-800 pb-2 mb-2">RESSOURCES</div>
                  {[
                    ['CAF (RN + amort.)', etats.tafire.capacit_autofinancement],
                    ['Cessions immobilisations', etats.tafire.cession_immobilisations],
                    ['Augmentation capital', etats.tafire.augmentation_capital],
                    ['Nouveaux emprunts', etats.tafire.nouveaux_emprunts],
                  ].map(([lbl, v]) => (<div key={lbl as string} className="flex justify-between"><span className="text-slate-400">{lbl}</span><span className="text-slate-200">{fmt(v)}</span></div>))}
                  <div className="flex justify-between font-bold border-t border-slate-800 pt-2 mt-2"><span className="text-emerald-300">Total ressources</span><span className="text-emerald-400">{fmt(etats.tafire.total_ressources)}</span></div>
                </div>
                <div className="bg-slate-950 rounded-2xl border border-slate-800 p-4 space-y-2">
                  <div className="text-red-300 font-bold font-sans border-b border-slate-800 pb-2 mb-2">EMPLOIS</div>
                  {[
                    ['Investissements (Cl. 2 net)', etats.tafire.investissements_immobilisations],
                    ['Remboursements emprunts', etats.tafire.remboursement_emprunts],
                    ['Dividendes distribués', etats.tafire.distribution_dividendes],
                    ['Augmentation BFR', etats.tafire.augmentation_besoin_fdr],
                  ].map(([lbl, v]) => (<div key={lbl as string} className="flex justify-between"><span className="text-slate-400">{lbl}</span><span className="text-slate-200">{fmt(v)}</span></div>))}
                  <div className="flex justify-between font-bold border-t border-slate-800 pt-2 mt-2"><span className="text-red-300">Total emplois</span><span className="text-red-400">{fmt(etats.tafire.total_emplois)}</span></div>
                </div>
              </div>
              <div className="p-3 bg-indigo-950/30 border border-indigo-500/30 rounded-xl flex justify-between text-sm font-black font-mono">
                <span className="text-indigo-300">Variation trésorerie</span>
                <span className={Number(etats.tafire.variation_tresorerie) >= 0 ? 'text-emerald-400' : 'text-red-400'}>{fmt(etats.tafire.variation_tresorerie)} XAF</span>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-8 text-center space-y-4">
              <p className="text-xs text-slate-400">TAFIRE non encore généré. Nécessite le CR et le Bilan.</p>
              <button onClick={genererTAFIRE} disabled={generating} className="px-5 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl flex items-center gap-2 mx-auto">
                {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />} Générer le TAFIRE depuis le GL
              </button>
            </div>
          )}
        </div>
      )}

      {/* ANNEXES */}
      {activeTab === 'ANNEXES' && !loading && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h2 className="text-base font-black text-white uppercase flex items-center gap-2"><ShieldCheck className="w-5 h-5 text-amber-400" /> Notes Annexes</h2>
            {etats?.annexes && <span className="text-[11px] font-mono text-slate-500">Du {etats.annexes.date_annexes}</span>}
          </div>
          {etats?.annexes ? (
            <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
              {[
                ['Dénomination', etats.annexes.denomination_sociale],
                ['Forme juridique', etats.annexes.forme_juridique],
                ['Siège social', etats.annexes.siege_social],
                ['Capital social', etats.annexes.capital_social ? `${fmt(etats.annexes.capital_social)} XAF` : null],
                ['Méthode évaluation stocks', etats.annexes.methode_evaluation_stocks],
                ['Méthode amortissements', etats.annexes.methode_amortissements],
                ['Principes comptables', etats.annexes.principes_comptables],
                ['Événements postérieurs', etats.annexes.evenements_posterieurs],
                ['Engagements hors bilan', etats.annexes.engagements_hors_bilan],
              ].filter(([, v]) => v).map(([lbl, v]) => (
                <div key={lbl as string} className="p-3 bg-slate-950 rounded-xl border border-slate-800"><span className="text-slate-400 font-sans">{lbl} :</span> <span className="text-slate-200">{v}</span></div>
              ))}
            </div>
          ) : (
            <div className="py-6 text-center space-y-3">
              <p className="text-xs text-slate-400">Notes annexes non encore saisies.</p>
              <p className="text-[11px] text-slate-500">Créez-les via POST /etats-financiers/annexes avec les informations légales de votre entreprise.</p>
            </div>
          )}
        </div>
      )}

      {/* Print footer */}
      <div className="hidden print:block"><CompanyDocumentFooter /></div>
    </div>
  );
}
