'use client';

export default function FinanceOhadaDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">💰 Tableau de Bord Finance OHADA</h1>
          <p className="text-on-surface-variant">KPIs financiers, cash flow, créances, dettes - Conformité OHADA</p>
        </div>
        <div className="flex gap-3">
          <button className="rounded-lg border border-outline bg-surface px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container">
            Actualiser
          </button>
          <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90">
            Nouvelle Facture
          </button>
        </div>
      </div>

      {/* KPIs Financiers OHADA */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-emerald-500/10 p-3">
              <span className="material-symbols-outlined text-emerald-600">account_balance</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">847M</p>
              <p className="text-sm text-on-surface-variant">FCFA Chiffre Affaires</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-blue-500/10 p-3">
              <span className="material-symbols-outlined text-blue-600">trending_up</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">156M</p>
              <p className="text-sm text-on-surface-variant">FCFA Créances Client</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-amber-500/10 p-3">
              <span className="material-symbols-outlined text-amber-600">payments</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">89M</p>
              <p className="text-sm text-on-surface-variant">FCFA Dettes Fournisseur</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-violet-500/10 p-3">
              <span className="material-symbols-outlined text-violet-600">savings</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">234M</p>
              <p className="text-sm text-on-surface-variant">FCFA Trésorerie</p>
            </div>
          </div>
        </div>
      </div>

      {/* Fiscalité Cameroun/CEMAC */}
      <div className="erp-card">
        <div className="erp-card-header">
          <h3 className="font-semibold text-on-surface flex items-center gap-2">
            <span className="material-symbols-outlined">flag</span>
            Fiscalité Cameroun & CEMAC 🇨🇲
          </h3>
        </div>
        <div className="erp-card-body">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg border border-outline p-4">
              <p className="text-sm font-semibold text-on-surface-variant">TVA à Déclarer</p>
              <p className="text-2xl font-bold text-amber-600">12.4M FCFA</p>
              <p className="text-xs text-on-surface-variant">Échéance: 15 Sept</p>
            </div>
            <div className="rounded-lg border border-outline p-4">
              <p className="text-sm font-semibold text-on-surface-variant">IRCM Provisionné</p>
              <p className="text-2xl font-bold text-blue-600">28.7M FCFA</p>
              <p className="text-xs text-on-surface-variant">Exercice 2024</p>
            </div>
            <div className="rounded-lg border border-outline p-4">
              <p className="text-sm font-semibold text-on-surface-variant">Droits Douane</p>
              <p className="text-2xl font-bold text-emerald-600">5.8M FCFA</p>
              <p className="text-xs text-on-surface-variant">Ce mois</p>
            </div>
            <div className="rounded-lg border border-outline p-4">
              <p className="text-sm font-semibold text-on-surface-variant">TEC CEMAC</p>
              <p className="text-2xl font-bold text-violet-600">3.2M FCFA</p>
              <p className="text-xs text-on-surface-variant">Tarif extérieur commun</p>
            </div>
          </div>
        </div>
      </div>

      {/* Transactions Récentes */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="erp-card">
          <div className="erp-card-header">
            <h3 className="font-semibold text-on-surface">Factures Émises Récentes</h3>
          </div>
          <div className="erp-card-body">
            <div className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">FAC-2024-08547</p>
                  <p className="text-sm text-on-surface-variant">Client SABC • Services transport</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-on-surface">2,450,000 FCFA</p>
                  <span className="status-badge status-planified">ÉMISE</span>
                </div>
              </div>

              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">FAC-2024-08546</p>
                  <p className="text-sm text-on-surface-variant">Client XYZ Corp • Acconage</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-on-surface">1,750,000 FCFA</p>
                  <span className="status-badge status-delivered">PAYÉE</span>
                </div>
              </div>

              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">FAC-2024-08545</p>
                  <p className="text-sm text-on-surface-variant">Export Tchad • Manutention</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-on-surface">987,500 FCFA</p>
                  <span className="status-badge status-maintenance">RETARD</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="erp-card">
          <div className="erp-card-header">
            <h3 className="font-semibold text-on-surface">Échéancier Trésorerie</h3>
          </div>
          <div className="erp-card-body">
            <div className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">Semaine Prochaine</p>
                  <p className="text-sm text-on-surface-variant">Encaissements prévisionnels</p>
                </div>
                <p className="font-semibold text-emerald-600">+45M FCFA</p>
              </div>

              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">Fin de Mois</p>
                  <p className="text-sm text-on-surface-variant">Paiements fournisseurs</p>
                </div>
                <p className="font-semibold text-red-600">-28M FCFA</p>
              </div>

              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">Septembre</p>
                  <p className="text-sm text-on-surface-variant">Charges fiscales</p>
                </div>
                <p className="font-semibold text-amber-600">-18M FCFA</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}