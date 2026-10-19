// src/services/bundles.service.ts
import { apiClient } from "@/lib/api-client";
import { PolicyBundleItem } from "@/types";

export const bundlesService = {
  async listBundles(
    tenantId: string,
    orgId: string,
    environment?: "staging" | "production"
  ): Promise<PolicyBundleItem[]> {
    const { data } = await apiClient.get<PolicyBundleItem[]>(
      `/tenants/${tenantId}/orgs/${orgId}/bundles`,
      { params: { environment } }
    );
    return data;
  },

  async getBundleDetail(tenantId: string, orgId: string, bundleId: string): Promise<PolicyBundleItem> {
    const { data } = await apiClient.get<PolicyBundleItem>(
      `/tenants/${tenantId}/orgs/${orgId}/bundles/${bundleId}`
    );
    return data;
  },

  async compileBundle(
    tenantId: string,
    orgId: string,
    payload: { environment: "staging" | "production"; change_summary?: string }
  ): Promise<PolicyBundleItem> {
    const { data } = await apiClient.post<PolicyBundleItem>(
      `/tenants/${tenantId}/orgs/${orgId}/bundles/compile`,
      payload
    );
    return data;
  },

  async rollbackBundle(
    tenantId: string,
    orgId: string,
    payload: { target_bundle_id: string }
  ): Promise<PolicyBundleItem> {
    const { data } = await apiClient.post<PolicyBundleItem>(
      `/tenants/${tenantId}/orgs/${orgId}/bundles/rollback`,
      payload
    );
    return data;
  },
};