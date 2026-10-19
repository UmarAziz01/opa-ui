"use client";

import { useMemo } from "react";
import { RoleItem, PermissionItem } from "@/types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";

interface RbacMatrixGridProps {
  roles: RoleItem[];
  permissions: PermissionItem[];
  onTogglePermission: (roleId: string, permissionId: string, isChecked: boolean) => void;
  disabled?: boolean;
}

export function RbacMatrixGrid({
  roles,
  permissions,
  onTogglePermission,
  disabled = false,
}: RbacMatrixGridProps) {
  // Mapping permission ID aktif per role untuk lookup cepat O(1)
  const rolePermMap = useMemo(() => {
    const map = new Map<string, Set<string>>();
    roles.forEach((r) => {
      map.set(r.id, new Set(r.permissions.map((p) => p.id)));
    });
    return map;
  }, [roles]);

  return (
    <div className="rounded-md border overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[250px]">Permission (Resource:Action)</TableHead>
            {roles.map((role) => (
              <TableHead key={role.id} className="text-center min-w-[120px]">
                {role.name}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {permissions.map((perm) => (
            <TableRow key={perm.id}>
              <TableCell className="font-mono text-xs">
                {perm.resource}:{perm.action}
              </TableCell>
              {roles.map((role) => {
                const isChecked = rolePermMap.get(role.id)?.has(perm.id) ?? false;
                return (
                  <TableCell key={role.id} className="text-center">
                    <Checkbox
                      checked={isChecked}
                      disabled={disabled}
                      onCheckedChange={(checked) =>
                        onTogglePermission(role.id, perm.id, Boolean(checked))
                      }
                    />
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}