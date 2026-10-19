import type { Metadata } from "next";
import { Geist, Geist_Mono, Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/common/Providers";

const inter = Inter({ subsets: ["latin"] });

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "OPA UI - Multi-Tenant Authorization Engine",
  description: "Enterprise SaaS platform for Open Policy Agent and RBAC governance",
  icons: {
    icon: "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/opa-ui-light.png",
    shortcut: "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/opa-ui-light.png",
    apple: "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/opa-ui-light.png",
  },
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
