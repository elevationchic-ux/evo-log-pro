'use client';

import React, { useEffect, useState } from 'react';
import { deepAPI } from '@/lib/api-client';
import { RefreshCw } from 'lucide-react';
import Link from 'next/link';

type Impersonation = {
  id: number;
  reference: string;
  admin?: string | null;
  cible_tenant?: string | null;
  motif?: string | null;
  debut?: string | null;
  fin?: string | null;
  statut?: string | null;
};

type Backup = {
  id: number;
  reference: string;
  tenant?: string | null;
  taille_octets?: number | null;
  frequence?: string | null;
  derniere_reussite?: string | null;
  statut?: string | null;
};

const fmtDate = (d?: string | null) => (d ? new Date(d).toLocaleString('fr-FR') : '—');
const fmtTaille = (n?: number | null) =>
  n === null || n === undefined ? '—' : n > 1e9 ? `${(n / 1e9).toFixed(1)} Go` : `${(n / 1e6).toFixed(1)} Mo`;

export default function AdminTenantSecuritePage() {
  const [impersonations, setImpersonations] = useState<Impersonation[]>([]);
  const [backups, setBackups] = useState<Backup[]>([]);
  const [loading, setLoading] = useState(true);
  const [formI, setFormI] = useState({ reference: '', admin: '', cible_tenant: '', motif: '', statut: 'en_cours' });
  const [formB, setFormB] = useState({ reference: '', tenant: '', taille_octets: '', frequence: 'quotidienne', statut: 'reussie' });
  const [msg, setMsg] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const [i, b] = await Promise.all([deepAPI.getImpersonationLogs(), deepAPI.getTenantBackups()]);
      const id = (i.data ?? i) as Impersonation[] | { items?: Impersonation[] };
      const bd = (b.data ?? b) as Backup[] | { items?: Backup[] };
      setImpersonations(Array.isArray(id) ? id : (id.items ?? []));
      setBackups(Array.isArray(bd) ? bd : (bd.items ?? []));
    } catch { /* endpoints peuvent être vides */ }
    setLoading(false);
  };
  useEffect(() => { load(); }, []);

  const submitI = async (e: React.FormEvent) => {
    e.preventDefault(); setMsg(null);
    try {
      await deepAPI.createImpersonationLog({
        reference: formI.reference,
        admin: formI.admin || undefined,
        cible_tenant: formI.cible_tenant || undefined,
        motif: formI.motif || undefined,
        statut: formI.statut || undefined,
      });
      setMsg('Session d’impersonation journalisée.');
      setFormI({ reference: '', admin: '', cible_tenant: '', motif: '', statut: 'en_cours' }); load();
    } catch (err: unknown) { setMsg(err instanceof Error ? err.message : 'Erreur'); }
  };

  const submitB = async (e: React.FormEvent) => {
    e.preventDefault(); setMsg(null);
    try {
      await deepAPI.createTenantBackup({
        reference: formB.reference,
        tenant: formB.tenant || undefined,
        taille_octets: formB.taille_octets ? Number(formB.taille_octets) : undefined,
        frequence: formB.frequence || undefined,
        statut: formB.statut || undefined,
      });
      setMsg('Sauvegarde enregistrée.');
      setFormB({ reference: '', tenant: '', taille_octets: '', frequence: 'quotidienne', statut: 'reussie' }); load();
    } catch (err: unknown) { setMsg(err instanceof Error ? err.message : 'Erreur'); }
  };

  return (
    <div className="p-6 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/admin-tenant/dashboard" className="text-sm text-gray-400 hover:text-gray-600">← Admin Tenant</Link>
          <h1 className="text-2xl font-bold mt-1">Impersonations & sauvegardes</h1>
          <p className="text-sm text-gray-500">Journal d'audit des accès support et état des sauvegardes tenants.</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 px-3 py-2 text-sm border rounded-lg hover:bg-gray-50">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Actualiser
        </button>
      </div>
      {msg && <p className="text-sm text-blue-700">{msg}</p>}

      <section>
        <h2 className="text-lg font-semibold mb-3">Sessions d'impersonation</h2>
        <form onSubmit={submitI} className="bg-white border rounded-xl p-5 shadow-sm grid grid-cols-6 gap-3 items-end mb-4">
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Référence *</span>
            <input required value={formI.reference} onChange={(e) => setFormI({ ...formI, reference: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" placeholder="IMP-001" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Admin</span>
            <input value={formI.admin} onChange={(e) => setFormI({ ...formI, admin: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Tenant cible</span>
            <input value={formI.cible_tenant} onChange={(e) => setFormI({ ...formI, cible_tenant: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Motif</span>
            <input value={formI.motif} onChange={(e) => setFormI({ ...formI, motif: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" placeholder="Support ticket #123" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Statut</span>
            <select value={formI.statut} onChange={(e) => setFormI({ ...formI, statut: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm">
              <option value="en_cours">En cours</option>
              <option value="terminee">Terminée</option>
              <option value="refusee">Refusée</option>
            </select></label>
          <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">Journaliser</button>
        </form>
        <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs text-gray-500">
              <tr><th className="px-4 py-3">Référence</th><th className="px-4 py-3">Admin</th><th className="px-4 py-3">Tenant cible</th><th className="px-4 py-3">Motif</th><th className="px-4 py-3">Début</th><th className="px-4 py-3">Fin</th><th className="px-4 py-3">Statut</th></tr>
            </thead>
            <tbody>
              {impersonations.map((i) => (
                <tr key={i.id} className="border-t">
                  <td className="px-4 py-2 font-medium">{i.reference}</td>
                  <td className="px-4 py-2">{i.admin ?? '—'}</td>
                  <td className="px-4 py-2">{i.cible_tenant ?? '—'}</td>
                  <td className="px-4 py-2">{i.motif ?? '—'}</td>
                  <td className="px-4 py-2">{fmtDate(i.debut)}</td>
                  <td className="px-4 py-2">{fmtDate(i.fin)}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${i.statut === 'terminee' ? 'bg-green-100 text-green-700' : i.statut === 'refusee' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>
                      {i.statut ?? '—'}
                    </span>
                  </td>
                </tr>
              ))}
              {!loading && impersonations.length === 0 && <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">Aucune session</td></tr>}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Sauvegardes tenants</h2>
        <form onSubmit={submitB} className="bg-white border rounded-xl p-5 shadow-sm grid grid-cols-6 gap-3 items-end mb-4">
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Référence *</span>
            <input required value={formB.reference} onChange={(e) => setFormB({ ...formB, reference: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" placeholder="BAK-2025-001" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Tenant</span>
            <input value={formB.tenant} onChange={(e) => setFormB({ ...formB, tenant: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Taille (octets)</span>
            <input type="number" value={formB.taille_octets} onChange={(e) => setFormB({ ...formB, taille_octets: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" /></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Fréquence</span>
            <select value={formB.frequence} onChange={(e) => setFormB({ ...formB, frequence: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm">
              <option value="quotidienne">Quotidienne</option>
              <option value="hebdomadaire">Hebdomadaire</option>
              <option value="mensuelle">Mensuelle</option>
            </select></label>
          <label className="text-sm"><span className="block text-xs text-gray-500 mb-1">Statut</span>
            <select value={formB.statut} onChange={(e) => setFormB({ ...formB, statut: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm">
              <option value="reussie">Réussie</option>
              <option value="echouee">Échouée</option>
              <option value="en_cours">En cours</option>
            </select></label>
          <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">Enregistrer</button>
        </form>
        <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs text-gray-500">
              <tr><th className="px-4 py-3">Référence</th><th className="px-4 py-3">Tenant</th><th className="px-4 py-3">Taille</th><th className="px-4 py-3">Fréquence</th><th className="px-4 py-3">Dernière réussite</th><th className="px-4 py-3">Statut</th></tr>
            </thead>
            <tbody>
              {backups.map((b) => (
                <tr key={b.id} className="border-t">
                  <td className="px-4 py-2 font-medium">{b.reference}</td>
                  <td className="px-4 py-2">{b.tenant ?? '—'}</td>
                  <td className="px-4 py-2">{fmtTaille(b.taille_octets)}</td>
                  <td className="px-4 py-2">{b.frequence ?? '—'}</td>
                  <td className="px-4 py-2">{fmtDate(b.derniere_reussite)}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${b.statut === 'reussie' ? 'bg-green-100 text-green-700' : b.statut === 'echouee' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>
                      {b.statut ?? '—'}
                    </span>
                  </td>
                </tr>
              ))}
              {!loading && backups.length === 0 && <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">Aucune sauvegarde</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
