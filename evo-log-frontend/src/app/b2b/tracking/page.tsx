'use client';

import React, { useState } from 'react';
import {
  Search,
  Package,
  Ship,
  Truck,
  MapPin,
  Clock,
  ShieldCheck,
  CheckCircle2,
  Calendar,
  Download,
  AlertTriangle,
  ArrowRight,
  ChevronRight,
  Phone,
  Thermometer,
  FileText
} from 'lucide-react';
import { toast } from 'sonner';

export default function B2BTrackingPage() {
  const [searchCode, setSearchCode] = useState('MSKU7829104');
  const [activeTab, setActiveTab] = useState<'timeline' | 'details' | 'documents'>('timeline');

  // Shipment Detailed Data Model
  const shipmentDetail = {
    blNumber: 'CADC-BL-2026-880',
    containerNumber: 'MSKU7829104',
    sealNumber: 'SEAL-MAERSK-982104',
    type: "Conteneur 40' High Cube",
    grossWeight: '26,450 kg',
    cargoDescription: 'Équipements Industriels, Pièces Mécaniques & Moteurs Électriques',
    vesselName: 'MSC ILONA',
    voyageNumber: 'VOY-2026-44E',
    shippingLine: 'MSC Mediterranean Shipping Company',
    bookingRef: 'BKG-SH-99218',
    portOfLoading: 'Shanghai (Chine)',
    portOfDischarge: 'Douala (PAD Quai 14)',
    finalDestination: "N'Djamena (Tchad - Zone Industrielle Farcha)",
    consignee: 'Société Camerounaise d\'Import (SOCAM)',
    clearingAgent: 'CADC Transit & Douane Cameroun (Agrément CAD #0421)',
    currentStatus: 'EN_TRANSIT_ROUTIER',
    currentLocation: 'Poste de Contrôle & Pesée Bertoua (PK 340)',
    etaDestination: '04 Septembre 2026 à 14h00',
    freeTimeEnd: '12 Septembre 2026 (Franchise OK)',
    temperature: 'N/A (Marchandise Sèche)',
    driverInfo: {
      name: 'Aboubakar Ousmane',
      phone: '+237 699 82 10 33',
      truckPlate: 'LT TR 892 AF',
      trailerPlate: 'LT SR 410 AA',
    },
    timeline: [
      {
        step: 1,
        title: 'Chargement à Bord du Navire',
        location: 'Port de Shanghai (Terminal Yangshan)',
        date: '18 Juillet 2026 • 10:30',
        completed: true,
        details: 'Conteneur empoté et scellé. Connaissement B/L original émis.',
      },
      {
        step: 2,
        title: 'Arrivée sur Rade & Accostage Navire',
        location: 'Port Autonome de Douala (PAD - Quai 14)',
        date: '24 Août 2026 • 06:15',
        completed: true,
        details: 'Navire MSC ILONA à quai. Déchargement par grue portique RTC.',
      },
      {
        step: 3,
        title: 'Débarquement & Stockage Terre-Plein',
        location: 'Terminal à Conteneurs de Douala (RTC - Travée D-08)',
        date: '24 Août 2026 • 14:00',
        completed: true,
        details: 'Pointage acconage conforme. Émission du bon de déchargement.',
      },
      {
        step: 4,
        title: 'Dédouanement GUCE & Obtention BAE',
        location: 'Bureau Principal des Douanes Port I (Douala)',
        date: '26 Août 2026 • 16:45',
        completed: true,
        details: 'Déclaration DUM validée. Liquidation des droits payée. Bon à Enlever (BAE) accordé.',
      },
      {
        step: 5,
        title: 'Sortie du Port (Gate Out) & Pose Balise GPS Douane',
        location: 'Porte 3 PAD Douala',
        date: '28 Août 2026 • 09:10',
        completed: true,
        details: 'Passage pont-bascule (26.45T). Balise GPS douanière T1 activée.',
      },
      {
        step: 6,
        title: 'Transit Routier sur Corridor CEMAC (En Cours)',
        location: 'Axe Douala - Yaoundé - Bertoua - Ngaoundéré - N\'Djamena',
        date: '31 Août 2026 • En direct',
        completed: true,
        current: true,
        details: 'Camion en progression normale. Prochain pointage : Ngaoundéré gare.',
      },
      {
        step: 7,
        title: 'Passage Frontière Kousseri / N\'Gueli',
        location: 'Poste Frontière Cameroun - Tchad',
        date: 'Prévu : 03 Septembre 2026',
        completed: false,
        details: 'Apurement du titre de transit T1 et contrôle douanier de sortie.',
      },
      {
        step: 8,
        title: 'Livraison Finale & Signature e-POD',
        location: 'N\'Djamena (Entrepôt Client)',
        date: 'Prévu : 04 Septembre 2026',
        completed: false,
        details: 'Dépotage et signature électronique de la preuve de livraison e-POD.',
      }
    ]
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchCode.trim()) {
      toast.error('Veuillez entrer un numéro de conteneur ou de B/L');
      return;
    }
    toast.success(`Chargement des données de tracking pour : ${searchCode}`);
  };

  return (
    <div className="space-y-6">
      
      {/* Search Header Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-2">
              <Package className="w-6 h-6 text-amber-400" /> Suivi de Cargaison en Temps Réel
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Historique complet de la chaîne logistique maritime, douanière et terrestre
            </p>
          </div>

          <form onSubmit={handleSearch} className="flex items-center gap-2 w-full md:w-auto">
            <div className="relative flex-1 md:w-80">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchCode}
                onChange={(e) => setSearchCode(e.target.value)}
                placeholder="Ex: MSKU7829104 ou CADC-BL-2026-880"
                className="w-full h-11 pl-10 pr-4 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:border-amber-500"
              />
            </div>
            <button
              type="submit"
              className="h-11 px-5 bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-400 hover:to-yellow-300 text-slate-950 font-black text-xs rounded-xl shadow-lg shadow-amber-500/20 transition-all shrink-0"
            >
              Actualiser
            </button>
          </form>
        </div>
      </div>

      {/* Main Tracking Summary Card */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
        
        {/* Header Badges & Core Identification */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-2xl font-black font-mono text-amber-300">
                {shipmentDetail.containerNumber}
              </span>
              <span className="px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-bold font-mono">
                EN TRANSIT ROUTIER CEMAC
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 text-xs font-mono">
                B/L: {shipmentDetail.blNumber}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              {shipmentDetail.cargoDescription} • {shipmentDetail.type} • {shipmentDetail.grossWeight}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-right">
              <div className="text-[10px] uppercase font-mono text-slate-400">Estimation Livraison</div>
              <div className="text-sm font-black text-emerald-400 font-mono">{shipmentDetail.etaDestination}</div>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-right">
              <div className="text-[10px] uppercase font-mono text-slate-400">Franchise Portuaire</div>
              <div className="text-sm font-black text-amber-400 font-mono">{shipmentDetail.freeTimeEnd}</div>
            </div>
          </div>
        </div>

        {/* Route Map Header Bar */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-950/80 border border-slate-800/80 rounded-2xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-slate-800 text-slate-400"><Ship className="w-5 h-5" /></div>
            <div>
              <div className="text-[10px] font-mono text-slate-400 uppercase">Port d'Embarquement</div>
              <div className="text-xs font-bold text-slate-100">{shipmentDetail.portOfLoading}</div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400"><MapPin className="w-5 h-5" /></div>
            <div>
              <div className="text-[10px] font-mono text-slate-400 uppercase">Port de Déchargement</div>
              <div className="text-xs font-bold text-slate-100">{shipmentDetail.portOfDischarge}</div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400"><Truck className="w-5 h-5" /></div>
            <div>
              <div className="text-[10px] font-mono text-slate-400 uppercase">Destination Finale</div>
              <div className="text-xs font-bold text-slate-100">{shipmentDetail.finalDestination}</div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-slate-800 pt-2">
          <button
            onClick={() => setActiveTab('timeline')}
            className={`pb-3 px-4 text-xs font-bold border-b-2 transition-colors ${activeTab === 'timeline' ? 'border-amber-400 text-amber-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
          >
            Chronologie des Événements ({shipmentDetail.timeline.length} Étapes)
          </button>
          <button
            onClick={() => setActiveTab('details')}
            className={`pb-3 px-4 text-xs font-bold border-b-2 transition-colors ${activeTab === 'details' ? 'border-amber-400 text-amber-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
          >
            Fiche Technique & Chauffeur
          </button>
          <button
            onClick={() => setActiveTab('documents')}
            className={`pb-3 px-4 text-xs font-bold border-b-2 transition-colors ${activeTab === 'documents' ? 'border-amber-400 text-amber-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
          >
            Documents Attachés (B/L, BAE, DUM)
          </button>
        </div>

        {/* TAB 1: Complete Detailed Timeline */}
        {activeTab === 'timeline' && (
          <div className="space-y-6 pt-2">
            <div className="relative pl-6 sm:pl-8 space-y-6 before:absolute before:left-3 sm:before:left-4 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
              {shipmentDetail.timeline.map((item) => (
                <div key={item.step} className="relative group">
                  
                  {/* Step bullet */}
                  <div
                    className={`absolute -left-6 sm:-left-8 top-1 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold border ${
                      item.current
                        ? 'bg-amber-500 border-yellow-300 text-slate-950 ring-4 ring-amber-500/20 animate-pulse'
                        : item.completed
                        ? 'bg-emerald-500 border-emerald-400 text-slate-950'
                        : 'bg-slate-900 border-slate-700 text-slate-500'
                    }`}
                  >
                    {item.completed ? '✓' : item.step}
                  </div>

                  {/* Step Card Content */}
                  <div
                    className={`rounded-2xl p-4 border transition-all ${
                      item.current
                        ? 'bg-amber-500/10 border-amber-500/40 shadow-lg shadow-amber-500/10'
                        : item.completed
                        ? 'bg-slate-950/60 border-slate-800/80'
                        : 'bg-slate-950/30 border-slate-800/40 opacity-60'
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <h3 className={`text-sm font-bold ${item.current ? 'text-amber-300' : item.completed ? 'text-white' : 'text-slate-400'}`}>
                        {item.title}
                      </h3>
                      <span className="text-[11px] font-mono text-slate-400">{item.date}</span>
                    </div>

                    <div className="text-xs text-amber-400/90 font-medium mt-0.5 flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 shrink-0" /> {item.location}
                    </div>

                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      {item.details}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 2: Details & Driver Info */}
        {activeTab === 'details' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            
            {/* Logistics & Maritime Data */}
            <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-2">
                <Ship className="w-4 h-4 text-amber-400" /> Données Maritimes & Douanières
              </h3>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <span className="text-slate-500 block">Navire & Escale</span>
                  <span className="font-bold text-slate-200">{shipmentDetail.vesselName} ({shipmentDetail.voyageNumber})</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Compagnie Maritime</span>
                  <span className="font-bold text-slate-200">{shipmentDetail.shippingLine}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">N° Plomb / Scellé</span>
                  <span className="font-bold text-amber-300 font-mono">{shipmentDetail.sealNumber}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Commissionnaire Agréé</span>
                  <span className="font-bold text-slate-200">{shipmentDetail.clearingAgent}</span>
                </div>
              </div>
            </div>

            {/* Road Transport & Driver Dispatch */}
            <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-2">
                <Truck className="w-4 h-4 text-emerald-400" /> Dispatch Routier & Chauffeur Assuré
              </h3>

              <div className="space-y-3 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Chauffeur Titulaire</span>
                  <span className="font-bold text-slate-100">{shipmentDetail.driverInfo.name}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Téléphone Direct</span>
                  <a href={`tel:${shipmentDetail.driverInfo.phone}`} className="font-mono text-emerald-400 font-bold flex items-center gap-1 hover:underline">
                    <Phone className="w-3.5 h-3.5" /> {shipmentDetail.driverInfo.phone}
                  </a>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Immatriculation Tracteur</span>
                  <span className="font-mono font-bold text-amber-300 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    {shipmentDetail.driverInfo.truckPlate}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Immatriculation Semi-Remorque</span>
                  <span className="font-mono font-bold text-slate-300 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    {shipmentDetail.driverInfo.trailerPlate}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: Attached Official Documents */}
        {activeTab === 'documents' && (
          <div className="space-y-3 pt-2">
            <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-amber-400" />
                <div>
                  <div className="text-xs font-bold text-slate-200">Connaissement Maritime (Bill of Lading Original)</div>
                  <div className="text-[11px] text-slate-500 font-mono">CADC-BL-2026-880.pdf • 2.4 MB • Signé Électroniquement</div>
                </div>
              </div>
              <button
                onClick={() => toast.success('Téléchargement du Connaissement B/L démarré')}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl border border-slate-700 flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" /> Télécharger
              </button>
            </div>

            <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <div>
                  <div className="text-xs font-bold text-slate-200">Bon à Enlever Douane (BAE Officiel GUCE)</div>
                  <div className="text-[11px] text-slate-500 font-mono">BAE-2026-DLA-8902.pdf • 1.1 MB • Validé Bureau Port I</div>
                </div>
              </div>
              <button
                onClick={() => toast.success('Téléchargement du BAE Douane démarré')}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl border border-slate-700 flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" /> Télécharger
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
