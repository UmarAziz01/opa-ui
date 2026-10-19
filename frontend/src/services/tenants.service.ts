// src/services/tenants.service.ts
import { apiClient } from "@/lib/api-client";
import { Tenant, TenantCreateRequest, TenantMember, TenantUpdateRequest } from "@/types";

export const tenantsService = {
  async createTenant(payload: TenantCreateRequest): Promise<Tenant> {
    const { data } = await apiClient.post<Tenant>("/tenants", payload);
    return data;
  },

  async getUserTenants(): Promise<Tenant[]> {
    const { data } = await apiClient.get<Tenant[]>("/tenants");
    return data;
  },

  async getTenant(tenantId: string): Promise<Tenant> {
    const { data } = await apiClient.get<Tenant>(`/tenants/${tenantId}`);
    return data;
  },

  async updateTenant(tenantId: string, payload: TenantUpdateRequest): Promise<Tenant> {
    const { data } = await apiClient.patch<Tenant>(`/tenants/${tenantId}`, payload);
    return data;
  },

  async listMembers(tenantId: string): Promise<TenantMember[]> {
    const { data } = await apiClient.get<TenantMember[]>(`/tenants/${tenantId}/members`);
    return data;
  },

  async addMember(tenantId: string, payload: { user_id: string; tenant_role: string }): Promise<TenantMember> {
    const { data } = await apiClient.post<TenantMember>(`/tenants/${tenantId}/members`, payload);
    return data;
  },
};