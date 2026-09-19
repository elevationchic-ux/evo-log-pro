"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Bell, Search, Zap } from "lucide-react";
import { alertsAPI } from "@/lib/api-client";

type AlertRecord = {
  id: number;
  type_alerte?: string | null;
  gravite?: string | null;
  description?: string | null;
  concerne_type?: string | null;
  concerne_id?: number | null;
  date_alerte?: string | null;
  statut?: string | null;
};

const labels: Record<string, string> = {
  critique: "CRITIQUE",
  haute: "HAUTE",
  moyenne: "MOYENNE",
  faible: "BASSE",
};

export default function AdminAlertsPage() {
  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    alertsAPI.getAlerts({ limit: 200 }).then(response => {
      setAlerts(Array.isArray(response.data?.data) ? response.data.data : []);
    }).catch(requestError => {
      setError(requestError?.response?.data?.detail || "Impossible de charger les alertes.");
    }).finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => alerts.filter(alert => {
    const text = `${alert.type_alerte || ""} ${alert.description || ""} ${alert.concerne_type || ""}`.toLowerCase();
    return text.includes(search.toLowerCase());
  }), [alerts, search]);

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2"><Zap className="text-red-400" size={28} /> Centre Alertes & Sécurité</h1>
        <p className="text-muted-foreground mt-1 text-sm">Alertes persistées de la société courante</p>
      </div>
      {error && <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm">{error}</div>}
      <div className="relative max-w-md">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm" placeholder="Rechercher une alerte..." value={search} onChange={event => setSearch(event.target.value)} />
      </div>
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        {loading ? <div className="p-8 text-muted-foreground">Chargement...</div> : filtered.length === 0 ? <div className="p-8 text-muted-foreground flex items-center gap-2"><Bell size={16} /> Aucune alerte enregistrée.</div> : (
          <div className="divide-y divide-border">
            {filtered.map(alert => <div key={alert.id} className="p-4 flex items-start gap-3">
              <AlertTriangle className="mt-1 text-amber-400" size={18} />
              <div className="flex-1"><div className="flex justify-between gap-4"><span className="font-medium text-foreground">{alert.type_alerte || "Type non renseigné"}</span><span className="text-xs text-muted-foreground">{labels[String(alert.gravite || "").toLowerCase()] || alert.gravite || "Gravité non renseignée"}</span></div><p className="text-sm text-muted-foreground mt-1">{alert.description || "Description non renseignée"}</p><p className="text-xs text-muted-foreground mt-2">{alert.statut || "Statut non renseigné"}{alert.date_alerte ? ` · ${new Date(alert.date_alerte).toLocaleString("fr-FR")}` : ""}</p></div>
            </div>)}
          </div>
        )}
      </div>
    </div>
  );
}
