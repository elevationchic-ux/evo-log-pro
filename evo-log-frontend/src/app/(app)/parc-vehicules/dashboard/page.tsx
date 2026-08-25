'use client';

export default function ParcVehiculesDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">🚗 Tableau de Bord Parc Véhicules</h1>
          <p className="text-on-surface-variant">Vue globale flotte, disponibilité, alertes maintenance</p>
        </div>
        <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary">
          Ajouter Véhicule
        </button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-violet-500/10 p-3">
              <span className="material-symbols-outlined text-violet-600">directions_car</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">127</p>
              <p className="text-sm text-on-surface-variant">Véhicules Total</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-emerald-500/10 p-3">
              <span className="material-symbols-outlined text-emerald-600">check_circle</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">89</p>
              <p className="text-sm text-on-surface-variant">Disponibles</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-amber-500/10 p-3">
              <span className="material-symbols-outlined text-amber-600">build</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">23</p>
              <p className="text-sm text-on-surface-variant">En Maintenance</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-red-500/10 p-3">
              <span className="material-symbols-outlined text-red-600">warning</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">15</p>
              <p className="text-sm text-on-surface-variant">Alertes</p>
            </div>
          </div>
        </div>
      </div>

      <div className="erp-card">
        <div className="erp-card-body">
          <p className="text-center text-on-surface-variant py-8">
            Module en cours de développement - Parc & Véhicules
            <br />
            <span className="text-sm">Fonctionnalités: Flotte complète, maintenance préventive, documents véhicules, coûts TCO, plaques d'immatriculation</span>
          </p>
        </div>
      </div>
    </div>
  );
}