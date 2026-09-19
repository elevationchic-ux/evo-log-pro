"use client";

import React, { useState, useEffect } from "react";
import {
  Fuel, TrendingDown, TrendingUp, BarChart3, Plus,
  Truck, RefreshCw, AlertTriangle, CheckCircle, Clock
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://EVO-LOG-backend-production.up.railway.app";

const fmtNum = (n: number) => new Intl.NumberFormat("fr-FR").format(n);

export default function TransportFuelDashboard() {
  const [loading, setLoading] = useState(false);

  const kpis = [
    { label: "Stock Gasoil", value: "8.500", unit: "litres", pct: 42, color: "text-amber-400", bg: "from-amber-500/10 to-yellow-500/10 border-amber-500/20", alert: false },
    { label: "Consommation Mois", value: "12.450", unit: "litres", pct: null, color: "text-cyan-400", bg: "from-cyan-500/10 to-blue-500/10 border-cyan-500/20", alert: false },
    { label: "Coût Moyen L", value: "720", unit: "XAF/L", pct: null, color: "text-indigo-400", bg: "from-indigo-500/10 to-violet-500/10 border-indigo-500/20", alert: false },
    { label: "Budget Restant", value: "2.880.000", unit: "XAF", pct: null, color: "text-emerald-400", bg: "from-emerald-500/10 to-teal-500/10 border-emerald-500/20", alert: false },
  ];

  const tickets = [
    { id: "FUEL-2026-088", vehicule: "DLA-TRK-001", chauffeur: "Jean-Marc MVONDO", station: "TotalEnergies Port Douala", litres: 450, montant_xaf: 324000, statut: "VALIDE", date: "2026-08-10" },
    { id: "FUEL-2026-089", vehicule: "DLA-TRK-002", chauffeur: "Martin EBANG", station: "TotalEnergies Bassa", litres: 380, montant_xaf: 273600, statut: "VALIDE", date: "2026-08-11" },
    { id: "FUEL-2026-090", vehicule: "DLA-TRK-007", chauffeur: "Paul KAMGA", station: "Shell Akwa", litres: 200, montant_xaf: 144000, statut: "EN_ATTENTE", date: "2026-08-12" },
    { id: "FUEL-2026-091", vehicule: "DLA-UTL-003", chauffeur: "Sarah MVONGO", station: "TotalEnergies Douala Centre", litres: 60, montant_xaf: 43200, statut: "VALIDE", date: "2026-08-12" },
  ];

  const consommationParVehicule = [
    { vehicule: "DLA-TRK-001", litres: 3240, budget_xaf: 2332800, taux_pct: 78 },
    { vehicule: "DLA-TRK-002", litres: 2850, budget_xaf: 2052000, taux_pct: 68 },
    { vehicule: "DLA-TRK-007", litres: 1890, budget_xaf: 1360800, taux_pct: 91 },
    { vehicule: "DLA-UTL-003", litres: 420, budget_xaf: 302400, taux_pct: 32 },
  ];

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Fuel className="text-amber-500" size={28} />
            Gestion Carburant
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Suivi consommation, tickets carburant et budget flotte  Août 2026
          </p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-3 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">
            <RefreshCw size={14} />
          </button>
          <a href="/transport/saisie-ticket-carburant" className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium transition-colors">
            <Plus size={16} />
            Saisir Ticket
          </a>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {kpis.map((k, i) => (
          <div key={i} className={`rounded-2xl border bg-gradient-to-br ${k.bg} p-5`}>
            <div className="flex justify-between items-start mb-2">
              <p className="text-xs text-muted-foreground">{k.label}</p>
              <Fuel size={16} className={`${k.color} opacity-60`} />
            </div>
            <p className={`text-2xl font-bold ${k.color}`}>{k.value}</p>
            <p className="text-xs text-muted-foreground mt-0.5">{k.unit}</p>
            {k.pct !== null && (
              <div className="mt-3">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-muted-foreground">Niveau cuve</span>
                  <span className={k.pct < 30 ? "text-red-400 font-bold" : "text-muted-foreground"}>{k.pct}%</span>
                </div>
                <div className="w-full bg-muted rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full transition-all ${k.pct < 30 ? "bg-red-500" : k.pct < 60 ? "bg-amber-500" : "bg-emerald-500"}`}
                    style={{ width: `${k.pct}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Consommation par véhicule */}
        <div className="rounded-2xl border border-border bg-card p-5">
          <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
            <Truck size={18} className="text-amber-400" />
            Consommation par Véhicule
          </h3>
          <div className="space-y-4">
            {consommationParVehicule.map((v, i) => (
              <div key={i}>
                <div className="flex justify-between items-center mb-1.5">
                  <div>
                    <span className="text-sm font-medium text-foreground font-mono">{v.vehicule}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold text-foreground">{fmtNum(v.litres)} L</span>
                    <span className="text-xs text-muted-foreground ml-2">({fmtNum(v.budget_xaf)} XAF)</span>
                  </div>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${v.taux_pct > 85 ? "bg-red-500" : v.taux_pct > 65 ? "bg-amber-500" : "bg-emerald-500"}`}
                    style={{ width: `${v.taux_pct}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>Budget utilisé</span>
                  <span className={v.taux_pct > 85 ? "text-red-400 font-bold" : ""}>{v.taux_pct}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tickets récents */}
        <div className="rounded-2xl border border-border bg-card p-5">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-foreground flex items-center gap-2">
              <BarChart3 size={18} className="text-amber-400" />
              Tickets Récents
            </h3>
            <a href="/transport/fuel/history" className="text-xs text-amber-400 hover:underline">Voir tout →</a>
          </div>
          <div className="space-y-3">
            {tickets.map((t, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-muted/30 hover:bg-muted/50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${t.statut === "VALIDE" ? "bg-emerald-500" : "bg-amber-500"}`} />
                  <div>
                    <p className="text-sm font-medium text-foreground font-mono">{t.id}</p>
                    <p className="text-xs text-muted-foreground">{t.vehicule} • {t.chauffeur}</p>
                    <p className="text-xs text-muted-foreground">{t.station}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-amber-400">{fmtNum(t.litres)} L</p>
                  <p className="text-xs text-muted-foreground">{fmtNum(t.montant_xaf)} XAF</p>
                  <span className={`text-xs font-medium ${t.statut === "VALIDE" ? "text-emerald-400" : "text-amber-400"}`}>
                    {t.statut === "VALIDE" ? "✓ Validé" : "⏳ En attente"}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <a href="/transport/saisie-ticket-carburant" className="mt-4 flex items-center justify-center gap-2 w-full py-2.5 rounded-xl border border-dashed border-amber-500/30 text-amber-400 text-sm hover:bg-amber-500/5 transition-colors">
            <Plus size={16} />
            Saisir nouveau ticket
          </a>
        </div>
      </div>
    </div>
  );
}
