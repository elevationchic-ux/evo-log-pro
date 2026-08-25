'use client';

import { ReactNode } from 'react';

interface ModuleLayoutProps {
  children: ReactNode;
  module?: string;
}

export default function ModuleLayout({ children, module }: ModuleLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-100">
      {children}
    </div>
  );
}
