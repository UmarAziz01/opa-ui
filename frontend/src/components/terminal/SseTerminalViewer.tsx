"use client";

import { useEffect, useRef } from "react";
import { useSidecarLogs } from "@/hooks/use-sidecar-logs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Trash2, Radio } from "lucide-react";

interface SseTerminalViewerProps {
  tenantId: string;
  orgId: string;
  appId: string;
}

export function SseTerminalViewer({ tenantId, orgId, appId }: SseTerminalViewerProps) {
  const { logs, isConnected, clearLogs } = useSidecarLogs({
    tenantId,
    orgId,
    appId,
  });

  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll ke baris paling bawah saat ada log masuk
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="rounded-md border bg-black text-green-400 font-mono text-xs overflow-hidden">
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-zinc-800 bg-zinc-950">
        <div className="flex items-center gap-2">
          <Radio
            className={`h-4 w-4 ${isConnected ? "text-green-500 animate-pulse" : "text-zinc-500"}`}
          />
          <span className="text-zinc-300 font-medium">OPA Sidecar Logs</span>
          <Badge variant={isConnected ? "default" : "secondary"} className="text-[10px] h-5">
            {isConnected ? "LIVE" : "DISCONNECTED"}
          </Badge>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={clearLogs}
          className="text-zinc-400 hover:text-white h-7 px-2"
        >
          <Trash2 className="h-3.5 w-3.5 mr-1" /> Bersihkan
        </Button>
      </div>

      {/* Terminal Logs Output */}
      <div ref={scrollRef} className="p-4 h-[400px] overflow-y-auto space-y-1">
        {logs.length === 0 ? (
          <div className="text-zinc-600 italic">Menunggu log dari container OPA...</div>
        ) : (
          logs.map((log, index) => (
            <div key={index} className="leading-relaxed whitespace-pre-wrap break-all">
              {log}
            </div>
          ))
        )}
      </div>
    </div>
  );
}