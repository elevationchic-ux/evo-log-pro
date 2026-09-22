// src/components/layout/ModuleLayout.tsx - Layout principal unifié avec thème par module
'use client';

import { ReactNode } from 'react';

interface ModuleLayoutProps {
  children: ReactNode;
  module?: string;
}

export function ModuleLayout({ children }: ModuleLayoutProps) {
  return <>{children}</>;
}

export default ModuleLayout;


