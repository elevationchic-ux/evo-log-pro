'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { PenLine, CheckCircle2, RotateCcw, Send, Package, MapPin, Calendar, Truck, Loader2, Inbox } from 'lucide-react';
import { toast } from 'sonner';
import { transportAPI } from '@/lib/api-client';

interface Mission {
  id: number;
  reference: string;
  statut: string;
  type_mission?: string;
  point_depart?: string;
  point_arrivee?: string;
  distance_km?: number;
  notes?: string;
  date_debut_prevue?: string;
  date_fin_prevue?: string;
  camion?: { immatriculation?: string; marque?: string; modele?: string };
}

const fmtDate = (iso?: string) => {
  if (!iso) return 'Date non planifiée';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' });
};

export default function MobileChauffeurEPODPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasInk, setHasInk] = useState(false);
  const [signed, setSigned] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [observation, setObservation] = useState('');
  const [nomReceptionnaire, setNomReceptionnaire] = useState('');
  const [etatMarchandise, setEtatMarchandise] = useState<'BON' | 'ENDOMMAGE' | 'MANQUANT'>('BON');
  const [mission, setMission] = useState<Mission | null>(null);
  const [loading, setLoading] = useState(true);
  const [podRef, setPodRef] = useState('');

  const fetchMission = useCallback(async () => {
    try {
      const res: any = await transportAPI.getMissions({ limit: 50, statut: 'en_cours' });
      const body = res.data ?? res;
      const list: Mission[] = Array.isArray(body) ? body : (body.items || []);
      const active = list.find(m => m.statut === 'en_cours')
        || list.find(m => m.statut === 'planifiee')
        || list[0]
        || null;
      setMission(active);
    } catch {
      setMission(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMission();
  }, [fetchMission]);

  const getPos = (e: React.TouchEvent | React.MouseEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    if ('touches' in e) {
      return { x: e.touches[0].clientX - rect.left, y: e.touches[0].clientY - rect.top };
    }
    return { x: (e as React.MouseEvent).clientX - rect.left, y: (e as React.MouseEvent).clientY - rect.top };
  };

  const startDraw = (e: React.TouchEvent | React.MouseEvent) => {
    const canvas = canvasRef.current;
    if (!canvas || signed) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const { x, y } = getPos(e);
    ctx.beginPath();
    ctx.moveTo(x, y);
    setIsDrawing(true);
    e.preventDefault();
  };

  const draw = (e: React.TouchEvent | React.MouseEvent) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const { x, y } = getPos(e);
    ctx.lineTo(x, y);
    ctx.strokeStyle = '#60a5fa';
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.stroke();
    setHasInk(true);
    e.preventDefault();
  };

  const stopDraw = () => setIsDrawing(false);

  const clearSignature = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx?.clearRect(0, 0, canvas.width, canvas.height);
    setHasInk(false);
    setSigned(false);
  };

  const validateEPOD = async () => {
    if (!mission) {
      toast.error('Aucune mission à livrer.');
      return;
    }
    if (!nomReceptionnaire.trim()) {
      toast.error('Le nom du réceptionnaire est requis.');
      return;
    }
    if (!hasInk) {
      toast.error('Le réceptionnaire doit signer avant validation.');
      return;
    }
    const canvas = canvasRef.current;
    const signature = canvas ? canvas.toDataURL('image/png') : '';
    setSubmitting(true);
    try {
      const note = `État: ${etatMarchandise}${observation.trim() ? `  ${observation.trim()}` : ''}`;
      const res: any = await transportAPI.livrerMission(mission.id, {
        signature,
        nom_receptionnaire: nomReceptionnaire.trim(),
        note,
      });
      const body = res?.data ?? res;
      const ref = body?.mission?.reference ?? mission.reference;
      setPodRef(`e-POD ${ref}`);
      setSigned(true);
      const factMsg = body?.facture_auto
        ? ` Facture ${body.facture_auto.numero_facture} émise.`
        : (body?.facturation_note ? ` ${body.facturation_note}` : '');
      toast.success(`e-POD transmis, mission clôturée.${factMsg}`);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || "Échec de la transmission de l'e-POD.";
      toast.error(typeof detail === 'string' ? detail : "Échec de la transmission de l'e-POD.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-emerald-400" />
      </div>
    );
  }

  if (!mission) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100">
        <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <PenLine className="w-5 h-5 text-emerald-400" />
            <div className="text-xs font-black text-slate-100">e-POD  Bon de Livraison Électronique</div>
          </div>
        </div>
        <div className="p-6 max-w-lg mx-auto text-center space-y-3">
          <Inbox className="w-10 h-10 text-slate-600 mx-auto" />
          <div className="text-sm font-bold text-slate-300">Aucune mission en cours à livrer</div>
          <p className="text-[11px] text-slate-500">
            L'e-POD se signature une fois une mission assignée et en route. Aucune donnée de livraison fictive n'est affichée.
          </p>
          <button onClick={fetchMission}
            className="mt-2 px-4 py-2 rounded-xl bg-slate-800 text-slate-200 text-xs font-bold border border-slate-700 hover:bg-slate-700 transition-colors cursor-pointer">
            Réactualiser
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <PenLine className="w-5 h-5 text-emerald-400" />
          <div>
            <div className="text-xs font-black text-slate-100">e-POD  Bon de Livraison Électronique</div>
            <div className="text-[11px] font-mono text-emerald-400">Mission : {mission.reference}</div>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4 max-w-lg mx-auto">
        {/* Infos livraison */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-2">
          <div className="text-[11px] text-slate-500 uppercase font-bold tracking-wider">Détails de la livraison</div>
          <div className="flex items-center gap-2 text-xs">
            <Package className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span className="text-slate-300">{mission.type_mission ? `Mission ${mission.type_mission}` : 'Type de mission non renseigné'}</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <MapPin className="w-3.5 h-3.5 text-red-400 shrink-0" />
            <span className="text-slate-300">{mission.point_arrivee || 'Destination non renseignée'}</span>
          </div>
          {mission.camion?.immatriculation && (
            <div className="flex items-center gap-2 text-xs">
              <Truck className="w-3.5 h-3.5 text-blue-400 shrink-0" />
              <span className="text-slate-300">{mission.camion.immatriculation}{mission.camion.marque ? `  ${mission.camion.marque}` : ''}</span>
            </div>
          )}
          <div className="flex items-center gap-2 text-xs">
            <Calendar className="w-3.5 h-3.5 text-blue-400 shrink-0" />
            <span className="text-slate-300">{fmtDate(mission.date_fin_prevue)}</span>
          </div>
        </div>

        {/* Réceptionnaire */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="text-[11px] text-slate-500 uppercase font-bold tracking-wider mb-2">Réceptionnaire</div>
          <input
            value={nomReceptionnaire}
            onChange={e => !signed && setNomReceptionnaire(e.target.value)}
            disabled={signed}
            placeholder="Nom et qualité de la personne qui réceptionne"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500 disabled:opacity-50"
          />
        </div>

        {/* État marchandise */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="text-[11px] text-slate-500 uppercase font-bold tracking-wider mb-2">État à la livraison</div>
          <div className="grid grid-cols-3 gap-2">
            {(['BON', 'ENDOMMAGE', 'MANQUANT'] as const).map(etat => (
              <button key={etat} onClick={() => !signed && setEtatMarchandise(etat)}
                className={`py-2 rounded-xl text-[11px] font-black border transition-all cursor-pointer ${etatMarchandise === etat
                  ? etat === 'BON' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50'
                    : etat === 'ENDOMMAGE' ? 'bg-amber-500/20 text-amber-400 border-amber-500/50'
                      : 'bg-red-500/20 text-red-400 border-red-500/50'
                  : 'bg-slate-800 text-slate-500 border-slate-700'
                  }`}>{etat}</button>
            ))}
          </div>
        </div>

        {/* Observations */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="text-[11px] text-slate-500 uppercase font-bold tracking-wider mb-2">Observations (optionnel)</div>
          <textarea value={observation} onChange={e => setObservation(e.target.value)} disabled={signed} rows={2}
            placeholder="Ex: 2 colis avec emballage légèrement froissé..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500 resize-none disabled:opacity-50"
          />
        </div>

        {/* Zone signature */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="text-[11px] text-slate-500 uppercase font-bold tracking-wider">
              Signature du Réceptionnaire
            </div>
            {!signed && hasInk && (
              <button onClick={clearSignature}
                className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-200 cursor-pointer">
                <RotateCcw className="w-3 h-3" /> Effacer
              </button>
            )}
          </div>
          <div className={`rounded-xl overflow-hidden border ${signed ? 'border-emerald-500/50' : 'border-slate-700'}`}>
            <canvas ref={canvasRef} width={360} height={140} className="w-full touch-none bg-slate-950 cursor-crosshair"
              onMouseDown={startDraw} onMouseMove={draw} onMouseUp={stopDraw} onMouseLeave={stopDraw}
              onTouchStart={startDraw} onTouchMove={draw} onTouchEnd={stopDraw}
            />
          </div>
          {!signed && <p className="text-[11px] text-slate-400 mt-1 text-center">← Faites signer le réceptionnaire ici</p>}
          {signed && <p className="text-[11px] text-emerald-400 mt-1 text-center flex items-center justify-center gap-1"><CheckCircle2 className="w-3 h-3" /> Signature enregistrée</p>}
        </div>

        {/* Valider */}
        {!signed ? (
          <button onClick={validateEPOD} disabled={submitting}
            className="w-full py-4 bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-black text-sm rounded-2xl shadow-lg shadow-emerald-500/20 hover:opacity-90 transition-opacity cursor-pointer active:scale-95 disabled:opacity-60 flex items-center justify-center gap-2">
            {submitting
              ? <Loader2 className="w-5 h-5 animate-spin" />
              : <Send className="w-5 h-5" />}
            {submitting ? "Transmission…" : "Valider et transmettre l'e-POD"}
          </button>
        ) : (
          <div className="py-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl text-center">
            <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto mb-1" />
            <div className="text-sm font-black text-emerald-400">e-POD validé et transmis</div>
            <div className="text-[11px] text-slate-400 mt-0.5 font-mono">{podRef || `e-POD ${mission.reference}`}</div>
          </div>
        )}
      </div>
    </div>
  );
}
