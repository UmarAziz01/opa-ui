Berikut struktur arsitektur frontend **Next.js (App Router, TypeScript)** yang matang, modular, memisahkan concern *public/marketing (SEO-friendly)* dengan *authenticated multi-tenant console*, serta siap untuk integrasi Monaco Editor, RBAC Matrix, TanStack Table/Query, dan SSE Terminal.

---

### 1. Struktur Folder Lengkap (`frontend/`)

```text
frontend/
├── src/
│   ├── app/                                 # Next.js App Router
│   │   ├── (marketing)/                     # SEO Route Group (SSR/SSG, Metadata, OpenGraph)
│   │   │   ├── layout.tsx                   # Public navbar & footer
│   │   │   ├── page.tsx                     # Landing page / Hero OPA platform
│   │   │   ├── docs/                        # Public developer docs & guides
│   │   │   │   └── page.tsx
│   │   │   ├── pricing/                     # Pricing & 30-Day Trial tiers
│   │   │   │   └── page.tsx
│   │   │   └── robots.ts / sitemap.ts       # Dynamic SEO crawlers
│   │   │
│   │   ├── (auth)/                          # Authentication flow
│   │   │   ├── login/page.tsx
│   │   │   └── callback/page.tsx            # OIDC Keycloak token exchange callback
│   │   │
│   │   ├── (dashboard)/                     # Authenticated Multi-Tenant Scope
│   │   │   └── tenants/
│   │   │       ├── page.tsx                 # Tenant switcher / Tenant selection
│   │   │       └── [tenantId]/
│   │   │           ├── layout.tsx           # Tenant sidebar & breadcrumbs context
│   │   │           ├── page.tsx             # Tenant overview & trial status widget
│   │   │           ├── settings/page.tsx    # Tenant quota & member invitations
│   │   │           └── orgs/
│   │   │               └── [orgId]/
│   │   │                   ├── layout.tsx   # Org navigation header
│   │   │                   ├── page.tsx     # Org dashboard summary
│   │   │                   │
│   │   │                   ├── apps/        # Applications & OPA Sidecar
│   │   │                   │   ├── page.tsx # Apps list & port allocation
│   │   │                   │   └── [appId]/
│   │   │                   │       ├── page.tsx        # App detail & tokens
│   │   │                   │       └── logs/page.tsx   # SSE Terminal log stream
│   │   │                   │
│   │   │                   ├── policies/    # RBAC & Rego Editor
│   │   │                   │   ├── matrix/page.tsx     # Interactive RBAC Matrix
│   │   │                   │   ├── editor/page.tsx     # Monaco Editor (Rego v1)
│   │   │                   │   └── simulate/page.tsx   # Dry-run evaluation tester
│   │   │                   │
│   │   │                   ├── bundles/     # Bundle Releases & Rollback
│   │   │                   │   └── page.tsx # TanStack Table bundle history & rollback
│   │   │                   │
│   │   │                   ├── governance/  # Quality Gates & Approvals
│   │   │                   │   ├── page.tsx            # Approval queue
│   │   │                   │   └── [approvalId]/page.tsx # Review timeline & opa test diff
│   │   │                   │
│   │   │                   └── audit/       # Security Logs
│   │   │                       └── page.tsx # TanStack Table JSONB audit logs
│   │   │
│   │   ├── api/                             # Internal Route Handlers / BFF (jika perlu)
│   │   ├── layout.tsx                       # Root layout (Fonts, QueryProvider, ThemeProvider)
│   │   └── not-found.tsx
│   │
│   ├── components/                          # Reusable UI Blocks
│   │   ├── ui/                              # shadcn/ui primitives (button, dialog, dropdown, dll)
│   │   ├── common/                          # Global components (header, tenant-selector, user-menu)
│   │   ├── seo/                             # JsonLd.tsx, MetaTags.tsx
│   │   ├── editor/                          # Monaco Rego editor wrapper & syntax configs
│   │   │   ├── RegoEditor.tsx
│   │   │   └── MonacoDiffViewer.tsx
│   │   ├── terminal/                        # Log streaming terminal
│   │   │   └── SseTerminalViewer.tsx        # xterm.js / custom virtualized log reader
│   │   ├── rbac/                            # Interactive RBAC Grid
│   │   │   ├── RbacMatrixGrid.tsx           # Checkbox matrix Role vs Permissions
│   │   │   └── SubjectAssignmentModal.tsx
│   │   ├── governance/
│   │   │   └── ApprovalTimeline.tsx         # Stepper visual rilis bundle & test output
│   │   └── tables/                          # Reusable TanStack Table components
│   │       ├── DataTable.tsx
│   │       ├── DataTablePagination.tsx
│   │       └── DataTableFacetedFilter.tsx
│   │
│   ├── hooks/                               # Custom Hooks
│   │   ├── use-sidecar-logs.ts              # SSE EventSource listener
│   │   ├── use-tenant.ts                    # Active tenant & org context
│   │   └── use-auth.ts                      # Session & Keycloak helpers
│   │
│   ├── lib/                                 # Core Utilities & Clients
│   │   ├── api-client.ts                    # Axios / ofetch configured with Bearer Token & Interceptors
│   │   ├── query-client.ts                  # TanStack React Query global config
│   │   ├── epoch.ts                         # Helper konversi & format integer Unix epoch
│   │   ├── utils.ts                         # cn() shadcn helper
│   │   └── seo.ts                           # generateMetadata helpers & OpenGraph builders
│   │
│   ├── services/                            # Typed Backend API Integrations
│   │   ├── auth.service.ts
│   │   ├── tenants.service.ts
│   │   ├── organizations.service.ts
│   │   ├── applications.service.ts
│   │   ├── policies.service.ts
│   │   ├── bundles.service.ts
│   │   ├── governance.service.ts
│   │   └── audit.service.ts
│   │
│   └── types/                               # TypeScript Definitions (Matching Backend Schemas)
│       ├── api.ts                           # PaginatedResponse<T>, ErrorResponse
│       ├── auth.ts
│       ├── tenant.ts
│       ├── policy.ts
│       ├── bundle.ts
│       └── audit.ts
│
├── public/                                  # Static assets, logos, OPA icons
├── tailwind.config.ts
├── tsconfig.json
└── package.json

```

---

### 2. Konfigurasi SEO & Metadata Standard (`src/lib/seo.ts`)

Untuk halaman publik (landing page, dokumentasi, pricing), SEO ditangani secara native melalui **Next.js Metadata API** dan structured data Schema.org (JSON-LD):

```typescript
// src/lib/seo.ts
import { Metadata } from "next";

interface MetadataProps {
  title: string;
  description: string;
  path?: string;
}

export function constructMetadata({
  title,
  description,
  path = "",
}: MetadataProps): Metadata {
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "https://opa-ui.internal";
  const url = `${baseUrl}${path}`;

  return {
    title: `${title} | OPA UI Platform`,
    description,
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: url,
    },
    openGraph: {
      title,
      description,
      url,
      siteName: "OPA UI Multi-Tenant Platform",
      locale: "id_ID",
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
    robots: {
      index: true,
      follow: true,
    },
  };
}

```

Penerapan di page publik (`src/app/(marketing)/page.tsx`):

```typescript
import { constructMetadata } from "@/lib/seo";

export const metadata = constructMetadata({
  title: "Multi-Tenant OPA Authorization Engine & Governance",
  description: "Enterprise SaaS platform for automated Rego policy lifecycle, dynamic sidecar management, and RBAC governance.",
});

export default function LandingPage() {
  return <main>{/* Komponen Hero & Fitur */}</main>;
}

```

---

### 3. API Client dengan Auto Epoch & Bearer Token (`src/lib/api-client.ts`)

```typescript
// src/lib/api-client.ts
import axios from "axios";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://100.100.30.50:7000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: Sisipkan token JWT Keycloak
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor: Normalisasi error code backend
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

```

---

### 4. Custom Hook SSE Terminal Log Viewer (`src/hooks/use-sidecar-logs.ts`)

Menghubungkan langsung ke endpoint streaming live logs backend (`GET /api/v1/tenants/.../apps/{appId}/sidecar/logs`):

```typescript
// src/hooks/use-sidecar-logs.ts
"use client";

import { useEffect, useState } from "react";

export function useSidecarLogs(logStreamUrl: string | null) {
  const [logs, setLogs] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!logStreamUrl) return;

    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    // URL EventSource dengan token query param jika reverse-proxy membutuhkannya
    const url = new URL(logStreamUrl);
    if (token) url.searchParams.set("token", token);

    const eventSource = new EventSource(url.toString());

    eventSource.onopen = () => setIsConnected(true);

    eventSource.onmessage = (event) => {
      setLogs((prev) => [...prev.slice(-1000), event.data]); // Keep last 1000 lines
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [logStreamUrl]);

  return { logs, isConnected, clearLogs: () => setLogs([]) };
}

```

---

### 5. Format Unix Epoch Helper (`src/lib/epoch.ts`)

```typescript
// src/lib/epoch.ts
export function formatEpoch(epochSec: number | null | undefined, format: "date" | "datetime" | "relative" = "datetime"): string {
  if (!epochSec) return "-";
  const date = new Date(epochSec * 1000);

  if (format === "date") {
    return date.toLocaleDateString("id-ID", { year: "numeric", month: "short", day: "numeric" });
  }

  if (format === "datetime") {
    return date.toLocaleString("id-ID", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  }

  // Relative time
  const diffSec = Math.floor(Date.now() / 1000) - epochSec;
  if (diffSec < 60) return `${diffSec} detik lalu`;
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)} menit lalu`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} jam lalu`;
  return `${Math.floor(diffSec / 86400)} hari lalu`;
}

```


catatan pr ; tabel applikasi audit log bundle approval dan service token belum sama seratus persen

Tabel applikasi kurang
- inherits_from_core boolean [default: true, note: 'Apakah mewarisi rule global/core dari tenant']
- requires_own_signing_key boolean [default: false, note: 'Gunakan asymmetric key terpisah untuk verifikasi bundle']

