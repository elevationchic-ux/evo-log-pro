'use client';

import { useState } from 'react';
import { toast } from 'sonner';
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
      toast.success('Paiement initié avec succès.');
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
        <h1 className="text-3xl font-bold text-white">Paiements Locaux</h1>
        <p className="text-slate-400 mt-2">Gestion des paiements locaux Cameroun (Mobile Money, Banques)</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-500/10 border border-red-700 text-red-300 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4 text-white">Méthodes de Paiement Disponibles</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => setSelectedMethod('orange')}
            className={`p-4 rounded-lg border-2 ${selectedMethod === 'orange'
                ? 'border-orange-500 bg-orange-500/10'
                : 'border-slate-700 hover:border-orange-500/60'
              }`}
          >
            <div className="text-3xl mb-2">🍊</div>
            <div className="font-semibold">Orange Money</div>
            <div className="text-sm text-slate-400">Paiement mobile Orange</div>
          </button>
          <button
            onClick={() => setSelectedMethod('mtn')}
            className={`p-4 rounded-lg border-2 ${selectedMethod === 'mtn'
                ? 'border-yellow-500 bg-yellow-500/10'
                : 'border-slate-700 hover:border-yellow-500/60'
              }`}
          >
            <div className="text-3xl mb-2">📱</div>
            <div className="font-semibold">MTN Mobile Money</div>
            <div className="text-sm text-slate-400">Paiement mobile MTN</div>
          </button>
          <button
            onClick={() => setSelectedMethod('virement')}
            className={`p-4 rounded-lg border-2 ${selectedMethod === 'virement'
                ? 'border-blue-500 bg-blue-500/10'
                : 'border-slate-700 hover:border-blue-500/60'
              }`}
          >
            <div className="text-3xl mb-2">🏦</div>
            <div className="font-semibold">Virement Bancaire</div>
            <div className="text-sm text-slate-400">Banques locales</div>
          </button>
        </div>
      </div>

      {selectedMethod === 'orange' && (
        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Paiement Orange Money</h2>

          <form onSubmit={handlePaiement}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Numéro Orange</label>
                <input
                  type="text"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: 699123456"
                  value={formData.numero || ''}
                  onChange={(e) => setFormData({ ...formData, numero: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Montant (FCFA)</label>
                <input
                  type="number"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: 50000"
                  value={formData.montant || ''}
                  onChange={(e) => setFormData({ ...formData, montant: parseFloat(e.target.value) })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Référence</label>
                <input
                  type="text"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: PAY-2026-001"
                  value={formData.reference || ''}
                  onChange={(e) => setFormData({ ...formData, reference: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Description</label>
                <input
                  type="text"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: Paiement facture"
                  value={formData.description || ''}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
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
        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Paiement MTN Mobile Money</h2>

          <form onSubmit={handlePaiement}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Numéro MTN</label>
                <input
                  type="text"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: 677987654"
                  value={formData.numero || ''}
                  onChange={(e) => setFormData({ ...formData, numero: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Montant (FCFA)</label>
                <input
                  type="number"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: 75000"
                  value={formData.montant || ''}
                  onChange={(e) => setFormData({ ...formData, montant: parseFloat(e.target.value) })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Référence</label>
                <input
                  type="text"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: PAY-2026-002"
                  value={formData.reference || ''}
                  onChange={(e) => setFormData({ ...formData, reference: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Description</label>
                <input
                  type="text"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: Paiement services"
                  value={formData.description || ''}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
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
        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Virement Bancaire</h2>

          <form onSubmit={handlePaiement}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Banque</label>
                <select
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  value={formData.banque || ''}
                  onChange={(e) => setFormData({ ...formData, banque: e.target.value })}
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
                <label className="block text-sm font-medium text-slate-300 mb-2">Compte Bancaire</label>
                <input
                  type="text"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: CM0012345678901234567890123"
                  value={formData.compte || ''}
                  onChange={(e) => setFormData({ ...formData, compte: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Montant (FCFA)</label>
                <input
                  type="number"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: 100000"
                  value={formData.montant || ''}
                  onChange={(e) => setFormData({ ...formData, montant: parseFloat(e.target.value) })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Bénéficiaire</label>
                <input
                  type="text"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: Entreprise ABC"
                  value={formData.beneficiaire || ''}
                  onChange={(e) => setFormData({ ...formData, beneficiaire: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Référence</label>
                <input
                  type="text"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: VIR-2026-001"
                  value={formData.reference || ''}
                  onChange={(e) => setFormData({ ...formData, reference: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Motif</label>
                <input
                  type="text"
                  className="w-full bg-slate-800 border border-slate-600 text-slate-100 placeholder:text-slate-500 rounded-md px-3 py-2"
                  placeholder="Ex: Paiement facture"
                  value={formData.motif || ''}
                  onChange={(e) => setFormData({ ...formData, motif: e.target.value })}
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

      <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 mt-6 overflow-x-auto">
        <h2 className="text-xl font-semibold mb-4 text-white">Historique des Paiements</h2>
        {paiementHistory.length === 0 ? (
          <p className="text-slate-500 text-sm text-center py-8">Aucun paiement enregistré pour le moment.</p>
        ) : (
          <table className="min-w-full divide-y divide-slate-700">
            <thead className="bg-slate-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Référence</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Méthode</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Montant</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Bénéficiaire</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Statut</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {paiementHistory.map((p: any, idx: number) => (
                <tr key={p.id || idx}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">{p.reference || p.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">{p.methode || selectedMethod}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">{p.montant} FCFA</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">{p.numero || p.beneficiaire || ''}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-emerald-400">{p.statut || 'Initié'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">{p.date ? new Date(p.date).toLocaleDateString('fr-FR') : ''}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
