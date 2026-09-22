'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { transportAPI } from '@/lib/api-client';
import { Mission } from '@/types';
import { Printer, ArrowLeft, Download, ShieldCheck, Truck, MapPin } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function DocumentBLPage() {
  const params = useParams();
  const router = useRouter();
  const missionId = parseInt(params.id as string);
  
  const [mission, setMission] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadMissionData = useCallback(async () => {
    try {
      setLoading(true);
      const res = await transportAPI.getMission(missionId);
      setMission(res.data);
    } catch (err) {
      console.error('Failed to load mission for BL', err);
    } finally {
      setLoading(false);
    }
  }, [missionId]);

  useEffect(() => {
    if (missionId) {
      loadMissionData();
    }
  }, [missionId, loadMissionData]);

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="animate-spin w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!mission) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center flex-col gap-4">
        <h2 className="text-xl font-bold text-slate-800">Document Introuvable</h2>
        <button onClick={() => router.back()} className="text-blue-600 hover:underline">Retour</button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 py-8 print:bg-white print:p-0">
      
      {/* ─── Control Bar (Hidden in Print) ─── */}
      <div className="max-w-4xl mx-auto mb-6 flex items-center justify-between print:hidden">
        <button 
          onClick={() => router.back()}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
        >
          <ArrowLeft className="w-4 h-4" /> Retour
        </button>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={handlePrint}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 rounded-xl text-sm font-bold text-white hover:bg-blue-700 transition-colors shadow-sm"
          >
            <Printer className="w-4 h-4" /> Imprimer / PDF
          </button>
        </div>
      </div>

      {/* ─── A4 Document Container ─── */}
      <div className="max-w-4xl mx-auto bg-white shadow-xl print:shadow-none print:max-w-none print:w-full">
        
        {/* Document Body */}
        <div className="p-12 print:p-6" style={{ minHeight: '297mm' }}>
          
          {/* Header */}
          <div className="flex justify-between items-start border-b-2 border-slate-800 pb-8 mb-8">
            <div>
              <h1 className="text-4xl font-black text-slate-900 tracking-tighter mb-2">EVO-LOG</h1>
              <p className="text-sm font-bold text-slate-600 tracking-widest uppercase">Enterprise Management ERP</p>
              <div className="mt-4 text-xs text-slate-500 space-y-1">
                <p>Port Autonome de Douala, Cameroun</p>
                <p>Tel: +237 200 00 00 00</p>
                <p>Email: dispatch@evo-log.cm</p>
              </div>
            </div>
            <div className="text-right">
              <h2 className="text-3xl font-bold text-slate-800 mb-2 uppercase tracking-wide">Bon de Livraison</h2>
              <div className="bg-slate-100 inline-block px-4 py-2 rounded-lg border border-slate-200">
                <p className="text-xs text-slate-500 uppercase font-bold mb-1">RÉFÉRENCE OT</p>
                <p className="text-xl font-black text-blue-700">{mission.reference}</p>
              </div>
              <p className="text-sm mt-4 text-slate-600">
                <span className="font-bold">Date d'émission:</span> {format(new Date(), 'dd MMMM yyyy', { locale: fr })}
              </p>
            </div>
          </div>

          {/* Client & Entities */}
          <div className="grid grid-cols-2 gap-8 mb-10">
            <div className="bg-slate-50 p-5 rounded-xl border border-slate-100">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4" /> Entité de Facturation (Client)
              </p>
              <h3 className="text-lg font-bold text-slate-800">{mission.tiers?.raison_sociale || `Client ID: ${mission.tiers_id}`}</h3>
              {mission.tiers?.niu && <p className="text-sm text-slate-600 mt-1">NIU: {mission.tiers.niu}</p>}
            </div>
            
            <div className="bg-slate-50 p-5 rounded-xl border border-slate-100">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <MapPin className="w-4 h-4" /> Détails d'Expédition
              </p>
              <div className="space-y-2 text-sm text-slate-700">
                <p><span className="font-semibold text-slate-500">Expéditeur:</span> {mission.expediteur_adresse || 'Non spécifié'}</p>
                <p><span className="font-semibold text-slate-500">Destinataire:</span> {mission.destinataire_adresse || 'Non spécifié'}</p>
                <p><span className="font-semibold text-slate-500">Contact Site:</span> {mission.contact_site || 'Non spécifié'}</p>
              </div>
            </div>
          </div>

          {/* Route & Cargo Details */}
          <div className="mb-10">
            <h3 className="text-lg font-bold text-slate-800 border-b border-slate-200 pb-2 mb-4">Itinéraire & Marchandise</h3>
            <table className="w-full text-left text-sm border border-slate-200 rounded-lg overflow-hidden">
              <thead className="bg-slate-100 text-slate-600 font-semibold uppercase text-xs">
                <tr>
                  <th className="p-3 border-b border-slate-200">Origine</th>
                  <th className="p-3 border-b border-slate-200">Destination</th>
                  <th className="p-3 border-b border-slate-200">Nature du Fret</th>
                  <th className="p-3 border-b border-slate-200 text-right">Distance</th>
                  <th className="p-3 border-b border-slate-200 text-right">Poids / Vol</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                <tr>
                  <td className="p-3 font-medium text-slate-800">{mission.origine}</td>
                  <td className="p-3 font-medium text-slate-800">{mission.destination}</td>
                  <td className="p-3">{mission.nature_fret.replace(/_/g, ' ')}</td>
                  <td className="p-3 text-right">{mission.distance_km} km</td>
                  <td className="p-3 text-right">
                    {mission.poids_kg ? `${mission.poids_kg} Kg` : ''} 
                    {mission.volume_m3 ? ` / ${mission.volume_m3} m³` : ''}
                    {!mission.poids_kg && !mission.volume_m3 && 'N/A'}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Execution Resources */}
          <div className="mb-12">
            <h3 className="text-lg font-bold text-slate-800 border-b border-slate-200 pb-2 mb-4">Ressources Allouées (Gate Out)</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-4 p-4 border border-slate-200 rounded-xl">
                <div className="p-3 bg-blue-50 text-blue-600 rounded-lg"><Truck className="w-6 h-6" /></div>
                <div>
                  <p className="text-xs text-slate-500 font-bold uppercase">Véhicule (Tracteur)</p>
                  <p className="text-base font-bold text-slate-900">{mission.camion?.immatriculation || `ID: ${mission.camion_id}`}</p>
                  <p className="text-xs text-slate-600">{mission.camion?.marque} {mission.camion?.modele}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-4 p-4 border border-slate-200 rounded-xl">
                <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg">
                  <span className="material-symbols-outlined text-[24px]">badge</span>
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-bold uppercase">Chauffeur Principal</p>
                  <p className="text-base font-bold text-slate-900">
                    {mission.chauffeur ? `${mission.chauffeur.nom} ${mission.chauffeur.prenoms}` : `ID: ${mission.chauffeur_id}`}
                  </p>
                  <p className="text-xs text-slate-600">{mission.chauffeur?.telephone || 'Non spécifié'}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Signatures Area */}
          <div className="mt-16 pt-8 border-t-2 border-slate-100">
            <div className="grid grid-cols-3 gap-8">
              <div className="text-center">
                <p className="text-sm font-bold text-slate-700 mb-20">Visa Expéditeur / Gate Out</p>
                <div className="border-t border-slate-300 w-3/4 mx-auto"></div>
                <p className="text-xs text-slate-400 mt-2">Date & Signature</p>
              </div>
              <div className="text-center">
                <p className="text-sm font-bold text-slate-700 mb-20">Visa Chauffeur</p>
                <div className="border-t border-slate-300 w-3/4 mx-auto"></div>
                <p className="text-xs text-slate-400 mt-2">Date & Signature</p>
              </div>
              <div className="text-center">
                <p className="text-sm font-bold text-slate-700 mb-20">Visa Destinataire</p>
                <div className="border-t border-slate-300 w-3/4 mx-auto"></div>
                <p className="text-xs text-slate-400 mt-2">Date, Signature & Cachet</p>
              </div>
            </div>
          </div>

          {/* Footer Footer */}
          <div className="mt-12 text-center text-[10px] text-slate-400 uppercase tracking-widest">
            <p>Document généré par le module K-Docs de EVO-LOG ERP.</p>
            <p>Ce bon de livraison fait foi en cas de litige concernant les marchandises transportées.</p>
          </div>

        </div>
      </div>

    </div>
  );
}
