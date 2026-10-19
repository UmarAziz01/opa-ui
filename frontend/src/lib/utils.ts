// src/lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Menggabungkan class Tailwind dengan resolusi konflik clsx & tailwind-merge.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Format ukuran byte menjadi format terdistribusi (KB, MB, GB).
 */
export function formatBytes(bytes: number, decimals: number = 2): string {
  if (!bytes || bytes === 0) return "0 Bytes";

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];

  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

/**
 * Helper styling badge status untuk berbagai modul (Tenant, Bundle, Approval, Audit).
 */
export function getStatusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
  const normalized = status.toUpperCase();

  switch (normalized) {
    case "ACTIVE":
    case "APPROVED":
    case "SUCCESS":
      return "default"; // Hijau / Primary
    case "TRIALING":
    case "BUILDING":
    case "PENDING":
    case "DRAFT":
      return "secondary"; // Kuning / Slate
    case "EXPIRED":
    case "REJECTED":
    case "SUSPENDED":
    case "FAILED":
      return "destructive"; // Merah
    default:
      return "outline";
  }
}