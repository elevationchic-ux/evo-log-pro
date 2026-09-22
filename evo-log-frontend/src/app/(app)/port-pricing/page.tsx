'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  DollarSign, Calculator, Search, Plus, CheckCircle2,
  Anchor, Ship, RefreshCw, X, ArrowRight, ShieldCheck, Tag
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function PortPricingPage() {
  const [tarifs, setTarifs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Simulateur de tarification portuaire
  const [calcInput, setCalcInput] = useState({
    type_prestation: 'debarquement_conteneur',
    taille_conteneur: '40',
    jours_sejour: 14,
    est_frigo: false,
    pesage_vgm: true,
  });

  const [calcResult, setCalcResult] = useState<any>({
    droits_quai: 85000,
    acconage_manutention: 120000,
    surestaries_sejour: 45000,
    branchement_reefer: 0,
    pesage_vgm: 15000,
    tva: 51012,
    total_estime_xaf: 316012,
  });

  const fetchTarifs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/port-pricing');
      if (res.data) {
        setTarifs(Array.isArray(res.data) ? res.data : (res.data.items || []));
      }
    } catch (err) {
      console.error('Erreur chargement barème tarifaire:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTarifs();
  }, [fetchTarifs]);

  const handleCalculate = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const is40 = calcInput.taille_conteneur === '40';
    const droits_quai = is40 ? 110000 : 75000;
    const manutention = is40 ? 145000 : 95000;
    const jours_extra = Math.max(0, calcInput.jours_sejour - 11); // franchise 11 jours
    const surestaries = jours_extra * (is40 ? 15000 : 9000);
    const reefer = calcInput.est_frigo ? calcInput.jours_sejour * 18000 : 0;
    const vgm = calcInput.pesage_vgm ? 15000 : 0;
    const ht = droits_quai + manutention + surestaries + reefer + vgm;
    const tva = ht * 0.1925;

    setCalcResult({
      droits_quai,
      acconage_manutention: manutention,
      surestaries_sejour: surestaries,
      branchement_reefer: reefer,
      pesage_vgm: vgm,
      tva,
      total_estime_xaf: ht + tva,
    });
  };

  return (
    <div className="space-y-8 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Tag className="w-3.5 h-3.5" /> Grille Officielle des Tarifs & Redevances Portuaires
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Tarification Portuaire & Simulateur d'Escales
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Barèmes homologués par le Port Autonome de Douala (PAD) et le Port de Kribi (PAK) : pilotage, quai, séjour et manutention.
          </p>
        </div>

        <button
          onClick={() => fetchTarifs()}
          className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
          title="Actualiser"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Simulator Section */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-6 space-y-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Calculator className="w-5 h-5 text-emerald-400" /> Simulateur de Frais Portuaires & Surestaries
          </h2>
          <p className="text-xs text-slate-400">
            Estimez instantanément les coûts de manutention, passage portuaire et frais de séjour selon les paramètres réels :
          </p>

          <form onSubmit={handleCalculate} className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-400 mb-1 font-semibold">Taille Conteneur</label>
                <select
                  value={calcInput.taille_conteneur}
                  onChange={(e) => setCalcInput({ ...calcInput, taille_conteneur: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="20">Conteneur 20 Pieds (1 EVP)</option>
                  <option value="40">Conteneur 40 Pieds (2 EVP / High Cube)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-semibold">Jours de Séjour au Quai</label>
                <input
                  type="number"
                  min="1"
                  max="90"
                  value={calcInput.jours_sejour}
                  onChange={(e) => setCalcInput({ ...calcInput, jours_sejour: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>

            <div className="flex flex-wrap gap-4 pt-1">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={calcInput.est_frigo}
                  onChange={(e) => setCalcInput({ ...calcInput, est_frigo: e.target.checked })}
                  className="rounded bg-slate-800 border-slate-700 text-emerald-600 focus:ring-emerald-500"
                />
                <span className="text-slate-300">Conteneur Frigorifique (Reefer Branché)</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={calcInput.pesage_vgm}
                  onChange={(e) => setCalcInput({ ...calcInput, pesage_vgm: e.target.checked })}
                  className="rounded bg-slate-800 border-slate-700 text-emerald-600 focus:ring-emerald-500"
                />
                <span className="text-slate-300">Pesage Certifié Solas VGM</span>
              </label>
            </div>

            <button
              type="button"
              onClick={() => handleCalculate()}
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/20 transition-all flex items-center gap-2"
            >
              <Calculator className="w-4 h-4" /> Calculer le Coût Prévisionnel
            </button>
          </form>
        </div>

        {/* Calculation Summary Card */}
        <div className="lg:col-span-6 bg-slate-950/80 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4">
          <div>
            <span className="text-xs font-mono text-emerald-400 font-bold uppercase tracking-wider block mb-2">
              Décomposition du Devis Estimé
            </span>
            <div className="space-y-2 text-xs divide-y divide-slate-800/60">
              <div className="flex justify-between pt-1">
                <span className="text-slate-400">Droits de Quai & Passage Portuaire</span>
                <span className="font-mono text-white">{Number(calcResult.droits_quai).toLocaleString()} XAF</span>
              </div>
              <div className="flex justify-between pt-2">
                <span className="text-slate-400">Acconage & Débarquement Portique</span>
                <span className="font-mono text-white">{Number(calcResult.acconage_manutention).toLocaleString()} XAF</span>
              </div>
              <div className="flex justify-between pt-2">
                <span className="text-slate-400">Frais de Séjour / Surestaries (Dépassement Franchise)</span>
                <span className={`font-mono ${calcResult.surestaries_sejour > 0 ? 'text-amber-400 font-bold' : 'text-slate-500'}`}>
                  {Number(calcResult.surestaries_sejour).toLocaleString()} XAF
                </span>
              </div>
              {calcResult.branchement_reefer > 0 && (
                <div className="flex justify-between pt-2">
                  <span className="text-slate-400">Alimentation Électrique & Monitoring Frigo</span>
                  <span className="font-mono text-cyan-400">{Number(calcResult.branchement_reefer).toLocaleString()} XAF</span>
                </div>
              )}
              {calcResult.pesage_vgm > 0 && (
                <div className="flex justify-between pt-2">
                  <span className="text-slate-400">Pesage Pont-Bascule Homologué SOLAS</span>
                  <span className="font-mono text-white">{Number(calcResult.pesage_vgm).toLocaleString()} XAF</span>
                </div>
              )}
              <div className="flex justify-between pt-2">
                <span className="text-slate-400">TVA Réglementaire (19.25%)</span>
                <span className="font-mono text-slate-300">{Number(calcResult.tva).toLocaleString()} XAF</span>
              </div>
            </div>
          </div>

          <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
            <span className="text-xs font-bold text-slate-300">TOTAL ESTIMÉ TTC :</span>
            <span className="text-xl font-black font-mono text-emerald-400">
              {Number(calcResult.total_estime_xaf).toLocaleString()} FCFA
            </span>
          </div>
        </div>
      </div>

      {/* Official Tariffs Grid */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="p-5 border-b border-slate-800 bg-slate-950/60">
          <h3 className="font-bold text-white text-sm flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-emerald-400" /> Barème Standard des Prestations Portuaires
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-slate-400 uppercase font-semibold">
                <th className="py-3 px-5">Code Prestation</th>
                <th className="py-3 px-5">Libellé Officiel</th>
                <th className="py-3 px-5">Unité de Taxation</th>
                <th className="py-3 px-5">Tarif 20' (XAF)</th>
                <th className="py-3 px-5">Tarif 40' (XAF)</th>
                <th className="py-3 px-5">Franchise</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
              {[
                { code: 'PRT-QUAI-01', nom: 'Droit de Quai Débarquement Import', unite: 'Par conteneur', t20: 75000, t40: 110000, franchise: 'Sans objet' },
                { code: 'PRT-ACCON-02', nom: 'Manutention Portique Bord/Terre', unite: 'Par mouvement', t20: 95000, t40: 145000, franchise: 'Sans objet' },
                { code: 'PRT-SEJOUR-03', nom: 'Séjour Terre-Plein Magasin 3', unite: 'Par jour / conteneur', t20: 9000, t40: 15000, franchise: '11 jours francs' },
                { code: 'PRT-REEFER-04', nom: 'Branchement Frigorifique Quai', unite: 'Par 24h entamée', t20: 18000, t40: 22000, franchise: 'Aucune' },
                { code: 'PRT-VGM-05', nom: 'Pesage Réglementaire SOLAS VGM', unite: 'Par passage bascule', t20: 15000, t40: 15000, franchise: 'Aucune' }
              ].map((row, i) => (
                <tr key={i} className="hover:bg-slate-800/40 font-sans">
                  <td className="py-3 px-5 font-mono text-cyan-400 font-bold">{row.code}</td>
                  <td className="py-3 px-5 font-medium text-white">{row.nom}</td>
                  <td className="py-3 px-5 text-slate-400">{row.unite}</td>
                  <td className="py-3 px-5 font-mono">{row.t20.toLocaleString()}</td>
                  <td className="py-3 px-5 font-mono">{row.t40.toLocaleString()}</td>
                  <td className="py-3 px-5 text-emerald-400 text-[11px] font-semibold">{row.franchise}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
