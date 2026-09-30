'use client';

import React, { useState } from 'react';
import { Calculator, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function CalculateurCotationPage() {
  // Parcours et frais reels a integrer a la simulation.
  const [distanceKm, setDistanceKm] = useState('1150');
  const [fraisPort, setFraisPort] = useState('450000');
  const [fraisDouane, setFraisDouane] = useState('850000');

  // Hypotheses de cout : laissees explicitement modifiables. Ce ne sont PAS des
  // tarifs officiels ni un modele « IA » : ce sont des parametres de simulation
  // que l'utilisateur ajuste, et dont le calcul depend entierement.
  const [coutCarburantKm, setCoutCarburantKm] = useState('850');
  const [coutChauffeurKm, setCoutChauffeurKm] = useState('120');
  const [margePct, setMargePct] = useState('22');

  const dist = Number(distanceKm) || 0;
  const port = Number(fraisPort) || 0;
  const customs = Number(fraisDouane) || 0;
  const carburantKm = Number(coutCarburantKm) || 0;
  const chauffeurKm = Number(coutChauffeurKm) || 0;
  const marge = Number(margePct) || 0;

  const coutCarburant = dist * carburantKm;
  const coutChauffeur = dist * chauffeurKm;
  const coutTotal = coutCarburant + coutChauffeur + port + customs;
  const prixConseille = Math.round(coutTotal * (1 + marge / 100));

  const champ = (
    label: string, value: string, onChange: (v: string) => void, suffix: string,
  ) => (
    <div>
      <label className="block text-xs font-bold text-slate-400 uppercase mb-2">{label}</label>
      <div className="relative">
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 pr-16 text-emerald-400 font-mono font-bold focus:outline-none focus:border-emerald-500"
        />
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[11px] text-slate-500 font-mono">{suffix}</span>
      </div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 text-white animate-in fade-in duration-500">
      <Link href="/cotations" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6">
        <ArrowLeft className="w-4 h-4" /> Retour aux cotations
      </Link>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6">
        <div className="flex items-center gap-3 pb-6 border-b border-slate-800">
          <div className="w-12 h-12 bg-emerald-500/10 text-emerald-400 rounded-2xl flex items-center justify-center border border-emerald-500/20">
            <Calculator className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black">Calculateur de Marge &amp; Coûts de Transport</h1>
            <p className="text-sm text-slate-400">
              Simulation à partir d&apos;hypothèses de coûts que vous ajustez (aucun tarif officiel, aucun modèle prédictif).
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {champ('Distance du trajet (km)', distanceKm, setDistanceKm, 'km')}
          {champ('Frais d’acconage & quai', fraisPort, setFraisPort, 'XAF')}
          {champ('Frais de douane estimés', fraisDouane, setFraisDouane, 'XAF')}
          {champ('Coût carburant', coutCarburantKm, setCoutCarburantKm, 'XAF/km')}
          {champ('Coût chauffeur', coutChauffeurKm, setCoutChauffeurKm, 'XAF/km')}
          {champ('Marge cible', margePct, setMargePct, '%')}
        </div>

        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Coût carburant estimé :</span>
            <span className="font-mono text-slate-200">{coutCarburant.toLocaleString()} XAF</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Coût chauffeur estimé :</span>
            <span className="font-mono text-slate-200">{coutChauffeur.toLocaleString()} XAF</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Coût total d’opération (hors marge) :</span>
            <span className="font-mono text-slate-200">{coutTotal.toLocaleString()} XAF</span>
          </div>
          <div className="pt-3 border-t border-slate-800 flex justify-between items-center">
            <span className="font-bold text-base text-slate-100">Prix de vente conseillé (+{marge} % marge) :</span>
            <span className="font-mono font-black text-2xl text-emerald-400">{prixConseille.toLocaleString()} XAF</span>
          </div>
        </div>

        <p className="text-[11px] text-slate-500">
          Les coûts carburant, chauffeur et la marge sont des hypothèses saisies, modifiables ci-dessus : ils ne
          proviennent d&apos;aucun tarif officiel ni d&apos;aucun calcul automatique. Ajustez-les à vos réalités
          d&apos;exploitation avant de chiffrer une cotation.
        </p>
      </div>
    </div>
  );
}
