// src/lib/epoch.ts

/**
 * Mengonversi Unix epoch (detik) ke teks waktu sesuai zona waktu lokal browser pengguna.
 */
export function formatLocalTime(
  epochSec: number | null | undefined,
  style: "datetime" | "date" | "time" | "relative" = "datetime"
): string {
  if (!epochSec) return "-";

  // Kalikan 1000 karena JavaScript Date membaca milidetik
  const date = new Date(epochSec * 1000);

  if (style === "date") {
    return new Intl.DateTimeFormat(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    }).format(date);
  }

  if (style === "time") {
    return new Intl.DateTimeFormat(undefined, {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      timeZoneName: "short", // Menampilkan label zona waktu (misal: WIB, WITA, GMT+7)
    }).format(date);
  }

  if (style === "datetime") {
    return new Intl.DateTimeFormat(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      timeZoneName: "short",
    }).format(date);
  }

  // Format relatif: "5 menit yang lalu"
  const diffSec = Math.floor(Date.now() / 1000) - epochSec;
  const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });

  if (diffSec < 60) return rtf.format(-diffSec, "second");
  if (diffSec < 3600) return rtf.format(-Math.floor(diffSec / 60), "minute");
  if (diffSec < 86400) return rtf.format(-Math.floor(diffSec / 3600), "hour");
  return rtf.format(-Math.floor(diffSec / 86400), "day");
}