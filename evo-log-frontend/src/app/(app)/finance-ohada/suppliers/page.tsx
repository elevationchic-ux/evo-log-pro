'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Wallet, Search, Download, CheckCircle2,
  AlertTriangle, CreditCard, Building, RefreshCw,
  Calendar, X, Loader2
} from 'lucide-react';
import { toast } from 'sonner';

interface BalanceAgeeFournisseur {
  fournisseur_id: number;
  fournisseur_nom: string;
  categorie: string;
  total_du: number;
  non_echu: number;
  echu_1_30: number;
  echu_31_60: number;
  echu_plus_60: number;
  dpo_jours: number;
  mode_paiement: string;
  compte_401: string;
  prochaine_echeance: string | null;
}

interface DPOData {
  dpo_moyen: number;
  dpo_objectif: number;
  variation_vs_mois_precedent: number;
  total_factures_ouvertes: number;
  montant_a_payer_semaine: number;
  fournisseur_semaine: string;
}

interface PaymentModal {
  fournisseur: BalanceAgeeFournisseur | null;
  open: boolean;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

async function apiFetch<T>(path: string): Promise<T> {
  const token = getToken();
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

function AgingBar({ non_echu, d30, d60, d60p }: { non_echu: number; d30: number; d60: number; d60p: number }) {
  const total = non_echu + d30 + d60 + d60p || 1;
  return (
    <div className="flex h-2 rounded-full overflow-hidden w-28 bg-slate-800">
      {non_echu > 0 && <div className="bg-emerald-500" style={{ width: `${(non_echu / total) * 100}%` }} />}
      {d30 > 0 && <div className="bg-amber-500" style={{ width: `${(d30 / total) * 100}%` }} />}
      {d60 > 0 && <div className="bg-orange-500" style={{ width: `${(d60 / total) * 100}%` }} />}
      {d60p > 0 && <div className="bg-red-500" style={{ width: `${(d60p / total) * 100}%` }} />}
    </div>
  );
}

export default function FinanceOhadaSuppliers() {
  const [data, setData] = useState<BalanceAgeeFournisseur[]>([]);
  const [dpo, setDpo] = useState<DPOData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterEchu, setFilterEchu] = useState<'ALL' | 'ECHU' | 'NON_ECHU'>('ALL');
  const [payModal, setPayModal] = useState<PaymentModal>({ fournisseur: null, open: false });
  const [submitting, setSubmitting] = useState(false);

  const today = new Date().toISOString().split('T')[0];
  const currentPeriode = new Date().toISOString().slice(0, 7);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [balanceData, dpoData] = await Promise.all([
        apiFetch<BalanceAgeeFournisseur[]>(`/finance-avance/dettes/balance-agee?date_reference=${today}`),
        apiFetch<DPOData>(`/finance-avance/dettes/dpo?periode=${currentPeriode}`),
      ]);
      setData(balanceData);
      setDpo(dpoData);
    } catch {
      setError('Impossible de charger les données fournisseurs. Vérifiez la connexion API.');
      setData([]);
      setDpo(null);
    } finally {
      setLoading(false);
    }
  }, [today, currentPeriode]);

  useEffect(() => { loadData(); }, [loadData]);

  const filtered = data.filter(item => {
    const matchSearch = item.fournisseur_nom.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.compte_401.includes(searchQuery) ||
      item.categorie.toLowerCase().includes(searchQuery.toLowerCase());
    const isEchuItem = (item.echu_1_30 + item.echu_31_60 + item.echu_plus_60) > 0;
    const matchFilter =
      filterEchu === 'ALL' ||
      (filterEchu === 'ECHU' && isEchuItem) ||
      (filterEchu === 'NON_ECHU' && !isEchuItem);
    return matchSearch && matchFilter;
  });

  const totalDu = data.reduce((s, d) => s + d.total_du, 0);
  const totalEchu = data.reduce((s, d) => s + d.echu_1_30 + d.echu_31_60 + d.echu_plus_60, 0);
  const totalCritique = data.reduce((s, d) => s + d.echu_plus_60, 0);

  const confirmPaiement = async () => {
    if (!payModal.fournisseur) return;
    setSubmitting(true);
    try {
      const token = getToken();
      const res = await fetch(`${API_BASE}/finance-avance/dettes/regler`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          fournisseur_id: payModal.fournisseur.fournisseur_id,
          montant: payModal.fournisseur.total_du,
          mode_paiement: payModal.fournisseur.mode_paiement,
        }),
      });
      if (!res.ok) throw new Error();
      toast.success(`Ordre de paiement pour ${payModal.fournisseur.fournisseur_nom} initié`);
      setPayModal({ fournisseur: null, open: false });
      await loadData();
    } catch {
      toast.error("Erreur lors de l'initiation du paiement");
    } finally {
      setSubmitting(false);
    }
  };

  const exportCSV = () => {
    const headers = ['Fournisseur', 'Compte 401', 'Catégorie', 'Total Dû (XAF)', 'Non Échu', 'Échu 1-30j', 'Échu 31-60j', 'Échu +60j', 'DPO', 'Mode'];
    const rows = filtered.map(d => [
      d.fournisseur_nom, d.compte_401, d.categorie,
      d.total_du, d.non_echu, d.echu_1_30, d.echu_31_60, d.echu_plus_60,
      `${d.dpo_jours}j`, d.mode_paiement
    ]);
    const csv = [headers, ...rows].map(r => r.join(';')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `balance_agee_fournisseurs_${today}.csv`; a.click();
    URL.revokeObjectURL(url);
    toast.success('Balance âgée exportée (CSV)');
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-emerald-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Gestion des Dettes &amp; Décaissements
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KFIN_DET
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Wallet className="w-8 h-8 text-emerald-400" />
            Dettes Fournisseurs &amp; Balance Âgée
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Contrôle factures (401), DPO et ordonnancement décaissements  Réf. {today}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={loadData} disabled={loading} className="px-3 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs rounded-xl flex items-center gap-2 border border-slate-700 transition-all">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button onClick={exportCSV} disabled={filtered.length === 0} className="px-3 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs rounded-xl flex items-center gap-2 border border-slate-700 transition-all">
            <Download className="w-4 h-4 text-emerald-400" /> CSV
          </button>
          <button onClick={() => toast.info('Ordonnancement groupé  disponible après validation DFC')} className="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-emerald-500/25 transition-all">
            <CreditCard className="w-4 h-4" /> Ordonnancer Règlements
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <p className="text-xs text-red-300">{error}</p>
        </div>
      )}

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            label: 'Total Dettes (401)', value: loading ? null : `${totalDu.toLocaleString('fr-FR')} XAF`,
            sub: `${data.length} fournisseurs`, color: 'text-slate-100',
          },
          {
            label: 'DPO Moyen', value: loading ? null : `${dpo?.dpo_moyen?.toFixed(0) ?? ''} jours`,
            sub: dpo ? `${dpo.variation_vs_mois_precedent > 0 ? '+' : ''}${dpo.variation_vs_mois_precedent?.toFixed(1)}j vs N-1` : 'N/D',
            color: 'text-blue-400',
          },
          {
            label: 'Montant Échu Total', value: loading ? null : `${totalEchu.toLocaleString('fr-FR')} XAF`,
            sub: `Critique +60j : ${totalCritique.toLocaleString('fr-FR')}`, color: 'text-amber-400',
          },
          {
            label: 'À Payer Cette Semaine', value: loading ? null : `${(dpo?.montant_a_payer_semaine ?? 0).toLocaleString('fr-FR')} XAF`,
            sub: dpo?.fournisseur_semaine ?? '', color: 'text-emerald-400',
          },
        ].map((kpi, i) => (
          <div key={i} className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{kpi.label}</div>
            {loading ? (
              <div className="h-8 bg-slate-800 rounded animate-pulse" />
            ) : (
              <>
                <div className={`text-2xl font-black font-mono ${kpi.color}`}>{kpi.value}</div>
                <div className="text-[11px] text-slate-400 mt-2">{kpi.sub}</div>
              </>
            )}
          </div>
        ))}
      </div>

      {/* Légende */}
      <div className="flex flex-wrap items-center gap-4 bg-slate-900/60 border border-slate-800 rounded-2xl px-5 py-3 text-xs">
        <span className="font-bold text-slate-400 uppercase tracking-wider text-[10px]">Balance Âgée :</span>
        {[['bg-emerald-500', 'Non Échu'], ['bg-amber-500', 'Échu 1-30j'], ['bg-orange-500', 'Échu 31-60j'], ['bg-red-500', '+60j (Critique)']].map(([c, l]) => (
          <div key={l} className="flex items-center gap-2"><div className={`w-3 h-3 rounded-full ${c}`} /><span className="text-slate-400">{l}</span></div>
        ))}
      </div>

      {/* Filtres */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
            placeholder="Fournisseur, compte 401, catégorie..."
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-mono" />
        </div>
        <div className="flex items-center gap-2">
          {(['ALL', 'ECHU', 'NON_ECHU'] as const).map(f => (
            <button key={f} onClick={() => setFilterEchu(f)}
              className={`px-3 py-2 rounded-xl text-xs font-bold transition-all border ${filterEchu === f ? 'bg-emerald-600 text-white border-emerald-500' : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'}`}>
              {f === 'ALL' ? 'Tous' : f === 'ECHU' ? 'Échus' : 'Non Échus'}
            </button>
          ))}
          <span className="text-xs text-slate-500 font-mono ml-1">{filtered.length} résultat(s)</span>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Fournisseur</th>
                <th className="py-3.5 px-4">Cpte 401</th>
                <th className="py-3.5 px-4">Catégorie</th>
                <th className="py-3.5 px-4 text-right">Total Dû</th>
                <th className="py-3.5 px-4 text-right">Non Échu</th>
                <th className="py-3.5 px-4 text-right">1-30j</th>
                <th className="py-3.5 px-4 text-right">31-60j</th>
                <th className="py-3.5 px-4 text-right text-red-400">+60j</th>
                <th className="py-3.5 px-4 text-center">Âge</th>
                <th className="py-3.5 px-4 text-center">DPO</th>
                <th className="py-3.5 px-4">Mode</th>
                <th className="py-3.5 px-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <tr key={i}>{Array.from({ length: 12 }).map((_, j) => (
                    <td key={j} className="py-4 px-4"><div className="h-3 bg-slate-800 rounded animate-pulse" /></td>
                  ))}</tr>
                ))
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={12} className="py-16 text-center">
                    <div className="flex flex-col items-center gap-3 text-slate-500">
                      <Building className="w-10 h-10 opacity-40" />
                      <p className="font-sans">{error ? 'Erreur de chargement' : 'Aucun fournisseur trouvé'}</p>
                      <button onClick={loadData} className="text-emerald-400 hover:underline text-xs">Réessayer</button>
                    </div>
                  </td>
                </tr>
              ) : (
                filtered.map(item => {
                  const isCritique = item.echu_plus_60 > 0;
                  return (
                    <tr key={item.fournisseur_id} className={`hover:bg-slate-800/40 transition-colors ${isCritique ? 'border-l-2 border-l-red-500' : ''}`}>
                      <td className="py-3.5 px-4 font-sans font-bold text-slate-100">
                        <div className="flex items-center gap-2">
                          {isCritique && <AlertTriangle className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />}
                          {item.fournisseur_nom}
                        </div>
                        {item.prochaine_echeance && (
                          <div className="text-[10px] text-slate-500 font-normal mt-0.5 flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(item.prochaine_echeance).toLocaleDateString('fr-FR')}
                          </div>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-amber-400 font-bold">{item.compte_401}</td>
                      <td className="py-3.5 px-4 text-slate-400">{item.categorie}</td>
                      <td className="py-3.5 px-4 text-right font-bold text-slate-100">{item.total_du.toLocaleString('fr-FR')}</td>
                      <td className="py-3.5 px-4 text-right text-emerald-400">{item.non_echu > 0 ? item.non_echu.toLocaleString('fr-FR') : ''}</td>
                      <td className="py-3.5 px-4 text-right text-amber-400">{item.echu_1_30 > 0 ? item.echu_1_30.toLocaleString('fr-FR') : ''}</td>
                      <td className="py-3.5 px-4 text-right text-orange-400">{item.echu_31_60 > 0 ? item.echu_31_60.toLocaleString('fr-FR') : ''}</td>
                      <td className="py-3.5 px-4 text-right font-bold text-red-400">{item.echu_plus_60 > 0 ? item.echu_plus_60.toLocaleString('fr-FR') : ''}</td>
                      <td className="py-3.5 px-4 text-center">
                        <AgingBar non_echu={item.non_echu} d30={item.echu_1_30} d60={item.echu_31_60} d60p={item.echu_plus_60} />
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className={`font-bold ${item.dpo_jours > 45 ? 'text-red-400' : item.dpo_jours > 30 ? 'text-amber-400' : 'text-blue-400'}`}>
                          {item.dpo_jours}j
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 text-[11px]">{item.mode_paiement}</td>
                      <td className="py-3.5 px-4 text-center">
                        <button onClick={() => setPayModal({ fournisseur: item, open: true })}
                          className="px-2.5 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 font-bold text-[10px] rounded-lg border border-emerald-500/30 transition-all">
                          Régler
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
            {!loading && filtered.length > 0 && (
              <tfoot className="bg-slate-950 border-t-2 border-slate-700">
                <tr className="text-slate-300 font-bold font-mono">
                  <td colSpan={3} className="py-3 px-4 text-slate-400 font-sans uppercase text-[10px] tracking-wider">TOTAUX GÉNÉRAUX</td>
                  <td className="py-3 px-4 text-right text-slate-100">{totalDu.toLocaleString('fr-FR')}</td>
                  <td className="py-3 px-4 text-right text-emerald-400">{data.reduce((s, d) => s + d.non_echu, 0).toLocaleString('fr-FR')}</td>
                  <td className="py-3 px-4 text-right text-amber-400">{data.reduce((s, d) => s + d.echu_1_30, 0).toLocaleString('fr-FR')}</td>
                  <td className="py-3 px-4 text-right text-orange-400">{data.reduce((s, d) => s + d.echu_31_60, 0).toLocaleString('fr-FR')}</td>
                  <td className="py-3 px-4 text-right text-red-400">{totalCritique.toLocaleString('fr-FR')}</td>
                  <td colSpan={4} />
                </tr>
              </tfoot>
            )}
          </table>
        </div>
      </div>

      {/* Modal règlement */}
      {payModal.open && payModal.fournisseur && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-slate-900 border border-emerald-500/40 rounded-3xl shadow-2xl w-full max-w-md p-6 space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-black text-slate-100">Initier un Règlement</h3>
                <p className="text-xs text-slate-400 font-mono mt-1">{payModal.fournisseur.compte_401}  {payModal.fournisseur.fournisseur_nom}</p>
              </div>
              <button onClick={() => setPayModal({ fournisseur: null, open: false })} className="p-2 hover:bg-slate-800 rounded-xl text-slate-400">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-3 bg-slate-950 rounded-2xl p-4 border border-slate-800 text-xs font-mono">
              {[
                ['Montant Total Dû', `${payModal.fournisseur.total_du.toLocaleString('fr-FR')} XAF`, 'text-slate-100'],
                ['Échu (urgent)', `${(payModal.fournisseur.echu_1_30 + payModal.fournisseur.echu_31_60 + payModal.fournisseur.echu_plus_60).toLocaleString('fr-FR')} XAF`, 'text-amber-400'],
                ['Mode de paiement', payModal.fournisseur.mode_paiement, 'text-slate-200'],
              ].map(([k, v, c]) => (
                <div key={k} className="flex justify-between text-slate-400">
                  <span>{k}</span><span className={`font-bold ${c}`}>{v}</span>
                </div>
              ))}
            </div>
            <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs text-amber-300">
              <strong>Contrôle Dual :</strong> Cet ordre sera transmis à la DFC pour co-signature avant exécution bancaire (SYSCOHADA Article 64).
            </div>
            <div className="flex gap-3">
              <button onClick={() => setPayModal({ fournisseur: null, open: false })} className="flex-1 px-4 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs rounded-xl border border-slate-700">Annuler</button>
              <button onClick={confirmPaiement} disabled={submitting} className="flex-1 px-4 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2">
                {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <CreditCard className="w-4 h-4" />}
                {submitting ? 'En cours…' : 'Confirmer Règlement'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
