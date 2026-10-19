// src/services/applications.service.ts
import { apiClient } from "@/lib/api-client";
import { ApplicationCreateRequest, ApplicationItem, ServiceTokenResponse } from "@/types";

export const applicationsService = {
  async listApplications(tenantId: string, orgId: string): Promise<ApplicationItem[]> {
    const { data } = await apiClient.get<ApplicationItem[]>(`/tenants/${tenantId}/orgs/${orgId}/apps`);
    return data;
  },

  async createApplication(
    tenantId: string,
    orgId: string,
    payload: ApplicationCreateRequest
  ): Promise<ApplicationItem> {
    const { data } = await apiClient.post<ApplicationItem>(`/tenants/${tenantId}/orgs/${orgId}/apps`, payload);
    return data;
  },

  async getApplication(tenantId: string, orgId: string, appId: string): Promise<ApplicationItem> {
    const { data } = await apiClient.get<ApplicationItem>(`/tenants/${tenantId}/orgs/${orgId}/apps/${appId}`);
    return data;
  },

  // Service Tokens untuk OPA Sidecar
  async listTokens(tenantId: string, orgId: string, appId: string): Promise<ServiceTokenResponse[]> {
    const { data } = await apiClient.get<ServiceTokenResponse[]>(
      `/tenants/${tenantId}/orgs/${orgId}/apps/${appId}/tokens`
    );
    return data;
  },

  async createToken(
    tenantId: string,
    orgId: string,
    appId: string,
    payload: { name: string; expires_days?: number }
  ): Promise<ServiceTokenResponse> {
    const { data } = await apiClient.post<ServiceTokenResponse>(
      `/tenants/${tenantId}/orgs/${orgId}/apps/${appId}/tokens`,
      payload
    );
    return data;
  },

  async revokeToken(tenantId: string, orgId: string, appId: string, tokenId: string): Promise<void> {
    await apiClient.delete(`/tenants/${tenantId}/orgs/${orgId}/apps/${appId}/tokens/${tokenId}`);
  },

  // Helper pembentuk URL Server-Sent Events (SSE) logs sidecar
  getSidecarLogsStreamUrl(tenantId: string, orgId: string, appId: string): string {
    const base = process.env.NEXT_PUBLIC_API_URL || "http://100.100.30.50:7000/api/v1";
    return `${base}/tenants/${tenantId}/orgs/${orgId}/apps/${appId}/sidecar/logs`;
  },
};