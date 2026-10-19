// src/app/(auth)/callback/page.tsx
"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { exchangeToken, syncProfile } = useAuth();

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const executedRef = useRef(false);

  useEffect(() => {
    if (executedRef.current) return;

    const code = searchParams.get("code");
    if (!code) {
      setErrorMsg("Parameter otorisasi code tidak ditemukan pada respon Keycloak.");
      return;
    }

    // Kunci eksekusi agar code tidak ditukar 2x
    const lockKey = `oidc_processed_${code}`;
    if (sessionStorage.getItem(lockKey)) {
      return;
    }

    executedRef.current = true;
    sessionStorage.setItem(lockKey, "true");

    const processAuth = async () => {
      try {
        const redirectUri = window.location.origin + "/callback";
        await exchangeToken({ code, redirect_uri: redirectUri });
        await syncProfile();
        router.replace("/tenants");
      } catch (err: any) {
        sessionStorage.removeItem(lockKey);
        setErrorMsg(
          err?.response?.data?.detail ||
            err?.message ||
            "Gagal memproses sesi otentikasi."
        );
      }
    };

    processAuth();
  }, [searchParams, exchangeToken, syncProfile, router]);

  return (
    <Card className="w-full max-w-sm border-border text-center">
      <CardContent className="pt-6 pb-6 space-y-4">
        {errorMsg ? (
          <div className="space-y-4">
            <div className="mx-auto w-10 h-10 rounded-full bg-destructive/10 text-destructive flex items-center justify-center">
              <AlertCircle className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <p className="font-semibold text-sm text-destructive">
                Otentikasi Gagal
              </p>
              <p className="text-xs text-muted-foreground">{errorMsg}</p>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={() => router.push("/login")}
            >
              Coba Masuk Kembali
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
            <div className="space-y-1">
              <p className="font-medium text-sm">Menghubungkan Sesi...</p>
              <p className="text-xs text-muted-foreground">
                Memverifikasi identitas pengguna dengan Keycloak OIDC.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function AuthCallbackPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/40 p-4">
      <Suspense
        fallback={
          <Card className="w-full max-w-sm border-border text-center">
            <CardContent className="pt-6 pb-6 space-y-3">
              <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
              <p className="font-medium text-sm">Memuat...</p>
            </CardContent>
          </Card>
        }
      >
        <CallbackContent />
      </Suspense>
    </div>
  );
}