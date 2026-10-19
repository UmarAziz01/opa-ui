"use client";

import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { KeyRound, ArrowRight, ShieldCheck } from "lucide-react";

const LOGO_URL = "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/opa-ui-light.png";

export default function LoginPage() {
  const { login } = useAuth();

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-md shadow-lg border-border">
        <CardHeader className="text-center space-y-3">
          <div className="mx-auto w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center p-2.5 shadow-sm">
            <Image
              src={LOGO_URL}
              alt="OPA Logo"
              width={40}
              height={40}
              className="w-full h-full object-contain"
              priority
              unoptimized
            />
          </div>

          <div className="space-y-1">
            <CardTitle className="text-2xl font-bold tracking-tight">
              OPA UI Engine
            </CardTitle>
            <CardDescription>
              Multi-Tenant Authorization & GitOps Policy Governance Platform
            </CardDescription>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="bg-muted p-3 rounded-lg border border-border text-xs text-muted-foreground flex gap-2 items-start">
            <ShieldCheck className="w-4 h-4 text-primary shrink-0 mt-0.5" />
            <span>
              Otentikasi diamankan menggunakan Single Sign-On (SSO) OIDC Keycloak dengan Role-Based Access Control terpusat.
            </span>
          </div>

          <Button onClick={login} className="w-full flex items-center justify-center gap-2" size="lg">
            <KeyRound className="w-4 h-4" />
            <span>Masuk via Keycloak SSO</span>
            <ArrowRight className="w-4 h-4 ml-auto" />
          </Button>

          <div className="text-center">
            <Link href="/" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              &larr; Kembali ke Landing Page
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}