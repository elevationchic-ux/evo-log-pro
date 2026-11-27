'use client';

import React, { useEffect, useState } from 'react';
import { deepAPI } from '@/lib/api-client';
import { RefreshCw } from 'lucide-react';
import Link from 'next/link';

type Permit = {
  id: number;
  reference: string;
  type?: string | null;
  lieu?: string | null;
  demandeur?: string | null;
  debut?: string | null;
  statut?: string | null;
  is_active?: boolean | null;
};

export default function PermisTravailPage() {
  const [rows, setRows] = useState<Permit[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ reference: '', type: '', lieu: '', demandeur: '', debut: '', statut: 'demande' });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const res = await deepAPI.getWorkPermitRequests();
      const data = (res.data ?? res) as Permit[] | { items?: Permit[] };
      setRows(Array.isArray(data) ? data : (data.items ?? []));
    } catch { setRows([]); }
    setLoading(false);
  };
  useEffect(() => { load(); }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true); setMsg(null);
    try {
      await deepAPI.createWorkPermitRequest({
        reference: form.reference,
        type: form.type || undefined,
        lieu: form.lieu || undefined,
        demandeur: form.demandeur || undefined,
        debut: form.debut ? new Date(form.debut).toISOString() : undefined,
        statut: form.statut || undefined,
      });
      setMsg('Demande enregistrée.');
      setForm({ reference: '', type: '', lieu: '', demandeur: '', debut: '', statut: 'demande' });
      load();
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : 'Erreur');
    } finally { setSaving(false); }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/portail-qhse" className="text-sm text-gray-400 hover:text-gray-600">← Portail QHSE</Link>
          <h1 className="text-2xl font-bold mt-1">Permis de travail</h1>
          <p className="text-sm text-gray-500">Demandes d'autorisation pour travaux à risque.</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 px-3 py-2 text-sm border rounded-lg hover:bg-gray-50">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Actualiser
        </button>
      </div>

      <form onSubmit={submit} className="bg-white border rounded-xl p-5 shadow-sm grid grid-cols-3 gap-3 items-end">
        <label className="text-sm">
          <span className="block text-xs text-gray-500 mb-1">Référence *</span>
          <input required value={form.reference}
            onChange={(e) => setForm({ ...form, reference: e.target.value })}
            className="w-full border rounded px-2 py-1.5 text-sm" placeholder="PT-2025-001" />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-gray-500 mb-1">Type</span>
          <input value={form.type}
            onChange={(e) => setForm({ ...form, type: e.target.value })}
            className="w-full border rounded px-2 py-1.5 text-sm" placeholder="Travail en hauteur" />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-gray-500 mb-1">Lieu</span>
          <input value={form.lieu}
            onChange={(e) => setForm({ ...form, lieu: e.target.value })}
            className="w-full border rounded px-2 py-1.5 text-sm" placeholder="Quai 3" />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-gray-500 mb-1">Demandeur</span>
          <input value={form.demandeur}
            onChange={(e) => setForm({ ...form, demandeur: e.target.value })}
            className="w-full border rounded px-2 py-1.5 text-sm" />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-gray-500 mb-1">Début</span>
          <input type="datetime-local" value={form.debut}
            onChange={(e) => setForm({ ...form, debut: e.target.value })}
            className="w-full border rounded px-2 py-1.5 text-sm" />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-gray-500 mb-1">Statut</span>
          <select value={form.statut} onChange={(e) => setForm({ ...form, statut: e.target.value })}
            className="w-full border rounded px-2 py-1.5 text-sm">
            <option value="demande">Demandé</option>
            <option value="approuve">Approuvé</option>
            <option value="refuse">Refusé</option>
            <option value="clos">Clos</option>
          </select>
        </label>
        <div className="col-span-3">
          <button disabled={saving} className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
            {saving ? 'Enregistrement…' : 'Créer la demande'}
          </button>
        </div>
      </form>
      {msg && <p className="text-sm text-blue-700">{msg}</p>}

      <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs text-gray-500">
            <tr>
              <th className="px-4 py-3">Référence</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Lieu</th>
              <th className="px-4 py-3">Demandeur</th>
              <th className="px-4 py-3">Début</th>
              <th className="px-4 py-3">Statut</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id} className="border-t">
                <td className="px-4 py-2 font-medium">{p.reference}</td>
                <td className="px-4 py-2">{p.type ?? '—'}</td>
                <td className="px-4 py-2">{p.lieu ?? '—'}</td>
                <td className="px-4 py-2">{p.demandeur ?? '—'}</td>
                <td className="px-4 py-2">{p.debut ? new Date(p.debut).toLocaleString('fr-FR') : '—'}</td>
                <td className="px-4 py-2">
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    p.statut === 'approuve' ? 'bg-green-100 text-green-700'
                    : p.statut === 'refuse' ? 'bg-red-100 text-red-700'
                    : 'bg-amber-100 text-amber-700'}`}>
                    {p.statut ?? '—'}
                  </span>
                </td>
              </tr>
            ))}
            {!loading && rows.length === 0 && (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">Aucune demande</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
