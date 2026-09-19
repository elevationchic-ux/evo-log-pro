'use client';

import React, { useState, useRef } from 'react';
import { PenLine, CheckCircle2, RotateCcw, Send, Package, MapPin, Calendar } from 'lucide-react';
import { toast } from 'sonner';

export default function MobileChauffeurEPODPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [signed, setSigned] = useState(false);
  const [observation, setObservation] = useState('');
  const [etatMarchandise, setEtatMarchandise] = useState<'BON' | 'ENDOMMAGE' | 'MANQUANT'>('BON');

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
    e.preventDefault();
  };

  const stopDraw = () => setIsDrawing(false);

  const clearSignature = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx?.clearRect(0, 0, canvas.width, canvas.height);
    setSigned(false);
  };

  const validateEPOD = () => {
    setSigned(true);
    toast.success('✅ e-POD signé et transmis au dispatching EVO-LOG !');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <PenLine className="w-5 h-5 text-emerald-400" />
          <div>
            <div className="text-xs font-black text-slate-100">e-POD  Bon de Livraison Électronique</div>
            <div className="text-[10px] font-mono text-emerald-400">T-Code : KDRV_POD  MIS-2026-01847</div>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4 max-w-lg mx-auto">
        {/* Infos livraison */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-2">
          <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Détails de la livraison</div>
          <div className="flex items-center gap-2 text-xs">
            <Package className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-300">32T  Matières premières (houblon)</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <MapPin className="w-3.5 h-3.5 text-red-400" />
            <span className="text-slate-300">Entrepôt Brasseries  Zone Industrielle Yaoundé</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <Calendar className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-slate-300">27/08/2026  12:24</span>
          </div>
        </div>

        {/* État marchandise */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-2">État à la livraison</div>
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
          <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-2">Observations (optionnel)</div>
          <textarea value={observation} onChange={e => setObservation(e.target.value)} disabled={signed} rows={2}
            placeholder="Ex: 2 colis avec emballage légèrement froissé..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500 resize-none disabled:opacity-50"
          />
        </div>

        {/* Zone signature */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">
              Signature du Réceptionnaire
            </div>
            {!signed && (
              <button onClick={clearSignature}
                className="flex items-center gap-1 text-[10px] text-slate-400 hover:text-slate-200 cursor-pointer">
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
          {!signed && <p className="text-[10px] text-slate-600 mt-1 text-center">← Faites signer le réceptionnaire ici</p>}
          {signed && <p className="text-[10px] text-emerald-400 mt-1 text-center flex items-center justify-center gap-1"><CheckCircle2 className="w-3 h-3" /> Signature enregistrée</p>}
        </div>

        {/* Valider */}
        {!signed ? (
          <button onClick={validateEPOD}
            className="w-full py-4 bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-black text-sm rounded-2xl shadow-lg shadow-emerald-500/20 hover:opacity-90 transition-opacity cursor-pointer active:scale-95 flex items-center justify-center gap-2">
            <Send className="w-5 h-5" /> Valider et transmettre l'e-POD
          </button>
        ) : (
          <div className="py-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl text-center">
            <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto mb-1" />
            <div className="text-sm font-black text-emerald-400">e-POD validé et transmis</div>
            <div className="text-[10px] text-slate-400 mt-0.5 font-mono">Réf: ePOD-MIS-2026-01847-{new Date().toISOString().slice(0, 10)}</div>
          </div>
        )}
      </div>
    </div>
  );
}
