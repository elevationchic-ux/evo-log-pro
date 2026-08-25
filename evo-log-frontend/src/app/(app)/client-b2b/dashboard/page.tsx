'use client';

export default function ClientB2bDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">🤝 CRM & Prospects</h1>
          <p className="text-on-surface-variant">Prospects, opportunités, pipeline commercial</p>
        </div>
        <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary">
          Nouveau Prospect
        </button>
      </div>
      <div className="erp-card">
        <div className="erp-card-body">
          <p className="text-center text-on-surface-variant py-8">
            Module en cours de développement - Client & B2B 🤝
            <br />
            <span className="text-sm">Fonctionnalités: CRM prospects, portail B2B, contrats & tarifications, service après-vente, fidélisation, analytics client</span>
          </p>
        </div>
      </div>
    </div>
  );
}