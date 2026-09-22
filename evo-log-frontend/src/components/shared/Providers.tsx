'use client';

import React, { useState } from 'react';
import { SessionProvider } from 'next-auth/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ComingSoonProvider } from '@/contexts/ComingSoonContext';
import { SettingsProvider } from '@/components/layout/SettingsProvider';
import { AuthProvider } from '@/components/layout/AuthProvider';

export default function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 300000, retry: 1 } },
  }));

  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <SettingsProvider>
            <ComingSoonProvider>
              {children}
            </ComingSoonProvider>
          </SettingsProvider>
        </AuthProvider>
      </QueryClientProvider>
    </SessionProvider>
  );
}