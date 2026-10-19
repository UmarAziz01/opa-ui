"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTenant } from "@/hooks/use-tenant";
import { organizationsService } from "@/services/organizations.service";
import { formatLocalTime } from "@/lib/epoch";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Clock, Building2, Users, ShieldAlert, Plus, ArrowRight, FolderKanban } from "lucide-react";
import Link from "next/link";

export default function TenantOverviewPage() {
  const params = useParams();
  const rawTenantId = params?.tenantId;
  const tenantId =
    typeof rawTenantId === "string" && rawTenantId !== "undefined" && rawTenantId.trim() !== ""
      ? rawTenantId
      : null;

  const queryClient = useQueryClient();
  const { tenant, isTrialExpired, isLoading: isTenantLoading } = useTenant();

  const [isCreatingOrg, setIsCreatingOrg] = useState(false);
  const [orgName, setOrgName] = useState("");
  const [orgSlug, setOrgSlug] = useState("");
  const [orgDesc, setOrgDesc] = useState("");

  const { data: orgs } = useQuery({
    queryKey: ["orgs", tenantId],
    queryFn: () => organizationsService.listOrganizations(tenantId!),
    enabled: Boolean(tenantId),
    retry: false,
  });

  const createOrgMutation = useMutation({
    mutationFn: () =>
      organizationsService.createOrganization(tenantId!, {
        name: orgName,
        slug: orgSlug,
        description: orgDesc,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orgs", tenantId] });
      setIsCreatingOrg(false);
      setOrgName("");
      setOrgSlug("");
      setOrgDesc("");
    },
  });

  if (!tenantId) {
    return <div className="text-sm text-destructive">ID Tenant tidak valid.</div>;
  }

  if (isTenantLoading || !tenant) {
    return <div className="text-sm text-muted-foreground">Memuat data tenant...</div>;
  }

  return (
    <div className="space-y-8 max-w-6xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{tenant.name} Overview</h1>
        <p className="text-sm text-muted-foreground font-mono">Tenant Slug: {tenant.slug}</p>
      </div>

      {/* Banner Trial Expired */}
      {isTrialExpired && (
        <div className="bg-destructive/15 border border-destructive/30 p-4 rounded-lg flex items-center gap-3 text-destructive">
          <ShieldAlert className="h-5 w-5 shrink-0" />
          <div className="text-sm">
            <p className="font-semibold">Masa Percobaan (Trial) Berakhir</p>
            <p className="text-xs">
              Kompilasi policy bundle dan deploy sidecar baru dinonaktifkan sementara.
            </p>
          </div>
        </div>
      )}

      {/* Metrik Kuota & Waktu Lokal */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Status Langganan</CardTitle>
            <Badge variant={isTrialExpired ? "destructive" : "default"}>
              {tenant.subscription_status}
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tenant.subscription_tier}</div>
            <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              Trial Selesai: {formatLocalTime(tenant.trial_ends_at, "datetime")}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Kuota Organisasi</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {orgs?.length || 0} / {tenant.max_organizations}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Grup otorisasi aktif</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Maksimal Developer</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tenant.max_developers} Pengguna</div>
            <p className="text-xs text-muted-foreground mt-1">Kuota akun pengembang</p>
          </CardContent>
        </Card>
      </div>

      {/* Bagian Organisasi */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold tracking-tight">Daftar Organisasi</h2>
            <p className="text-xs text-muted-foreground">Pilih organisasi untuk masuk ke manajemen RBAC dan OPA sidecar.</p>
          </div>
          <Button size="sm" onClick={() => setIsCreatingOrg(!isCreatingOrg)}>
            <Plus className="h-4 w-4 mr-1" /> Tambah Organisasi
          </Button>
        </div>

        {/* Form Tambah Organisasi */}
        {isCreatingOrg && (
          <Card className="border-dashed max-w-lg">
            <CardHeader>
              <CardTitle className="text-sm">Buat Organisasi Baru</CardTitle>
              <CardDescription>Organisasi memisahkan aplikasi, policy bundle, dan role pengguna.</CardDescription>
            </CardHeader>
            <CardContent>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  createOrgMutation.mutate();
                }}
                className="space-y-3"
              >
                <div>
                  <Label className="text-xs">Nama Organisasi</Label>
                  <Input
                    placeholder="Contoh: Payments Service"
                    value={orgName}
                    onChange={(e) => {
                      setOrgName(e.target.value);
                      setOrgSlug(e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, ""));
                    }}
                    required
                  />
                </div>
                <div>
                  <Label className="text-xs">Slug Organisasi</Label>
                  <Input
                    placeholder="payments-service"
                    value={orgSlug}
                    onChange={(e) => setOrgSlug(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <Label className="text-xs">Deskripsi (Opsional)</Label>
                  <Input
                    placeholder="Layanan pemrosesan transaksi"
                    value={orgDesc}
                    onChange={(e) => setOrgDesc(e.target.value)}
                  />
                </div>
                <div className="flex gap-2">
                  <Button size="sm" type="submit" disabled={createOrgMutation.isPending}>
                    {createOrgMutation.isPending ? "Menyimpan..." : "Simpan Organisasi"}
                  </Button>
                  <Button size="sm" variant="ghost" type="button" onClick={() => setIsCreatingOrg(false)}>
                    Batal
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Grid Organisasi */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {orgs?.map((org) => (
            <Card key={org.id} className="hover:border-primary/50 transition-colors">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <FolderKanban className="h-5 w-5 text-primary" />
                  <CardTitle className="text-base">{org.name}</CardTitle>
                </div>
                <CardDescription className="text-xs font-mono">{org.slug}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {org.description || "Tidak ada deskripsi organisasi."}
                </p>
                <div className="pt-2 border-t border-border flex justify-between items-center text-xs">
                  <span className="text-muted-foreground">
                    {formatLocalTime(org.created_at, "date")}
                  </span>
                  <Link href={`/tenants/${tenantId}/orgs/${org.id}`}>
                    <Button size="sm" variant="outline" className="h-7 text-xs">
                      Buka Scope <ArrowRight className="h-3 w-3 ml-1" />
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}