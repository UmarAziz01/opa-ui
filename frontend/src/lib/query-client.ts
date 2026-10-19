// src/lib/query-client.ts
import { QueryClient } from "@tanstack/react-query";

export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 30, // Data dianggap fresh selama 30 detik
        gcTime: 1000 * 60 * 5, // Cache disimpan dalam memory selama 5 menit
        retry: (failureCount, error: any) => {
          // Jangan retry jika error disebabkan oleh unauthenticated (401) atau forbidden (403)
          const status = error?.response?.status;
          if (status === 401 || status === 403 || status === 404) {
            return false;
          }
          return failureCount < 2;
        },
        refetchOnWindowFocus: false, // Hindari refetch agresif saat ganti tab browser
        refetchOnReconnect: true,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined = undefined;

export function getQueryClient(): QueryClient {
  if (typeof window === "undefined") {
    // Di server: selalu buat instance baru
    return makeQueryClient();
  }
  // Di browser: gunakan singleton pattern
  if (!browserQueryClient) {
    browserQueryClient = makeQueryClient();
  }
  return browserQueryClient;
}