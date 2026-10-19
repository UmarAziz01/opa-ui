export interface AuditLogItem {
  id: string;
  tenant_id?: string | null;
  organization_id?: string | null;
  actor_id?: string | null;
  action: string;
  resource_type: string;
  resource_id?: string | null;
  ip_address?: string | null;
  user_agent?: string | null;
  changes?: Record<string, unknown> | null;
  status: string;
  timestamp: number;
  created_at: number;
}

export interface AuditLogQueryParams {
  org_id?: string;
  action?: string;
  resource_type?: string;
  actor_id?: string;
  start_time?: number;
  end_time?: number;
  limit?: number;
  offset?: number;
}