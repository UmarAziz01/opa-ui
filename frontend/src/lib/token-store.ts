// src/lib/token-store.ts
const ACCESS_TOKEN_KEY = "opa_access_token";
const REFRESH_TOKEN_KEY = "opa_refresh_token";

export const tokenStore = {
  setTokens: (accessToken: string, refreshToken?: string | null) => {
    if (typeof window !== "undefined") {
      sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
      if (refreshToken) {
        sessionStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
      }
    }
  },

  getAccessToken: (): string | null => {
    if (typeof window !== "undefined") {
      return sessionStorage.getItem(ACCESS_TOKEN_KEY);
    }
    return null;
  },

  getRefreshToken: (): string | null => {
    if (typeof window !== "undefined") {
      return sessionStorage.getItem(REFRESH_TOKEN_KEY);
    }
    return null;
  },

  clearTokens: () => {
    if (typeof window !== "undefined") {
      sessionStorage.removeItem(ACCESS_TOKEN_KEY);
      sessionStorage.removeItem(REFRESH_TOKEN_KEY);
    }
  },
};