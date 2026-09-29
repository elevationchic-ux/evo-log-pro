'use client';

// Console Super-Admin CADC  File d'arbitrage des demandes d'accréditation.
//
// Boucle Phase 3 : un admin entreprise (niveau 1) demande l'ouverture d'un
// module verrouillé (POST /company-admin/modules/demandes -> Accreditation
// statut "demande"). Cette file est la SEULE interface où le CADC traite ces
// demandes :
//   - APPROUVER  : conversion EN PLACE de la demande en accréditation active
//     datée (pas de doublon) ; le module bascule en « accrédité » chez
//     l'entreprise et le demandeur porte désormais le droit granulaire ;
//   - REFUSER    : statut « refuse » (trace conservee), le module redevient
//     « verrouille » et l'entreprise peut redemander plus tard.
//
// Garde : toute la sous-arborescence /admin/super-admin est verrouillee par
// layout.tsx (require_superadmin) ; le backend rejette independamment (403).

import React, { useState, useEffect, useCallback } from 'react';
import { Inbox, RefreshCw, CheckCircle2, XCircle, X, CalendarClock, Building2, ShieldQuestion } from 'lucide-react';
import { toast } from 'sonner';
import { saasConsoleAPI } from '@/lib/api-client';

interface Demande {
  id: number; company_id: number; company_nom?: string | null;
  user_id: number; code: string; libelle?: string | null; module?: string | null;
  motif?: string | null; created_at?: string | null;
}

const toISO = (d: Date) => d.toISOString().slice(0, 10);
const fmtDate = (s?: string | null) => (s ? new Date(s).toLocaleDateString('fr-FR') : '');

export default function CadcDemandesAccreditationPage() {
  const [rows, setRows] = useState<Demande[]>([]);
  const [loading, setLoading] = useState(true);

  const [approving, setApproving] = useState<Demande | null>(null);
  const [rejecting, setRejecting] = useState<Demande | null>(null);
  const [saving, setSaving] = useState(false);
  const [dateDebut, setDateDebut] = useState('');
  const [dateFin, setDateFin] = useState('');
  const [motif, setMotif] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await saasConsoleAPI.listPendingAccreditationRequests();
      setRows(Array.isArray(res.data) ? res.data : []);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Chargement de la file impossible');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const openApprove = (d: Demande) => {
    setDateDebut(toISO(new Date()));
    setDateFin('');
    setMotif('');
    setApproving(d);
  };
  const openReject = (d: Demande) => {
    setMotif('');
    setRejecting(d);
  };
  const closeModal = () => { setApproving(null); setRejecting(null); };

  const confirmApprove = async () => {
    if (!approving) return;
    if (dateFin && dateFin < dateDebut) { toast.error('La date de fin précède la date de début'); return; }
    setSaving(true);
    try {
      await saasConsoleAPI.approveAccreditationRequest(approving.id, {
        date_debut: dateDebut || undefined,
        date_fin: dateFin || undefined,
        motif: motif || undefined,
      });
      toast.success(`Module « ${approving.module} » accrédité`);
      closeModal();
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Approbation impossible');
    } finally { setSaving(false); }
  };

  const confirmReject = async () => {
    if (!rejecting) return;
    setSaving(true);
    try {
      await saasConsoleAPI.rejectAccreditationRequest(rejecting.id, { motif: motif || undefined });
      toast.success('Demande refusée');
      closeModal();
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Refus impossible');
    } finally { setSaving(false); }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">Console Super-Admin CADC</span>
          <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">T-Code : KCADC_REQ</span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
              <Inbox className="w-8 h-8 text-amber-400" /> Demandes d&apos;accréditation
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              File d&apos;arbitrage des modules demandés par les administrateurs d&apos;entreprise.
              {rows.length > 0 && <span className="ml-1 font-bold text-amber-300">{rows.length} en attente.</span>}
            </p>
          </div>
          <button onClick={load} className="p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-slate-300">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-amber-400' : ''}`} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-12 text-center text-sm text-slate-500 font-sans">Chargement de la file…</div>
      ) : rows.length === 0 ? (
        <div className="bg-slate-900/60 border border-dashed border-slate-800 rounded-3xl p-12 text-center">
          <ShieldQuestion className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <p className="text-sm text-slate-500 font-sans">Aucune demande en attente d&apos;arbitrage.</p>
        </div>
      ) : (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider bg-slate-950">
                  <th className="py-3.5 px-4">Entreprise</th>
                  <th className="py-3.5 px-4">Module demandé</th>
                  <th className="py-3.5 px-4">Motif</th>
                  <th className="py-3.5 px-4">Reçue le</th>
                  <th className="py-3.5 px-4 text-right">Arbitrage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {rows.map(d => (
                  <tr key={d.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-sans">
                      <span className="inline-flex items-center gap-1.5 text-slate-200">
                        <Building2 className="w-3.5 h-3.5 text-slate-500" /> {d.company_nom || `#${d.company_id}`}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-amber-300 font-mono text-[11px]">{d.module}</span>
                      <p className="text-[10px] text-slate-500 font-sans mt-0.5">{d.libelle}</p>
                    </td>
                    <td className="py-3.5 px-4 font-sans text-slate-400 max-w-[240px] truncate" title={d.motif || ''}>{d.motif || ''}</td>
                    <td className="py-3.5 px-4 text-[11px] text-slate-400">{fmtDate(d.created_at)}</td>
                    <td className="py-3.5 px-4">
                      <div className="flex justify-end gap-2">
                        <button onClick={() => openApprove(d)} className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[11px] flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Approuver
                        </button>
                        <button onClick={() => openReject(d)} className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-red-500/20 border border-slate-700 hover:border-red-500/40 text-red-300 font-bold text-[11px] flex items-center gap-1">
                          <XCircle className="w-3.5 h-3.5" /> Refuser
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {(approving || rejecting) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm" onClick={closeModal} />
          <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl">
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <h2 className="text-lg font-black text-slate-100">
                {approving ? 'Approuver la demande' : 'Refuser la demande'}
              </h2>
              <button onClick={closeModal} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6 space-y-4">
              <p className="text-xs text-slate-400">
                {approving ? (
                  <>Le module <span className="font-bold text-amber-300">{approving.module}</span> de{' '}
                    <span className="font-semibold text-slate-200">{approving.company_nom || `l'entreprise #${approving.company_id}`}</span>
                    {' '}sera converti en accréditation active datée (aucun doublon).</>
                ) : (
                  <>La demande de <span className="font-bold text-red-300">{rejecting?.module}</span> sera marquée refusée.
                    {' '}L&apos;entreprise retrouvera le module verrouillé et pourra redemander plus tard.</>
                )}
              </p>

              {approving && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1 flex items-center gap-1"><CalendarClock className="w-3.5 h-3.5" /> Début</label>
                    <input type="date" value={dateDebut} onChange={e => setDateDebut(e.target.value)} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1">Fin (délai)</label>
                    <input type="date" value={dateFin} onChange={e => setDateFin(e.target.value)} className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100" />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Motif {rejecting ? '' : '(facultatif)'}</label>
                <textarea rows={3} value={motif} onChange={e => setMotif(e.target.value)}
                  placeholder={rejecting ? 'Ex : hors forfait du plan, à revoir au prochain renouvellement' : 'Ex : accord pour la campagne portuaire'}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100 resize-none" />
              </div>
            </div>
            <div className="px-6 py-4 border-t border-slate-800 flex justify-end gap-3">
              <button onClick={closeModal} className="px-4 py-2 text-sm rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700">Annuler</button>
              {approving ? (
                <button onClick={confirmApprove} disabled={saving} className="px-4 py-2 text-sm rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold disabled:opacity-50 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" /> {saving ? 'Traitement...' : 'Approuver'}
                </button>
              ) : (
                <button onClick={confirmReject} disabled={saving} className="px-4 py-2 text-sm rounded-lg bg-red-600 hover:bg-red-500 text-white font-bold disabled:opacity-50 flex items-center gap-2">
                  <XCircle className="w-4 h-4" /> {saving ? 'Traitement...' : 'Confirmer le refus'}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
