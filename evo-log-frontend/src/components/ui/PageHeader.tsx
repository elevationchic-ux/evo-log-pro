'use client';

import React from 'react';

interface PageHeaderProps {
  title: string;
  description?: string;
  breadcrumbs?: Array<{
    label: string;
    href?: string;
  }>;
  actions?: React.ReactNode;
  subtitle?: string;
}

export function PageHeader({ 
  title, 
  description, 
  breadcrumbs, 
  actions,
  subtitle 
}: PageHeaderProps) {
  return (
    <div className="space-y-4">
      {/* Breadcrumbs */}
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav className="flex items-center gap-2 text-sm">
          {breadcrumbs.map((crumb, index) => (
            <React.Fragment key={index}>
              {index > 0 && (
                <span className="material-symbols-outlined text-[16px] text-on-surface-variant">
                  chevron_right
                </span>
              )}
              {crumb.href ? (
                <a 
                  href={crumb.href} 
                  className="text-on-surface-variant hover:text-primary transition-colors"
                >
                  {crumb.label}
                </a>
              ) : (
                <span className="text-on-surface font-medium">{crumb.label}</span>
              )}
            </React.Fragment>
          ))}
        </nav>
      )}

      {/* Title & Description */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl sm:text-3xl font-bold text-on-surface truncate">
            {title}
          </h1>
          {description && (
            <p className="text-on-surface-variant mt-1">
              {description}
            </p>
          )}
          {subtitle && (
            <p className="text-sm text-primary mt-1 font-medium">
              {subtitle}
            </p>
          )}
        </div>
        
        {/* Actions */}
        {actions && (
          <div className="flex items-center gap-3 flex-shrink-0">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}

export default PageHeader;