'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { fiscaliteCamerounApi } from '@/lib/api-cameroun';
import { useAuth } from '@/components/layout/AuthProvider';

export default function FiscaliteCamerounPage() {
  const [activeTab, setActiveTab] = useState('declarations');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [declarations, setDeclarations] = useState<any[]>([]);
  const [retenues, setRetenues] = useState<any[]>([]);
  const [formData, setFormData] = useState<any>({});
  const [retenueData, setRetenueData] = useState<any>({});
  const [tvaData, setTvaData] = useState<any>({ montant_ht: '', taux: '19.25' });
  const [tvaResult, setTvaResult] = useState<any>(null);
  const [centimeData, setCentimeData] = useState<any>({ montant: '', taux: '10' });
  const [centimeResult, setCentimeResult] = useState<any>(null);
  const [isMinData, setIsMinData] = useState<any>({ chiffre_affaires: '' });
  const [isMinResult, setIsMinResult] = useState<any>(null);
  const [exercice, setExercice] = useState<number>(new Date().getFullYear());
  const [rapport, setRapport] = useState<{ type: string; exercice: number; data: any } | null>(null);
  const { user } = useAuth();

  const handleCreateDeclaration = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user?.companyId) {
      setError('Aucune société active sur cette session : impossible de rattacher la déclaration fiscale.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await fiscaliteCamerounApi.creerDeclaration({
        ...formData,
        company_id: user.companyId,
      });
      // Le backend répond { success, data } : on empile la déclaration réellement créée.
      setDeclarations(prev => [...prev, result?.data ?? result]);
      setFormData({});
      toast.success('Déclaration créée et enregistrée.');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de la création de la déclaration');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCalculTva = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await fiscaliteCamerounApi.calculerTVA(
        parseFloat(tvaData.montant_ht || '0'),
        parseFloat(tvaData.taux || '19.25')
      );
      setTvaResult(result?.data ?? result);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors du calcul TVA');
    } finally {
      setLoading(false);
    }
  };

  const handleCalculCentimes = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await fiscaliteCamerounApi.calculerCentimes(
        parseFloat(centimeData.montant || '0'),
        parseFloat(centimeData.taux || '10')
      );
      setCentimeResult(result?.data ?? result);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors du calcul des centimes additionnels');
    } finally {
      setLoading(false);
    }
  };

  const handleCalculIsMinimum = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await fiscaliteCamerounApi.calculerISMinimum(
        parseFloat(isMinData.chiffre_affaires || '0')
      );
      setIsMinResult(result?.data ?? result);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors du calcul de l\'IS minimum');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRetenue = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user?.companyId) {
      setError('Aucune société active sur cette session : impossible de rattacher la retenue.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await fiscaliteCamerounApi.creerRetenueSource({
        type_retenue: retenueData.type_retenue || 'SALAIRE',
        montant_brut: parseFloat(retenueData.montant_brut || '0'),
        beneficiaire: retenueData.beneficiaire || '',
        numero_contribuable: retenueData.numero_contribuable || '',
        company_id: user.companyId,
      });
      setRetenues(prev => [...prev, result?.data ?? result]);
      setRetenueData({});
      toast.success('Retenue à la source créée et enregistrée.');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de la création de la retenue');
    } finally {
      setLoading(false);
    }
  };

  const handleGenererBilan = async () => {
    if (!user?.companyId) {
      setError('Aucune société active sur cette session : impossible de générer le bilan.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await fiscaliteCamerounApi.genererBilan(user.companyId, exercice);
      setRapport({ type: 'Bilan OHADA', exercice, data: result?.data ?? result });
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de la génération du bilan');
    } finally {
      setLoading(false);
    }
  };

  const handleGenererCompteResultat = async () => {
    if (!user?.companyId) {
      setError('Aucune société active sur cette session : impossible de générer le compte de résultat.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await fiscaliteCamerounApi.genererCompteResultat(user.companyId, exercice);
      setRapport({ type: 'Compte de Résultat', exercice, data: result?.data ?? result });
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de la génération du compte de résultat');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-slate-100">Fiscalité Cameroun</h1>
        <p className="text-slate-400 mt-2">Gestion fiscalité Cameroun/OHADA (IRPP, IS, TCF, TDR, TVA)</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-500/10 border border-red-500/40 text-red-300 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="border-b border-slate-700 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('declarations')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'declarations'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
          >
            Déclarations Fiscales
          </button>
          <button
            onClick={() => setActiveTab('retenues')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'retenues'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
          >
            Retenues à la Source
          </button>
          <button
            onClick={() => setActiveTab('ohada')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'ohada'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
          >
            Calculs OHADA
          </button>
          <button
            onClick={() => setActiveTab('rapports')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'rapports'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
          >
            Rapports Financiers
          </button>
        </nav>
      </div>

      {activeTab === 'declarations' && (
        <div className="bg-slate-900 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Créer Déclaration Fiscale</h2>

          <form onSubmit={handleCreateDeclaration} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Type d'Impôt</label>
              <select
                className="w-full border border-slate-600 rounded-md px-3 py-2"
                value={formData.type_impot || 'IS'}
                onChange={(e) => setFormData({ ...formData, type_impot: e.target.value })}
              >
                <option value="IS">IS - Impôt Sociétés</option>
                <option value="IRPP">IRPP - Impôt Revenu Personnes Physiques</option>
                <option value="TCF">TCF - Taxe Communale</option>
                <option value="TDR">TDR - Taxe Développement Régional</option>
                <option value="PATENTE">Patente</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Période Début</label>
              <input
                type="date"
                required
                className="w-full border border-slate-600 rounded-md px-3 py-2"
                value={formData.periode_debut || ''}
                onChange={(e) => setFormData({ ...formData, periode_debut: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Période Fin</label>
              <input
                type="date"
                required
                className="w-full border border-slate-600 rounded-md px-3 py-2"
                value={formData.periode_fin || ''}
                onChange={(e) => setFormData({ ...formData, periode_fin: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Chiffre d'Affaires (FCFA)</label>
              <input
                type="number"
                required
                min={0}
                className="w-full border border-slate-600 rounded-md px-3 py-2"
                placeholder="Ex: 100000000"
                value={formData.chiffre_affaires ?? ''}
                onChange={(e) => setFormData({ ...formData, chiffre_affaires: parseFloat(e.target.value) })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Bénéfice (FCFA)</label>
              <input
                type="number"
                required
                min={0}
                className="w-full border border-slate-600 rounded-md px-3 py-2"
                placeholder="Ex: 15000000"
                value={formData.benefice ?? ''}
                onChange={(e) => setFormData({ ...formData, benefice: parseFloat(e.target.value) })}
              />
            </div>
            <div className="flex items-end">
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Enregistrement...' : 'Créer Déclaration'}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-3">Déclarations créées pendant la session</h3>
            {declarations.length === 0 ? (
              <p className="text-sm text-slate-400 border border-dashed border-slate-600 rounded-md px-4 py-6 text-center">
                Aucune déclaration enregistrée. Le backend n'expose pas encore de liste historique :
                les déclarations créées ci-dessus apparaîtront ici.
              </p>
            ) : (
              <table className="min-w-full divide-y divide-slate-800">
                <thead className="bg-slate-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Référence</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Période</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Montant Du</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Statut</th>
                  </tr>
                </thead>
                <tbody className="bg-slate-900 divide-y divide-slate-800">
                  {declarations.map((d, idx) => (
                    <tr key={d.id ?? idx}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-100">{d.reference_declaration || `DEC-${d.id ?? idx + 1}`}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-100">{d.type_impot || ''}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-100">{d.periode_debut || '?'} → {d.periode_fin || '?'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-100">{typeof d.montant_du === 'number' ? `${d.montant_du.toLocaleString()} FCFA` : ''}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-yellow-600">{d.statut || 'En attente'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {activeTab === 'retenues' && (
        <div className="bg-slate-900 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Créer Retenue à la Source</h2>

          <form onSubmit={handleCreateRetenue} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Type de Retenue</label>
              <select
                className="w-full border border-slate-600 rounded-md px-3 py-2"
                value={retenueData.type_retenue || 'SALAIRE'}
                onChange={(e) => setRetenueData({ ...retenueData, type_retenue: e.target.value })}
              >
                <option value="SALAIRE">Salaire (15%)</option>
                <option value="HONORAIRE">Honoraires (20%)</option>
                <option value="DIVIDENDE">Dividendes (15%)</option>
                <option value="LOYER">Loyer (15%)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Montant Brut (FCFA)</label>
              <input
                type="number"
                required
                min={0}
                className="w-full border border-slate-600 rounded-md px-3 py-2"
                placeholder="Ex: 500000"
                value={retenueData.montant_brut ?? ''}
                onChange={(e) => setRetenueData({ ...retenueData, montant_brut: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Bénéficiaire</label>
              <input
                type="text"
                required
                className="w-full border border-slate-600 rounded-md px-3 py-2"
                placeholder="Nom du bénéficiaire"
                value={retenueData.beneficiaire || ''}
                onChange={(e) => setRetenueData({ ...retenueData, beneficiaire: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Numéro Contribuable</label>
              <input
                type="text"
                required
                className="w-full border border-slate-600 rounded-md px-3 py-2"
                placeholder="Ex: P123456789"
                value={retenueData.numero_contribuable || ''}
                onChange={(e) => setRetenueData({ ...retenueData, numero_contribuable: e.target.value })}
              />
            </div>
            <div className="flex items-end">
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Enregistrement...' : 'Créer Retenue'}
              </button>
            </div>
          </form>

          {retenues.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-3">Retenues créées pendant la session</h3>
              <table className="min-w-full divide-y divide-slate-800">
                <thead className="bg-slate-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Brut</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Retenue</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Bénéficiaire</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Statut</th>
                  </tr>
                </thead>
                <tbody className="bg-slate-900 divide-y divide-slate-800">
                  {retenues.map((r, idx) => (
                    <tr key={r.id ?? idx}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-100">{r.type_retenue || ''}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-100">{typeof r.montant_brut === 'number' ? `${r.montant_brut.toLocaleString()} FCFA` : ''}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-100">{typeof r.montant_retenue === 'number' ? `${r.montant_retenue.toLocaleString()} FCFA` : ''}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-100">{r.beneficiaire || ''}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-yellow-600">{r.statut || 'En attente de versement'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'ohada' && (
        <div className="bg-slate-900 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Calculs OHADA</h2>
          <p className="text-sm text-slate-400 mb-4">
            Ces calculs sont exécutés par le service fiscal backend (barèmes OHADA / Cameroun)  aucune approximation côté navigateur.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <form onSubmit={handleCalculTva} className="bg-slate-800 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">TVA OHADA</h3>
              <div className="mb-3">
                <label className="block text-sm font-medium text-slate-200 mb-2">Montant HT (FCFA)</label>
                <input
                  type="number"
                  required
                  min={0}
                  className="w-full border border-slate-600 rounded-md px-3 py-2"
                  placeholder="Ex: 100000"
                  value={tvaData.montant_ht}
                  onChange={(e) => setTvaData({ ...tvaData, montant_ht: e.target.value })}
                />
              </div>
              <div className="mb-3">
                <label className="block text-sm font-medium text-slate-200 mb-2">Taux TVA (%)</label>
                <input
                  type="number"
                  step="0.01"
                  className="w-full border border-slate-600 rounded-md px-3 py-2"
                  value={tvaData.taux}
                  onChange={(e) => setTvaData({ ...tvaData, taux: e.target.value })}
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 w-full"
              >
                {loading ? 'Calcul...' : 'Calculer TVA'}
              </button>
              {tvaResult && (
                <div className="mt-3 text-sm bg-slate-900 border border-green-500/40 rounded-md p-3 space-y-1">
                  {Object.entries(tvaResult).map(([k, v]) => (
                    <p key={k}><span className="font-medium text-slate-400">{k} :</span> {typeof v === 'number' ? v.toLocaleString() : String(v)}</p>
                  ))}
                </div>
              )}
            </form>

            <form onSubmit={handleCalculCentimes} className="bg-slate-800 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Centimes Additionnels</h3>
              <div className="mb-3">
                <label className="block text-sm font-medium text-slate-200 mb-2">Montant (FCFA)</label>
                <input
                  type="number"
                  required
                  min={0}
                  className="w-full border border-slate-600 rounded-md px-3 py-2"
                  placeholder="Ex: 100000"
                  value={centimeData.montant}
                  onChange={(e) => setCentimeData({ ...centimeData, montant: e.target.value })}
                />
              </div>
              <div className="mb-3">
                <label className="block text-sm font-medium text-slate-200 mb-2">Taux (%)</label>
                <input
                  type="number"
                  className="w-full border border-slate-600 rounded-md px-3 py-2"
                  value={centimeData.taux}
                  onChange={(e) => setCentimeData({ ...centimeData, taux: e.target.value })}
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 w-full"
              >
                {loading ? 'Calcul...' : 'Calculer Centimes'}
              </button>
              {centimeResult && (
                <div className="mt-3 text-sm bg-slate-900 border border-green-500/40 rounded-md p-3 space-y-1">
                  {Object.entries(centimeResult).map(([k, v]) => (
                    <p key={k}><span className="font-medium text-slate-400">{k} :</span> {typeof v === 'number' ? v.toLocaleString() : String(v)}</p>
                  ))}
                </div>
              )}
            </form>

            <form onSubmit={handleCalculIsMinimum} className="bg-slate-800 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">IS Minimum Cameroun</h3>
              <div className="mb-3">
                <label className="block text-sm font-medium text-slate-200 mb-2">Chiffre d'Affaires (FCFA)</label>
                <input
                  type="number"
                  required
                  min={0}
                  className="w-full border border-slate-600 rounded-md px-3 py-2"
                  placeholder="Ex: 100000000"
                  value={isMinData.chiffre_affaires}
                  onChange={(e) => setIsMinData({ ...isMinData, chiffre_affaires: e.target.value })}
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 w-full"
              >
                {loading ? 'Calcul...' : 'Calculer IS Minimum'}
              </button>
              {isMinResult && (
                <div className="mt-3 text-sm bg-slate-900 border border-green-500/40 rounded-md p-3 space-y-1">
                  {Object.entries(isMinResult).map(([k, v]) => (
                    <p key={k}><span className="font-medium text-slate-400">{k} :</span> {typeof v === 'number' ? v.toLocaleString() : String(v)}</p>
                  ))}
                </div>
              )}
            </form>
          </div>
        </div>
      )}

      {activeTab === 'rapports' && (
        <div className="bg-slate-900 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Rapports Financiers OHADA</h2>

          <div className="mb-4 max-w-xs">
            <label className="block text-sm font-medium text-slate-200 mb-2">Exercice</label>
            <input
              type="number"
              className="w-full border border-slate-600 rounded-md px-3 py-2"
              value={exercice}
              min={2000}
              max={2100}
              onChange={(e) => setExercice(parseInt(e.target.value, 10) || new Date().getFullYear())}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-slate-800 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Bilan OHADA</h3>
              <p className="text-xs text-slate-400 mb-3">Agrège les écritures comptables réelles de la société pour l'exercice choisi.</p>
              <button
                onClick={handleGenererBilan}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 w-full"
              >
                {loading ? 'Génération...' : 'Générer Bilan'}
              </button>
            </div>

            <div className="bg-slate-800 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Compte de Résultat</h3>
              <p className="text-xs text-slate-400 mb-3">Produits et charges de l'exercice, calculés depuis la comptabilité OHADA.</p>
              <button
                onClick={handleGenererCompteResultat}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 w-full"
              >
                {loading ? 'Génération...' : 'Générer Compte de Résultat'}
              </button>
            </div>
          </div>

          {rapport && (
            <div className="border border-blue-500/40 bg-blue-50/50 rounded-md p-4">
              <h3 className="font-semibold text-slate-100 mb-2">{rapport.type}  exercice {rapport.exercice}</h3>
              <pre className="text-xs text-slate-200 whitespace-pre-wrap overflow-x-auto">
                {JSON.stringify(rapport.data, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
