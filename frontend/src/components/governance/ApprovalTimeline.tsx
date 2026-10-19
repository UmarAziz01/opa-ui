"use client";

import { BundleApprovalItem } from "@/types";
import { formatLocalTime } from "@/lib/epoch";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Clock, XCircle, ShieldAlert } from "lucide-react";

interface ApprovalTimelineProps {
  approval: BundleApprovalItem;
}

export function ApprovalTimeline({ approval }: ApprovalTimelineProps) {
  const isApproved = approval.status === "APPROVED";
  const isRejected = approval.status === "REJECTED";
  const isPending = approval.status === "PENDING";

  return (
    <div className="space-y-6">
      {/* Step 1: Quality Gate OPA Test */}
      <div className="flex gap-4">
        <div className="flex flex-col items-center">
          {approval.tests_passed ? (
            <CheckCircle2 className="h-6 w-6 text-green-500" />
          ) : (
            <ShieldAlert className="h-6 w-6 text-red-500" />
          )}
          <div className="w-0.5 h-full bg-border mt-2" />
        </div>
        <div className="pb-6">
          <p className="font-semibold text-sm">Automated Quality Gate (opa test)</p>
          <div className="flex items-center gap-2 mt-1">
            <Badge variant={approval.tests_passed ? "default" : "destructive"}>
              {approval.tests_passed ? "PASSED" : "FAILED"}
            </Badge>
            <span className="text-xs text-muted-foreground">
              {formatLocalTime(approval.created_at, "datetime")}
            </span>
          </div>
          {approval.test_output && (
            <pre className="mt-2 text-xs bg-muted p-2 rounded max-h-40 overflow-y-auto">
              {approval.test_output}
            </pre>
          )}
        </div>
      </div>

      {/* Step 2: Human Review Decision */}
      <div className="flex gap-4">
        <div className="flex flex-col items-center">
          {isApproved && <CheckCircle2 className="h-6 w-6 text-green-500" />}
          {isRejected && <XCircle className="h-6 w-6 text-red-500" />}
          {isPending && <Clock className="h-6 w-6 text-yellow-500" />}
        </div>
        <div>
          <p className="font-semibold text-sm">Review & Approval Decision</p>
          <div className="flex items-center gap-2 mt-1">
            <Badge
              variant={isApproved ? "default" : isRejected ? "destructive" : "secondary"}
            >
              {approval.status}
            </Badge>
            {approval.reviewed_at && (
              <span className="text-xs text-muted-foreground">
                {formatLocalTime(approval.reviewed_at, "datetime")}
              </span>
            )}
          </div>
          {approval.review_notes && (
            <p className="mt-2 text-xs text-foreground bg-muted p-2 rounded">
              {approval.review_notes}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}