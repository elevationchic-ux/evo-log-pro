'use client';

/**
 * Mouvements de parc — Gate In / Gate Out (saisie manuelle).
 *
 * Honnêteté (règle Zéro-Mock) : le bloc « Reconnaissance OCR / IA » a été
 * RETIRÉ. Le backend ne publie plus aucune route d'extraction optique
 * (`/parc/ocr-extract` a été supprimée : aucun moteur Tesseract n'est installé
 * côté serveur, elle renvoyait un 501). L'écran promettait pourtant « Analyse
 * IA en cours… », « Loading Tesseract engine… » et une « Fiabilité X% » :
 * c'était un contrôle mort qui échouait systématiquement puis retombait, sans
 * le dire, sur une saisie manuelle. On n'affiche plus que ce qui fonctionne
 * réellement : la déclaration manuelle d'une entrée ou d'une sortie.
 */
import React, { useState, useEffect } from 'react';
import { ModuleLayout } from '@/components/layout/ModuleLayout';
import { Truck, ShieldAlert } from 'lucide-react';
import { parcAPI } from '@/lib/api-client';
import { EmplacementParc } from '@/types/parc';
import { toast } from 'sonner';

export default function GateOperationsPage() {
  const [submitting, setSubmitting] = useState(false);
  const [mode, setMode] = useState<'IN' | 'OUT'>('IN');
  const [emplacements, setEmplacements] = useState<EmplacementParc[]>([]);

  const [form, setForm] = useState({
    numero_conteneur: '',
    type_conteneur: '20DRY',
    etat: 'BON_ETAT',
    poids_tare_kg: 2200,
    emplacement_id: 0,
  });

  useEffect(() => {
    parcAPI.getEmplacements().then(res => {
      setEmplacements(res.data.filter((e: any) => e.statut === 'LIBRE'));
    }).catch(() => {
      // Un échec de lecture est annoncé, pas avalé : la liste reste vide et
      // l'opérateur sait pourquoi aucun emplacement ne s'affiche.
      toast.error("Impossible de charger les emplacements du parc.");
    });
  }, []);

  const resetForm = () => setForm({
    numero_conteneur: '',
    type_conteneur: '20DRY',
    etat: 'BON_ETAT',
    poids_tare_kg: 2200,
    emplacement_id: 0,
  });

  const handleGateIn = async () => {
    if (!form.numero_conteneur || !form.emplacement_id) {
      toast.error("Veuillez remplir le numéro de conteneur et choisir un emplacement.");
      return;
    }
    setSubmitting(true);
    try {
      await parcAPI.gateIn({
        numero_conteneur: form.numero_conteneur,
        type_conteneur: form.type_conteneur,
        etat: form.etat,
        poids_tare_kg: form.poids_tare_kg,
        emplacement_id: form.emplacement_id,
      });
      toast.success("Gate In validé avec succès !");
      resetForm();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Erreur lors du Gate In");
    } finally {
      setSubmitting(false);
    }
  };

  const handleGateOut = async () => {
    if (!form.numero_conteneur) {
      toast.error("Veuillez remplir le numéro de conteneur.");
      return;
    }
    setSubmitting(true);
    try {
      await parcAPI.gateOut({ numero_conteneur: form.numero_conteneur });
      toast.success("Gate Out validé avec succès !");
      setForm(prev => ({ ...prev, numero_conteneur: '' }));
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Erreur lors du Gate Out");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ModuleLayout module="parc">
      <div className="max-w-2xl mx-auto py-8 px-4 animate-in fade-in duration-500">

        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-black text-slate-200 flex items-center gap-3">
              <Truck className="w-8 h-8 text-blue-600" />
              Mouvements de parc
            </h1>
            <p className="text-sm text-slate-500 mt-2">
              Déclaration manuelle des entrées (Gate In) et sorties (Gate Out) de conteneurs.
            </p>
          </div>
          <div className="flex bg-slate-900 p-1 rounded-xl">
            <button onClick={() => setMode('IN')} className={`px-4 py-2 text-sm font-bold rounded-lg transition-colors ${mode === 'IN' ? 'bg-slate-800 text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}>Gate IN</button>
            <button onClick={() => setMode('OUT')} className={`px-4 py-2 text-sm font-bold rounded-lg transition-colors ${mode === 'OUT' ? 'bg-slate-800 text-rose-600 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}>Gate OUT</button>
          </div>
        </div>

        {/* Formulaire de saisie */}
        <div className="bg-slate-900 rounded-3xl p-8 shadow-xl text-white relative overflow-hidden border border-slate-700">
          <div className="absolute top-0 right-0 opacity-10 transform translate-x-1/4 -translate-y-1/4">
            <ShieldAlert className="w-48 h-48" />
          </div>

          <h2 className="text-lg font-bold mb-6 flex items-center gap-2 relative z-10">
            <Truck className="w-5 h-5 text-blue-400" />
            {`Validation Gate ${mode}`}
          </h2>

          <div className="space-y-4 relative z-10">
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 block">N° Conteneur</label>
              <input type="text" value={form.numero_conteneur} onChange={e => setForm({ ...form, numero_conteneur: e.target.value })} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500" placeholder="Ex: MSKU1234567" />
            </div>

            {mode === 'IN' && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 block">Type</label>
                    <select value={form.type_conteneur} onChange={e => setForm({ ...form, type_conteneur: e.target.value })} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none">
                      <option value="20DRY">20' DRY</option>
                      <option value="40DRY">40' DRY</option>
                      <option value="20REEFER">20' REEFER</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 block">Etat</label>
                    <select value={form.etat} onChange={e => setForm({ ...form, etat: e.target.value })} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none">
                      <option value="BON_ETAT">Bon état</option>
                      <option value="ENDOMMAGE">Endommagé</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 block">Tare (kg)</label>
                  <input type="number" value={form.poids_tare_kg} onChange={e => setForm({ ...form, poids_tare_kg: Number(e.target.value) })} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500" />
                </div>

                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 block">Emplacement (Cour)</label>
                  <select value={form.emplacement_id} onChange={e => setForm({ ...form, emplacement_id: Number(e.target.value) })} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none">
                    <option value={0}>Sélectionnez un emplacement libre…</option>
                    {emplacements.map(e => (
                      <option key={e.id} value={e.id}>{e.code_emplacement}</option>
                    ))}
                  </select>
                  {emplacements.length === 0 && (
                    <p className="text-[11px] text-slate-500 mt-1">Aucun emplacement libre disponible actuellement.</p>
                  )}
                </div>
              </>
            )}

            <button
              onClick={mode === 'IN' ? handleGateIn : handleGateOut}
              disabled={submitting}
              className={`mt-8 w-full py-3 rounded-xl font-bold text-white transition-colors disabled:opacity-50 ${mode === 'IN' ? 'bg-emerald-600 hover:bg-emerald-500' : 'bg-rose-600 hover:bg-rose-500'}`}
            >
              {submitting ? 'Validation...' : `Valider le Gate ${mode}`}
            </button>
          </div>
        </div>

      </div>
    </ModuleLayout>
  );
}
