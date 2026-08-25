'use client';

export default function TransportControlTowerPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">🚛 Control Tower Transport</h1>
          <p className="text-on-surface-variant">Centre de contrôle transport temps réel, dispatch missions</p>
        </div>
        <div className="flex gap-3">
          <button className="rounded-lg border border-outline bg-surface px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container">
            Actualiser Live
          </button>
          <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90">
            Nouvelle Mission
          </button>
        </div>
      </div>

      {/* KPIs Transport */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-cyan-500/10 p-3">
              <span className="material-symbols-outlined text-cyan-600">local_shipping</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">45</p>
              <p className="text-sm text-on-surface-variant">Véhicules Actifs</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-emerald-500/10 p-3">
              <span className="material-symbols-outlined text-emerald-600">route</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">128</p>
              <p className="text-sm text-on-surface-variant">Missions en Cours</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-amber-500/10 p-3">
              <span className="material-symbols-outlined text-amber-600">local_gas_station</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">87%</p>
              <p className="text-sm text-on-surface-variant">Efficacité Carburant</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-blue-500/10 p-3">
              <span className="material-symbols-outlined text-blue-600">schedule</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">94%</p>
              <p className="text-sm text-on-surface-variant">Ponctualité</p>
            </div>
          </div>
        </div>
      </div>

      {/* Carte et Missions Live */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="erp-card">
          <div className="erp-card-header">
            <h3 className="font-semibold text-on-surface">Missions Temps Réel</h3>
          </div>
          <div className="erp-card-body">
            <div className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div className="flex items-center gap-3">
                  <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse"></div>
                  <div>
                    <p className="font-medium text-on-surface">CMR-T-4512</p>
                    <p className="text-sm text-on-surface-variant">Douala → Yaoundé • 3h15 restantes</p>
                  </div>
                </div>
                <span className="status-badge status-transit">EN ROUTE</span>
              </div>

              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div className="flex items-center gap-3">
                  <div className="h-3 w-3 rounded-full bg-blue-500"></div>
                  <div>
                    <p className="font-medium text-on-surface">CMR-T-4513</p>
                    <p className="text-sm text-on-surface-variant">Port → Client Bassa • Chargement</p>
                  </div>
                </div>
                <span className="status-badge status-loading">CHARGEMENT</span>
              </div>

              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div className="flex items-center gap-3">
                  <div className="h-3 w-3 rounded-full bg-emerald-500"></div>
                  <div>
                    <p className="font-medium text-on-surface">CMR-T-4510</p>
                    <p className="text-sm text-on-surface-variant">Bafoussam • Livré avec e-POD</p>
                  </div>
                </div>
                <span className="status-badge status-delivered">LIVRÉ</span>
              </div>
            </div>
          </div>
        </div>

        <div className="erp-card">
          <div className="erp-card-header">
            <h3 className="font-semibold text-on-surface">Carte GPS Live</h3>
          </div>
          <div className="erp-card-body">
            <div className="aspect-video rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
              <div className="text-center">
                <span className="material-symbols-outlined text-6xl text-slate-400 mb-4">map</span>
                <p className="text-on-surface-variant">Intégration Carte GPS</p>
                <p className="text-sm text-on-surface-variant">45 véhicules géolocalisés</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}