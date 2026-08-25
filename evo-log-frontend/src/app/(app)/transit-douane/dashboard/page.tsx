'use client';

export default function TransitDouaneDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">🛃 Centre de Dédouanement</h1>
          <p className="text-on-surface-variant">Centre de traitement des procédures douanières</p>
        </div>
        <div className="flex gap-3">
          <button className="rounded-lg border border-outline bg-surface px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container">
            Actualiser
          </button>
          <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90">
            Nouvelle DUM
          </button>
        </div>
      </div>

      {/* KPIs Douane */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-violet-500/10 p-3">
              <span className="material-symbols-outlined text-violet-600">gavel</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">47</p>
              <p className="text-sm text-on-surface-variant">DUM En Cours</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-emerald-500/10 p-3">
              <span className="material-symbols-outlined text-emerald-600">check_circle</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">128</p>
              <p className="text-sm text-on-surface-variant">BAE Émis</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-amber-500/10 p-3">
              <span className="material-symbols-outlined text-amber-600">schedule</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">23</p>
              <p className="text-sm text-on-surface-variant">En Attente Visite</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-blue-500/10 p-3">
              <span className="material-symbols-outlined text-blue-600">payments</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">2.4M</p>
              <p className="text-sm text-on-surface-variant">FCFA Droits</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tableau Dossiers Transit */}
      <div className="erp-card">
        <div className="erp-card-header">
          <h3 className="font-semibold text-on-surface">Dossiers Transit CEMAC du Jour</h3>
        </div>
        <div className="erp-card-body">
          <div className="space-y-4">
            <div className="flex items-center justify-between rounded-lg border border-outline p-4">
              <div className="flex items-center gap-4">
                <span className="material-symbols-outlined text-violet-600">description</span>
                <div>
                  <p className="font-medium text-on-surface">DUM-CM-2024-08547</p>
                  <p className="text-sm text-on-surface-variant">Import • Conteneur TEMU4567890 • Marchandises diverses</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm text-on-surface-variant">1,245,000 FCFA</span>
                <span className="status-badge status-loading">Taxation</span>
              </div>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-outline p-4">
              <div className="flex items-center gap-4">
                <span className="material-symbols-outlined text-violet-600">description</span>
                <div>
                  <p className="font-medium text-on-surface">DUM-CM-2024-08546</p>
                  <p className="text-sm text-on-surface-variant">Export • Conteneur FCIU7890123 • Produits agricoles</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm text-on-surface-variant">387,500 FCFA</span>
                <span className="status-badge status-delivered">BAE Émis</span>
              </div>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-outline p-4">
              <div className="flex items-center gap-4">
                <span className="material-symbols-outlined text-violet-600">description</span>
                <div>
                  <p className="font-medium text-on-surface">DUM-CM-2024-08545</p>
                  <p className="text-sm text-on-surface-variant">Transit • Direction Yaoundé • Matériel industriel</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm text-on-surface-variant">856,750 FCFA</span>
                <span className="status-badge status-planified">Visite Programmée</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}