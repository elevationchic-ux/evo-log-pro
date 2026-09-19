'use client';

import React, { useState } from 'react';
import {
  FileCheck, Search, Filter, Download, Camera,
  CheckCircle2, AlertTriangle, MapPin, Calendar, Clock, PenTool, ShieldCheck
} from 'lucide-react';
import { toast } from 'sonner';

interface EPODRecord {
  id: string;
  missionCode: string;
  client: string;
  recipientName: string;
  destination: string;
  deliveryDate: string;
  containerNumber: string;
  sealNumber: string;
  sealIntact: boolean;
  hasSignature: boolean;
  photoCount: number;
  status: 'VALIDE_CONFORME' | 'RESERVES_EMISES' | 'EN_ATTENTE_SIGNATURE';
}

const EPOD_DATA: EPODRecord[] = [
  { id: '1', missionCode: 'TR-2026-0939', client: 'SABC Boissons', recipientName: 'M. Tagne (Resp. Quai)', destination: 'Yaoundé Usine', deliveryDate: '27/08/2026 11:30', containerNumber: 'MSCU1029384', sealNumber: 'SL-884920', sealIntact: true, hasSignature: true, photoCount: 4, status: 'VALIDE_CONFORME' },
  { id: '2', missionCode: 'TR-2026-0935', client: 'TOTAL Cameroun', recipientName: 'M. Amadou (Chef Dépôt)', destination: 'N\'Djamena Dépôt', deliveryDate: '26/08/2026 16:45', containerNumber: 'CMAU9482011', sealNumber: 'SL-772910', sealIntact: true, hasSignature: true, photoCount: 6, status: 'VALIDE_CONFORME' },
  { id: '3', missionCode: 'TR-2026-0932', client: 'Centrafrique Mining Transit', recipientName: 'M. Zola', destination: 'Bangui PK12', deliveryDate: '25/08/2026 09:15', containerNumber: 'SUDU8492018', sealNumber: 'SL-993821', sealIntact: false, hasSignature: true, photoCount: 8, status: 'RESERVES_EMISES' },
];

export default function TransportFlotteTrackingEPOD() {
  const [records, setRecords] = useState<EPODRecord[]>(EPOD_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = records.filter(r =>
    r.missionCode.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.client.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.containerNumber.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-blue-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-blue-500/20 text-blue-300 border border-blue-500/30">
              Preuve Électronique de Livraison (e-POD)
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KTRN_POD
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <FileCheck className="w-8 h-8 text-blue-400" />
            e-POD & Preuves de Livraison
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Capture de signatures électroniques, photos de scellés/conteneurs à l arrivée et procès-verbaux de réception.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.success('Bordereaux e-POD certifiés exportés en archive PDF')}
            className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-blue-500/25 transition-all cursor-pointer"
          >
            <Download className="w-4 h-4" /> Exporter Dossiers e-POD
          </button>
        </div>
      </div>

      {/* Table e-POD */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par mission, client, conteneur..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Mission</th>
                <th className="py-3.5 px-4">Client & Destination</th>
                <th className="py-3.5 px-4">Réceptionnaire</th>
                <th className="py-3.5 px-4">N° Conteneur & Scellé</th>
                <th className="py-3.5 px-4 text-center">Scellé Intact</th>
                <th className="py-3.5 px-4 text-center">Signature & Photos</th>
                <th className="py-3.5 px-4 text-center">Statut e-POD</th>
                <th className="py-3.5 px-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(r => (
                <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-blue-400">{r.missionCode}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-sans text-slate-100 font-semibold">{r.client}</div>
                    <div className="text-[11px] text-slate-400 flex items-center gap-1"><MapPin className="w-3 h-3 text-red-400" /> {r.destination}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{r.recipientName}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-slate-200">{r.containerNumber}</div>
                    <div className="text-[11px] text-slate-400 font-mono">Scellé: {r.sealNumber}</div>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    {r.sealIntact ? (
                      <span className="text-emerald-400 font-bold flex items-center justify-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Oui</span>
                    ) : (
                      <span className="text-red-400 font-bold flex items-center justify-center gap-1"><AlertTriangle className="w-3.5 h-3.5" /> Brisé</span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 text-[10px] border border-blue-500/20">
                      ✍️ Signé • 📷 {r.photoCount} photos
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      r.status === 'VALIDE_CONFORME' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      'bg-red-500/10 text-red-400 border border-red-500/20'
                    }`}>
                      {r.status === 'VALIDE_CONFORME' ? '✓ Conforme' : '⚠️ Réserves'}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <button
                      onClick={() => toast.success(`Affichage du procès-verbal e-POD ${r.missionCode}`)}
                      className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-blue-300 font-bold text-[10px] rounded-lg border border-slate-700"
                    >
                      Consulter
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
