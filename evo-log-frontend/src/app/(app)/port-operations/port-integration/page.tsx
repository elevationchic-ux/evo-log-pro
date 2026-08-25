'use client';

export default function PortIntegrationPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">🔗 Intégration Systèmes Portuaires</h1>
          <p className="text-on-surface-variant">Intégration EDI avec autorités portuaires Douala/Kribi</p>
        </div>
      </div>

      <div className="erp-card">
        <div className="erp-card-body">
          <p className="text-center text-on-surface-variant py-8">
            Module en cours de développement - Intégration Systèmes Portuaires 🇨🇲
            <br />
            <span className="text-sm">Fonctionnalités: EDI autorités, API portuaires, synchronisation données</span>
          </p>
        </div>
      </div>
    </div>
  );
}