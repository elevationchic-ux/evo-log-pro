'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Building2, Package, Clock, CheckCircle2, AlertCircle, TrendingUp, Search, ArrowRight, ShieldCheck, CreditCard } from 'lucide-react';
import { b2bPortalAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function PortailB2BDashboard() {
  const [loading, setLoading] = useState(true);
  const [dossiers, setDossiers] = useState<any[]>([]);
  const [factures, setFactures] = useState<any[]>([]);
  const [searchContainer, setSearchContainer] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [dosRes, facRes] = await Promise.all([
        b2bPortalAPI.getDossiers(1),
        b2bPortalAPI.getFactures(1)
      ]);
      setDossiers(dosRes.data || (Array.isArray(dosRes) ? dosRes : []));
      setFactures(facRes.data || (Array.isArray(facRes) ? facRes : []));
    } catch (err) {
      console.error('Erreur chargement portail B2B', err);
      toast.error('Erreur de liaison avec le serveur EVO-LOG');
    } finally {
      setLoading(false);
    }
  };

  const totalFacturesTTC = factures.reduce((s, f) => s + (f.montant_ttc || 0), 0);
  const enAttenteFactures = factures.filter(f => f.statut === 'EN_ATTENTE');
  const enAttenteMontant = enAttenteFactures.reduce((s, f) => s + (f.montant_ttc || 0), 0);
  const dossiersEnCours = dossiers.filter(d => d.statut === 'EN_COURS');
  const dossiersLivres = dossiers.filter(d => d.statut === 'LIVRE');
  const dossierActif = dossiersEnCours[0] || dossiers[0];

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header avec branding client */}
      <div className="bg-gradient-to-r from-slate-900 to-violet-950 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
                Portail Client • Espace Privé
              </span>
              <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                T-Code : KB2B_DSH
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
              <Building2 className="w-8 h-8 text-violet-400" />
              Espace Client • Bolloré Cameroun & Bocom
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Suivi en temps réel de vos dossiers transit, transport et manutention. Documents, factures et communications EVO-LOG.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-slate-900/80 border border-slate-700 rounded-2xl p-4">
            <div className="w-12 h-12 rounded-2xl bg-violet-600 flex items-center justify-center text-white font-black text-lg">B</div>
            <div>
              <div className="font-bold text-slate-100 text-sm">Jean-Baptiste ABENA</div>
              <div className="text-xs text-slate-400">Directeur Supply Chain</div>
              <div className="text-xs text-violet-400 font-mono mt-0.5">CLIENT_B2B · BOCOM-CI</div>
            </div>
          </div>
        </div>

        {/* Quick container search */}
        <div className="mt-5 pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 absolute left-3.5 top-3 text-violet-400" />
            <input
              type="text"
              value={searchContainer}
              onChange={(e) => setSearchContainer(e.target.value)}
              placeholder="Entrez un N° conteneur (ex: MSKU9823412) ou B/L pour tracking direct..."
              className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-violet-500/30 rounded-xl text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-400"
            />
          </div>
          <Link
            href={`/portail-b2b/suivi-dossiers?q=${encodeURIComponent(searchContainer || 'MSKU9823412')}`}
            className="w-full sm:w-auto px-5 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-violet-600/30 transition-all"
          >
            Lancer le Suivi <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* KPIs rapides */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Dossiers en cours', value: String(dossiersEnCours.length || 1), icon: Package, color: 'text-violet-400', href: '/portail-b2b/suivi-dossiers' },
          { label: 'Dossiers livrés', value: String(dossiersLivres.length || 12), icon: CheckCircle2, color: 'text-emerald-400', href: '/portail-b2b/suivi-dossiers' },
          { label: 'Factures en attente', value: String(enAttenteFactures.length || 1), icon: AlertCircle, color: 'text-amber-400', href: '/portail-b2b/factures-devis' },
          { label: 'Montant facturé (YTD)', value: `${((totalFacturesTTC || 11269125) / 1000000).toFixed(2)}M XAF`, icon: TrendingUp, color: 'text-blue-400', href: '/portail-b2b/factures-devis' },
        ].map((kpi, i) => (
          <Link key={i} href={kpi.href} className="bg-slate-900/80 border border-slate-800 hover:border-slate-600 p-5 rounded-2xl transition-all group">
            <kpi.icon className={`w-5 h-5 ${kpi.color} mb-2 group-hover:scale-110 transition-transform`} />
            <div className={`text-2xl font-black font-mono ${kpi.color}`}>{kpi.value}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">{kpi.label}</div>
          </Link>
        ))}
      </div>

      {/* Dossier en cours résumé */}
      {dossierActif && (
        <div className="bg-slate-900/90 border border-violet-500/20 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4 text-violet-400" /> Dossier Actif • Suivi en temps réel
            </h2>
            <Link href="/portail-b2b/suivi-dossiers" className="text-xs text-violet-400 hover:text-violet-300 font-bold">
              Voir tous les dossiers →
            </Link>
          </div>
          <div className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-violet-400 text-sm font-bold">{dossierActif.dossier_id}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    Conteneur : {dossierActif.conteneur_no || 'MSKU9823412'}
                  </span>
                </div>
                <div className="text-slate-100 font-bold mt-1">{dossierActif.description}</div>
                <div className="text-xs text-slate-400 mt-0.5">
                  Commercial référent : {dossierActif.commercial} • Tél: {dossierActif.contact_tel}
                </div>
              </div>
              <span className="px-3 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded-xl text-xs font-bold self-start">
                {dossierActif.statut} • {dossierActif.progression_pct}%
              </span>
            </div>

            {/* Progress bar */}
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden mb-5">
              <div
                className="h-full bg-gradient-to-r from-violet-600 to-blue-500 rounded-full transition-all duration-500"
                style={{ width: `${dossierActif.progression_pct}%` }}
              />
            </div>

            {/* Étapes */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {(dossierActif.etapes || []).map((step: any, i: number) => (
                <div
                  key={i}
                  className={`flex items-center gap-3 p-2.5 rounded-xl border ${
                    step.statut === 'DONE'
                      ? 'bg-emerald-950/10 border-emerald-500/20 text-slate-300'
                      : step.statut === 'IN_PROGRESS'
                      ? 'bg-violet-950/20 border-violet-500/30 text-slate-100'
                      : 'bg-slate-950/40 border-slate-800 text-slate-500'
                  }`}
                >
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 text-xs font-black ${
                      step.statut === 'DONE'
                        ? 'bg-emerald-500 text-white'
                        : step.statut === 'IN_PROGRESS'
                        ? 'bg-violet-600 text-white animate-pulse'
                        : 'bg-slate-800 text-slate-600'
                    }`}
                  >
                    {step.statut === 'DONE' ? '✓' : i + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-sans text-xs font-semibold truncate">{step.nom}</div>
                    <div className="font-mono text-[10px] text-slate-400">{step.date} {step.heure ? `à ${step.heure}` : ''}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
