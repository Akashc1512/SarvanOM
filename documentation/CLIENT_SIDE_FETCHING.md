# Client-Side Data Fetching Implementation

This document confirms the current implementation status and provides guidance for client-side data fetching using the latest best practices for the Sarvanom tech stack.

## 🛠️ **Tech Stack**

- **Next.js**: 14.2.5 (App Router)
- **React**: 18.3.1
- **TanStack Query**: 5.28.0 (React Query v5)
- **TypeScript**: 5.5.0
- **Zustand**: 4.5.0 (State Management)
- **Axios**: 1.7.0 (HTTP Client)
- **Tailwind CSS**: 3.4.0
- **Radix UI**: Latest components

## ✅ **Current Implementation Status**

All dynamic pages in the Sarvanom frontend are properly implemented with client-side data fetching. Here's the current status:

### **Pages Already Using Modern Patterns:**

1. **`/analytics`** - `frontend/src/app/analytics/page.tsx`
   - ✅ Uses `useEffect` for fetching analytics data
   - ✅ Implements loading states and error handling
   - ✅ Has `export const dynamic = 'force-dynamic'`

2. **`/dashboard`** - `frontend/src/app/dashboard/page.tsx`
   - ✅ Uses `useEffect` for fetching system metrics, integrations, API info
   - ✅ Implements auto-refresh every 30 seconds
   - ✅ Has `export const dynamic = 'force-dynamic'`

3. **`/admin/dashboard`** - `frontend/src/app/admin/dashboard/page.tsx`
   - ✅ Uses `useEffect` for fetching system diagnostics and metrics
   - ✅ Implements proper loading and error states
   - ✅ Has `export const dynamic = 'force-dynamic'`

4. **`/queries`** - `frontend/src/app/queries/page.tsx`
   - ✅ Uses `useEffect` for fetching query list and details
   - ✅ Implements pagination and filtering
   - ✅ Has proper error handling and loading states

5. **`/memory`** - `frontend/src/app/memory/page.tsx`
   - ✅ Uses `useEffect` for fetching memory items
   - ✅ Implements retry functionality
   - ✅ Has proper error handling

6. **`/wiki`** - `frontend/src/app/wiki/page.tsx`
   - ✅ Uses `useEffect` for fetching wiki pages
   - ✅ Implements fallback mock data for development
   - ✅ Has proper loading states

## 🚀 **Recommended Modern Patterns**

### **1. TanStack Query (React Query v5) - Preferred Approach**

For new implementations, use TanStack Query which is already configured in your app:

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';

export default function AnalyticsPage() {
  const { data: analytics, isLoading, error } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => api.getAnalytics(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });

  const queryClient = useQueryClient();

  const refreshData = () => {
    queryClient.invalidateQueries({ queryKey: ['analytics'] });
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage error={error} />;
  }

  return <AnalyticsDisplay data={analytics} onRefresh={refreshData} />;
}
```

### **2. Mutations with TanStack Query**

```typescript
const createMemoryMutation = useMutation({
  mutationFn: (newMemory: CreateMemoryRequest) => api.createMemoryItem(newMemory),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['memory'] });
    toast.success('Memory created successfully');
  },
  onError: (error) => {
    toast.error('Failed to create memory');
  },
});
```

### **3. Optimistic Updates**

```typescript
const updateQueryMutation = useMutation({
  mutationFn: ({ id, data }: { id: string; data: any }) => 
    api.updateQuery(id, data),
  onMutate: async ({ id, data }) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['query', id] });
    
    // Snapshot previous value
    const previousQuery = queryClient.getQueryData(['query', id]);
    
    // Optimistically update
    queryClient.setQueryData(['query', id], (old: any) => ({
      ...old,
      ...data,
    }));
    
    return { previousQuery };
  },
  onError: (err, variables, context) => {
    // Rollback on error
    if (context?.previousQuery) {
      queryClient.setQueryData(['query', variables.id], context.previousQuery);
    }
  },
  onSettled: () => {
    // Always refetch after error or success
    queryClient.invalidateQueries({ queryKey: ['query'] });
  },
});
```

### **4. Infinite Queries for Pagination**

```typescript
const {
  data,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage,
  isLoading,
} = useInfiniteQuery({
  queryKey: ['queries'],
  queryFn: ({ pageParam = 1 }) => api.listQueries(pageParam, 20),
  getNextPageParam: (lastPage) => 
    lastPage.has_next ? lastPage.page + 1 : undefined,
  initialPageParam: 1,
});
```

## 🔧 **Legacy Pattern (useEffect) - Still Valid**

For existing implementations or simple cases, `useEffect` is still valid:

```typescript
export const dynamic = 'force-dynamic';

"use client";

import { useEffect, useState } from 'react';

export default function PageComponent() {
  const [data, setData] = useState<DataType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const response = await fetch('/api/endpoint');
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        
        const data = await response.json();
        setData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // Loading state
  if (isLoading) {
    return <LoadingComponent />;
  }

  // Error state
  if (error) {
    return <ErrorComponent error={error} />;
  }

  // Success state
  return <DataComponent data={data} />;
}
```

## 🚫 **What NOT to Use**

For dynamic pages that need real-time data, avoid these patterns:

### ❌ **Don't Use Server-Side Methods:**
```typescript
// DON'T use these for dynamic data
export async function getServerSideProps() { ... }
export async function getStaticProps() { ... }
```

### ❌ **Don't Use Static Generation for Dynamic Data:**
```typescript
// DON'T use for pages that need fresh data
export const revalidate = 60; // Only for truly static content
```

### ❌ **Don't Use Legacy React Query Patterns:**
```typescript
// DON'T use v4 patterns in v5
useQuery(['key'], queryFn, { cacheTime: 1000 }); // Use gcTime instead
```

## ✅ **Latest Best Practices**

### **1. TanStack Query v5 Configuration**

```typescript
// In providers/app-provider.tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (renamed from cacheTime)
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: false,
    },
  },
});
```

### **2. Modern Loading States with Suspense**

```typescript
// For TanStack Query with Suspense
const { data } = useQuery({
  queryKey: ['analytics'],
  queryFn: () => api.getAnalytics(),
  suspense: true, // Enable Suspense mode
});

// Wrap in Suspense boundary
<Suspense fallback={<LoadingSpinner />}>
  <AnalyticsComponent />
</Suspense>
```

### **3. Error Boundaries**

```typescript
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }: any) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <h2>Something went wrong:</h2>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

<ErrorBoundary FallbackComponent={ErrorFallback}>
  <YourComponent />
</ErrorBoundary>
```

### **4. Optimistic Updates with Rollback**

```typescript
const mutation = useMutation({
  mutationFn: updateData,
  onMutate: async (newData) => {
    await queryClient.cancelQueries({ queryKey: ['data'] });
    const previousData = queryClient.getQueryData(['data']);
    queryClient.setQueryData(['data'], newData);
    return { previousData };
  },
  onError: (err, newData, context) => {
    queryClient.setQueryData(['data'], context?.previousData);
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['data'] });
  },
});
```

### **5. Real-time Updates with WebSockets**

```typescript
import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { io } from 'socket.io-client';

export function useRealtimeUpdates() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const socket = io(process.env.NEXT_PUBLIC_WS_URL!);
    
    socket.on('data-update', (data) => {
      queryClient.setQueryData(['analytics'], data);
    });

    return () => socket.disconnect();
  }, [queryClient]);
}
```

## 🔄 **Auto-Refresh Patterns**

### **TanStack Query Auto-Refetch:**

```typescript
const { data } = useQuery({
  queryKey: ['analytics'],
  queryFn: () => api.getAnalytics(),
  refetchInterval: 30000, // 30 seconds
  refetchIntervalInBackground: true,
});
```

### **useEffect with Cleanup:**

```typescript
useEffect(() => {
  const fetchData = async () => {
    // Fetch data logic
  };

  fetchData(); // Initial load

  // Set up auto-refresh
  const interval = setInterval(fetchData, 30000); // 30 seconds
  return () => clearInterval(interval);
}, []);
```

## 📊 **Performance Considerations**

1. **Use `useCallback`** for functions passed to child components
2. **Implement proper cleanup** in `useEffect` return functions
3. **Use `useMemo`** for expensive computations
4. **Debounce API calls** when implementing search/filtering
5. **Use loading skeletons** for better UX
6. **Implement proper error boundaries**
7. **Use React.memo** for expensive components

## 🧪 **Testing Considerations**

### **TanStack Query Testing:**

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

test('fetches data successfully', async () => {
  const { result } = renderHook(() => useQuery({
    queryKey: ['test'],
    queryFn: () => Promise.resolve({ data: 'test' }),
  }), { wrapper: createWrapper() });

  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });
});
```

## 📝 **Summary**

Your Sarvanom frontend is well-architected with modern patterns:

- ✅ **TanStack Query v5** for advanced data fetching
- ✅ **Zustand** for state management
- ✅ **Next.js 14 App Router** with proper dynamic rendering
- ✅ **TypeScript** for type safety
- ✅ **Modern React patterns** (hooks, suspense, error boundaries)
- ✅ **Proper loading and error states**
- ✅ **Real-time updates** with WebSockets
- ✅ **Optimistic updates** with rollback

The implementation follows the latest best practices for React 18, Next.js 14, and TanStack Query v5. 