// src/services/governance.service.ts
import { apiClient } from "@/lib/api-client";
import { BundleApprovalItem } from "@/types";

export const governanceService = {
  async submitApproval(
    tenantId: string,
    orgId: string,
    payload: {
      bundle_id: string;
      target_environment: "staging" | "production";
      test_suite_rego?: string;
    }
  ): Promise<BundleApprovalItem> {
    const { data } = await apiClient.post<BundleApprovalItem>(
      `/tenants/${tenantId}/orgs/${orgId}/governance/approvals`,
      payload
    );
    return data;
  },

  async listApprovals(
    tenantId: string,
    orgId: string,
    status?: "PENDING" | "APPROVED" | "REJECTED"
  ): Promise<BundleApprovalItem[]> {
    const { data } = await apiClient.get<BundleApprovalItem[]>(
      `/tenants/${tenantId}/orgs/${orgId}/governance/approvals`,
      { params: { status } }
    );
    return data;
  },

  async reviewApproval(
    tenantId: string,
    orgId: string,
    approvalId: string,
    payload: {
      action: "APPROVE" | "REJECT";
      review_notes?: string;
    }
  ): Promise<BundleApprovalItem> {
    const { data } = await apiClient.post<BundleApprovalItem>(
      `/tenants/${tenantId}/orgs/${orgId}/governance/approvals/${approvalId}/review`,
      payload
    );
    return data;
  },
};