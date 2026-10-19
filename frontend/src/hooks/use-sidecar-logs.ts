// src/hooks/use-sidecar-logs.ts
"use client";

import { useEffect, useState, useCallback, useRef } from "react";

interface UseSidecarLogsProps {
  tenantId: string | null;
  orgId: string | null;
  appId: string | null;
  maxBufferLines?: number;
  autoConnect?: boolean;
}

export function useSidecarLogs({
  tenantId,
  orgId,
  appId,
  maxBufferLines = 1000,
  autoConnect = true,
}: UseSidecarLogsProps) {
  const [logs, setLogs] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, []);

  const connect = useCallback(() => {
    if (!tenantId || !orgId || !appId) return;

    disconnect();
    setError(null);

    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://100.100.30.50:7000/api/v1";
    const logUrl = new URL(
      `${baseUrl}/tenants/${tenantId}/orgs/${orgId}/apps/${appId}/sidecar/logs`
    );

    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (token) {
      logUrl.searchParams.set("token", token);
    }

    const es = new EventSource(logUrl.toString());
    eventSourceRef.current = es;

    es.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    es.onmessage = (event) => {
      if (!event.data) return;
      setLogs((prevLogs) => {
        const nextLogs = [...prevLogs, event.data];
        return nextLogs.length > maxBufferLines
          ? nextLogs.slice(nextLogs.length - maxBufferLines)
          : nextLogs;
      });
    };

    es.onerror = () => {
      setIsConnected(false);
      setError("Koneksi log sidecar terputus atau gagal terhubung.");
      disconnect();
    };
  }, [tenantId, orgId, appId, maxBufferLines, disconnect]);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  const clearLogs = useCallback(() => {
    setLogs([]);
  }, []);

  return {
    logs,
    isConnected,
    error,
    connect,
    disconnect,
    clearLogs,
  };
}