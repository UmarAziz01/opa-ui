export interface PermissionItem {
  id: string;
  organization_id: string;
  resource: string;
  action: string;
  description?: string | null;
  created_at: number;
}

export interface PermissionCreateRequest {
  resource: string;
  action: string;
  description?: string;
}

export interface RoleItem {
  id: string;
  organization_id: string;
  name: string;
  description?: string | null;
  permissions: PermissionItem[];
  created_at: number;
  updated_at: number;
}

export interface RoleCreateRequest {
  name: string;
  description?: string;
  permission_ids: string[];
}

export interface RoleUpdateRequest {
  name?: string;
  description?: string;
  permission_ids?: string[];
}

export interface SubjectMappingItem {
  id: string;
  organization_id: string;
  role_id: string;
  subject_identifier: string;
  created_at: number;
}

export interface SubjectAssignRequest {
  subject_identifier: string;
  role_id: string;
}

export interface SimulateEvaluationRequest {
  subject: string;
  resource: string;
  action: string;
  context?: Record<string, unknown>;
}

export interface SimulateEvaluationResponse {
  allow: boolean;
  evaluated_at: number;
  execution_time_ms: number;
  rego_package: string;
  details?: Record<string, unknown>;
}