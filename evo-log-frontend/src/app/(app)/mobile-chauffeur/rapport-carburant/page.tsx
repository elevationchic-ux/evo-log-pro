'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Fuel, AlertTriangle, Camera, CheckCircle2, Send, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { transportAPI } from '@/lib/api-client';

interface Mission {
  id: number;
  reference: string;
  statut: string;
  camion?: { immatriculation?: string; marque?: string; modele?: string };
}

const fmtDateTime = (iso?: string) => {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' });
};

export default function MobileChauffeurCarburantPage() {
  const [form, setForm] = useState({
    km_depart: '',
    km_arrivee: '',
    litres_plein: '',
    station: '',
    montant_xaf: '',
    anomalie: false,
    observation_anomalie: '',
  });
  const [mission, setMission] = useState<Mission | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [receipt, setReceipt] = useState<{ ref: string; date: string } | null>(null);

  const fetchActiveMission = useCallback(async () => {
    try {
      const res: any = await transportAPI.getMissions({ limit: 50, statut: 'en_cours' });
      const body = res.data ?? res;
      const list: Mission[] = Array.isArray(body) ? body : (body.items || []);
      const active = list.find(m => m.statut === 'en_cours') || list[0] || null;
      setMission(active);
    } catch {
      setMission(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchActiveMission();
  }, [fetchActiveMission]);

  const vehicule = mission?.camion?.immatriculation || '';

  const kmParcourus = (form.km_arrivee && form.km_depart)
    ? parseInt(form.km_arrivee) - parseInt(form.km_depart)
    : 0;
  const consoL100 = form.litres_plein && kmParcourus > 0
    ? ((parseFloat(form.litres_plein) / kmParcourus) * 100).toFixed(1)
    : '';

  const SEUIL_ALERTE_L100 = 45; // Alerte si > 45L/100km

  const handleSubmit = async () => {
    if (!form.km_arrivee || !form.litres_plein || !form.station) {
      toast.error('Veuillez remplir les champs obligatoires (station, litres, KM arrivée)');
      return;
    }
    setSubmitting(true);
    try {
      const notes: string[] = [];
      if (form.anomalie && form.observation_anomalie.trim()) {
        notes.push(`Anomalie : ${form.observation_anomalie.trim()}`);
      }
      if (consoL100 && parseFloat(consoL100) > SEUIL_ALERTE_L100) {
        notes.push(`Alerte consommation : ${consoL100} L/100km (seuil ${SEUIL_ALERTE_L100})`);
      }
      const payload: Record<string, unknown> = {
        station: form.station.trim(),
        litres: parseFloat(form.litres_plein),
        kilometrage: parseInt(form.km_arrivee),
        notes: notes.join(' | ') || undefined,
      };
      if (form.km_depart) payload.index_precedent = parseInt(form.km_depart);
      if (form.montant_xaf) payload.montant = parseFloat(form.montant_xaf);
      if (mission) payload.mission_id = mission.id;
      if (vehicule) payload.immatriculation = vehicule;

      const res: any = await transportAPI.createTicketCarburant(payload);
      const body = res?.data ?? res;
      const ref = body?.numero_ticket || (body?.id ? `Ticket #${body.id}` : 'Ticket enregistré');
      setReceipt({ ref, date: fmtDateTime(body?.date_plein) || new Date().toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' }) });
      setSubmitted(true);
      if (consoL100 && parseFloat(consoL100) > SEUIL_ALERTE_L100) {
        toast.warning(`Consommation anormale enregistrée : ${consoL100} L/100km — signal FuelGuard consigné`);
      } else {
        toast.success('Rapport carburant transmis au dispatching');
      }
    } catch (err: any) {
      const detail = err?.response?.data?.detail || "Échec de l'enregistrement du rapport carburant.";
      toast.error(typeof detail === 'string' ? detail : "Échec de l'enregistrement du rapport carburant.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-orange-400" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <Fuel className="w-5 h-5 text-orange-400" />
          <div>
            <div className="text-xs font-black text-slate-100">Rapport Carburant & Anti-Siphonnage</div>
            <div className="text-[11px] font-mono text-orange-400">T-Code : KDRV_CBT  {vehicule || 'Véhicule non lié à une mission'}</div>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4 max-w-lg mx-auto">
        {!mission && (
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-3 text-[11px] text-amber-300">
            Aucune mission en cours : le rapport sera enregistré sans rattachement de mission.
          </div>
        )}

        {/* Alerte seuil si dépassé */}
        {consoL100 !== '' && parseFloat(consoL100) > SEUIL_ALERTE_L100 && (
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
          <div className="text-[11px] text-slate-500 uppercase font-bold tracking-wider mb-3">Kilométrage</div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] text-slate-400 font-bold">KM Départ</label>
              <input value={form.km_depart} onChange={e => setForm({ ...form, km_depart: e.target.value })}
                type="number" placeholder="index précédent" disabled={submitted}
                className="w-full mt-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-orange-500 font-mono disabled:opacity-50" />
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
          <div className="text-[11px] text-slate-500 uppercase font-bold tracking-wider mb-3">Ravitaillement Carburant</div>
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
          <button onClick={handleSubmit} disabled={submitting}
            className="w-full py-4 bg-gradient-to-r from-orange-600 to-amber-500 text-white font-black text-sm rounded-2xl shadow-lg shadow-orange-500/20 hover:opacity-90 transition-opacity cursor-pointer active:scale-95 disabled:opacity-60 flex items-center justify-center gap-2">
            {submitting
              ? <Loader2 className="w-5 h-5 animate-spin" />
              : <Send className="w-5 h-5" />}
            {submitting ? "Transmission…" : "Transmettre le rapport carburant"}
          </button>
        ) : (
          <div className="py-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl text-center">
            <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto mb-1" />
            <div className="text-sm font-black text-emerald-400">Rapport transmis au dispatching</div>
            <div className="text-[11px] text-slate-400 mt-0.5 font-mono">
              {receipt?.ref}{receipt?.date ? `  ${receipt.date}` : ''}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
