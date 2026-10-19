"use client";

import { SetStateAction, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { governanceService } from "@/services/governance.service";
import { ApprovalTimeline } from "@/components/governance/ApprovalTimeline";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export default function ApprovalDetailPage() {
  const { tenantId, orgId, approvalId } = useParams() as {
    tenantId: string;
    orgId: string;
    approvalId: string;
  };
  const router = useRouter();
  const queryClient = useQueryClient();
  const [notes, setNotes] = useState("");

  const { data: approvals } = useQuery({
    queryKey: ["approvals", tenantId, orgId],
    queryFn: () => governanceService.listApprovals(tenantId, orgId),
  });

  const approval = approvals?.find((a) => a.id === approvalId);

  const reviewMutation = useMutation({
    mutationFn: (action: "APPROVE" | "REJECT") =>
      governanceService.reviewApproval(tenantId, orgId, approvalId, {
        action,
        review_notes: notes,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["approvals", tenantId, orgId] });
      router.push(`/tenants/${tenantId}/orgs/${orgId}/governance`);
    },
  });

  if (!approval) return <div className="text-xs">Data persetujuan tidak ditemukan.</div>;

  return (
    <div className="space-y-6 max-w-3xl">
      <h3 className="text-xl font-bold tracking-tight">Review Rilis Bundle #{approval.id.slice(0, 8)}</h3>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Tahapan Persetujuan</CardTitle>
        </CardHeader>
        <CardContent>
          <ApprovalTimeline approval={approval} />
        </CardContent>
      </Card>

      {approval.status === "PENDING" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Tindakan Reviewer</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="Catatan review..."
              value={notes}
              onChange={(e: { target: { value: SetStateAction<string>; }; }) => setNotes(e.target.value)}
            />
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={() => reviewMutation.mutate("APPROVE")}
                disabled={reviewMutation.isPending || !approval.tests_passed}
              >
                Setujui Rilis (Approve)
              </Button>
              <Button
                size="sm"
                variant="destructive"
                onClick={() => reviewMutation.mutate("REJECT")}
                disabled={reviewMutation.isPending}
              >
                Tolak (Reject)
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}