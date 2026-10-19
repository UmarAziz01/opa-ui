"use client";

import Link from "next/link";
import { constructMetadata } from "@/lib/seo";
import { useAppearance } from "@/components/common/ThemeAppearanceProvider";
import { GoogleTranslateFallback } from "@/components/common/GoogleTranslateFallback";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Shield, Cpu, RefreshCw, Layers, Moon, Sun, Monitor, Check } from "lucide-react";

export default function LandingPage() {
  const { theme, accent, setTheme, setAccent } = useAppearance();

  const accentOptions: Array<"zinc" | "blue" | "violet" | "emerald" | "rose"> = [
    "zinc", "blue", "violet", "emerald", "rose"
  ];

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-200">
      {/* Top Navbar */}
      <header className="border-b border-border/40 backdrop-blur sticky top-0 z-50">
        <div className="container mx-auto flex items-center justify-between p-4">
          <div className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-primary" />
            <span className="font-bold tracking-tight text-lg">OPA UI Engine</span>
          </div>

          <div className="flex items-center gap-4">
            {/* 5 Color Accents Switcher */}
            <div className="flex items-center gap-1.5 p-1 rounded-full border border-border">
              {accentOptions.map((item) => (
                <button
                  key={item}
                  onClick={() => setAccent(item)}
                  className={`w-4 h-4 rounded-full transition-all ${
                    item === "zinc" ? "bg-zinc-500" :
                    item === "blue" ? "bg-blue-500" :
                    item === "violet" ? "bg-violet-500" :
                    item === "emerald" ? "bg-emerald-500" : "bg-rose-500"
                  } ${accent === item ? "ring-2 ring-primary ring-offset-1 ring-offset-background" : "opacity-60"}`}
                  title={`Warna Aksen: ${item}`}
                />
              ))}
            </div>

            {/* Dark / Light / System Theme Switcher */}
            <div className="flex items-center rounded-lg border border-border p-0.5">
              <Button
                variant={theme === "light" ? "secondary" : "ghost"}
                size="sm"
                className="h-7 px-2"
                onClick={() => setTheme("light")}
              >
                <Sun className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant={theme === "dark" ? "secondary" : "ghost"}
                size="sm"
                className="h-7 px-2"
                onClick={() => setTheme("dark")}
              >
                <Moon className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant={theme === "system" ? "secondary" : "ghost"}
                size="sm"
                className="h-7 px-2"
                onClick={() => setTheme("system")}
              >
                <Monitor className="h-3.5 w-3.5" />
              </Button>
            </div>

            {/* Google Translate Fallback */}
            <GoogleTranslateFallback />

            <Link href="/login">
              <Button size="sm">Masuk Dashboard</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-20 text-center max-w-4xl">
        <Badge variant="outline" className="mb-4 px-3 py-1 text-xs">
          Multi-Tenant OPA Governance Engine
        </Badge>
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6">
          Manajemen Otorisasi OPA & Policy Engine Terdistribusi
        </h1>
        <p className="text-muted-foreground text-lg mb-8 leading-relaxed">
          Otomatisasi siklus rilis bundle OPA, manajemen kontainer sidecar modular per aplikasi, 
          dan tata kelola RBAC multi-tenant secara terpadu melalui kontrol GitOps.
        </p>

        <div className="flex justify-center gap-4 mb-16">
          <Link href="/login">
            <Button size="lg" className="px-8">
              Mulai 30 Hari Trial Bebas Biaya
            </Button>
          </Link>
          <Link href="/docs">
            <Button size="lg" variant="outline">
              Dokumentasi Arsitektur
            </Button>
          </Link>
        </div>

        {/* Feature Grid */}
        <div className="grid md:grid-cols-3 gap-6 text-left">
          <div className="p-6 rounded-lg border border-border bg-card">
            <Cpu className="h-8 w-8 text-primary mb-3" />
            <h3 className="font-semibold text-lg mb-2">Dynamic Sidecar OPA</h3>
            <p className="text-sm text-muted-foreground">
              Manajemen alokasi port dinamis kontainer Docker OPA dan streaming live logs secara realtime via SSE.
            </p>
          </div>

          <div className="p-6 rounded-lg border border-border bg-card">
            <Layers className="h-8 w-8 text-primary mb-3" />
            <h3 className="font-semibold text-lg mb-2">RBAC Matrix Builder</h3>
            <p className="text-sm text-muted-foreground">
              Visualisasi pemetaan relasi role dan permission secara fleksibel dengan editor monaco untuk syntax Rego.
            </p>
          </div>

          <div className="p-6 rounded-lg border border-border bg-card">
            <RefreshCw className="h-8 w-8 text-primary mb-3" />
            <h3 className="font-semibold text-lg mb-2">Automated Quality Gate</h3>
            <p className="text-sm text-muted-foreground">
              Verifikasi unit test `opa test` sebelum kompilasi bundle tar.gz dipublikasikan ke S3 storage MinIO.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}