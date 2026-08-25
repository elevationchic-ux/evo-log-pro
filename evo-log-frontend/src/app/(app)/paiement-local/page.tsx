'use client';

import { useState } from 'react';
import { paiementLocalApi } from '@/lib/api-cameroun';

export default function PaiementLocalPage() {
  const [selectedMethod, setSelectedMethod] = useState('orange');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paiementHistory, setPaiementHistory] = useState<any[]>([]);
  const [formData, setFormData] = useState<any>({});

  const handlePaiement = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      let result;
      if (selectedMethod === 'orange') {
        result = await paiementLocalApi.initierOrangeMoney(formData);
      } else if (selectedMethod === 'mtn') {
        result = await paiementLocalApi.initierMTN(formData);
      } else if (selectedMethod === 'virement') {
        result = await paiementLocalApi.initierVirement(formData);
      }
      setPaiementHistory([...paiementHistory, result.data]);
      setFormData({});
      alert('Paiement initié avec succès!');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de l\'initiation du paiement');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Paiements Locaux</h1>
        <p className="text-gray-600 mt-2">Gestion des paiements locaux Cameroun (Mobile Money, Banques)</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Méthodes de Paiement Disponibles</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => setSelectedMethod('orange')}
            className={`p-4 rounded-lg border-2 ${
              selectedMethod === 'orange'
                ? 'border-orange-500 bg-orange-50'
                : 'border-gray-200 hover:border-orange-300'
            }`}
          >
            <div className="text-3xl mb-2">🍊</div>
            <div className="font-semibold">Orange Money</div>
            <div className="text-sm text-gray-600">Paiement mobile Orange</div>
          </button>
          <button
            onClick={() => setSelectedMethod('mtn')}
            className={`p-4 rounded-lg border-2 ${
              selectedMethod === 'mtn'
                ? 'border-yellow-500 bg-yellow-50'
                : 'border-gray-200 hover:border-yellow-300'
            }`}
          >
            <div className="text-3xl mb-2">📱</div>
            <div className="font-semibold">MTN Mobile Money</div>
            <div className="text-sm text-gray-600">Paiement mobile MTN</div>
          </button>
          <button
            onClick={() => setSelectedMethod('virement')}
            className={`p-4 rounded-lg border-2 ${
              selectedMethod === 'virement'
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-blue-300'
            }`}
          >
            <div className="text-3xl mb-2">🏦</div>
            <div className="font-semibold">Virement Bancaire</div>
            <div className="text-sm text-gray-600">Banques locales</div>
          </button>
        </div>
      </div>

      {selectedMethod === 'orange' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Paiement Orange Money</h2>
          
          <form onSubmit={handlePaiement}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Numéro Orange</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: 699123456"
                  value={formData.numero || ''}
                  onChange={(e) => setFormData({...formData, numero: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Montant (FCFA)</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: 50000"
                  value={formData.montant || ''}
                  onChange={(e) => setFormData({...formData, montant: parseFloat(e.target.value)})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Référence</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: PAY-2026-001"
                  value={formData.reference || ''}
                  onChange={(e) => setFormData({...formData, reference: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: Paiement facture"
                  value={formData.description || ''}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                />
              </div>
            </div>

            <button 
              type="submit"
              className="bg-orange-600 text-white px-4 py-2 rounded-md hover:bg-orange-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Initiation en cours...' : 'Initier Paiement Orange Money'}
            </button>
          </form>
        </div>
      )}

      {selectedMethod === 'mtn' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Paiement MTN Mobile Money</h2>
          
          <form onSubmit={handlePaiement}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Numéro MTN</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: 677987654"
                  value={formData.numero || ''}
                  onChange={(e) => setFormData({...formData, numero: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Montant (FCFA)</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: 75000"
                  value={formData.montant || ''}
                  onChange={(e) => setFormData({...formData, montant: parseFloat(e.target.value)})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Référence</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: PAY-2026-002"
                  value={formData.reference || ''}
                  onChange={(e) => setFormData({...formData, reference: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: Paiement services"
                  value={formData.description || ''}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                />
              </div>
            </div>

            <button 
              type="submit"
              className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Initiation en cours...' : 'Initier Paiement MTN Mobile Money'}
            </button>
          </form>
        </div>
      )}

      {selectedMethod === 'virement' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Virement Bancaire</h2>
          
          <form onSubmit={handlePaiement}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Banque</label>
                <select 
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  value={formData.banque || ''}
                  onChange={(e) => setFormData({...formData, banque: e.target.value})}
                >
                  <option value="">Sélectionner...</option>
                  <option value="SG">Société Générale Cameroun</option>
                  <option value="BICEC">BICEC</option>
                  <option value="AFRILAND">Afriland First Bank</option>
                  <option value="SCB">SCB Cameroun</option>
                  <option value="ECOBANK">Ecobank Cameroun</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Compte Bancaire</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: CM0012345678901234567890123"
                  value={formData.compte || ''}
                  onChange={(e) => setFormData({...formData, compte: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Montant (FCFA)</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: 100000"
                  value={formData.montant || ''}
                  onChange={(e) => setFormData({...formData, montant: parseFloat(e.target.value)})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Bénéficiaire</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: Entreprise ABC"
                  value={formData.beneficiaire || ''}
                  onChange={(e) => setFormData({...formData, beneficiaire: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Référence</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: VIR-2026-001"
                  value={formData.reference || ''}
                  onChange={(e) => setFormData({...formData, reference: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Motif</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ex: Paiement facture"
                  value={formData.motif || ''}
                  onChange={(e) => setFormData({...formData, motif: e.target.value})}
                />
              </div>
            </div>

            <button 
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Initiation en cours...' : 'Initier Virement'}
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 mt-6">
        <h2 className="text-xl font-semibold mb-4">Historique des Paiements</h2>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Référence</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Méthode</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Montant</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bénéficiaire</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            <tr>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">PAY-2026-001</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Orange Money</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">50 000 FCFA</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">699123456</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">Réussi</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">18/01/2026</td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">PAY-2026-002</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">MTN Mobile Money</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">75 000 FCFA</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">677987654</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">Réussi</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">18/01/2026</td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">VIR-2026-001</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Virement</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">100 000 FCFA</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Entreprise ABC</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-yellow-600">En attente</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">18/01/2026</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
