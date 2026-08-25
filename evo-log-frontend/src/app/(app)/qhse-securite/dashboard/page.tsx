'use client';

export default function QhseSecuriteDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">🛡️ Centre Sécurité QHSE</h1>
          <p className="text-on-surface-variant">Tableaux bord sécurité, incidents, conformité</p>
        </div>
        <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary">
          Déclarer Incident
        </button>
      </div>
      <div className="erp-card">
        <div className="erp-card-body">
          <p className="text-center text-on-surface-variant py-8">
            Module en cours de développement - QHSE & Sécurité 🛡️
            <br />
            <span className="text-sm">Fonctionnalités: Inspections portuaires, gestion incidents, formations sécurité, conformité OHADA, environnement RSE</span>
          </p>
        </div>
      </div>
    </div>
  );
}