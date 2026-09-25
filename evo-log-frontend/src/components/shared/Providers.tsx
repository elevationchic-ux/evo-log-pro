'use client';

import React, { useState } from 'react';
import { SessionProvider } from 'next-auth/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SettingsProvider } from '@/components/layout/SettingsProvider';
import { AuthProvider } from '@/components/layout/AuthProvider';
import ServiceWorkerRegistrar from '@/components/shared/ServiceWorkerRegistrar';

export default function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 300000, retry: 1 } },
  }));

  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <SettingsProvider>
            <ServiceWorkerRegistrar />
            {children}
          </SettingsProvider>
        </AuthProvider>
      </QueryClientProvider>
    </SessionProvider>
  );
}