'use client';

import React, { useEffect, useState } from 'react';
import { apiClient } from './api-client';
import { RefreshCw } from 'lucide-react';
import Link from 'next/link';

export interface DeepField {
  name: string;
  label: string;
  type?: 'text' | 'number' | 'date' | 'bool';
  required?: boolean;
}

export interface DeepResourceConfig {
  label: string;
  listUrl: string;
  createUrl: string;
  fields: DeepField[];
}

type Row = Record<string, unknown>;

const fmt = (v: unknown) => {
  if (v === null || v === undefined || v === '') return '—';
  if (typeof v === 'boolean') return v ? 'Oui' : 'Non';
  const n = Number(v);
  if (typeof v === 'number' || (typeof v === 'string' && v !== '' && !isNaN(Number(v)) && /[0-9]/.test(v) && v.length > 3)) {
    return Number.isFinite(n) ? n.toLocaleString('fr-FR') : String(v);
  }
  return String(v);
};

const COLUMNS = (r: Row) =>
  Object.keys(r).filter((k) => !['company_id', 'is_active', 'created_at', 'updated_at', 'tenant_id'].includes(k)).slice(0, 6);

function ResourcePanel({ cfg }: { cfg: DeepResourceConfig }) {
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);
  const [vals, setVals] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [cols, setCols] = useState<string[]>([]);

  const load = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(cfg.listUrl);
      const d = res.data ?? res;
      const list: Row[] = Array.isArray(d) ? d : ((d as { items?: Row[] }).items ?? []);
      setRows(list);
      if (list.length) setCols(COLUMNS(list[0]));
      else setCols([]);
    } catch { setRows([]); setCols([]); }
    setLoading(false);
  };
  useEffect(() => { load(); }, [cfg.listUrl]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true); setMsg(null);
    const body: Row = {};
    cfg.fields.forEach((f) => {
      const v = vals[f.name];
      if (v === undefined || v === '') return;
      if (f.type === 'number') body[f.name] = Number(v);
      else if (f.type === 'bool') body[f.name] = v === 'true';
      else body[f.name] = v;
    });
    try {
      await apiClient.post(cfg.createUrl, body);
      setMsg('Enregistré.');
      setVals({});
      load();
    } catch (err: unknown) {
      const ax = err as { response?: { data?: { detail?: unknown } } };
      const d = ax?.response?.data?.detail;
      setMsg(typeof d === 'string' ? d : err instanceof Error ? err.message : 'Erreur');
    } finally { setSaving(false); }
  };

  return (
    <div className="space-y-4">
      <form onSubmit={submit} className="bg-white border rounded-xl p-4 shadow-sm">
        <div className="grid grid-cols-4 gap-3 items-end">
          {cfg.fields.map((f) => (
            <label key={f.name} className="text-sm">
              <span className="block text-xs text-gray-500 mb-1">{f.label}{f.required ? ' *' : ''}</span>
              {f.type === 'bool' ? (
                <select value={vals[f.name] ?? ''} onChange={(e) => setVals({ ...vals, [f.name]: e.target.value })}
                  className="w-full border rounded px-2 py-1.5 text-sm">
                  <option value="">—</option><option value="true">Oui</option><option value="false">Non</option>
                </select>
              ) : (
                <input type={f.type ?? 'text'} required={f.required}
                  value={vals[f.name] ?? ''}
                  onChange={(e) => setVals({ ...vals, [f.name]: e.target.value })}
                  className="w-full border rounded px-2 py-1.5 text-sm" />
              )}
            </label>
          ))}
          <button disabled={saving} className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
            {saving ? '…' : 'Créer'}
          </button>
        </div>
        {msg && <p className="text-sm text-blue-700 mt-2">{msg}</p>}
      </form>

      <div className="bg-white border rounded-xl shadow-sm overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs text-gray-500">
            <tr>{(cols.length ? cols : cfg.fields.slice(0, 6).map((f) => f.name)).map((c) => (
              <th key={c} className="px-4 py-3">{c.replace(/_/g, ' ')}</th>
            ))}</tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={Number(r.id ?? i)} className="border-t">
                {(cols.length ? cols : cfg.fields.slice(0, 6).map((f) => f.name)).map((c) => (
                  <td key={c} className="px-4 py-2 max-w-48 truncate">{fmt(r[c])}</td>
                ))}
              </tr>
            ))}
            {!loading && rows.length === 0 && (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">Aucune donnée</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function DeepDomainPage({ titre, description, backHref, backLabel, resources }: {
  titre: string;
  description: string;
  backHref: string;
  backLabel: string;
  resources: DeepResourceConfig[];
}) {
  const [tab, setTab] = useState(resources[0]?.label ?? '');
  const [nonce, setNonce] = useState(0);
  const current = resources.find((r) => r.label === tab) ?? resources[0];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href={backHref} className="text-sm text-gray-400 hover:text-gray-600">← {backLabel}</Link>
          <h1 className="text-2xl font-bold mt-1">{titre}</h1>
          <p className="text-sm text-gray-500">{description} ({resources.length} registres)</p>
        </div>
        <button onClick={() => setNonce((n) => n + 1)}
          className="flex items-center gap-2 px-3 py-2 text-sm border rounded-lg hover:bg-gray-50">
          <RefreshCw className="w-4 h-4" /> Actualiser
        </button>
      </div>

      <div className="flex flex-wrap gap-2 border-b pb-2">
        {resources.map((r) => (
          <button key={r.label} onClick={() => setTab(r.label)}
            className={`px-3 py-1.5 text-xs rounded-lg ${tab === r.label ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {r.label}
          </button>
        ))}
      </div>

      {current && <ResourcePanel key={`${current.label}-${nonce}`} cfg={current} />}
    </div>
  );
}
