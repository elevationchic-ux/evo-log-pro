"use client";

import React, { useState } from "react";
import {
  ShieldAlert, AlertTriangle, CheckCircle, XCircle,
  Clock, Plus, Search, Bell, Eye, CheckCheck,
  Truck, Package, DollarSign, Wrench, Globe, Users,
  Filter, RefreshCw, Zap
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://EVO-LOG-backend-production.up.railway.app";

interface Alert {
  id: number;
  titre: string;
  description: string;
  niveau: "CRITIQUE" | "HAUTE" | "MOYENNE" | "BASSE";
  module: string;
  statut: "ACTIVE" | "ACQUITTEE" | "RESOLUE";
  created_at: string;
  actions_requises?: string[];
}

const niveauConfig = {
  CRITIQUE: { color: "text-red-400 bg-red-400/10 border-red-400/30", dot: "bg-red-500 animate-pulse", badge: "bg-red-500" },
  HAUTE: { color: "text-orange-400 bg-orange-400/10 border-orange-400/30", dot: "bg-orange-500", badge: "bg-orange-500" },
  MOYENNE: { color: "text-amber-400 bg-amber-400/10 border-amber-400/30", dot: "bg-amber-500", badge: "bg-amber-500" },
  BASSE: { color: "text-blue-400 bg-blue-400/10 border-blue-400/30", dot: "bg-blue-500", badge: "bg-blue-500" },
};

const FALLBACK_ALERTS: Alert[] = [
  { id: 1, titre: "Accès non autorisé – Zone YARD-A01", description: "Individu non identifié tenté d'accéder sans badge à 23h47. Sécurité intervenue. Rapport transmis à Police Portuaire.", niveau: "CRITIQUE", module: "SECURITE", statut: "ACTIVE", created_at: new Date().toISOString(), actions_requises: ["Vérifier enregistrements CCTV", "Contacter Police Portuaire", "Renforcer patrouilles"] },
  { id: 2, titre: "Stock Critique – MAT-SOUDURE-006", description: "Niveau de stock en dessous du seuil minimum. Réapprovisionnement requis avant arrêt total des opérations atelier.", niveau: "HAUTE", module: "MAGASIN", statut: "ACTIVE", created_at: new Date(Date.now() - 3600000).toISOString(), actions_requises: ["Créer bon de commande", "Contacter fournisseur"] },
  { id: 3, titre: "Usure Pneumatiques DLA-TRK-001", description: "Niveau d'usure à 90% sur les pneus avant. Risque pour la sécurité routière. Mission planifiée pour demain.", niveau: "HAUTE", module: "MAINTENANCE", statut: "ACQUITTEE", created_at: new Date(Date.now() - 7200000).toISOString(), actions_requises: ["Planifier remplacement urgent"] },
  { id: 4, titre: "Facture en retard +30j – BOLLORE", description: "Facture FAC-2026-0187 (2.350.000 XAF) non réglée depuis 31 jours. Relance automatique envoyée.", niveau: "MOYENNE", module: "FINANCE", statut: "ACTIVE", created_at: new Date(Date.now() - 86400000).toISOString(), actions_requises: ["Envoyer relance formelle", "Contacter client"] },
  { id: 5, titre: "WebSocket Déconnecté – 4 tentatives", description: "Le service WebSocket temps réel a échoué 4 fois consécutives. Fonctionnalités temps réel dégradées.", niveau: "MOYENNE", module: "SYSTEME", statut: "RESOLUE", created_at: new Date(Date.now() - 172800000).toISOString(), actions_requises: [] },
  { id: 6, titre: "Rapport QHSE en attente validation", description: "Inspection quai 3 soumise il y a 48h sans validation superviseur. Délai dépassé.", niveau: "BASSE", module: "QHSE", statut: "ACTIVE", created_at: new Date(Date.now() - 172800000).toISOString(), actions_requises: ["Valider rapport QHSE-2026-012"] },
];

export default function AdminAlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>(FALLBACK_ALERTS);
  const [filterNiveau, setFilterNiveau] = useState("TOUS");
  const [filterStatut, setFilterStatut] = useState("TOUS");
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState<number | null>(null);

  const filtered = alerts.filter(a => {
    const matchSearch = search === "" || a.titre.toLowerCase().includes(search.toLowerCase()) || a.module.toLowerCase().includes(search.toLowerCase());
    const matchNiveau = filterNiveau === "TOUS" || a.niveau === filterNiveau;
    const matchStatut = filterStatut === "TOUS" || a.statut === filterStatut;
    return matchSearch && matchNiveau && matchStatut;
  });

  const acquitter = (id: number) => setAlerts(prev => prev.map(a => a.id === id ? { ...a, statut: "ACQUITTEE" } : a));
  const resoudre = (id: number) => setAlerts(prev => prev.map(a => a.id === id ? { ...a, statut: "RESOLUE" } : a));

  const critiques = alerts.filter(a => a.niveau === "CRITIQUE" && a.statut === "ACTIVE").length;

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Zap className="text-red-400" size={28} />
            Centre Alertes & Sécurité
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            {critiques > 0 && <span className="text-red-400 font-semibold">{critiques} alerte{critiques > 1 ? "s" : ""} critique{critiques > 1 ? "s" : ""} active{critiques > 1 ? "s" : ""}  </span>}
            Supervision globale de toutes les alertes système EVO-LOG
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-sm font-medium transition-colors">
          <Plus size={16} />
          Créer Alerte
        </button>
      </div>

      {/* KPI par niveau */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {(["CRITIQUE", "HAUTE", "MOYENNE", "BASSE"] as const).map(niveau => {
          const cfg = niveauConfig[niveau];
          const count = alerts.filter(a => a.niveau === niveau && a.statut === "ACTIVE").length;
          const labels = { CRITIQUE: "Critiques", HAUTE: "Hautes", MOYENNE: "Moyennes", BASSE: "Basses" };
          return (
            <button
              key={niveau}
              onClick={() => setFilterNiveau(filterNiveau === niveau ? "TOUS" : niveau)}
              className={`rounded-2xl border p-4 text-left transition-all hover:scale-[1.02] ${cfg.color} ${filterNiveau === niveau ? "ring-2 ring-current" : ""}`}
            >
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-2.5 h-2.5 rounded-full ${cfg.dot}`} />
                <span className="text-xs font-medium">{labels[niveau]}</span>
              </div>
              <p className="text-2xl font-bold">{count}</p>
              <p className="text-xs opacity-70 mt-0.5">actives</p>
            </button>
          );
        })}
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500/30 placeholder:text-muted-foreground" placeholder="Rechercher une alerte..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm" value={filterStatut} onChange={e => setFilterStatut(e.target.value)}>
          <option value="TOUS">Tous les statuts</option>
          <option value="ACTIVE">Actives</option>
          <option value="ACQUITTEE">Acquittées</option>
          <option value="RESOLUE">Résolues</option>
        </select>
      </div>

      {/* Liste Alertes */}
      <div className="space-y-3">
        {filtered.map(alert => {
          const cfg = niveauConfig[alert.niveau];
          const isExpanded = expanded === alert.id;
          return (
            <div key={alert.id} className={`rounded-2xl border bg-card overflow-hidden transition-all ${alert.niveau === "CRITIQUE" && alert.statut === "ACTIVE" ? "ring-1 ring-red-500/40" : ""}`}>
              <div
                className="flex items-start gap-4 p-4 cursor-pointer hover:bg-muted/20 transition-colors"
                onClick={() => setExpanded(isExpanded ? null : alert.id)}
              >
                <div className={`w-2.5 h-2.5 rounded-full mt-1.5 flex-shrink-0 ${cfg.dot}`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold border ${cfg.color}`}>{alert.niveau}</span>
                        <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">{alert.module}</span>
                        {alert.statut === "RESOLUE" && <span className="text-xs text-emerald-400">✓ Résolue</span>}
                        {alert.statut === "ACQUITTEE" && <span className="text-xs text-amber-400">⏳ Acquittée</span>}
                      </div>
                      <p className={`font-semibold mt-1.5 ${alert.statut === "RESOLUE" ? "text-muted-foreground line-through" : "text-foreground"}`}>{alert.titre}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">{alert.description}</p>
                    </div>
                    <div className="flex gap-1 flex-shrink-0">
                      {alert.statut === "ACTIVE" && (
                        <>
                          <button onClick={e => { e.stopPropagation(); acquitter(alert.id); }} className="px-2 py-1 rounded-lg text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 hover:bg-amber-500/20 transition-colors whitespace-nowrap">Acquitter</button>
                          <button onClick={e => { e.stopPropagation(); resoudre(alert.id); }} className="px-2 py-1 rounded-lg text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors whitespace-nowrap">Résoudre</button>
                        </>
                      )}
                      {alert.statut === "ACQUITTEE" && (
                        <button onClick={e => { e.stopPropagation(); resoudre(alert.id); }} className="px-2 py-1 rounded-lg text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors">Résoudre</button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              {isExpanded && alert.actions_requises && alert.actions_requises.length > 0 && (
                <div className="px-4 pb-4 pt-2 border-t border-border bg-muted/20">
                  <p className="text-xs font-semibold text-muted-foreground mb-2">ACTIONS REQUISES :</p>
                  <ul className="space-y-1">
                    {alert.actions_requises.map((action, i) => (
                      <li key={i} className="flex items-center gap-2 text-xs text-foreground">
                        <div className="w-1.5 h-1.5 rounded-full bg-current opacity-60" />
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
