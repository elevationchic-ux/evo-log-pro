'use client';

import React, { useEffect, useState } from 'react';
import { apiClient } from './api-client';
import { RefreshCw, Pencil, Trash2, X } from 'lucide-react';
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

// Lookups verifies : endpoints de liste existants. En cas d'echec reseau ou
// de shape inattendue, le champ reste une saisie libre (datalist vide) —
// jamais de blocage, jamais de donnee inventee.
const FIELD_LOOKUPS: Record<string, string> = {
  employe_id: '/api/rh/employes',
  utilisateur_id: '/api/v1/admin/users',
  user_id: '/api/v1/admin/users',
  client_id: '/api/v1/tiers/clients/',
  fournisseur_id: '/api/v1/tiers/fournisseurs/',
  tiers_id: '/api/v1/tiers/',
};

const LABEL_KEYS = ['nom', 'name', 'full_name', 'username', 'email', 'intitule', 'reference', 'code', 'raison_sociale'];

function useLookup(url?: string) {
  const [options, setOptions] = useState<{ id: number | string; label: string }[]>([]);
  useEffect(() => {
    if (!url) { setOptions([]); return; }
    let alive = true;
    apiClient.get(url).then((res) => {
      if (!alive) return;
      const d = res.data ?? res;
      const list: Row[] = Array.isArray(d) ? d : ((d as { items?: Row[] }).items ?? []);
      setOptions(list.slice(0, 500).map((r) => {
        const label = LABEL_KEYS.map((k) => r[k]).find((v) => v !== null && v !== undefined && v !== '') ?? `#${r.id}`;
        return { id: r.id as number | string, label: `${label} (#${r.id})` };
      }));
    }).catch(() => { if (alive) setOptions([]); });
    return () => { alive = false; };
  }, [url]);
  return options;
}

type Row = Record<string, unknown>;

const SKIP_COLS = ['company_id', 'is_active', 'created_at', 'updated_at', 'tenant_id'];

const fmt = (v: unknown) => {
  if (v === null || v === undefined || v === '') return '—';
  if (typeof v === 'boolean') return v ? 'Oui' : 'Non';
  if (typeof v === 'object') return JSON.stringify(v).slice(0, 60);
  const s = String(v);
  const n = Number(s);
  if (s.length > 3 && !isNaN(n) && /^-?[\d.,\s]+$/.test(s)) return n.toLocaleString('fr-FR');
  return s.length > 60 ? s.slice(0, 57) + '…' : s;
};

const COLUMNS = (r: Row) => Object.keys(r).filter((k) => !SKIP_COLS.includes(k)).slice(0, 6);

function errMsg(err: unknown): string {
  const ax = err as { response?: { data?: { detail?: unknown } } };
  const d = ax?.response?.data?.detail;
  if (typeof d === 'string') return d;
  if (Array.isArray(d)) return d.map((x) => (x as { msg?: string }).msg ?? JSON.stringify(x)).join(' ; ');
  return err instanceof Error ? err.message : 'Erreur';
}

function LookupInput({ name, lookupUrl, value, onChange, required, type }: {
  name: string; lookupUrl?: string; value: string; onChange: (v: string) => void;
  required?: boolean; type?: string;
}) {
  const options = useLookup(lookupUrl);
  const listId = `dl-${name}`;
  return (
    <>
      <input type={type ?? 'text'} required={required} list={options.length ? listId : undefined}
        value={value} onChange={(e) => onChange(e.target.value)}
        className="w-full border rounded px-2 py-1.5 text-sm" />
      {options.length > 0 && (
        <datalist id={listId}>
          {options.map((o) => <option key={o.id} value={o.id}>{o.label}</option>)}
        </datalist>
      )}
    </>
  );
}

function ResourcePanel({ cfg }: { cfg: DeepResourceConfig }) {
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);
  const [vals, setVals] = useState<Record<string, string>>({});
  const [editing, setEditing] = useState<Row | null>(null);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [cols, setCols] = useState<string[]>([]);
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 100;

  const load = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(cfg.listUrl);
      const d = res.data ?? res;
      const list: Row[] = Array.isArray(d) ? d : ((d as { items?: Row[] }).items ?? []);
      setRows(list);
      setCols(list.length ? COLUMNS(list[0]) : []);
      setPage(0);
    } catch { setRows([]); setCols([]); }
    setLoading(false);
  };
  useEffect(() => { load(); setEditing(null); setVals({}); }, [cfg.listUrl]);

  const buildBody = (): Row => {
    const body: Row = {};
    cfg.fields.forEach((f) => {
      const v = vals[f.name];
      if (v === undefined || v === '') return;
      if (f.type === 'number') body[f.name] = Number(v);
      else if (f.type === 'bool') body[f.name] = v === 'true';
      else body[f.name] = v;
    });
    return body;
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true); setMsg(null);
    const body = buildBody();
    try {
      if (editing && editing.id !== undefined) {
        await apiClient.put(`${cfg.listUrl}/${editing.id}`, body);
        setMsg('Modifié.');
      } else {
        await apiClient.post(cfg.createUrl, body);
        setMsg('Enregistré.');
      }
      setVals({}); setEditing(null);
      load();
    } catch (err: unknown) {
      setMsg(errMsg(err));
    } finally { setSaving(false); }
  };

  const startEdit = (r: Row) => {
    setEditing(r);
    const next: Record<string, string> = {};
    cfg.fields.forEach((f) => {
      const v = r[f.name];
      if (v === null || v === undefined) { next[f.name] = ''; return; }
      if (f.type === 'bool') next[f.name] = v ? 'true' : 'false';
      else if (f.type === 'date' && typeof v === 'string') next[f.name] = v.slice(0, 10);
      else next[f.name] = String(v);
    });
    setVals(next);
    setMsg(null);
  };

  const remove = async (r: Row) => {
    if (r.id === undefined) return;
    if (!window.confirm(`Supprimer l'enregistrement #${r.id} ?`)) return;
    try {
      await apiClient.delete(`${cfg.listUrl}/${r.id}`);
      setMsg('Supprimé.');
      load();
    } catch (err: unknown) { setMsg(errMsg(err)); }
  };

  const displayCols = cols.length ? cols : cfg.fields.slice(0, 6).map((f) => f.name);

  return (
    <div className="space-y-4">
      <form onSubmit={submit} className="bg-white border rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-semibold">{editing ? `Modifier #${editing.id}` : 'Nouvel enregistrement'}</p>
          {editing && (
            <button type="button" onClick={() => { setEditing(null); setVals({}); }}
              className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700">
              <X className="w-3.5 h-3.5" /> Annuler
            </button>
          )}
        </div>
        <div className="grid grid-cols-4 gap-3 items-end">
          {cfg.fields.map((f) => (
            <label key={f.name} className="text-sm">
              <span className="block text-xs text-gray-500 mb-1">{f.label}{f.required && !editing ? ' *' : ''}</span>
              {f.type === 'bool' ? (
                <select value={vals[f.name] ?? ''} onChange={(e) => setVals({ ...vals, [f.name]: e.target.value })}
                  className="w-full border rounded px-2 py-1.5 text-sm">
                  <option value="">—</option><option value="true">Oui</option><option value="false">Non</option>
                </select>
              ) : (
                <LookupInput name={f.name} lookupUrl={FIELD_LOOKUPS[f.name]}
                  type={f.type ?? 'text'} required={f.required && !editing}
                  value={vals[f.name] ?? ''}
                  onChange={(v) => setVals({ ...vals, [f.name]: v })} />
              )}
            </label>
          ))}
          <button disabled={saving}
            className={`px-4 py-2 text-white text-sm rounded-lg disabled:opacity-50 ${editing ? 'bg-amber-600 hover:bg-amber-700' : 'bg-blue-600 hover:bg-blue-700'}`}>
            {saving ? '…' : editing ? 'Enregistrer' : 'Créer'}
          </button>
        </div>
        {msg && <p className="text-sm text-blue-700 mt-2">{msg}</p>}
      </form>

      <div className="bg-white border rounded-xl shadow-sm overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs text-gray-500">
            <tr>
              {displayCols.map((c) => <th key={c} className="px-4 py-3">{c.replace(/_/g, ' ')}</th>)}
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE).map((r, i) => (
              <tr key={Number(r.id ?? i)} className="border-t">
                {displayCols.map((c) => <td key={c} className="px-4 py-2 max-w-48 truncate">{fmt(r[c])}</td>)}
                <td className="px-4 py-2">
                  <div className="flex justify-end gap-1">
                    <button onClick={() => startEdit(r)} title="Modifier"
                      className="p-1.5 rounded hover:bg-amber-50 text-amber-600"><Pencil className="w-4 h-4" /></button>
                    <button onClick={() => remove(r)} title="Supprimer"
                      className="p-1.5 rounded hover:bg-red-50 text-red-600"><Trash2 className="w-4 h-4" /></button>
                  </div>
                </td>
              </tr>
            ))}
            {!loading && rows.length === 0 && (
              <tr><td colSpan={displayCols.length + 1} className="px-4 py-8 text-center text-gray-400">Aucune donnée</td></tr>
            )}
          </tbody>
        </table>
        {rows.length > PAGE_SIZE && (
          <div className="flex items-center justify-between px-4 py-3 border-t text-xs text-gray-500">
            <span>{rows.length.toLocaleString('fr-FR')} enregistrements — page {page + 1}/{Math.ceil(rows.length / PAGE_SIZE)}</span>
            <div className="flex gap-2">
              <button disabled={page === 0} onClick={() => setPage(page - 1)}
                className="px-3 py-1 border rounded disabled:opacity-40 hover:bg-gray-50">Préc.</button>
              <button disabled={(page + 1) * PAGE_SIZE >= rows.length} onClick={() => setPage(page + 1)}
                className="px-3 py-1 border rounded disabled:opacity-40 hover:bg-gray-50">Suiv.</button>
            </div>
          </div>
        )}
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
