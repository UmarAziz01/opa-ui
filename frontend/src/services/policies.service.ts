// src/services/policies.service.ts
import { apiClient } from "@/lib/api-client";
import {
  PermissionItem,
  RoleItem,
  SimulateEvaluationRequest,
  SimulateEvaluationResponse,
  SubjectMappingItem,
} from "@/types";

export const policiesService = {
  // ── Permissions ──
  async listPermissions(tenantId: string, orgId: string): Promise<PermissionItem[]> {
    const { data } = await apiClient.get<PermissionItem[]>(
      `/tenants/${tenantId}/orgs/${orgId}/policies/permissions`
    );
    return data;
  },

  async createPermission(
    tenantId: string,
    orgId: string,
    payload: { resource: string; action: string; description?: string }
  ): Promise<PermissionItem> {
    const { data } = await apiClient.post<PermissionItem>(
      `/tenants/${tenantId}/orgs/${orgId}/policies/permissions`,
      payload
    );
    return data;
  },

  // ── Roles & Matrix ──
  async listRoles(tenantId: string, orgId: string): Promise<RoleItem[]> {
    const { data } = await apiClient.get<RoleItem[]>(`/tenants/${tenantId}/orgs/${orgId}/policies/roles`);
    return data;
  },

  async createRole(
    tenantId: string,
    orgId: string,
    payload: { name: string; description?: string; permission_ids: string[] }
  ): Promise<RoleItem> {
    const { data } = await apiClient.post<RoleItem>(
      `/tenants/${tenantId}/orgs/${orgId}/policies/roles`,
      payload
    );
    return data;
  },

  async updateRole(
    tenantId: string,
    orgId: string,
    roleId: string,
    payload: { name?: string; description?: string; permission_ids?: string[] }
  ): Promise<RoleItem> {
    const { data } = await apiClient.patch<RoleItem>(
      `/tenants/${tenantId}/orgs/${orgId}/policies/roles/${roleId}`,
      payload
    );
    return data;
  },

  // ── Subject Role Mappings ──
  async listSubjectMappings(tenantId: string, orgId: string): Promise<SubjectMappingItem[]> {
    const { data } = await apiClient.get<SubjectMappingItem[]>(
      `/tenants/${tenantId}/orgs/${orgId}/policies/subjects`
    );
    return data;
  },

  async assignSubjectRole(
    tenantId: string,
    orgId: string,
    payload: { subject_identifier: string; role_id: string }
  ): Promise<SubjectMappingItem> {
    const { data } = await apiClient.post<SubjectMappingItem>(
      `/tenants/${tenantId}/orgs/${orgId}/policies/subjects/assign`,
      payload
    );
    return data;
  },

  // ── Dry-Run Simulator ──
  async simulateEvaluation(
    tenantId: string,
    orgId: string,
    payload: SimulateEvaluationRequest
  ): Promise<SimulateEvaluationResponse> {
    const { data } = await apiClient.post<SimulateEvaluationResponse>(
      `/tenants/${tenantId}/orgs/${orgId}/policies/simulate`,
      payload
    );
    return data;
  },

  // ── Instant Publish Bundle ──
  async publishBundle(
    tenantId: string,
    orgId: string,
    environment: "staging" | "production" = "production"
  ): Promise<string> {
    const { data } = await apiClient.post<string>(
      `/tenants/${tenantId}/orgs/${orgId}/policies/publish-bundle`,
      null,
      { params: { environment } }
    );
    return data;
  },
};