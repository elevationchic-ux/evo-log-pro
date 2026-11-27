'use client';

import React, { useEffect, useState } from 'react';
import { deepAPI } from '@/lib/api-client';
import { RefreshCw } from 'lucide-react';
import Link from 'next/link';

type Sensor = {
  id: number;
  immatriculation_camion: string;
  niveau_actuel_litres: number;
  capacite_totale_litres?: number | null;
  alerte_vol_detectee?: boolean;
  derniere_station?: string | null;
  updated_at?: string | null;
};

const pct = (s: Sensor) =>
  s.capacite_totale_litres ? Math.round((s.niveau_actuel_litres / s.capacite_totale_litres) * 100) : null;

export default function FuelSensorsPage() {
  const [rows, setRows] = useState<Sensor[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ immatriculation_camion: '', niveau_actuel_litres: '', derniere_station: '' });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const res = await deepAPI.getFuelSensors();
      const data = (res.data ?? res) as Sensor[] | { items?: Sensor[] };
      setRows(Array.isArray(data) ? data : (data.items ?? []));
    } catch { setRows([]); }
    setLoading(false);
  };
  useEffect(() => { load(); }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true); setMsg(null);
    try {
      await deepAPI.createFuelSensor({
        immatriculation_camion: form.immatriculation_camion,
        niveau_actuel_litres: Number(form.niveau_actuel_litres),
        derniere_station: form.derniere_station || undefined,
      });
      setMsg('Lecture enregistrée — variation calculée vs dernière lecture.');
      setForm({ immatriculation_camion: '', niveau_actuel_litres: '', derniere_station: '' });
      load();
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : 'Erreur');
    } finally { setSaving(false); }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/fuel-guard" className="text-sm text-gray-400 hover:text-gray-600">← FuelGuard</Link>
          <h1 className="text-2xl font-bold mt-1">Capteurs cuves carburant</h1>
          <p className="text-sm text-gray-500">Lectures manuelles — aucune alerte de vol automatique (baisse ≠ vol certain).</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 px-3 py-2 text-sm border rounded-lg hover:bg-gray-50">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Actualiser
        </button>
      </div>

      <form onSubmit={submit} className="bg-white border rounded-xl p-5 shadow-sm grid grid-cols-4 gap-3 items-end">
        <label className="text-sm">
          <span className="block text-xs text-gray-500 mb-1">Immatriculation</span>
          <input required value={form.immatriculation_camion}
            onChange={(e) => setForm({ ...form, immatriculation_camion: e.target.value })}
            className="w-full border rounded px-2 py-1.5 text-sm" placeholder="LT-0000-A" />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-gray-500 mb-1">Niveau (litres)</span>
          <input required type="number" step="0.01" value={form.niveau_actuel_litres}
            onChange={(e) => setForm({ ...form, niveau_actuel_litres: e.target.value })}
            className="w-full border rounded px-2 py-1.5 text-sm" />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-gray-500 mb-1">Dernière station</span>
          <input value={form.derniere_station}
            onChange={(e) => setForm({ ...form, derniere_station: e.target.value })}
            className="w-full border rounded px-2 py-1.5 text-sm" />
        </label>
        <button disabled={saving} className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {saving ? 'Enregistrement…' : 'Enregistrer'}
        </button>
      </form>
      {msg && <p className="text-sm text-blue-700">{msg}</p>}

      <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs text-gray-500">
            <tr>
              <th className="px-4 py-3">Camion</th>
              <th className="px-4 py-3">Niveau</th>
              <th className="px-4 py-3">% cuve</th>
              <th className="px-4 py-3">Station</th>
              <th className="px-4 py-3">MAJ</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => {
              const p = pct(s);
              return (
                <tr key={s.id} className="border-t">
                  <td className="px-4 py-2 font-medium">{s.immatriculation_camion}</td>
                  <td className="px-4 py-2">{s.niveau_actuel_litres} L</td>
                  <td className="px-4 py-2">
                    {p !== null ? (
                      <span className={p < 20 ? 'text-red-600 font-semibold' : p < 40 ? 'text-amber-600' : 'text-green-700'}>
                        {p} %
                      </span>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-2">{s.derniere_station ?? '—'}</td>
                  <td className="px-4 py-2 text-gray-500">{s.updated_at ? new Date(s.updated_at).toLocaleString('fr-FR') : '—'}</td>
                </tr>
              );
            })}
            {!loading && rows.length === 0 && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">Aucune lecture enregistrée</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
