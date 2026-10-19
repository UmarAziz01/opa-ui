"use client";

import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { bundlesService } from "@/services/bundles.service";
import { formatLocalTime } from "@/lib/epoch";
import { formatBytes } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { History, RotateCcw, PackageCheck } from "lucide-react";

export default function BundlesHistoryPage() {
  const { tenantId, orgId } = useParams() as { tenantId: string; orgId: string };
  const queryClient = useQueryClient();

  const { data: bundles } = useQuery({
    queryKey: ["bundles", tenantId, orgId],
    queryFn: () => bundlesService.listBundles(tenantId, orgId),
  });

  const compileMutation = useMutation({
    mutationFn: () =>
      bundlesService.compileBundle(tenantId, orgId, {
        environment: "production",
        change_summary: "Manual trigger bundle build",
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["bundles", tenantId, orgId] }),
  });

  const rollbackMutation = useMutation({
    mutationFn: (target_bundle_id: string) =>
      bundlesService.rollbackBundle(tenantId, orgId, { target_bundle_id }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["bundles", tenantId, orgId] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold tracking-tight">Rilis Bundle Policy (GitOps)</h3>
          <p className="text-xs text-muted-foreground">Daftar arsip bundle tar.gz yang didistribusikan ke S3 MinIO.</p>
        </div>
        <Button size="sm" onClick={() => compileMutation.mutate()} disabled={compileMutation.isPending}>
          <PackageCheck className="h-4 w-4 mr-1" />
          {compileMutation.isPending ? "Mengompilasi..." : "Kompilasi Bundle"}
        </Button>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Versi</TableHead>
            <TableHead>Environment</TableHead>
            <TableHead>Ukuran</TableHead>
            <TableHead>Checksum (SHA256)</TableHead>
            <TableHead>Dibuat</TableHead>
            <TableHead className="text-right">Aksi</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {bundles?.map((b) => (
            <TableRow key={b.id}>
              <TableCell className="font-bold">v{b.version}</TableCell>
              <TableCell><Badge variant="outline">{b.environment}</Badge></TableCell>
              <TableCell className="text-xs">{formatBytes(b.bundle_size_bytes)}</TableCell>
              <TableCell className="font-mono text-xs">{b.checksum_sha256?.slice(0, 12)}...</TableCell>
              <TableCell className="text-xs text-muted-foreground">{formatLocalTime(b.created_at, "datetime")}</TableCell>
              <TableCell className="text-right">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => rollbackMutation.mutate(b.id)}
                  title="Rollback ke versi ini"
                >
                  <RotateCcw className="h-3.5 w-3.5 mr-1" /> Rollback
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}