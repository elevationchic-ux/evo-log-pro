'use client';

import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export function Card({ children, className = '', noPadding = false }: CardProps) {
  return (
    <div className={`erp-card ${noPadding ? '' : 'p-5'} ${className}`}>
      {children}
    </div>
  );
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
}

export function CardHeader({ title, subtitle, action, icon }: CardHeaderProps) {
  return (
    <div className="flex items-start justify-between pb-4 border-b border-outline">
      <div className="flex items-center gap-3">
        {icon && (
          <div className="p-2 rounded-lg bg-primary/10 text-primary">
            {icon}
          </div>
        )}
        <div>
          <h3 className="font-semibold text-on-surface">{title}</h3>
          {subtitle && (
            <p className="text-sm text-on-surface-variant">{subtitle}</p>
          )}
        </div>
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export function CardContent({ children, className = '' }: CardContentProps) {
  return <div className={className}>{children}</div>;
}

export function CardFooter({ children, className = '' }: CardContentProps) {
  return (
    <div className={`pt-4 mt-4 border-t border-outline ${className}`}>
      {children}
    </div>
  );
}

export default Card;