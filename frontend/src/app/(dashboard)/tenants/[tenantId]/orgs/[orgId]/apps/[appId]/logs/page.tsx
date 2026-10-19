"use client";

import { useParams } from "next/navigation";
import { SseTerminalViewer } from "@/components/terminal/SseTerminalViewer";

export default function AppLogsStreamPage() {
  const { tenantId, orgId, appId } = useParams() as { tenantId: string; orgId: string; appId: string };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-bold tracking-tight">Live Sidecar Stream</h3>
        <p className="text-xs text-muted-foreground">Streaming real-time log OPA decision & engine via SSE.</p>
      </div>
      <SseTerminalViewer tenantId={tenantId} orgId={orgId} appId={appId} />
    </div>
  );
}