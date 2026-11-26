'use client';

import React from 'react';

interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  cell?: (item: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyField?: string;
  onRowClick?: (item: T) => void;
  emptyMessage?: string;
  isLoading?: boolean;
  loading?: boolean;
}

export function DataTable<T extends Record<string, any>>({
  columns,
  data,
  keyField = 'id',
  onRowClick,
  emptyMessage = 'Aucune donnee',
  isLoading = false,
  loading = false,
}: DataTableProps<T>) {
  if (isLoading || loading) {
    return (
      <div className="text-center py-12 text-slate-400 flex items-center justify-center gap-2">
        <span className="material-symbols-outlined animate-spin">progress_activity</span>
        <span>Chargement...</span>
      </div>
    );
  }
  if (data.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700">
            {columns.map(col => (
              <th key={col.key} className="text-left px-4 py-3 font-medium text-slate-400">{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, idx) => (
            <tr
              key={item[keyField] || idx}
              onClick={() => onRowClick?.(item)}
              className={`border-b border-slate-700 ${onRowClick ? 'cursor-pointer hover:bg-slate-800' : ''}`}
            >
              {columns.map(col => (
                <td key={col.key} className="px-4 py-3 text-slate-200">
                  {col.render ? col.render(item) : col.cell ? col.cell(item) : item[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
