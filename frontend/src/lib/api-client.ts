// src/lib/api-client.ts
import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { tokenStore } from "./token-store";
import { ApiErrorResponse, TokenResponse } from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://100.100.30.50:7000/api/v1";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else if (token) {
      promise.resolve(token);
    }
  });
  failedQueue = [];
};

// 1. Sisipkan Access Token ke Authorization Header
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = tokenStore.getAccessToken();
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 2. Response Interceptor & Silent Auto-Refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorResponse>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (!error.response || error.response.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    const requestUrl = originalRequest.url || "";
    const isAuthRoute =
      requestUrl.includes("/auth/token") ||
      requestUrl.includes("/auth/refresh") ||
      requestUrl.includes("/auth/sync");

    const isAuthPage =
      typeof window !== "undefined" &&
      (window.location.pathname.startsWith("/login") ||
        window.location.pathname.startsWith("/callback"));

    // Cegah loop redirect jika error 401 terjadi di alur auth atau halaman auth
    if (isAuthRoute || isAuthPage) {
      if (!isAuthPage && typeof window !== "undefined") {
        tokenStore.clearTokens();
        window.location.href = "/login";
      }
      return Promise.reject(error);
    }

    // Jika proses refresh sedang berjalan, masukkan request ke antrean
    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((newToken) => {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return apiClient(originalRequest);
        })
        .catch((err) => Promise.reject(err));
    }

    const refreshToken = tokenStore.getRefreshToken();
    if (!refreshToken) {
      tokenStore.clearTokens();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      return Promise.reject(error);
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const res = await axios.post<TokenResponse>(
        `${BASE_URL}/auth/refresh`,
        { refresh_token: refreshToken },
        { headers: { "Content-Type": "application/json" } }
      );

      const { access_token, refresh_token: newRefreshToken } = res.data;
      tokenStore.setTokens(access_token, newRefreshToken);

      apiClient.defaults.headers.common.Authorization = `Bearer ${access_token}`;
      originalRequest.headers.Authorization = `Bearer ${access_token}`;

      processQueue(null, access_token);
      return apiClient(originalRequest);
    } catch (refreshErr) {
      processQueue(refreshErr as Error, null);
      tokenStore.clearTokens();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      return Promise.reject(refreshErr);
    } finally {
      isRefreshing = false;
    }
  }
);

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiErrorResponse | undefined;
    if (data?.detail) {
      if (typeof data.detail === "string") return data.detail;
      if (Array.isArray(data.detail) && data.detail.length > 0) {
        return data.detail.map((err) => `${err.loc.slice(-1)}: ${err.msg}`).join(", ");
      }
    }
    return error.message || "Terjadi kesalahan pada jaringan";
  }
  return "Terjadi kesalahan tak terduga";
}