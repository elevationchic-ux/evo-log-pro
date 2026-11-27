'use client';

import React, { useEffect, useState } from 'react';
import { deepAPI } from '@/lib/api-client';
import { RefreshCw } from 'lucide-react';
import Link from 'next/link';

type Data = Record<string, unknown>;
type Row = Record<string, unknown>;
const isNote = (d: Data) => typeof d?.note === 'string';

function Panel({ titre, children }: { titre: string; children: React.ReactNode }) {
  return (
    <div className="bg-white border rounded-xl p-5 shadow-sm">
      <h3 className="font-semibold mb-3">{titre}</h3>
      {children}
    </div>
  );
}

function Json({ data, loading }: { data: Data | null; loading: boolean }) {
  if (loading) return <p className="text-sm text-gray-400">Chargement…</p>;
  if (!data) return <p className="text-sm text-gray-400">Indisponible</p>;
  if (isNote(data)) return <p className="text-sm text-amber-700">{String(data.note)}</p>;
  return <pre className="text-xs bg-gray-50 border rounded p-3 overflow-auto max-h-80">{JSON.stringify(data, null, 2)}</pre>;
}

function useFetch(fn: () => Promise<{ data: Data }>) {
  const [data, setData] = useState<Data | null>(null);
  const [loading, setLoading] = useState(true);
  const load = async () => {
    setLoading(true);
    try { setData((await fn()).data); } catch { setData(null); }
    setLoading(false);
  };
  useEffect(() => { load(); }, []);
  return { data, loading, reload: load };
}

function useSubmit() {
  const [result, setResult] = useState<Data | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const run = async (fn: () => Promise<{ data: Data }>) => {
    setLoading(true); setError(null); setResult(null);
    try { setResult((await fn()).data); }
    catch (e: unknown) {
      const ax = e as { response?: { data?: { detail?: unknown } } };
      const d = ax?.response?.data?.detail;
      setError(typeof d === 'string' ? d : e instanceof Error ? e.message : 'Erreur');
    } finally { setLoading(false); }
  };
  return { result, loading, error, run };
}

export default function OutilsPage() {
  const [tab, setTab] = useState<'confidentialite' | 'facturation' | 'clés' | 'bourse' | 'jumeau' | 'eco'>('confidentialite');

  // Confidentialité
  const policy = useFetch(() => deepAPI.getPrivacyPolicy());
  const registry = useFetch(() => deepAPI.getPrivacyRegistry());
  const exportData = useFetch(() => deepAPI.exportMyData());
  const breach = useSubmit();
  const [breachForm, setBreachForm] = useState({ incident_type: '', description: '', affected_count: '0' });

  // Facturation électronique
  const sign = useSubmit();
  const [einvoice, setEinvoice] = useState({ invoice_number: '', client_niu: '', total_ht: '', total_tva: '', total_ttc: '' });
  const [verifyHash, setVerifyHash] = useState('');
  const verify = useSubmit();

  // Clés API
  const apiKeys = useFetch(() => deepAPI.getApiKeys());
  const createKey = useSubmit();
  const [keyForm, setKeyForm] = useState({ key_name: '' });
  const [newKey, setNewKey] = useState<string | null>(null);

  // Bourse de fret
  const offers = useFetch(() => deepAPI.getFreightOffers());
  const publish = useSubmit();
  const [offerForm, setOfferForm] = useState({ origin: '', destination: '', cargo_type: '', weight_tons: '', offered_price_xaf: '' });

  // Jumeau + éco-conduite
  const yard = useFetch(() => deepAPI.getYardState());
  const scores = useFetch(() => deepAPI.getDriverScores());

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Outils & conformité</h1>
        <p className="text-sm text-gray-500">RGPD, facturation électronique, clés API, bourse de fret CEMAC, jumeau numérique, éco-conduite.</p>
      </div>

      <div className="flex flex-wrap gap-2 border-b pb-2">
        {([
          ['confidentialite', 'Confidentialité RGPD'],
          ['facturation', 'Facturation électronique'],
          ['clés', 'Clés API'],
          ['bourse', 'Bourse de fret'],
          ['jumeau', 'Jumeau & éco-conduite'],
        ] as const).map(([k, l]) => (
          <button key={k} onClick={() => setTab(k)}
            className={`px-4 py-2 text-sm rounded-t-lg ${tab === k ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {l}
          </button>
        ))}
      </div>

      {tab === 'confidentialite' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Panel titre="Politique de confidentialité"><Json data={policy.data} loading={policy.loading} /></Panel>
          <Panel titre="Registre des traitements"><Json data={registry.data} loading={registry.loading} /></Panel>
          <Panel titre="Export de mes données (portabilité)">
            <Json data={exportData.data} loading={exportData.loading} />
            <button onClick={exportData.reload} className="mt-2 text-xs text-blue-600 hover:underline">Recharger</button>
          </Panel>
          <Panel titre="Déclarer une violation">
            <form className="space-y-2" onSubmit={(e) => {
              e.preventDefault();
              breach.run(() => deepAPI.notifyBreach({
                incident_type: breachForm.incident_type,
                description: breachForm.description,
                affected_count: Number(breachForm.affected_count) || 0,
              }));
            }}>
              <input required placeholder="Type d'incident (ex: UNAUTHORIZED_ACCESS)" value={breachForm.incident_type}
                onChange={(e) => setBreachForm({ ...breachForm, incident_type: e.target.value })}
                className="w-full border rounded px-2 py-1.5 text-sm" />
              <input required placeholder="Description" value={breachForm.description}
                onChange={(e) => setBreachForm({ ...breachForm, description: e.target.value })}
                className="w-full border rounded px-2 py-1.5 text-sm" />
              <input type="number" placeholder="Personnes affectées" value={breachForm.affected_count}
                onChange={(e) => setBreachForm({ ...breachForm, affected_count: e.target.value })}
                className="w-full border rounded px-2 py-1.5 text-sm" />
              <button disabled={breach.loading} className="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 disabled:opacity-50">
                {breach.loading ? '…' : 'Enregistrer l’incident'}
              </button>
            </form>
            {breach.error && <p className="text-sm text-red-600 mt-2">{breach.error}</p>}
            {breach.result && <pre className="text-xs bg-gray-50 border rounded p-3 mt-2 overflow-auto max-h-40">{JSON.stringify(breach.result, null, 2)}</pre>}
          </Panel>
        </div>
      )}

      {tab === 'facturation' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Panel titre="Sceau de facture (SHA-256)">
            <form className="space-y-2" onSubmit={(e) => {
              e.preventDefault();
              sign.run(() => deepAPI.signEinvoice({
                invoice_number: einvoice.invoice_number,
                client_niu: einvoice.client_niu,
                total_ht: Number(einvoice.total_ht),
                total_tva: Number(einvoice.total_tva),
                total_ttc: Number(einvoice.total_ttc),
              }));
            }}>
              <input required placeholder="N° facture" value={einvoice.invoice_number}
                onChange={(e) => setEinvoice({ ...einvoice, invoice_number: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" />
              <input required placeholder="NIU client" value={einvoice.client_niu}
                onChange={(e) => setEinvoice({ ...einvoice, client_niu: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" />
              <div className="grid grid-cols-3 gap-2">
                <input required type="number" placeholder="HT" value={einvoice.total_ht}
                  onChange={(e) => setEinvoice({ ...einvoice, total_ht: e.target.value })} className="border rounded px-2 py-1.5 text-sm" />
                <input required type="number" placeholder="TVA" value={einvoice.total_tva}
                  onChange={(e) => setEinvoice({ ...einvoice, total_tva: e.target.value })} className="border rounded px-2 py-1.5 text-sm" />
                <input required type="number" placeholder="TTC" value={einvoice.total_ttc}
                  onChange={(e) => setEinvoice({ ...einvoice, total_ttc: e.target.value })} className="border rounded px-2 py-1.5 text-sm" />
              </div>
              <button disabled={sign.loading} className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
                {sign.loading ? '…' : 'Signer'}
              </button>
            </form>
            {sign.error && <p className="text-sm text-red-600 mt-2">{sign.error}</p>}
            {sign.result && <pre className="text-xs bg-gray-50 border rounded p-3 mt-2 overflow-auto max-h-40">{JSON.stringify(sign.result, null, 2)}</pre>}
          </Panel>
          <Panel titre="Vérifier une empreinte">
            <form className="flex gap-2" onSubmit={(e) => {
              e.preventDefault();
              verify.run(() => deepAPI.verifyEinvoice(verifyHash));
            }}>
              <input required placeholder="Hash fiscal (SHA-256)" value={verifyHash}
                onChange={(e) => setVerifyHash(e.target.value)} className="flex-1 border rounded px-2 py-1.5 text-sm font-mono" />
              <button disabled={verify.loading} className="px-4 py-2 bg-gray-700 text-white text-sm rounded-lg hover:bg-gray-800 disabled:opacity-50">Vérifier</button>
            </form>
            {verify.error && <p className="text-sm text-red-600 mt-2">{verify.error}</p>}
            {verify.result && <pre className="text-xs bg-gray-50 border rounded p-3 mt-2 overflow-auto max-h-40">{JSON.stringify(verify.result, null, 2)}</pre>}
          </Panel>
        </div>
      )}

      {tab === 'clés' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Panel titre="Créer une clé API">
            <form className="space-y-2" onSubmit={async (e) => {
              e.preventDefault();
              await createKey.run(() => deepAPI.createApiKey({ key_name: keyForm.key_name }));
              if (createKey.result) {
                const d = createKey.result as Data;
                setNewKey(String(d.clé_complete ?? d.key ?? d.raw_key ?? ''));
                apiKeys.reload();
              }
            }}>
              <input required placeholder="Nom de la clé (ex: Intégration Odoo)" value={keyForm.key_name}
                onChange={(e) => setKeyForm({ ...keyForm, key_name: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" />
              <button disabled={createKey.loading} className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
                {createKey.loading ? '…' : 'Générer'}
              </button>
            </form>
            {createKey.error && <p className="text-sm text-red-600 mt-2">{createKey.error}</p>}
            {newKey && (
              <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded text-xs">
                <p className="font-semibold text-amber-800">Clé complète (affichée une seule fois) :</p>
                <code className="break-all">{newKey}</code>
              </div>
            )}
          </Panel>
          <Panel titre="Clés existantes (préfixe + état)">
            {apiKeys.loading ? <p className="text-sm text-gray-400">Chargement…</p> : (
              <table className="w-full text-sm">
                <thead className="text-left text-xs text-gray-500"><tr><th className="py-1">Nom</th><th>Préfixe</th><th>Statut</th></tr></thead>
                <tbody>
                  {((apiKeys.data as unknown as Row[] | { items?: Row[] }) ?? []) && (() => {
                    const d = apiKeys.data as unknown as Row[] | { items?: Row[] } | null;
                    const list = Array.isArray(d) ? d : ((d as { items?: Row[] })?.items ?? []);
                    return list.map((k, i) => (
                      <tr key={i} className="border-t">
                        <td className="py-1.5">{String(k.key_name ?? '—')}</td>
                        <td className="font-mono text-xs">{String(k.key_prefix ?? '—')}…</td>
                        <td>{String(k.active ?? k.statut ?? '—')}</td>
                      </tr>
                    ));
                  })()}
                </tbody>
              </table>
            )}
          </Panel>
        </div>
      )}

      {tab === 'bourse' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Panel titre="Publier une offre de fret">
            <form className="space-y-2" onSubmit={(e) => {
              e.preventDefault();
              publish.run(() => deepAPI.publishFreightOffer({
                origin: offerForm.origin,
                destination: offerForm.destination,
                cargo_type: offerForm.cargo_type || undefined,
                weight_tons: Number(offerForm.weight_tons),
                offered_price_xaf: Number(offerForm.offered_price_xaf),
              }));
            }}>
              <div className="grid grid-cols-2 gap-2">
                <input required placeholder="Origine" value={offerForm.origin}
                  onChange={(e) => setOfferForm({ ...offerForm, origin: e.target.value })} className="border rounded px-2 py-1.5 text-sm" />
                <input required placeholder="Destination" value={offerForm.destination}
                  onChange={(e) => setOfferForm({ ...offerForm, destination: e.target.value })} className="border rounded px-2 py-1.5 text-sm" />
              </div>
              <input placeholder="Type de cargaison" value={offerForm.cargo_type}
                onChange={(e) => setOfferForm({ ...offerForm, cargo_type: e.target.value })} className="w-full border rounded px-2 py-1.5 text-sm" />
              <div className="grid grid-cols-2 gap-2">
                <input required type="number" step="0.1" placeholder="Poids (t)" value={offerForm.weight_tons}
                  onChange={(e) => setOfferForm({ ...offerForm, weight_tons: e.target.value })} className="border rounded px-2 py-1.5 text-sm" />
                <input required type="number" placeholder="Prix offert XAF" value={offerForm.offered_price_xaf}
                  onChange={(e) => setOfferForm({ ...offerForm, offered_price_xaf: e.target.value })} className="border rounded px-2 py-1.5 text-sm" />
              </div>
              <button disabled={publish.loading} className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
                {publish.loading ? '…' : 'Publier'}
              </button>
            </form>
            {publish.error && <p className="text-sm text-red-600 mt-2">{publish.error}</p>}
            {publish.result && <p className="text-xs text-green-600 mt-1">Offre publiée — liste rechargée.</p>}
          </Panel>
          <Panel titre="Offres publiées (tous tenants)">
            <Json data={offers.data} loading={offers.loading} />
            <button onClick={offers.reload} className="mt-2 text-xs text-blue-600 hover:underline">Actualiser</button>
          </Panel>
        </div>
      )}

      {tab === 'jumeau' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Panel titre="État du parc (jumeau numérique)"><Json data={yard.data} loading={yard.loading} /></Panel>
          <Panel titre="Scores éco-conduite chauffeurs"><Json data={scores.data} loading={scores.loading} /></Panel>
        </div>
      )}
    </div>
  );
}
