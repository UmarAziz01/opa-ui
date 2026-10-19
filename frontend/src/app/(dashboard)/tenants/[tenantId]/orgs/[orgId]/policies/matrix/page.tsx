"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { policiesService } from "@/services/policies.service";
import { RbacMatrixGrid } from "@/components/rbac/RbacMatrixGrid";
import { SubjectAssignmentModal } from "@/components/rbac/SubjectAssignmentModal";
import { Button } from "@/components/ui/button";
import { Plus, UserPlus } from "lucide-react";

export default function RbacMatrixPage() {
  const { tenantId, orgId } = useParams() as { tenantId: string; orgId: string };
  const queryClient = useQueryClient();
  const [isAssignOpen, setIsAssignOpen] = useState(false);

  const { data: roles } = useQuery({
    queryKey: ["roles", tenantId, orgId],
    queryFn: () => policiesService.listRoles(tenantId, orgId),
  });

  const { data: permissions } = useQuery({
    queryKey: ["permissions", tenantId, orgId],
    queryFn: () => policiesService.listPermissions(tenantId, orgId),
  });

  const updateRoleMutation = useMutation({
    mutationFn: ({ roleId, permissionIds }: { roleId: string; permissionIds: string[] }) =>
      policiesService.updateRole(tenantId, orgId, roleId, { permission_ids: permissionIds }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles", tenantId, orgId] });
    },
  });

  const handleToggle = (roleId: string, permissionId: string, isChecked: boolean) => {
    const role = roles?.find((r) => r.id === roleId);
    if (!role) return;

    const currentPermIds = role.permissions.map((p) => p.id);
    const updatedIds = isChecked
      ? [...currentPermIds, permissionId]
      : currentPermIds.filter((id) => id !== permissionId);

    updateRoleMutation.mutate({ roleId, permissionIds: updatedIds });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold tracking-tight">Interactive RBAC Matrix</h3>
          <p className="text-xs text-muted-foreground">Hubungkan relasi role dan permission secara visual.</p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => setIsAssignOpen(true)}>
            <UserPlus className="h-4 w-4 mr-1" /> Tugaskan Subjek
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-1" /> Buat Role Baru
          </Button>
        </div>
      </div>

      <RbacMatrixGrid
        roles={roles || []}
        permissions={permissions || []}
        onTogglePermission={handleToggle}
      />

      <SubjectAssignmentModal
        isOpen={isAssignOpen}
        onClose={() => setIsAssignOpen(false)}
        roles={roles || []}
        onSubmit={async (subject, roleId) => {
          await policiesService.assignSubjectRole(tenantId, orgId, {
            subject_identifier: subject,
            role_id: roleId,
          });
        }}
      />
    </div>
  );
}