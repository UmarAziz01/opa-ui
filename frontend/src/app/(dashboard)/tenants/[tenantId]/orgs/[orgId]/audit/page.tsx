"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { auditService } from "@/services/audit.service";
import { formatLocalTime } from "@/lib/epoch";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function AuditLogsPage() {
  const { tenantId, orgId } = useParams() as { tenantId: string; orgId: string };

  const { data: logs } = useQuery({
    queryKey: ["auditLogs", tenantId, orgId],
    queryFn: () => auditService.getAuditTrail(tenantId, { org_id: orgId }),
  });

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-bold tracking-tight">Audit Trail Forensik</h3>
        <p className="text-xs text-muted-foreground">Catatan mutasi keamanan dan perubahan policy.</p>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Aksi</TableHead>
            <TableHead>Resource</TableHead>
            <TableHead>IP Address</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Waktu</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs?.map((l) => (
            <TableRow key={l.id}>
              <TableCell className="font-semibold text-xs">{l.action}</TableCell>
              <TableCell className="font-mono text-xs">{l.resource_type}:{l.resource_id || "-"}</TableCell>
              <TableCell className="font-mono text-xs">{l.ip_address || "-"}</TableCell>
              <TableCell>
                <Badge variant={l.status === "SUCCESS" ? "default" : "destructive"}>
                  {l.status}
                </Badge>
              </TableCell>
              <TableCell className="text-xs text-muted-foreground">
                {formatLocalTime(l.timestamp, "datetime")}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}