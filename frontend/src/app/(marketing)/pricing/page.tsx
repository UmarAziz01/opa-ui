import Link from "next/link";
import { Check, ArrowRight, Zap, ShieldCheck, Building2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function PricingPage() {
  const tiers = [
    {
      name: "Free Trial",
      badge: "Masa Uji Coba 30 Hari",
      popular: false,
      price: "Rp 0",
      period: "selama 30 hari",
      description: "Paket onboarding otomatis untuk pengujian integrasi OPA sidecar dan evaluasi policy.",
      features: [
        "Masa aktif penuh 30 Hari (Auto-provisioning)",
        "Maksimal 3 Organisasi per Tenant",
        "Maksimal 5 Developer / Anggota Tim",
        "Monaco Rego v1 Editor & Sintaks Checker",
        "Interactive RBAC Matrix & Permission Assignment",
        "Simulasi Evaluasi Kebijakan (Dry-Run Tester)",
        "Audit Log JSONB & History Rilis Bundle",
      ],
      cta: "Mulai Trial Sekarang",
      href: "/tenants",
      variant: "outline" as const,
    },
    {
      name: "Developer Team",
      badge: "Paling Populer",
      popular: true,
      price: "Hubungi Tim",
      period: "skalabilitas tim",
      description: "Untuk tim engineering yang membutuhkan orkestrasi OPA sidecar di multi-environment.",
      features: [
        "Semua fitur di Free Trial",
        "Hingga 15 Organisasi aktif",
        "Hingga 25 Developer dengan RBAC role-level",
        "Real-time SSE Sidecar Terminal Log Viewer",
        "Automated Quality Gates & Approval Queue",
        "Instant Rollback ke versi Bundle sebelumnya",
        "Dukungan teknis responsif 24/7",
      ],
      cta: "Ajukan Upgrade",
      href: "/tenants",
      variant: "default" as const,
    },
    {
      name: "Enterprise Dedicated",
      badge: "Kustomisasi Penuh",
      popular: false,
      price: "Custom",
      period: "perusahaan skala besar",
      description: "Isolasi infrastruktur, SLA ketersediaan tinggi, dan kepatuhan audit keamanan ketat.",
      features: [
        "Kuota Organisasi & Developer Tanpa Batas",
        "Self-hosted / On-Premise OPA Cluster integration",
        "Custom Keycloak Realm & Identity Federation",
        "Long-term Retention Audit Logs & Export S3",
        "Custom Rego Unit Testing CI/CD Pipeline",
        "Dedicated Technical Account Manager",
        "SLA Ketersediaan 99.9%",
      ],
      cta: "Hubungi Sales",
      href: "/tenants",
      variant: "outline" as const,
    },
  ];

  return (
    <div className="container mx-auto px-6 py-12 max-w-6xl space-y-12">
      {/* Header */}
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <Badge variant="outline" className="border-primary/30 text-primary">
          Paket Langganan & 30-Day Trial
        </Badge>
        <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight">
          Pilihan Paket yang Fleksibel untuk Setiap Tahap
        </h1>
        <p className="text-muted-foreground text-base md:text-lg">
          Mulai langsung dengan Free Trial 30 Hari tanpa kartu kredit. Kuota dan batas modul dapat disesuaikan seiring pertumbuhan aplikasi Anda.
        </p>
      </div>

      {/* Kartu Paket Harga */}
      <div className="grid md:grid-cols-3 gap-8 items-stretch pt-4">
        {tiers.map((tier) => (
          <Card
            key={tier.name}
            className={`flex flex-col justify-between border relative transition-all ${
              tier.popular
                ? "border-primary shadow-lg ring-2 ring-primary/30 bg-card z-10"
                : "border-border bg-card/60"
            }`}
          >
            {tier.popular && (
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 z-20">
                <Badge className="bg-primary text-primary-foreground font-semibold text-xs px-3.5 py-1 shadow-md whitespace-nowrap">
                  {tier.badge}
                </Badge>
              </div>
            )}

            <div>
              <CardHeader className="space-y-2 pt-6">
                {!tier.popular && (
                  <span className="text-xs font-mono text-muted-foreground">{tier.badge}</span>
                )}
                <CardTitle className="text-2xl">{tier.name}</CardTitle>
                <CardDescription className="text-xs leading-relaxed">
                  {tier.description}
                </CardDescription>
                <div className="pt-2">
                  <div className="text-3xl font-extrabold">{tier.price}</div>
                  <span className="text-xs text-muted-foreground">{tier.period}</span>
                </div>
              </CardHeader>

              <CardContent className="space-y-3 pt-2">
                <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Fitur yang disertakan:
                </div>
                <ul className="space-y-2.5 text-sm">
                  {tier.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2.5">
                      <Check className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                      <span className="text-xs leading-normal">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </div>

            <CardFooter className="pt-6">
              <Link href={tier.href} className="w-full">
                <Button variant={tier.variant} className="w-full">
                  {tier.cta} <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </CardFooter>
          </Card>
        ))}
      </div>

      {/* FAQ Singkat */}
      <div className="border-t border-border pt-12 space-y-6 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold tracking-tight text-center">Pertanyaan yang Sering Diajukan</h2>
        <div className="grid md:grid-cols-2 gap-6 text-sm">
          <div className="space-y-2">
            <h3 className="font-semibold">Apa yang terjadi setelah masa Free Trial 30 hari berakhir?</h3>
            <p className="text-muted-foreground text-xs leading-relaxed">
              Setelah 30 hari, status subscription tenant akan berpindah ke EXPIRED. Akses ke pembuatan organisasi baru, aplikasi, dan rilis bundle akan ditangguhkan hingga Anda memperbarui status langganan.
            </p>
          </div>
          <div className="space-y-2">
            <h3 className="font-semibold">Berapa batas alokasi sidecar di masa trial?</h3>
            <p className="text-muted-foreground text-xs leading-relaxed">
              Secara default pada tier Free Trial, setiap tenant diberikan kuota hingga 3 Organisasi dan 5 Developer terdaftar. Setiap organisasi dapat menaungi multiple port sidecar aplikasi.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}