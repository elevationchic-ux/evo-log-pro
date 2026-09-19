'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Ship,
  Package,
  Truck,
  Clock,
  AlertTriangle,
  CheckCircle2,
  FileText,
  CreditCard,
  Calculator,
  ArrowRight,
  TrendingUp,
  MapPin,
  ExternalLink,
  Download,
  Search,
  Filter,
  ShieldAlert
} from 'lucide-react';

export default function B2BClientDashboard() {
  const [filterType, setFilterType] = useState('ALL');

  // Realistic Port Logistics active client shipments
  const activeShipments = [
    {
      id: 'SHP-2026-091',
      blNumber: 'CADC-BL-2026-880',
      containerNumber: 'MSKU7829104',
      type: "Conteneur 40' High Cube",
      cargo: 'Équipements Industriels & Pièces Mécaniques',
      vessel: 'MSC ILONA (Escale #DLA-2026-44)',
      portOfLoading: 'Shanghai (Chine)',
      portOfDischarge: 'Douala (PAD Quai 14)',
      finalDestination: "N'Djamena (Tchad)",
      corridor: 'Corridor Douala - N\'Djamena',
      status: 'EN_TRANSIT_ROUTIER',
      statusLabel: 'En Transit Routier (Vers Garoua/Kousseri)',
      statusColor: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
      eta: '04 Sept 2026',
      freeTimeDaysLeft: 12,
      lastCheckpoint: 'Passage Pesée Pont-Bascule Bertoua (Validé)',
      isCustomsCleared: true,
      customsStatus: 'BAE Accordé (Circuit Vert)',
    },
    {
      id: 'SHP-2026-088',
      blNumber: 'CADC-BL-2026-742',
      containerNumber: 'CMAU9102834',
      type: "Conteneur 20' Dry Standard",
      cargo: 'Matières Premières Agro-alimentaires',
      vessel: 'CMA CGM AFRICA FOUR (Escale #PAK-2026-19)',
      portOfLoading: 'Anvers (Belgique)',
      portOfDischarge: 'Kribi (Port en Eau Profonde PAK)',
      finalDestination: 'Douala Zone Industrielle Bassa',
      corridor: 'Navette Kribi - Douala',
      status: 'DEDOUANEMENT_EN_COURS',
      statusLabel: 'En Cours de Dédouanement (GUCE/SYDONIA)',
      statusColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      eta: '02 Sept 2026',
      freeTimeDaysLeft: 4, // Warning urgency
      lastCheckpoint: 'Visite Documentaire en Cours - Déclarant Assigné',
      isCustomsCleared: false,
      customsStatus: 'Déclaration DUM #2026-DLA-8902',
    },
    {
      id: 'SHP-2026-079',
      blNumber: 'CADC-BL-2026-619',
      containerNumber: 'HLXU3891025',
      type: "Conteneur 40' Reefer (Frigorifique)",
      cargo: 'Produits Pharmaceutiques & Vaccins (-20°C)',
      vessel: 'HAPAG LLOYD TOGO EXPRESS',
      portOfLoading: 'Le Havre (France)',
      portOfDischarge: 'Douala (PAD Quai Conteneurs RTC)',
      finalDestination: 'Yaoundé Cradat',
      corridor: 'Axe Douala - Yaoundé',
      status: 'LIVRE_EPOD',
      statusLabel: 'Livré avec Succès (e-POD Signé)',
      statusColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      eta: 'Livré le 29 Août 2026',
      freeTimeDaysLeft: 0,
      lastCheckpoint: 'Signature Électronique e-POD Validée #EPOD-9921',
      isCustomsCleared: true,
      customsStatus: 'Dossier Dédouané & Archivé',
    },
    {
      id: 'SHP-2026-094',
      blNumber: 'CADC-BL-2026-904',
      containerNumber: 'SUDU5521098',
      type: "Conteneur 20' Open Top",
      cargo: 'Matériel BTP & Groupes Électrogènes',
      vessel: 'MAERSK CAIRO',
      portOfLoading: 'Jebel Ali (Dubaï, EAU)',
      portOfDischarge: 'Douala (PAD)',
      finalDestination: 'Bangui (RCA)',
      corridor: 'Corridor Douala - Bangui',
      status: 'A_QUAI_TERMINAL',
      statusLabel: 'Débarqué à Quai (Attente Enlèvement)',
      statusColor: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
      eta: '30 Août 2026 (À quai)',
      freeTimeDaysLeft: 7,
      lastCheckpoint: 'Conteneur positionné au Terminal RTC Travée C-12',
      isCustomsCleared: true,
      customsStatus: 'BAE Délivré par la Douane',
    }
  ];

  const filteredShipments = activeShipments.filter((s) => {
    if (filterType === 'TRANSIT') return s.status === 'EN_TRANSIT_ROUTIER';
    if (filterType === 'CUSTOMS') return s.status === 'DEDOUANEMENT_EN_COURS';
    if (filterType === 'DELIVERED') return s.status === 'LIVRE_EPOD';
    return true;
  });

  return (
    <div className="space-y-8">
      
      {/* Welcome & Global Overview Card */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                ESPACE CHARGEUR EN DIRECT
              </span>
              <span className="text-xs text-slate-400">Dernière synchronisation portuaire : il y a 2 min</span>
            </div>
            <h1 className="text-3xl font-black text-white">Tableau de Bord Chargeur & Importateur</h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
              Bienvenue, <strong className="text-slate-200">Société Camerounaise d'Import (SOCAM)</strong>. Visualisez vos flux maritimes et terrestres connectés aux terminaux PAD Douala et PAK Kribi.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Link
              href="/b2b/cotations"
              className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-400 hover:to-yellow-300 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all"
            >
              <Calculator className="w-4 h-4" /> Demander une Cotation
            </Link>
            <Link
              href="/b2b/tracking"
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-xl flex items-center gap-2 border border-slate-700 transition-all"
            >
              <Search className="w-4 h-4" /> Recherche Approfondie B/L
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Counters Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Cargaisons Actives</span>
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400"><Ship className="w-4 h-4" /></div>
          </div>
          <div className="text-3xl font-black text-white mt-2">4 Conteneurs</div>
          <div className="text-[11px] text-blue-400 mt-1 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" /> 2 Navires en rade / à quai
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Dédouanement (GUCE)</span>
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400"><Clock className="w-4 h-4" /></div>
          </div>
          <div className="text-3xl font-black text-white mt-2">3 BAE Obtenus</div>
          <div className="text-[11px] text-amber-400 mt-1 flex items-center gap-1">
            <span>1 Déclaration DUM en cours</span>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">En Transit Routier CEMAC</span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400"><Truck className="w-4 h-4" /></div>
          </div>
          <div className="text-3xl font-black text-white mt-2">1 Camion en Route</div>
          <div className="text-[11px] text-emerald-400 mt-1">Axe N'Djamena (Balise GPS OK)</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Factures & Débours</span>
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400"><CreditCard className="w-4 h-4" /></div>
          </div>
          <div className="text-3xl font-black text-white mt-2">1 À Régler</div>
          <div className="text-[11px] text-slate-400 mt-1">Solde disponible : 0 FCFA de pénalité</div>
        </div>
      </div>

      {/* Critical Demurrage / Surestaries Expiration Alert Banner */}
      <div className="bg-gradient-to-r from-red-950/70 via-slate-900 to-slate-900 border border-red-500/40 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-xl bg-red-500/20 text-red-400 shrink-0">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-red-400 flex items-center gap-2">
              <span>Alerte Franchise Surestaries Portuaires (Demurrage Guard)</span>
              <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-300 font-mono text-[10px]">URGENT</span>
            </div>
            <div className="text-sm font-bold text-slate-200 mt-0.5">
              Conteneur CMAU9102834 (Kribi PAK) : Il ne vous reste que <strong className="text-amber-400 font-mono">4 jours de franchise gratuite</strong> avant facturation des surestaries armateur.
            </div>
            <div className="text-xs text-slate-400 mt-0.5">
              Le dossier douane DUM est priorisé pour libération sous 48h.
            </div>
          </div>
        </div>

        <Link
          href="/b2b/tracking"
          className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-200 border border-red-500/40 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 shrink-0 transition-colors"
        >
          <span>Accélérer l'Enlèvement</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Active Shipments Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-black text-white flex items-center gap-2">
              <Package className="w-5 h-5 text-amber-400" /> Vos Expéditions en Cours de Traitement
            </h2>
            <p className="text-xs text-slate-400">Suivi direct de l'escale, dédouanement et livraison</p>
          </div>

          {/* Filter tabs */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 p-1 rounded-xl text-xs font-semibold">
            <button
              onClick={() => setFilterType('ALL')}
              className={`px-3 py-1 rounded-lg transition-colors ${filterType === 'ALL' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
            >
              Tous ({activeShipments.length})
            </button>
            <button
              onClick={() => setFilterType('TRANSIT')}
              className={`px-3 py-1 rounded-lg transition-colors ${filterType === 'TRANSIT' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
            >
              Transit Route
            </button>
            <button
              onClick={() => setFilterType('CUSTOMS')}
              className={`px-3 py-1 rounded-lg transition-colors ${filterType === 'CUSTOMS' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
            >
              Douane (GUCE)
            </button>
            <button
              onClick={() => setFilterType('DELIVERED')}
              className={`px-3 py-1 rounded-lg transition-colors ${filterType === 'DELIVERED' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
            >
              Livrées (e-POD)
            </button>
          </div>
        </div>

        {/* Shipments List */}
        <div className="space-y-3">
          {filteredShipments.map((shipment) => (
            <div
              key={shipment.id}
              className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 shadow-lg transition-all"
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                
                {/* Left info: Container + BL + Cargo */}
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-base font-black text-amber-300">
                      {shipment.containerNumber}
                    </span>
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                      B/L: {shipment.blNumber}
                    </span>
                    <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${shipment.statusColor}`}>
                      {shipment.statusLabel}
                    </span>
                  </div>

                  <div className="text-sm font-semibold text-white">
                    {shipment.cargo} • <span className="text-slate-400 text-xs font-normal">{shipment.type}</span>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 pt-1">
                    <span className="flex items-center gap-1">
                      <Ship className="w-3.5 h-3.5 text-slate-500" /> {shipment.vessel}
                    </span>
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-amber-400" /> {shipment.portOfLoading} ➔ {shipment.portOfDischarge} ➔ <strong className="text-slate-200">{shipment.finalDestination}</strong>
                    </span>
                  </div>
                </div>

                {/* Right info: Customs status, free time and action */}
                <div className="flex flex-col sm:flex-row lg:flex-col items-start lg:items-end justify-between gap-3 shrink-0 pt-3 lg:pt-0 border-t lg:border-t-0 border-slate-800">
                  <div className="text-right">
                    <div className="text-xs font-mono font-bold text-slate-300 flex items-center gap-1 lg:justify-end">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> {shipment.customsStatus}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      Franchise magasinage : <strong className={shipment.freeTimeDaysLeft <= 5 ? 'text-amber-400 font-bold' : 'text-emerald-400 font-bold'}>{shipment.freeTimeDaysLeft} jours restants</strong>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 w-full sm:w-auto">
                    <Link
                      href={`/b2b/tracking?query=${shipment.containerNumber}`}
                      className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl border border-slate-700 flex items-center justify-center gap-1.5 transition-colors flex-1 sm:flex-none"
                    >
                      <span>Historique & Étapes</span>
                      <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                    </Link>
                    <Link
                      href="/b2b/documents"
                      className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700"
                      title="Télécharger les documents du conteneur"
                    >
                      <Download className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </div>

              {/* Real-time Checkpoint banner */}
              <div className="mt-3.5 pt-2.5 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400 font-mono">
                <div className="flex items-center gap-1.5 truncate">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse shrink-0" />
                  <span className="text-slate-500">Dernier pointage :</span>
                  <span className="text-slate-300 truncate">{shipment.lastCheckpoint}</span>
                </div>
                <span className="shrink-0 text-slate-500 text-[11px]">ETA finale: {shipment.eta}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Corridor Condition & Border Feeds */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4">
          <div className="text-xs font-bold text-slate-300 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /> Corridor Douala - N'Djamena
          </div>
          <div className="text-xs text-slate-400 mt-1.5">
            Trafic fluide sur l'axe Douala - Bertoua - Ngaoundéré - Kousseri. Postes de pesée opérationnels.
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4">
          <div className="text-xs font-bold text-slate-300 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /> Corridor Douala - Bangui
          </div>
          <div className="text-xs text-slate-400 mt-1.5">
            Poste frontière de Garoua-Boulaï ouvert. Convois sous escorte douanière CEMAC réguliers.
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4">
          <div className="text-xs font-bold text-slate-300 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-400" /> Navette Portuaire Douala - Kribi
          </div>
          <div className="text-xs text-slate-400 mt-1.5">
            Autoroute Kribi - Edéa fluide. Temps de transfert moyen conteneur : 3h30.
          </div>
        </div>
      </div>
    </div>
  );
}
