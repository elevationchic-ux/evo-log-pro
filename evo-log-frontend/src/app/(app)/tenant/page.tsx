'use client';

/**
 * Gestion Multi-Tenant & Sociétés (Super-Admin).
 *
 * Liaisons backend vérifiées (règle Zéro-Mock) : chaque champ affiché ou envoyé
 * correspond EXACTEMENT au contrat de l'API, sinon l'écran ment.
 *  - `GET /tenant/companies` -> List[CompanyResponse] : statut réel = booléen
 *    `is_active` (il n'existe AUCUNE colonne `statut` sur Company) ; plan =
 *    `subscription_plan_id` (pas `plan_id`).
 *  - `GET /tenant/reports/companies` -> { total_companies, actives, trial,
 *    par_plan } (comptes SQL réels). Le champ `suspendues` n'existe pas : on le
 *    calcule depuis la liste, on ne le lit pas dans un rapport muet.
 *  - `GET /tenant/company-profile` -> raison_sociale / pays / email /
 *    forme_juridique (les clés sont `raison_sociale`, `forme_juridique` :
 *    `nom` et `statut` n'y figurent pas).
 *  - `POST /tenant/companies` -> CompanyCreate exige code, nom, legal_form,
 *    tax_id, email, telephone, subscription_plan_id : le formulaire collecte
 *    désormais ces champs, sinon la création échouait systématiquement (422).
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Building2, CreditCard, RefreshCw, PlusCircle, AlertTriangle, Settings, Globe, X, Save
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api-client';

interface Company {
  id: number;
  code: string;
  nom: string;
  pays?: string | null;
  email?: string | null;
  is_active: boolean;
  subscription_plan_id?: number | null;
}

interface Plan { id: number; code: string; nom: string; }

function messageErreur(e: unknown, defaut: string): string {
  const status = (e as { response?: { status?: number } })?.response?.status;
  if (status === 401) return 'Session expirée. Reconnectez-vous.';
  if (status === 403) return 'Accès réservé au Super-Admin.';
  return defaut;
}

export default function TenantPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [companyProfile, setCompanyProfile] = useState<any>(null);
  const [rapportCompanies, setRapportCompanies] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newCompany, setNewCompany] = useState({
    code: '',
    nom: '',
    legal_form: 'SARL',
    tax_id: '',
    email: '',
    telephone: '',
    pays: 'Cameroun',
    subscription_plan_id: '',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    const [resCo, resPlans, resProfile, resRapport] = await Promise.allSettled([
      apiClient.get('/api/v1/tenant/companies'),
      apiClient.get('/api/v1/tenant/plans'),
      apiClient.get('/api/v1/tenant/company-profile'),
      apiClient.get('/api/v1/tenant/reports/companies'),
    ]);
    if (resCo.status === 'fulfilled' && Array.isArray(resCo.value.data)) {
      setCompanies(resCo.value.data);
    } else {
      // Le lister des sociétés est la source principale : son échec est une
      // erreur d'écran, pas un « aucune société ».
      setCompanies([]);
      setError(messageErreur(resCo.status === 'rejected' ? resCo.reason : null, 'Impossible de charger les sociétés.'));
    }
    if (resPlans.status === 'fulfilled' && Array.isArray(resPlans.value.data)) setPlans(resPlans.value.data);
    if (resProfile.status === 'fulfilled' && resProfile.value.data) setCompanyProfile(resProfile.value.data);
    if (resRapport.status === 'fulfilled' && resRapport.value.data) setRapportCompanies(resRapport.value.data);
    setLoading(false);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreateCompany = async () => {
    // Miroir exact de CompanyCreate : sans ces champs, l'API renvoie 422.
    if (!newCompany.code.trim() || !newCompany.nom.trim() || !newCompany.tax_id.trim()
      || !newCompany.email.trim() || !newCompany.telephone.trim() || !newCompany.subscription_plan_id) {
      toast.error("Renseignez le code, la raison sociale, le NIF, l'email, le téléphone et le plan.");
      return;
    }
    try {
      await apiClient.post('/api/v1/tenant/companies', {
        code: newCompany.code.trim(),
        nom: newCompany.nom.trim(),
        legal_form: newCompany.legal_form,
        tax_id: newCompany.tax_id.trim(),
        email: newCompany.email.trim(),
        telephone: newCompany.telephone.trim(),
        pays: newCompany.pays,
        subscription_plan_id: Number(newCompany.subscription_plan_id),
      });
      toast.success('Société créée.');
      setShowCreateForm(false);
      setNewCompany({ code: '', nom: '', legal_form: 'SARL', tax_id: '', email: '', telephone: '', pays: 'Cameroun', subscription_plan_id: '' });
      fetchData();
    } catch (err) {
      toast.error(messageErreur(err, "Erreur lors de la création de la société."));
    }
  };

  const handleActiver = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/tenant/companies/${id}/activer`);
      fetchData();
    } catch (err) {
      toast.error(messageErreur(err, "Erreur lors de l'activation."));
    }
  };

  const handleSuspendre = async (id: number) => {
    try {
      // Le backend exige un motif de suspension en query param.
      await apiClient.put(`/api/v1/tenant/companies/${id}/suspendre?raison=Suspension%20administrative`);
      fetchData();
    } catch (err) {
      toast.error(messageErreur(err, 'Erreur lors de la suspension.'));
    }
  };

  const activeCount = rapportCompanies?.actives ?? companies.filter(c => c.is_active).length;
  const suspendedCount = companies.filter(c => !c.is_active).length;

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Building2 className="w-3.5 h-3.5" /> Multi-Tenant · Gestion des Sociétés Clientes & Abonnements SaaS
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Gestion Multi-Tenant & Sociétés</h1>
          <p className="text-xs text-slate-400 mt-1">Administration des tenants SaaS, plans d&apos;abonnement, activation/suspension de sociétés et personnalisation des portails B2B.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button onClick={() => setShowCreateForm(true)} className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-900/20 transition-all">
            <PlusCircle className="w-4 h-4" /> Nouvelle Société
          </button>
        </div>
      </div>

      {/* Rapport Stats — toutes dérivées de la liste réelle / du rapport SQL */}
      {!loading && !error && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Sociétés Actives', value: activeCount, icon: Building2, color: 'text-emerald-400' },
            { label: 'Total Sociétés', value: companies.length, icon: Globe, color: 'text-cyan-400' },
            { label: 'Plans Disponibles', value: plans.length, icon: CreditCard, color: 'text-purple-400' },
            { label: 'Suspendues', value: suspendedCount, icon: AlertTriangle, color: 'text-amber-400' },
          ].map((s) => (
            <div key={s.label} className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400">{s.label}</span>
                <s.icon className={`w-4 h-4 ${s.color}`} />
              </div>
              <p className={`text-2xl font-black mt-2 ${s.color}`}>{s.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Company Profile Card — clés réelles de /company-profile */}
      {companyProfile && Object.keys(companyProfile).length > 0 && (
        <div className="bg-slate-900/80 border border-emerald-500/20 p-6 rounded-3xl">
          <div className="flex items-center gap-3 mb-4">
            <Settings className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-black text-white">Profil de la Société Courante</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            {[
              { label: 'Raison Sociale', value: companyProfile.raison_sociale },
              { label: 'Pays', value: companyProfile.pays },
              { label: 'Email', value: companyProfile.email },
              { label: 'Forme Juridique', value: companyProfile.forme_juridique },
            ].map(f => (
              <div key={f.label}>
                <span className="text-[11px] font-semibold text-slate-500 block">{f.label}</span>
                <span className="text-slate-100 font-bold">{f.value || '—'}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {showCreateForm && (
        <div className="bg-slate-900/90 border border-emerald-500/30 p-6 rounded-3xl shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-black text-white">Créer une Nouvelle Société (Tenant)</h2>
            <button onClick={() => setShowCreateForm(false)}><X className="w-5 h-5 text-slate-400 hover:text-white" /></button>
          </div>
          <p className="text-[11px] text-slate-400 mb-4">Les champs marqués * sont requis par l&apos;API (sinon la création échoue).</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { key: 'code', label: 'Code (ex. EVOLOGS-CMR) *', type: 'text' },
              { key: 'nom', label: 'Raison Sociale *', type: 'text' },
              { key: 'tax_id', label: 'NIF *', type: 'text' },
              { key: 'email', label: 'Email Principal *', type: 'email' },
              { key: 'telephone', label: 'Téléphone *', type: 'text' },
              { key: 'pays', label: 'Pays', type: 'text' },
            ].map(f => (
              <div key={f.key}>
                <label className="text-xs font-medium text-slate-400 block mb-1">{f.label}</label>
                <input type={f.type} value={(newCompany as any)[f.key]} onChange={(e) => setNewCompany({ ...newCompany, [f.key]: e.target.value })}
                  className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-emerald-500 transition-colors" />
              </div>
            ))}
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1">Forme Juridique *</label>
              <select value={newCompany.legal_form} onChange={(e) => setNewCompany({ ...newCompany, legal_form: e.target.value })}
                className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-emerald-500">
                <option value="SARL">SARL</option>
                <option value="SA">SA</option>
                <option value="SAS">SAS</option>
                <option value="OTHER">Autre</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1">Plan d&apos;Abonnement *</label>
              <select value={newCompany.subscription_plan_id} onChange={(e) => setNewCompany({ ...newCompany, subscription_plan_id: e.target.value })}
                className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-emerald-500">
                <option value="">Sélectionnez un plan…</option>
                {plans.map(p => (
                  <option key={p.id} value={p.id}>{p.nom} ({p.code})</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-3 mt-5">
            <button onClick={() => setShowCreateForm(false)} className="px-5 py-2.5 rounded-2xl bg-slate-800 text-slate-300 text-xs font-bold">Annuler</button>
            <button onClick={handleCreateCompany} className="px-5 py-2.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center gap-2">
              <Save className="w-4 h-4" /> Créer le Tenant
            </button>
          </div>
        </div>
      )}

      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-slate-800 flex items-center gap-3">
          <Building2 className="w-5 h-5 text-emerald-400" />
          <h2 className="text-base font-black text-white">Sociétés Clientes (Tenants)</h2>
          {!loading && !error && <span className="ml-auto text-xs text-slate-400">{companies.length} sociétés</span>}
        </div>
        {loading ? (
          <div className="p-12 text-center"><RefreshCw className="w-6 h-6 animate-spin text-emerald-400 mx-auto mb-2" /></div>
        ) : error ? (
          <div className="p-12 text-center text-amber-400">
            <AlertTriangle className="w-10 h-10 mx-auto mb-2" />
            <p className="font-bold text-white">Chargement impossible</p>
            <p className="text-sm text-slate-400 mt-1">{error}</p>
            <button onClick={fetchData} className="mt-4 px-4 py-2 rounded-2xl bg-slate-800 border border-slate-700 text-xs font-bold text-slate-200">Réessayer</button>
          </div>
        ) : companies.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <Building2 className="w-10 h-10 text-slate-400 mx-auto mb-2" />
            <p className="font-bold text-white">Aucune société cliente enregistrée</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800/80">
                  {['Raison Sociale', 'Pays', 'Email', 'Plan', 'Statut', 'Actions'].map(h => (
                    <th key={h} className="px-5 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {companies.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-5 py-4 font-bold text-white">{c.nom}</td>
                    <td className="px-5 py-4 text-slate-300">{c.pays || '—'}</td>
                    <td className="px-5 py-4 text-slate-300 text-xs">{c.email || '—'}</td>
                    <td className="px-5 py-4 text-slate-300">{c.subscription_plan_id ?? '—'}</td>
                    <td className="px-5 py-4">
                      <span className={`px-2.5 py-1 rounded-xl text-[11px] font-bold uppercase border ${
                        c.is_active ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                      }`}>
                        {c.is_active ? 'Actif' : 'Suspendu'}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        {c.is_active ? (
                          <button onClick={() => handleSuspendre(c.id)} className="px-3 py-1.5 rounded-xl bg-amber-600/20 hover:bg-amber-600/30 text-amber-400 border border-amber-500/30 text-xs font-bold transition-all">Suspendre</button>
                        ) : (
                          <button onClick={() => handleActiver(c.id)} className="px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-bold transition-all">Activer</button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
