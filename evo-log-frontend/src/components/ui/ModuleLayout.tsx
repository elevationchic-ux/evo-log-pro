'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';

interface ModuleLayoutProps {
  children: React.ReactNode;
  moduleKey: string;
  moduleTitle: string;
  moduleIcon: string;
  subModules: Array<{
    key: string;
    label: string;
    path: string;
    icon?: string;
    badge?: string;
  }>;
}

export function ModuleLayout({ 
  children, 
  moduleKey, 
  moduleTitle, 
  moduleIcon,
  subModules 
}: ModuleLayoutProps) {
  const pathname = usePathname();

  // Get current sub-module based on pathname
  const currentSubModule = subModules.find(sub => 
    pathname === sub.path || pathname.startsWith(sub.path + '/')
  )?.key || 'dashboard';

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="flex items-center gap-4 p-4 rounded-xl bg-gradient-to-r from-primary/10 to-transparent border border-primary/20">
        <div className="p-3 rounded-xl bg-primary/10">
          <span className="material-symbols-outlined text-3xl text-primary">
            {moduleIcon}
          </span>
        </div>
        <div>
          <h1 className="text-2xl font-bold text-on-surface">{moduleTitle}</h1>
          <p className="text-sm text-on-surface-variant">
            Navigation vers les sous-modules
          </p>
        </div>
      </div>

      {/* Sub-module Tabs */}
      <div className="flex flex-wrap gap-2">
        {subModules.map((sub) => {
          const isActive = currentSubModule === sub.key || pathname === sub.path;
          
          return (
            <Link
              key={sub.key}
              href={sub.path}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-primary text-on-primary shadow-md'
                  : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high border border-outline'
              }`}
            >
              {sub.icon && (
                <span className="material-symbols-outlined text-[18px]">
                  {sub.icon}
                </span>
              )}
              <span>{sub.label}</span>
              {sub.badge && (
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                  isActive 
                    ? 'bg-white/20 text-white' 
                    : 'bg-primary/10 text-primary'
                }`}>
                  {sub.badge}
                </span>
              )}
            </Link>
          );
        })}
      </div>

      {/* Main Content */}
      <div className="min-h-[400px]">
        {children}
      </div>
    </div>
  );
}

export default ModuleLayout;