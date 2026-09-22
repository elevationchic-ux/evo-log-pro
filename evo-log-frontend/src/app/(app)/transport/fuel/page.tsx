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

  const kpis: Array<any> = [];

  const tickets: Array<any> = [];

  const consommationParVehicule: Array<any> = [];

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
