'use client';
// Dashboard module 🔧 K-Maintenance Industrielle
import Link from 'next/link';

const MODULE_DIR = 'maintenance-industrielle';
const PERM = 'maintindustrielle';

export default function PageDashboard() {
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">🔧 K-Maintenance Industrielle</h1>
      <p className="text-sm text-gray-500">Centre de pilotage — selectionnez un registre ci-dessous.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border bg-white dark:bg-slate-900 p-4 shadow-sm">
          <div className="text-sm text-gray-500">Module</div>
          <div className="text-lg font-semibold">{PERM}</div>
        </div>
      </div>
    </div>
  );
}
