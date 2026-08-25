'use client';

import React, { useState } from 'react';

interface Column<T> {
  key: string;
  header: string;
  sortable?: boolean;
  width?: string;
  render?: (item: T) => React.ReactNode;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  keyField: keyof T;
  loading?: boolean;
  emptyMessage?: string;
  onRowClick?: (item: T) => void;
  selectable?: boolean;
  selectedRows?: T[];
  onSelectionChange?: (selected: T[]) => void;
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
  keyField,
  loading = false,
  emptyMessage = 'Aucune donnée disponible',
  onRowClick,
  selectable = false,
  selectedRows = [],
  onSelectionChange,
  pagination,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

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
    
    if (selectedRows.length === data.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange([...data]);
    }
  };

  if (loading) {
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
    <div className="erp-card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-surface-container-low border-b border-outline">
              {selectable && (
                <th className="w-12 px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedRows.length === data.length && data.length > 0}
                    onChange={toggleAllSelection}
                    className="rounded border-outline text-primary focus:ring-primary"
                  />
                </th>
              )}
              {columns.map(col => (
                <th
                  key={col.key}
                  className={`px-4 py-3 text-left text-sm font-semibold text-on-surface ${
                    col.sortable ? 'cursor-pointer hover:bg-surface-container select-none' : ''
                  }`}
                  style={{ width: col.width }}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className="flex items-center gap-2">
                    {col.header}
                    {col.sortable && sortKey === col.key && (
                      <span className="material-symbols-outlined text-[16px]">
                        {sortDirection === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.length === 0 ? (
              <tr>
                <td 
                  colSpan={columns.length + (selectable ? 1 : 0)} 
                  className="px-4 py-12 text-center text-on-surface-variant"
                >
                  <span className="material-symbols-outlined text-4xl mb-2 block opacity-50">
                    inbox
                  </span>
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((item, index) => (
                <tr
                  key={String(item[keyField])}
                  className={`border-b border-outline transition-colors hover:bg-surface-container-low ${
                    onRowClick ? 'cursor-pointer' : ''
                  } ${index % 2 === 1 ? 'bg-surface-container-lowest/30' : ''}`}
                  onClick={() => onRowClick?.(item)}
                >
                  {selectable && (
                    <td className="w-12 px-4 py-3" onClick={e => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={selectedRows.some(row => row[keyField] === item[keyField])}
                        onChange={() => toggleRowSelection(item)}
                        className="rounded border-outline text-primary focus:ring-primary"
                      />
                    </td>
                  )}
                  {columns.map(col => (
                    <td key={col.key} className="px-4 py-3 text-sm text-on-surface">
                      {col.render 
                        ? col.render(item) 
                        : item[col.key]
                      }
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {pagination && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-outline bg-surface-container-low">
          <p className="text-sm text-on-surface-variant">
            Affichage de {(pagination.page - 1) * pagination.pageSize + 1} à{' '}
            {Math.min(pagination.page * pagination.pageSize, pagination.total)} sur {pagination.total} résultats
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => pagination.onPageChange(pagination.page - 1)}
              disabled={pagination.page === 1}
              className="p-2 rounded-lg border border-outline text-on-surface-variant hover:bg-surface-container disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="material-symbols-outlined text-[20px]">chevron_left</span>
            </button>
            <span className="px-3 py-1 rounded-lg bg-surface-container text-sm font-medium">
              Page {pagination.page}
            </span>
            <button
              onClick={() => pagination.onPageChange(pagination.page + 1)}
              disabled={pagination.page * pagination.pageSize >= pagination.total}
              className="p-2 rounded-lg border border-outline text-on-surface-variant hover:bg-surface-container disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="material-symbols-outlined text-[20px]">chevron_right</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DataTable;