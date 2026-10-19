// src/services/organizations.service.ts
import { apiClient } from "@/lib/api-client";
import { Organization, OrganizationCreateRequest, OrganizationMember } from "@/types";

export const organizationsService = {
  async listOrganizations(tenantId: string): Promise<Organization[]> {
    const { data } = await apiClient.get<Organization[]>(`/tenants/${tenantId}/orgs`);
    return data;
  },

  async createOrganization(tenantId: string, payload: OrganizationCreateRequest): Promise<Organization> {
    const { data } = await apiClient.post<Organization>(`/tenants/${tenantId}/orgs`, payload);
    return data;
  },

  async getOrganization(tenantId: string, orgId: string): Promise<Organization> {
    const { data } = await apiClient.get<Organization>(`/tenants/${tenantId}/orgs/${orgId}`);
    return data;
  },

  async updateOrganization(
    tenantId: string,
    orgId: string,
    payload: { name?: string; description?: string }
  ): Promise<Organization> {
    const { data } = await apiClient.patch<Organization>(`/tenants/${tenantId}/orgs/${orgId}`, payload);
    return data;
  },

  async listMembers(tenantId: string, orgId: string): Promise<OrganizationMember[]> {
    const { data } = await apiClient.get<OrganizationMember[]>(`/tenants/${tenantId}/orgs/${orgId}/members`);
    return data;
  },

  async assignMember(
    tenantId: string,
    orgId: string,
    payload: { user_id: string; org_role: "ORG_ADMIN" | "DEVELOPER" | "VIEWER" }
  ): Promise<OrganizationMember> {
    const { data } = await apiClient.post<OrganizationMember>(`/tenants/${tenantId}/orgs/${orgId}/members`, payload);
    return data;
  },
};