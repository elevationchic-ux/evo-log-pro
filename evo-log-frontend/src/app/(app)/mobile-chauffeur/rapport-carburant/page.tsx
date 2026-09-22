'use client';

import React, { useState } from 'react';
import { Fuel, AlertTriangle, Camera, CheckCircle2, Send } from 'lucide-react';
import { toast } from 'sonner';

export default function MobileChauffeurCarburantPage() {
  const [form, setForm] = useState({
    vehicule: 'CMR-TK-4521',
    km_depart: 289500,
    km_arrivee: '',
    litres_plein: '',
    station: '',
    montant_xaf: '',
    km_parcourus: 0,
    anomalie: false,
    observation_anomalie: '',
  });
  const [submitted, setSubmitted] = useState(false);

  const kmParcourus = form.km_arrivee ? parseInt(form.km_arrivee) - form.km_depart : 0;
  const consoL100 = form.litres_plein && kmParcourus > 0 ?
    ((parseFloat(form.litres_plein) / kmParcourus) * 100).toFixed(1) : '';

  const SEUIL_ALERTE_L100 = 45; // Alerte si > 45L/100km

  const handleSubmit = () => {
    if (!form.km_arrivee || !form.litres_plein || !form.station) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }
    if (parseFloat(consoL100) > SEUIL_ALERTE_L100) {
      toast.warning(`⚠️ Consommation anormale détectée : ${consoL100} L/100km  Signal anti-siphonnage envoyé`);
    } else {
      toast.error("La transmission du rapport carburant n'est pas encore raccordée à l'API.");
    }
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <Fuel className="w-5 h-5 text-orange-400" />
          <div>
            <div className="text-xs font-black text-slate-100">Rapport Carburant & Anti-Siphonnage</div>
            <div className="text-[10px] font-mono text-orange-400">T-Code : KDRV_CBT  {form.vehicule}</div>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4 max-w-lg mx-auto">
        {/* Alerte seuil si dépassé */}
        {parseFloat(consoL100) > SEUIL_ALERTE_L100 && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-3 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
            <div>
              <div className="text-xs font-black text-red-400">Consommation anormale détectée !</div>
              <div className="text-[11px] text-slate-400">Seuil : 45 L/100km  Mesurée : {consoL100} L/100km</div>
            </div>
          </div>
        )}

        {/* Kilométrage */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-3">Kilométrage</div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] text-slate-400 font-bold">KM Départ</label>
              <div className="mt-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-400 font-mono">
                {form.km_depart.toLocaleString()} km
              </div>
            </div>
            <div>
              <label className="text-[11px] text-slate-400 font-bold">KM Arrivée *</label>
              <input value={form.km_arrivee} onChange={e => setForm({ ...form, km_arrivee: e.target.value })}
                type="number" placeholder="ex: 289746" disabled={submitted}
                className="w-full mt-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-orange-500 font-mono disabled:opacity-50" />
            </div>
          </div>
          {kmParcourus > 0 && (
            <div className="mt-2 text-xs text-blue-400 font-mono font-bold">
              Distance parcourue : {kmParcourus} km
            </div>
          )}
        </div>

        {/* Ravitaillement */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-3">Ravitaillement Carburant</div>
          <div className="space-y-3">
            <div>
              <label className="text-[11px] text-slate-400 font-bold">Station-Service *</label>
              <input value={form.station} onChange={e => setForm({ ...form, station: e.target.value })}
                placeholder="Ex: Total Bonabéri  N1 Douala" disabled={submitted}
                className="w-full mt-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-orange-500 disabled:opacity-50" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] text-slate-400 font-bold">Litres *</label>
                <input value={form.litres_plein} onChange={e => setForm({ ...form, litres_plein: e.target.value })}
                  type="number" placeholder="ex: 280" disabled={submitted}
                  className="w-full mt-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-orange-500 font-mono disabled:opacity-50" />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 font-bold">Montant (XAF) *</label>
                <input value={form.montant_xaf} onChange={e => setForm({ ...form, montant_xaf: e.target.value })}
                  type="number" placeholder="ex: 270000" disabled={submitted}
                  className="w-full mt-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-orange-500 font-mono disabled:opacity-50" />
              </div>
            </div>
            {consoL100 !== '' && (
              <div className={`p-2 rounded-xl text-xs font-mono font-black text-center ${parseFloat(consoL100) > SEUIL_ALERTE_L100 ? 'bg-red-500/10 text-red-400' : 'bg-emerald-500/10 text-emerald-400'
                }`}>
                Consommation calculée : {consoL100} L/100 km
                {parseFloat(consoL100) > SEUIL_ALERTE_L100 && ' ⚠️'}
              </div>
            )}
          </div>
        </div>

        {/* Anomalie */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.anomalie} onChange={e => setForm({ ...form, anomalie: e.target.checked })}
              disabled={submitted} className="w-4 h-4 rounded accent-orange-500" />
            <span className="text-xs font-bold text-slate-300">Signaler une anomalie (siphonnage, panne, incident)</span>
          </label>
          {form.anomalie && (
            <textarea value={form.observation_anomalie} onChange={e => setForm({ ...form, observation_anomalie: e.target.value })}
              disabled={submitted} rows={2} placeholder="Décrivez l'anomalie observée..."
              className="w-full mt-2 px-3 py-2 bg-slate-950 border border-red-500/30 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-red-400 resize-none disabled:opacity-50"
            />
          )}
        </div>

        {/* Photo bon */}
        <button onClick={() => toast.info('Ouverture de la caméra pour photographier le ticket')}
          disabled={submitted}
          className="w-full py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs rounded-2xl flex items-center justify-center gap-2 transition-colors cursor-pointer disabled:opacity-50">
          <Camera className="w-4 h-4 text-blue-400" /> Photographier le ticket de caisse
        </button>

        {!submitted ? (
          <button onClick={handleSubmit}
            className="w-full py-4 bg-gradient-to-r from-orange-600 to-amber-500 text-white font-black text-sm rounded-2xl shadow-lg shadow-orange-500/20 hover:opacity-90 transition-opacity cursor-pointer active:scale-95 flex items-center justify-center gap-2">
            <Send className="w-5 h-5" /> Transmettre le rapport carburant
          </button>
        ) : (
          <div className="py-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl text-center">
            <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto mb-1" />
            <div className="text-sm font-black text-emerald-400">Rapport transmis au dispatching</div>
            <div className="text-[10px] text-slate-400 mt-0.5 font-mono">27/08/2026  {form.vehicule}</div>
          </div>
        )}
      </div>
    </div>
  );
}
