'use client';

import React, { useState, useEffect } from 'react';
import { Wrench, ArrowLeft, CheckCircle2, AlertTriangle, Truck } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function CreateWorkOrderPage() {
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  const [equipment, setEquipment] = useState('TRACTEUR_ACTROS_01');
  const [priority, setPriority] = useState('HAUTE');
  const [description, setDescription] = useState('');
  const [technician, setTechnician] = useState('MBIDA Jean-Baptiste (Atelier Central)');

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="p-8 text-center text-slate-500 font-mono">Chargement du Formulaire Work Order...</div>;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Ordre de travail Workshop créé avec succès !");
    router.push('/parc/worEVO-orders');
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-in fade-in duration-500 text-slate-100">
      {/* Header */}
      <div className="flex items-center justify-between bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.back()}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 text-xs font-semibold mb-1 border border-purple-500/20">
              <Wrench className="w-3.5 h-3.5" />
              EVO-Parc & Maintenance â€¢ CrÃ©ation d'Ordre de Travail (Work Order)
            </div>
            <h1 className="text-2xl font-black tracking-tight">Nouveau Work Order Workshop</h1>
          </div>
        </div>
      </div>

      {/* Form Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Ã‰quipement / Engin de Parc</label>
              <select
                value={equipment}
                onChange={(e) => setEquipment(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-purple-500"
              >
                <option value="TRACTEUR_ACTROS_01">Tracteur Actros 3344 (LT-802-AA)</option>
                <option value="GRUE_GOTTWALD_02">Grue Gottwald Quai #2</option>
                <option value="STACKER_KALMAR_05">Chariot Stacker Kalmar (45 Tonnes)</option>
                <option value="CAMION_MAN_04">Camion Remorque MAN TGS (LT-401-BB)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Niveau de PrioritÃ©</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-purple-500"
              >
                <option value="URGENTE">ðŸš¨ URGENTE (Immobilisation)</option>
                <option value="HAUTE">âš ï¸ HAUTE (Sous 24h)</option>
                <option value="NORMALE">â„¹ï¸ NORMALE (Entretien PÃ©riodique)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Technicien / Chef d'Atelier AssignÃ©</label>
            <input
              type="text"
              value={technician}
              onChange={(e) => setTechnician(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Description des RÃ©parations / Diagnostics</label>
            <textarea
              required
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Saisissez les dÃ©tails de la panne ou de l'entretien Ã  effectuer..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-purple-500"
            />
          </div>

          <div className="flex justify-end gap-4 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={() => router.back()}
              className="px-5 py-3 rounded-xl text-sm font-semibold text-slate-400 hover:text-slate-200"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="px-6 py-3 rounded-xl text-sm font-bold bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-600/30 transition-all cursor-pointer"
            >
              CrÃ©er le Work Order
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
