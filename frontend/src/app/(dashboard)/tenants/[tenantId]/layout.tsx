// src/app/(dashboard)/tenants/[tenantId]/layout.tsx
"use client";

import { ReactNode, Suspense } from "react";
import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import { useTenant } from "@/hooks/use-tenant";
import { useAuth } from "@/hooks/use-auth";
import {
  Shield,
  LayoutDashboard,
  Settings,
  LogOut,
  Building,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";

function TenantDashboardLayoutContent({ children }: { children: ReactNode }) {
  const params = useParams();
  const pathname = usePathname();
  const tenantId = (params?.tenantId as string) || "";
  const { tenant } = useTenant();
  const { user, logout } = useAuth();

  const navItems = [
    { label: "Overview & Orgs", href: `/tenants/${tenantId}`, icon: LayoutDashboard },
    { label: "Pengaturan Tenant", href: `/tenants/${tenantId}/settings`, icon: Settings },
  ];

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-background">
      {/* Sidebar Navigasi Tenant */}
      <aside className="w-full md:w-64 border-r border-border bg-card p-4 flex flex-col justify-between shrink-0">
        <div className="space-y-6">
          <div className="flex items-center gap-2 px-2">
            <Shield className="h-6 w-6 text-primary" />
            <span className="font-bold tracking-tight text-lg">OPA Console</span>
          </div>

          {/* Active Tenant Box */}
          <div className="bg-muted p-2.5 rounded-md border border-border">
            <p className="text-[10px] uppercase font-mono text-muted-foreground tracking-wider">Tenant Scope</p>
            <div className="flex items-center justify-between mt-1">
              <span className="font-semibold text-sm truncate">{tenant?.name || "Memuat..."}</span>
              <Link href="/tenants">
                <Button variant="ghost" size="icon" className="h-6 w-6" title="Ganti Tenant">
                  <Building className="h-3.5 w-3.5" />
                </Button>
              </Link>
            </div>
          </div>

          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer Sidebar */}
        <div className="pt-4 border-t border-border space-y-3">
          <div className="px-2">
            <p className="text-xs font-medium text-foreground truncate">{user?.full_name}</p>
            <p className="text-[11px] text-muted-foreground truncate">{user?.email}</p>
          </div>
          <Button variant="outline" size="sm" onClick={logout} className="w-full justify-start text-xs">
            <LogOut className="h-3.5 w-3.5 mr-2" /> Keluar Sesi
          </Button>
        </div>
      </aside>

      {/* Konten Halaman */}
      <main className="flex-1 p-6 md:p-8 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}

export default function TenantDashboardLayout({ children }: { children: ReactNode }) {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-background">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      }
    >
      <TenantDashboardLayoutContent>
        {children}
      </TenantDashboardLayoutContent>
    </Suspense>
  );
}