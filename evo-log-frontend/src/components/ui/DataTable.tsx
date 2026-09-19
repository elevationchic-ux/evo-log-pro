'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { toast } from 'sonner';

export interface Column<T> {
  key: string;
  header: string;
  sortable?: boolean;
  width?: string;
  render?: (item: T) => React.ReactNode;
  cell?: (item: T) => React.ReactNode;
  isNumeric?: boolean;
}

export type TableDensity = 'compact' | 'normal' | 'comfortable';

export interface BulkAction<T> {
  label: string;
  icon?: string;
  onClick: (selected: T[]) => void;
  variant?: 'default' | 'danger' | 'primary';
}

export interface QuickFilter<T> {
  id: string;
  label: string;
  count?: number;
  icon?: string;
  predicate: (item: T) => boolean;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  keyField?: keyof T;
  tableId?: string;
  loading?: boolean;
  isLoading?: boolean;
  emptyMessage?: string;
  emptyTitle?: string;
  emptyAction?: {
    label: string;
    icon?: string;
    onClick: () => void;
  };
  onRowClick?: (item: T) => void;
  selectable?: boolean;
  selectedRows?: T[];
  onSelectionChange?: (selected: T[]) => void;
  bulkActions?: BulkAction<T>[];
  enableExport?: boolean;
  exportFileName?: string;
  enableCopyClipboard?: boolean;
  enableColumnCustomization?: boolean;
  quickFilters?: QuickFilter<T>[];
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
    onPageChange: (page: number) => void;
  };
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  keyField = 'id' as keyof T,
  tableId,
  loading = false,
  isLoading = false,
  emptyMessage = 'Aucune donnée disponible pour le moment.',
  emptyTitle = 'Aucun élément trouvé',
  emptyAction,
  onRowClick,
  selectable = false,
  selectedRows = [],
  onSelectionChange,
  bulkActions = [],
  enableExport = true,
  exportFileName = 'export_evolog',
  enableCopyClipboard = true,
  enableColumnCustomization = true,
  quickFilters,
  pagination,
}: DataTableProps<T>) {
  const actualLoading = loading || isLoading;
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [density, setDensity] = useState<TableDensity>('normal');
  const [activeFilterId, setActiveFilterId] = useState<string | null>(null);
  const [isColumnDropdownOpen, setIsColumnDropdownOpen] = useState(false);
  const [visibleColumnKeys, setVisibleColumnKeys] = useState<string[]>(() => columns.map(c => c.key));

  // Initialize density & visible columns from localStorage
  useEffect(() => {
    try {
      const savedDensity = localStorage.getItem('evolog_datatable_density') as TableDensity;
      if (savedDensity && ['compact', 'normal', 'comfortable'].includes(savedDensity)) {
        setDensity(savedDensity);
      }

      if (tableId) {
        const savedCols = localStorage.getItem(`evolog_cols_${tableId}`);
        if (savedCols) {
          const parsed = JSON.parse(savedCols);
          if (Array.isArray(parsed) && parsed.length > 0) {
            setVisibleColumnKeys(parsed);
          }
        }
      }
    } catch {
      // Ignored if restricted
    }
  }, [tableId]);

  const handleDensityChange = (newDensity: TableDensity) => {
    setDensity(newDensity);
    try {
      localStorage.setItem('evolog_datatable_density', newDensity);
    } catch {
      // Ignored
    }
  };

  const toggleColumnVisibility = (key: string) => {
    setVisibleColumnKeys(prev => {
      let updated: string[];
      if (prev.includes(key)) {
        if (prev.length <= 1) return prev; // Keep at least one column visible
        updated = prev.filter(k => k !== key);
      } else {
        updated = [...prev, key];
      }

      if (tableId) {
        try {
          localStorage.setItem(`evolog_cols_${tableId}`, JSON.stringify(updated));
        } catch {
          // Ignored
        }
      }
      return updated;
    });
  };

  const resetColumns = () => {
    const allKeys = columns.map(c => c.key);
    setVisibleColumnKeys(allKeys);
    if (tableId) {
      try {
        localStorage.removeItem(`evolog_cols_${tableId}`);
      } catch {
        // Ignored
      }
    }
  };

  const activeColumns = useMemo(() => {
    return columns.filter(c => visibleColumnKeys.includes(c.key));
  }, [columns, visibleColumnKeys]);

  const filteredData = useMemo(() => {
    if (!quickFilters || !activeFilterId) return data;
    const filter = quickFilters.find(f => f.id === activeFilterId);
    if (!filter) return data;
    return data.filter(filter.predicate);
  }, [data, quickFilters, activeFilterId]);

  const sortedData = useMemo(() => {
    if (!sortKey) return filteredData;
    return [...filteredData].sort((a, b) => {
      const valA = a[sortKey];
      const valB = b[sortKey];
      if (valA === valB) return 0;
      if (valA === null || valA === undefined) return 1;
      if (valB === null || valB === undefined) return -1;
      const res = valA < valB ? -1 : 1;
      return sortDirection === 'asc' ? res : -res;
    });
  }, [filteredData, sortKey, sortDirection]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const toggleRowSelection = (item: T) => {
    if (!onSelectionChange) return;
    const isSelected = selectedRows.some(row => row[keyField] === item[keyField]);
    if (isSelected) {
      onSelectionChange(selectedRows.filter(row => row[keyField] !== item[keyField]));
    } else {
      onSelectionChange([...selectedRows, item]);
    }
  };

  const toggleAllSelection = () => {
    if (!onSelectionChange) return;
    if (selectedRows.length === sortedData.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange([...sortedData]);
    }
  };

  const exportToCSV = useCallback((rowsToExport: T[] = sortedData) => {
    if (!rowsToExport || rowsToExport.length === 0) return;

    const headers = activeColumns.map(c => `"${c.header.replace(/"/g, '""')}"`).join(';');
    const rows = rowsToExport.map(item =>
      activeColumns.map(c => {
        const val = item[c.key];
        return `"${val !== undefined && val !== null ? String(val).replace(/"/g, '""') : ''}"`;
      }).join(';')
    );
    const csvContent = '\uFEFF' + [headers, ...rows].join('\r\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${exportFileName}_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast.success('Fichier CSV exporté avec succès !', { icon: '📥' });
  }, [activeColumns, sortedData, exportFileName]);

  const copyToClipboardTSV = useCallback(async () => {
    if (!sortedData || sortedData.length === 0) return;

    try {
      const headers = activeColumns.map(c => c.header).join('\t');
      const rows = sortedData.map(item =>
        activeColumns.map(c => {
          const val = item[c.key];
          return val !== undefined && val !== null ? String(val).replace(/[\t\n\r]/g, ' ') : '';
        }).join('\t')
      );
      const tsvContent = [headers, ...rows].join('\n');
      await navigator.clipboard.writeText(tsvContent);
      toast.success('Tableau copié au format Excel (TSV) !', {
        description: 'Collez directement avec Ctrl+V dans votre tableur.',
        icon: '📋',
      });
    } catch {
      toast.error('Impossible de copier dans le presse-papier');
    }
  }, [activeColumns, sortedData]);

  const densityPadding = {
    compact: 'py-1.5 px-3 text-xs',
    normal: 'py-2.5 px-4 text-sm',
    comfortable: 'py-4 px-4 text-sm',
  }[density];

  const headerDensityPadding = {
    compact: 'py-2 px-3 text-xs',
    normal: 'py-3 px-4 text-xs',
    comfortable: 'py-3.5 px-4 text-xs',
  }[density];

  if (actualLoading && data.length === 0) {
    return (
      <div className="erp-card overflow-hidden">
        <div className="animate-pulse">
          <div className="h-12 bg-slate-100 dark:bg-slate-800 border-b border-outline" />
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 border-b border-outline p-4">
              <div className="flex gap-4">
                {[...Array(5)].map((_, j) => (
                  <div key={j} className="h-4 flex-1 rounded bg-slate-100 dark:bg-slate-800" />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="erp-card overflow-hidden relative flex flex-col">
      {/* QUICK FILTER PILLS (IF PROVIDED) */}
      {quickFilters && quickFilters.length > 0 && (
        <div className="flex items-center gap-1.5 px-4 py-2.5 border-b border-outline/70 bg-surface-container-low/50 overflow-x-auto text-xs scrollbar-none">
          <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant/80 mr-1 shrink-0 flex items-center gap-1">
            <span className="material-symbols-outlined text-[14px]">filter_alt</span>
            Vues :
          </span>
          <button
            onClick={() => setActiveFilterId(null)}
            className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all shrink-0 ${
              activeFilterId === null
                ? 'bg-primary text-on-primary shadow-xs'
                : 'bg-surface border border-outline/70 text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
            }`}
          >
            Tous ({data.length})
          </button>
          {quickFilters.map(filter => {
            const count = filter.count ?? data.filter(filter.predicate).length;
            const isActive = activeFilterId === filter.id;
            return (
              <button
                key={filter.id}
                onClick={() => setActiveFilterId(isActive ? null : filter.id)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all shrink-0 ${
                  isActive
                    ? 'bg-primary text-on-primary shadow-xs'
                    : 'bg-surface border border-outline/70 text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
                }`}
              >
                {filter.icon && (
                  <span className="material-symbols-outlined text-[14px]">{filter.icon}</span>
                )}
                <span>{filter.label}</span>
                <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                  isActive ? 'bg-white/20 text-white' : 'bg-surface-container text-on-surface-variant'
                }`}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* UPPER TOOLBAR: Density, Columns Customizer, Copy Excel, Export CSV */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-outline/70 bg-surface-container-lowest/70 text-xs flex-wrap gap-2">
        <div className="flex items-center gap-2 text-on-surface-variant flex-wrap">
          <span className="font-semibold text-[11px] uppercase tracking-wider">Densité :</span>
          <div className="inline-flex rounded-lg border border-outline bg-surface p-0.5">
            <button
              onClick={() => handleDensityChange('compact')}
              title="Mode Compact (Haute densité, idéal comptabilité/stocks)"
              className={`px-2 py-0.5 rounded text-[11px] font-bold transition-colors ${
                density === 'compact'
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              Compact
            </button>
            <button
              onClick={() => handleDensityChange('normal')}
              title="Mode Normal (Standard)"
              className={`px-2 py-0.5 rounded text-[11px] font-bold transition-colors ${
                density === 'normal'
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              Normal
            </button>
            <button
              onClick={() => handleDensityChange('comfortable')}
              title="Mode Confortable (Aéré)"
              className={`px-2 py-0.5 rounded text-[11px] font-bold transition-colors ${
                density === 'comfortable'
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              Aéré
            </button>
          </div>

          {/* COLUMN CUSTOMIZER DROPDOWN */}
          {enableColumnCustomization && (
            <div className="relative">
              <button
                onClick={() => setIsColumnDropdownOpen(!isColumnDropdownOpen)}
                className="inline-flex items-center gap-1 px-2 py-1 rounded-lg border border-outline bg-surface hover:bg-surface-container text-on-surface-variant text-xs font-medium transition-colors"
                title="Personnaliser les colonnes visibles"
                aria-expanded={isColumnDropdownOpen}
              >
                <span className="material-symbols-outlined text-[15px] text-primary">view_column</span>
                <span>Colonnes ({activeColumns.length}/{columns.length})</span>
              </button>

              {isColumnDropdownOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setIsColumnDropdownOpen(false)} />
                  <div className="absolute left-0 top-full mt-1.5 w-64 rounded-xl border border-outline bg-surface shadow-xl z-50 p-2 animate-in fade-in slide-in-from-top-2 duration-150">
                    <div className="flex items-center justify-between pb-2 mb-2 border-b border-outline px-2">
                      <span className="font-bold text-[11px] uppercase tracking-wider text-on-surface-variant">Colonnes visibles</span>
                      <button
                        onClick={resetColumns}
                        className="text-[10px] text-primary hover:underline font-bold"
                      >
                        Tout afficher
                      </button>
                    </div>
                    <div className="max-h-60 overflow-y-auto space-y-1">
                      {columns.map(col => {
                        const isVisible = visibleColumnKeys.includes(col.key);
                        return (
                          <label
                            key={col.key}
                            className="flex items-center gap-2 px-2 py-1 rounded-lg hover:bg-surface-container text-xs cursor-pointer select-none text-on-surface"
                          >
                            <input
                              type="checkbox"
                              checked={isVisible}
                              onChange={() => toggleColumnVisibility(col.key)}
                              className="rounded border-outline text-primary focus:ring-primary h-3.5 w-3.5"
                            />
                            <span className="truncate">{col.header}</span>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* EXPORT & COPY BUTTONS */}
        <div className="flex items-center gap-1.5">
          {enableCopyClipboard && sortedData.length > 0 && (
            <button
              onClick={copyToClipboardTSV}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-outline hover:bg-surface-container text-on-surface transition-colors font-medium text-xs"
              title="Copier les données visibles au format Excel (Coller directement avec Ctrl+V)"
            >
              <span className="material-symbols-outlined text-[15px] text-primary">content_copy</span>
              <span>Copier Excel</span>
            </button>
          )}

          {enableExport && sortedData.length > 0 && (
            <button
              onClick={() => exportToCSV(sortedData)}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-outline hover:bg-surface-container text-on-surface transition-colors font-medium text-xs"
              title="Télécharger l'ensemble des données au format CSV"
            >
              <span className="material-symbols-outlined text-[15px] text-emerald-600">download</span>
              <span>Export CSV</span>
            </button>
          )}
        </div>
      </div>

      {/* MAIN SCROLLABLE TABLE */}
      <div className="overflow-x-auto max-h-[calc(100vh-230px)] overflow-y-auto">
        <table className="w-full text-left border-collapse">
          <thead className="sticky top-0 z-10 bg-surface-container-low/95 backdrop-blur-sm shadow-xs border-b border-outline">
            <tr>
              {selectable && (
                <th className={`w-12 ${headerDensityPadding}`}>
                  <input
                    type="checkbox"
                    checked={selectedRows.length === sortedData.length && sortedData.length > 0}
                    onChange={toggleAllSelection}
                    className="rounded border-outline text-primary focus:ring-primary h-4 w-4 cursor-pointer"
                  />
                </th>
              )}
              {activeColumns.map(col => (
                <th
                  key={col.key}
                  className={`${headerDensityPadding} font-bold text-on-surface uppercase tracking-wider ${
                    col.sortable ? 'cursor-pointer hover:bg-surface-container select-none' : ''
                  } ${col.isNumeric ? 'text-right' : ''}`}
                  style={{ width: col.width }}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className={`flex items-center gap-1.5 ${col.isNumeric ? 'justify-end' : ''}`}>
                    {col.header}
                    {col.sortable && sortKey === col.key && (
                      <span className="material-symbols-outlined text-[15px] text-primary">
                        {sortDirection === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.length === 0 ? (
              <tr>
                <td 
                  colSpan={activeColumns.length + (selectable ? 1 : 0)} 
                  className="px-6 py-16 text-center text-on-surface-variant"
                >
                  <div className="max-w-sm mx-auto flex flex-col items-center">
                    <div className="h-16 w-16 rounded-2xl bg-surface-container-low border border-outline flex items-center justify-center mb-4 text-on-surface-variant/60 shadow-inner">
                      <span className="material-symbols-outlined text-4xl">inbox</span>
                    </div>
                    <h4 className="font-bold text-base text-on-surface mb-1">{emptyTitle}</h4>
                    <p className="text-xs text-on-surface-variant mb-5 leading-relaxed">
                      {emptyMessage}
                    </p>
                    {emptyAction && (
                      <button
                        onClick={emptyAction.onClick}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-on-primary font-bold text-xs shadow-md hover:bg-primary/90 transition-transform active:scale-95"
                      >
                        <span className="material-symbols-outlined text-[18px]">
                          {emptyAction.icon || 'add'}
                        </span>
                        {emptyAction.label}
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ) : (
              sortedData.map((item, index) => {
                const isSelected = selectedRows.some(row => row[keyField] === item[keyField]);
                return (
                  <tr
                    key={item[keyField] !== undefined ? String(item[keyField]) : index}
                    className={`border-b border-outline/70 transition-colors ${
                      isSelected
                        ? 'bg-primary/5 hover:bg-primary/10'
                        : index % 2 === 1
                        ? 'bg-surface-container-lowest/40 hover:bg-surface-container-low'
                        : 'hover:bg-surface-container-low'
                    } ${onRowClick ? 'cursor-pointer' : ''}`}
                    onClick={() => onRowClick?.(item)}
                  >
                    {selectable && (
                      <td className={`w-12 ${densityPadding}`} onClick={e => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleRowSelection(item)}
                          className="rounded border-outline text-primary focus:ring-primary h-4 w-4 cursor-pointer"
                        />
                      </td>
                    )}
                    {activeColumns.map(col => {
                      const rawValue = item[col.key];
                      const isNumberVal = typeof rawValue === 'number' || col.isNumeric;

                      return (
                        <td
                          key={col.key}
                          className={`${densityPadding} text-on-surface ${
                            isNumberVal ? 'font-mono tabular-nums-erp text-right' : ''
                          }`}
                        >
                          {col.render 
                            ? col.render(item) 
                            : col.cell
                            ? col.cell(item)
                            : rawValue
                          }
                        </td>
                      );
                    })}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* FLOATING BULK ACTIONS BAR */}
      {selectable && selectedRows.length > 0 && (
        <div className="sticky bottom-3 left-0 right-0 mx-auto max-w-2xl z-30 px-4 py-3 rounded-2xl bg-surface/95 border-2 border-primary/40 shadow-2xl backdrop-blur-md flex items-center justify-between gap-4 animate-in slide-in-from-bottom-3 duration-200 mt-2">
          <div className="flex items-center gap-3">
            <span className="flex h-7 min-w-7 px-2 items-center justify-center rounded-lg bg-primary text-on-primary font-black text-xs shadow-sm">
              {selectedRows.length}
            </span>
            <span className="text-xs font-bold text-on-surface">
              {selectedRows.length === 1 ? 'ligne sélectionnée' : 'lignes sélectionnées'}
            </span>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {bulkActions.map((action, idx) => (
              <button
                key={idx}
                onClick={() => action.onClick(selectedRows)}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all active:scale-95 shadow-sm ${
                  action.variant === 'danger'
                    ? 'bg-rose-600 text-white hover:bg-rose-700'
                    : action.variant === 'primary'
                    ? 'bg-primary text-on-primary hover:bg-primary/90'
                    : 'bg-surface-container border border-outline text-on-surface hover:bg-surface-container-high'
                }`}
              >
                {action.icon && (
                  <span className="material-symbols-outlined text-[16px]">{action.icon}</span>
                )}
                {action.label}
              </button>
            ))}

            <button
              onClick={() => exportToCSV(selectedRows)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-600 text-white hover:bg-emerald-700 text-xs font-bold shadow-sm transition-all active:scale-95"
              title="Exporter uniquement les lignes sélectionnées en CSV"
            >
              <span className="material-symbols-outlined text-[16px]">file_download</span>
              Export Sélection
            </button>

            <button
              onClick={() => onSelectionChange?.([])}
              className="px-2 py-1.5 rounded-xl border border-outline hover:bg-surface-container text-on-surface-variant text-xs font-semibold"
              title="Annuler la sélection"
            >
              Désélectionner
            </button>
          </div>
        </div>
      )}

      {/* PAGINATION BAR */}
      {pagination && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-outline bg-surface-container-low mt-auto">
          <p className="text-xs text-on-surface-variant">
            Affichage de {(pagination.page - 1) * pagination.pageSize + 1} à{' '}
            {Math.min(pagination.page * pagination.pageSize, pagination.total)} sur {pagination.total} résultats
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => pagination.onPageChange(pagination.page - 1)}
              disabled={pagination.page === 1}
              className="p-1.5 rounded-lg border border-outline text-on-surface-variant hover:bg-surface-container disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <span className="material-symbols-outlined text-[18px]">chevron_left</span>
            </button>
            <span className="px-2.5 py-1 rounded-lg bg-surface-container text-xs font-bold">
              Page {pagination.page}
            </span>
            <button
              onClick={() => pagination.onPageChange(pagination.page + 1)}
              disabled={pagination.page * pagination.pageSize >= pagination.total}
              className="p-1.5 rounded-lg border border-outline text-on-surface-variant hover:bg-surface-container disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <span className="material-symbols-outlined text-[18px]">chevron_right</span>
            </button>
          </div>
        </div>
      )}

      {actualLoading && (
        <div className="absolute inset-0 bg-surface/50 backdrop-blur-[1px] flex items-center justify-center z-20">
          <div className="flex items-center gap-2 text-primary font-bold text-xs bg-surface px-4 py-2 rounded-xl shadow-lg border border-outline">
            <span className="material-symbols-outlined animate-spin text-[18px]">progress_activity</span>
            Chargement des données réelles...
          </div>
        </div>
      )}
    </div>
  );
}

export default DataTable;