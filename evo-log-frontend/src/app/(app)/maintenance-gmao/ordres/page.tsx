'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Wrench, Plus, RefreshCw, CheckCircle2, Cog } from 'lucide-react';
import { apiClient, apiUrl } from '@/lib/api-client';
import { toast } from 'sonner';

interface Ordre {
  id: number;
  numero_ordre: string;
  equipement_id: number;
  type_maintenance: string;
  priorite: string;
  description: string;
  date_planifiee?: string;
  duree_estimee?: number;
  travaux?: string;
  technicien_id?: number;
  statut: string;
  cout_total?: number;
}

interface Equipement {
  id: number;
  numero_serie: string;
  designation: string;
  type_equipement: string;
  marque?: string;
  modele?: string;
  localisation?: string;
  statut?: string;
}

const TYPES_MAINT = ['preventive', 'corrective', 'predictive', 'conditionnelle', 'ameliorative'];
const PRIORITES = ['critique', 'haute', 'moyenne', 'basse'];
const STATUTS: Record<string, string> = {
  planifiee: 'bg-sky-500/15 text-sky-400 border-sky-500/30',
  en_cours: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  en_attente: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
  valide: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  annulee: 'bg-slate-500/15 text-slate-400 border-slate-500/30',
  rejete: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
};

export default function GmaoOrdresPage() {
  const [onglet, setOnglet] = useState<'ordres' | 'equipements'>('ordres');
  const [ordres, setOrdres] = useState<Ordre[]>([]);
  const [equipements, setEquipements] = useState<Equipement[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formOT, setFormOT] = useState({
    numero_ordre: '', equipement_id: '', type_maintenance: 'preventive',
    priorite: 'moyenne', description: '', date_planifiee: new Date().toISOString().slice(0, 10),
    duree_estimee: 2, travaux: '', technicien_id: '',
  });
  const [formEq, setFormEq] = useState({
    numero_serie: '', designation: '', type_equipement: 'autre',
    marque: '', modele: '', localisation: '',
  });

  const charger = useCallback(async () => {
    setLoading(true);
    try {
      const [o, e] = await Promise.all([
        apiClient.get(apiUrl('/maintenance-gmao/ordres')),
        apiClient.get(apiUrl('/maintenance-gmao/equipements')),
      ]);
      setOrdres(Array.isArray(o.data) ? o.data : o.data?.items || []);
      setEquipements(Array.isArray(e.data) ? e.data : e.data?.items || []);
    } catch { toast.error('Impossible de charger les données GMAO'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  const creerOT = async (ev: React.FormEvent) => {
    ev.preventDefault();
    try {
      await apiClient.post(apiUrl('/maintenance-gmao/ordres'), {
        ...formOT,
        equipement_id: Number(formOT.equipement_id),
        duree_estimee: Number(formOT.duree_estimee),
        technicien_id: formOT.technicien_id ? Number(formOT.technicien_id) : null,
      });
      toast.success('Ordre de maintenance créé');
      setShowForm(false);
      charger();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur création OT');
    }
  };

  const creerEquipement = async (ev: React.FormEvent) => {
    ev.preventDefault();
    try {
      await apiClient.post(apiUrl('/maintenance-gmao/equipements'), formEq);
      toast.success('Équipement enregistré');
      setShowForm(false);
      charger();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur création équipement');
    }
  };

  const completer = async (id: number) => {
    try {
      await apiClient.put(apiUrl(`/maintenance-gmao/ordres/${id}/completer`), {});
      toast.success('OT complété');
      charger();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur');
    }
  };

  const input = 'w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-cyan-500 focus:outline-none min-h-[44px]';
  const label = 'block text-xs font-medium text-slate-400 mb-1';

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 md:p-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-xl font-semibold text-slate-100">
            <Cog className="h-6 w-6 text-cyan-400" /> GMAO — Ordres &amp; Équipements
          </h1>
          <p className="text-sm text-slate-400">Gestion des ordres de maintenance et du parc d'équipements.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={charger} className="inline-flex min-h-[44px] items-center gap-2 rounded-lg border border-slate-700 px-4 text-sm text-slate-300 hover:bg-slate-800">
            <RefreshCw className="h-4 w-4" /> Actualiser
          </button>
          <button onClick={() => setShowForm(!showForm)} className="inline-flex min-h-[44px] items-center gap-2 rounded-lg bg-cyan-600 px-4 text-sm font-medium text-white hover:bg-cyan-500">
            <Plus className="h-4 w-4" /> {onglet === 'ordres' ? 'Nouvel OT' : 'Nouvel équipement'}
          </button>
        </div>
      </header>

      <div className="flex items-center gap-2">
        {(['ordres', 'equipements'] as const).map(o => (
          <button key={o} onClick={() => { setOnglet(o); setShowForm(false); }}
            className={`rounded-lg px-4 py-2 text-sm font-medium min-h-[44px] ${onglet === o ? 'bg-cyan-600 text-white' : 'border border-slate-700 text-slate-300 hover:bg-slate-800'}`}>
            {o === 'ordres' ? `Ordres (${ordres.length})` : `Équipements (${equipements.length})`}
          </button>
        ))}
      </div>

      {showForm && onglet === 'ordres' && (
        <form onSubmit={creerOT} className="rounded-xl border border-slate-700 bg-slate-900/50 p-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div><label className={label}>N° ordre *</label><input required className={input} value={formOT.numero_ordre} onChange={e => setFormOT({ ...formOT, numero_ordre: e.target.value })} placeholder="OT-2026-001" /></div>
            <div><label className={label}>Équipement *</label>
              <select required className={input} value={formOT.equipement_id} onChange={e => setFormOT({ ...formOT, equipement_id: e.target.value })}>
                <option value="">— Sélectionner —</option>
                {equipements.map(eq => <option key={eq.id} value={eq.id}>{eq.numero_serie} — {eq.designation}</option>)}
              </select>
            </div>
            <div><label className={label}>Type</label>
              <select className={input} value={formOT.type_maintenance} onChange={e => setFormOT({ ...formOT, type_maintenance: e.target.value })}>
                {TYPES_MAINT.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div><label className={label}>Priorité</label>
              <select className={input} value={formOT.priorite} onChange={e => setFormOT({ ...formOT, priorite: e.target.value })}>
                {PRIORITES.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div><label className={label}>Planifié le *</label><input required type="date" className={input} value={formOT.date_planifiee} onChange={e => setFormOT({ ...formOT, date_planifiee: e.target.value })} /></div>
            <div><label className={label}>Durée estimée (h)</label><input type="number" min={0} className={input} value={formOT.duree_estimee} onChange={e => setFormOT({ ...formOT, duree_estimee: Number(e.target.value) })} /></div>
            <div className="md:col-span-2"><label className={label}>Description *</label><input required className={input} value={formOT.description} onChange={e => setFormOT({ ...formOT, description: e.target.value })} /></div>
            <div><label className={label}>Technicien ID</label><input type="number" className={input} value={formOT.technicien_id} onChange={e => setFormOT({ ...formOT, technicien_id: e.target.value })} /></div>
            <div className="md:col-span-3"><label className={label}>Travaux</label><input className={input} value={formOT.travaux} onChange={e => setFormOT({ ...formOT, travaux: e.target.value })} /></div>
          </div>
          <div className="mt-4 flex justify-end gap-2">
            <button type="button" onClick={() => setShowForm(false)} className="min-h-[44px] rounded-lg px-4 text-sm text-slate-400 hover:bg-slate-800">Annuler</button>
            <button type="submit" className="min-h-[44px] rounded-lg bg-cyan-600 px-5 text-sm font-medium text-white hover:bg-cyan-500">Créer l'OT</button>
          </div>
        </form>
      )}

      {showForm && onglet === 'equipements' && (
        <form onSubmit={creerEquipement} className="rounded-xl border border-slate-700 bg-slate-900/50 p-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div><label className={label}>N° série *</label><input required className={input} value={formEq.numero_serie} onChange={e => setFormEq({ ...formEq, numero_serie: e.target.value })} /></div>
            <div className="md:col-span-2"><label className={label}>Désignation *</label><input required className={input} value={formEq.designation} onChange={e => setFormEq({ ...formEq, designation: e.target.value })} /></div>
            <div><label className={label}>Type</label><input required className={input} value={formEq.type_equipement} onChange={e => setFormEq({ ...formEq, type_equipement: e.target.value })} placeholder="grue, camion, groupe…" /></div>
            <div><label className={label}>Marque</label><input className={input} value={formEq.marque} onChange={e => setFormEq({ ...formEq, marque: e.target.value })} /></div>
            <div><label className={label}>Modèle</label><input className={input} value={formEq.modele} onChange={e => setFormEq({ ...formEq, modele: e.target.value })} /></div>
            <div><label className={label}>Localisation</label><input className={input} value={formEq.localisation} onChange={e => setFormEq({ ...formEq, localisation: e.target.value })} /></div>
          </div>
          <div className="mt-4 flex justify-end gap-2">
            <button type="button" onClick={() => setShowForm(false)} className="min-h-[44px] rounded-lg px-4 text-sm text-slate-400 hover:bg-slate-800">Annuler</button>
            <button type="submit" className="min-h-[44px] rounded-lg bg-cyan-600 px-5 text-sm font-medium text-white hover:bg-cyan-500">Enregistrer</button>
          </div>
        </form>
      )}

      {onglet === 'ordres' && (
        <section className="overflow-x-auto rounded-xl border border-slate-700">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
              <tr>
                <th className="px-4 py-3">N° OT</th><th className="px-4 py-3">Équipement</th>
                <th className="px-4 py-3">Type</th><th className="px-4 py-3">Priorité</th>
                <th className="px-4 py-3">Planifié</th><th className="px-4 py-3 text-right">Coût</th>
                <th className="px-4 py-3">Statut</th><th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-500">Chargement…</td></tr>
              ) : ordres.length === 0 ? (
                <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-500">Aucun ordre de maintenance.</td></tr>
              ) : ordres.map(o => (
                <tr key={o.id} className="hover:bg-slate-900/50">
                  <td className="px-4 py-3 font-mono text-xs text-cyan-300">{o.numero_ordre}</td>
                  <td className="px-4 py-3 text-slate-300">#{o.equipement_id}</td>
                  <td className="px-4 py-3 capitalize text-slate-300">{o.type_maintenance}</td>
                  <td className="px-4 py-3 capitalize text-slate-400">{o.priorite}</td>
                  <td className="px-4 py-3 text-slate-400">{o.date_planifiee || '—'}</td>
                  <td className="px-4 py-3 text-right text-slate-300">{Number(o.cout_total || 0).toLocaleString('fr-FR')}</td>
                  <td className="px-4 py-3"><span className={`rounded-full border px-2 py-0.5 text-xs ${STATUTS[o.statut] || 'border-slate-600 text-slate-400'}`}>{o.statut}</span></td>
                  <td className="px-4 py-3 text-right">
                    {o.statut === 'planifiee' && (
                      <button onClick={() => completer(o.id)} className="inline-flex min-h-[44px] items-center gap-1 rounded-lg px-2 text-xs text-emerald-400 hover:bg-emerald-500/10">
                        <CheckCircle2 className="h-4 w-4" /> Compléter
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {onglet === 'equipements' && (
        <section className="overflow-x-auto rounded-xl border border-slate-700">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
              <tr>
                <th className="px-4 py-3">N° série</th><th className="px-4 py-3">Désignation</th>
                <th className="px-4 py-3">Type</th><th className="px-4 py-3">Marque/Modèle</th>
                <th className="px-4 py-3">Localisation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-500">Chargement…</td></tr>
              ) : equipements.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-500"><Wrench className="mx-auto mb-2 h-8 w-8 text-slate-600" />Aucun équipement.</td></tr>
              ) : equipements.map(eq => (
                <tr key={eq.id} className="hover:bg-slate-900/50">
                  <td className="px-4 py-3 font-mono text-xs text-cyan-300">{eq.numero_serie}</td>
                  <td className="px-4 py-3 text-slate-200">{eq.designation}</td>
                  <td className="px-4 py-3 capitalize text-slate-300">{eq.type_equipement}</td>
                  <td className="px-4 py-3 text-slate-400">{[eq.marque, eq.modele].filter(Boolean).join(' ') || '—'}</td>
                  <td className="px-4 py-3 text-slate-400">{eq.localisation || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
