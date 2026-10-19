// src/services/auth.service.ts
import { apiClient } from "@/lib/api-client";
import { AuthContextResponse, TokenExchangeRequest, TokenResponse, UserProfile } from "@/types";

export const authService = {
  async exchangeToken(payload: TokenExchangeRequest): Promise<TokenResponse> {
    const res = await apiClient.post<TokenResponse>("/auth/token", payload);
    return res.data;
  },

  async syncProfile(): Promise<UserProfile> {
    const res = await apiClient.post<UserProfile>("/auth/sync");
    return res.data;
  },

  async getMyContext(): Promise<AuthContextResponse> {
    const res = await apiClient.get<AuthContextResponse>("/auth/me");
    return res.data;
  },

  async logout(): Promise<{ status: string }> {
    const res = await apiClient.post<{ status: string }>("/auth/logout");
    return res.data;
  },
};