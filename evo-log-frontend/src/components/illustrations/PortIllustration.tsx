'use client';

import React from 'react';

export function PortIllustration({ className }: { className?: string } = {}) {
  return (
    <svg viewBox="0 0 500 300" className={className || "w-full h-full"} xmlns="http://www.w3.org/2000/svg">
      <rect width="500" height="300" fill="#0c4a6e" rx="12" />
      <rect x="0" y="200" width="500" height="100" fill="#0369a1" rx="0" />
      <rect x="50" y="120" width="80" height="80" fill="#64748b" />
      <rect x="60" y="100" width="10" height="20" fill="#94a3b8" />
      <rect x="100" y="90" width="10" height="30" fill="#94a3b8" />
      <rect x="200" y="140" width="120" height="60" fill="#475569" />
      <rect x="220" y="130" width="80" height="10" fill="#64748b" />
      <polygon points="350,160 420,160 400,200 370,200" fill="#1e293b" />
      <rect x="380" y="130" width="5" height="30" fill="#94a3b8" />
      <path d="M0 220 Q50 210 100 220 T200 220 T300 220 T400 220 T500 220" stroke="#38bdf8" strokeWidth="2" fill="none" opacity="0.5" />
    </svg>
  );
}