'use client';

export default function ReportsBiExecutiveDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Executive Dashboard</h1>
          <p className="text-on-surface-variant">Module en cours de développement</p>
        </div>
      </div>

      <div className="erp-card">
        <div className="erp-card-body">
          <div className="text-center py-12">
            <span className="material-symbols-outlined text-6xl text-on-surface-variant/50 mb-4 block">construction</span>
            <h3 className="text-lg font-semibold text-on-surface mb-2">Module en cours de développement</h3>
            <p className="text-on-surface-variant">
              Reports Bi - Executive Dashboard
              <br />
              <span className="text-sm">Architecture ERP Portuaire End-to-End • Processus Navire → Client</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
