// src/app/(app)/documents/archive/page.tsx - Documents Digital Archive - Fidèle 100% au HTML original
'use client'

export default function DocumentsArchivePage() {
  return (
    <>
      <style jsx global>{`
        body { font-family: 'Inter', sans-serif; }
        .material-symbols-outlined {
          font-variation-settings: 'FILL 0, wght 400, GRAD 0, opsz 24';
        }
        .material-symbols-outlined.fill {
          font-variation-settings: 'FILL 1';
        }
      `}</style>
      <div className="bg-surface-container-low text-on-surface flex">
        
        

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col h-full bg-background overflow-hidden">
          
          

          {/* Canvas */}
          <div className="flex-1 overflow-y-auto p-gutter lg:p-margin-desktop">
            <div className="max-w-max-width mx-auto space-y-md">
              {/* Page Header */}
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-sm mb-lg">
                <div>
                  <div className="flex items-center gap-xxs text-label-sm font-label-sm text-on-surface-variant mb-xxs">
                    <span>Accueil</span>
                    <span className="material-symbols-outlined text-[14px]">chevron_right</span>
                    <span>Système</span>
                    <span className="material-symbols-outlined text-[14px]">chevron_right</span>
                    <span className="text-primary">Archivage Documents</span>
                  </div>
                  <h2 className="font-headline-lg text-headline-lg text-on-surface">Documents & Archivage</h2>
                  <p className="font-body-md text-body-md text-on-surface-variant mt-xxs">Consultez, recherchez et téléchargez les documents générés par le système.</p>
                </div>
                <div className="flex items-center gap-sm">
                  <button className="flex items-center gap-xs px-sm py-xs bg-surface-container-lowest border border-outline-variant text-on-surface font-label-md text-label-md rounded hover:bg-surface-container-low transition-colors">
                    <span className="material-symbols-outlined text-[18px]">filter_list</span>
                    Filtres Avancés
                  </button>
                  <button className="flex items-center gap-xs px-sm py-xs bg-primary text-on-primary font-label-md text-label-md rounded hover:bg-primary-fixed-dim transition-colors shadow-sm">
                    <span className="material-symbols-outlined text-[18px]">download</span>
                    Export ZIP
                  </button>
                </div>
              </div>

              {/* Search & Filters */}
              <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-md shadow-sm">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-sm">
                  <div className="col-span-1 md:col-span-2">
                    <label className="block font-label-md text-label-md text-on-surface-variant mb-xxs">Recherche Globale</label>
                    <div className="relative">
                      <span className="material-symbols-outlined absolute left-sm top-1/2 -translate-y-1/2 text-outline">search</span>
                      <input className="w-full pl-xl pr-sm py-xs border border-outline-variant rounded focus:ring-2 focus:ring-primary focus:border-primary font-body-sm text-body-sm" placeholder="N° Document, Référence, Client..." type="text"/>
                    </div>
                  </div>
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface-variant mb-xxs">Module Source</label>
                    <select className="w-full px-sm py-xs border border-outline-variant rounded focus:ring-2 focus:ring-primary focus:border-primary font-body-sm text-body-sm bg-surface-container-lowest">
                      <option>Tous les modules</option>
                      <option>Finances (Factures)</option>
                      <option>Transport (Manifestes)</option>
                      <option>Opérations (OT Reports)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block font-label-md text-label-md text-on-surface-variant mb-xxs">Période</label>
                    <div className="relative">
                      <span className="material-symbols-outlined absolute left-sm top-1/2 -translate-y-1/2 text-outline">calendar_today</span>
                      <input className="w-full pl-xl pr-sm py-xs border border-outline-variant rounded focus:ring-2 focus:ring-primary focus:border-primary font-body-sm text-body-sm cursor-pointer" placeholder="Ce mois-ci" readOnly type="text"/>
                    </div>
                  </div>
                </div>
              </div>

              {/* Bento Grid Layout for Document Categories */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-md mb-lg">
                {/* Category Card 1 */}
                <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-md shadow-sm flex flex-col hover:border-primary transition-colors cursor-pointer group">
                  <div className="flex justify-between items-start mb-sm">
                    <div className="p-sm bg-surface-container-low rounded-lg text-primary group-hover:bg-primary group-hover:text-on-primary transition-colors">
                      <span className="material-symbols-outlined fill">receipt_long</span>
                    </div>
                    <span className="font-label-sm text-label-sm text-on-surface-variant bg-surface-variant px-xs py-xxs rounded-sm">1,245 Doc</span>
                  </div>
                  <h3 className="font-title-md text-title-md text-on-surface mb-xxs">Factures & Reçus</h3>
                  <p className="font-body-sm text-body-sm text-on-surface-variant mt-auto">Dernier ajout: Aujourd'hui, 10:42</p>
                </div>
                {/* Category Card 2 */}
                <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-md shadow-sm flex flex-col hover:border-primary transition-colors cursor-pointer group">
                  <div className="flex justify-between items-start mb-sm">
                    <div className="p-sm bg-surface-container-low rounded-lg text-secondary group-hover:bg-secondary group-hover:text-on-secondary transition-colors">
                      <span className="material-symbols-outlined fill">description</span>
                    </div>
                    <span className="font-label-sm text-label-sm text-on-surface-variant bg-surface-variant px-xs py-xxs rounded-sm">842 Doc</span>
                  </div>
                  <h3 className="font-title-md text-title-md text-on-surface mb-xxs">Manifestes Navires</h3>
                  <p className="font-body-sm text-body-sm text-on-surface-variant mt-auto">Dernier ajout: Hier, 14:15</p>
                </div>
                {/* Category Card 3 */}
                <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-md shadow-sm flex flex-col hover:border-primary transition-colors cursor-pointer group">
                  <div className="flex justify-between items-start mb-sm">
                    <div className="p-sm bg-surface-container-low rounded-lg text-tertiary group-hover:bg-tertiary group-hover:text-on-tertiary transition-colors">
                      <span className="material-symbols-outlined fill">assignment</span>
                    </div>
                    <span className="font-label-sm text-label-sm text-on-surface-variant bg-surface-variant px-xs py-xxs rounded-sm">3,109 Doc</span>
                  </div>
                  <h3 className="font-title-md text-title-md text-on-surface mb-xxs">Ordres de Transit (OT)</h3>
                  <p className="font-body-sm text-body-sm text-on-surface-variant mt-auto">Dernier ajout: Aujourd'hui, 09:30</p>
                </div>
              </div>

              {/* Document List Table */}
              <div className="bg-surface-container-lowest border border-outline-variant rounded-lg shadow-sm overflow-hidden flex flex-col">
                <div className="p-sm border-b border-outline-variant bg-surface-container flex justify-between items-center">
                  <h3 className="font-title-md text-title-md text-on-surface">Documents Récents</h3>
                  <div className="flex gap-xs">
                    <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[20px]">view_list</span></button>
                    <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[20px]">grid_view</span></button>
                  </div>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-surface-container-low border-b border-outline-variant">
                        <th className="p-sm font-label-md text-label-md text-on-surface-variant font-semibold w-10">
                          <input className="rounded-sm border-outline-variant text-primary focus:ring-primary" type="checkbox"/>
                        </th>
                        <th className="p-sm font-label-md text-label-md text-on-surface-variant font-semibold">Type</th>
                        <th className="p-sm font-label-md text-label-md text-on-surface-variant font-semibold">Référence</th>
                        <th className="p-sm font-label-md text-label-md text-on-surface-variant font-semibold">Date de Génération</th>
                        <th className="p-sm font-label-md text-label-md text-on-surface-variant font-semibold">Module</th>
                        <th className="p-sm font-label-md text-label-md text-on-surface-variant font-semibold">Taille</th>
                        <th className="p-sm font-label-md text-label-md text-on-surface-variant font-semibold text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="font-data-tabular text-data-tabular">
                      {/* Row 1 */}
                      <tr className="border-b border-outline-variant hover:bg-surface-container-low transition-colors group">
                        <td className="p-sm"><input className="rounded-sm border-outline-variant text-primary focus:ring-primary" type="checkbox"/></td>
                        <td className="p-sm">
                          <div className="flex items-center gap-xs">
                            <span className="material-symbols-outlined text-[18px] text-error fill">picture_as_pdf</span>
                            <span className="font-medium">INV-2023-1042</span>
                          </div>
                        </td>
                        <td className="p-sm text-on-surface-variant">Facture Client - MAERSK</td>
                        <td className="p-sm">24 Oct 2023, 10:42</td>
                        <td className="p-sm">
                          <span className="inline-flex items-center px-xs py-xxs rounded-sm bg-primary-fixed text-on-primary-fixed font-label-sm text-label-sm">
                            Finances
                          </span>
                        </td>
                        <td className="p-sm text-on-surface-variant">1.2 MB</td>
                        <td className="p-sm text-right">
                          <div className="flex items-center justify-end gap-xs opacity-0 group-hover:opacity-100 transition-opacity">
                            <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[18px]">visibility</span></button>
                            <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[18px]">download</span></button>
                            <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[18px]">share</span></button>
                          </div>
                        </td>
                      </tr>
                      {/* Row 2 */}
                      <tr className="bg-[#F9FAFB] border-b border-outline-variant hover:bg-surface-container-low transition-colors group">
                        <td className="p-sm"><input className="rounded-sm border-outline-variant text-primary focus:ring-primary" type="checkbox"/></td>
                        <td className="p-sm">
                          <div className="flex items-center gap-xs">
                            <span className="material-symbols-outlined text-[18px] text-error fill">picture_as_pdf</span>
                            <span className="font-medium">OT-2023-8831</span>
                          </div>
                        </td>
                        <td className="p-sm text-on-surface-variant">Rapport Ordre de Transit - MSC ALINA</td>
                        <td className="p-sm">24 Oct 2023, 09:30</td>
                        <td className="p-sm">
                          <span className="inline-flex items-center px-xs py-xxs rounded-sm bg-tertiary-fixed text-on-tertiary-fixed font-label-sm text-label-sm">
                            Opérations
                          </span>
                        </td>
                        <td className="p-sm text-on-surface-variant">3.4 MB</td>
                        <td className="p-sm text-right">
                          <div className="flex items-center justify-end gap-xs opacity-0 group-hover:opacity-100 transition-opacity">
                            <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[18px]">visibility</span></button>
                            <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[18px]">download</span></button>
                            <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[18px]">share</span></button>
                          </div>
                        </td>
                      </tr>
                      {/* Row 3 */}
                      <tr className="border-b border-outline-variant hover:bg-surface-container-low transition-colors group">
                        <td className="p-sm"><input className="rounded-sm border-outline-variant text-primary focus:ring-primary" type="checkbox"/></td>
                        <td className="p-sm">
                          <div className="flex items-center gap-xs">
                            <span className="material-symbols-outlined text-[18px] text-error fill">picture_as_pdf</span>
                            <span className="font-medium">MAN-2023-092</span>
                          </div>
                        </td>
                        <td className="p-sm text-on-surface-variant">Manifeste Déchargement - CMA CGM</td>
                        <td className="p-sm">23 Oct 2023, 14:15</td>
                        <td className="p-sm">
                          <span className="inline-flex items-center px-xs py-xxs rounded-sm bg-secondary-container text-on-secondary-container font-label-sm text-label-sm">
                            Transport
                          </span>
                        </td>
                        <td className="p-sm text-on-surface-variant">8.1 MB</td>
                        <td className="p-sm text-right">
                          <div className="flex items-center justify-end gap-xs opacity-0 group-hover:opacity-100 transition-opacity">
                            <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[18px]">visibility</span></button>
                            <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[18px]">download</span></button>
                            <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[18px]">share</span></button>
                          </div>
                        </td>
                      </tr>
                      {/* Row 4 */}
                      <tr className="bg-[#F9FAFB] border-b border-outline-variant hover:bg-surface-container-low transition-colors group">
                        <td className="p-sm"><input className="rounded-sm border-outline-variant text-primary focus:ring-primary" type="checkbox"/></td>
                        <td className="p-sm">
                          <div className="flex items-center gap-xs">
                            <span className="material-symbols-outlined text-[18px] text-error fill">picture_as_pdf</span>
                            <span className="font-medium">INV-2023-1041</span>
                          </div>
                        </td>
                        <td className="p-sm text-on-surface-variant">Facture Douane - Import X</td>
                        <td className="p-sm">23 Oct 2023, 11:05</td>
                        <td className="p-sm">
                          <span className="inline-flex items-center px-xs py-xxs rounded-sm bg-primary-fixed text-on-primary-fixed font-label-sm text-label-sm">
                            Finances
                          </span>
                        </td>
                        <td className="p-sm text-on-surface-variant">0.8 MB</td>
                        <td className="p-sm text-right">
                          <div className="flex items-center justify-end gap-xs opacity-0 group-hover:opacity-100 transition-opacity">
                            <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[18px]">visibility</span></button>
                            <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[18px]">download</span></button>
                            <button className="p-xxs text-on-surface-variant hover:text-primary transition-colors"><span className="material-symbols-outlined text-[18px]">share</span></button>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                {/* Pagination */}
                <div className="p-sm border-t border-outline-variant bg-surface-container flex items-center justify-between">
                  <span className="font-body-sm text-body-sm text-on-surface-variant">Affichage de 1 à 4 sur 5,196 documents</span>
                  <div className="flex items-center gap-xs">
                    <button className="p-xs text-on-surface-variant hover:bg-surface-container-high rounded-sm disabled:opacity-50" disabled>
                      <span className="material-symbols-outlined text-[18px]">chevron_left</span>
                    </button>
                    <span className="font-body-sm text-body-sm text-on-surface px-xs">Page 1 de 130</span>
                    <button className="p-xs text-on-surface-variant hover:bg-surface-container-high rounded-sm">
                      <span className="material-symbols-outlined text-[18px]">chevron_right</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  )
}
