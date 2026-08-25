'use client';

export default function QuaiOperationsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">⚓ Opérations de Quai Live</h1>
          <p className="text-on-surface-variant">Coordination déchargement, manutention portuaire temps réel</p>
        </div>
      </div>

      <div className="erp-card">
        <div className="erp-card-body">
          <p className="text-center text-on-surface-variant py-8">
            Module en cours de développement - Opérations de Quai Live
            <br />
            <span className="text-sm">Fonctionnalités: Manutention temps réel, coordination équipes, suivi TEU</span>
          </p>
        </div>
      </div>
    </div>
  );
}