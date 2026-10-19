"use client";

import { useState } from "react";
import { useTenant } from "@/hooks/use-tenant";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { formatLocalTime } from "@/lib/epoch";

export default function TenantSettingsPage() {
  const { tenant, members, updateTenant, addMember, isUpdating, isAddingMember } = useTenant();
  const [tenantName, setTenantName] = useState(tenant?.name || "");
  const [newUserId, setNewUserId] = useState("");
  const [newRole, setNewRole] = useState("MEMBER");

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tenantName) return;
    await updateTenant({ name: tenantName });
  };

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUserId) return;
    await addMember({ user_id: newUserId, tenant_role: newRole });
    setNewUserId("");
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Pengaturan Tenant</h1>
        <p className="text-sm text-muted-foreground">Kelola identitas tenant dan anggota tim workspace.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Profil Tenant</CardTitle>
          <CardDescription>Ubah nama tampilan workspace tenant.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUpdate} className="space-y-4 max-w-sm">
            <div className="space-y-2">
              <Label htmlFor="tName">Nama Workspace</Label>
              <Input
                id="tName"
                defaultValue={tenant?.name}
                onChange={(e) => setTenantName(e.target.value)}
              />
            </div>
            <Button size="sm" type="submit" disabled={isUpdating}>
              {isUpdating ? "Menyimpan..." : "Simpan Perubahan"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Anggota Tenant</CardTitle>
          <CardDescription>Daftar pengguna yang memiliki akses ke tenant ini.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <form onSubmit={handleAddMember} className="flex gap-2 max-w-md">
            <Input
              placeholder="User ID (UUID)"
              value={newUserId}
              onChange={(e) => setNewUserId(e.target.value)}
              required
            />
            <Button size="sm" type="submit" disabled={isAddingMember}>
              {isAddingMember ? "Menambahkan..." : "Tambah"}
            </Button>
          </form>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User ID</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Ditambahkan</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {members.map((m) => (
                <TableRow key={m.id}>
                  <TableCell className="font-mono text-xs">{m.user_id}</TableCell>
                  <TableCell><Badge variant="outline">{m.tenant_role}</Badge></TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {formatLocalTime(m.created_at, "datetime")}
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