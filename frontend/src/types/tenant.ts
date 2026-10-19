export interface Tenant {
  id: string;
  name: string;
  slug: string;
  owner_user_id: string;
  subscription_tier: string;
  subscription_status: string;
  trial_starts_at: number;
  trial_ends_at: number;
  max_organizations: number;
  max_developers: number;
  created_at: number;
  updated_at: number;
}

export interface TenantCreateRequest {
  name: string;
  slug: string;
}

export interface TenantUpdateRequest {
  name?: string;
  max_organizations?: number;
  max_developers?: number;
}

export interface TenantMember {
  id: string;
  tenant_id: string;
  user_id: string;
  tenant_role: string;
  created_at: number;
}

export interface Organization {
  id: string;
  tenant_id: string;
  name: string;
  slug: string;
  description?: string | null;
  created_at: number;
  updated_at: number;
}

export interface OrganizationCreateRequest {
  name: string;
  slug: string;
  description?: string;
}

export interface OrganizationMember {
  id: string;
  organization_id: string;
  user_id: string;
  assigned_by: string;
  org_role: "ORG_ADMIN" | "DEVELOPER" | "VIEWER";
  created_at: number;
  updated_at: number;
}

export interface ApplicationItem {
  id: string;
  organization_id: string;
  slug: string;
  display_name: string;
  description?: string | null;
  sidecar_port: number;
  created_by: string;
  created_at: number;
  updated_at: number;
}

export interface ApplicationCreateRequest {
  slug: string;
  display_name: string;
  description?: string;
  sidecar_port?: number;
}

export interface ServiceTokenResponse {
  id: string;
  name: string;
  token_prefix: string;
  created_at: number;
  expires_at?: number | null;
  revoked_at?: number | null;
  raw_token?: string;
}