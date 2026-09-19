'use client';

import React, { useState, useEffect } from 'react';
import { ModuleLayout } from '@/components/layout/ModuleLayout';
import { ScanText, UploadCloud, Truck, CheckCircle2, ShieldAlert } from 'lucide-react';
import { parcAPI } from '@/lib/api-client';
import { EmplacementParc } from '@/types/parc';
import { toast } from 'sonner';

export default function GateOperationsPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);
  const [isManual, setIsManual] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [mode, setMode] = useState<'IN' | 'OUT'>('IN');
  const [emplacements, setEmplacements] = useState<EmplacementParc[]>([]);
  
  const [form, setForm] = useState({
    numero_conteneur: '',
    type_conteneur: '20DRY',
    etat: 'BON_ETAT',
    poids_tare_kg: 2200,
    emplacement_id: 0
  });

  useEffect(() => {
    parcAPI.getEmplacements().then(res => {
      setEmplacements(res.data.filter((e: any) => e.statut === 'LIBRE'));
    }).catch(console.error);
  }, []);

  const handleExtractOCR = async () => {
    if (!file) return;
    setIsScanning(true);
    try {
      const res = await parcAPI.extractOCR(file);
      setScanResult(res.data);
      setIsManual(true);
      setForm(prev => ({...prev, numero_conteneur: res.data.containerId}));
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Erreur lors de l'extraction OCR");
      // Fallback gracefull
      setIsManual(true);
    } finally {
      setIsScanning(false);
    }
  };

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
        emplacement_id: form.emplacement_id
      });
      toast.success("Gate In validé avec succès !");
      setScanResult(null);
      setFile(null);
      setIsManual(false);
      setForm({
        numero_conteneur: '',
        type_conteneur: '20DRY',
        etat: 'BON_ETAT',
        poids_tare_kg: 2200,
        emplacement_id: 0
      });
    } catch (err: any) {
      toast.error(err.message || "Erreur lors du Gate In");
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
      await parcAPI.gateOut({
        numero_conteneur: form.numero_conteneur,
      });
      toast.success("Gate Out validé avec succès !");
      setScanResult(null);
      setFile(null);
      setIsManual(false);
      setForm({
        ...form,
        numero_conteneur: '',
      });
    } catch (err: any) {
      toast.error(err.message || "Erreur lors du Gate Out");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ModuleLayout module="parc">
      <div className="max-w-4xl mx-auto py-8 px-4 animate-in fade-in duration-500">
        
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-black text-slate-900 flex items-center gap-3">
              <ScanText className="w-8 h-8 text-blue-600" />
              Gate Operations & IA (OCR)
            </h1>
            <p className="text-sm text-slate-500 mt-2">Reconnaissance optique des documents d'entrée/sortie du parc.</p>
          </div>
          <div className="flex bg-slate-100 p-1 rounded-xl">
            <button onClick={() => setMode('IN')} className={`px-4 py-2 text-sm font-bold rounded-lg transition-colors ${mode === 'IN' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>Gate IN</button>
            <button onClick={() => setMode('OUT')} className={`px-4 py-2 text-sm font-bold rounded-lg transition-colors ${mode === 'OUT' ? 'bg-white text-rose-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>Gate OUT</button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Upload Section */}
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-200">
            <h2 className="text-lg font-bold text-slate-800 mb-6">Scanner un Document</h2>
            
            <div className="border-2 border-dashed border-slate-300 rounded-2xl p-8 flex flex-col items-center justify-center text-center bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer mb-6" onClick={() => document.getElementById('file-upload')?.click()}>
              <input 
                id="file-upload" 
                type="file" 
                className="hidden" 
                accept="image/*"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              <UploadCloud className="w-12 h-12 text-slate-400 mb-4" />
              <p className="text-sm font-bold text-slate-700">Cliquez pour capturer ou uploader</p>
              <p className="text-xs text-slate-500 mt-1">BL, Interchange, ou Plaque Immatriculation</p>
              
              {file && (
                <div className="mt-4 px-4 py-2 bg-blue-100 text-blue-700 rounded-xl text-sm font-semibold">
                  Fichier sélectionné : {file.name}
                </div>
              )}
            </div>

            <button 
              onClick={handleExtractOCR}
              disabled={!file || isScanning}
              className={`w-full py-4 rounded-xl font-bold text-white shadow-lg transition-all flex items-center justify-center gap-2 mb-4 ${file && !isScanning ? 'bg-blue-600 hover:bg-blue-700' : 'bg-slate-300 cursor-not-allowed'}`}
            >
              {isScanning ? (
                <>
                  <ScanText className="w-5 h-5 animate-spin" /> Analyse IA en cours...
                </>
              ) : (
                <>Lancer la reconnaissance OCR</>
              )}
            </button>
            <button 
              onClick={() => setIsManual(true)}
              className="w-full py-4 rounded-xl font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors flex items-center justify-center gap-2"
            >
              Saisie Manuelle (Fallback)
            </button>
          </div>

          {/* Results Section */}
          <div className="bg-slate-900 rounded-3xl p-8 shadow-xl text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 opacity-10 transform translate-x-1/4 -translate-y-1/4">
              <ShieldAlert className="w-48 h-48" />
            </div>
            
            <h2 className="text-lg font-bold mb-6 flex items-center gap-2 relative z-10">
              <ScanText className="w-5 h-5 text-blue-400" />
              {isManual ? `Validation Gate ${mode}` : "Résultats de l'Extraction"}
            </h2>

            {isScanning ? (
              <div className="space-y-4 relative z-10">
                <div className="h-4 bg-slate-800 rounded animate-pulse w-3/4"></div>
                <div className="h-4 bg-slate-800 rounded animate-pulse w-1/2"></div>
                <div className="h-4 bg-slate-800 rounded animate-pulse w-5/6"></div>
                <p className="text-blue-400 text-sm mt-8 animate-pulse font-mono">Loading Tesseract engine...</p>
              </div>
            ) : isManual ? (
              <div className="space-y-4 relative z-10 animate-in slide-in-from-right duration-300">
                {scanResult && (
                  <div className="flex items-center gap-3 text-emerald-400 mb-6">
                    <CheckCircle2 className="w-6 h-6" />
                    <span className="font-bold">Extraction réussie (Fiabilité {scanResult.confidence}%)</span>
                  </div>
                )}
                
                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 block">N° Conteneur</label>
                  <input type="text" value={form.numero_conteneur} onChange={e => setForm({...form, numero_conteneur: e.target.value})} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500" placeholder="Ex: MSKU1234567" />
                </div>
                
                {mode === 'IN' && (
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 block">Type</label>
                        <select value={form.type_conteneur} onChange={e => setForm({...form, type_conteneur: e.target.value})} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none">
                          <option value="20DRY">20' DRY</option>
                          <option value="40DRY">40' DRY</option>
                          <option value="20REEFER">20' REEFER</option>
                        </select>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 block">Etat</label>
                        <select value={form.etat} onChange={e => setForm({...form, etat: e.target.value})} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none">
                          <option value="BON_ETAT">Bon état</option>
                          <option value="ENDOMMAGE">Endommagé</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 block">Emplacement (Cour)</label>
                      <select value={form.emplacement_id} onChange={e => setForm({...form, emplacement_id: Number(e.target.value)})} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none">
                        <option value={0}>Sélectionnez un emplacement libre...</option>
                        {emplacements.map(e => (
                          <option key={e.id} value={e.id}>{e.code_emplacement}</option>
                        ))}
                      </select>
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
            ) : (
              <div className="text-center text-slate-500 mt-12 relative z-10">
                <ScanText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Aucun document scanné.</p>
                <p className="text-sm mt-2">Uploadez une image pour que le moteur OCR en extraie les données.</p>
              </div>
            )}
          </div>

        </div>

      </div>
    </ModuleLayout>
  );
}
