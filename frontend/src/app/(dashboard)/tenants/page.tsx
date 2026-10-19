// src/app/(dashboard)/tenants/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { tenantsService } from "@/services/tenants.service";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Building2, Plus, ArrowRight, Loader2, LogOut } from "lucide-react";

export default function TenantsSelectionPage() {
  const router = useRouter();
  const { user, logout, isLoading: isAuthLoading } = useAuth();
  const [isCreating, setIsCreating] = useState(false);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch daftar tenant milik user langsung via API
  const {
    data: tenants = [],
    isLoading: isTenantsLoading,
    refetch,
  } = useQuery({
    queryKey: ["user-tenants"],
    queryFn: () => tenantsService.getUserTenants(),
    enabled: Boolean(user),
  });

  const handleCreateTenant = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !slug) return;

    try {
      setIsSubmitting(true);
      const newTenant = await tenantsService.createTenant({ name, slug });
      if (newTenant?.id) {
        await refetch();
        router.push(`/tenants/${newTenant.id}`);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isAuthLoading || isTenantsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-muted/30 p-6 md:p-12">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="flex items-center justify-between border-b border-border pb-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Pilih Workspace Tenant</h1>
            <p className="text-sm text-muted-foreground">
              Masuk sebagai <span className="font-semibold text-foreground">{user?.full_name || user?.username}</span>
            </p>
          </div>
          <Button variant="ghost" size="sm" onClick={logout} className="text-muted-foreground">
            <LogOut className="w-4 h-4 mr-2" /> Keluar
          </Button>
        </div>

        {/* List Tenant Terdaftar */}
        <div className="grid md:grid-cols-2 gap-4">
          {tenants.length > 0 ? (
            tenants.map((t) => (
              <Card
                key={t.id}
                className="hover:border-primary/50 transition-all cursor-pointer bg-card"
                onClick={() => router.push(`/tenants/${t.id}`)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Building2 className="h-5 w-5 text-primary" />
                      <CardTitle className="text-lg">{t.name}</CardTitle>
                    </div>
                    <Badge variant="outline">{t.subscription_tier}</Badge>
                  </div>
                  <CardDescription className="font-mono text-xs">
                    slug: {t.slug}
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex justify-between items-center text-xs text-muted-foreground">
                  <span>Status: {t.subscription_status}</span>
                  <span className="flex items-center text-primary font-medium">
                    Buka Console <ArrowRight className="h-3.5 w-3.5 ml-1" />
                  </span>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="col-span-2 text-center py-8 text-sm text-muted-foreground border border-dashed rounded-lg">
              Belum ada workspace tenant terdaftar untuk akun ini. Silakan buat tenant baru di bawah.
            </div>
          )}
        </div>

        {/* Registrasi Tenant Baru */}
        <Card className="border-dashed">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              <CardTitle className="text-base">Registrasi Tenant Baru</CardTitle>
            </div>
            <CardDescription>
              Buat organisasi tenant baru untuk mengelola policy bundle dan sidecar OPA.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isCreating ? (
              <form onSubmit={handleCreateTenant} className="space-y-4 max-w-md">
                <div className="space-y-1">
                  <Label htmlFor="tenant-name">Nama Tenant</Label>
                  <Input
                    id="tenant-name"
                    placeholder="Contoh: FinTech Hub"
                    value={name}
                    onChange={(e) => {
                      setName(e.target.value);
                      setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, ""));
                    }}
                    required
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="tenant-slug">Tenant Slug</Label>
                  <Input
                    id="tenant-slug"
                    placeholder="fintech-hub"
                    value={slug}
                    onChange={(e) => setSlug(e.target.value)}
                    required
                  />
                </div>
                <div className="flex gap-2">
                  <Button type="submit" size="sm" disabled={isSubmitting}>
                    {isSubmitting ? "Membuat..." : "Simpan Tenant"}
                  </Button>
                  <Button type="button" size="sm" variant="ghost" onClick={() => setIsCreating(false)}>
                    Batal
                  </Button>
                </div>
              </form>
            ) : (
              <Button variant="outline" size="sm" onClick={() => setIsCreating(true)}>
                <Plus className="w-4 h-4 mr-2" /> Tambah Tenant
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}