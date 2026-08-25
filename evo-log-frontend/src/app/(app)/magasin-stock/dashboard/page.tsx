'use client';

export default function MagasinStockDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">📦 Dashboard WMS Central</h1>
          <p className="text-on-surface-variant">Vue globale stock, mouvements, alertes, KPIs entrepôt</p>
        </div>
        <div className="flex gap-3">
          <button className="rounded-lg border border-outline bg-surface px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container">
            Inventaire
          </button>
          <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90">
            Nouvelle Réception
          </button>
        </div>
      </div>

      {/* KPIs WMS */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-amber-500/10 p-3">
              <span className="material-symbols-outlined text-amber-600">warehouse</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">12,847</p>
              <p className="text-sm text-on-surface-variant">Articles en Stock</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-blue-500/10 p-3">
              <span className="material-symbols-outlined text-blue-600">move_up</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">247</p>
              <p className="text-sm text-on-surface-variant">Mouvements Jour</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-emerald-500/10 p-3">
              <span className="material-symbols-outlined text-emerald-600">check_circle</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">96%</p>
              <p className="text-sm text-on-surface-variant">Taux de Service</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-red-500/10 p-3">
              <span className="material-symbols-outlined text-red-600">warning</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">23</p>
              <p className="text-sm text-on-surface-variant">Alertes Stock</p>
            </div>
          </div>
        </div>
      </div>

      {/* Activité WMS */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="erp-card">
          <div className="erp-card-header">
            <h3 className="font-semibold text-on-surface">Réceptions du Jour</h3>
          </div>
          <div className="erp-card-body">
            <div className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">REC-WMS-240847</p>
                  <p className="text-sm text-on-surface-variant">147 colis • Contrôle qualité terminé</p>
                </div>
                <span className="status-badge status-delivered">RÉCEPTIONNÉ</span>
              </div>
              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">REC-WMS-240848</p>
                  <p className="text-sm text-on-surface-variant">89 palettes • En cours de déchargement</p>
                </div>
                <span className="status-badge status-loading">EN COURS</span>
              </div>
            </div>
          </div>
        </div>

        <div className="erp-card">
          <div className="erp-card-header">
            <h3 className="font-semibold text-on-surface">Expéditions Préparées</h3>
          </div>
          <div className="erp-card-body">
            <div className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">EXP-WMS-240567</p>
                  <p className="text-sm text-on-surface-variant">Client ABC • 24 colis prêts</p>
                </div>
                <span className="status-badge status-planified">PRÊT</span>
              </div>
              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">EXP-WMS-240568</p>
                  <p className="text-sm text-on-surface-variant">Export Tchad • 156 colis</p>
                </div>
                <span className="status-badge status-loading">PICKING</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Plan Entrepôt */}
      <div className="erp-card">
        <div className="erp-card-header">
          <h3 className="font-semibold text-on-surface">Occupation Entrepôt par Zone</h3>
        </div>
        <div className="erp-card-body">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 rounded-lg border border-outline">
              <p className="text-2xl font-bold text-emerald-600">87%</p>
              <p className="text-sm text-on-surface-variant">Zone A</p>
            </div>
            <div className="text-center p-4 rounded-lg border border-outline">
              <p className="text-2xl font-bold text-amber-600">65%</p>
              <p className="text-sm text-on-surface-variant">Zone B</p>
            </div>
            <div className="text-center p-4 rounded-lg border border-outline">
              <p className="text-2xl font-bold text-red-600">92%</p>
              <p className="text-sm text-on-surface-variant">Zone C</p>
            </div>
            <div className="text-center p-4 rounded-lg border border-outline">
              <p className="text-2xl font-bold text-blue-600">73%</p>
              <p className="text-sm text-on-surface-variant">Zone D</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}