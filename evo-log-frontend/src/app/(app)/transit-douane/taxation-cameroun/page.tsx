'use client';

import React, { useState, useCallback } from 'react';
import {
  Calculator, Search, Plus, AlertTriangle, ChevronDown,
  CheckCircle2, DollarSign, Package, Info, Zap, RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';

// CEMAC Tariff Reference - simplified HS headings for demo
const HS_DATABASE = [
  { code: '1001.99.00', desc: 'Froment (blé) et méteil - Autres', dd: 5, tva: 0, pcs: 1.5, tac: 1, rs: 0 },
  { code: '2710.12.10', desc: 'Gasoil, huiles légères', dd: 20, tva: 19.25, pcs: 1.5, tac: 1, rs: 0.5, accises: 5 },
  { code: '8471.30.00', desc: 'Machines automatiques de traitement de l\'information', dd: 10, tva: 19.25, pcs: 1.5, tac: 1, rs: 0 },
  { code: '3004.90.00', desc: 'Médicaments, pour la médecine humaine', dd: 5, tva: 0, pcs: 1.5, tac: 1, rs: 0 },
  { code: '7308.90.00', desc: 'Constructions & parties en acier', dd: 20, tva: 19.25, pcs: 1.5, tac: 1, rs: 0 },
  { code: '8704.21.10', desc: 'Véhicules automobiles pour transport de marchandises, diesel <= 5T', dd: 30, tva: 19.25, pcs: 1.5, tac: 1, rs: 1 },
  { code: '2204.21.00', desc: 'Vins de raisins frais en bouteilles', dd: 30, tva: 19.25, pcs: 1.5, tac: 1, rs: 0.5, accises: 25 },
  { code: '3808.91.00', desc: 'Insecticides & pesticides', dd: 5, tva: 0, pcs: 1.5, tac: 1, rs: 0 },
];

export default function TransitDouaneTaxationPage() {
  const [hsSearch, setHsSearch] = useState('');
  const [selectedHS, setSelectedHS] = useState<typeof HS_DATABASE[0] | null>(null);
  const [showHSDropdown, setShowHSDropdown] = useState(false);

  const [form, setForm] = useState({
    valeurFOB: 0,
    fretsAssurances: 0,
    incoterm: 'CIF',
    origine: 'CN',
    quantite: 1,
  });

  const filteredHS = HS_DATABASE.filter(h =>
    hsSearch && (h.code.includes(hsSearch) || h.desc.toLowerCase().includes(hsSearch.toLowerCase()))
  ).slice(0, 8);

  const valeurCIF = form.valeurFOB + form.fretsAssurances;

  const taxes = selectedHS ? (() => {
    const dd = (valeurCIF * selectedHS.dd) / 100;
    const pcs = (valeurCIF * selectedHS.pcs) / 100;
    const tac = (valeurCIF * selectedHS.tac) / 100;
    const rs = (valeurCIF * selectedHS.rs) / 100;
    const accises = ((selectedHS as any).accises) ? (valeurCIF * (selectedHS as any).accises) / 100 : 0;
    const tva = ((valeurCIF + dd + pcs + tac + accises) * selectedHS.tva) / 100;
    const total = dd + pcs + tac + rs + accises + tva;
    return { dd, pcs, tac, rs, accises, tva, total };
  })() : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-white">Calculateur Taxation Douanière CEMAC</h1>
        <p className="text-xs text-slate-400 mt-0.5">Estimation DD + RS + TAC + PCS + TVA + Accises  Barème CEMAC / DGD Cameroun</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Calculator Inputs */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-5">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Calculator className="w-4 h-4 text-amber-400" /> Paramètres de la Déclaration
          </h2>

          {/* HS Code search */}
          <div className="relative">
            <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Code HS / Désignation de la Marchandise</label>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={hsSearch}
                onChange={e => { setHsSearch(e.target.value); setShowHSDropdown(true); }}
                onFocus={() => setShowHSDropdown(true)}
                placeholder="Tapez le code HS ou la désignation..."
                className="w-full h-11 pl-9 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>
            {showHSDropdown && filteredHS.length > 0 && (
              <div className="absolute z-20 top-full left-0 right-0 mt-1 bg-slate-950 border border-slate-800 rounded-xl shadow-2xl overflow-hidden">
                {filteredHS.map(h => (
                  <button
                    key={h.code}
                    onClick={() => { setSelectedHS(h); setHsSearch(`${h.code}  ${h.desc}`); setShowHSDropdown(false); }}
                    className="w-full text-left px-4 py-3 hover:bg-slate-800 border-b border-slate-800/60 last:border-0 transition-colors"
                  >
                    <div className="text-xs font-mono font-bold text-amber-300">{h.code}</div>
                    <div className="text-[11px] text-slate-400">{h.desc}</div>
                    <div className="text-[11px] text-slate-500 mt-0.5">
                      DD: {h.dd}% • TVA: {h.tva}% • PCS: {h.pcs}% • TAC: {h.tac}%
                      {(h as any).accises ? ` • Accises: ${(h as any).accises}%` : ''}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Values */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Valeur FOB (XAF)</label>
              <input
                type="number"
                value={form.valeurFOB || ''}
                onChange={e => setForm(f => ({ ...f, valeurFOB: parseFloat(e.target.value) || 0 }))}
                placeholder="Ex: 45 000 000"
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Fret + Assurance (XAF)</label>
              <input
                type="number"
                value={form.fretsAssurances || ''}
                onChange={e => setForm(f => ({ ...f, fretsAssurances: parseFloat(e.target.value) || 0 }))}
                placeholder="Ex: 3 500 000"
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Incoterm</label>
              <select
                value={form.incoterm}
                onChange={e => setForm(f => ({ ...f, incoterm: e.target.value }))}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500"
              >
                {['EXW', 'FCA', 'FOB', 'CFR', 'CIF', 'DAP', 'DDP'].map(i => <option key={i}>{i}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Pays d'Origine</label>
              <select
                value={form.origine}
                onChange={e => setForm(f => ({ ...f, origine: e.target.value }))}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500"
              >
                <option value="CN">🇨🇳 Chine</option>
                <option value="IN">🇮🇳 Inde</option>
                <option value="FR">🇫🇷 France (UE)</option>
                <option value="US">🇺🇸 États-Unis</option>
                <option value="DE">🇩🇪 Allemagne (UE)</option>
                <option value="MA">🇲🇦 Maroc</option>
                <option value="TR">🇹🇷 Turquie</option>
              </select>
            </div>
          </div>

          {/* Value CIF derived */}
          <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Valeur CIF (Base d'imposition CEMAC) =</span>
              <span className="font-mono font-black text-amber-300">{valeurCIF.toLocaleString()} XAF</span>
            </div>
          </div>
        </div>

        {/* Tax Result Panel */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-emerald-400" /> Droits & Taxes Calculés
          </h2>

          {selectedHS && taxes ? (
            <>
              <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-3 mb-4">
                <div className="text-[11px] text-emerald-400 font-mono">{selectedHS.code}</div>
                <div className="text-xs text-slate-300 font-medium">{selectedHS.desc}</div>
              </div>

              <div className="space-y-2">
                {[
                  { label: `Droit de Douane (DD)  ${selectedHS.dd}%`, amount: taxes.dd, color: 'text-blue-400' },
                  { label: `Redevance Statistique (RS)  ${selectedHS.rs}%`, amount: taxes.rs, color: 'text-purple-400' },
                  { label: `Taxe Communautaire d'Intégration (TCI/TAC)  ${selectedHS.tac}%`, amount: taxes.tac, color: 'text-cyan-400' },
                  { label: `Prélèvement Communautaire de Solidarité (PCS)  ${selectedHS.pcs}%`, amount: taxes.pcs, color: 'text-indigo-400' },
                  ...(taxes.accises > 0 ? [{ label: `Accises  ${(selectedHS as any).accises}%`, amount: taxes.accises, color: 'text-orange-400' }] : []),
                  { label: `TVA (sur valeur importation)  ${selectedHS.tva}%`, amount: taxes.tva, color: 'text-amber-400' },
                ].map((t, i) => (
                  <div key={i} className="flex justify-between text-xs py-1.5 border-b border-slate-800/60">
                    <span className="text-slate-400">{t.label}</span>
                    <span className={`font-mono font-bold ${t.color}`}>{Math.round(t.amount).toLocaleString()} XAF</span>
                  </div>
                ))}
              </div>

              <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 flex items-center justify-between mt-4">
                <div>
                  <div className="text-xs font-bold text-slate-300 uppercase">Total Droits & Taxes</div>
                  <div className="text-2xl font-black text-amber-300 font-mono mt-0.5">
                    {Math.round(taxes.total).toLocaleString()} XAF
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    Taux effectif global: {valeurCIF > 0 ? ((taxes.total / valeurCIF) * 100).toFixed(1) : 0}% de la valeur CIF
                  </div>
                </div>
                <button
                  onClick={() => toast.error("L'enregistrement des simulations DUM n'est pas encore raccordé à l'API.")}
                  className="px-4 py-2 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-bold text-xs rounded-xl border border-amber-500/30 transition-colors"
                >
                  Enregistrer
                </button>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center py-16 text-slate-500">
              <Calculator className="w-10 h-10 mb-3 opacity-30" />
              <p className="text-sm text-center">Sélectionnez un code HS et renseignez les valeurs pour calculer les droits et taxes</p>
            </div>
          )}
        </div>
      </div>

      {/* Notes légales */}
      <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
        <p className="text-[11px] text-slate-500 flex items-start gap-2">
          <Info className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          Simulation indicative basée sur le Tarif Douanier CEMAC et le barème DGD Cameroun en vigueur au 01/01/2026. Les droits définitifs sont liquidés par l'inspecteur des douanes après vérification physique et/ou documentaire. EVO-LOG décline toute responsabilité en cas de différence entre la simulation et la liquidation officielle.
        </p>
      </div>
    </div>
  );
}
