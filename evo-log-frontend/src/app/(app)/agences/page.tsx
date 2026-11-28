'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Building2, Search, Plus, MapPin, Phone, Mail, Users, RefreshCw, X,
  Globe, GitBranch, BarChart3, UserCog, ArrowLeft, CheckCircle2, AlertTriangle,
} from 'lucide-react';
import { agencesAPI } from '@/lib/api-client';

// ============================================================================
// Module Agences & succursales — reseau territorial multi-sites.
// Donnees reelles via /api/v1/agences : referentiel, comparatif inter-agences,
// effectifs, bascule d'agence active (perimetre ORM scope backend).
// ============================================================================

type Agency = {
  id: number; code: string; name: string; type_agence?: string;
  parent_id?: number | null; address?: string; city?: string; country?: string;
  phone?: string; email?: string; is_active: boolean; is_headquarters: boolean;
  users_count?: number; is_current?: boolean;
};

type Kpis = {
  utilisateurs?: { rattaches: number; session_active: number };
  tiers?: { clients_fournisseurs: number };
  transport?: { missions: number; camions: number; conducteurs: number; tournees: number; livraisons: number };
  parc?: { vehicules: number };
  acconage?: { navires: number; escales: number; conteneurs: number };
  finance?: { factures: number; ca_facture_ttc: number; ca_encaisse_ttc: number };
};

type ComparatifRow = Omit<Agency, 'city' | 'country'> & { ville?: string; pays?: string } & Kpis;

const TYPE_LABELS: Record<string, string> = {
  SIEGE: 'Siège', AGENCE: 'Agence', EXTENSION: 'Extension', BUREAU: 'Bureau',
};

const fmtXaf = (n?: number) =>
  n === undefined ? '—' : new Intl.NumberFormat('fr-FR').format(Math.round(n)) + ' XAF';

type Tab = 'reseau' | 'comparatif' | 'effectifs' | 'detail';

export default function AgencesPage() {
  const [tab, setTab] = useState<Tab>('reseau');
  const [agences, setAgences] = useState<Agency[]>([]);
  const [contexte, setContexte] = useState<{ agence_active: Agency | null; filtrage_actif: boolean; peut_gerer_reseau: boolean; peut_voir_pilotage?: boolean; peut_voir_comptes?: boolean; peut_gerer_comptes?: boolean } | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [comparatif, setComparatif] = useState<{ agences: ComparatifRow[]; donnees_non_rattachees?: Record<string, number> } | null>(null);
  const [detail, setDetail] = useState<any>(null);
  const [utilisateurs, setUtilisateurs] = useState<{ id: number; email: string; full_name?: string; role_level: number; is_active: boolean }[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    code: '', name: '', type_agence: 'AGENCE', parent_id: '',
    address: '', city: 'Douala', country: 'Cameroun', phone: '', email: '',
    is_headquarters: false,
  });
  const [error, setError] = useState<string | null>(null);

  const fetchReseau = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const [resCtx, resList] = await Promise.allSettled([
        agencesAPI.contexte(),
        agencesAPI.lister({ search: search || undefined, limit: 100 }),
      ]);
      if (resCtx.status === 'fulfilled') {
        const d = resCtx.value.data as any;
        setContexte({
          agence_active: d.agence_active, filtrage_actif: !!d.filtrage_actif,
          peut_gerer_reseau: !!d.peut_gerer_reseau, peut_voir_pilotage: !!d.peut_voir_pilotage,
          peut_voir_comptes: !!d.peut_voir_comptes, peut_gerer_comptes: !!d.peut_gerer_comptes,
        });
      }
      if (resList.status === 'fulfilled') {
        setAgences((resList.value.data as any)?.items ?? []);
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Chargement impossible');
    } finally { setLoading(false); }
  }, [search]);

  useEffect(() => { void fetchReseau(); }, [fetchReseau]);

  const fetchComparatif = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const res = await agencesAPI.comparatif();
      setComparatif(res.data as any);
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Comparatif indisponible');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => {
    if (tab === 'comparatif' && !comparatif) void fetchComparatif();
    if (tab === 'reseau') void fetchReseau();
  }, [tab]); // eslint-disable-line react-hooks/exhaustive-deps

  const ouvrirDetail = async (a: Agency) => {
    setTab('detail');
    try {
      const [resD, resT] = await Promise.allSettled([
        agencesAPI.detail(a.id),
        agencesAPI.tableauBord(a.id, 30),
      ]);
      const d = resD.status === 'fulfilled' ? resD.value.data : null;
      const t = resT.status === 'fulfilled' ? resT.value.data : null;
      setDetail(d ? { ...d, kpis: t?.kpis ?? d.kpis, activite: t?.activite } : null);
    } catch { setDetail(null); }
  };

  const chargerEffectifs = async (a: Agency) => {
    setTab('effectifs');
    setDetail(a);
    try {
      const res = await agencesAPI.utilisateurs(a.id);
      setUtilisateurs((res.data as any)?.items ?? []);
    } catch { setUtilisateurs([]); }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault(); setError(null);
    try {
      await agencesAPI.creer({
        ...formData,
        parent_id: formData.parent_id ? Number(formData.parent_id) : null,
      });
      setIsModalOpen(false);
      setFormData({ code: '', name: '', type_agence: 'AGENCE', parent_id: '', address: '', city: 'Douala', country: 'Cameroun', phone: '', email: '', is_headquarters: false });
      await fetchReseau();
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Création impossible');
    }
  };

  const handleActiver = async (id: number) => {
    try {
      await agencesAPI.activer(id);
      window.location.reload();
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Bascule impossible');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Confirmer la suppression ou désactivation de cette agence ?')) return;
    try { await agencesAPI.supprimer(id); await fetchReseau(); }
    catch (e: any) { setError(e?.response?.data?.detail ?? 'Suppression impossible'); }
  };

  const TABS: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: 'reseau', label: 'Réseau d’agences', icon: <Building2 className="w-4 h-4" /> },
    ...(contexte?.peut_voir_pilotage ? [{ key: 'comparatif' as Tab, label: 'Comparatif inter-agences', icon: <BarChart3 className="w-4 h-4" /> }] : []),
    ...(contexte?.peut_voir_comptes ? [{ key: 'effectifs' as Tab, label: 'Effectifs', icon: <UserCog className="w-4 h-4" /> }] : []),
    { key: 'detail', label: 'Fiche agence', icon: <GitBranch className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Building2 className="w-3.5 h-3.5" /> Gouvernance & Réseau territorial
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Agences, succursales & extensions
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Multi-sites national et international : bascule d'agence active, filtrage des données par site, comparatif.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={() => void fetchReseau()} className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700" title="Actualiser">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          {contexte?.peut_gerer_reseau && (
            <button onClick={() => setIsModalOpen(true)} className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-lg shadow-blue-600/20">
              <Plus className="w-4 h-4" /> Nouvelle agence
            </button>
          )}
        </div>
      </div>

      {/* Contexte actif */}
      {contexte && (
        <div className={`flex items-center gap-3 px-5 py-3 rounded-2xl border text-sm ${
          contexte.agence_active
            ? 'bg-blue-500/10 border-blue-500/30 text-blue-300'
            : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
        }`}>
          <Globe className="w-4 h-4 shrink-0" />
          <span>
            {contexte.agence_active
              ? <>Agence active : <strong>{contexte.agence_active.name}</strong> ({contexte.agence_active.city}, {contexte.agence_active.country}) — vous ne voyez que ses données + les données partagées.</>
              : 'Vue consolidée : toutes les agences et données partagées sont visibles.'}
          </span>
          {contexte.agence_active && (
            <button onClick={async () => { await agencesAPI.reinitialiser(); window.location.reload(); }} className="ml-auto text-xs font-bold underline hover:no-underline">
              Revenir à la vue consolidée
            </button>
          )}
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
          <AlertTriangle className="w-4 h-4" /> {error}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-900/60 border border-slate-800 rounded-2xl p-1 w-fit">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-colors ${
              tab === t.key ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* ── Onglet Réseau ── */}
      {tab === 'reseau' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            <div className="col-span-full py-12 text-center text-slate-400"><RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />Chargement…</div>
          ) : agences.length === 0 ? (
            <div className="col-span-full py-12 text-center text-slate-500">Aucune agence accessible. Créez la première succursale.</div>
          ) : agences.map((a) => (
            <div key={a.id} className={`bg-slate-900/80 border rounded-3xl p-6 shadow-xl space-y-4 transition-all ${a.is_current ? 'border-blue-500/60 ring-1 ring-blue-500/30' : 'border-slate-800 hover:border-slate-700'}`}>
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-mono font-bold text-blue-400 px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20">{a.code}</span>
                  <h3 className="text-lg font-bold text-white mt-2">{a.name}</h3>
                  <p className="text-xs text-slate-400">{TYPE_LABELS[a.type_agence ?? 'AGENCE'] ?? a.type_agence}</p>
                </div>
                {a.is_headquarters && <span className="text-[11px] font-bold px-2 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400">Siège</span>}
              </div>
              <div className="space-y-2 text-xs text-slate-300 pt-2 border-t border-slate-800/60">
                <div className="flex items-center gap-2"><MapPin className="w-3.5 h-3.5 text-slate-500" /><span>{a.city}, {a.country}</span></div>
                {a.phone && <div className="flex items-center gap-2"><Phone className="w-3.5 h-3.5 text-slate-500" /><span>{a.phone}</span></div>}
                <div className="flex items-center gap-2"><Users className="w-3.5 h-3.5 text-slate-500" /><span>{a.users_count ?? 0} collaborateur(s)</span></div>
              </div>
              <div className="pt-3 border-t border-slate-800/60 flex flex-wrap items-center gap-2">
                <span className={`inline-flex items-center gap-1 text-xs font-bold ${a.is_active ? 'text-emerald-400' : 'text-slate-500'}`}>
                  <span className={`w-2 h-2 rounded-full ${a.is_active ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                  {a.is_active ? 'Opérationnelle' : 'Inactive'}
                </span>
                {!a.is_current && a.is_active && (
                  <button onClick={() => void handleActiver(a.id)} className="ml-auto text-xs font-bold px-3 py-1.5 rounded-lg bg-blue-600/20 text-blue-300 hover:bg-blue-600/40 border border-blue-500/30">
                    Basculer ici
                  </button>
                )}
                {a.is_current && <span className="ml-auto text-xs font-bold px-3 py-1.5 rounded-lg bg-blue-600 text-white">Active</span>}
                <button onClick={() => void ouvrirDetail(a)} className="text-xs text-slate-300 hover:text-white font-medium px-2 py-1.5">Détail</button>
                {contexte?.peut_voir_comptes && (
                  <button onClick={() => void chargerEffectifs(a)} className="text-xs text-slate-300 hover:text-white font-medium px-2 py-1.5">Effectifs</button>
                )}
                {contexte?.peut_gerer_reseau && (
                  <button onClick={() => void handleDelete(a.id)} className="text-xs text-rose-400 hover:text-rose-300 font-medium px-2 py-1.5">Supprimer</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Onglet Comparatif ── */}
      {tab === 'comparatif' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden">
          <div className="p-5 border-b border-slate-800 flex items-center justify-between">
            <h2 className="font-bold text-white flex items-center gap-2"><BarChart3 className="w-5 h-5 text-blue-400" /> Performance par agence</h2>
            <button onClick={() => { setComparatif(null); void fetchComparatif(); }} className="text-xs text-slate-400 hover:text-white flex items-center gap-1"><RefreshCw className="w-3.5 h-3.5" /> Actualiser</button>
          </div>
          {loading || !comparatif ? (
            <div className="p-12 text-center text-slate-400"><RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />Calcul des KPI par agence…</div>
          ) : comparatif.agences.length === 0 ? (
            <div className="p-12 text-center text-slate-500">Aucune agence active.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-800">
                    <th className="px-5 py-3">Agence</th>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3 text-right">Collaborateurs</th>
                    <th className="px-4 py-3 text-right">Tiers</th>
                    <th className="px-4 py-3 text-right">Missions</th>
                    <th className="px-4 py-3 text-right">Véhicules</th>
                    <th className="px-4 py-3 text-right">Escales</th>
                    <th className="px-4 py-3 text-right">Conteneurs</th>
                    <th className="px-4 py-3 text-right">Factures</th>
                    <th className="px-4 py-3 text-right">CA TTC</th>
                    <th className="px-4 py-3 text-right">Encaissé</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {comparatif.agences.map((r) => (
                    <tr key={r.id} className={`border-b border-slate-800/60 hover:bg-slate-800/40 ${r.is_current ? 'bg-blue-500/5' : ''}`}>
                      <td className="px-5 py-3">
                        <div className="font-bold text-white">{r.name}</div>
                        <div className="text-[11px] text-slate-500">{r.code} — {r.ville}, {r.pays}</div>
                      </td>
                      <td className="px-4 py-3 text-slate-400">{TYPE_LABELS[r.type_agence ?? 'AGENCE'] ?? '—'}</td>
                      <td className="px-4 py-3 text-right text-slate-200">{r.utilisateurs?.rattaches ?? 0}</td>
                      <td className="px-4 py-3 text-right text-slate-200">{r.tiers?.clients_fournisseurs ?? 0}</td>
                      <td className="px-4 py-3 text-right text-slate-200">{r.transport?.missions ?? 0}</td>
                      <td className="px-4 py-3 text-right text-slate-200">{(r.parc?.vehicules ?? 0) + (r.transport?.camions ?? 0)}</td>
                      <td className="px-4 py-3 text-right text-slate-200">{r.acconage?.escales ?? 0}</td>
                      <td className="px-4 py-3 text-right text-slate-200">{r.acconage?.conteneurs ?? 0}</td>
                      <td className="px-4 py-3 text-right text-slate-200">{r.finance?.factures ?? 0}</td>
                      <td className="px-4 py-3 text-right font-mono text-slate-200">{fmtXaf(r.finance?.ca_facture_ttc)}</td>
                      <td className="px-4 py-3 text-right font-mono text-emerald-400">{fmtXaf(r.finance?.ca_encaisse_ttc)}</td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex gap-1 justify-end">
                          {!r.is_current && r.is_active && (
                            <button onClick={() => void handleActiver(r.id)} className="text-[11px] font-bold px-2 py-1 rounded-lg bg-blue-600/20 text-blue-300 hover:bg-blue-600/40 border border-blue-500/30">Basculer</button>
                          )}
                          <button onClick={() => void ouvrirDetail(r)} className="text-[11px] font-bold px-2 py-1 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700">Détail</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {comparatif?.donnees_non_rattachees && (
            <div className="px-5 py-3 border-t border-slate-800 text-[11px] text-slate-500">
              Données non rattachées (visibles par toutes les agences) : {comparatif.donnees_non_rattachees.tiers ?? 0} tiers · {comparatif.donnees_non_rattachees.missions ?? 0} missions · {comparatif.donnees_non_rattachees.factures ?? 0} factures
            </div>
          )}
        </div>
      )}

      {/* ── Onglet Effectifs ── */}
      {tab === 'effectifs' && detail && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden">
          <div className="p-5 border-b border-slate-800 flex items-center justify-between">
            <h2 className="font-bold text-white flex items-center gap-2"><Users className="w-5 h-5 text-blue-400" /> Effectifs — {detail.name}</h2>
            <button onClick={() => setTab('reseau')} className="text-xs text-slate-400 hover:text-white flex items-center gap-1"><ArrowLeft className="w-3.5 h-3.5" /> Retour</button>
          </div>
          {utilisateurs.length === 0 ? (
            <div className="p-12 text-center text-slate-500">Aucun collaborateur rattaché à cette agence.</div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-800">
                  <th className="px-5 py-3">Collaborateur</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3 text-right">Niveau</th>
                  <th className="px-4 py-3">Statut</th>
                </tr>
              </thead>
              <tbody>
                {utilisateurs.map((u) => (
                  <tr key={u.id} className="border-b border-slate-800/60">
                    <td className="px-5 py-3 font-semibold text-white">{u.full_name || `#${u.id}`}</td>
                    <td className="px-4 py-3 text-slate-400">{u.email}</td>
                    <td className="px-4 py-3 text-right text-slate-300">{u.role_level}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-bold ${u.is_active ? 'text-emerald-400' : 'text-slate-500'}`}>{u.is_active ? 'Actif' : 'Inactif'}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* ── Onglet Détail ── */}
      {tab === 'detail' && detail && (
        <div className="space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-mono font-bold text-blue-400 px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20">{detail.code}</span>
                <h2 className="text-2xl font-black text-white mt-2">{detail.name}</h2>
                <p className="text-sm text-slate-400">{TYPE_LABELS[detail.type_agence ?? 'AGENCE']} — {detail.city}, {detail.country}</p>
              </div>
              <button onClick={() => setTab('reseau')} className="text-xs text-slate-400 hover:text-white flex items-center gap-1"><ArrowLeft className="w-3.5 h-3.5" /> Retour</button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-5 text-xs">
              {[
                ['Collaborateurs', detail.kpis?.utilisateurs?.rattaches ?? detail.collaborateurs?.length ?? 0],
                ['Tiers', detail.kpis?.tiers?.clients_fournisseurs ?? 0],
                ['Missions', detail.kpis?.transport?.missions ?? 0],
                ['CA facturé TTC', fmtXaf(detail.kpis?.finance?.ca_facture_ttc)],
                ['Encaissé TTC', fmtXaf(detail.kpis?.finance?.ca_encaisse_ttc)],
                ['Véhicules', (detail.kpis?.parc?.vehicules ?? 0) + (detail.kpis?.transport?.camions ?? 0)],
                ['Escales', detail.kpis?.acconage?.escales ?? 0],
                ['Conteneurs', detail.kpis?.acconage?.conteneurs ?? 0],
              ].map(([label, val]) => (
                <div key={String(label)} className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
                  <div className="text-slate-500">{label}</div>
                  <div className="text-lg font-black text-white mt-1">{val}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Modal création */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2"><Building2 className="w-5 h-5 text-blue-400" /> Nouvelle agence / extension</h2>
              <button onClick={() => setIsModalOpen(false)} className="p-1 rounded-lg text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Code (trigramme)</label>
                  <input type="text" required placeholder="ex: KBI" value={formData.code} onChange={(e) => setFormData({ ...formData, code: e.target.value })} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Type</label>
                  <select value={formData.type_agence} onChange={(e) => setFormData({ ...formData, type_agence: e.target.value })} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white">
                    {Object.entries(TYPE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Nom</label>
                <input type="text" required placeholder="ex: Agence Port Kribi" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Agence parente (extension/bureau)</label>
                <select value={formData.parent_id} onChange={(e) => setFormData({ ...formData, parent_id: e.target.value })} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white">
                  <option value="">— Aucune (agence principale) —</option>
                  {agences.map((a) => <option key={a.id} value={a.id}>{a.name} ({a.code})</option>)}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Ville</label>
                  <input type="text" required value={formData.city} onChange={(e) => setFormData({ ...formData, city: e.target.value })} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Pays</label>
                  <input type="text" required value={formData.country} onChange={(e) => setFormData({ ...formData, country: e.target.value })} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Adresse</label>
                <input type="text" value={formData.address} onChange={(e) => setFormData({ ...formData, address: e.target.value })} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Téléphone</label>
                  <input type="text" value={formData.phone} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Email</label>
                  <input type="email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
                </div>
              </div>
              <label className="flex items-center gap-2 text-xs font-semibold text-slate-300">
                <input type="checkbox" checked={formData.is_headquarters} onChange={(e) => setFormData({ ...formData, is_headquarters: e.target.checked })} className="rounded bg-slate-800 border-slate-700" />
                Désigner comme siège social
              </label>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold">Annuler</button>
                <button type="submit" className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold">Créer</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
