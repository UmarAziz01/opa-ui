"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { applicationsService } from "@/services/applications.service";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { Cpu, Terminal, ArrowRight, Plus } from "lucide-react";

export default function AppsListPage() {
  const { tenantId, orgId } = useParams() as { tenantId: string; orgId: string };
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [slug, setSlug] = useState("");
  const [port, setPort] = useState<number | undefined>();

  const { data: apps, isLoading } = useQuery({
    queryKey: ["apps", tenantId, orgId],
    queryFn: () => applicationsService.listApplications(tenantId, orgId),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      applicationsService.createApplication(tenantId, orgId, {
        display_name: displayName,
        slug,
        sidecar_port: port,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["apps", tenantId, orgId] });
      setIsOpen(false);
      setDisplayName("");
      setSlug("");
      setPort(undefined);
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold tracking-tight">Daftar Aplikasi & Sidecar OPA</h3>
          <p className="text-xs text-muted-foreground">Kelola aplikasi yang mengonsumsi bundle via sidecar port.</p>
        </div>
        <Button size="sm" onClick={() => setIsOpen(!isOpen)}>
          <Plus className="h-4 w-4 mr-1" /> Tambah Aplikasi
        </Button>
      </div>

      {isOpen && (
        <Card className="border-dashed max-w-md">
          <CardHeader>
            <CardTitle className="text-sm">Registrasi Aplikasi Baru</CardTitle>
          </CardHeader>
          <CardContent>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                createMutation.mutate();
              }}
              className="space-y-3"
            >
              <div>
                <Label className="text-xs">Nama Aplikasi</Label>
                <Input
                  value={displayName}
                  onChange={(e) => {
                    setDisplayName(e.target.value);
                    setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, "-"));
                  }}
                  required
                />
              </div>
              <div>
                <Label className="text-xs">Slug</Label>
                <Input value={slug} onChange={(e) => setSlug(e.target.value)} required />
              </div>
              <div>
                <Label className="text-xs">Port Sidecar (Opsional)</Label>
                <Input
                  type="number"
                  placeholder="8181"
                  value={port || ""}
                  onChange={(e) => setPort(Number(e.target.value))}
                />
              </div>
              <div className="flex gap-2">
                <Button size="sm" type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? "Menyimpan..." : "Simpan"}
                </Button>
                <Button size="sm" variant="ghost" type="button" onClick={() => setIsOpen(false)}>
                  Batal
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nama Aplikasi</TableHead>
            <TableHead>Slug</TableHead>
            <TableHead>Port Sidecar</TableHead>
            <TableHead className="text-right">Aksi</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {apps?.map((app) => (
            <TableRow key={app.id}>
              <TableCell className="font-medium flex items-center gap-2">
                <Cpu className="h-4 w-4 text-primary" /> {app.display_name}
              </TableCell>
              <TableCell className="font-mono text-xs">{app.slug}</TableCell>
              <TableCell>
                <Badge variant="outline">Port {app.sidecar_port}</Badge>
              </TableCell>
              <TableCell className="text-right space-x-2">
                <Link href={`/tenants/${tenantId}/orgs/${orgId}/apps/${app.id}/logs`}>
                  <Button size="sm" variant="ghost">
                    <Terminal className="h-3.5 w-3.5 mr-1" /> Log Sidecar
                  </Button>
                </Link>
                <Link href={`/tenants/${tenantId}/orgs/${orgId}/apps/${app.id}`}>
                  <Button size="sm" variant="outline">
                    Detail <ArrowRight className="h-3.5 w-3.5 ml-1" />
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