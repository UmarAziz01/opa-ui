// src/hooks/use-tenant.ts
"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tenantsService } from "@/services/tenants.service";
import { Tenant, TenantMember, TenantUpdateRequest } from "@/types";

export function useTenant() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();

  const rawTenantId = params?.tenantId;
  const tenantId =
    typeof rawTenantId === "string" && rawTenantId !== "undefined" && rawTenantId.trim() !== ""
      ? rawTenantId
      : null;

  const rawOrgId = params?.orgId;
  const orgId =
    typeof rawOrgId === "string" && rawOrgId !== "undefined" && rawOrgId.trim() !== ""
      ? rawOrgId
      : null;

  const isValidTenantId = Boolean(tenantId);

  // Detail Tenant Aktif
  const {
    data: currentTenant,
    isLoading: isLoadingTenant,
    isError: isErrorTenant,
    error: tenantError,
  } = useQuery<Tenant>({
    queryKey: ["tenant", tenantId],
    queryFn: () => tenantsService.getTenant(tenantId!),
    enabled: isValidTenantId,
    retry: false,
  });

  // Daftar Member Tenant
  const {
    data: members,
    isLoading: isLoadingMembers,
    refetch: refetchMembers,
  } = useQuery<TenantMember[]>({
    queryKey: ["tenant", tenantId, "members"],
    queryFn: () => tenantsService.listMembers(tenantId!),
    enabled: isValidTenantId,
    retry: false,
  });

  // Update Konfigurasi Tenant
  const updateTenantMutation = useMutation<Tenant, Error, TenantUpdateRequest>({
    mutationFn: (payload) => tenantsService.updateTenant(tenantId!, payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(["tenant", tenantId], updated);
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    },
  });

  // Tambah Member ke Tenant
  const addMemberMutation = useMutation<
    TenantMember,
    Error,
    { user_id: string; tenant_role: string }
  >({
    mutationFn: (payload) => tenantsService.addMember(tenantId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tenant", tenantId, "members"] });
    },
  });

  // Periksa apakah masa trial sudah habis
  const isTrialExpired =
    currentTenant?.subscription_status === "EXPIRED" ||
    (currentTenant?.trial_ends_at
      ? currentTenant.trial_ends_at <= Math.floor(Date.now() / 1000)
      : false);

  const switchTenant = (targetTenantId: string) => {
    if (targetTenantId && targetTenantId !== "undefined") {
      router.push(`/tenants/${targetTenantId}`);
    }
  };

  return {
    tenantId,
    orgId,
    tenant: currentTenant ?? null,
    members: members ?? [],
    isTrialExpired,
    isLoading: isLoadingTenant || isLoadingMembers,
    isError: isErrorTenant,
    error: tenantError,
    updateTenant: updateTenantMutation.mutateAsync,
    isUpdating: updateTenantMutation.isPending,
    addMember: addMemberMutation.mutateAsync,
    isAddingMember: addMemberMutation.isPending,
    refetchMembers,
    switchTenant,
  };
}