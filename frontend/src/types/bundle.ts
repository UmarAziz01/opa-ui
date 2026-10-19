export interface PolicyBundleItem {
  id: string;
  tenant_id: string;
  organization_id?: string | null;
  application_id?: string | null;
  version: number;
  environment: "staging" | "production";
  status: string;
  bundle_size_bytes: number;
  checksum_sha256?: string | null;
  s3_object_key?: string | null;
  git_commit?: string | null;
  change_summary?: string | null;
  compiled_by?: string | null;
  created_at: number;
  snapshot_data?: Record<string, unknown>;
  file_diff?: string | null;
  download_url?: string | null;
}

export interface BundleCompileRequest {
  environment: "staging" | "production";
  change_summary?: string;
}

export interface BundleRollbackRequest {
  target_bundle_id: string;
}

export interface BundleApprovalItem {
  id: string;
  tenant_id: string;
  organization_id: string;
  bundle_id: string;
  requester_id: string;
  reviewer_id?: string | null;
  target_environment: "staging" | "production";
  status: "PENDING" | "APPROVED" | "REJECTED";
  tests_passed: boolean;
  test_output?: string | null;
  review_notes?: string | null;
  reviewed_at?: number | null;
  created_at: number;
  updated_at: number;
}

export interface BundleApprovalCreateRequest {
  bundle_id: string;
  target_environment: "staging" | "production";
  test_suite_rego?: string;
}

export interface BundleReviewActionRequest {
  action: "APPROVE" | "REJECT";
  review_notes?: string;
}