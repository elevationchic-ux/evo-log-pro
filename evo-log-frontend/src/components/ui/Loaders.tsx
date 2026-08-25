'use client';

import React from 'react';

export function CardSkeletonLoader({ rows = 5 }: { rows?: number }) {
  return (
    <div className="animate-pulse space-y-3">
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="h-12 bg-gray-200 rounded" />
      ))}
    </div>
  );
}

export function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
    </div>
  );
}

export function TableSkeletonLoader({ rows = 10, cols = 5 }: { rows?: number; cols?: number }) {
  return (
    <div className="animate-pulse">
      <div className="h-10 bg-gray-200 rounded mb-4" />
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="flex gap-4 mb-3">
          {[...Array(cols)].map((_, j) => (
            <div key={j} className="h-8 bg-gray-200 rounded flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}
