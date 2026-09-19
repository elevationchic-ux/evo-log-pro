'use client';

import React, { useState } from 'react';
import {
  Calculator, User, Download, ChevronDown,
  DollarSign, Percent, FileText, CheckCircle2, AlertTriangle,
  Printer, Send
} from 'lucide-react';
import { toast } from 'sonner';

// OHADA/Cameroon payroll engine
function computePayroll(salaireBase: number, anciennete: number, primes: number, heuresSup: number) {
  const indemniteAnciennete = salaireBase * (anciennete >= 3 ? Math.min(anciennete * 0.02, 0.25) : 0);
  const heuresSupMontant = heuresSup * (salaireBase / 208) * 1.3; // majorées 30%
  const salairesBrut = salaireBase + indemniteAnciennete + primes + heuresSupMontant;

  // CNPS Salarié: 4.2% sur salaire brut plafonné (750 000 XAF)
  const plafondCNPS = 750000;
  const baseCNPS = Math.min(salairesBrut, plafondCNPS);
  const cnpsSalarie = baseCNPS * 0.042;

  // IRPP (barème progressif simplifié Cameroun 2026)
  const salaireImposable = salairesBrut - cnpsSalarie - (salairesBrut * 0.30); // déduction 30% frais professionnels
  let irpp = 0;
  if (salaireImposable > 0 && salaireImposable <= 2000000) irpp = salaireImposable * 0.10;
  else if (salaireImposable <= 3000000) irpp = 200000 + (salaireImposable - 2000000) * 0.165;
  else if (salaireImposable <= 5000000) irpp = 365000 + (salaireImposable - 3000000) * 0.25;
  else irpp = 865000 + (salaireImposable - 5000000) * 0.35;

  const irppMensuel = irpp / 12;

  // CAC: 10% de l'IRPP
  const cac = irppMensuel * 0.10;

  // Total retenues salariales
  const totalRetenues = cnpsSalarie + irppMensuel + cac;
  const salaireNet = salairesBrut - totalRetenues;

  // Charges patronales
  const cnpsPatronal = salairesBrut * 0.1675; // AT+VF+PS+AF
  const fne = salairesBrut * 0.01;
  const rav = salairesBrut * 0.005;
  const totalChargesPatronales = cnpsPatronal + fne + rav;

  return {
    salairesBrut,
    indemniteAnciennete,
    heuresSupMontant,
    cnpsSalarie,
    irppMensuel,
    cac,
    totalRetenues,
    salaireNet,
    cnpsPatronal,
    fne,
    rav,
    totalChargesPatronales,
    coutEmployeur: salairesBrut + totalChargesPatronales,
  };
}

export default function RHPaiePage() {
  const [selectedEmp, setSelectedEmp] = useState('EMP-002');
  const [salaireBase, setSalaireBase] = useState(720000);
  const [anciennete, setAnciennete] = useState(5);
  const [primes, setPrimes] = useState(50000);
  const [heuresSup, setHeuresSup] = useState(8);
  const [showBulletin, setShowBulletin] = useState(false);

  const employees = [
    { id: 'EMP-001', nom: 'Essama Jean-Baptiste', poste: 'Agent Transit Senior', salaire: 580000, anciennete: 7 },
    { id: 'EMP-002', nom: 'Nkeng Marie-Claire', poste: 'CAD Agréée', salaire: 720000, anciennete: 5 },
    { id: 'EMP-003', nom: 'Moukouri Jean-Paul', poste: 'Chauffeur Long-Courrier', salaire: 420000, anciennete: 6 },
    { id: 'EMP-004', nom: 'Mbida Paul', poste: 'Gestionnaire WMS', salaire: 450000, anciennete: 4 },
    { id: 'EMP-007', nom: 'Ayuk Rose', poste: 'Comptable OHADA', salaire: 390000, anciennete: 3 },
  ];

  const paie = computePayroll(salaireBase, anciennete, primes, heuresSup);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-white flex items-center gap-2">
          <Calculator className="w-6 h-6 text-amber-400" /> Moteur de Paie OHADA Cameroun
        </h1>
        <p className="text-xs text-slate-400 mt-0.5">Calcul IRPP (progressif) · CNPS Salarié + Patronal · CAC 10% · FNE 1% · RAV 0.5% · Heures supplémentaires</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Inputs */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl space-y-5">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <User className="w-4 h-4 text-blue-400" /> Paramètres de la Fiche de Paie
          </h2>

          {/* Employee selector */}
          <div>
            <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Employé</label>
            <select
              value={selectedEmp}
              onChange={e => {
                const emp = employees.find(em => em.id === e.target.value);
                if (emp) { setSelectedEmp(emp.id); setSalaireBase(emp.salaire); setAnciennete(emp.anciennete); }
              }}
              className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500"
            >
              {employees.map(emp => (
                <option key={emp.id} value={emp.id}>{emp.nom}  {emp.poste}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Salaire de Base (XAF)</label>
              <input type="number" value={salaireBase} onChange={e => setSalaireBase(+e.target.value)}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-mono" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Ancienneté (années)</label>
              <input type="number" value={anciennete} onChange={e => setAnciennete(+e.target.value)} min={0}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-mono" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Primes & Indemnités (XAF)</label>
              <input type="number" value={primes} onChange={e => setPrimes(+e.target.value)}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-mono" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Heures Supp. (h)</label>
              <input type="number" value={heuresSup} onChange={e => setHeuresSup(+e.target.value)} min={0}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-mono" />
            </div>
          </div>

          <button
            onClick={() => setShowBulletin(true)}
            className="w-full py-3 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-sm rounded-xl flex items-center justify-center gap-2 shadow-lg"
          >
            <Calculator className="w-4 h-4" /> Calculer & Générer Bulletin
          </button>
        </div>

        {/* Pay Result */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-emerald-400" /> Résultat de Paie (Calcul Temps Réel)
          </h2>

          {/* GAINS section */}
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase mb-2">ÉLÉMENTS DE RÉMUNÉRATION</div>
            <div className="space-y-1">
              {[
                { label: 'Salaire de Base', amount: salaireBase },
                { label: `Indemnité d'Ancienneté (${anciennete >= 3 ? Math.min(anciennete * 2, 25) : 0}%)`, amount: paie.indemniteAnciennete },
                { label: 'Primes & Indemnités Diverses', amount: primes },
                { label: `Heures Supplémentaires (${heuresSup}h × 130%)`, amount: paie.heuresSupMontant },
              ].map((l, i) => (
                <div key={i} className="flex justify-between text-xs py-1">
                  <span className="text-slate-400">{l.label}</span>
                  <span className="font-mono text-emerald-400">+{Math.round(l.amount).toLocaleString()} XAF</span>
                </div>
              ))}
              <div className="flex justify-between text-xs py-2 border-t border-slate-800 font-bold">
                <span className="text-slate-200">SALAIRE BRUT</span>
                <span className="font-mono text-white">{Math.round(paie.salairesBrut).toLocaleString()} XAF</span>
              </div>
            </div>
          </div>

          {/* COTISATIONS */}
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase mb-2">RETENUES SALARIALES</div>
            <div className="space-y-1">
              {[
                { label: 'CNPS Part Salarié (4.2% sur brut plafonné 750k)', amount: paie.cnpsSalarie },
                { label: 'IRPP (barème progressif mensuel)', amount: paie.irppMensuel },
                { label: 'CAC (10% de l\'IRPP)', amount: paie.cac },
              ].map((l, i) => (
                <div key={i} className="flex justify-between text-xs py-1">
                  <span className="text-slate-400">{l.label}</span>
                  <span className="font-mono text-red-400">-{Math.round(l.amount).toLocaleString()} XAF</span>
                </div>
              ))}
            </div>
          </div>

          {/* NET */}
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4">
            <div className="flex justify-between items-center">
              <div>
                <div className="text-[11px] text-slate-400 uppercase font-bold">SALAIRE NET À PAYER</div>
                <div className="text-2xl font-black text-amber-300 font-mono mt-0.5">
                  {Math.round(paie.salaireNet).toLocaleString()} XAF
                </div>
              </div>
              <div className="text-right">
                <div className="text-[10px] text-slate-500">Coût total employeur</div>
                <div className="text-sm font-black text-slate-300 font-mono">{Math.round(paie.coutEmployeur).toLocaleString()} XAF</div>
              </div>
            </div>
          </div>

          {/* Charges patronales */}
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase mb-2">CHARGES PATRONALES</div>
            <div className="space-y-1">
              {[
                { label: 'CNPS Patronal (AT+VF+PS+AF = 16.75%)', amount: paie.cnpsPatronal },
                { label: 'FNE  Fonds National Emploi (1%)', amount: paie.fne },
                { label: 'RAV  Redevance Audiovisuelle (0.5%)', amount: paie.rav },
              ].map((l, i) => (
                <div key={i} className="flex justify-between text-xs py-0.5">
                  <span className="text-slate-500">{l.label}</span>
                  <span className="font-mono text-slate-400">{Math.round(l.amount).toLocaleString()} XAF</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <button onClick={() => toast.success('Bulletin de paie généré en PDF')} className="flex-1 py-2.5 bg-slate-800 border border-slate-700 text-slate-200 font-bold text-xs rounded-xl flex items-center justify-center gap-2 hover:bg-slate-700">
              <Printer className="w-3.5 h-3.5" /> Imprimer Bulletin
            </button>
            <button onClick={() => toast.success('Bulletin envoyé par email à l\'employé')} className="flex-1 py-2.5 bg-blue-500/10 border border-blue-500/30 text-blue-400 font-bold text-xs rounded-xl flex items-center justify-center gap-2 hover:bg-blue-500/20">
              <Send className="w-3.5 h-3.5" /> Envoyer Email
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
