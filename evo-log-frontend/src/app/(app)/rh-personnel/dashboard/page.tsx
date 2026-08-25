'use client';

export default function RhPersonnelDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">👥 Dashboard RH Central</h1>
          <p className="text-on-surface-variant">Effectifs, KPIs RH, turnover, absentéisme</p>
        </div>
        <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary">
          Nouvel Employé
        </button>
      </div>
      <div className="erp-card">
        <div className="erp-card-body">
          <p className="text-center text-on-surface-variant py-8">
            Module en cours de développement - RH & Personnel 👥
            <br />
            <span className="text-sm">Fonctionnalités: Gestion employés, paie OHADA Cameroun, temps & présences, formations, déclarations sociales CNPS</span>
          </p>
        </div>
      </div>
    </div>
  );
}