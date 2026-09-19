'use client';

import React, { useState, useEffect } from 'react';
import { ShoppingBag, Plus, Search, CheckCircle2, Clock, DollarSign, X } from 'lucide-react';
import { toast } from 'sonner';

export default function FinanceRequisitionsPage() {
  const [mounted, setMounted] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [supplier, setSupplier] = useState('');
  const [itemTitle, setItemTitle] = useState('');
  const [amount, setAmount] = useState('');
  const [department, setDepartment] = useState('MAGASIN');

  const [requisitions, setRequisitions] = useState([
    { id: 'PO-2026-041', title: 'Achat Lubrifiants Synthétiques 15W40 (20 Fûts)', department: 'WMS Magasin', amount: 3800000, supplier: 'TOTALENERGIES CAMEROUN', status: 'APPROUVÉ', date: '2026-07-22' },
    { id: 'PO-2026-042', title: 'Pièces de Rechange Grue Gottwald #2', department: 'Atelier Maintenance', amount: 8400000, supplier: 'KONECRANES AFRICA', status: 'EN_ATTENTE', date: '2026-07-23' },
    { id: 'PO-2026-043', title: 'Equipements EPI Sécurité Gilets & Casques', department: 'QHSE Port', amount: 1200000, supplier: 'SOCIÉTÉ CAMEROUNAISE DE SÉCURITÉ', status: 'APPROUVÉ', date: '2026-07-21' },
  ]);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="p-8 text-center text-slate-500 font-mono">Chargement des Demandes d'Achat PO...</div>;

  const handleCreatePO = (e: React.FormEvent) => {
    e.preventDefault();
    const newPO = {
      id: `PO-2026-0${requisitions.length + 44}`,
      title: itemTitle || 'Achat Fournitures Logistiques',
      department: department,
      amount: Number(amount) || 2500000,
      supplier: supplier || 'CFAO LOGISTICS',
      status: 'EN_ATTENTE',
      date: new Date().toISOString().split('T')[0],
    };
    setRequisitions([newPO, ...requisitions]);
    toast.success("Demande d'achat créée et soumise au DAF pour approbation !");
    setIsModalOpen(false);
    setItemTitle('');
    setSupplier('');
    setAmount('');
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500 text-slate-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-2 border border-emerald-500/20">
            <ShoppingBag className="w-3.5 h-3.5" />
            K-Finance & Procurement • Requisitions d'Achats (PO)
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Demandes d'Achat & Bon de Commande PO</h1>
          <p className="text-slate-400 text-sm mt-1">Gestion des réquisitions d'équipement, pièces détachées et validation budgétaire.</p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-emerald-600/30 transition-all hover:scale-[1.02] cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          Nouvelle Demande d'Achat PO
        </button>
      </div>

      {/* Requisitions List */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-bold text-slate-100 text-base">Historique des Demandes d'Achat PO</h3>
          <span className="text-xs font-mono text-slate-400">{requisitions.length} POs enregistrés</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">N° PO / Désignation</th>
                <th className="px-6 py-4">Département</th>
                <th className="px-6 py-4">Fournisseur Tiers</th>
                <th className="px-6 py-4 text-right">Montant TTC (XAF)</th>
                <th className="px-6 py-4 text-right">Statut DAF</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {requisitions.map((req) => (
                <tr key={req.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-6 py-4 font-bold text-slate-100">
                    <div className="text-emerald-400 font-mono text-xs">{req.id}</div>
                    <div className="text-slate-200 text-sm font-semibold">{req.title}</div>
                  </td>
                  <td className="px-6 py-4 text-slate-400 font-medium">
                    {req.department}
                  </td>
                  <td className="px-6 py-4 text-slate-300 font-medium">
                    {req.supplier}
                  </td>
                  <td className="px-6 py-4 text-right font-mono font-bold text-slate-100">
                    {req.amount.toLocaleString('fr-FR')} XAF
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${
                      req.status === 'APPROUVÉ'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {req.status === 'APPROUVÉ' ? <CheckCircle2 className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                      {req.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal New PO */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 text-white shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-lg font-bold">Créer une Demande d'Achat PO</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreatePO} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Désignation de la Demande</label>
                <input
                  type="text"
                  required
                  value={itemTitle}
                  onChange={(e) => setItemTitle(e.target.value)}
                  placeholder="ex: Achat de 10 Pneus 315/80 R22.5"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Département Demandeur</label>
                  <select
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                  >
                    <option value="MAGASIN">WMS Magasin</option>
                    <option value="TRANSPORT">Flotte Transport</option>
                    <option value="MAINTENANCE">Atelier Maintenance</option>
                    <option value="QHSE">Sécurité QHSE</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Montant Estimé (XAF)</label>
                  <input
                    type="number"
                    required
                    min={10000}
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="ex: 1500000"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Fournisseur Tiers</label>
                <input
                  type="text"
                  required
                  value={supplier}
                  onChange={(e) => setSupplier(e.target.value)}
                  placeholder="ex: CFAO LOGISTICS / TOTALENERGIES"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-400 hover:text-slate-200"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30"
                >
                  Soumettre la Requisition
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
