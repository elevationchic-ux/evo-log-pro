// src/app/(app)/finance/billing/page.tsx - K-Finance Billing Invoicing - Fidèle 100% au HTML original
'use client'


import { TCodeSearch } from '@/components/ui/TCodeSearch'
export default function KFinanceBillingInvoicing() {
  return (
    <>
      <style jsx global>{`
        .material-symbols-outlined {
          font-variation-settings: 'FILL 0, wght 400, GRAD 0, opsz 24';
        }
        .material-symbols-outlined.fill {
          font-variation-settings: 'FILL 1';
        }
        /* Custom Scrollbar for High-Density UI */
        ::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        ::-webkit-scrollbar-track {
          background: #f0f3ff;
        }
        ::-webkit-scrollbar-thumb {
          background: #c2c6d6;
          border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
          background: #727785;
        }
      `}</style>
      <div className="bg-surface-container-low text-on-surface font-body-md h-screen flex overflow-hidden antialiased selection:bg-primary-container selection:text-on-primary-container">
      
      

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        
        

        {/* Main Stage Canvas */}
        <main className="flex-1 overflow-y-auto p-margin-desktop bg-surface-container-low flex flex-col gap-lg">
          {/* Page Header & Breadcrumbs */}
          <div className="flex flex-col gap-xs">
            <div className="flex items-center gap-2 text-label-md font-label-md text-on-surface-variant">
              <a className="hover:text-primary transition-colors" href="/finance/overview">K-Finance</a>
              <span className="material-symbols-outlined text-[14px]">chevron_right</span>
              <span className="text-on-surface">Facturation</span>
            </div>
            <div className="flex justify-between items-end">
              <div>
                <h2 className="font-headline-lg text-headline-lg text-on-surface font-semibold tracking-tight">Gestion des Factures</h2>
                <p className="font-body-md text-body-md text-on-surface-variant mt-1">Aperçu détaillé et suivi des encaissements clients.</p>
              </div>
              <div className="flex gap-sm">
                <button className="flex items-center gap-xs px-4 py-2 border border-outline-variant bg-surface hover:bg-surface-container text-on-surface font-title-md text-title-md rounded transition-colors shadow-sm">
                  <span className="material-symbols-outlined text-[18px]">download</span>
                  Exporter
                </button>
                <button className="flex items-center gap-xs px-4 py-2 bg-primary hover:bg-primary-container text-on-primary font-title-md text-title-md rounded transition-colors shadow-sm">
                  <span className="material-symbols-outlined text-[18px]">receipt_long</span>
                  Créer Facture
                </button>
              </div>
            </div>
          </div>

          {/* Bento Grid Metrics (Level 1 Surface) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-md">
            {/* Metric Card 1 */}
            <div className="bg-surface border border-outline-variant rounded p-md flex flex-col gap-sm relative overflow-hidden">
              <div className="absolute -right-4 -top-4 w-24 h-24 bg-primary/5 rounded-full blur-xl"></div>
              <div className="flex justify-between items-center z-10">
                <span className="font-label-caps text-label-caps uppercase tracking-wider text-on-surface-variant text-[11px] font-semibold">Total En Attente</span>
                <span className="material-symbols-outlined text-tertiary-fixed-dim bg-tertiary-fixed/20 p-1.5 rounded text-[20px]">pending_actions</span>
              </div>
              <div className="z-10">
                <span className="font-headline-lg text-headline-lg text-on-surface">45.2M</span>
                <span className="font-body-sm text-body-sm text-on-surface-variant ml-1">FCFA</span>
              </div>
              <div className="text-label-sm font-label-sm text-on-surface-variant z-10">14 factures en cours</div>
            </div>

            {/* Metric Card 2 */}
            <div className="bg-surface border border-outline-variant rounded p-md flex flex-col gap-sm relative overflow-hidden">
              <div className="absolute -right-4 -top-4 w-24 h-24 bg-secondary/5 rounded-full blur-xl"></div>
              <div className="flex justify-between items-center z-10">
                <span className="font-label-caps text-label-caps uppercase tracking-wider text-on-surface-variant text-[11px] font-semibold">Encaissé (Ce Mois)</span>
                <span className="material-symbols-outlined text-secondary bg-secondary/10 p-1.5 rounded text-[20px]">check_circle</span>
              </div>
              <div className="z-10">
                <span className="font-headline-lg text-headline-lg text-on-surface">128.5M</span>
                <span className="font-body-sm text-body-sm text-on-surface-variant ml-1">FCFA</span>
              </div>
              <div className="text-label-sm font-label-sm text-secondary flex items-center gap-1 z-10">
                <span className="material-symbols-outlined text-[14px]">trending_up</span> +12% vs. mois pr.
              </div>
            </div>

            {/* Metric Card 3 */}
            <div className="bg-surface border border-outline-variant rounded p-md flex flex-col gap-sm relative overflow-hidden">
              <div className="absolute -right-4 -top-4 w-24 h-24 bg-error/5 rounded-full blur-xl"></div>
              <div className="flex justify-between items-center z-10">
                <span className="font-label-caps text-label-caps uppercase tracking-wider text-on-surface-variant text-[11px] font-semibold">Échues / Impayés</span>
                <span className="material-symbols-outlined text-error bg-error/10 p-1.5 rounded text-[20px]">warning</span>
              </div>
              <div className="z-10">
                <span className="font-headline-lg text-headline-lg text-error">8.9M</span>
                <span className="font-body-sm text-body-sm text-error ml-1">FCFA</span>
              </div>
              <div className="text-label-sm font-label-sm text-error flex items-center gap-1 z-10">
                3 factures critiques
              </div>
            </div>
          </div>

          {/* Main Data Table Section */}
          <div className="bg-surface border border-outline-variant rounded flex flex-col flex-1 min-h-[400px]">
            {/* Table Toolbar */}
            <div className="p-md border-b border-outline-variant flex flex-wrap items-center justify-between gap-md bg-surface-container-lowest">
              {/* Search */}
              <div className="relative w-full max-w-xs focus-within:ring-2 focus-within:ring-primary rounded">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">search</span>
                <input className="w-full pl-10 pr-4 py-2 bg-surface-container-low border border-outline-variant rounded text-body-md font-body-md text-on-surface placeholder:text-outline focus:outline-none transition-all" placeholder="Rechercher par ID, Client..." type="text"/>
              </div>
              {/* Filters */}
              <div className="flex gap-sm">
                <button className="flex items-center gap-xs px-3 py-1.5 border border-outline-variant bg-surface hover:bg-surface-container rounded text-body-sm font-title-md text-on-surface transition-colors">
                  <span className="material-symbols-outlined text-[16px]">calendar_today</span>
                  Date: Les 30 derniers jours
                  <span className="material-symbols-outlined text-[16px]">arrow_drop_down</span>
                </button>
                <button className="flex items-center gap-xs px-3 py-1.5 border border-outline-variant bg-surface hover:bg-surface-container rounded text-body-sm font-title-md text-on-surface transition-colors">
                  <span className="material-symbols-outlined text-[16px]">filter_alt</span>
                  Statut: Tous
                  <span className="material-symbols-outlined text-[16px]">arrow_drop_down</span>
                </button>
              </div>
            </div>

            {/* High-Density Table */}
            <div className="flex-1 overflow-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-surface-container-low sticky top-0 z-20 shadow-[0_1px_0_0_#c2c6d6]">
                  <tr>
                    <th className="py-2 px-md font-label-md text-label-md text-on-surface-variant font-semibold uppercase tracking-wider w-12 text-center">
                      <input className="rounded border-outline-variant text-primary focus:ring-primary bg-surface h-4 w-4" type="checkbox" />
                    </th>
                    <th className="py-2 px-md font-label-md text-label-md text-on-surface-variant font-semibold uppercase tracking-wider">ID Facture</th>
                    <th className="py-2 px-md font-label-md text-label-md text-on-surface-variant font-semibold uppercase tracking-wider">Client / Projet</th>
                    <th className="py-2 px-md font-label-md text-label-md text-on-surface-variant font-semibold uppercase tracking-wider">Date d'Émission</th>
                    <th className="py-2 px-md font-label-md text-label-md text-on-surface-variant font-semibold uppercase tracking-wider">Échéance</th>
                    <th className="py-2 px-md font-label-md text-label-md text-on-surface-variant font-semibold uppercase tracking-wider text-right">Montant (FCFA)</th>
                    <th className="py-2 px-md font-label-md text-label-md text-on-surface-variant font-semibold uppercase tracking-wider text-center">Statut</th>
                    <th className="py-2 px-md font-label-md text-label-md text-on-surface-variant font-semibold uppercase tracking-wider w-12"></th>
                  </tr>
                </thead>
                <tbody className="font-data-tabular text-on-surface divide-y divide-outline-variant/50">
                  {/* Row 1 */}
                  <tr className="hover:bg-surface-container-high transition-colors bg-surface group">
                    <td className="py-2 px-md text-center"><input className="rounded border-outline-variant text-primary focus:ring-primary bg-surface h-4 w-4" type="checkbox" /></td>
                    <td className="py-2 px-md font-medium text-primary cursor-pointer hover:underline">FAC-2023-1042</td>
                    <td className="py-2 px-md">
                      <div className="font-medium text-on-surface">CMA CGM MALI</div>
                      <div className="text-[11px] text-on-surface-variant">Logistique Transfrontalière</div>
                    </td>
                    <td className="py-2 px-md">12 Oct 2023</td>
                    <td className="py-2 px-md text-error font-medium">12 Nov 2023</td>
                    <td className="py-2 px-md text-right font-medium">12,500,000</td>
                    <td className="py-2 px-md text-center">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-error-container text-on-error-container border border-error/20">
                        Échue
                      </span>
                    </td>
                    <td className="py-2 px-md text-right">
                      <button className="text-outline hover:text-primary transition-colors opacity-0 group-hover:opacity-100">
                        <span className="material-symbols-outlined text-[18px]">more_vert</span>
                      </button>
                    </td>
                  </tr>

                  {/* Row 2 */}
                  <tr className="hover:bg-surface-container-high transition-colors bg-[#F9FAFB] group">
                    <td className="py-2 px-md text-center"><input className="rounded border-outline-variant text-primary focus:ring-primary bg-surface h-4 w-4" type="checkbox" /></td>
                    <td className="py-2 px-md font-medium text-primary cursor-pointer hover:underline">FAC-2023-1045</td>
                    <td className="py-2 px-md">
                      <div className="font-medium text-on-surface">MAERSK LINE</div>
                      <div className="text-[11px] text-on-surface-variant">Manutention Portuaire</div>
                    </td>
                    <td className="py-2 px-md">15 Oct 2023</td>
                    <td className="py-2 px-md">15 Nov 2023</td>
                    <td className="py-2 px-md text-right font-medium">8,250,000</td>
                    <td className="py-2 px-md text-center">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-tertiary-fixed/30 text-tertiary-container border border-tertiary-fixed">
                        En Attente
                      </span>
                    </td>
                    <td className="py-2 px-md text-right">
                      <button className="text-outline hover:text-primary transition-colors opacity-0 group-hover:opacity-100">
                        <span className="material-symbols-outlined text-[18px]">more_vert</span>
                      </button>
                    </td>
                  </tr>

                  {/* Row 3 */}
                  <tr className="hover:bg-surface-container-high transition-colors bg-surface group">
                    <td className="py-2 px-md text-center"><input className="rounded border-outline-variant text-primary focus:ring-primary bg-surface h-4 w-4" type="checkbox" /></td>
                    <td className="py-2 px-md font-medium text-primary cursor-pointer hover:underline">FAC-2023-1050</td>
                    <td className="py-2 px-md">
                      <div className="font-medium text-on-surface">BOLLORÉ TRANSPORT</div>
                      <div className="text-[11px] text-on-surface-variant">Fret Terrestre</div>
                    </td>
                    <td className="py-2 px-md">18 Oct 2023</td>
                    <td className="py-2 px-md">18 Nov 2023</td>
                    <td className="py-2 px-md text-right font-medium">4,100,000</td>
                    <td className="py-2 px-md text-center">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-secondary/10 text-secondary border border-secondary/20">
                        Payée
                      </span>
                    </td>
                    <td className="py-2 px-md text-right">
                      <button className="text-outline hover:text-primary transition-colors opacity-0 group-hover:opacity-100">
                        <span className="material-symbols-outlined text-[18px]">more_vert</span>
                      </button>
                    </td>
                  </tr>

                  {/* Row 4 */}
                  <tr className="hover:bg-surface-container-high transition-colors bg-[#F9FAFB] group">
                    <td className="py-2 px-md text-center"><input className="rounded border-outline-variant text-primary focus:ring-primary bg-surface h-4 w-4" type="checkbox" /></td>
                    <td className="py-2 px-md font-medium text-primary cursor-pointer hover:underline">FAC-2023-1052</td>
                    <td className="py-2 px-md">
                      <div className="font-medium text-on-surface">MSC DAKAR</div>
                      <div className="text-[11px] text-on-surface-variant">Stockage Entrepôt C</div>
                    </td>
                    <td className="py-2 px-md">20 Oct 2023</td>
                    <td className="py-2 px-md">20 Nov 2023</td>
                    <td className="py-2 px-md text-right font-medium">1,850,000</td>
                    <td className="py-2 px-md text-center">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-tertiary-fixed/30 text-tertiary-container border border-tertiary-fixed">
                        En Attente
                      </span>
                    </td>
                    <td className="py-2 px-md text-right">
                      <button className="text-outline hover:text-primary transition-colors opacity-0 group-hover:opacity-100">
                        <span className="material-symbols-outlined text-[18px]">more_vert</span>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Pagination Footer */}
            <div className="p-3 border-t border-outline-variant bg-surface-container-lowest flex items-center justify-between text-body-sm text-on-surface-variant">
              <div>Affichage 1-4 de 42 résultats</div>
              <div className="flex gap-1">
                <button className="p-1 border border-outline-variant rounded hover:bg-surface-container disabled:opacity-50" disabled>
                  <span className="material-symbols-outlined text-[16px]">chevron_left</span>
                </button>
                <button className="px-3 py-1 border border-outline-variant rounded bg-primary text-on-primary">1</button>
                <button className="px-3 py-1 border border-outline-variant rounded hover:bg-surface-container">2</button>
                <button className="px-3 py-1 border border-outline-variant rounded hover:bg-surface-container">3</button>
                <button className="p-1 border border-outline-variant rounded hover:bg-surface-container">
                  <span className="material-symbols-outlined text-[16px]">chevron_right</span>
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
    </>
  )
}
