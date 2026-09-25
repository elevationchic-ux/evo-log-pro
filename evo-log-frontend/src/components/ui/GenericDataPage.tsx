'use client';

import React, { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import { Search, Plus, Edit2, Trash2, Eye, Download, X, FileText, ChevronLeft, ChevronRight } from 'lucide-react';
import { TableSkeletonLoader } from '@/components/ui/Loaders';
import { useI18n } from '@/hooks/useI18n';

interface Column {
  key: string;
  label: string;
  render?: (val: any, row: any) => React.ReactNode;
}

interface GenericDataPageProps {
  title: string;
  description: string;
  columns: Column[];
  data: any[];
  isLoading?: boolean;
  onAdd?: () => void;
  onExport?: () => void;
  onView?: (row: any) => void;
  onEdit?: (row: any) => void;
  onDelete?: (row: any) => void;
  primaryActionLabel?: string;
  icon?: React.ReactNode;
  /** Optional KPI cards rendered above the table */
  kpiCards?: React.ReactNode;
  /** Page size for pagination */
  pageSize?: number;
  /** Server-side pagination support */
  serverTotalPages?: number;
  serverCurrentPage?: number;
  serverTotalResults?: number;
  onPageChange?: (page: number) => void;
  onSearchChange?: (term: string) => void;
}

// ── Detail Drawer ──────────────────────────────────────────────────────────────
function DetailDrawer({
  row,
  columns,
  onClose,
}: {
  row: any;
  columns: Column[];
  onClose: () => void;
}) {
  const t = useI18n();
  const drawerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/30 backdrop-blur-sm z-[60] transition-opacity animate-in fade-in duration-200"
        onClick={onClose}
      />
      {/* Drawer */}
      <div
        ref={drawerRef}
        className="fixed right-0 top-0 h-full w-full max-w-lg bg-surface shadow-2xl z-[70] flex flex-col animate-in slide-in-from-right duration-300 border-l border-outline"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-outline bg-surface-container-low">
          <div>
            <h3 className="text-base font-bold text-on-surface">{t.common?.recordDetail || 'Détails de l\'enregistrement'}</h3>
            <p className="text-xs text-on-surface-variant mt-0.5">{t.common?.fullDataView || 'Vue complète des données'}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-surface-container rounded-xl text-on-surface-variant hover:text-on-surface transition-colors"
            aria-label={t.common?.close || 'Fermer'}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-0.5 scrollbar-sidebar">
          {columns.map((col) => (
            <div key={col.key} className="group">
              <div className="flex flex-col sm:flex-row sm:items-start gap-1 py-3.5 px-3 rounded-xl hover:bg-surface-container transition-colors">
                <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider min-w-[130px] shrink-0 pt-0.5">
                  {col.label}
                </span>
                <span className="text-sm text-on-surface font-medium flex-1 break-words">
                  {col.render
                    ? col.render(row[col.key], row)
                    : row[col.key] != null
                    ? String(row[col.key])
                    : <span className="text-on-surface-variant italic opacity-50">Non renseigné</span>}
                </span>
              </div>
              <div className="mx-3 border-b border-outline-variant group-last:border-0 opacity-50" />
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="border-t border-outline bg-surface-container-low p-4 flex justify-end gap-3 shrink-0">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl border border-outline text-on-surface font-semibold hover:bg-surface-container transition-colors text-sm"
          >
            {t.common?.close || 'Fermer'}
          </button>
        </div>
      </div>
    </>
  );
}

// ── CSV Export ──────────────────────────────────────────────────────────────────
function exportToCSV(columns: Column[], data: any[], title: string) {
  // Séparateur ';' : ouvrable directement dans Excel FR/Africain (le ',' casse les colonnes).
  // BOM UTF-8 déjà présent pour les accents.
  const sep = ';';
  const escape = (str: string) =>
    str.includes(sep) || str.includes(',') || str.includes('"') || str.includes('\n')
      ? `"${str.replace(/"/g, '""')}"`
      : str;
  const header = columns.map((c) => escape(c.label)).join(sep);
  const rows = data.map((row) =>
    columns
      .map((c) => {
        const val = row[c.key];
        return escape(val != null ? String(val) : '');
      })
      .join(sep)
  );
  const csv = [header, ...rows].join('\r\n');
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${title.replace(/\s+/g, '_').toLowerCase()}_export.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

// ── Main Component ─────────────────────────────────────────────────────────────
export default function GenericDataPage({
  title,
  description,
  columns,
  data,
  isLoading = false,
  onAdd,
  onExport,
  onView,
  onEdit,
  onDelete,
  primaryActionLabel,
  icon = <FileText className="w-5 h-5 text-primary" />,
  kpiCards,
  pageSize = 15,
  serverTotalPages,
  serverCurrentPage,
  serverTotalResults,
  onPageChange,
  onSearchChange,
}: GenericDataPageProps) {
  const t = useI18n();
  const [localSearchTerm, setLocalSearchTerm] = useState('');
  const [drawerRow, setDrawerRow] = useState<any | null>(null);
  const [localCurrentPage, setLocalCurrentPage] = useState(1);
  
  const isServerSide = serverTotalPages !== undefined;
  const currentPage = isServerSide ? (serverCurrentPage || 1) : localCurrentPage;

  const addLabel = primaryActionLabel || t.common.new;

  const handleAction = (actionFn: ((...args: any[]) => void) | undefined, _fallbackName: string, ...args: any[]) => {
    if (actionFn) actionFn(...args);
  };

  // Reset page on search or data change (client-side only)
  useEffect(() => {
    if (!isServerSide) {
      setLocalCurrentPage(1);
    }
  }, [localSearchTerm, data, isServerSide]);

  // ── Search filtering ─────────────────────────────────────────
  const handleSearchChange = (val: string) => {
    setLocalSearchTerm(val);
    if (onSearchChange) {
      onSearchChange(val);
    }
  };

  const filteredData = useMemo(() => {
    if (isServerSide) return data; // Server handles filtering
    if (!localSearchTerm.trim()) return data;
    const term = localSearchTerm.toLowerCase();
    return data.filter((row) =>
      columns.some((col) => {
        const val = row[col.key];
        if (val == null) return false;
        return String(val).toLowerCase().includes(term);
      })
    );
  }, [data, localSearchTerm, columns, isServerSide]);

  // ── Pagination ───────────────────────────────────────────────────────────
  const totalPages = isServerSide ? serverTotalPages : Math.max(1, Math.ceil(filteredData.length / pageSize));
  const totalResults = isServerSide ? (serverTotalResults || data.length) : filteredData.length;
  
  const paginatedData = useMemo(() => {
    if (isServerSide) return data; // Server handles pagination
    const start = (currentPage - 1) * pageSize;
    return filteredData.slice(start, start + pageSize);
  }, [filteredData, currentPage, pageSize, isServerSide, data]);

  // ── Handlers ─────────────────────────────────────────────────────────────
  const handleView = useCallback(
    (row: any) => {
      if (onView) {
        onView(row);
      } else {
        setDrawerRow(row);
      }
    },
    [onView]
  );

  const handleExport = useCallback(() => {
    if (onExport) {
      onExport();
    } else {
      exportToCSV(columns, filteredData, title);
    }
  }, [onExport, columns, filteredData, title]);

  const hasRowActions = !!(onView || onEdit || onDelete);

  return (
    <>
      <div className="p-3 sm:p-5 lg:p-6">

        {/* ── Page Header ────────────────────────────────────────────── */}
        <div className="flex flex-col gap-3 mb-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex-shrink-0 p-2.5 bg-surface rounded-xl border border-outline shadow-sm">
              {icon}
            </div>
            <div className="min-w-0">
              <h1 className="text-xl font-bold text-on-surface tracking-tight truncate">{title}</h1>
              <p className="text-sm text-on-surface-variant mt-0.5 truncate">{description}</p>
            </div>
          </div>

          {/* Header actions */}
          <div className="flex flex-wrap items-center gap-2 shrink-0">
            <button
              onClick={handleExport}
              className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-on-surface bg-surface border border-outline rounded-xl hover:bg-surface-container transition-all shadow-sm"
              title={t.common.export}
            >
              <Download className="w-4 h-4" />
              <span className="hidden sm:inline">{t.common.export}</span>
            </button>
            {onAdd && (
              <button
                onClick={() => handleAction(onAdd, addLabel)}
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-on-primary bg-primary rounded-xl hover:opacity-90 transition-all shadow-sm"
              >
                <Plus className="w-4 h-4" />
                <span className="hidden xs:inline">{addLabel}</span>
              </button>
            )}
          </div>
        </div>

        {/* ── KPI Cards ─────────────────────────────────────────────── */}
        {kpiCards && <div className="mb-5">{kpiCards}</div>}

        {/* ── Filters Bar ───────────────────────────────────────────── */}
        <div className="bg-surface border border-outline rounded-xl shadow-sm mb-4 p-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          {/* Search */}
          <div className="relative flex-1 min-w-0">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant w-4 h-4 pointer-events-none" />
            <input
              type="text"
              value={localSearchTerm}
              onChange={(e) => handleSearchChange(e.target.value)}
              placeholder={t.common.searchPlaceholder}
              aria-label={t.common.search}
              className="w-full pl-9 pr-9 py-2 rounded-lg border border-outline bg-surface-container-low text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:border-primary focus:ring-2 focus:ring-primary/20 focus:bg-surface focus:outline-none transition-all"
            />
            {localSearchTerm && (
              <button
                onClick={() => handleSearchChange('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface transition-colors rounded p-0.5"
                aria-label="Effacer la recherche"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Info résultats (le bouton « Filtrer » sans action a été retiré : faux contrôle UI) */}
          <div className="flex items-center gap-2 shrink-0">
            {!isLoading && (
              <span className="text-sm text-on-surface-variant whitespace-nowrap">
                <span className="font-semibold text-on-surface">{totalResults}</span>
                {' '}{totalResults !== 1 ? t.common.results : t.common.result}
                {localSearchTerm && !isServerSide && (
                  <span className="text-on-surface-variant/60"> / {data.length}</span>
                )}
              </span>
            )}
          </div>
        </div>

        {/* ── Data Table ────────────────────────────────────────────── */}
        <div className="bg-surface rounded-xl shadow-sm border border-outline overflow-hidden">
          
          {/* Mobile Card View (Visible only on small screens) */}
          <div className="md:hidden divide-y divide-outline">
            {isLoading ? (
              <div className="p-6 flex flex-col gap-4">
                <TableSkeletonLoader columns={1} rows={3} />
              </div>
            ) : paginatedData.length === 0 ? (
              <div className="p-10 text-center">
                <div className="mx-auto w-12 h-12 bg-surface-container rounded-2xl flex items-center justify-center mb-3">
                  <Search className="w-5 h-5 text-on-surface-variant opacity-50" />
                </div>
                <p className="text-on-surface font-semibold text-sm">{t.common.noResults}</p>
                <p className="text-on-surface-variant text-xs mt-1">
                  {localSearchTerm
                    ? `${t.common.noResultsFor}${localSearchTerm}${t.common.tryOtherTerm}`
                    : t.common.noData}
                </p>
              </div>
            ) : (
              paginatedData.map((row, rowIndex) => (
                <div 
                  key={rowIndex} 
                  className="p-4 hover:bg-surface-container transition-colors cursor-pointer"
                  onClick={() => handleView(row)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex flex-col">
                      <span className="font-bold text-on-surface text-base">
                        {columns[0]?.render ? columns[0].render(row[columns[0].key], row) : row[columns[0]?.key]}
                      </span>
                      {columns[1] && (
                        <span className="text-sm text-on-surface-variant mt-0.5">
                          {columns[1].render ? columns[1].render(row[columns[1].key], row) : row[columns[1].key]}
                        </span>
                      )}
                    </div>
                    {hasRowActions && (
                      <div className="flex gap-1">
                        <button
                          onClick={(e) => { e.stopPropagation(); handleView(row); }}
                          className="p-2 text-on-surface-variant bg-surface-container-low rounded-lg"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {onEdit && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleAction(onEdit, 'Modification', row);
                            }}
                            className="p-2 text-on-surface-variant bg-surface-container-low rounded-lg"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                  {columns.slice(2, 4).map((col) => (
                    <div key={col.key} className="flex justify-between items-center text-sm py-1 border-t border-outline/30 mt-2 pt-2">
                      <span className="text-on-surface-variant">{col.label}</span>
                      <span className="font-medium text-on-surface">
                        {col.render ? col.render(row[col.key], row) : row[col.key]}
                      </span>
                    </div>
                  ))}
                </div>
              ))
            )}
          </div>

          {/* Horizontal scroll wrapper for tablet/desktop */}
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[480px]">
              <thead>
                <tr className="bg-surface-container-low border-b border-outline text-[11px] uppercase tracking-wider text-on-surface-variant">
                  {columns.map((col, i) => (
                    <th key={col.key} className={`p-3.5 font-semibold whitespace-nowrap ${i === 0 ? 'pl-5' : ''}`}>
                      {col.label}
                    </th>
                  ))}
                  {hasRowActions && (
                    <th className="p-3.5 font-semibold text-right pr-5 w-[120px]">{t.common.actions}</th>
                  )}
                </tr>
              </thead>

              <tbody className="divide-y divide-outline-variant/50">
                {isLoading ? (
                  <tr>
                    <td colSpan={columns.length + (hasRowActions ? 1 : 0)} className="p-6">
                      <TableSkeletonLoader columns={columns.length} rows={5} />
                    </td>
                  </tr>
                ) : paginatedData.length === 0 ? (
                  <tr>
                    <td colSpan={columns.length + (hasRowActions ? 1 : 0)} className="p-10 text-center">
                      <div className="mx-auto w-12 h-12 bg-surface-container rounded-2xl flex items-center justify-center mb-3">
                        <Search className="w-5 h-5 text-on-surface-variant opacity-50" />
                      </div>
                      <p className="text-on-surface font-semibold text-sm">{t.common.noResults}</p>
                      <p className="text-on-surface-variant text-xs mt-1">
                        {localSearchTerm
                          ? `${t.common.noResultsFor}${localSearchTerm}${t.common.tryOtherTerm}`
                          : t.common.noData}
                      </p>
                    </td>
                  </tr>
                ) : (
                  paginatedData.map((row, rowIndex) => (
                    <tr
                      key={rowIndex}
                      className={`
                        hover:bg-primary/5 transition-colors group cursor-pointer
                        ${rowIndex % 2 === 1 ? 'bg-surface-container-lowest/60' : ''}
                      `}
                      onClick={() => handleView(row)}
                    >
                      {columns.map((col, colIndex) => (
                        <td
                          key={col.key}
                          className={`p-3.5 text-sm text-on-surface-variant ${
                            colIndex === 0 ? 'pl-5 font-medium text-on-surface' : ''
                          }`}
                        >
                          {col.render ? col.render(row[col.key], row) : row[col.key] ?? ''}
                        </td>
                      ))}

                      {hasRowActions && (
                        <td className="p-3.5 text-right pr-5">
                          {/* Actions toujours visibles : sur tablette/tactile il n'y a pas de
                              hover, un opacity-0 rendrait les boutons inaccessibles. */}
                          <div className="flex items-center justify-end gap-1">
                            <button
                              onClick={(e) => { e.stopPropagation(); handleView(row); }}
                              className="p-2 text-on-surface-variant hover:text-primary hover:bg-primary/10 rounded-lg transition-all"
                              title={t.common.view}
                              aria-label={t.common.view}
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            {onEdit && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleAction(onEdit, 'Modification', row);
                                }}
                                className="p-2 text-on-surface-variant hover:text-primary hover:bg-surface-container rounded-lg transition-colors"
                                title={t.common.edit}
                                aria-label={t.common.edit}
                              >
                                <Edit2 className="w-4 h-4" />
                              </button>
                            )}
                            {onDelete && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleAction(onDelete, 'Suppression', row);
                                }}
                                className="p-2 text-on-surface-variant hover:text-error hover:bg-error-container/50 rounded-lg transition-colors"
                                title={t.common.delete}
                                aria-label={t.common.delete}
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </td>
                      )}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* ── Pagination Footer ──────────────────────────────────── */}
          {!isLoading && totalResults > 0 && (
            <div className="px-5 py-3.5 border-t border-outline bg-surface-container-low flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <span className="text-xs text-on-surface-variant">
                {t.common.showing}{' '}
                <span className="font-semibold text-on-surface">{(currentPage - 1) * pageSize + 1}</span>
                {' – '}
                <span className="font-semibold text-on-surface">
                  {Math.min(currentPage * pageSize, totalResults)}
                </span>
                {' '}{t.common.of}{' '}
                <span className="font-semibold text-on-surface">{totalResults}</span>
                {' '}{t.common.results}
              </span>

              <div className="flex items-center gap-1">
                <button
                  onClick={() => {
                    const newPage = Math.max(1, currentPage - 1);
                    if (isServerSide && onPageChange) onPageChange(newPage);
                    else setLocalCurrentPage(newPage);
                  }}
                  disabled={currentPage === 1}
                  className={`p-1.5 rounded-lg border text-sm transition-all ${
                    currentPage === 1
                      ? 'border-outline-variant text-on-surface-variant/30 cursor-not-allowed'
                      : 'border-outline text-on-surface hover:bg-surface-container'
                  }`}
                  aria-label="Page précédente"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>

                {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                  let page: number;
                  if (totalPages <= 5) {
                    page = i + 1;
                  } else if (currentPage <= 3) {
                    page = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    page = totalPages - 4 + i;
                  } else {
                    page = currentPage - 2 + i;
                  }
                  return (
                    <button
                      key={page}
                      onClick={() => {
                        if (isServerSide && onPageChange) onPageChange(page);
                        else setLocalCurrentPage(page);
                      }}
                      className={`w-8 h-8 rounded-lg text-xs font-semibold transition-all ${
                        page === currentPage
                          ? 'bg-primary text-on-primary shadow-sm'
                          : 'text-on-surface-variant hover:bg-surface-container'
                      }`}
                    >
                      {page}
                    </button>
                  );
                })}

                <button
                  onClick={() => {
                    const newPage = Math.min(totalPages || 1, currentPage + 1);
                    if (isServerSide && onPageChange) onPageChange(newPage);
                    else setLocalCurrentPage(newPage);
                  }}
                  disabled={currentPage === totalPages}
                  className={`p-1.5 rounded-lg border text-sm transition-all ${
                    currentPage === totalPages
                      ? 'border-outline-variant text-on-surface-variant/30 cursor-not-allowed'
                      : 'border-outline text-on-surface hover:bg-surface-container'
                  }`}
                  aria-label="Page suivante"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Detail Drawer */}
      {drawerRow && (
        <DetailDrawer
          row={drawerRow}
          columns={columns}
          onClose={() => setDrawerRow(null)}
        />
      )}
    </>
  );
}
