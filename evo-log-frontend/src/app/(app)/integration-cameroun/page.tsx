'use client';

import { useCallback, useEffect, useState } from 'react';
import { toast } from 'sonner';
import { integrationCamerounApi } from '@/lib/api-cameroun';
import { useSettings } from '@/components/layout/SettingsProvider';

type Lang = 'fr' | 'en';

const TABS = [
  { key: 'bsc', fr: 'BSC', en: 'BSC' },
  { key: 'csc', fr: 'CSC', en: 'CSC' },
  { key: 'syged', fr: 'SYGED / DUM', en: 'SYGED / DUM' },
  { key: 'ape', fr: 'APE', en: 'APE' },
] as const;

type TabKey = (typeof TABS)[number]['key'];

const inputCls = 'w-full rounded-md border border-slate-600 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500';
const labelCls = 'mb-1 block text-sm font-medium text-slate-200';

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className={labelCls}>{label}</label>
      {children}
    </div>
  );
}

function EmptyRow({ colSpan, text }: { colSpan: number; text: string }) {
  return (
    <tr>
      <td colSpan={colSpan} className="px-4 py-6 text-center text-sm text-slate-400">
        {text}
      </td>
    </tr>
  );
}

export default function IntegrationCamerounPage() {
  const { language } = useSettings();
  const lang: Lang = language === 'en' ? 'en' : 'fr';

  const [activeTab, setActiveTab] = useState<TabKey>('bsc');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [bscList, setBscList] = useState<any[]>([]);
  const [cscList, setCscList] = useState<any[]>([]);
  const [dumList, setDumList] = useState<any[]>([]);
  const [apeList, setApeList] = useState<any[]>([]);

  const [bscForm, setBscForm] = useState<any>({});
  const [cscForm, setCscForm] = useState<any>({});
  const [dumForm, setDumForm] = useState<any>({});
  const [apeForm, setApeForm] = useState<any>({});

  // Chargement honnête des listes réelles depuis le backend.
  const loadAll = useCallback(async () => {
    try {
      const [bsc, csc, dum, ape] = await Promise.all([
        integrationCamerounApi.listerBSC({ limit: 100 }),
        integrationCamerounApi.listerCSC({ limit: 100 }),
        integrationCamerounApi.listerDUM({ limit: 100 }),
        integrationCamerounApi.listerAPE({ limit: 100 }),
      ]);
      setBscList(bsc?.data ?? []);
      setCscList(csc?.data ?? []);
      setDumList(dum?.data ?? []);
      setApeList(ape?.data ?? []);
    } catch (e: any) {
      setError(e?.response?.data?.detail || null);
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  useEffect(() => {
    const t = new URLSearchParams(window.location.search).get('tab');
    if (t && TABS.some((x) => x.key === t)) setActiveTab(t as TabKey);
  }, []);

  const submit = async (fn: () => Promise<any>, successMsg: string, refresh: () => Promise<void> | void) => {
    setLoading(true);
    setError(null);
    try {
      await fn();
      toast.success(successMsg);
      await refresh();
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Erreur');
      toast.error(e?.response?.data?.detail || 'Erreur');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBSC = (e: React.FormEvent) => {
    e.preventDefault();
    submit(() => integrationCamerounApi.creerBSC(bscForm), lang === 'en' ? 'BSC created and saved.' : 'BSC créé et enregistré.', async () => {
      setBscForm({});
      const res = await integrationCamerounApi.listerBSC({ limit: 100 });
      setBscList(res?.data ?? []);
    });
  };

  const handleCreateCSC = (e: React.FormEvent) => {
    e.preventDefault();
    submit(() => integrationCamerounApi.demanderCSC(cscForm), lang === 'en' ? 'CSC request saved.' : 'Demande CSC enregistrée.', async () => {
      setCscForm({});
      const res = await integrationCamerounApi.listerCSC({ limit: 100 });
      setCscList(res?.data ?? []);
    });
  };

  const handleCreateDUM = (e: React.FormEvent) => {
    e.preventDefault();
    submit(() => integrationCamerounApi.creerDUM(dumForm), lang === 'en' ? 'DUM created and saved.' : 'DUM créé et enregistré.', async () => {
      setDumForm({});
      const res = await integrationCamerounApi.listerDUM({ limit: 100 });
      setDumList(res?.data ?? []);
    });
  };

  const handleCreateAPE = (e: React.FormEvent) => {
    e.preventDefault();
    submit(() => integrationCamerounApi.creerAPE(apeForm), lang === 'en' ? 'APE created and saved.' : 'APE créé et enregistré.', async () => {
      setApeForm({});
      const res = await integrationCamerounApi.listerAPE({ limit: 100 });
      setApeList(res?.data ?? []);
    });
  };

  return (
    <div className="p-4 sm:p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-100">
          {lang === 'en' ? 'Cameroon / CEMAC Integration' : 'Intégration Cameroun / CEMAC'}
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          {lang === 'en'
            ? 'BSC, CSC, DUM (SYGED) and APE (BEAC)  records are stored in the backend.'
            : 'BSC, CSC, DUM (SYGED) et APE (BEAC)  les enregistrements sont stockés côté backend.'}
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-6 overflow-x-auto">
        <nav className="flex min-w-max space-x-4 border-b border-slate-700">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`whitespace-nowrap border-b-2 px-3 py-3 text-sm font-medium ${activeTab === t.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
            >
              {lang === 'en' ? t.en : t.fr}
            </button>
          ))}
        </nav>
      </div>

      {error && (
        <div className="mb-4 rounded-md border border-red-500/50 bg-red-500/10 px-4 py-2 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* BSC */}
      {activeTab === 'bsc' && (
        <div className="rounded-lg bg-slate-900 p-4 shadow sm:p-6">
          <h2 className="mb-4 text-xl font-semibold">BSC  {lang === 'en' ? 'Cargo Tracking Slip' : 'Bulletin de Soumission Connaissement'}</h2>
          <form onSubmit={handleCreateBSC} className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
            <Field label={lang === 'en' ? 'Bill of Lading No.' : 'Numéro de Connaissement'}>
              <input required className={inputCls} value={bscForm.numero_connaisse || ''} onChange={(e) => setBscForm({ ...bscForm, numero_connaisse: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Vessel' : 'Navire'}>
              <input required className={inputCls} value={bscForm.navire || ''} onChange={(e) => setBscForm({ ...bscForm, navire: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Loading Port' : 'Port de Chargement'}>
              <input required className={inputCls} value={bscForm.port_chargement || ''} onChange={(e) => setBscForm({ ...bscForm, port_chargement: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Discharge Port' : 'Port de Déchargement'}>
              <input required className={inputCls} value={bscForm.port_dechargement || ''} onChange={(e) => setBscForm({ ...bscForm, port_dechargement: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Agent (licensed forwarder)' : 'Agent (transitaire agréé)'}>
              <input required className={inputCls} value={bscForm.agent || ''} onChange={(e) => setBscForm({ ...bscForm, agent: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Importer' : 'Importateur'}>
              <input required className={inputCls} value={bscForm.importateur || ''} onChange={(e) => setBscForm({ ...bscForm, importateur: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Gross Weight (t)' : 'Poids Total (tonnes)'}>
              <input type="number" step="0.01" className={inputCls} value={bscForm.poids_total ?? ''} onChange={(e) => setBscForm({ ...bscForm, poids_total: e.target.value ? parseFloat(e.target.value) : undefined })} />
            </Field>
            <Field label={lang === 'en' ? 'FOB Value (USD)' : 'Valeur FOB (USD)'}>
              <input type="number" step="0.01" className={inputCls} value={bscForm.valeur_fob ?? ''} onChange={(e) => setBscForm({ ...bscForm, valeur_fob: e.target.value ? parseFloat(e.target.value) : undefined })} />
            </Field>
            <div className="md:col-span-2">
              <button type="submit" disabled={loading} className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                {loading ? '…' : (lang === 'en' ? 'Create BSC' : 'Créer BSC')}
              </button>
            </div>
          </form>

          <h3 className="mb-3 text-lg font-semibold">{lang === 'en' ? 'Registered BSC' : 'BSC enregistrés'}</h3>
          <div className="overflow-x-auto rounded-md border border-slate-700">
            <table className="min-w-full divide-y divide-slate-800">
              <thead className="bg-slate-800">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">BSC</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'BL No.' : 'Connaissement'}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Vessel' : 'Navire'}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Status' : 'Statut'}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Date' : 'Date'}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 bg-slate-900">
                {bscList.length === 0 ? (
                  <EmptyRow colSpan={5} text={lang === 'en' ? 'No BSC recorded yet.' : 'Aucun BSC enregistré.'} />
                ) : (
                  bscList.map((b, idx) => (
                    <tr key={b.id ?? idx}>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{b.numero_bsc}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{b.numero_connaisse}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{b.navire}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-green-600">{b.statut}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{b.date_emission}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* CSC */}
      {activeTab === 'csc' && (
        <div className="rounded-lg bg-slate-900 p-4 shadow sm:p-6">
          <h2 className="mb-4 text-xl font-semibold">CSC  {lang === 'en' ? 'Cargo Safety Certificate' : 'Certificat de Sécurité Cargaison'}</h2>
          <form onSubmit={handleCreateCSC} className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
            <Field label={lang === 'en' ? 'Bill of Lading No.' : 'Numéro de Connaissement'}>
              <input required className={inputCls} value={cscForm.numero_connaisse || ''} onChange={(e) => setCscForm({ ...cscForm, numero_connaisse: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Vessel' : 'Navire'}>
              <input required className={inputCls} value={cscForm.navire || ''} onChange={(e) => setCscForm({ ...cscForm, navire: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Origin Port' : 'Port d’Origine'}>
              <input required className={inputCls} value={cscForm.port_origine || ''} onChange={(e) => setCscForm({ ...cscForm, port_origine: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Destination Port' : 'Port de Destination'}>
              <input required className={inputCls} value={cscForm.port_destination || ''} onChange={(e) => setCscForm({ ...cscForm, port_destination: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Goods Type' : 'Type de Marchandise'}>
              <select className={inputCls} value={cscForm.type_marchandise || ''} onChange={(e) => setCscForm({ ...cscForm, type_marchandise: e.target.value })}>
                <option value=""></option>
                <option value="General">General</option>
                <option value="Dangereux">Dangereux</option>
                <option value="Refrigéré">Réfrigéré</option>
                <option value="Vrac">Vrac</option>
              </select>
            </Field>
            <Field label={lang === 'en' ? 'Gross Weight (t)' : 'Poids Brut (tonnes)'}>
              <input type="number" step="0.01" className={inputCls} value={cscForm.poids_brut_tonnes ?? ''} onChange={(e) => setCscForm({ ...cscForm, poids_brut_tonnes: e.target.value ? parseFloat(e.target.value) : undefined })} />
            </Field>
            <Field label={lang === 'en' ? 'Packages' : 'Nombre de Colis'}>
              <input type="number" className={inputCls} value={cscForm.nombre_colis ?? ''} onChange={(e) => setCscForm({ ...cscForm, nombre_colis: e.target.value ? parseInt(e.target.value) : undefined })} />
            </Field>
            <Field label={lang === 'en' ? 'FOB Value (USD)' : 'Valeur FOB (USD)'}>
              <input type="number" step="0.01" className={inputCls} value={cscForm.valeur_fob ?? ''} onChange={(e) => setCscForm({ ...cscForm, valeur_fob: e.target.value ? parseFloat(e.target.value) : undefined })} />
            </Field>
            <div className="md:col-span-2">
              <button type="submit" disabled={loading} className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                {loading ? '…' : (lang === 'en' ? 'Request CSC' : 'Demander CSC')}
              </button>
            </div>
          </form>

          <h3 className="mb-3 text-lg font-semibold">{lang === 'en' ? 'Registered CSC' : 'CSC enregistrés'}</h3>
          <div className="overflow-x-auto rounded-md border border-slate-700">
            <table className="min-w-full divide-y divide-slate-800">
              <thead className="bg-slate-800">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">CSC</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Vessel' : 'Navire'}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Goods' : 'Marchandise'}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Status' : 'Statut'}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Date' : 'Date'}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 bg-slate-900">
                {cscList.length === 0 ? (
                  <EmptyRow colSpan={5} text={lang === 'en' ? 'No CSC recorded yet.' : 'Aucun CSC enregistré.'} />
                ) : (
                  cscList.map((c, idx) => (
                    <tr key={c.id ?? idx}>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{c.numero_csc}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{c.navire}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{c.type_marchandise || ''}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-green-600">{c.statut}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{c.date_demande}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* DUM / SYGED */}
      {activeTab === 'syged' && (
        <div className="rounded-lg bg-slate-900 p-4 shadow sm:p-6">
          <h2 className="mb-4 text-xl font-semibold">SYGED  {lang === 'en' ? 'Single Customs Declaration' : 'Déclaration Unique de Marchandises'}</h2>
          <form onSubmit={handleCreateDUM} className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
            <Field label={lang === 'en' ? 'Operation Type' : 'Type d’Opération'}>
              <select required className={inputCls} value={dumForm.type_operation || ''} onChange={(e) => setDumForm({ ...dumForm, type_operation: e.target.value })}>
                <option value=""></option>
                <option value="import">Import</option>
                <option value="export">Export</option>
                <option value="transit">Transit</option>
              </select>
            </Field>
            <Field label={lang === 'en' ? 'Customs Regime' : 'Régime Douanier'}>
              <select required className={inputCls} value={dumForm.regime_douanier || ''} onChange={(e) => setDumForm({ ...dumForm, regime_douanier: e.target.value })}>
                <option value=""></option>
                <option value="mise_a_la_consommation">Mise à la consommation</option>
                <option value="transit">Transit</option>
                <option value="admission_temporaire">Admission temporaire</option>
                <option value="entrepot">Entrepôt</option>
              </select>
            </Field>
            <Field label={lang === 'en' ? 'Customs Office' : 'Bureau de Douane'}>
              <input required className={inputCls} value={dumForm.bureau_douane || ''} onChange={(e) => setDumForm({ ...dumForm, bureau_douane: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Declarant' : 'Déclarant'}>
              <input required className={inputCls} value={dumForm.declarant || ''} onChange={(e) => setDumForm({ ...dumForm, declarant: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Importer' : 'Importateur'}>
              <input required className={inputCls} value={dumForm.importateur || ''} onChange={(e) => setDumForm({ ...dumForm, importateur: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Goods' : 'Marchandise'}>
              <input required className={inputCls} value={dumForm.marchandise || ''} onChange={(e) => setDumForm({ ...dumForm, marchandise: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'FOB Value (USD)' : 'Valeur FOB (USD)'}>
              <input type="number" step="0.01" className={inputCls} value={dumForm.valeur_fob ?? ''} onChange={(e) => setDumForm({ ...dumForm, valeur_fob: e.target.value ? parseFloat(e.target.value) : undefined })} />
            </Field>
            <Field label={lang === 'en' ? 'Exchange Rate' : 'Taux de Change'}>
              <input type="number" step="0.01" className={inputCls} value={dumForm.taux_change ?? ''} onChange={(e) => setDumForm({ ...dumForm, taux_change: e.target.value ? parseFloat(e.target.value) : undefined })} />
            </Field>
            <div className="md:col-span-2">
              <button type="submit" disabled={loading} className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                {loading ? '…' : (lang === 'en' ? 'Create DUM' : 'Créer DUM')}
              </button>
            </div>
          </form>

          <h3 className="mb-3 text-lg font-semibold">{lang === 'en' ? 'Registered DUM' : 'DUM enregistrés'}</h3>
          <div className="overflow-x-auto rounded-md border border-slate-700">
            <table className="min-w-full divide-y divide-slate-800">
              <thead className="bg-slate-800">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">DUM</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Regime' : 'Régime'}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Goods' : 'Marchandise'}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Status' : 'Statut'}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Date' : 'Date'}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 bg-slate-900">
                {dumList.length === 0 ? (
                  <EmptyRow colSpan={5} text={lang === 'en' ? 'No DUM recorded yet.' : 'Aucun DUM enregistré.'} />
                ) : (
                  dumList.map((d, idx) => (
                    <tr key={d.id ?? idx}>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{d.numero_dum}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{d.regime_douanier}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{d.marchandise}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-green-600">{d.statut}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{d.date_depot}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* APE */}
      {activeTab === 'ape' && (
        <div className="rounded-lg bg-slate-900 p-4 shadow sm:p-6">
          <h2 className="mb-4 text-xl font-semibold">APE  {lang === 'en' ? 'Foreign Payment Order (BEAC)' : 'Arrêté de Paiement des Étrangers (BEAC)'}</h2>
          <form onSubmit={handleCreateAPE} className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
            <Field label={lang === 'en' ? 'Importer' : 'Importateur'}>
              <input required className={inputCls} value={apeForm.importateur || ''} onChange={(e) => setApeForm({ ...apeForm, importateur: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Amount (XAF)' : 'Montant (XAF)'}>
              <input required type="number" step="0.01" className={inputCls} value={apeForm.montant_xaf ?? ''} onChange={(e) => setApeForm({ ...apeForm, montant_xaf: e.target.value ? parseFloat(e.target.value) : undefined })} />
            </Field>
            <Field label={lang === 'en' ? 'Currency' : 'Devise'}>
              <select required className={inputCls} value={apeForm.devise || ''} onChange={(e) => setApeForm({ ...apeForm, devise: e.target.value })}>
                <option value=""></option>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
              </select>
            </Field>
            <Field label={lang === 'en' ? 'Bank' : 'Banque'}>
              <input required className={inputCls} value={apeForm.banque || ''} onChange={(e) => setApeForm({ ...apeForm, banque: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Foreign Beneficiary' : 'Bénéficiaire Étranger'}>
              <input className={inputCls} value={apeForm.beneficiaire_etranger || ''} onChange={(e) => setApeForm({ ...apeForm, beneficiaire_etranger: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Beneficiary Country' : 'Pays du Bénéficiaire'}>
              <input className={inputCls} value={apeForm.pays_beneficiaire || ''} onChange={(e) => setApeForm({ ...apeForm, pays_beneficiaire: e.target.value })} />
            </Field>
            <Field label={lang === 'en' ? 'Transfer Purpose' : 'Objet du Transfert'}>
              <input className={inputCls} value={apeForm.objet_transfert || ''} onChange={(e) => setApeForm({ ...apeForm, objet_transfert: e.target.value })} />
            </Field>
            <div className="md:col-span-2">
              <button type="submit" disabled={loading} className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                {loading ? '…' : (lang === 'en' ? 'Create APE' : 'Créer APE')}
              </button>
            </div>
          </form>

          <h3 className="mb-3 text-lg font-semibold">{lang === 'en' ? 'Registered APE' : 'APE enregistrés'}</h3>
          <div className="overflow-x-auto rounded-md border border-slate-700">
            <table className="min-w-full divide-y divide-slate-800">
              <thead className="bg-slate-800">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">APE</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Importer' : 'Importateur'}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Amount' : 'Montant'}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Status' : 'Statut'}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-400">{lang === 'en' ? 'Date' : 'Date'}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 bg-slate-900">
                {apeList.length === 0 ? (
                  <EmptyRow colSpan={5} text={lang === 'en' ? 'No APE recorded yet.' : 'Aucun APE enregistré.'} />
                ) : (
                  apeList.map((a, idx) => (
                    <tr key={a.id ?? idx}>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{a.numero_ape}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{a.importateur}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{a.montant_xaf} {a.devise}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-green-600">{a.statut}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{a.date_demande}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
