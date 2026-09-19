"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertTriangle, Fuel, Plus, RefreshCw, Truck } from "lucide-react";
import { fuelGuardAPI } from "@/lib/api-client";

type FuelSensor = {
  id: number;
  immatriculation_camion: string;
  niveau_actuel_litres: number;
  capacite_totale_litres: number;
  alerte_vol_detectee: boolean;
  derniere_station?: string | null;
  updated_at?: string | null;
};

const formatNumber = (value: number) => new Intl.NumberFormat("fr-FR").format(value);

export default function TransportFuelDashboard() {
  const [sensors, setSensors] = useState<FuelSensor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fuelGuardAPI.getSensors();
      setSensors(Array.isArray(response.data?.items) ? response.data.items : []);
    } catch (requestError: any) {
      setSensors([]);
      setError(requestError?.response?.data?.detail || "Impossible de charger les niveaux carburant.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const totalLitres = useMemo(() => sensors.reduce((total, sensor) => total + Number(sensor.niveau_actuel_litres || 0), 0), [sensors]);
  const totalCapacity = useMemo(() => sensors.reduce((total, sensor) => total + Number(sensor.capacite_totale_litres || 0), 0), [sensors]);
  const alertCount = sensors.filter(sensor => sensor.alerte_vol_detectee).length;

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2"><Fuel className="text-amber-500" size={28} /> Gestion Carburant</h1>
          <p className="text-muted-foreground mt-1 text-sm">Niveaux des cuves et alertes FuelGuard persistés</p>
        </div>
        <div className="flex gap-2">
          <button onClick={load} disabled={loading} className="flex items-center gap-2 px-3 py-2 rounded-xl border border-border text-sm">
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} /> Actualiser
          </button>
          <a href="/transport/saisie-ticket-carburant" className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 text-white text-sm font-medium">
            <Plus size={16} /> Saisir Ticket
          </a>
        </div>
      </div>

      {error && <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm">{error}</div>}

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-amber-500/20 bg-amber-500/10 p-5"><p className="text-xs text-muted-foreground">Carburant mesuré</p><p className="text-2xl font-bold text-amber-400">{formatNumber(totalLitres)} L</p></div>
        <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 p-5"><p className="text-xs text-muted-foreground">Capacité déclarée</p><p className="text-2xl font-bold text-cyan-400">{formatNumber(totalCapacity)} L</p></div>
        <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-5"><p className="text-xs text-muted-foreground">Alertes capteurs</p><p className="text-2xl font-bold text-red-400">{alertCount}</p></div>
      </div>

      <div className="rounded-2xl border border-border bg-card p-5">
        <h2 className="font-semibold text-foreground mb-4 flex items-center gap-2"><Truck size={18} className="text-amber-400" /> Capteurs par véhicule</h2>
        {loading ? <p className="text-muted-foreground">Chargement...</p> : sensors.length === 0 ? <p className="text-muted-foreground">Aucun capteur carburant enregistré.</p> : (
          <div className="space-y-4">
            {sensors.map(sensor => {
              const capacity = Number(sensor.capacite_totale_litres || 0);
              const level = capacity > 0 ? Math.min(100, (Number(sensor.niveau_actuel_litres) / capacity) * 100) : 0;
              return <div key={sensor.id} className="border-b border-border pb-4 last:border-0">
                <div className="flex justify-between gap-4 text-sm"><span className="font-mono text-foreground">{sensor.immatriculation_camion}</span><span className="text-muted-foreground">{formatNumber(Number(sensor.niveau_actuel_litres))} / {formatNumber(capacity)} L</span></div>
                <div className="mt-2 h-2 rounded-full bg-muted"><div className={`h-2 rounded-full ${level < 30 ? "bg-red-500" : "bg-emerald-500"}`} style={{ width: `${level}%` }} /></div>
                <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground"><span>{sensor.derniere_station || "Station non renseignée"}</span>{sensor.alerte_vol_detectee && <span className="text-red-400 flex items-center gap-1"><AlertTriangle size={13} /> Alerte</span>}</div>
              </div>;
            })}
          </div>
        )}
      </div>

      <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-amber-200">
        Les tickets de remplissage et leur coût ne sont pas affichés : aucun endpoint persistant de tickets carburant n’est encore disponible.
      </div>
    </div>
  );
}
