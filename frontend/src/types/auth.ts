export interface UserProfile {
  id: string;
  keycloak_id: string;
  username: string;
  email: string;
  full_name: string;
  phone?: string | null;
  avatar_url?: string | null;
  user_type: string;
  status: string;
  created_at: number;
  updated_at: number;
}

export interface TenantMembershipSummary {
  tenant_id: string;
  tenant_name: string;
  tenant_slug: string;
  tenant_role: string;
  subscription_status: string;
}

export interface AuthContextResponse {
  user: UserProfile;
  roles: string[];
  tenant_memberships: TenantMembershipSummary[];
}

export interface TokenExchangeRequest {
  code: string;
  redirect_uri: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  refresh_expires_in?: number;
  id_token?: string;
}