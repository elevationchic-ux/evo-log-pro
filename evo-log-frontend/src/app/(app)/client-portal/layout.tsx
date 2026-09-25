'use client';

import { ReactNode } from 'react';

export default function ClientPortalLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-800">
      {children}
    </div>
  );
}
