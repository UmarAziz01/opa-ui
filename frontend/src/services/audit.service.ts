// src/services/audit.service.ts
import { apiClient } from "@/lib/api-client";
import { AuditLogItem, AuditLogQueryParams } from "@/types";

export const auditService = {
  async getAuditTrail(tenantId: string, params?: AuditLogQueryParams): Promise<AuditLogItem[]> {
    const { data } = await apiClient.get<AuditLogItem[]>(`/tenants/${tenantId}/audit-logs`, {
      params,
    });
    return data;
  },
};