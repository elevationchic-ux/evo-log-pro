'use client';

import React from 'react';

const roleColors: Record<string, string> = {
  admin: 'bg-red-500/15 text-red-300',
  manager: 'bg-blue-500/15 text-blue-300',
  user: 'bg-slate-800 text-slate-100',
  viewer: 'bg-green-500/15 text-green-300',
};

interface RoleBadgeProps {
  role: string;
  size?: 'sm' | 'md' | 'lg';
}

export function RoleBadge({ role, size = 'sm' }: RoleBadgeProps) {
  const color = roleColors[role.toLowerCase()] || 'bg-slate-800 text-slate-100';
  const sizeClass = size === 'sm' ? 'px-2 py-0.5 text-xs' : size === 'md' ? 'px-3 py-1 text-sm' : 'px-4 py-1.5 text-base';

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${color} ${sizeClass}`}>
      {role}
    </span>
  );
}
