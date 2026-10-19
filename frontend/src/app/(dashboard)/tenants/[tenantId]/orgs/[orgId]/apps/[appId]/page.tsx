"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { applicationsService } from "@/services/applications.service";
import { formatLocalTime } from "@/lib/epoch";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { KeyRound, Trash2 } from "lucide-react";

export default function AppDetailPage() {
  const { tenantId, orgId, appId } = useParams() as { tenantId: string; orgId: string; appId: string };
  const queryClient = useQueryClient();
  const [tokenName, setTokenName] = useState("");
  const [rawToken, setRawToken] = useState<string | null>(null);

  const { data: app } = useQuery({
    queryKey: ["app", tenantId, orgId, appId],
    queryFn: () => applicationsService.getApplication(tenantId, orgId, appId),
  });

  const { data: tokens } = useQuery({
    queryKey: ["tokens", tenantId, orgId, appId],
    queryFn: () => applicationsService.listTokens(tenantId, orgId, appId),
  });

  const createTokenMutation = useMutation({
    mutationFn: () => applicationsService.createToken(tenantId, orgId, appId, { name: tokenName }),
    onSuccess: (data) => {
      setRawToken(data.raw_token || null);
      setTokenName("");
      queryClient.invalidateQueries({ queryKey: ["tokens", tenantId, orgId, appId] });
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (tokenId: string) => applicationsService.revokeToken(tenantId, orgId, appId, tokenId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tokens", tenantId, orgId, appId] });
    },
  });

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h3 className="text-xl font-bold tracking-tight">{app?.display_name}</h3>
        <p className="text-xs text-muted-foreground font-mono">App Slug: {app?.slug} | Port: {app?.sidecar_port}</p>
      </div>

      {rawToken && (
        <div className="bg-primary/10 border border-primary/20 p-4 rounded-md">
          <p className="text-xs font-semibold text-primary">Simpan Service Token Ini Sekarang!</p>
          <code className="text-xs bg-background p-2 rounded block mt-1 select-all font-mono break-all">{rawToken}</code>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Service Tokens (Autentikasi Sidecar)</CardTitle>
          <CardDescription>Token kriptografis untuk otorisasi akses bundle OPA.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              createTokenMutation.mutate();
            }}
            className="flex gap-2 max-w-md"
          >
            <Input
              placeholder="Nama token (mis: sidecar-prod)"
              value={tokenName}
              onChange={(e) => setTokenName(e.target.value)}
              required
            />
            <Button size="sm" type="submit" disabled={createTokenMutation.isPending}>
              Generate
            </Button>
          </form>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nama</TableHead>
                <TableHead>Prefix</TableHead>
                <TableHead>Dibuat</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Aksi</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tokens?.map((t) => (
                <TableRow key={t.id}>
                  <TableCell className="font-medium flex items-center gap-1.5">
                    <KeyRound className="h-3.5 w-3.5 text-muted-foreground" /> {t.name}
                  </TableCell>
                  <TableCell className="font-mono text-xs">{t.token_prefix}***</TableCell>
                  <TableCell className="text-xs text-muted-foreground">{formatLocalTime(t.created_at, "datetime")}</TableCell>
                  <TableCell>
                    <Badge variant={t.revoked_at ? "destructive" : "default"}>
                      {t.revoked_at ? "Revoked" : "Active"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    {!t.revoked_at && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => revokeMutation.mutate(t.id)}
                      >
                        <Trash2 className="h-3.5 w-3.5 text-destructive" />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}