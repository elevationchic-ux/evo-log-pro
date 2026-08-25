'use client';

import { useState } from 'react';
import { fiscaliteCamerounApi } from '@/lib/api-cameroun';

export default function FiscaliteCamerounPage() {
  const [activeTab, setActiveTab] = useState('declarations');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [declarations, setDeclarations] = useState<any[]>([]);
  const [formData, setFormData] = useState<any>({});
  const [calculationResult, setCalculationResult] = useState(null);

  const handleCreateDeclaration = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await fiscaliteCamerounApi.creerDeclaration(formData);
      setDeclarations([...declarations, result.data]);
      setFormData({});
      alert('Déclaration créée avec succès!');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de la création de la déclaration');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCalculTVA = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await fiscaliteCamerounApi.calculerTVA(formData.montant_ht, formData.taux_tva);
      setCalculationResult(result.data);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors du calcul TVA');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Fiscalité Cameroun</h1>
        <p className="text-gray-600 mt-2">Gestion fiscalité Cameroun/OHADA (IRPP, IS, TCF, TDR, TVA)</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('declarations')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'declarations'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Déclarations Fiscales
          </button>
          <button
            onClick={() => setActiveTab('retenues')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'retenues'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Retenues à la Source
          </button>
          <button
            onClick={() => setActiveTab('ohada')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'ohada'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Calculs OHADA
          </button>
          <button
            onClick={() => setActiveTab('rapports')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'rapports'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Rapports Financiers
          </button>
        </nav>
      </div>

      {activeTab === 'declarations' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Créer Déclaration Fiscale</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Type d'Impôt</label>
              <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                <option value="IS">IS - Impôt Sociétés</option>
                <option value="IRPP">IRPP - Impôt Revenu Personnes Physiques</option>
                <option value="TCF">TCF - Taxe Communale</option>
                <option value="TDR">TDR - Taxe Développement Régional</option>
                <option value="PATENTE">Patente</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Période Début</label>
              <input
                type="date"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Période Fin</label>
              <input
                type="date"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Chiffre d'Affaires (FCFA)</label>
              <input
                type="number"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="Ex: 100000000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Bénéfice (FCFA)</label>
              <input
                type="number"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="Ex: 15000000"
              />
            </div>
          </div>

          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Créer Déclaration
          </button>

          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-3">Déclarations en Cours</h3>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Référence</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Période</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Montant Du</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">DEC-2026-001</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">IS</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">01/01/2026 - 31/12/2026</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">3 000 000 FCFA</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-yellow-600">En attente</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'retenues' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Créer Retenue à la Source</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Type de Retenue</label>
              <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                <option value="SALAIRE">Salaire (15%)</option>
                <option value="HONORAIRE">Honoraires (20%)</option>
                <option value="DIVIDENDE">Dividendes (15%)</option>
                <option value="LOYER">Loyer (15%)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Montant Brut (FCFA)</label>
              <input
                type="number"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="Ex: 500000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Bénéficiaire</label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="Ex: Jean Dupont"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Numéro Contribuable</label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="Ex: P123456789"
              />
            </div>
          </div>

          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Créer Retenue
          </button>
        </div>
      )}

      {activeTab === 'ohada' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Calculs OHADA</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">TVA OHADA</h3>
              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">Montant HT (FCFA)</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: 100000"
                />
              </div>
              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">Taux TVA (%)</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  defaultValue="19.25"
                />
              </div>
              <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 w-full">
                Calculer TVA
              </button>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Centimes Additionnels</h3>
              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">Montant (FCFA)</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: 100000"
                />
              </div>
              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">Taux (%)</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  defaultValue="10"
                />
              </div>
              <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 w-full">
                Calculer Centimes
              </button>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">IS Minimum Cameroun</h3>
              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">Chiffre d'Affaires (FCFA)</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: 100000000"
                />
              </div>
              <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 w-full">
                Calculer IS Minimum
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'rapports' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Rapports Financiers OHADA</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Bilan OHADA</h3>
              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">Exercice</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  defaultValue="2026"
                />
              </div>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 w-full">
                Générer Bilan
              </button>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Compte de Résultat</h3>
              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">Exercice</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  defaultValue="2026"
                />
              </div>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 w-full">
                Générer Compte de Résultat
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
