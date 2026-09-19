'use client';

import React, { useState } from 'react';
import {
  Calculator,
  Ship,
  Truck,
  Package,
  MapPin,
  ArrowRight,
  CheckCircle2,
  Clock,
  Info,
  DollarSign,
  Globe2,
  Zap
} from 'lucide-react';
import { toast } from 'sonner';

export default function B2BCotationsPage() {
  const [step, setStep] = useState(1);
  const [isCalculating, setIsCalculating] = useState(false);
  const [showQuote, setShowQuote] = useState(false);

  const [form, setForm] = useState({
    serviceType: 'TRANSIT_IMPORT',
    containerType: '40HC',
    containerCount: 1,
    cargoNature: '',
    portOfLoading: 'CNSHA', // Shanghai
    finalDestination: 'CMTNG', // N'Djamena via Douala
    incoterm: 'CIF',
    urgency: 'STANDARD',
    additionalServices: [] as string[],
  });

  const serviceTypes = [
    { value: 'TRANSIT_IMPORT', label: 'Transit Import Douala / Kribi', icon: '⚓', desc: 'Dédouanement + Manutention Portuaire + Livraison Finale' },
    { value: 'CORRIDOR_TCHAD', label: 'Corridor CEMAC - Tchad', icon: '🚛', desc: "Transport Douala ➔ N'Djamena via Ngaoundéré / Kousseri" },
    { value: 'CORRIDOR_RCA', label: 'Corridor CEMAC - Centrafrique', icon: '🌐', desc: 'Transport Douala ➔ Bangui via Garoua-Boulaï' },
    { value: 'WAREHOUSING', label: 'Entreposage Sous-Douane (MAD)', icon: '📦', desc: 'Stockage en Magasin et Aires de Dédouanement Agréées' },
    { value: 'DOMESTIC', label: 'Transport Domestique Cameroun', icon: '🚗', desc: 'Douala ↔ Yaoundé, Bafoussam, Garoua, Bertoua' },
  ];

  const containerTypes = [
    { value: '20DV', label: "20' Dry Van Standard", cbm: '33 m³', payload: '21,700 kg' },
    { value: '40DV', label: "40' Dry Van Standard", cbm: '67 m³', payload: '26,500 kg' },
    { value: '40HC', label: "40' High Cube", cbm: '76 m³', payload: '26,500 kg' },
    { value: '20REEFER', label: "20' Reefer Frigorifique", cbm: '28 m³', payload: '21,200 kg' },
    { value: '40OPENTOP', label: "40' Open Top (Hors-Gabarit)", cbm: '66 m³', payload: '26,300 kg' },
  ];

  const additionalServicesOptions = [
    { id: 'ASSURANCE', label: 'Assurance Tous Risques Transport (TRC)' },
    { id: 'EMPOTAGE', label: 'Empotage / Dépotage Marchandises' },
    { id: 'FUMIGATION', label: 'Fumigation Phytosanitaire Certifiée' },
    { id: 'PESEE', label: 'Pesée Pont-Bascule Certifiée' },
    { id: 'ESCORTE', label: 'Escorte Sécurisée Corridor CEMAC' },
  ];

  const toggleService = (id: string) => {
    setForm(prev => ({
      ...prev,
      additionalServices: prev.additionalServices.includes(id)
        ? prev.additionalServices.filter(s => s !== id)
        : [...prev.additionalServices, id]
    }));
  };

  const handleCalculate = (e: React.FormEvent) => {
    e.preventDefault();
    setIsCalculating(true);
    setTimeout(() => {
      setIsCalculating(false);
      setShowQuote(true);
      setStep(3);
    }, 1200);
  };

  // Dynamically calculated quote based on user parameters
  const quote = React.useMemo(() => {
    const is40 = form.containerType.includes('40');
    const isReefer = form.containerType.includes('REEFER');
    const containerMultiplier = isReefer ? 2.2 : (is40 ? 1.75 : 1.0);

    let transportBase = 1200000;
    let transitTimeStr = '12 à 15 jours ouvrables';
    if (form.serviceType === 'CORRIDOR_TCHAD' || form.finalDestination.includes('TNG') || form.finalDestination.includes('NDJ')) {
      transportBase = 2450000;
      transitTimeStr = '14 à 18 jours ouvrables';
    } else if (form.serviceType === 'CORRIDOR_RCA' || form.finalDestination.includes('BGF')) {
      transportBase = 2150000;
      transitTimeStr = '12 à 16 jours ouvrables';
    } else if (form.serviceType === 'DOMESTIC') {
      transportBase = 450000;
      transitTimeStr = '2 à 4 jours ouvrables';
    }

    const portHandling = Math.round(285000 * containerMultiplier);
    const transitFee = Math.round(420000 * (is40 ? 1.4 : 1.0));
    const customsDuties = Math.round(1850000 * containerMultiplier);
    const roadTransport = Math.round(transportBase * (is40 ? 1.5 : 1.0));
    const docFees = 45000;

    const breakdownItems = [
      { label: `Manutention Portuaire Quai PAD (${form.containerType})`, amount: portHandling },
      { label: 'Honoraires Déclarant Douane Agréé (CAD)', amount: transitFee },
      { label: 'Droits & Taxes Douanières Estimatives (SYDONIA)', amount: customsDuties },
      { label: `Transport Routier (${form.serviceType.replace('_', ' ')})`, amount: roadTransport },
      { label: 'Frais d\'Émission BAE & Connaissement', amount: docFees },
    ];

    if (form.additionalServices.includes('ASSURANCE')) {
      breakdownItems.push({ label: 'Assurance TRC Tous Risques Marchandise', amount: 85000 });
    }
    if (form.additionalServices.includes('ESCORTE')) {
      breakdownItems.push({ label: 'Escorte Sécurisée GPS & Douane Corridor', amount: 250000 });
    }
    if (form.additionalServices.includes('FUMIGATION')) {
      breakdownItems.push({ label: 'Traitement Phytosanitaire & Certificat', amount: 65000 });
    }
    if (form.additionalServices.includes('PESEE')) {
      breakdownItems.push({ label: 'Pesée VGM Certifiée Pont-Bascule', amount: 35000 });
    }
    if (form.additionalServices.includes('EMPOTAGE')) {
      breakdownItems.push({ label: 'Manutention Empotage / Dépotage Magasin', amount: 120000 });
    }

    const totalXAF = breakdownItems.reduce((acc, curr) => acc + curr.amount, 0);
    const totalEUR = Math.round(totalXAF / 655.957);

    const validDate = new Date();
    validDate.setDate(validDate.getDate() + 30);

    return {
      ref: `CADC-COT-2026-${Math.floor(Math.random() * 9000 + 1000)}`,
      validUntil: validDate.toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' }),
      breakdown: breakdownItems,
      totalXAF,
      totalEUR,
      currency: 'XAF (FCFA)',
      transitTime: transitTimeStr,
      notes: `Cotation dynamique calculée selon incoterm ${form.incoterm}, conteneur ${form.containerType} et destination.`
    };
  }, [form]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
        <h1 className="text-2xl font-black text-white flex items-center gap-2">
          <Calculator className="w-6 h-6 text-amber-400" /> Demande de Cotation Logistique
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Obtenez une estimation tarifaire instantanée pour vos opérations de transit, douane et transport en zone CEMAC
        </p>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center gap-3">
        {[
          { n: 1, label: 'Type de Service' },
          { n: 2, label: 'Détails Cargaison' },
          { n: 3, label: 'Devis Instantané' },
        ].map((s, idx) => (
          <React.Fragment key={s.n}>
            <div
              className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold cursor-pointer transition-all ${step >= s.n ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-slate-900 text-slate-500 border border-slate-800'}`}
              onClick={() => !showQuote && step >= s.n && setStep(s.n)}
            >
              <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-black ${step >= s.n ? 'bg-amber-500 text-slate-950' : 'bg-slate-800 text-slate-500'}`}>{s.n}</span>
              {s.label}
            </div>
            {idx < 2 && <ArrowRight className="w-4 h-4 text-slate-700 shrink-0" />}
          </React.Fragment>
        ))}
      </div>

      {/* STEP 1 */}
      {step === 1 && (
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-slate-200">1. Sélectionnez le type de service logistique</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {serviceTypes.map((svc) => (
              <button
                key={svc.value}
                onClick={() => setForm(f => ({ ...f, serviceType: svc.value }))}
                className={`p-4 rounded-2xl border text-left transition-all ${form.serviceType === svc.value ? 'bg-amber-500/10 border-amber-500/40 shadow-lg' : 'bg-slate-900 border-slate-800 hover:border-slate-700'}`}
              >
                <div className="text-2xl mb-2">{svc.icon}</div>
                <div className="text-xs font-bold text-slate-200">{svc.label}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">{svc.desc}</div>
              </button>
            ))}
          </div>

          <h2 className="text-sm font-bold text-slate-200 mt-6">2. Type et nombre de conteneurs</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {containerTypes.map((ct) => (
              <button
                key={ct.value}
                onClick={() => setForm(f => ({ ...f, containerType: ct.value }))}
                className={`p-4 rounded-2xl border text-left transition-all ${form.containerType === ct.value ? 'bg-blue-500/10 border-blue-500/40' : 'bg-slate-900 border-slate-800 hover:border-slate-700'}`}
              >
                <div className="text-xs font-bold text-slate-200">{ct.label}</div>
                <div className="text-[11px] text-slate-400 mt-1">CBM: {ct.cbm} • Payload: {ct.payload}</div>
              </button>
            ))}
          </div>

          <button
            onClick={() => setStep(2)}
            className="mt-4 px-6 py-3 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-sm rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all hover:from-amber-400 hover:to-yellow-300"
          >
            Continuer vers les détails <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* STEP 2 */}
      {step === 2 && (
        <form onSubmit={handleCalculate} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Nature de la Marchandise</label>
              <input
                type="text"
                value={form.cargoNature}
                onChange={e => setForm(f => ({ ...f, cargoNature: e.target.value }))}
                placeholder="Ex: Équipements industriels, Céréales, Produits chimiques..."
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Nombre de Conteneurs</label>
              <input
                type="number"
                min={1}
                max={50}
                value={form.containerCount}
                onChange={e => setForm(f => ({ ...f, containerCount: parseInt(e.target.value) }))}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-300 uppercase mb-2">Services Additionnels</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {additionalServicesOptions.map((opt) => (
                <label key={opt.id} className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all ${form.additionalServices.includes(opt.id) ? 'bg-amber-500/10 border-amber-500/30 text-amber-300' : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'}`}>
                  <input
                    type="checkbox"
                    checked={form.additionalServices.includes(opt.id)}
                    onChange={() => toggleService(opt.id)}
                    className="rounded border-slate-700 bg-slate-950 text-amber-500"
                  />
                  <span className="text-xs font-medium">{opt.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <button type="button" onClick={() => setStep(1)} className="px-5 py-3 bg-slate-800 text-slate-300 font-bold text-sm rounded-xl border border-slate-700">
              Retour
            </button>
            <button
              type="submit"
              disabled={isCalculating}
              className="px-8 py-3 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-sm rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all disabled:opacity-70"
            >
              {isCalculating ? <><Zap className="w-4 h-4 animate-pulse" /> Calcul en cours...</> : <><Calculator className="w-4 h-4" /> Calculer le Devis Instantané</>}
            </button>
          </div>
        </form>
      )}

      {/* STEP 3: Quote Result */}
      {step === 3 && showQuote && (
        <div className="space-y-4">
          <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-amber-500/30 rounded-3xl p-6 sm:p-8 shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span className="text-xs font-mono font-bold text-emerald-400 uppercase">Devis Généré avec Succès</span>
                </div>
                <h2 className="text-xl font-black text-white">Référence : {quote.ref}</h2>
                <p className="text-xs text-slate-400 mt-0.5">Validité : jusqu'au {quote.validUntil} • Délai de transit estimé : {quote.transitTime}</p>
              </div>
              <button
                onClick={() => toast.success('Devis téléchargé en PDF')}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl border border-slate-700 flex items-center gap-2"
              >
                Télécharger PDF
              </button>
            </div>

            {/* Cost Breakdown */}
            <div className="space-y-2 mb-6">
              {quote.breakdown.map((line, idx) => (
                <div key={idx} className="flex items-center justify-between py-2 border-b border-slate-800/60 text-xs">
                  <span className="text-slate-400">{line.label}</span>
                  <span className="font-mono font-bold text-slate-200">{line.amount.toLocaleString()} XAF</span>
                </div>
              ))}
            </div>

            {/* Total */}
            <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-slate-300 uppercase">Total Estimatif</div>
                <div className="text-3xl font-black text-amber-300 font-mono mt-0.5">
                  {quote.totalXAF.toLocaleString()} FCFA
                </div>
                <div className="text-xs text-slate-400 font-mono">≈ {quote.totalEUR.toLocaleString()} EUR</div>
              </div>
              <button
                onClick={() => toast.success('Demande de confirmation du devis envoyée à votre gestionnaire de compte.')}
                className="px-6 py-3 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-sm rounded-xl shadow-lg"
              >
                Confirmer & Commander
              </button>
            </div>

            <p className="text-[11px] text-slate-500 mt-3 flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5" /> {quote.notes}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
