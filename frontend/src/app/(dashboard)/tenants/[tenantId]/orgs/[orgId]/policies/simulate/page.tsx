"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { policiesService } from "@/services/policies.service";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Play, ShieldCheck, ShieldAlert } from "lucide-react";

export default function DryRunSimulatorPage() {
  const { tenantId, orgId } = useParams() as { tenantId: string; orgId: string };
  const [subject, setSubject] = useState("alice@internal.net");
  const [resource, setResource] = useState("documents");
  const [action, setAction] = useState("read");
  const [result, setResult] = useState<any>(null);

  const simulateMutation = useMutation({
    mutationFn: () =>
      policiesService.simulateEvaluation(tenantId, orgId, {
        subject,
        resource,
        action,
      }),
    onSuccess: (data) => setResult(data),
  });

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Parameter Evaluasi Simulator</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              simulateMutation.mutate();
            }}
            className="space-y-4"
          >
            <div>
              <Label className="text-xs">Subject (User/Klien)</Label>
              <Input value={subject} onChange={(e) => setSubject(e.target.value)} required />
            </div>
            <div>
              <Label className="text-xs">Resource</Label>
              <Input value={resource} onChange={(e) => setResource(e.target.value)} required />
            </div>
            <div>
              <Label className="text-xs">Action</Label>
              <Input value={action} onChange={(e) => setAction(e.target.value)} required />
            </div>
            <Button size="sm" type="submit" disabled={simulateMutation.isPending}>
              <Play className="h-3.5 w-3.5 mr-1" /> Jalankan Simulasi
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Keputusan OPA Engine</CardTitle>
        </CardHeader>
        <CardContent>
          {result ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                {result.allow ? (
                  <Badge className="bg-green-600 text-white text-sm px-3 py-1">
                    <ShieldCheck className="h-4 w-4 mr-1 inline" /> ALLOW
                  </Badge>
                ) : (
                  <Badge variant="destructive" className="text-sm px-3 py-1">
                    <ShieldAlert className="h-4 w-4 mr-1 inline" /> DENY
                  </Badge>
                )}
                <span className="text-xs text-muted-foreground">{result.execution_time_ms} ms</span>
              </div>
              <pre className="p-3 bg-muted rounded text-xs overflow-x-auto font-mono">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          ) : (
            <p className="text-xs text-muted-foreground italic">Tekan 'Jalankan Simulasi' untuk melihat output OPA.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}