'use client';

export default function ComptabiliteOhadaDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">📚 Comptabilité OHADA Dashboard</h1>
          <p className="text-on-surface-variant">Pilotage comptable OHADA - Écritures, Grand Livre, États Financiers</p>
        </div>
        <div className="flex gap-3">
          <button className="rounded-lg border border-outline bg-surface px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container">
            Clôture Mensuelle
          </button>
          <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90">
            Nouvelle Écriture
          </button>
        </div>
      </div>

      {/* KPIs Comptables OHADA */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-indigo-500/10 p-3">
              <span className="material-symbols-outlined text-indigo-600">menu_book</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">1,247</p>
              <p className="text-sm text-on-surface-variant">Écritures du Mois</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-emerald-500/10 p-3">
              <span className="material-symbols-outlined text-emerald-600">balance</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">✓</p>
              <p className="text-sm text-on-surface-variant">Balance Équilibrée</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-amber-500/10 p-3">
              <span className="material-symbols-outlined text-amber-600">schedule</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">J-7</p>
              <p className="text-sm text-on-surface-variant">Clôture Août</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-blue-500/10 p-3">
              <span className="material-symbols-outlined text-blue-600">receipt_long</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">847M</p>
              <p className="text-sm text-on-surface-variant">FCFA Total Bilan</p>
            </div>
          </div>
        </div>
      </div>

      <div className="erp-card">
        <div className="erp-card-header">
          <h3 className="font-semibold text-on-surface">États Financiers OHADA - Exercice 2024</h3>
        </div>
        <div className="erp-card-body">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="text-center p-6 rounded-lg border border-outline">
              <span className="material-symbols-outlined text-4xl text-emerald-600 mb-2 block">account_balance</span>
              <p className="font-semibold text-on-surface">Bilan OHADA</p>
              <p className="text-sm text-on-surface-variant">Conforme SYSCOHADA</p>
            </div>
            <div className="text-center p-6 rounded-lg border border-outline">
              <span className="material-symbols-outlined text-4xl text-blue-600 mb-2 block">trending_up</span>
              <p className="font-semibold text-on-surface">Compte de Résultat</p>
              <p className="text-sm text-on-surface-variant">Résultat net: +156M FCFA</p>
            </div>
            <div className="text-center p-6 rounded-lg border border-outline">
              <span className="material-symbols-outlined text-4xl text-violet-600 mb-2 block">receipt</span>
              <p className="font-semibold text-on-surface">TAFIRE</p>
              <p className="text-sm text-on-surface-variant">Tableau financier</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}