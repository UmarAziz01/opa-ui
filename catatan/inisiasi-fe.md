Jalankan seluruh rangkaian perintah berikut langsung dari direktori root proyek (`/data/e/project/opa-ui/`):

```bash
# 1. Buat proyek Next.js dengan App Router, TypeScript, Tailwind, dan src/ directory
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*" \
  --use-npm

cd frontend

# 2. Instal library core (TanStack Query & Table, Axios, Monaco, Lucide, dll.)
npm install @tanstack/react-query @tanstack/react-table axios lucide-react \
  @monaco-editor/react clsx tailwind-merge class-variance-authority \
  oidc-client-ts

npm install -D @types/node @types/react @types/react-dom

# 3. Inisialisasi shadcn/ui
npx shadcn@latest init -d

# 4. Pasang komponen dasar shadcn/ui yang diperlukan dashboard
npx shadcn@latest add button card dialog dropdown-menu input label \
  select table tabs badge sheet tooltip separator scroll-area alert

```

---

### Pembuatan Struktur Folder dan Berkas Otomatis

Jalankan skrip bash berikut di dalam direktori `frontend/` untuk menghasilkan seluruh susunan direktori dan berkas *boilerplate* sekaligus:

```bash
# Buat struktur direktori
mkdir -p src/app/\(marketing\)/docs \
         src/app/\(marketing\)/pricing \
         src/app/\(auth\)/login \
         src/app/\(auth\)/callback \
         src/app/\(dashboard\)/tenants/\[tenantId\]/settings \
         src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/apps/\[appId\]/logs \
         src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/policies/matrix \
         src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/policies/editor \
         src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/policies/simulate \
         src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/bundles \
         src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/governance/\[approvalId\] \
         src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/audit \
         src/components/common \
         src/components/seo \
         src/components/editor \
         src/components/terminal \
         src/components/rbac \
         src/components/governance \
         src/components/tables \
         src/hooks \
         src/lib \
         src/services \
         src/types

# Buat berkas-berkas App Router
touch src/app/\(marketing\)/layout.tsx \
      src/app/\(marketing\)/page.tsx \
      src/app/\(marketing\)/docs/page.tsx \
      src/app/\(marketing\)/pricing/page.tsx \
      src/app/\(marketing\)/robots.ts \
      src/app/\(marketing\)/sitemap.ts \
      src/app/\(auth\)/login/page.tsx \
      src/app/\(auth\)/callback/page.tsx \
      src/app/\(dashboard\)/tenants/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/layout.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/settings/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/layout.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/apps/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/apps/\[appId\]/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/apps/\[appId\]/logs/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/policies/matrix/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/policies/editor/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/policies/simulate/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/bundles/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/governance/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/governance/\[approvalId\]/page.tsx \
      src/app/\(dashboard\)/tenants/\[tenantId\]/orgs/\[orgId\]/audit/page.tsx

# Buat berkas-berkas Components
touch src/components/seo/JsonLd.tsx \
      src/components/seo/MetaTags.tsx \
      src/components/editor/RegoEditor.tsx \
      src/components/editor/MonacoDiffViewer.tsx \
      src/components/terminal/SseTerminalViewer.tsx \
      src/components/rbac/RbacMatrixGrid.tsx \
      src/components/rbac/SubjectAssignmentModal.tsx \
      src/components/governance/ApprovalTimeline.tsx \
      src/components/tables/DataTable.tsx \
      src/components/tables/DataTablePagination.tsx \
      src/components/tables/DataTableFacetedFilter.tsx

# Buat berkas Hooks, Lib, Services, dan Types
touch src/hooks/use-sidecar-logs.ts \
      src/hooks/use-tenant.ts \
      src/hooks/use-auth.ts \
      src/lib/api-client.ts \
      src/lib/query-client.ts \
      src/lib/epoch.ts \
      src/lib/seo.ts \
      src/services/auth.service.ts \
      src/services/tenants.service.ts \
      src/services/organizations.service.ts \
      src/services/applications.service.ts \
      src/services/policies.service.ts \
      src/services/bundles.service.ts \
      src/services/governance.service.ts \
      src/services/audit.service.ts \
      src/types/api.ts \
      src/types/auth.ts \
      src/types/tenant.ts \
      src/types/policy.ts \
      src/types/bundle.ts \
      src/types/audit.ts

```

---

### Setup Berkas Inti Fondasi

**1. Provider TanStack Query (`src/components/common/Providers.tsx`)**

```tsx
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, ReactNode } from "react";

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 1000 * 30, // 30 detik
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

```

**2. Bungkus Root Layout (`src/app/layout.tsx`)**

```tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/common/Providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "OPA UI - Multi-Tenant Authorization Engine",
  description: "Enterprise SaaS platform for Open Policy Agent and RBAC governance",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

```

**3. Generator SEO Crawler (`src/app/(marketing)/robots.ts` & `sitemap.ts`)**

```typescript
// src/app/(marketing)/robots.ts
import { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://100.100.30.50:3000";
  return {
    rules: {
      userAgent: "*",
      allow: ["/", "/docs", "/pricing"],
      disallow: ["/tenants/", "/api/"],
    },
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}

```

```typescript
// src/app/(marketing)/sitemap.ts
import { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://100.100.30.50:3000";
  return [
    { url: baseUrl, lastModified: new Date(), changeFrequency: "daily", priority: 1.0 },
    { url: `${baseUrl}/docs`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
    { url: `${baseUrl}/pricing`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.8 },
  ];
}

```

Jalankan server dev:

```bash
npm run dev

```