// src/hooks/use-auth.ts
"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { authService } from "@/services/auth.service";
import { AuthContextResponse, TokenExchangeRequest, TokenResponse, UserProfile } from "@/types";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { tokenStore } from "@/lib/token-store";

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [hasToken, setHasToken] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setHasToken(Boolean(tokenStore.getAccessToken()));
    }
  }, []);

  const {
    data: authContext,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<AuthContextResponse>({
    queryKey: ["auth", "me"],
    queryFn: () => authService.getMyContext(),
    enabled: hasToken,
    retry: false,
    staleTime: 1000 * 60 * 5,
  });

  const syncProfileMutation = useMutation<UserProfile, Error>({
    mutationFn: () => authService.syncProfile(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    },
  });

  const exchangeTokenMutation = useMutation<TokenResponse, Error, TokenExchangeRequest>({
    mutationFn: (payload) => authService.exchangeToken(payload),
    onSuccess: (data) => {
      tokenStore.setTokens(data.access_token, data.refresh_token);
      setHasToken(true);
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    },
  });

  const login = () => {
    const keycloakUrl = process.env.NEXT_PUBLIC_KEYCLOAK_URL || "https://d-sso.4212.my.id";
    const realm = process.env.NEXT_PUBLIC_KEYCLOAK_REALM || "master";
    const clientId = process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID || "one-auth";
    const redirectUri = encodeURIComponent(
      process.env.NEXT_PUBLIC_OIDC_REDIRECT_URI || `${window.location.origin}/callback`
    );

    const loginUrl = `${keycloakUrl}/realms/${realm}/protocol/openid-connect/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=openid%20profile%20email`;
    window.location.href = loginUrl;
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch {
      // Abaikan jika ada kegagalan jaringan saat logout
    } finally {
      tokenStore.clearTokens();
      setHasToken(false);
      queryClient.clear();
      router.push("/login");
    }
  };

  return {
    user: authContext?.user ?? null,
    roles: authContext?.roles ?? [],
    tenantMemberships: authContext?.tenant_memberships ?? [],
    isAuthenticated: hasToken && Boolean(authContext?.user),
    isLoading,
    isError,
    error,
    refetchUser: refetch,
    syncProfile: syncProfileMutation.mutateAsync,
    isSyncing: syncProfileMutation.isPending,
    exchangeToken: exchangeTokenMutation.mutateAsync,
    isExchanging: exchangeTokenMutation.isPending,
    login,
    logout,
  };
}