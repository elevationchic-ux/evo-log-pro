'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { transportAPI } from '@/lib/api-client';
import {
  FileCheck, ArrowLeft, Send, DollarSign, CheckCircle2, Loader2, Eraser
} from 'lucide-react';
import { toast } from 'sonner';
import Link from 'next/link';
import { useSettings } from '@/components/layout/SettingsProvider';

interface MissionLite {
  id: number;
  reference: string;
  statut: string | null;
  origine: string | null;
  destination: string | null;
  montant_fret: number | null;
}

interface FactureAuto {
  id: number;
  numero_facture: string;
  montant_ht: number;
  montant_tva: number;
  montant_ttc: number;
  devise: string;
  statut: string;
}

const fmtXaf = (n: number | null | undefined, lang: string) =>
  n == null ? '' : new Intl.NumberFormat(lang === 'en' ? 'en-US' : 'fr-FR').format(n);

export default function EPodCapturePage() {
  const { language } = useSettings();
  const lang = language || 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [missions, setMissions] = useState<MissionLite[]>([]);
  const [loadingMissions, setLoadingMissions] = useState(true);
  const [missionId, setMissionId] = useState('');
  const [destinataire, setDestinataire] = useState('');
  const [clientNom, setClientNom] = useState('');
  const [montantFret, setMontantFret] = useState('');
  const [note, setNote] = useState('');
  const [invoiceResult, setInvoiceResult] = useState<FactureAuto | null>(null);
  const [facturationNote, setFacturationNote] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Véritable pad de signature : les tracés sont capturés puis envoyés en base64
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const drawing = useRef(false);
  const [hasSignature, setHasSignature] = useState(false);

  useEffect(() => {
    setLoadingMissions(true);
    transportAPI
      .getMissions({ limit: 200 })
      .then(res => {
        const rows = Array.isArray(res.data) ? res.data : res.data?.items || [];
        setMissions(
          rows.map((m: any) => ({
            id: m.id,
            reference: m.reference || `MISSION-${m.id}`,
            statut: m.statut || null,
            origine: m.origine || m.point_depart || null,
            destination: m.destination || m.point_arrivee || null,
            montant_fret: m.montant_fret ?? m.cout_reel ?? null,
          }))
        );
      })
      .catch(() => {
        setMissions([]);
        toast.error(t('Erreur réseau  chargement des missions impossible', 'Network error  could not load missions'));
      })
      .finally(() => setLoadingMissions(false));
  }, [lang]);

  const handleMissionChange = (id: string) => {
    setMissionId(id);
    const m = missions.find(x => String(x.id) === id);
    // Pré-remplit uniquement à partir des données réelles de la mission
    if (m && m.montant_fret != null && !montantFret) {
      setMontantFret(String(m.montant_fret));
    }
  };

  // Signature canvas plumbing
  const getCtx = () => canvasRef.current?.getContext('2d') || null;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#22d3ee';
  }, []);

  const pos = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    return {
      x: (e.clientX - rect.left) * (canvas.width / rect.width),
      y: (e.clientY - rect.top) * (canvas.height / rect.height),
    };
  };

  const startDraw = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const ctx = getCtx();
    if (!ctx) return;
    drawing.current = true;
    canvasRef.current?.setPointerCapture(e.pointerId);
    const { x, y } = pos(e);
    ctx.beginPath();
    ctx.moveTo(x, y);
  };

  const draw = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!drawing.current) return;
    const ctx = getCtx();
    if (!ctx) return;
    const { x, y } = pos(e);
    ctx.lineTo(x, y);
    ctx.stroke();
    setHasSignature(true);
  };

  const endDraw = () => { drawing.current = false; };

  const clearSignature = () => {
    const canvas = canvasRef.current;
    const ctx = getCtx();
    if (canvas && ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
    setHasSignature(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!missionId) {
      toast.error(t('Sélectionnez une mission réelle à livrer.', 'Select an actual mission to deliver.'));
      return;
    }
    if (!hasSignature && !destinataire.trim()) {
      toast.error(t(
        'Preuve de livraison incomplète : signez ou indiquez le nom du réceptionnaire.',
        'Incomplete proof of delivery: sign or provide the recipient name.'
      ));
      return;
    }
    setLoading(true);
    setInvoiceResult(null);
    setFacturationNote(null);
    try {
      const signatureData = hasSignature ? canvasRef.current!.toDataURL('image/png') : undefined;
      const res = await transportAPI.livrerMission(Number(missionId), {
        signature: signatureData,
        nom_receptionnaire: destinataire.trim() || undefined,
        note: note.trim() || undefined,
        montant_fret_xaf: montantFret ? parseFloat(montantFret) : undefined,
        client_nom: clientNom.trim() || undefined,
      });
      const data = res.data || {};
      if (data.facture_auto) {
        setInvoiceResult(data.facture_auto);
        toast.success(t(
          `e-POD validé  facture ${data.facture_auto.numero_facture} générée automatiquement.`,
          `e-POD confirmed  invoice ${data.facture_auto.numero_facture} auto-generated.`
        ));
      } else {
        setFacturationNote(data.facturation_note || null);
        toast.success(t('e-POD validé  mission clôturée.', 'e-POD confirmed  mission closed.'));
      }
      // Réinitialise la preuve après envoi (la mission est désormais terminée en base)
      clearSignature();
      setDestinataire('');
      setNote('');
      setMissionId('');
      transportAPI.getMissions({ limit: 200 }).then(r => {
        const rows = Array.isArray(r.data) ? r.data : r.data?.items || [];
        setMissions(rows.map((m: any) => ({
          id: m.id,
          reference: m.reference || `MISSION-${m.id}`,
          statut: m.statut || null,
          origine: m.origine || m.point_depart || null,
          destination: m.destination || m.point_arrivee || null,
          montant_fret: m.montant_fret ?? m.cout_reel ?? null,
        })));
      }).catch(() => { });
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : t('Erreur réseau  validation impossible', 'Network error  could not validate'));
    } finally {
      setLoading(false);
    }
  };

  const inputCls = "w-full bg-background border border-border rounded-2xl p-4 text-sm text-foreground focus:ring-2 focus:ring-cyan-500";
  const labelCls = "block text-xs font-bold text-muted-foreground uppercase mb-2";

  return (
    <div className="max-w-2xl mx-auto py-8 px-4 text-foreground animate-in fade-in duration-500">
      <Link href="/tracking" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6">
        <ArrowLeft className="w-4 h-4" /> {t('Retour au tracking', 'Back to tracking')}
      </Link>

      <div className="bg-card border border-border rounded-3xl p-5 sm:p-8 shadow-2xl">
        <div className="flex items-center gap-3 pb-6 border-b border-border mb-6">
          <div className="w-12 h-12 bg-cyan-500/10 text-cyan-400 rounded-2xl flex items-center justify-center border border-cyan-500/20 shrink-0">
            <FileCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-foreground">
              {t('Numérisation e-POD & Facturation Auto', 'e-POD Digitization & Auto-Invoicing')}
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground">
              {t('Signature réceptionnaire capturée en base & facture émise automatiquement par K-Finance.', 'Recipient signature persisted and invoice automatically issued by K-Finance.')}
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className={labelCls}>{t('Mission à livrer *', 'Mission to deliver *')}</label>
            {loadingMissions ? (
              <div className="flex items-center gap-2 text-xs text-muted-foreground p-4 border border-border rounded-2xl">
                <Loader2 className="w-4 h-4 animate-spin text-cyan-400" /> {t('Chargement des missions...', 'Loading missions...')}
              </div>
            ) : missions.length === 0 ? (
              <div className="p-4 border border-border rounded-2xl bg-background text-xs text-muted-foreground">
                {t('Aucune mission enregistrée  créez d\u2019abord une mission dans Transport.', 'No mission on record  first create a mission in Transport.')}{' '}
                <Link href="/transport/missions" className="text-cyan-400 hover:underline font-bold">{t('Aller aux missions', 'Go to missions')}</Link>
              </div>
            ) : (
              <select value={missionId} onChange={e => handleMissionChange(e.target.value)} className={`${inputCls} font-mono font-bold`}>
                <option value="">{t(' Sélectionner une mission ', ' Select a mission ')}</option>
                {missions.map(m => (
                  <option key={m.id} value={m.id}>
                    {m.reference}  {[m.origine, m.destination].filter(Boolean).join(' → ') || t('trajet non renseigné', 'route not set')} {m.statut ? ` [${m.statut}]` : ''}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className={labelCls}>{t('Client facturé', 'Billed client')}</label>
              <input
                type="text"
                value={clientNom}
                onChange={(e) => setClientNom(e.target.value)}
                placeholder={t('Nom du client (facultatif si rattaché)', 'Client name (optional if linked)')}
                className={inputCls}
              />
            </div>
            <div>
              <label className={labelCls}>{t('Montant Fret HT (FCFA)', 'Freight Amount excl. tax (FCFA)')}</label>
              <input
                type="number"
                min="0"
                value={montantFret}
                onChange={(e) => setMontantFret(e.target.value)}
                placeholder="0"
                className={`${inputCls} font-bold`}
              />
            </div>
          </div>

          <div>
            <label className={labelCls}>{t('Nom du Réceptionnaire / Destinataire', 'Recipient Name')}</label>
            <input
              type="text"
              value={destinataire}
              onChange={(e) => setDestinataire(e.target.value)}
              className={inputCls}
            />
          </div>

          <div>
            <label className={labelCls}>{t('Note de livraison', 'Delivery note')}</label>
            <textarea
              rows={2}
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder={t('Réserves éventuelles, état des colis...', 'Any remarks, package condition...')}
              className={`${inputCls} resize-none`}
            />
          </div>

          {/* Pad de signature réel (pointer events → PNG base64 envoyé au backend) */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className={`${labelCls} mb-0`}>{t('Signature Électronique du Destinataire', 'Recipient Electronic Signature')}</label>
              <button
                type="button"
                onClick={clearSignature}
                className="flex items-center gap-1 text-[11px] text-muted-foreground hover:text-cyan-400 transition-colors"
              >
                <Eraser size={12} /> {t('Effacer', 'Clear')}
              </button>
            </div>
            <div className="relative border border-dashed border-cyan-500/40 rounded-2xl bg-cyan-500/5 overflow-hidden">
              <canvas
                ref={canvasRef}
                width={640}
                height={180}
                onPointerDown={startDraw}
                onPointerMove={draw}
                onPointerUp={endDraw}
                onPointerLeave={endDraw}
                className="w-full h-40 sm:h-[180px] touch-none cursor-crosshair"
              />
              {!hasSignature && (
                <p className="absolute inset-0 flex items-center justify-center text-xs text-cyan-400/60 font-mono pointer-events-none">
                  {t('Signez ici avec le doigt ou le stylet', 'Sign here with finger or stylus')}
                </p>
              )}
            </div>
            <p className="text-[10px] text-muted-foreground mt-1">
              {t('La signature est capturée, transmise et archivée sur la mission.', 'The signature is captured, transmitted and archived onto the mission.')}
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || !missionId}
            className="w-full py-4 rounded-2xl bg-cyan-600 hover:bg-cyan-700 disabled:opacity-50 text-white font-bold transition-all shadow-lg shadow-cyan-600/20 flex items-center justify-center gap-2 mt-4"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            {t('Valider e-POD & Générer Facture K-Finance', 'Confirm e-POD & Generate K-Finance Invoice')}
          </button>
        </form>

        {/* Alerte Facture Générée (données réelles renvoyées par le backend) */}
        {invoiceResult && (
          <div className="mt-6 p-5 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 space-y-2 animate-in slide-in-from-bottom duration-300">
            <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
              <CheckCircle2 size={18} />
              {t('Facture émise automatiquement dans K-Finance', 'Invoice automatically issued in K-Finance')}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-foreground font-mono mt-2">
              <div>{t('Facture N°', 'Invoice No')}: <span className="font-bold text-emerald-400">{invoiceResult.numero_facture}</span></div>
              <div>{t('Montant HT', 'Amount excl. tax')}: {fmtXaf(invoiceResult.montant_ht, lang)} {invoiceResult.devise}</div>
              <div>{t('TVA', 'VAT')}: {fmtXaf(invoiceResult.montant_tva, lang)} {invoiceResult.devise}</div>
              <div>{t('Montant TTC', 'Total incl. tax')}: <span className="font-bold text-emerald-400">{fmtXaf(invoiceResult.montant_ttc, lang)} {invoiceResult.devise}</span></div>
            </div>
            <div className="pt-2">
              <Link href="/finance/invoicing" className="text-xs text-emerald-400 hover:underline flex items-center gap-1">
                <DollarSign size={12} /> {t('Voir dans K-Finance →', 'View in K-Finance →')}
              </Link>
            </div>
          </div>
        )}

        {facturationNote && !invoiceResult && (
          <div className="mt-6 p-4 rounded-2xl border border-amber-500/30 bg-amber-500/10 text-xs text-amber-300">
            {facturationNote}
          </div>
        )}
      </div>
    </div>
  );
}
