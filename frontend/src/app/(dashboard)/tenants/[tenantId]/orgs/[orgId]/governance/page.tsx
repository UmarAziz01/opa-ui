"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { governanceService } from "@/services/governance.service";
import { formatLocalTime } from "@/lib/epoch";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export default function GovernanceApprovalQueuePage() {
  const { tenantId, orgId } = useParams() as { tenantId: string; orgId: string };

  const { data: approvals } = useQuery({
    queryKey: ["approvals", tenantId, orgId],
    queryFn: () => governanceService.listApprovals(tenantId, orgId),
  });

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-bold tracking-tight">Quality Gate & Antrean Persetujuan</h3>
        <p className="text-xs text-muted-foreground">Tinjau hasil opa test dan putuskan rilis bundle ke production.</p>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Target Env</TableHead>
            <TableHead>Quality Gate Test</TableHead>
            <TableHead>Status Review</TableHead>
            <TableHead>Diajukan</TableHead>
            <TableHead className="text-right">Aksi</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {approvals?.map((item) => (
            <TableRow key={item.id}>
              <TableCell className="font-semibold">{item.target_environment}</TableCell>
              <TableCell>
                <Badge variant={item.tests_passed ? "default" : "destructive"}>
                  {item.tests_passed ? "PASSED" : "FAILED"}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge variant="outline">{item.status}</Badge>
              </TableCell>
              <TableCell className="text-xs text-muted-foreground">
                {formatLocalTime(item.created_at, "datetime")}
              </TableCell>
              <TableCell className="text-right">
                <Link href={`/tenants/${tenantId}/orgs/${orgId}/governance/${item.id}`}>
                  <Button size="sm" variant="outline">
                    Review <ArrowRight className="h-3.5 w-3.5 ml-1" />
                  </Button>
                </Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}