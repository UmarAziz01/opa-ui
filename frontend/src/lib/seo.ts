// src/lib/seo.ts
import { Metadata } from "next";

interface MetadataOptions {
  title: string;
  description: string;
  path?: string;
  image?: string;
  noIndex?: boolean;
}

export function constructMetadata({
  title,
  description,
  path = "",
  image = "/og-image.png",
  noIndex = false,
}: MetadataOptions): Metadata {
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://100.100.30.50:3000";
  const fullUrl = path.startsWith("http") ? path : `${baseUrl}${path.startsWith("/") ? path : `/${path}`}`;

  return {
    title: {
      template: "%s | OPA UI Authz Engine",
      default: `${title} | OPA UI Authz Engine`,
    },
    description,
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: fullUrl,
    },
    openGraph: {
      title: `${title} | OPA UI Authz Engine`,
      description,
      url: fullUrl,
      siteName: "OPA UI Multi-Tenant Platform",
      images: [
        {
          url: image,
          width: 1200,
          height: 630,
          alt: title,
        },
      ],
      locale: "id_ID",
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: `${title} | OPA UI Authz Engine`,
      description,
      images: [image],
      creator: "@opa_ui",
    },
    robots: {
      index: !noIndex,
      follow: !noIndex,
      googleBot: {
        index: !noIndex,
        follow: !noIndex,
      },
    },
  };
}

/**
 * Helper pembuat JSON-LD Structured Data untuk Google Search.
 */
export function constructSoftwareApplicationJsonLd() {
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://100.100.30.50:3000";

  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "OPA UI Multi-Tenant Authz Engine",
    operatingSystem: "Linux, Cloud, Kubernetes",
    applicationCategory: "SecurityApplication",
    description: "Enterprise SaaS platform for Open Policy Agent (OPA) policy management, RBAC matrix, and GitOps bundles.",
    url: baseUrl,
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
      description: "30-Day Free Trial",
    },
  };
}