'use client';

export default function PortOperationsManifestsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">📋 Manifestes & Escales Navires</h1>
          <p className="text-on-surface-variant">Gestion des manifestes de cargaison et programmation escales</p>
        </div>
        <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary">
          Nouveau Manifeste
        </button>
      </div>

      <div className="erp-card">
        <div className="erp-card-header">
          <h3 className="font-semibold text-on-surface">Liste des Manifestes</h3>
        </div>
        <div className="erp-card-body">
          <p className="text-center text-on-surface-variant py-8">
            Module en cours de développement - Manifestes & Escales Navires
            <br />
            <span className="text-sm">Fonctionnalités: Saisie manifestes, validation cargaison, programmation escales</span>
          </p>
        </div>
      </div>
    </div>
  );
}