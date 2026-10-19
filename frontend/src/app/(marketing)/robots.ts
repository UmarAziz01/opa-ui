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