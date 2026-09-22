"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Anchor,
  ArrowLeft,
  Activity,
  AlertTriangle,
  Users,
  Wrench,
  Boxes,
  Clock,
  ShieldCheck,
  CheckCircle2,
  Plus,
  Zap,
  TrendingUp,
  RefreshCw
} from "lucide-react";

export default function StevedoringOperationsPage() {
  const [holds, setHolds] = useState([
    {
      id: 1,
      name: "CALE NO 1",
      capacity: 6250,
      stowed: 3100,
      remaining: 3150,
      rateMtHr: 345,
      targetRate: 350,
      cycles: 182,
      equipment: "Trémie Hydraulique #1 + Grue Mobile Gottwald 100T",
      gang: "GANG-UEMC-01 (14 Docks)",
      status: "NORMAL"
    },
    {
      id: 2,
      name: "CALE NO 2",
      capacity: 7500,
      stowed: 4200,
      remaining: 3300,
      rateMtHr: 220, // Slow rate! Alert trigger!
      targetRate: 350,
      cycles: 140,
      equipment: "Trémie Hydraulique #2 + Crapaud Clamshell Bucket",
      gang: "GANG-UEMC-02 (12 Docks)",
      status: "SLOWDOWN_ALERT" // Rate dropped < threshold!
    },
    {
      id: 3,
      name: "CALE NO 3",
      capacity: 6250,
      stowed: 3150,
      remaining: 3100,
      rateMtHr: 355,
      targetRate: 350,
      cycles: 195,
      equipment: "Trémie Hydraulique #3",
      gang: "GANG-UEMC-03 (14 Docks)",
      status: "NORMAL"
    },
    {
      id: 4,
      name: "CALE NO 4",
      capacity: 5000,
      stowed: 2400,
      remaining: 2600,
      rateMtHr: 340,
      targetRate: 350,
      cycles: 150,
      equipment: "Trémie Hydraulique #4",
      gang: "GANG-UEMC-04 (12 Docks)",
      status: "NORMAL"
    }
  ]);

  const [gangs, setGangs] = useState([
    {
      id: "GANG-UEMC-01",
      name: "Équipe UEMC Hold 1",
      size: 14,
      leader: "Tchagang Pierre",
      shift: "SHIFT JOUR (06h - 18h)",
      ppeVerified: true,
      laborCostXaf: 210000,
      status: "WORKING"
    },
    {
      id: "GANG-UEMC-02",
      name: "Équipe UEMC Hold 2",
      size: 12,
      leader: "Eboa Samuel",
      shift: "SHIFT JOUR (06h - 18h)",
      ppeVerified: true,
      laborCostXaf: 180000,
      status: "WORKING"
    }
  ]);

  return (
    <div className="p-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Link
            href="/port-operations"
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="p-2.5 rounded-2xl bg-amber-600/20 border border-amber-500/40 text-amber-400">
            <Anchor className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400 bg-amber-950 px-2 py-0.5 rounded-full border border-amber-800">
                Sub-Module B • Amber Theme
              </span>
            </div>
            <h1 className="text-2xl font-black text-white tracking-tight">
              Stevedoring & Hold Operations (Acconage & Manutention)
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Navire Actif :</span>
          <strong className="text-amber-400 font-mono text-sm">M/V PACIFIC RICE (QUAI-15)</strong>
        </div>
      </div>

      {/* Machinery Downtime Alert Warning Banner */}
      {holds.some((h) => h.status === "SLOWDOWN_ALERT") && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-red-950/80 via-amber-950/60 to-slate-900 border border-red-500/50 flex items-start gap-4 shadow-lg shadow-red-950/40">
          <div className="p-2 rounded-xl bg-red-600/20 text-red-400 border border-red-500/40 shrink-0">
            <AlertTriangle className="w-6 h-6 animate-pulse" />
          </div>
          <div className="space-y-1">
            <div className="text-sm font-extrabold text-red-300 flex items-center gap-2">
              <span>Alerte Baisse de Cadence - Panne Équipement Suspectée !</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-red-900 text-red-200 uppercase font-mono">AUTOMATED DETECT</span>
            </div>
            <p className="text-xs text-slate-300">
              La cadence de déchargement sur la <strong>CALE NO 2</strong> a chuté à <strong>220 MT/h</strong> (seuil nominal : 350 MT/h). Inspections recommandées sur la Trémie Hydraulique #2 ou le Crapaud (Clamshell Bucket).
            </p>
          </div>
        </div>
      )}

      {/* Holds Monitoring Grid */}
      <div className="space-y-3">
        <h2 className="text-base font-extrabold text-white flex items-center gap-2">
          <Boxes className="w-5 h-5 text-amber-400" />
          <span>Suivi par Cale (Hold Discharge Progress & Equipment Deployment)</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {holds.map((h) => {
            const pct = Math.round(((h.capacity - h.remaining) / h.capacity) * 100);
            const isSlow = h.status === "SLOWDOWN_ALERT";
            return (
              <div
                key={h.id}
                className={`p-5 rounded-2xl bg-slate-900/90 border transition-all ${
                  isSlow ? "border-amber-500/60 shadow-lg shadow-amber-500/10" : "border-slate-800"
                }`}
              >
                <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="font-black text-base text-white">{h.name}</span>
                    {isSlow && (
                      <span className="px-2 py-0.5 text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40 rounded-full animate-pulse">
                        Ralentissement MT/h
                      </span>
                    )}
                  </div>
                  <div className="text-xs font-mono text-slate-400">
                    Cycles Grue : <strong className="text-white">{h.cycles}</strong>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px]">Cadence Actuelle</span>
                    <span className={`text-xl font-black font-mono ${isSlow ? "text-amber-400" : "text-emerald-400"}`}>
                      {h.rateMtHr} MT/h
                    </span>
                    <span className="text-[10px] text-slate-500 block">Cible: {h.targetRate} MT/h</span>
                  </div>

                  <div>
                    <span className="text-slate-400 block text-[10px]">Restant à Décharger</span>
                    <span className="text-xl font-black font-mono text-white">
                      {h.remaining.toLocaleString()} MT
                    </span>
                    <span className="text-[10px] text-slate-500 block">Capacité: {h.capacity.toLocaleString()} MT</span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-4 space-y-1">
                  <div className="flex justify-between text-[11px]">
                    <span className="text-slate-400">Progression Cale</span>
                    <span className="font-bold text-amber-400">{pct}%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full" style={{ width: `${pct}%` }}></div>
                  </div>
                </div>

                {/* Equipment & Docker Gang Footer */}
                <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-1 text-[11px]">
                  <div className="flex items-center gap-1.5 text-slate-300">
                    <Wrench className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <span>{h.equipment}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-400">
                    <Users className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <span>Affectation : <strong className="text-white">{h.gang}</strong></span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Docker Shift & Gang Management (UEMC / GIE Integration) */}
      <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-base font-extrabold text-white flex items-center gap-2">
              <Users className="w-5 h-5 text-amber-400" />
              <span>Gestion des Équipes Docks UEMC / GIE & Contrôle EPI / PPE</span>
            </h3>
            <p className="text-xs text-slate-400">Reconstitution des équipes de manutention par shift et suivi des coûts de main d'œuvre</p>
          </div>
          <button className="px-3.5 py-2 rounded-xl bg-amber-600 text-white font-bold text-xs hover:bg-amber-500">
            + Affecter Nouveau Gang
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {gangs.map((g) => (
            <div key={g.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3 text-xs">
              <div className="flex justify-between items-center">
                <span className="font-bold text-white text-sm">{g.name}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">
                  {g.shift}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                <div>Shift Leader: <strong className="text-white">{g.leader}</strong></div>
                <div>Effectif Docks: <strong className="text-white">{g.size} Manutentionnaires</strong></div>
                <div>Coût Shift Estimated: <strong className="text-amber-400 font-mono">{g.laborCostXaf.toLocaleString()} XAF</strong></div>
                <div className="flex items-center gap-1 text-emerald-400">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>EPI / PPE Conforme</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
