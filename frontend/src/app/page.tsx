// src/app/(marketing)/page.tsx atau src/app/page.tsx
import Link from "next/link";
import {
  ShieldCheck,
  Code2,
  Terminal,
  Layers,
  History,
  FileCheck2,
  ArrowRight,
  CheckCircle2,
  Lock,
  Cpu,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function LandingPage() {
  const features = [
    {
      icon: Code2,
      title: "Monaco Rego v1 Editor",
      description:
        "Tulis, validasi, dan kelola sintaks kebijakan OPA Rego secara langsung di browser dengan intellisense dan syntax highlighting terintegrasi.",
    },
    {
      icon: Terminal,
      title: "Real-time SSE Sidecar Stream",
      description:
        "Pantau keputusan evaluasi akses OPA sidecar secara langsung via Server-Sent Events tanpa jeda polling.",
    },
    {
      icon: Layers,
      title: "Matriks RBAC Interaktif",
      description:
        "Petakan hak akses, peran (roles), dan permissions lintas microservices tanpa perlu hardcode pada level kode aplikasi.",
    },
    {
      icon: History,
      title: "Bundle Releases & Instant Rollback",
      description:
        "Distribusi otomatis policy bundle ke seluruh instance OPA sidecar dengan kapabilitas rollback instan jika terdeteksi anomali.",
    },
    {
      icon: FileCheck2,
      title: "Governance & Quality Gates",
      description:
        "Persetujuan multi-tahap (approval queue) dan verifikasi otomatis 'opa test' sebelum kebijakan dirilis ke production.",
    },
    {
      icon: Lock,
      title: "Enterprise Multi-Tenancy & SSO",
      description:
        "Isolasi workspace berbasis tenant dan organisasi yang terintegrasi penuh dengan Keycloak OIDC/OAuth2.",
    },
  ];

  const codeSnippet = `package authz.api

import rego.v1

default allow := false

# Evaluasi akses berdasarkan RBAC Matrix
allow if {
    some grant in input.user.roles
    grant == "security_admin"
}

allow if {
    input.method == "GET"
    input.path = ["api", "v1", "tenants", tenant_id, "policies"]
    tenant_id == input.user.tenant_id
}`;

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      {/* Header Navigasi Sederhana */}
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-6 w-6 text-primary" />
            <span className="font-bold tracking-tight text-lg">OPA Control Plane</span>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
            <Link href="/docs" className="text-muted-foreground hover:text-foreground transition-colors">
              Dokumentasi
            </Link>
            <Link href="/pricing" className="text-muted-foreground hover:text-foreground transition-colors">
              Paket Harga
            </Link>
          </nav>

          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm">
                Masuk Sesi
              </Button>
            </Link>
            <Link href="/tenants">
              <Button size="sm">
                Buka Console <ArrowRight className="ml-1.5 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="py-20 md:py-32 border-b border-border/40 bg-gradient-to-b from-muted/30 via-background to-background">
          <div className="container mx-auto px-6 text-center max-w-4xl space-y-8">
            <Badge variant="outline" className="px-3 py-1 text-xs border-primary/30 text-primary bg-primary/5">
              🚀 OPA Policy Management Platform • Multi-Tenant Ready
            </Badge>

            <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight">
              Manajemen Kebijakan Akses Terpusat dengan{" "}
              <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
                Open Policy Agent
              </span>
            </h1>

            <p className="text-lg md:text-xl text-muted-foreground leading-relaxed max-w-2xl mx-auto">
              Pisahkan logika otorisasi dari kode aplikasi. Bangun, uji, distribusikan, dan audit kebijakan
              keamanan mikroservis dalam satu antarmuka kontrol terpadu.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link href="/tenants">
                <Button size="lg" className="w-full sm:w-auto h-12 px-8 font-medium">
                  Mulai Free Trial 30 Hari <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/docs">
                <Button size="lg" variant="outline" className="w-full sm:w-auto h-12 px-8 font-medium">
                  Baca Dokumentasi
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Code & Visual Preview Section */}
        <section className="py-16 bg-muted/20 border-b border-border/40">
          <div className="container mx-auto px-6 max-w-5xl">
            <div className="rounded-xl border border-border bg-card shadow-2xl overflow-hidden">
              <div className="flex items-center justify-between border-b border-border bg-muted/60 px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-red-500/80" />
                  <div className="h-3 w-3 rounded-full bg-amber-500/80" />
                  <div className="h-3 w-3 rounded-full bg-emerald-500/80" />
                  <span className="ml-2 font-mono text-xs text-muted-foreground">authz_rules.rego</span>
                </div>
                <Badge variant="secondary" className="font-mono text-[11px]">
                  Rego v1 Engine
                </Badge>
              </div>
              <div className="p-6 overflow-x-auto bg-[#0d1117] text-[#c9d1d9] font-mono text-sm leading-relaxed">
                <pre>{codeSnippet}</pre>
              </div>
            </div>
          </div>
        </section>

        {/* Core Features Grid */}
        <section className="py-20 md:py-28 container mx-auto px-6 max-w-6xl">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl font-bold tracking-tight">Semua Alat Otorisasi di Satu Tempat</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Solusi end-to-end untuk tim platform engineering dan DevOps dalam mengamankan arsitektur cloud-native.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <Card key={idx} className="border border-border bg-card/60 backdrop-blur hover:border-primary/50 transition-colors">
                  <CardHeader className="pb-3">
                    <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-3">
                      <Icon className="h-5 w-5" />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-sm leading-normal">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </section>

        {/* Workflow Steps */}
        <section className="py-20 bg-muted/30 border-t border-border/40">
          <div className="container mx-auto px-6 max-w-5xl">
            <div className="text-center space-y-4 mb-16">
              <h2 className="text-3xl font-bold tracking-tight">Siklus Hidup Kebijakan yang Aman</h2>
              <p className="text-muted-foreground">Dari penulisan aturan hingga evaluasi sidecar di production</p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              <div className="space-y-3">
                <div className="font-mono text-primary text-xl font-bold">01. Authoring</div>
                <h3 className="text-lg font-semibold">Tulis Aturan Rego</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Definisikan aturan akses melalui RBAC matrix visual atau langsung menggunakan Monaco Rego editor.
                </p>
              </div>
              <div className="space-y-3">
                <div className="font-mono text-primary text-xl font-bold">02. Simulation & Gates</div>
                <h3 className="text-lg font-semibold">Uji & Persetujuan</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Jalankan dry-run simulasi payload JSON dan lewati pipeline approval sebelum rilis dikonfirmasi.
                </p>
              </div>
              <div className="space-y-3">
                <div className="font-mono text-primary text-xl font-bold">03. Distribution</div>
                <h3 className="text-lg font-semibold">Sinkronisasi Sidecar</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  OPA sidecar menarik rilis bundle terbaru secara otomatis dengan audit log evaluasi real-time.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 border-t border-border">
          <div className="container mx-auto px-6 max-w-4xl text-center space-y-6">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
              Siap Mengamankan Ekosistem Layanan Anda?
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Daftarkan workspace tenant Anda sekarang dan nikmati akses penuh seluruh modul tanpa kartu kredit selama masa uji coba.
            </p>
            <div className="pt-2">
              <Link href="/tenants">
                <Button size="lg" className="h-12 px-8">
                  Masuk ke Workspace Console <ChevronRight className="ml-1.5 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-8 bg-card">
        <div className="container mx-auto px-6 flex flex-col sm:flex-row items-center justify-between text-xs text-muted-foreground gap-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-primary" />
            <span>&copy; {new Date().getFullYear()} OPA Control Plane. Seluruh hak cipta dilindungi.</span>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/docs" className="hover:text-foreground transition-colors">
              Dokumentasi
            </Link>
            <Link href="/pricing" className="hover:text-foreground transition-colors">
              Harga
            </Link>
            <Link href="/login" className="hover:text-foreground transition-colors">
              Login
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}