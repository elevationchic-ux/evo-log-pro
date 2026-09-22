'use client';

import { useState } from 'react';
import Link from 'next/link';
import { integrationCamerounApi } from '@/lib/api-cameroun';

export default function IntegrationCamerounPage() {
  const [activeTab, setActiveTab] = useState('bsc');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [bscList, setBscList] = useState<any[]>([]);
  const [formData, setFormData] = useState<any>({});

  const handleCreateBSC = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await integrationCamerounApi.creerBSC(formData);
      setBscList([...bscList, result.data]);
      setFormData({});
      alert('BSC créé avec succès!');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de la création du BSC');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCSC = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await integrationCamerounApi.demanderCSC(formData);
      alert('CSC demandé avec succès!');
      setFormData({});
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de la demande CSC');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDUM = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await integrationCamerounApi.creerDUM(formData);
      alert('DUM créé avec succès!');
      setFormData({});
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de la création du DUM');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAPE = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await integrationCamerounApi.creerAPE(formData);
      alert('APE créé avec succès!');
      setFormData({});
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de la création de l\'APE');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Intégration Cameroun</h1>
        <p className="text-gray-600 mt-2">Gestion des intégrations officielles Cameroun/CEMAC</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('bsc')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'bsc'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            BSC (Bulletin de Soumission Connaissement)
          </button>
          <button
            onClick={() => setActiveTab('csc')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'csc'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            CSC (Certificat de Sécurité)
          </button>
          <button
            onClick={() => setActiveTab('syged')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'syged'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            SYGED (Système de Gestion des Droits)
          </button>
          <button
            onClick={() => setActiveTab('ape')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'ape'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            APE (Arrêté de Paiement des Étrangers)
          </button>
        </nav>
      </div>

      {activeTab === 'bsc' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">BSC - Bulletin de Soumission Connaissement</h2>
          <p className="text-gray-600 mb-4">
            Génération et validation des BSC via l'API CNCC (Chambre de Commerce Cameroun)
          </p>
          
          <form onSubmit={handleCreateBSC}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Numéro de Connaissement</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: MSCD1234567"
                  value={formData.numero_connaisse || ''}
                  onChange={(e) => setFormData({...formData, numero_connaisse: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Navire</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: MSC CAMEROUN"
                  value={formData.navire || ''}
                  onChange={(e) => setFormData({...formData, navire: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nombre de Conteneurs</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: 10"
                  value={formData.nombre_conteneurs || ''}
                  onChange={(e) => setFormData({...formData, nombre_conteneurs: parseInt(e.target.value)})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Poids Total (tonnes)</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: 250"
                  value={formData.poids_total || ''}
                  onChange={(e) => setFormData({...formData, poids_total: parseFloat(e.target.value)})}
                />
              </div>
            </div>

            <button 
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Génération en cours...' : 'Générer BSC'}
            </button>
          </form>

          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-3">Derniers BSC</h3>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Numéro BSC</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Connaissement</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Navire</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">BSC-2026-001</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">MSCD1234567</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">MSC CAMEROUN</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">Validé</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">18/01/2026</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'csc' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">CSC - Certificat de Sécurité Cargaison</h2>
          <p className="text-gray-600 mb-4">
            Demande et validation des CSC via l'API INS (Inspection Nationale)
          </p>
          
          <form onSubmit={handleCreateCSC}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">BSC Référence</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="BSC-2026-001"
                  value={formData.bsc_id || ''}
                  onChange={(e) => setFormData({...formData, bsc_id: parseInt(e.target.value)})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date Inspection</label>
                <input
                  type="date"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  value={formData.date_inspection || ''}
                  onChange={(e) => setFormData({...formData, date_inspection: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Type Marchandise</label>
                <select 
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  value={formData.type_marchandise || ''}
                  onChange={(e) => setFormData({...formData, type_marchandise: e.target.value})}
                >
                  <option value="">Sélectionner...</option>
                  <option value="General">General</option>
                  <option value="Dangereux">Dangereux</option>
                  <option value="Refrigéré">Refrigéré</option>
                  <option value="Vrac">Vrac</option>
                </select>
              </div>
            </div>

            <button 
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Demande en cours...' : 'Demander CSC'}
            </button>
          </form>
        </div>
      )}

      {activeTab === 'syged' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">SYGED - Système de Gestion des Droits</h2>
          <p className="text-gray-600 mb-4">
            Création et gestion des DUM (Déclaration Unique de Marchandises) via SYGED
          </p>
          
          <form onSubmit={handleCreateDUM}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Navire</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: MSC CAMEROUN"
                  value={formData.navire || ''}
                  onChange={(e) => setFormData({...formData, navire: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Numéro Connaissement</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: MSCD1234567"
                  value={formData.numero_connaisse || ''}
                  onChange={(e) => setFormData({...formData, numero_connaisse: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Régime Douanier</label>
                <select 
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  value={formData.regime || ''}
                  onChange={(e) => setFormData({...formData, regime: e.target.value})}
                >
                  <option value="">Sélectionner...</option>
                  <option value="mise_a_la_consommation">Mise à la consommation</option>
                  <option value="transit">Transit</option>
                  <option value="admission_temporaire">Admission temporaire</option>
                  <option value="entrepot">Entrepôt</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Valeur CIF (FCFA)</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: 50000000"
                  value={formData.valeur_cif || ''}
                  onChange={(e) => setFormData({...formData, valeur_cif: parseFloat(e.target.value)})}
                />
              </div>
            </div>

            <button 
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Création en cours...' : 'Créer DUM'}
            </button>
          </form>
        </div>
      )}

      {activeTab === 'ape' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">APE - Arrêté de Paiement des Étrangers</h2>
          <p className="text-gray-600 mb-4">
            Gestion des transferts de devises via BEAC (Banque Centrale)
          </p>
          
          <form onSubmit={handleCreateAPE}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Navire</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: MSC CAMEROUN"
                  value={formData.navire || ''}
                  onChange={(e) => setFormData({...formData, navire: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date Arrivée</label>
                <input
                  type="date"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  value={formData.date_arrivee || ''}
                  onChange={(e) => setFormData({...formData, date_arrivee: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nombre Conteneurs</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: 10"
                  value={formData.nombre_conteneurs || ''}
                  onChange={(e) => setFormData({...formData, nombre_conteneurs: parseInt(e.target.value)})}
                />
              </div>
            </div>

            <button 
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Création en cours...' : 'Créer APE'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
