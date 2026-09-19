'use client';

import React, { useState, useEffect } from 'react';
import { 
  Award, 
  Plus, 
  Search, 
  Filter, 
  Star, 
  CheckCircle2, 
  Percent, 
  TrendingUp, 
  Gift, 
  Building2,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';

interface LoyaltyAccount {
  id: string;
  clientNom: string;
  palier: 'PLATINUM' | 'GOLD' | 'SILVER' | 'STANDARD';
  volumesCumulesTeu: number;
  tauxRistourneRfa: number;
  joursFranchiseOfferts: number;
  gestionnaireDedie: string;
  statut: 'ACTIF' | 'SUSPENDU';
}

export default function ClientB2bLoyaltyPage() {
  const [accounts, setAccounts] = useState<LoyaltyAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  const [form, setForm] = useState({
    clientNom: '',
    palier: 'GOLD',
    volumesCumulesTeu: 250,
    tauxRistourneRfa: 3.5,
    joursFranchiseOfferts: 5,
    gestionnaireDedie: 'Service Grands Comptes CADC'
  });

  const handleCreateLoyalty = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.clientNom) {
      toast.error('Veuillez renseigner le nom du client.');
      return;
    }

    const created: LoyaltyAccount = {
      id: Date.now().toString(),
      clientNom: form.clientNom,
      palier: form.palier as any,
      volumesCumulesTeu: Number(form.volumesCumulesTeu) || 0,
      tauxRistourneRfa: Number(form.tauxRistourneRfa) || 0,
      joursFranchiseOfferts: Number(form.joursFranchiseOfferts) || 0,
      gestionnaireDedie: form.gestionnaireDedie,
      statut: 'ACTIF'
    };

    setAccounts([created, ...accounts]);
    setShowAddModal(false);
    setForm({
      clientNom: '',
      palier: 'GOLD',
      volumesCumulesTeu: 250,
      tauxRistourneRfa: 3.5,
      joursFranchiseOfferts: 5,
      gestionnaireDedie: 'Service Grands Comptes CADC'
    });
    toast.success(`Barème de fidélisation RFA activé pour ${created.clientNom}.`);
  };

  const filteredAccounts = accounts.filter(a => 
    a.clientNom.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Programme Fidélisation & Ristournes RFA</h1>
            <p className="text-sm text-on-surface-variant">
              Paliers de volumes maritimes (EVP), ristournes de fin d'année et franchises de stationnement bonus
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-95 transition-opacity"
        >
          <Plus className="w-4 h-4" />
          Configurer Compte Fidélité
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-surface border border-outline rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher par nom de client..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-surface-container-low border border-outline text-xs rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>
      </div>

      {/* Table / Clean Slate State */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
        {filteredAccounts.length === 0 ? (
          <div className="p-12 text-center">
            <Award className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
            <h3 className="font-semibold text-on-surface text-base">Aucun compte fidélité ou barème RFA paramétré</h3>
            <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto mb-4">
              Récompensez vos plus gros chargeurs en configurant des seuils de volumes en conteneurs (TEU) avec des ristournes financières et des jours de franchise conteneur offerts.
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold text-xs hover:opacity-95"
            >
              + Paramétrer le Premier Compte
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-surface-container-low border-b border-outline uppercase font-semibold text-on-surface-variant">
                  <th className="p-3 pl-5">Client Chargeur</th>
                  <th className="p-3">Palier VIP</th>
                  <th className="p-3 text-right">Volume Traité (EVP)</th>
                  <th className="p-3 text-right">Taux RFA (%)</th>
                  <th className="p-3 text-center">Franchise Bonus</th>
                  <th className="p-3">Gestionnaire Dédié</th>
                  <th className="p-3 text-right pr-5">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline/40">
                {filteredAccounts.map(a => (
                  <tr key={a.id} className="hover:bg-surface-container transition-colors">
                    <td className="p-3 pl-5 font-bold text-on-surface">{a.clientNom}</td>
                    <td className="p-3">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        a.palier === 'PLATINUM' ? 'bg-purple-500/10 text-purple-600' :
                        a.palier === 'GOLD' ? 'bg-amber-500/10 text-amber-600' :
                        a.palier === 'SILVER' ? 'bg-slate-500/10 text-slate-600' :
                        'bg-surface-container text-on-surface-variant'
                      }`}>
                        {a.palier}
                      </span>
                    </td>
                    <td className="p-3 text-right font-mono font-bold text-on-surface">{a.volumesCumulesTeu} EVP</td>
                    <td className="p-3 text-right font-mono font-bold text-primary">{a.tauxRistourneRfa}%</td>
                    <td className="p-3 text-center font-mono font-semibold text-emerald-600">+{a.joursFranchiseOfferts} jours</td>
                    <td className="p-3 text-on-surface">{a.gestionnaireDedie}</td>
                    <td className="p-3 text-right pr-5">
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 font-bold text-[10px]">
                        {a.statut}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-md p-6 space-y-4 shadow-xl">
            <div className="flex justify-between items-center border-b border-outline pb-3">
              <h3 className="font-bold text-on-surface text-base">Configurer un Barème RFA / Fidélité</h3>
              <button onClick={() => setShowAddModal(false)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <form onSubmit={handleCreateLoyalty} className="space-y-3 text-xs">
              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Raison Sociale du Client * :</label>
                <input
                  type="text"
                  placeholder="Ex: CHOCOCAM / NESTLÉ"
                  value={form.clientNom}
                  onChange={(e) => setForm({ ...form, clientNom: e.target.value })}
                  required
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-semibold focus:outline-none focus:border-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Palier VIP :</label>
                  <select
                    value={form.palier}
                    onChange={(e) => setForm({ ...form, palier: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  >
                    <option value="PLATINUM">Platinum (&gt; 1 000 EVP)</option>
                    <option value="GOLD">Gold (&gt; 500 EVP)</option>
                    <option value="SILVER">Silver (&gt; 200 EVP)</option>
                    <option value="STANDARD">Standard</option>
                  </select>
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Taux RFA Annuel (%) :</label>
                  <input
                    type="number"
                    step="0.5"
                    value={form.tauxRistourneRfa}
                    onChange={(e) => setForm({ ...form, tauxRistourneRfa: Number(e.target.value) })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Volume Actuel (EVP) :</label>
                  <input
                    type="number"
                    value={form.volumesCumulesTeu}
                    onChange={(e) => setForm({ ...form, volumesCumulesTeu: Number(e.target.value) })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Jours Franchise Offerts :</label>
                  <input
                    type="number"
                    value={form.joursFranchiseOfferts}
                    onChange={(e) => setForm({ ...form, joursFranchiseOfferts: Number(e.target.value) })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-outline rounded-xl text-on-surface hover:bg-surface-container font-semibold"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold hover:opacity-90"
                >
                  Activer les Avantages
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
