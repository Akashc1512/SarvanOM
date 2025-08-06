"use client";

import * as React from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { stateProviderConfig } from '@/lib/state-management';

interface StateProviderProps {
  children: React.ReactNode;
}

export function StateProvider({ children }: StateProviderProps) {
  return (
    <QueryClientProvider client={stateProviderConfig.queryClient}>
      {children}
      {stateProviderConfig.enableDevtools && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}