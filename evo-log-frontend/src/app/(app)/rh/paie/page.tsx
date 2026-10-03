'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Calculator, User, AlertTriangle, CheckCircle2, Download
} from 'lucide-react';
import { toast } from 'sonner';
import { rhAPI } from '@/lib/api-client';
import { exportToCSV } from '@/lib/export';

interface Employe {
  id: number;
  full_name: string;
  matricule: string | null;
  poste: string | null;
  salaire_base: number | null;
}

// Fiche telle que la renvoie GET/POST /api/v1/rh/paie/bulletin (_bulletin_dict).
interface Bulletin {
  id: number;
  reference: string;
  employe_id: number;
  periode: string | null;
  salaire_base: number;
  heures_supplementaires: number;
  indemnite_heures_sup: number;
  primes: number;
  salaire_brut: number;
  cotisations_cnps: number;
  retenues_fiscales: number;
  autres_deductions: number;
  total_deductions: number;
  taux_cnps: number | null;
  net_a_payer: number;
  statut: string;
  date_paiement: string | null;
  devise: string | null;
}

// Statuts reellement admises par le backend (STATUTS_PAIE, en minuscules).
const STATUTS_PAIE = ['en_attente', 'paye', 'annule'];

function fmt(n: number | null | undefined): string {
  return n == null ? '' : Math.round(n).toLocaleString();
}

export default function RHPaiePage() {
  const [employes, setEmployes] = useState<Employe[]>([]);
  const [bulletins, setBulletins] = useState<Bulletin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Saisie de la fiche  le calcul CNPS/IRGM reste cote serveur (PaieService,
  // source unique des baremes Cameroun/CEMAC) : cet ecran ne re-invente aucun taux.
  const [employeId, setEmployeId] = useState('');
  const [mois, setMois] = useState(new Date().getMonth() + 1);
  const [annee, setAnnee] = useState(new Date().getFullYear());
  const [salaireBase, setSalaireBase] = useState(0);
  const [heuresSup, setHeuresSup] = useState(0);
  const [montantPrimes, setMontantPrimes] = useState(0);
  const [typePrime, setTypePrime] = useState('transport');
  const [montantDeductions, setMontantDeductions] = useState(0);
  const [saving, setSaving] = useState(false);
  const [dernierBulletin, setDernierBulletin] = useState<Bulletin | null>(null);

  const charger = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [empRes, paieRes] = await Promise.all([
        rhAPI.getEmployes(),
        rhAPI.getPaie(),
      ]);
      setEmployes(Array.isArray(empRes.data?.items) ? empRes.data.items : []);
      setBulletins(Array.isArray(paieRes.data) ? paieRes.data : []);
    } catch {
      setError(
        'Données de paie indisponibles : le serveur n\'a pas répondu. ' +
        'Aucun montant n\'est affiché sans avoir été récupéré de la base.'
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  const nomEmploye = useMemo(() => {
    const map = new Map<number, string>();
    employes.forEach(e => map.set(e.id, e.full_name));
    return (id: number) => map.get(id) || `Employé #${id}`;
  }, [employes]);

  async function enregistrerFiche() {
    if (!employeId) { toast.error('Sélectionnez un collaborateur enregistré.'); return; }
    if (salaireBase <= 0) { toast.error('Le salaire de base doit être positif.'); return; }
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {
        employe_id: Number(employeId),
        mois,
        annee,
        salaire_base: salaireBase,
        heures_supplementaires: heuresSup,
        primes: montantPrimes > 0 ? [{ type: typePrime, montant: montantPrimes }] : [],
        deductions: montantDeductions > 0 ? [{ type: 'autre', montant: montantDeductions }] : [],
        statut: 'en_attente',
      };
      const res = await rhAPI.createFichePaie(payload);
      setDernierBulletin(res.data as Bulletin);
      toast.success(res.data?.message || `Fiche ${mois.toString().padStart(2, '0')}/${annee} enregistrée.`);
      await charger();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Enregistrement impossible.');
    } finally {
      setSaving(false);
    }
  }

  function exporterCSV() {
    if (bulletins.length === 0) { toast.info('Aucune fiche enregistrée à exporter.'); return; }
    exportToCSV(
      bulletins.map(b => ({
        reference: b.reference,
        employe: nomEmploye(b.employe_id),
        periode: b.periode ?? '',
        salaire_brut: b.salaire_brut,
        cotisations_cnps: b.cotisations_cnps,
        retenues_fiscales: b.retenues_fiscales,
        net_a_payer: b.net_a_payer,
        statut: b.statut,
      })),
      'fiches_paie_enregistrees'
    );
  }

  const b = dernierBulletin;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-white flex items-center gap-2">
          <Calculator className="w-6 h-6 text-amber-400" /> Paie Cameroun  Fiches enregistrées
        </h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Le calcul CNPS / IRGM est effectué côté serveur (PaieService, barèmes Cameroun/CEMAC) :
          cette page n&apos;applique aucun taux inventé localement.
        </p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 flex items-start gap-3">
          <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
          <div className="flex-1">
            <div className="text-xs font-bold text-red-300">Données indisponibles</div>
            <div className="text-[11px] text-slate-400 mt-0.5">{error}</div>
          </div>
          <button onClick={charger} className="px-3 py-1.5 bg-red-500/20 border border-red-500/40 text-red-300 text-[11px] font-bold rounded-lg">
            Réessayer
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Saisie fiche */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl space-y-5">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <User className="w-4 h-4 text-blue-400" /> Enregistrer une fiche de paie
          </h2>

          <div>
            <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Collaborateur (annuaire réel)</label>
            <select
              value={employeId}
              onChange={e => {
                const emp = employes.find(e2 => String(e2.id) === e.target.value);
                setEmployeId(e.target.value);
                if (emp && emp.salaire_base != null) setSalaireBase(emp.salaire_base);
              }}
              className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500"
            >
              <option value="">
                {employes.length === 0 ? ' Aucun collaborateur enregistré ' : ' Sélectionner '}
              </option>
              {employes.map(emp => (
                <option key={emp.id} value={emp.id}>
                  {emp.full_name}{emp.poste ? `  ${emp.poste}` : ''}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Période  mois</label>
              <input type="number" value={mois} onChange={e => setMois(+e.target.value)} min={1} max={12}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-mono" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Année</label>
              <input type="number" value={annee} onChange={e => setAnnee(+e.target.value)} min={2000} max={2100}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-mono" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Salaire de base (XAF)</label>
              <input type="number" value={salaireBase} onChange={e => setSalaireBase(+e.target.value)}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-mono" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Heures supp. (h)</label>
              <input type="number" value={heuresSup} onChange={e => setHeuresSup(+e.target.value)} min={0}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-mono" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Prime (XAF)</label>
              <input type="number" value={montantPrimes} onChange={e => setMontantPrimes(+e.target.value)} min={0}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-mono" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Type de prime</label>
              <select value={typePrime} onChange={e => setTypePrime(e.target.value)}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500">
                <option value="anciennete">Ancienneté</option>
                <option value="performance">Performance</option>
                <option value="responsabilite">Responsabilité</option>
                <option value="logement">Logement</option>
                <option value="transport">Transport</option>
                <option value="autre">Autre</option>
              </select>
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Autres retenues (XAF)</label>
              <input type="number" value={montantDeductions} onChange={e => setMontantDeductions(+e.target.value)} min={0}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-mono" />
            </div>
          </div>

          <button
            onClick={enregistrerFiche}
            disabled={saving}
            className="w-full py-3 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-sm rounded-xl flex items-center justify-center gap-2 shadow-lg disabled:opacity-60"
          >
            <Calculator className="w-4 h-4" /> {saving ? 'Calcul serveur en cours…' : 'Calculer & Enregistrer (serveur)'}
          </button>

          {/* Bulletin retourne par le serveur  valeurs reellement frappees */}
          {b && (
            <div className="bg-slate-950 border border-emerald-500/30 rounded-2xl p-4 space-y-1.5">
              <div className="text-xs font-bold text-emerald-300 flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-4 h-4" /> Bulletin {b.reference}  calculé par le serveur
              </div>
              {[
                { label: 'Salaire de base', v: b.salaire_base },
                { label: 'Indemnité heures sup.', v: b.indemnite_heures_sup },
                { label: 'Primes', v: b.primes },
                { label: 'SALAIRE BRUT', v: b.salaire_brut, bold: true },
                { label: 'Cotisations CNPS (calcul serveur)', v: -b.cotisations_cnps },
                { label: 'Retenues fiscales IRGM (calcul serveur)', v: -b.retenues_fiscales },
                { label: 'Autres déductions', v: -b.autres_deductions },
                { label: 'NET À PAYER', v: b.net_a_payer, bold: true },
              ].map((l, i) => (
                <div key={i} className={`flex justify-between text-xs ${l.bold ? 'border-t border-slate-800 pt-1.5 font-black' : ''}`}>
                  <span className="text-slate-400">{l.label}</span>
                  <span className={`font-mono ${l.bold ? 'text-emerald-400' : l.v < 0 ? 'text-red-400' : 'text-slate-200'}`}>
                    {fmt(l.v)} XAF
                  </span>
                </div>
              ))}
              {b.taux_cnps != null && (
                <div className="text-[10px] text-slate-500 pt-1">
                  Taux CNPS effectivement appliqué : {(b.taux_cnps * 100).toFixed(2)} % du brut  retrouvé à partir des retenues réelles.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Fiches enregistrees */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200">Fiches de paie enregistrées ({bulletins.length})</h2>
            <button onClick={exporterCSV} className="px-3 py-1.5 bg-slate-800 border border-slate-700 text-slate-300 text-[11px] font-bold rounded-lg flex items-center gap-1.5 hover:bg-slate-700">
              <Download className="w-3.5 h-3.5" /> Export CSV
            </button>
          </div>

          {loading ? (
            <div className="text-center text-slate-500 text-xs py-8">Chargement des fiches…</div>
          ) : bulletins.length === 0 ? (
            <div className="text-center text-slate-500 text-xs py-8 border border-dashed border-slate-800 rounded-2xl">
              Aucune fiche de paie enregistrée. Les montants n&apos;apparaissent qu&apos;après enregistrement réel en base.
            </div>
          ) : (
            <div className="overflow-x-auto max-h-[560px]">
              <table className="w-full text-xs">
                <thead className="sticky top-0 bg-slate-950">
                  <tr className="border-b border-slate-800 text-left text-slate-400 uppercase">
                    <th className="px-3 py-2.5">Réf.</th>
                    <th className="px-3 py-2.5">Collaborateur</th>
                    <th className="px-3 py-2.5">Période</th>
                    <th className="px-3 py-2.5 text-right">Brut</th>
                    <th className="px-3 py-2.5 text-right">CNPS</th>
                    <th className="px-3 py-2.5 text-right">IRGM</th>
                    <th className="px-3 py-2.5 text-right">Net</th>
                    <th className="px-3 py-2.5 text-center">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {bulletins.map(f => (
                    <tr key={f.id} className="hover:bg-slate-800/30">
                      <td className="px-3 py-2.5 font-mono text-amber-300">{f.reference}</td>
                      <td className="px-3 py-2.5 text-slate-200 font-bold">{nomEmploye(f.employe_id)}</td>
                      <td className="px-3 py-2.5 font-mono text-slate-400">{f.periode ?? ''}</td>
                      <td className="px-3 py-2.5 text-right font-mono text-slate-300">{fmt(f.salaire_brut)}</td>
                      <td className="px-3 py-2.5 text-right font-mono text-pink-400">{fmt(f.cotisations_cnps)}</td>
                      <td className="px-3 py-2.5 text-right font-mono text-amber-400">{fmt(f.retenues_fiscales)}</td>
                      <td className="px-3 py-2.5 text-right font-mono font-black text-emerald-400">{fmt(f.net_a_payer)}</td>
                      <td className="px-3 py-2.5 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${f.statut === 'paye' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : f.statut === 'annule' ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                              : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          }`}>{f.statut}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="text-[10px] text-slate-500">
            Statuts gérés par le serveur : {STATUTS_PAIE.join(' · ')}.
          </p>
        </div>
      </div>
    </div>
  );
}
