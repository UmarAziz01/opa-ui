"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { organizationsService } from "@/services/organizations.service";
import { applicationsService } from "@/services/applications.service";
import { bundlesService } from "@/services/bundles.service";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Cpu, History, Users } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function OrgDashboardPage() {
  const { tenantId, orgId } = useParams() as { tenantId: string; orgId: string };

  const { data: apps } = useQuery({
    queryKey: ["apps", tenantId, orgId],
    queryFn: () => applicationsService.listApplications(tenantId, orgId),
  });

  const { data: bundles } = useQuery({
    queryKey: ["bundles", tenantId, orgId],
    queryFn: () => bundlesService.listBundles(tenantId, orgId),
  });

  const { data: members } = useQuery({
    queryKey: ["orgMembers", tenantId, orgId],
    queryFn: () => organizationsService.listMembers(tenantId, orgId),
  });

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Aplikasi Aktif</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{apps?.length || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Sidecar OPA yang dialokasikan</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Bundle Terkompilasi</CardTitle>
            <History className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{bundles?.length || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Total rilis bundle policy</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Anggota Organisasi</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{members?.length || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Admin, Developer, & Viewer</p>
          </CardContent>
        </Card>
      </div>

      <div className="flex gap-4">
        <Link href={`/tenants/${tenantId}/orgs/${orgId}/policies/matrix`}>
          <Button size="sm">Buka RBAC Matrix</Button>
        </Link>
        <Link href={`/tenants/${tenantId}/orgs/${orgId}/bundles`}>
          <Button size="sm" variant="outline">Kompilasi Bundle Baru</Button>
        </Link>
      </div>
    </div>
  );
}