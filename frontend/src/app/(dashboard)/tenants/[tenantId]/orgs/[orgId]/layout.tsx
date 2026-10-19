"use client";

import { ReactNode } from "react";
import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { organizationsService } from "@/services/organizations.service";
import { ShieldCheck, Cpu, Layers, History, ShieldAlert, FileCode2, TestTube2, LayoutList } from "lucide-react";

export default function OrgLayout({ children }: { children: ReactNode }) {
  const params = useParams();
  const pathname = usePathname();
  const tenantId = params.tenantId as string;
  const orgId = params.orgId as string;

  const { data: org } = useQuery({
    queryKey: ["org", tenantId, orgId],
    queryFn: () => organizationsService.getOrganization(tenantId, orgId),
    enabled: Boolean(tenantId && orgId),
  });

  const orgNav = [
    { label: "Dashboard", href: `/tenants/${tenantId}/orgs/${orgId}`, icon: LayoutList },
    { label: "Aplikasi & Sidecar", href: `/tenants/${tenantId}/orgs/${orgId}/apps`, icon: Cpu },
    { label: "RBAC Matrix", href: `/tenants/${tenantId}/orgs/${orgId}/policies/matrix`, icon: Layers },
    { label: "Rego Editor", href: `/tenants/${tenantId}/orgs/${orgId}/policies/editor`, icon: FileCode2 },
    { label: "Dry-Run Simulator", href: `/tenants/${tenantId}/orgs/${orgId}/policies/simulate`, icon: TestTube2 },
    { label: "Policy Bundles", href: `/tenants/${tenantId}/orgs/${orgId}/bundles`, icon: History },
    { label: "Governance & Review", href: `/tenants/${tenantId}/orgs/${orgId}/governance`, icon: ShieldCheck },
    { label: "Audit Logs", href: `/tenants/${tenantId}/orgs/${orgId}/audit`, icon: ShieldAlert },
  ];

  return (
    <div className="space-y-6">
      <div className="border-b border-border pb-4">
        <div className="flex items-center gap-2">
          <span className="text-xs uppercase font-mono bg-muted px-2 py-0.5 rounded text-muted-foreground">Org Scope</span>
          <h2 className="text-xl font-bold tracking-tight">{org?.name || orgId}</h2>
        </div>
        <div className="flex gap-2 overflow-x-auto mt-4 pt-1">
          {orgNav.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-colors ${
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {item.label}
              </Link>
            );
          })}
        </div>
      </div>
      <div>{children}</div>
    </div>
  );
}