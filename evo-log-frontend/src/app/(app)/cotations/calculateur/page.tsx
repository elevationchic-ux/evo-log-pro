'use client';

import React, { useState } from 'react';
import { Calculator, ArrowLeft, RefreshCw, DollarSign } from 'lucide-react';
import Link from 'next/link';

export default function CalculateurCotationPage() {
  const [distanceKm, setDistanceKm] = useState('1150');
  const [poidsTons, setPoidsTons] = useState('28');
  const [fraisPort, setFraisPort] = useState('450000');
  const [fraisDouane, setFraisDouane] = useState('850000');

  const dist = Number(distanceKm) || 0;
  const weight = Number(poidsTons) || 0;
  const port = Number(fraisPort) || 0;
  const customs = Number(fraisDouane) || 0;

  const coutCarburant = dist * 850; // 850 XAF / km
  const coutChauffeur = dist * 120;
  const coutTotal = coutCarburant + coutChauffeur + port + customs;
  const prixConseille = coutTotal * 1.22; // 22% margin

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
            <h1 className="text-2xl font-black">Calculateur de Marge & Tarif IA</h1>
            <p className="text-sm text-slate-400">Simulation instantanée des coûts de transport multimodal et acconage.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Distance du Trajet (km)</label>
            <input
              type="number"
              value={distanceKm}
              onChange={(e) => setDistanceKm(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-emerald-400 font-mono font-bold"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Poids du Fret (Tonnes)</label>
            <input
              type="number"
              value={poidsTons}
              onChange={(e) => setPoidsTons(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-emerald-400 font-mono font-bold"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Frais d'Acconage & Quai (XAF)</label>
            <input
              type="number"
              value={fraisPort}
              onChange={(e) => setFraisPort(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-emerald-400 font-mono font-bold"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Frais Douane Estimés (XAF)</label>
            <input
              type="number"
              value={fraisDouane}
              onChange={(e) => setFraisDouane(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-emerald-400 font-mono font-bold"
            />
          </div>
        </div>

        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Coût Carburant Estimé :</span>
            <span className="font-mono text-slate-200">{coutCarburant.toLocaleString()} XAF</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Coût Total d'Opération (Prerequis) :</span>
            <span className="font-mono text-slate-200">{coutTotal.toLocaleString()} XAF</span>
          </div>
          <div className="pt-3 border-t border-slate-800 flex justify-between items-center">
            <span className="font-bold text-base text-slate-100">Prix de Vente Conseillé (+22% Marge) :</span>
            <span className="font-mono font-black text-2xl text-emerald-400">{Math.round(prixConseille).toLocaleString()} XAF</span>
          </div>
        </div>
      </div>
    </div>
  );
}
