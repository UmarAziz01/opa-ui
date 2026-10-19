import Link from "next/link";
import {
  BookOpen,
  Terminal,
  ShieldAlert,
  ArrowRight,
  Layers,
  Code2,
  FileCheck2,
  Network,
  Cpu,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function DocsPage() {
  const sections = [
    {
      id: "architecture",
      title: "Arsitektur OPA Control Plane",
      icon: Network,
      content:
        "Platform ini memisahkan policy administration point (PAP) dengan policy enforcement point (PEP). Kebijakan Rego dikompilasi ke dalam bundle release yang ditarik (pulled) secara berkala atau real-time oleh OPA sidecar yang berjalan berdampingan dengan microservices Anda.",
    },
    {
      id: "rego-v1",
      title: "Penulisan Kebijakan (Rego v1)",
      icon: Code2,
      content:
        "Kebijakan otorisasi ditulis menggunakan sintaks standar OPA Rego v1. Aturan mengevaluasi input request berupa identitas subject token (dari Keycloak JWT), method HTTP, dan path resource untuk menghasilkan keputusan boolean 'allow' atau filtering payload data.",
    },
    {
      id: "sidecar-allocation",
      title: "Alokasi Port & OPA Sidecar",
      icon: Cpu,
      content:
        "Setiap aplikasi yang didaftarkan di dalam organisasi akan menerima port unik dan app token. Token ini digunakan sidecar container untuk mengotentikasi penarikan bundle dan mengirim log keputusan evaluasi ke endpoint stream SSE.",
    },
    {
      id: "governance",
      title: "Quality Gate & Approval Workflow",
      icon: FileCheck2,
      content:
        "Sebelum perubahan kebijakan didistribusikan ke environment production, sistem menjalankan dry-run pengujian otomatis (opa test). Setiap rilis bundle baru memerlukan tinjauan diff dan persetujuan dari Tenant Admin.",
    },
  ];

  const quickstartYaml = `# docker-compose.sidecar.yaml
version: "3.8"
services:
  opa-sidecar:
    image: openpolicyagent/opa:latest-envoy
    ports:
      - "8181:8181"
    command:
      - "run"
      - "--server"
      - "--config-file=/etc/opa/config.yaml"
    volumes:
      - ./opa-config.yaml:/etc/opa/config.yaml:ro`;

  return (
    <div className="container mx-auto px-6 py-12 max-w-5xl space-y-12">
      {/* Header Halaman */}
      <div className="space-y-3 border-b border-border pb-6">
        <Badge variant="outline" className="border-primary/30 text-primary">
          Developer Documentation
        </Badge>
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">Dokumentasi OPA UI</h1>
        <p className="text-muted-foreground text-base max-w-2xl">
          Panduan integrasi policy bundle, alokasi port sidecar OPA, penulisan aturan Rego, dan tata kelola RBAC multi-tenant.
        </p>
      </div>

      {/* Grid Topik Dokumentasi */}
      <div className="grid md:grid-cols-2 gap-6">
        {sections.map((sec) => {
          const Icon = sec.icon;
          return (
            <Card key={sec.id} className="border-border bg-card">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary/10 text-primary">
                    <Icon className="h-5 w-5" />
                  </div>
                  <CardTitle className="text-lg">{sec.title}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-sm leading-relaxed text-muted-foreground">
                  {sec.content}
                </CardDescription>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Quickstart Contoh Sidecar */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="h-5 w-5 text-primary" />
            <h2 className="text-xl font-bold tracking-tight">Quickstart Sidecar Run</h2>
          </div>
          <Badge variant="secondary" className="font-mono text-xs">
            Docker Compose
          </Badge>
        </div>
        <div className="rounded-xl border border-border bg-[#0d1117] p-5 text-sm text-[#c9d1d9] font-mono overflow-x-auto">
          <pre>{quickstartYaml}</pre>
        </div>
      </div>

      {/* Langkah Integrasi */}
      <div className="space-y-6">
        <h2 className="text-xl font-bold tracking-tight">Alur Penerapan Kebijakan</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="rounded-lg border border-border p-4 bg-muted/20 space-y-2">
            <span className="font-mono text-xs text-primary font-bold">LANGKAH 1</span>
            <h3 className="font-semibold text-sm">Registrasi Tenant & Org</h3>
            <p className="text-xs text-muted-foreground leading-normal">
              Buat organisasi dan daftarkan aplikasi Anda untuk memperoleh App Token dan alokasi port sidecar.
            </p>
          </div>
          <div className="rounded-lg border border-border p-4 bg-muted/20 space-y-2">
            <span className="font-mono text-xs text-primary font-bold">LANGKAH 2</span>
            <h3 className="font-semibold text-sm">Desain Matriks & Aturan</h3>
            <p className="text-xs text-muted-foreground leading-normal">
              Susun mapping permission lewat RBAC Matrix Grid atau tulis aturan kondisional di Monaco Rego Editor.
            </p>
          </div>
          <div className="rounded-lg border border-border p-4 bg-muted/20 space-y-2">
            <span className="font-mono text-xs text-primary font-bold">LANGKAH 3</span>
            <h3 className="font-semibold text-sm">Validasi & Rilis Bundle</h3>
            <p className="text-xs text-muted-foreground leading-normal">
              Jalankan tes simulasi, buat bundle release, lewati gate approval, lalu pantau stream log evaluasinya.
            </p>
          </div>
        </div>
      </div>

      {/* Footer CTA */}
      <div className="rounded-xl border border-border bg-muted/30 p-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="font-bold text-lg">Siap mengonfigurasi workspace Anda?</h3>
          <p className="text-sm text-muted-foreground">
            Buka console tenant untuk mendaftarkan aplikasi dan organisasi pertama Anda.
          </p>
        </div>
        <Link href="/tenants">
          <Button>
            Buka Console <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </Link>
      </div>
    </div>
  );
}